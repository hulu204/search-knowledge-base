---
title: 'Solr AutoGeneratePhraseQueries and Minimum Should Match with Synonyms'
company: Sease
tag: 查询理解
date: 2025-05-26
url: https://sease.io/2025/05/solr-autogeneratephrasequeries-and-minimum-should-match-with-synonyms.html
account: 
origin: harvest3-202607
---
Hi readers!

Exploiting the features of Solr, we encounter an interesting behaviour when using together the **autoGeneratePhraseQueries** parameter, **synonyms** and the **minimum should match** parameter.

Probably not all of you are aware of this, so let’s see it together!

## What is the autoGeneratePhraseQueries parameter?

As reported in Solr documentation: *“For text fields. If true, Solr automatically generates phrase queries for adjacent terms. If false, terms must be enclosed in double quotes to be treated as phrases.”*

Also in [Solr 3.x *CHANGES.txt*](https://lists.apache.org/thread/1815ltywr8mhqlsh2cwzlwdk411vnjwy):

*[SOLR-2015](https://issues.apache.org/jira/browse/SOLR-2015): “autoGeneratePhraseQueries=”true” causes the query parser to generate phrase queries if multiple tokens are generated from a single non-quoted analysis string. For example WordDelimiterFilter splitting text:pdp-11 will cause the parser to generate text:”pdp 11″ rather than (text:PDP OR text:11). Note that autoGeneratePhraseQueries=”true” tends to not work well for non whitespace delimited languages.”*

As clearly described in this last citation, **this parameter generates phrase queries whenever multiple tokens are generated from a single non-quoted analysis string**.  
This is also the case with the [synonym graph filter](https://solr.apache.org/guide/solr/latest/indexing-guide/filters.html#synonym-graph-filter) when dealing with multi-token synonyms. Every time a word is detected in the synonym file and has a corresponding multi-token translation, this generated string will be treated by Solr as a quoted string, leading to a phrase query (exact match required).

***Want to explore more about it? Read our post on [Apache Solr autoGeneratePhraseQueries and Schema](https://sease.io/2024/12/solr-autogeneratephrasequeries-schema-version.html)***

## What is the synonym graph filter?

From [Solr documentation](https://solr.apache.org/guide/solr/latest/indexing-guide/filters.html#synonym-graph-filter): *“This filter does synonym mapping. Each token is looked up in the list of synonyms and if a match is found, then the synonym is emitted in place of the token. This filter maps single- or multi-token synonyms, producing a fully correct graph output. This filter is a replacement for the Synonym Filter, which produces incorrect graphs for multi-token synonyms.”*

Synonyms are defined in a dedicated file, which could contain:

* A comma-separated list of words. If the token matches any of the words, then all the words in the list are substituted, which will include the original token.
 * Two comma-separated lists of words with the symbol “=>” between them. If the token matches any word on the left, then the list on the right is substituted. The original token will not be included unless it is also in the list on the right.

For example:

```
				
					couch,sofa,divan
teh =&gt; the
huge,ginormous,humungous =&gt; large
small =&gt; tiny,teeny,weeny
				
			
```

The case of interest for this “tips and tricks” is when dealing with multi-token synonyms like:

```
				
					science fiction,sci fi,scifi,sci-fi
				
			
```

Here, a single token query like scifi will be translated into more than one token science fiction etc. We therefore would like to match the entire generated string exactly as written and not the single tokens as separate units.

## What is the minimum should match parameter?

From [Solr documentation](https://solr.apache.org/guide/solr/latest/query-guide/dismax-query-parser.html#mm-minimum-should-match-parameter): *“When processing queries, there are three types of clauses: mandatory, prohibited, and “optional” (also known as “should” clauses). By default, all words or phrases specified in the `q` parameter are treated as “optional” clauses unless they are preceded by a “+” or a “-“. When dealing with these “optional” clauses, the `mm` parameter makes it possible to say that a certain minimum number of those clauses must match.”*

Suppose we do a query like: “**Dorian Grey book 1890**” with mm=2, what we expect is for Solr to return documents that match at least two of the required 4 tokens. They could be any of the tokens since they are considered independent OR clauses.

## Use Case

Suppose to have the *text\_general* field type with this simple text analysis in your schema:

![](https://i0.wp.com/sease.io/wp-content/uploads/2024/09/Screenshot-2024-09-19-at-17.23.02.png?fit=1196%2C259&ssl=1)

Where this is the content of the *synonyms.txt* file:

![](https://i0.wp.com/sease.io/wp-content/uploads/2024/09/Screenshot-2024-09-19-at-17.24.00.png?fit=390%2C47&ssl=1)

We have defined *autoGeneratePhraseQueries* to be *true* and suppose *\_text\_* to be a field with the *text\_general* type.

When doing a search like *“australia”* with the *minimum should match* set to *3*, we can see Solr parsing the query and expanding it with its synonym *“land of kangaroos”*. Since it is a *multi-token* synonym and we have declared *autoGeneratePhraseQueries* to be *true*, Solr is generating a phrase query for the synonym, leading to this parsed result query.

Query:

```
				
					"params": {
  "mm": "3",
  "q": "australia",
  "defType": "edismax",
  "debugQuery": "true"
}
				
			
```

Parsed query:

```
				
					+DisjunctionMaxQuery(((((_text_:\"land ? kangaroos\" _text_:australia))~1)))
				
			
```

As you can see *land of kangaroos* is surrounded by double quotes (*of* is substituted with *?* because of the stopwords removal) as wanted, and ~1 is added due to the *minimum should match* parameter (we only have one query term and therefore 1 is the max number of clauses we can require to be present).

##### What about the opposite?

Suppose we do the search *“land of kangaroos”* with the *minimum should match* set to *3*, we can see Solr parsing the query and expanding it with its synonym *“australia”*. This is the result.

Query:

```
				
					"params": {
  "mm": "3",
  "q": "land of kangaroos",
  "defType": "edismax",
  "debugQuery": "true"
}
				
			
```

Parsed query:

```
				
					+DisjunctionMaxQuery(((_text_:australia _text_:\"land ? kangaroos\")))
				
			
```

Here, having the *autoGeneratePhraseQueries* set to true and having the query text match a synonym is actually limiting the search. **Solr is not searching for the single terms *land* and *kangaroos* as different clauses, but is putting them in a phrase query, requiring to have an exact match of the phrase with the index.** **Also, the minimum should match parameter is ignored.**This would indeed be the expected behaviour:

```
				
					+(DisjunctionMaxQuery((_text_:australia)) DisjunctionMaxQuery((_text_:land)) DisjunctionMaxQuery((_text_:kangaroos)))~2
				
			
```

Behaviour obtained with all those queries that do not match the synonyms file:

```
				
					{
  "mm": "3",
  "q": "beautiful land",
  "defType": "edismax",
  "debugQuery": "true"
}
				
			
```

Which is parsed to:

```
				
					+(DisjunctionMaxQuery((_text_:beautiful)) DisjunctionMaxQuery((_text_:land)))~2
				
			
```

## Final Considerations

Determine if this is the “correct” behaviour actually depends on your use case and what you would like to obtain from the query.

Solr is currently moving the search more to precision rather than recall. It searches for documents that exactly match the query, knowing that the user’s information need (query) corresponds to a concrete “entity” thanks to the synonyms file.

**If you therefore use all these parameters together, pay very high attention to how you declare the synonyms file content, since it would highly impact the final queries and corresponding results.**

## Need Help with this topic?​

If you're struggling with Solr AutoGeneratePhraseQueries, Minimum Should Match or/and Synonyms, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with Solr AutoGeneratePhraseQueries, Minimum Should Match or/and Synonyms, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)