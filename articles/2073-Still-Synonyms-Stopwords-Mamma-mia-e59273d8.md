---
title: 'Still Synonyms + Stopwords?? Mamma mia!'
company: Sease
tag: 查询理解
date: 2018-08-30
url: https://sease.io/2018/08/still-synonyms-stopwords-mamma-mia.html
account: 
origin: harvest3-202607
---
## The Context

Brief recap of where we arrived in the [preceding article](https://sease.io/2018/07/combining-synonyms-and-stopwords.html): we had the following synonyms and stopwords settings:

* + synonyms = {“out of warranty”,”oow”}
  + stopwords = {“of”}

Both of those filters **were configured exclusively at query time**; the synonym filter first and then the stopwords filter.

Using the built-in *StopFilter* we had a synonym detection issue because of the removal of the “of” term in the query string (e.g. “my device ran *out **of** warranty*“). For that reason, we introduced a custom *StopFilter* subclass which was aware of stopwords in synonyms.

The other scenario we are going to describe is a little bit different: let’s suppose we have the following data:

* + synonyms = {test code, tdd, testing}
  + stopwords = {my, your, how ,to, in}

Still, here, we want to manage synonyms and stopwords only at query time.  
We have this document indexed:

```
				
					{
      "id": 1,
      "title": "Java programmer: do you want to test your code?"
   }
				
			
```

And a query like this:

```
"how to test code in Java?"
```

## The Problem: missing synonym match

The query parser matches the “test code” synonym in the query and produces a query like this:

```
				
					(title:tdd title:testing PhraseQuery(title:"test code")) title:java
				
			
```

unfortunately there’s no match, because the document title contains an intruder: the “your” term between the “test” and “code”.

## A Solution: invisible queries with and without synonym phrases

In the preceding article, we’ve underlined the role of the **autoGeneratePhraseQueries** flag. It is responsible for creating phrase clauses for all detected multi-term synonyms. In case this flag is set to false (or even missing) the generated query won’t have any phrase, even if a multi-term synonym is detected.

While usually this is not what you would expect, in this specific case it could be a valid alternative for dealing with such mismatching: a first request would require the “synonym phrasing” behaviour, but a second one wouldn’t. The first query would be:

```
				
					(title:tdd title:testing PhraseQuery(title:"test code")) title:java
				
			
```

After receiving an empty response, a second query will be sent, targeting another (similar) field related to a field type which has the **autoGeneratePhraseQueries** parameter set to **false**. That would generate the following query:

```
				
					(title:testing title:tdd (+title:test +title:code)) title:java
				
			
```

and here we would get a match!

A couple of notes:

* + On the second try, we require the disjoint presence of those two terms (“test” and “code”) in whatever order, with whatever proximity, so the increased recall could produce some unexpected results. In case we are using the edismax query parser, a “pf” parameter would help move up those results which adhere better to the entered query, in terms of proximity and terms order.
  + we could put the stop filter at index time, but that violates the precondition: we want pure query-time management.

How to implement such search workflow? In Solr, we need a couple of fields, the first one is exactly the field + field type we described in the [preceding article](https://sease.io/2018/07/combining-synonyms-and-stopwords.html), and the second is similar, the only difference is in the **autoGeneratePhraseQueries** parameter, which is set to **false**:

```
				
					&lt;fieldtype 
       name="text_with_synonyms_phrases" 
       class="solr.TextField" autoGeneratePhraseQueries="true"&gt;
       
       &lt;analyzer type="index"&gt;
           &lt;tokenizer class="solr.StandardTokenizerFactory"/&gt;
           &lt;filter class="solr.LowerCaseFilterFactory"/&gt;
       &lt;/analyzer&gt;
       &lt;analyzer type="query"&gt;
           &lt;tokenizer class="solr.StandardTokenizerFactory"/&gt;
           &lt;filter class="solr.LowerCaseFilterFactory"/&gt;
           &lt;filter class="solr.SynonymGraphFilterFactory" 
                   synonyms="synonyms.txt" 
                   ignoreCase="false" 
                   expand="true"/&gt;
           &lt;filter class="sc.SynonymAwareStopFilterFactory" 
                   words="stopwords.txt" 
                   ignoreCase="true"/&gt;
       &lt;/analyzer&gt;
&lt;/fieldtype&gt;
				
			
```

```
				
					&lt;fieldtype 
       name="text_without_synonyms_phrases" 
       class="solr.TextField" autoGeneratePhraseQueries="false"&gt;
       
       &lt;analyzer type="index"&gt;
           &lt;tokenizer class="solr.StandardTokenizerFactory"/&gt;
           &lt;filter class="solr.LowerCaseFilterFactory"/&gt;
       &lt;/analyzer&gt;
       &lt;analyzer type="query"&gt;
           &lt;tokenizer class="solr.StandardTokenizerFactory"/&gt;
           &lt;filter class="solr.LowerCaseFilterFactory"/&gt;
           &lt;filter class="solr.SynonymGraphFilterFactory" 
                   synonyms="synonyms.txt" 
                   ignoreCase="false" 
                   expand="true"/&gt;
           &lt;filter class="sc.SynonymAwareStopFilterFactory" 
                   words="stopwords.txt" 
                   ignoreCase="true"/&gt;
       &lt;/analyzer&gt;
&lt;/fieldtype&gt;

&lt;field 
      name="title_with_synonyms_phrases" 
      type="text_with_synonyms_phrases .../&gt;
&lt;field 
      name="title_without_synonyms_phrases" 
      type="text_without_synonyms_phrases .../&gt;
				
			
```

then, here is the minimal request handler:

```
				
					&lt;requestHandler name="/search" class="solr.SearchHandler" default="true"&gt;
       &lt;lst name="defaults"&gt;
           &lt;bool name="sow"&gt;false&lt;/bool&gt;
           &lt;str name="df"&gt;title_with_synonyms_phrases&lt;/str&gt;
           &lt;str name="defType"&gt;lucene&lt;/str&gt; 
       &lt;/lst&gt;
   &lt;/requestHandler&gt;
				
			
```

A client would send first a request like this:

```
				
					/search?q=how to test code in Java
				
			
```

And, after receiving an empty response, it will send a second query:

```
				
					/search?q=how to test code in Java&amp;df=text_without_synonyms_phrases
				
			
```

Another option, which moves the search workflow on Solr side, is our [CompositeRequestHandler](https://sease.io/2018/03/compositesearchhandler.html), a Solr component which invokes in chain a set of RequestHandler instances: a first request handler, targeting the **title\_with\_synonyms\_phrases** would be invoked and, in case of zero results, the same query will be sent to another request handler, which would target the **title\_without\_synonyms\_phrases**.

*Note for **Elasticsearch users**: you will find some differences in applying what is described above. Although the* **auto\_generate\_phrase\_queries** *attribute is also present in Elasticsearch, it doesn’t have the same effect. What you’re looking for is an attribute which is not related to field types, it is a query attribute* [[2]](https://www.elastic.co/guide/en/elasticsearch/reference/master/query-dsl-match-query.html#query-dsl-match-query-synonyms) [[3]](https://www.elastic.co/guide/en/elasticsearch/reference/master/query-dsl-query-string-query.html)*and it is called **auto\_generate\_synonyms\_phrase\_query**.*

## Need Help With This Topic?​​

If you’re struggling with synonyms and stopwords, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with synonyms and stopwords, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)