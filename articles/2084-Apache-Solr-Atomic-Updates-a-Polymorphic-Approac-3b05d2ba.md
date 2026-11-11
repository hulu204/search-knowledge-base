---
title: 'Apache Solr Atomic Updates: a Polymorphic Approach'
company: Sease
tag: 工程相关
date: 2020-01-28
url: https://sease.io/2020/01/apache-solr-atomic-updates-polymorphic-approach.html
account: 
origin: harvest3-202607
---
In this post we describe an approach to solve the problem of an application that requires both Full and Atomic Updates, using one of the powerful concepts in Object Oriented Programming: **Polymorphism**.

In Object-Oriented Programming, Polymorphism refers to the ability of a variable, method or object to take on multiple forms.

Although the example context has been abstracted to provide a high-level perspective, a practical application of the described approach has been implemented in **Alfresco Search Services** [[1]](https://github.com/Alfresco/SearchServices).

**Alfresco Search Services** provides search capabilities to **Alfresco Content Services** by leveraging **Apache Solr**.  
It is used by both Enterprise and Community releases of Alfresco Content Services.

## Context

**The existing code** creates *SolrInputDocument* instances from an incoming data model. Once created, documents are sent to Solr for indexing.   
Each document represents **the full state** of a domain object: that means the very first time it is sent, it will be **inserted**; the following time the same document (i.e. a document with the same id) is sent, it **replaces** the existing document.

This is a core part of the system, and the logic is quite complex: a *SolrInputDocument* instance is created in several places and passed around a lot of methods that enrich it with a specific set of attributes. Something like this:

```
				
					public void indexScenario1(DomainObject o) {
    SolrInputDocument doc = new SolrInputDocument();

    ...

    addAttributeSetA(doc, Domain);
    addAttributeSetB(doc, Domain);

    if (something) 
       addAttributeSetC(doc, Domain);
    else
       addAttributeSetD(doc, Domain);
    ...  
				
			
```

## Challenge

With our contribution the part of the system that creates the domain model instances changed a bit: the main improvement consists of the additional capability to work with **“delta” objects**.  In other words, the caller code can provide to that indexing component either **“full” or “partial” domain objects** (i.e. domain objects containing only things that have been updated).

## Constraints

So far, you think that this is a perfect fit for using **atomic updates**! Definitely true: the domain objects that contain only the changed bits can be transformed in **partial** *SolrInputDocument* instances, and then sent to Solr for indexing.

However, a **first constraint** needs to be addressed: the **partial objects** won’t be an exclusive scenario, we will still have to deal with **full objects**.

**Second constraint**: as said above, the indexing component represents a central/critical part of the system so even a **minimal change** carries on a certain level of risk so the code changes should be minimised.

In our experience that requires a “the less you change, the better” approach, and the old good **Object Oriented Programming** is definitely great at it!

## What are Atomic Updates?

Atomic Updates [[2]](https://lucene.apache.org/solr/guide/6_6/updating-parts-of-documents.html) are a way to execute indexing commands client side using an **“update” semantic**, by applying/indexing a document representing a **partial state of a domain object**.

So practically, using **Atomic Updates** a client can **send only a “partial” document** that contains only the updates that need to be applied to an existing (i.e. previously indexed) document.

Let’s see an example. After indexing the following document:

```
				
					{
   "id": 1
   "title": "Design Patterns: Elements of Reusable Object-Oriented Software",
   "author": [
      "Erich Gamma",
      "Richard Helm",
      "Ralph Jonson"
   ]
}      
				
			
```

You realise a missing “h” in “Ralph Johnson” (aaaarrgh! Mistaking the name of such a Guru: unacceptable!); in addition, you forgot John Vlissides…what a disaster!

So you can do one of the following two things.

The usual way consists of **recreating the whole document** without the mistake and re-send it to Solr:

```
				
					{
  "id":1
  "title":"Design Patterns: Elements of Reusable Object-Oriented Software",
  "author":[
      "Erich Gamma",
      "Richard Helm",
      "Ralph Johnson",
      "John Vlissides"
  ]
}      
				
			
```

That new document completely **replaces the indexed one** (note: the implicit assumption is that the *uniqueId* field is “id”).

The other way allows us to send only things we want to change on an existing document. In this case, we would send to Solr a document like this:

```
				
					{
  "id": 1
  "author": {
     "remove": "Ralph Jonson",
     "add": ["Ralph Johnson", "John Vlissides"]
  }
}    
				
			
```

It will target the indexed document with id=1 and

* it **remove**s the wrong value (“Ralph Jonson”)
* it **add**s the correct value for the author (“Ralph Jo**h**nson”)
* it **add**s the other missing author

As you can see, the value of a field that needs to be updated is **no longer a literal** **value** (e.g. a String, an Integer) or a list of values; instead, we have **a map** where **keys** are the **update commands we want to apply** (e.g. remove, add, set) and **values** are one or more literal values **we want to use for the update**.

More information about the whole semantics of the **AtomicUpdates** can be found in the **Apache Solr Reference Guide**[2]: here it is important to remember that Solr side, there’s no “true” partial update happening behind the scenes: the old version of the document is **fetched** and it is **merged** with the **partial state**; after that, the new “full” resulting document is **indexed again**.

Still, it is hugely beneficial as it reduces a lot the amount of data you may transfer to Solr when you need to update documents.

In **Java**, specifically in **SolrJ**, the *SolrInputDocument* class represents data we send to Solr for indexing. That is a Map so we can add, set or remove fields and values.

We are interested in the following three methods:

```
				
					// If a field with that name doesn’t exist it adds a new entry with the 
// corresponding value, otherwise the value is collected together with 
// the existing value(s)
// This is typically used on multivalued fields (i.e. calling twice this
// method on the same field, will collect 2 xvalues for that field)  
addField(String name, Object value)     

// Sets/Replaces a field value
setField(String name, Object value)     

// Remove a field from the document
removeField(String name, Object value)
				
			
```

The **same class** is also used for representing a **partial document**. You can do that by setting a map as a value in the *setField* or *addField* method. The map can have one or more modifiers:

* + **“add”**: adds the specified values to a multiValued field.
  + **“remove”**: removes all occurrences of the specified values from a multiValued field.
  + **“set”**: sets or replaces the field value(s) with the specified value(s), or removes the values if a ‘null’ or empty list is specified as the new value.

Note there are two additional modifiers (inc, removeregex) but we are not interested in them in this context.

## The Idea

Remember the constraints we put above:

* + the existing code always does **full document updates**
  + a change has been implemented on the caller side: **incoming domain objects** will be **full or partial**, depending on the use case
  + the Solr document instance valorisation is **spread across a lot of methods**. A *SolrInputDocument* instance is created and then passed on to several methods that set some part of the document state.
  + we need **partial updates** but they **won’t be the exclusive scenario**: in some cases, we still have **full updates**

Implementing in Java the partial update mechanism described so far requires that the methods *addField*, *setField* or *removeField* are aware of their context of execution (partial or full update).   
That is because in case of a full update, adding a new author would simply be

```
				
					doc.addField(“author”, “Ralph Johnson”);  
				
			
```

while in a **partial update**, it is necessary to take into account the difference between the **very first time** the add happened:

```
				
					List&lt;String&gt; authors = new ArrayList();
authors.add(“Ralph Johnson”);
doc.addField(“author”,  new HashMap() {{ “add”, authors}};
				
			
```

from the subsequent times:

```
				
					Map&lt;String, Object&gt; fieldModifier = 
            (Map&lt;String,Object&gt;)doc.getFieldValue(“author);

List&lt;String&gt; authors = (List&lt;String&gt;) fieldModifier.get(“add”);
authors.add(“John Vlissides”);
				
			
```

The logic above (that could be written better) needs to be done for a field, for each add/set/remove call! Is there a better way to deal with this?  Yes, of course:

creating a subclass of ***SolrInputDocument***:

```
				
					public class PartialSolrInputDocument extends SolrInputDocument {
     static Function&lt;String, List&lt;Object&gt;&gt; LAZY_EMPTY_MUTABLE_LIST = 
                key -&gt; new ArrayList&lt;&gt;();

     @Override
     @SuppressWarnings("unchecked")
     public void addField(String name, Object value) {
         Map&lt;String, List&lt;Object&gt;&gt; fieldModifier =
                 (Map&lt;String, List&lt;Object&gt;&gt;)computeIfAbsent(name, k -&gt; {
                     remove(name);
                     setField(name, newFieldModifier("add"));

                     return getField(name);
                 }).getValue();

        ofNullable(value)
             .ifPresent(v -&gt; 
                      fieldModifier.computeIfAbsent(
                                fieldModifier
                                  .keySet()
                                  .iterator()
                                  .next(),
                                LAZY_EMPTY_MUTABLE_LIST).add(v));
     }

     @Override
     public SolrInputField removeField(String name) {
        setField(name, newFieldModifier("set"));
        return getField(name);
     }

     private Map&lt;String, List&lt;String&gt;&gt; newFieldModifier(String op) {
        return new HashMap&lt;&gt;()
        {{
           put(op, null);
        }};
     }
}
				
			
```

the logic of this class can be summarised as follows:

* + **setField**: it maintains the original semantic: calling this method will replace any existing value
  + **removeField**: a removeField on a partial document means “Hey, I want to remove any existing value from the indexed document”. This semantic is implemented in atomic updates using a **“set” modifier with a null value**
  + **addField**: the logic here changes depending if a call “removeField” previously happened or not (on a given field).
    - If a *removeField* happened for field X, it is associated with a **“set” modifier** and a **null value**. Then “addField” is called, and the added value(s) populates the list associated with that “set” modifier. In other words, the meaning is “Solr, take this field definition and use it for replacing the existing values in the indexed document”.
    - else (a *removeField* DID NOT happen for field X): *addField* collects a set of values in the **“add” field modifier**. In other words, the collected values **are added** to the existing value(s) in the indexed document.

Using this approach, the question is: **shall we use a full or a partial update?** is **solved at object construction time**.

Let’s see an example. The following is an existing method which uses an input *SolrInputDocument* instance and adds a new name to the multiValued field “author”:

```
				
					public void addAuthor(SolrInputDocument doc, String authorName) {
    doc.addField(“author”, authorName)
}   
				
			
```

Now, assuming the method that creates the *SolrInputDocument* instance **is aware of the context (full or partial update**):

```
				
					// In case of full document update
SolrInputDocument doc = new SolrInputDocument();
				
			
```

or

```
				
					// in case of partial document update (i.e. atomic update)
SolrInputDocument doc = new PartialInputDocument();
				
			
```

and then, **regardless the previous choice**, the following method behaves correctly:

```
				
					addAuthor(doc, “Ralph Johnson”); 
				
			
```

depending on the passed ***SolrInputDocument*** instance type, the proper *addField* method is called, and the resulting document triggers a **full or a partial** update. The same is valid for all other methods that populate the document state.

It’s important to underline that no change happened to the signature of those methods, **polimorphism** manages the correct implementation depending on the type.

As a side note, please keep in mind that the *SolrInputDocument* (and therefore the *PartialSolrinputDocument* subclass) is a potential good candidate for being a **Fragile class** [[3]](https://en.wikipedia.org/wiki/Fragile_base_class).   
This means that what is described above is not intended to act as a general-purpose solution which fits any possible scenario.

## Need Help With This Topic?​​

If you’re struggling with Full and Atomic Updates in Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Full and Atomic Updates in Apache Solr, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)