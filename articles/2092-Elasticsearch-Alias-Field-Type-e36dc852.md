---
title: 'Elasticsearch Alias Field Type'
company: Sease
tag: 工程相关
date: 2020-11-17
url: https://sease.io/2020/11/elasticsearch-alias-field-type.html
account: 
origin: harvest3-202607
---
Elasticsearch provides a field type called [“alias”](https://www.elastic.co/guide/en/elasticsearch/reference/master/alias.html) which can be used for defining an additional/alternate name for a real field.

To define a field alias you must provide:

* + a name
  + a reference to a real field

here is an example:

```
				
					{
  "mappings": {
    "properties": {
      "title": {
        "type": "keyword"
      },
      "title_untokenized": {
        "type": "alias",
        "path": "title" 
      }
    }
  }
}
				
			
```

The field can be used in different contexts, in place of the target field. However, there are some restrictions to keep in mind. Let’s list them.

## The path must indicate an existent, concrete field

The target field of an alias **cannot be** an **object**, an **array** or another **field alias**, including the field itself: it must be a **concrete field**.

In addition, it **can’t be a dynamic field** (i.e. a field whose name has been declared with wildcards in the **dynamic\_templates** section) because the **alias binding** is done at **mapping time**. As a consequence of that, the **target field** must **exist** when the **alias** is **created**. The following request:

```
				
					{
  "mappings": {
    "dynamic_templates": [
      {
        "dates": {
          "match": "*_date",
          "mapping": {
            "type": "date",
            "format": "dd/MM/yyyy"
          }
        }
      }
    ],
    "properties": {
      "title": {
        "type": "text"
      },
      "author": {
        "type": "text"
      },
      "headings": {
        "type": "alias",
        "path": "creation_date"
      }
    }
  }
}
				
			
```

will return a 400 error with the following message:

###### *Invalid [path] value [creation\_date] for field alias [headings]: an alias must refer to an existing field in the mappings*

## An alias can't have multiple target fields

That means the value of the *path* attribute **cannot** be an array, only a **single value**. In other words, it’s not possible to have a single field that aliases multiple fields. The following request:

```
				
					{
  "mappings": {
    "properties": {
      "title": {
        "type": "text"
      },
      "author": {
        "type": "text"
      },
      "headings": {
        "type": "alias",
        "path" : ["title", "author"]
      }
    }
  }
}
				
			
```

will return a 400 error with the following message:

###### *Invalid [path] value [[title, author]] for field alias [headings]: an alias must refer to an existing field in the mappings*

which I could agree with you, that doesn’t really indicate the real problem. That is because the **whole value of the path attribute** is interpreted as a field name, and “[[title, author]]” doesn’t correspond to a field.

## Target field cannot be an alias

This means that we cannot indicate an **alias field** in the **path** attribute:

```
				
					"headings": {
  "type": "alias",
  "path" : "another_field_whose_type_is_alias"
}
				
			
```

a request like the above will return the following error:

###### *Invalid [path] value [another\_field\_whose\_type\_is\_alias] for field alias [headings]: an alias cannot refer to another alias*

other than the example above, under the same rule we should mention:

* + an alias field **cannot be used** in the **copy\_to** directive
  + an alias field **cannot be used** as a type of a **multi-field**

The reason is the same for both points above: the alias field **doesn’t exist**, it’s **virtual**, so it **cannot be used as a destination** for a value coming from another field, as it happens in multi-fields or in the copy\_to directive.

The following definitions are invalid:

```
				
					{
  "properties": {
    "title": {
      "type": "text",
      "copy_to": "alias_field"
    },
    "alias_field": {
      "type": "alias",
      "path": &lt;some other field, even a concrete one&gt;
    }
  }
}
{
  "properties": {
    "title": { 
      "type": "text",
      "fields": {
        "en": {
          "type": "text",
          "analyzer": "english"
        },
        "it": {
          "type": "alias",
          "path": &lt;some other field, even a concrete one&gt;
        }
      } 
    }
  }
}
				
			
```

## (Alias) Field name containing a dot

This is actually a rule that is valid for all fields. The **dot character** has a special meaning in Elasticsearch: it is used for defining **derived fields** (called **[multi-fields](https://www.elastic.co/guide/en/elasticsearch/reference/current/multi-fields.html)**) that are created on top of a **parent field definition**, as in the following example:

```
				
					{
  "properties": {
    "title": { 
      "type": "text",
      "fields": {
        "en": {
          "type": "text",
          "analyzer": "english"
        },
        "it": {
          "type": "text",
          "analyzer": "italian"
        }
      } 
    }
  }
}
				
			
```

The configuration above will create three different fields:

* + **title**: the parent field. It is associated with a **standard** analyzer
  + **title.en**: a derived field which will inherit the value from the parent field. The value will be processed using a symmetric (i.e. index and query time) **english** analyzer
  + **title.it**: is a derived field which will inherit the value from the parent field. The value will be processed using a symmetric (i.e. index and query time) **italian** analyzer

So in the definition above, the value assigned to the parent field will be used also for creating the derived fields.

Can a field name contain a dot? The answer is “it depends”.

Specifically, if the **part before the dot denotes another existing field**, then the answer is **negative** because Elasticsearch will interpret it as a de-touched multi-field. The following request:

```
				
					{
  "mappings": {
    "properties": {
      "title": {
        "type": "text"
      },
      "title.en": {
        "type": "alias",
        "path": "title" 
      }
    }
  }
}
				
			
```

produces a 400 response with the following error message:

###### *Can’t merge a non object mapping [title] with an object mapping [title]*

However, the **following requests is perfectly valid**:

```
				
					{
  "mappings": {
    "properties": {
      "title": {
        "type": "text"
      },
      "author.en": {
        "type": "alias",
        "path": "title"
      }
    }
  }
}
				
			
```

and it will create the following mappings:

```
				
					{
  "mappings": {
    "properties": {
      "title": {
        "type": "text"
      },
      "author.en": {
        "type": "alias",
        "path": "title"
      }
    }
  }
}
				
			
```

## An alias can't be used in input documents (i.e. indexing)

Being **virtual fields**, input documents (i.e. documents sent to Elasticsearch for indexing) **cannot** **contain alias fields**: they must indicate only concrete fields.

## Aliases cannot be used in source filtering

Remember: alias fields are virtual, they are not part of the source document, and as a consequence of that:

* + they **won’t appear** within the **\_source** element in responses
  + they **cannot** be used in **[source filtering clauses](https://www.elastic.co/guide/en/elasticsearch/reference/7.9/search-fields.html)**

## Unsupported

It’s not possible to use the alias fields in some APIs such as [term vectors](https://www.elastic.co/guide/en/elasticsearch/reference/master/docs-termvectors.html) and some queries such as [term](https://www.elastic.co/guide/en/elasticsearch/reference/master/query-dsl-term-query.html)/[terms](https://www.elastic.co/guide/en/elasticsearch/reference/master/query-dsl-terms-query.html) and [more\_like\_this](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-mlt-query.html).

## Need Help With This Topic?​​

If you’re struggling with the Elasticsearch alias field type, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Elasticsearch search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with the Elasticsearch alias field type, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Elasticsearch search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)