---
title: 'When and How to Use N-grams in Elasticsearch'
company: Sease
tag: 索引构建
date: 2023-12-18
url: https://sease.io/2023/12/when-and-how-to-use-n-grams-in-elasticsearch.html
account: 
origin: harvest3-202607
---
The costs associated with Elasticsearch’s n-gram tokenizer are sometimes not considered enough. If you search on StackOverflow, you find **a lot of questions from people who use n-gram lightly**, not considering the impact in terms of performance, memory footprint, and index size.

Most of the time, people don’t have a deep knowledge of how to use search engines like Elasticsearch, they find a solution that uses n-grams, it works and they are happy. For example, if you search the term “wi-fi” and you also want to match “wi fi”, a solution with n-gram can work **but there are better solutions in terms of performance and index size**.

This blog post aims to **describe the use cases where n-grams are useful, explain the risks of using them**, and present some alternative solutions that should be considered.

## What are n-grams?

All the Lucene-based search engines like Elasticsearch use text analyzers to manipulate the text at index time and query time. Each analyzer is composed of:

* a tokenizer that splits the input sequence of characters into a list of tokens [[official documentation](https://www.elastic.co/guide/en/elasticsearch/reference/8.11/analysis-tokenizers.html)]
* a list of filters that process the stream of tokens [[official documentation](https://www.elastic.co/guide/en/elasticsearch/reference/8.11/analysis-tokenfilters.html)]

For example, the standard tokenizer breaks the text into words allowing you to search for each of them. The sentence `"The quick brown fox jumps over the lazy dog"` becomes the list of words `["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]`.

The n-gram is a sequence of n adjacent characters. They are collected from a text extracting all the substrings of size n. For example, the 2-grams for the sentence `"The quick fox"` becomes `["Th", "he", "e ", " q", "qu", "ui", "ic", "ck", "k ", " f", "fo", "ox"]`.

ElasticSearch gives you the possibility to generate n-grams at the tokenizer level and filter level. **The n-gram tokenizer acts on the whole source string while the n-gram filter acts on each token**.

##### N-GRAM TOKENIZER EXAMPLE

The n-gram tokenized transforms the source string into multiple n-gram lists from `min_gram` to `max_gram`. As you can see in the official documentation, by default `min_gram = 1` and `max_gram = 2`.

Indeed, in the example below, you can see the original string transformed into the lists of 1-gram and 2-gram.

###### REQUEST

```
				
					GET _analyze 
{
"tokenizer": "ngram", 
"text": "the fox" 
}
				
			
```

###### RESPONSE

```
				
					{
 "tokens": [
  {"token":"t", "start_offset":0,"end_offset":1},
  {"token":"th","start_offset":0,"end_offset":2},
  {"token":"h", "start_offset":1,"end_offset":2},
  {"token":"he","start_offset":1,"end_offset":3},
  {"token":"e", "start_offset":2,"end_offset":3},
  {"token":"e ","start_offset":2,"end_offset":4},
  {"token":" ", "start_offset":3,"end_offset":4},
  {"token":" f","start_offset":3,"end_offset":5},
  {"token":"f", "start_offset":4,"end_offset":5},
  {"token":"fo","start_offset":4,"end_offset":6},
  {"token":"o", "start_offset":5,"end_offset":6},
  {"token":"ox","start_offset":5,"end_offset":7},
  {"token":"x", "start_offset":6,"end_offset":7}
 ]
}
				
			
```

The search engine has to index a higher number of tokens with a significant impact on the storage size, memory footprint, and CPU used for indexing and searching.

##### Edge n-gram tokenizer example

There is also a lighter version of the n-gram tokenizer `edge_ngram` that generates all the n-grams at the beginning of the string:

###### REQUEST

```
				
					GET _analyze
{
 "tokenizer": "ngram",
 "text": "the fox"
}
				
			
```

###### RESPONSE

```
				
					{
 "tokens":[
  {"token":"t","start_offset":0,"end_offset":1},
  {"token":"th","start_offset":0,"end_offset":2}
 ]
}
				
			
```

##### Edge n-gram filter example

If you want to get the list of n-grams at the beginning of each word, you should use a custom analyzer composed by a tokenizer that splits the text into words, and then apply the edge\_ngram filter, as you can see in the example below:

###### REQUEST

```
				
					GET _analyze 
{ 
"tokenizer": "standard",
"filter": [ 
{ 
"type": "edge_ngram",
"min_gram": 2,
"max_gram": 3 
} 
],
"text": "the quick fox" 
}
				
			
```

###### RESPONSE

```
				
					{ 
 "tokens":[
  {"token":"th","start_offset":0,"end_offset":3}, 
  {"token":"the","start_offset":0,"end_offset":3}, 
  {"token":"qu","start_offset":4,"end_offset":9}, 
  {"token":"qui","start_offset":4,"end_offset":9}, 
  {"token":"fo","start_offset":10,"end_offset":13}, 
  {"token":"fox","start_offset":10,"end_offset":13} 
 ] 
}
				
			
```

Given the high potential and the high cost of using the n\_gram tokenizer, we should only use it if it’s strictly necessary, and if there is not a better solution.

## Where is the n-gram often used?

As said before, the n-gram tokenizer is useful to match the partial text. Let’s analyze some cases where it is used most frequently.

##### Prefix search / search-as-you-type

To implement the prefix search we can use the n-gram tokenizer/filter and the solution works because the prefix is one of the n-gram generated and stored in the index. On the other side, we produce a lot of n-grams that we never use. The edge\_ngram tokenizer is by far a better option because it only generates the prefixes.

We need to be aware that Elasticsearch has the Search-as-you-type field type that is optimized for the prefix search. It generates multiple fields that use n-grams and shingle tokens [[official documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-as-you-type.html#search-as-you-type)]

##### Suffix search

What we said for the prefix search is still valid: a solution that uses n-gram can work to match all suffixes. If we don’t want to generate all n-grams to match only suffixes, we can consider that, if we revert the text, the suffix becomes a prefix. We can then create our custom analyzer with a [reverse filter](https://www.elastic.co/guide/en/elasticsearch/reference/8.10/analysis-reverse-tokenfilter.html) first and then we apply the edge\_ngram filter.

##### Error correction/Did you mean feature

If a user writes a typo in its search, we would like the search engine to ignore the typos and find the correct word. If our index stores multiple n-grams of the original text, a reasonable percentage of tokens can probably be found anyway.

###### TEXT

“`The brown fox`” -> [“Th”, “he”, “e “, ” b”, “br”, “ro”, “ow”, “wn”, “n “, ” f”, “fo”, “ox”]

###### QUERY

“`The rown fox`” -> [“**Th**“, “**he**“, “**e**“, “~~r~~“, “**ro**“, “**ow**“, “**wn**“, “**n**“, “**f**“, “**fo**“, “**ox**“]

In the example above, the text matches 10 tokens over the 11 tokens of the query so it can be considered as a relevant result.

Even if we may think the n-gram-based solution can work, Elasticsearch implements

* the term suggester based on the edit distance that can ignore typos without creating all n-grams [[official documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-suggesters.html#term-suggester)]
* the sentence suggester that implemented on top of the term suggester but it uses the co-occurrences and frequencies of tokens to determine the best option [[official documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-suggesters.html#phrase-suggester)]

##### Compound words

If we deal with languages that don’t use spaces or that have long compound words, we may want to search for a word in the middle of the compounded word. In German, we have the word `Orangensaft` (orange juice) and the word `Saft` (juice). If the user wants to retrieve all documents mentioning juice (`Saft`), it should be able to find the document that talks about orange juice (`Orangensaft`) even if there is not a space to split the words.

In this case, the n-gram solution works but it can be considered as a brute force approach that requires a lot of resources while it’s probably a better idea to use a library or a tool to split the original compound words at index time.

For example, after a quick search, I was able to find some free libraries to split compound words

* <https://pypi.org/project/compound-word-splitter/>
* <https://github.com/repodiac/german_compound_splitter>

##### Not whitespace delimiter

Finally, let’s analyze the example shown in the indroduction of this blogpost. We may want to search for words that can be connected by the character “-” like “wi-fi” or “hard-working”. Or maybe we have words formatted in camel case like “nGram” or “ElasticSearch”. Retrieving this kind of terms can be easily solved by using the n-gram but, as we said before, we waste a lot of resources when there is a better solution.

In ElasticSearch **we have the “word delimiter graph” token filter** that splits a token into multiple ones depending on:

* non-alphanumeric characters (“hard-working” -> “hard”, “working”)
* case transitions (“ElasticSearch” -> “Elastic”, “Search”)
* letter-number transitions (“3gram” -> “3”, “gram”)

The word delimiter graph token filter allows many possible customizations depending on our needs [[official documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-word-delimiter-graph-tokenfilter.html)].

## Conclusion

> With great power comes great responsibility
>
> Uncle Ben

N-grams are a really powerful tool that, depending on the configuration, **may potentially allow us to match any possible substring of the original text**. This can be a very easy and implementation-free solution to solve many searching problems so it’s often used even if there are more lightweight and performing alternatives.

We showed a list of problems where n-grams are often used and we also presented some alternatives or smarter implementations to improve performance and use fewer resources.

## Need Help with this topic?​

If you're struggling with n-grams in Elasticsearch, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)