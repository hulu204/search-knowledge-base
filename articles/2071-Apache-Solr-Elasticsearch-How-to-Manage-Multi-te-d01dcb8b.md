---
title: 'Apache Solr / Elasticsearch: How to Manage Multi-term Concepts out of the Box?'
company: Sease
tag: 查询理解
date: 2018-07-22
url: https://sease.io/2018/07/apache-solr-elasticsearch-auto-phrasing-out-of-the-box.html
account: 
origin: harvest3-202607
---
This flash blog post will address a very specific and common problem: how to manage entities/concepts composed of multiple terms in a vanilla Apache Solr/Elasticsearch instance (no plugins or extensions to install).

## The (deployment) context

An **Elasticsearch** or **Apache Solr** infrastructure where you **cannot install** third-party components (e.g. plugins, filters, query parsers). This can happen for several reasons:

* + **endogenous factors**: lack of required expertise/skills for implementing/installing things in your infrastructure.
  + **exogenous factors**: search capabilities live in an external and managed context which doesn’t allow custom components. This happens for example with services like the Amazon Elasticsearch Service [[1]](https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/aes-supported-plugins.html).

## The Problem

How can I model multi-terms concepts (i.e. concepts composed of multiple terms)?

Concepts are a fundamental piece of a domain-specific vocabulary: “United States of America”, “Phone Number”, and “Out of Warranty” are just examples of entities you **probably** want to manage as a whole; if a user searches something like “How can I transfer a Phone Number?” you **probably** don’t want to return things about numbers or phones, which have a broader scope (i.e. sacrificing precision in favour of recall).

Note, that “**probably**” is in bold because there’s not an absolute truth here: everything depends on the functional context where the application is running. Here we assume this requirement, but things could be different in another context.

## Index/Query Time Solutions

The problem can be solved using two different approaches that involve Indexing time and Query time configurations:

* + **Simple Contraction**: using the SynonymFilter with Simple Contraction [[2]](https://www.elastic.co/guide/en/elasticsearch/guide/current/multi-word-synonyms.html#_use_simple_contraction_for_phrase_queries) [[3]](https://lucene.apache.org/core/6_6_0//analyzers-common/org/apache/lucene/analysis/synonym/SolrSynonymParser.html) to inject a **single term** that represents the concepts (with optional synonyms)

```
Multimedia Messaging Service, Multimedia Text Message => mms
```

* + **Shingles**: combining **shingles** and a **keep word filter** for generating bigrams and trigrams from a given text (assuming we are limiting our interest only to concepts composed by a maximum of 3 terms).

## ...an Additional Constraint: Query-Time Only

One of the drawbacks of the first group (index + query time) is the cost of **reindexing the whole dataset** when a change occurs in the synonyms or the keywords list. So the **additional constraint** we will introduce is: we want to be able to change the concepts list at runtime **without** any reindexing.

Again, this is not an absolute constraint: there are a lot of scenarios where reindexing everything is completely ok. In my experience, this has a direct correlation with the index size plus how the whole reindexing process takes.

So in other words: if the full reindexing process takes a reasonable amount of time and doesn’t produce any service interruption, then you should consider removing the “query-time only” constraint.

## A Solution

The synonym management has been enhanced in Elasticsearch and Apache Solr [[4]](https://lucidworks.com/2017/04/18/multi-word-synonyms-solr-adds-query-time-support/#footnote1), with the introduction of “graph-aware” token filters, for enabling full support of **Multi-Word Synonyms.**

Before that, both index/query time and query time approaches suffered from some limitations when dealing with synonyms [[5]](https://opensourceconnections.com/blog/2013/10/27/why-is-multi-term-synonyms-so-hard-in-solr/).

In any case, the current implementation allows us to correctly manage multi-word synonyms as a whole. So, coming back to our question, we can try to “shape” the synonym filter at our will for managing compound concepts as well.

First, a compound concept can or cannot have synonyms.

##### Concept with Synonym(s)

If the concept has one or more synonyms, we are within a regular context of the synonym filter. Here’s a sample content of the *synonyms.txt* file:

```
Multimedia Messaging Service,Multimedia Text Message,MMS
USA,United States of America
...
```

Here’s the corresponding configuration:

![](https://i0.wp.com/sease.io/wp-content/uploads/2018/07/solr-logo-e1532273210873.png?resize=100%2C51&ssl=1 "Apache Solr")

```
				
					&lt;fieldtype name="txt" 
           class="solr.TextField" 
          autoGeneratePhraseQueries="true"&gt;
       &lt;analyzer type="index"&gt;
           &lt;tokenizer class="solr.StandardTokenizerFactory"/&gt;
           &lt;filter class="solr.LowerCaseFilterFactory"/&gt;
       &lt;/analyzer&gt;
       &lt;analyzer type="query"&gt;
           &lt;tokenizer class="solr.StandardTokenizerFactory"/&gt;
           &lt;filter class="solr.LowerCaseFilterFactory"/&gt;
           &lt;filter 
              class="solr.SynonymGraphFilterFactory" 
              synonyms="synonyms.txt" 
              expand="true"/&gt;
       &lt;/analyzer&gt;
&lt;/fieldtype&gt;
&lt;field name="title" type="txt" indexed="true" stored="true"/&gt;
				
			
```

![](https://i0.wp.com/sease.io/wp-content/uploads/2018/07/es-logo.png?resize=300%2C60&ssl=1 "Elasticsearch")

```
				
					"analysis": {
    "filter": {
      "english_synonyms": {
         "type": "synonym_graph",
         "synonyms_path": "synonyms.txt",
         "expand": true
      }
    },
    "analyzer": {
      "text_index_analyzer": {
        "tokenizer": "standard",
        "filter": [ "lowercase" ]
      },
      "text_query_analyzer": {
        "tokenizer": "standard",
        "filter": [
          "lowercase",
          "english_synonyms"
        ]
      }
    }
...
"properties": {
   "title": {
      "type": "text",
      "analyzer": "text_index_analyzer",
      "search_analyzer": "text_query_analyzer"
   }
}
				
			
```

Issuing the following queries:

![](https://i0.wp.com/sease.io/wp-content/uploads/2018/07/solr-logo-e1532273210873.png?resize=100%2C51&ssl=1 "Apache Solr")

```
				
					q={!lucene}multimedia messaging service&amp;sow=false&amp;df=title
				
			
```

![](https://i0.wp.com/sease.io/wp-content/uploads/2018/07/es-logo.png?resize=300%2C60&ssl=1 "Elasticsearch")

```
				
					{
  "query": {
     "match": {
       "title": "Multimedia messaging service"
     }
   }
}

{
   "query": {
     "query_string": {
       "query": "Multimedia messaging service",
       "default_field": "title",
     }
   }
}
				
			
```

produces (use debug=true in Solr or \_validate/query?explain=true in Elasticsearch) the following query:

```
				
					(PhraseQuery(title:"multimedia text message") 
 title:MMS 
 PhraseQuery(title:"multimedia messaging service"))
				
			
```

Which is exactly what we want: the concept expressed in the query has been detected and the output query is looking for its expanded (United States of America) or contracted (USA) form.   
So far, so good.

##### Concept without Synonyms

What about if a multi-term concept doesn’t have any variant/synonym but we still want to manage it as a whole? Can we use the synonym filter without synonyms? Let’s try to see what happens.

The first obvious idea is to declare something like this, in our synonyms.txt:

```
				
					Multimedia Messaging Service  
...
				
			
```

That is, a line containing our concept without any synonym. Unfortunately this is not working, the engine detects there are no synonyms and the resulting query is something like this:

```
				
					title:multimedia title:messaging title:service
				
			
```

The same happens if you put a dummy synonym which is removed later, in the indexing chain, by a stopword filter. Something like:

```
				
					Multimedia Messaging Service, something_that_will_be_configured_as_stopword 
...
				
			
```

So the last chance is to duplicate the entry. Something like this:

```
				
					Multimedia Messaging Service, Multimedia Messaging Service 
...
				
			
```

Here things start to be interesting. Running the same queries above we got the following explain:

![](https://i0.wp.com/sease.io/wp-content/uploads/2018/07/solr-logo-e1532273210873.png?resize=100%2C51&ssl=1 "Apache Solr")

```
				
					(PhraseQuery(title:"multimedia messaging service") 
 PhraseQuery(title:"multimedia messaging service"))
				
			
```

![](https://i0.wp.com/sease.io/wp-content/uploads/2018/07/es-logo.png?resize=300%2C60&ssl=1 "Elasticsearch")

```
				
					title:"multimedia messaging service"^2.0
				
			
```

```
				
					4.544185 = sum of:
  4.544185 = weight(title:"multimedia messaging service" in 1) [SchemaSimilarity], result of:
    4.544185 = score(doc=1,freq=1.0 = phraseFreq=1.0
), product of:
      2.0 = boost
      2.7725887 = idf(), sum of:
        0.6931472 = idf, computed as ... from:
          1.0 = docFreq
          2.0 = docCount
        0.6931472 = idf, computed as ... from:
          1.0 = docFreq
          2.0 = docCount
        0.6931472 = idf, computed as ... from:
          1.0 = docFreq
...
				
			
```

That is, the score of the match above would have been **2.2720926** (4.544185 / 2) but since we have that artificial boost it has been doubled; at the same time it’s important to underline our concept has been correctly managed as a whole, and the queries above won’t return items related with messages, multimedia or services, which are broader concepts.

Is that boost factor a problem? That depends on your application: you should

* + have a representative number of search cases
  + try a plain term-centric search
  + try the approach suggested above
  + use a [search quality evaluation tool](https://sease.io/2018/07/rated-ranking-evaluator.html)
  + compare and choose

## Summary

* + You have an **Elasticsearch** or **Apache Solr** cluster
  + You **cannot install** custom plugins
  + You want to manage **compound concepts**
  + You **don’t want to reindex your corpus** when adding / removing / updating the concepts list
  + If a concept **has one or more synonyms**, this is quite straightforward: use the synonym (graph) filter at query time\*
  + if a **concept doesn’t have any synonym**, you can still use the synonym (graph) filter: **just double the concept definition,** but keep in mind the double (2.0) boost applied to the corresponding phrase query\*

*\* Apache Solr users: make sure the target field type has autoGeneratePhraseQueries set to true, and the sow parameter (defined in the RequestHandler settings or as a request parameter) set to false.*

## Need Help With This Topic?​​

If you’re struggling with Multi-Term Concepts in Apache Solr or Elasticsearch, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Multi-Term Concepts in Apache Solr or Elasticsearch, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)