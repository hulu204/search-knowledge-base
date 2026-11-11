---
title: 'Synonyms and Stopwords: Vademecum'
company: Sease
tag: 查询理解
date: 2018-09-10
url: https://sease.io/2018/09/synonyms-and-stopwords-vademecum.html
account: 
origin: harvest3-202607
---
In this post we’ll cover two additional synonyms scenarios and we’ll try to summarise all previous tips in a concise form. Following the approach of the previous posts [[1]](https://sease.io/2018/07/apache-solr-elasticsearch-auto-phrasing-out-of-the-box.html) [[2]](https://sease.io/2018/07/combining-synonyms-and-stopwords.html) [[3]](https://sease.io/2018/08/still-synonyms-stopwords-mamma-mia.html), everything can be applied both to **Apache Solr** and **Elasticsearch**.

## Preconditions

* + **Synonyms and stopwords at query time**: this is not just a “theoretical” constraint; imagine if you have to manage a deployment context belonging to the same customer with a lot of small / medium indexes: you cannot re-build from scratch everything each time a synonym or a stopword changes.
  + **Synonyms, not hypernyms or hyponyms**: or better, we aren’t talking about what a thesaurus calls broader, narrower or related terms. Although some of the things below could be also valid in those contexts, the broader or narrower scope introduced with hypernyms, hyponyms or related concepts can have some weird side-effects on the scoring phase.

## Test data

Let’s start with the test data.

* + **synonyms** = [“out of warranty, oow”, “transfer phone number, port number”]
  + **stopwords** = [“of”, “my”]
  + **query analyzer** = [ “standard\_tokenizer”, “lowercase filter”, “synonyms (graph) filter”, “stopwords filter”]

## #1: How can I define Multi-terms Concepts?

If you want to manage a multi-terms concept as a whole, regardless it has synonyms or not, you can use the synonyms file. Here’s a couple of examples: the first is a concept with one synonym, the second one doesn’t have any synonym:

```
Multimedia Messaging Service,Multimedia Text Message,MMS
Apache Cassandra, Apache Cassandra
```

As you can see, when a concept doesn’t have any available synonym, we can just repeat it.

Solr users only: don’t forget the following things:

* + the request handler should use an edismax or Lucene query parser, and the **SplitOnWhiteSpace** flag (**sow**) must be set to **true**
  + the field type which includes the synonyms graph filter must have the **autoGeneratePhraseQueries** set to **true**

You can read more here [[1]](https://sease.io/2018/07/apache-solr-elasticsearch-auto-phrasing-out-of-the-box.html) about this approach.

Note: this will work until the Lucene *SynonymMap* uses a *List/Array* for collecting the synonyms associated with a given concept. When and if the implementation will switch to a *Set-like approach*, there’s a high chance this trick will stop working.

## #2: What if the query contains multi-terms concepts with stopwords?

Imagine a query like this:

```
				
					q=my car is out of warranty. What can I do?
				
			
```

Well, with the configuration above the stopwords removal after the synonyms detection causes a weird effect on the generated query: the “what” term is wrongly added to the synonym phrase query: “out ? warranty what”.

While the issue affects the *FilteringTokenFilter* (the superclass of *StopFilter*) and therefore it has a wider scope, for this specific problem we proposed a solution [[2]](https://sease.io/2018/07/combining-synonyms-and-stopwords.html), consisting of a specialised *StopFilter*which is aware about synonym tokens. The result is that terms which are part of a previously detected synonym are not removed, even if they are stopwords. The query analyzer of our field becomes something like this:

```
				
					&lt;tokenizer class="solr.StandardTokenizerFactory"/&gt;
&lt;filter class="solr.LowerCaseFilterFactory"/&gt;
&lt;filter class="solr.SynonymGraphFilterFactory" 
        synonyms="synonyms.txt" 
        ignoreCase="false" 
        expand="true"/&gt;
&lt;filter class="io.sease.SynonymAwareStopFilterFactory" 
        words="stopwords.txt" 
        ignoreCase="true"/&gt;
				
			
```

## #3: What if the document contains multi-terms concepts with "intruder" stopwords?

We have a document like this:

```
				
					{
  "id": 1,
  "title": "how do I transfer my phone number?"
}
				
			
```

and the query:

```
				
					q=transfer phone number procedure
				
			
```

at query time, the synonym is correctly detected and phrase clauses are generated, but unfortunately it doesn’t match the document above because the intermediate “my” stopwords:

You can read here [[3]](https://sease.io/2018/08/still-synonyms-stopwords-mamma-mia.html) the proposed solution for this scenario, which basically consists of a two-steps query plan: in the first, the detected synonyms generate phrase clauses, while in the second they are destructured in term clauses.

## #4: What if the query contains multi-terms concepts with "intruder" stopwords?

And here we are in the opposite case. We have a document like this:

```
				
					{ 
  "id": 1, 
  "title": "transfer phone number procedure" 
}
				
			
```

and the query:

```
				
					q=how do I transfer my phone number?
				
			
```

As you can see, at query time the synonym is not detected because the “my” stopword between terms. While the document above could be still be part of the response of the generated query, here we are focusing on the missing synonym detection.

A possible solution is to double the synonym filter before and after the stopwords filter:

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
                   ignoreCase="true" 
                   expand="true"/&gt;
           &lt;filter class="io.sease.SynonymAwareStopFilterFactory" 
                   words="stopwords.txt" 
                   ignoreCase="true"/&gt;
           &lt;filter class="solr.SynonymGraphFilterFactory" 
                   synonyms="synonyms.txt" 
                   ignoreCase="true" 
                   expand="true"/&gt;
       &lt;/analyzer&gt;
&lt;/fieldtype&gt;
				
			
```

In the first iteration the synonym is not detected, then the *StopFilter* removes the “my” stopword so in the second iteration the synonym will be correctly recognized. Note the *StopFilter* is still the custom class we introduced in #2 because we want to cover also that scenario.

What is the drawback of this approach? This is something which worked in my specific case, but be aware that the *SynonymGraphFilter* documentation states this explicit warning:

NOTE: this cannot consume an incoming graph; results will be undefined.

## #5 (UNSOLVED) What if the query contains multi-terms concepts more than one "intruder" stopwords?

This is the worst case, where we have a query like this:

```
				
					q=out of my warranty
				
			
```

That is: we have a couple of terms which have been declared as stopwords, but the first (of) is potentially part of a synonym (out of warranty) while the second (my) isn’t.

We’re still working on this case so unfortunately there’s no proposal here, if you have some ideas or feedback, it is warmly welcome.

## Need Help With This Topic?​​

If you’re struggling with synonyms and stopwords, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with synonyms and stopwords, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)