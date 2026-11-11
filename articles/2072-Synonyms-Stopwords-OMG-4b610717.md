---
title: 'Synonyms + Stopwords?? OMG!'
company: Sease
tag: 查询理解
date: 2018-07-30
url: https://sease.io/2018/07/combining-synonyms-and-stopwords.html
account: 
origin: harvest3-202607
---
The scenario description is quite simple: we want to use **synonyms** and **stopwords**.

Following the path of our previous [article](https://sease.io/2018/07/apache-solr-elasticsearch-auto-phrasing-out-of-the-box.html), we will introduce an additional component in the analysis chain: a *StopFilter*, which, as the name suggests, removes a set of words from an incoming token stream.

We will use the following data through the examples:

* + synonyms = [“out of warranty”,”oow”]
  + stopwords = [“of”]

Token filters can be configured at index and/or query time. In this context we are focused on the query side: both synonyms and stopwords will be configured only in the query analyzer.

Working exclusively at query time has a great benefit: we can change things at runtime without any reindex need. At the same time, no stopwords filtering will be executed at index time so those terms will be uselessly part of the dictionary.

We have the following analyzers:

* + **index analyzer**
    - standard-tokenizer
    - lowercase
  + **query analyzer**
    - standard-tokenizer
    - lowercase + **synonyms** + **stopwords**

Theoretically, in the query analyzer we would have two options: the stopwords filter could be defined before or after the synonym filter. However, the first way (before) doesn’t make so much sense, because terms that are stopwords and that are, at the same time, part of a synonym will be removed before the synonym detection. As consequence of that those synonym won’t be detected: in the example data, issuing a query like

q=out of warranty

the “of” term will be removed by the *StopFilter*, the subsequent filter would receive [“out”, “warranty”], which doesn’t match the configured synonym (“out of warranty”).

*Elasticsearch users: Elasticsearch doesn’t allow this scenario at all; if you try to use the PUT Settings API with a chain defined as above (first stopwords then synonyms with some term intersection), it will throw an illegal argument exception saying “term: out of warranty analyzed to a token (warranty) with position increment != 1 (got: 2)” .*

*Apache Solr instead uses a lenient approach: no errors at index creation, but the problem remains (personally I prefer the Elasticsearch approach)*

So the obvious choice is to postpone the stopwords management after the synonym filter. Unfortunately, here there’s an issue: the stopword(s) removal has some unwanted side-effect in the generated token graph and the query parser generates a wrong query because it consumes the token stream at the end of the chain.

Let’s imagine we have the following query:

q=tv went out **of**warranty something **of**

it will generate the following:

title:tv title:went (title:**oow** **PhraseQuery(title:**“out ? warranty **something**“**))**

As you can see, the synonym (out of warranty -> oow) is correctly detected but the stopwords filter removes all the “of” tokens, even if the first occurrence is part of a synonym. In the generated query you can see the sneaky effect: the “hole” created by the first “of” occurrence removal, produces the inclusion, in the phrase query, of the next available token in the stream (“something”, in the example).

In other words, the **oow** token synonym is marked with a positionLength = 3, which correctly means it spans three tokens (1=out, 2=of, 3=warranty); later, the query parser will include the next three available terms for generating a synonym phrase queries but since we no longer have the 2nd token (of), such count includes also “something”, which is the 3rd available token in the stream.

Before proceeding: this is a known problem, a long-standing issue [[1]](https://issues.apache.org/jira/browse/LUCENE-4065) in Lucene which has a broader domain because it is related with the *FilteringTokenFilter*, the superclass of *StopFilter*.

The problem we will try to solve is: how can we manage synonyms and stopwords at query time without generating the conflict above?

A note first: the token filter we are going to create is something that deals only with Lucene classes. However, when things need to be plugged in a runtime container (e.g. Apache Solr or Elasticsearch) the deployment procedure depends on the target platform: we won’t cover this part here.

The proposed solution is to create a *StopFilter subclass* which will be “synonym-aware”; it will check the *tokenType* and *positionLength* attributes before deciding if a token needs to be removed from the stream. The goal is to avoid removing those terms which have been defined in the stopwords list but are part of a synonym definition.

The class that we are going to extends is *org.apache.lucene.analysis.core.StopFlter*. This is an empty class, because all the filtering logic is in the superclasses (*org.apache.lucene.analysis.StopFilter* and the more generic *org.apache.lucene.analysis.FilteringTokenFilter*). The stopwords logic resides in the *accept()* method, which as you can see is very simple:

```
protected boolean accept() {
  return !stopWords.contains(termAtt.buffer(), 0, termAtt.length());
}
```

If the stopwords list contains the current term, it will be removed. So far, so good. We need to extend (actually we could also decorate) the *StopFilter* class for doing something else before calling the logic above.

First we need to check the **token type**: if a token has been marked as a **SYNONYM** then our filter doesn’t have to remove it. Then we need to check the **positionLength** attribute, because, within a synonym detection context, a position length greater than 1 means we have traversing a multi-term synonym:

```
public class SynonymAwareStopFilter extends StopFilter {

  private TypeAttribute tAtt = 
                             addAttribute(TypeAttribute.class);
  private PositionLengthAttribute plAtt = 
                             addAttribute(PositionLengthAttribute.class);

  private int synonymSpans;

  protected SynonymAwareStopFilter(
                         TokenStream in, CharArraySet stopwords) {
    super(in, stopwords);
  }

  @Override
  protected boolean accept() {
    if (isSynonymToken()) {
      synonymSpans = plAtt.getPositionLength() > 1 
                             ? plAtt.getPositionLength() 
                             : 0;
      return true;
    }

    return (--synonymSpans > 0) || super.accept();
  }

  private boolean isSynonymToken() {
    return "SYNONYM".equals(tAtt.type());
  }
```

Let’s do some test. We will use Apache Solr 7.4.0 for checking the results. Here is the field type definition, where you can see our SynonymAwareStopFilter:

```
<fieldtype name="text" class="solr.TextField" autoGeneratePhraseQueries="true">
       <analyzer type="index">
           <tokenizer class="solr.StandardTokenizerFactory"/>
           <filter class="solr.LowerCaseFilterFactory"/>
       </analyzer>
       <analyzer type="query">
           <tokenizer class="solr.StandardTokenizerFactory"/>
           <filter class="solr.LowerCaseFilterFactory"/>
           <filter class="solr.SynonymGraphFilterFactory" 
                   synonyms="synonyms.txt" 
                   ignoreCase="false" 
                   expand="true"/>
           <filter class="sc.SynonymAwareStopFilterFactory" 
                   words="stopwords.txt" 
                   ignoreCase="true"/>
       </analyzer>
</fieldtype>
```

and this is a minimal request handler:

```
<requestHandler name="/def" class="solr.SearchHandler" default="true">
       <lst name="defaults">
           <bool name="sow">false</bool>
           <str name="df">title</str>
           <str name="defType">lucene</str>
           <bool name="debug">true</bool>
       </lst>
   </requestHandler>
```

Running the previous query:

```
q=tv went out of warranty something of
```

we have the following:

```
title:tv title:went (title:oow PhraseQuery(title:"out of warranty")) title:something
```

if we use instead the other synonym variant:

```
q=tv went oow something of
```

we have the following:

```
title:tv title:went (PhraseQuery(title:"out of warranty") title:oow) title:something
```

Everything seems working as expected! This is probably just one specific scenario among those addressed by LUCENE-4065; however, it helped me a lot because this is (at least in my experience) a frequent use case.

As usual, any feedback is warmly welcome. See you next time!

Did I mention we do [Apache Solr Beginner](https://sease.io/training/apache-solr-training/apache-solr-beginner-training) and [Elasticsearch Beginner](https://sease.io/training/elasticsearch-trainings/elasticsearch-beginner-training) training?  
We also provide consulting on these topics, [get in touch](https://sease.io/contacts) if you want to bring your search engine to the next level!

Did you like this post about Synonyms + Stopwords? Don’t forget to subscribe to our Newsletter to stay always updated from the Information Retrieval world!

[I have read and agree the Privacy Policy](https://sease.io/privacy-policy)

Leave this field empty if you're human: