---
title: 'How Does Fuzzy Queries Work in Elasticsearch?'
company: Sease
tag: 查询理解
date: 2023-12-01
url: https://sease.io/2023/12/how-does-fuzzy-queries-work-in-elasticsearch.html
account: 
origin: harvest3-202607
---
How many of you have happened to execute fuzzy queries in Elasticsearch and not obtain the expected results?

Let’s dive together into fuzziness behaviour, seeing how it works in Elasticsearch, when to use it, and which elements to pay attention to.

## WHAT ARE FUZZY QUERIES?

As you can read from the Elasticsearch documentation[[1]](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-fuzzy-query.html):

> *Fuzzy queries are queries that return documents that contain terms close to the search term, as measured by a [Levenshtein edit distance](https://en.wikipedia.org/wiki/Levenshtein_distance).*

An edit distance is the number of one-character changes needed to turn one term into another. These changes can include:

* Changing a character (**b**ox → **f**ox)
* Removing a character (**b**lack → lack)
* Inserting a character (sic → sic**k**)
* Transposing two adjacent characters (**ac**t → **ca**t)

If you type something like *Elasticsearc*; the Levenshtein distance with *Elasticsearch* is **1**, since you just need to add the ***h*** character at the end to turn one term into the other: *Elasticsearc**h***.  
If you type something like *Elastacsearc*; the Levenshtein distance with *Elasticsearch* is **2**, since you need to make two changes to turn one term into the other: *Elastacsearc* -> *Elast**i**csearc* -> *Elast**i**csearc**h**.*

## How to Perform a Fuzzy Query in Elasticsearch

There are three possible ways of doing a fuzzy query:

1. With the **`fuzzy`** clause in the query Domain Specific Language (DSL) of Elasticsearch [[1]](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-fuzzy-query.html);
2. With the **`fuzziness`** parameter, where supported by the queries API you are using [[2]](https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#fuzziness);
3. Using the ***~*** operator in the `query_string` query [[3]](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-fuzziness).

Let’s see some examples!

Suppose we indexed a book collection in Elasticsearch, and suppose we would like to retrieve all the documents with an author name equal to *“thomas”* but the user wrongly typed *“toma”.*

##### 1. perform a fuzzy query With the fuzzy clause

```
				
					GET /_search 
{ 
 "query": { 
  "fuzzy": { 
   "name": { 
    "value": "toma" 
   } 
  } 
 }
}
				
			
```

Here, to find similar terms, the `fuzzy` query creates a set of all possible variations, or expansions, of the search term within a specified edit distance. The query then returns exact matches for each expansion [[1]](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-fuzzy-query.html).

In this example:

* **`name`** is the **field** to search on;
* **`value`** is the term to find in the provided field

There are several other parameters for the fuzzy query. If you want to go into detail, you can read about them in the [documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-fuzzy-query.html#fuzzy-query-top-level-params). Here I would like to talk to you about the **`fuzziness`** and **`max_expansions`** parameters.

###### the fuzziness parameter in elasticsearch

**`fuzziness`** is the maximum edit distance allowed for matching [[2]](https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#fuzziness). Therefore our maximum Levenshtein distance. It can assume two values:

* `0, 1, 2`: the number of edits (Levenshtein distance);
* `AUTO`: generates an edit distance based on the length of the term.   
  Low and high distance arguments may be optionally provided `AUTO:[low],[high]`.   
  If not specified, the default values are 3 and 6, equivalent to `AUTO:3,6` that make short words (length <= 2) match exactly, medium-length words (3 <= length <= 5) accept one edit, and long words (length > 5) accept two edits.

###### the max\_expansions parameter in elasticsearch

**`max_expansions`** is the maximum number of variations created. Defaults to `50`. Pay attention to the value you choose here since a high value in `max_expansions` can cause poor performance due to the high number of variations examined.

##### 2. perform a fuzzy query with the fuzziness parameter

```
				
					"query": { 
 "match": { 
  "text": { 
   "query": "toma", 
   "fuzziness": "2" 
  } 
 } 
}
				
			
```

Here we are asking for all the documents matching terms that have at most a Levenshtein distance of 2 from *toma*.   
The maximum allowed distance is defined in the `fuzziness` parameter.  
The `fuzziness` parameter is the same as defined in point 1 but used in a different query type.

##### 3. perform a fuzzy query using the ~ operator

```
				
					{ 
 "query": { 
  "query_string": { 
   "query": "toma~", 
   "fields" : ["author"] 
  } 
 } 
}
				
			
```

The main thing to keep in mind with this type of query is that the `query_string` passed is [normalized](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-normalizers.html).

**What is normalization?**

Normalization is a sort of text analysis that supports only per-character filters. This is because no tokenizer is used, only a single token is emitted, and therefore filters that need to look at the keyword as a whole cannot be used. Here you can find the list of the currently supported filters:

`arabic_normalization`,   
`asciifolding`,   
`bengali_normalization`,   
`cjk_width`,   
`decimal_digit`,   
`elision`,   
`german_normalization`,   
`hindi_normalization`,   
`indic_normalization`,   
`lowercase`,   
`pattern_replace`,   
`persian_normalization`,   
`scandinavian_folding`,   
`serbian_normalization`,   
`sorani_normalization`,   
`trim`,   
`uppercase`.

After normalization, the query behaviour follows the same process as points 1 and 2. A set of all possible variations, or expansions, of the search term within a specified edit distance is created and the exact matches for each expansion are returned from the query.

The default *edit distance* is `2`, but a different edit distance can be specified as:

```
quikc~1
```

## Best Practices: What to Pay Attention to with Fuzzy Queries in Elasticsearch

From what we have learned so far, there are four main things to pay attention to:

##### PERFORMANCE

When using fuzzy queries a great set of variations/expansions is created and the search considers matches with all of them. This is a very expensive process that could lead to poor performance at query time. You can read more about this in [this Elasticsearch blog post](https://www.elastic.co/blog/found-fuzzy-search#performance-considerations).

##### NORMALIZATION

When using the ~ operator in the `query_string` clause normalization is done. Be aware that this modifies the way text analysis is executed since only specific filters are applied. This also changes the final query construction.   
Let’s see an example [[4]](https://stackoverflow.com/questions/74366441/which-analyzer-is-used-while-using-fuzzy-operator-with-query-string-clause). Suppose to execute a query like:

```
				
					{ 
 "query": { 
  "query_string": { 
   "query": "dog toma~", 
   "fields": [ 
    "title", 
    "author" 
    ], 
   "default_operator": "and" 
  } 
 } 
}
				
			
```

**When using fuzziness, the query text is split by whitespaces**. Then, for each term, a mandatory clause is built (the AND operator states that each term MUST appear in the document). You can call this a **“term-centric” query**. Then each term is searched across the multiple fields in input with a disjunction (|) clause. You therefore see:

```
				
					"explanation": "+(title:dog | author:dog) +(title:toma~1 | author:toma~1)"
				
			
```

“dog MUST be in title OR author, AND toma (with variations within the [Levenshtein\_distance](https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance)) MUST be in title OR author”

If **no fuzziness is used, the query is passed to each field and then the terms will follow the corresponding field text analysis** (if any). You may call this a **“field-centric” query**. Therefore you see:

```
				
					"explanation": "(title:dog toma | author:dog toma)"
				
			
```

“dog toma MUST be in title OR author”

You are effectively moving from an “I want all the terms to appear in the document” (it could be in different fields) to “I want all terms to appear in a single field” [[8]](https://sease.io/2021/05/apache-solr-sow-parameter-split-on-whitespace-and-multi-field-full-text-search.html).

##### WILDCARDS

Avoid mixing fuzziness and wildcards [[5]](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#avoid-widlcards-fuzzy-searches). This is not supported in Elasticsearch.

##### CHOOSE THE BEST FUZZY OPTION

From [[6]](https://www.elastic.co/blog/found-fuzzy-search), a match query with the `fuzziness` parameter set is perhaps the most versatile of the fuzzy queries. The fuzzy query type supports the exact same behaviour, except it does not allow for any analysis of the query text. Additionally, the `fuzzy` query type is a subset of the functionality of a match query makes it more confusing than useful.

## Fuzzy Search Alternatives

Sometimes, fuzzy search is not the best solution for imprecise matches [[6]](https://www.elastic.co/blog/found-fuzzy-search). There are good alternatives that can be used depending on your necessities:

1. Using a [phonetic analysis plugin](https://www.elastic.co/guide/en/elasticsearch/plugins/current/analysis-phonetic.html) can help in finding words that sound similar to other words.
2. Using [N-grams](https://sease.io/2023/12/when-and-how-to-use-n-grams-in-elasticsearch.html) can speed up that query process leading to the same good results since a search just needs to have a plurality of matches of sub-parts of a given term [[7]](https://web.archive.org/web/20140209084956/http://exploringelasticsearch.com/book/searching-natural-language/searching-non-word-text.html). N-grams do, however, come at the cost of additional storage/memory usage, slightly more index-time processing, and a long tail of false positives after good matches [[6]](https://www.elastic.co/blog/found-fuzzy-search).

## Need Help with this topic?​

If you're struggling with fuzzy queries in Elasticsearch, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)