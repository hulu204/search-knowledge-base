---
title: 'How to search languages with compound words'
company: Elastic
tag: 查询理解
date: 2025-01-29
url: https://www.elastic.co/search-labs/blog/compound-word-search
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# How to search languages with compound words

Compound words present challenges in search engines during text analysis and tokenization, as they can obscure meaningful connections between word components. Tools like the Hyphenation Decompounder Token Filter help address these issues by deconstructing compound words.

January 29, 2025

[Peter Straßer](/search-labs/author/peter-straer)

[Relevance](/search-labs/blog/category/relevance)[Basics](/search-labs/blog/category/basics)

Jump to

Share

Germans are famous for their lengthy compound words: [*Rindfleischetikettierungsüberwachungsaufgabenübertragungsgesetz*](https://en.wikipedia.org/wiki/Rinderkennzeichnungs-_und_Rindfleischetikettierungs%C3%BCberwachungsaufgaben%C3%BCbertragungsgesetz) is the longest word in the german dictionary — and a nightmare for search engines unprepared to handle compounding. Many other languages such as Dutch, Swedish and others have this concept as well. Even English - though to a lesser extent - has some of these words. Think about “sunflower” or “basketball”.

Let’s discuss the problems and challenges that come with compound word search, why this is an issue and how to address it.

## The problem with compound word search

When doing full text searches, search engines such as Elasticsearch analyze text during the query and indexing time and turn the text into tokens. Rather than exactly matching the string, we want to extract the *meaning* of the word. For our search, we don't worry about whether the bunny is “running” or “runs” —we simply reduce the word to its root form: "run."

When we are dealing with compound words this stage will fail if we don’t address it and handle it in a certain way. Imagine we have an index with a document: “Basketballs”. If we were to \_analyze this with the standard English analyzer we get:

```
GET _analyze
{
  "text": "Basketballs", 
  "analyzer": "english"
}
```

Response:

```
{
  "tokens": [
    {
      "token": "basketbal",
      "start_offset": 0,
      "end_offset": 11,
      "type": "<ALPHANUM>",
      "position": 0
    }
  ]
}
```

In this example, the compound word 'basketballs' is tokenized into 'basketbal'. While we were able to lowercase and remove the plural form of the word, we were not able to capture the meaning that a basketball is also a ball. Now if we were to search for “ball” within our index we would expect to find our basketball - but “bal” (analyzed) does not match “basketbal”, so we are not getting any results!

How do we address this problem?

## Can synonyms solve compound word search?

The first thought we might have is to try synonyms to associate the different sub words with our compound words. This works well enough for English because of the fairly limited use of compound words:

```
basketball => basketball, ball
```

Now let’s take a look at German. The way that the grammar works is that any arbitrary amount of words can be combined to form a more precise word.

*Rind* (cow) and *Fleisch* (meat) become *Rindfleisch* (cowmeat/beef).

*Rind* (cow), *Fleisch* (meat) and *Etikett* (label) become *Rindfleischetikett* (cowmeatlabel). This can be done at arbitrary length until we get lovely words such as *Rindfleischetikettierungsüberwachungsaufgabenübertragungsgesetz.*

To solve this with our synonyms file we would have to model an infinite amount of permutation of words:

```
# cowmeat, cowmeatlabel, meatlabel
rindfleisch => rindfleisch, rind, fleisch
rindfleischetikett => rindfleischetikett, rind, fleisch, etikett
fleischetikett => fleischetikett, fleisch, etikett
…
```

In languages such as German this becomes impractical really quickly. So we have to approach the problem from the opposite angle. We don’t go from the compound word to its compounds but rather we look at the available compound parts and deconstruct the word based on this knowledge.

## Using the Hyphenation Decompounder for compound word search​

The [Hyphenation Decompounder Token Filter](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-hyp-decomp-tokenfilter.html) is a Lucene token filter that relies on hyphenation rules to detect potential word splits. Rule files are specified in the [Objects For Formatting Objects (OFFO)](https://offo.sourceforge.net/#FOP+XML+Hyphenation+Patterns) format, where we can also find some example files. We also need a list of words that is used to decompound the compound words into their sub-parts. The word list can be provided inline, but for production workloads we typically also upload a file to disk as these files can be quite large and typically contain entire dictionaries.

Example files for the German language, provided under their license, can be found in [this repository](https://github.com/uschindler/german-decompounder/tree/master).

So what does it do?

```
# word list: coffee, sugar, cup
# text: coffee cup
GET _analyze
{
  "tokenizer": "standard",
  "filter": [
    "lowercase",
    {
      "type": "hyphenation_decompounder",
      "hyphenation_patterns_path": "analysis/hyphenation_patterns.xml",
      
      "word_list": ["kaffee", "zucker", "tasse"]
    }
  ],
  "text": "Kaffeetasse"
}

Response:

# coffee cup, coffee, cup
[ "kaffeetasse", "kaffee", "tasse"]
```

This helps ensure that a user searching for “Tasse” (cup) can find documents that contain the larger compound “Kaffeetasse” (coffee cup).

Notes:

1. Check out [this article](https://www.elastic.co/guide/en/cloud/current/ec-custom-bundles.html) on how to upload a bundle to be able to access these files in your Elastic Cloud Hosted deployments.
2. There is also the [Dictionary Decompounder](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-dict-decomp-tokenfilter.html), which does the same thing without the hyphenation rules and instead brute forces the word detection. For most use cases we recommend the Hyphenation Decompounder.

### Avoiding partial matches

Because we typically use word lists of entire dictionaries with many thousand words, the decompounder may split words in unintended ways with the default settings, leading to irrelevant matches.

```
# word list: coffee, fairy, cup
# text: coffee cup
GET _analyze
{
  "tokenizer": "standard",
  "filter": [
    "lowercase",
    {
      "type": "hyphenation_decompounder",
      "hyphenation_patterns_path": "analysis/hyphenation_patterns.xml",
     
      "word_list": ["kaffee", "fee", "tasse"]
    }
  ],
  "text": "Kaffeetasse"
}

Response:

# coffee cup, coffee, fairy, cup
["kaffeetasse", "kaffee", "fee", "tasse"]
```

This example detects “fee” (fairy) within “Kaf**fee”** (coffee). This is of course accidental and not intended. Another example might be “St**reifen**bluse” (striped blouse) which finds “Reifen” (tires) in it. “Streifen” (stripe), “Reifen” (tire) and “Bluse” (blouse) are all common words that we would normally want to split on.

Our users searching for “fee” (fairies) and “reifen” (tires) now find coffee and blouses! That’s not good.

In 8.17 there is a new parameter `no_sub_matches` added to the`hyphenation_decompounder`to account for this problem.

```
# word list: coffee, fairy, cup
# text: coffee cup
GET _analyze
{
  "tokenizer": "standard",
  "filter": [
    "lowercase",
    {
      "type": "hyphenation_decompounder",
      "hyphenation_patterns_path": "analysis/hyphenation_patterns.xml",
      "word_list": ["kaffee", "fee", "tasse"],
      "no_sub_matches": true
    }
  ],
  "text": "Kaffeetasse"
}

Response:

# coffee cup, coffee, cup
["kaffeetasse", "kaffee", "tasse"]
```

This prevents creating the “fee” (fairy) token and our search works as expected!

### Matching all query terms

With what we have looked at so far an index mapping to search german text might look like something along this index definition:

```
PUT products
{
  "mappings": {
    "properties": {
      "full_text": {
        "type": "text",
        "analyzer": "german_analyzer_with_decompounding"
      }
    }
  },
  "settings": {
    "analysis": {
      "analyzer": {
        "german_analyzer_with_decompounding": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "german_stop_words_filter",
            "german_decompounder",
            "german_normalization",
            "german_stemmer"
          ]
        },
        "german_analyzer_without_decompounding": { 
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "german_stop_words_filter",
            "german_normalization",
            "german_stemmer"
          ]
        }
      },
      "filter": {
        "german_stop_words_filter": {
          "type": "stop",
          "stopwords": "_german_"
        },
        "german_decompounder": {
          "only_longest_match": "true",
          "word_list_path": "dictionary/dictionary.txt",
          "type": "hyphenation_decompounder",
          "hyphenation_patterns_path": "dictionary/hyphenation_patterns.xml"
        },
        "german_stemmer": {
          "type": "stemmer",
          "language": "light_german"
        }
      }
    }
  }
}
```

Note: In a real production setting there will most likely be filters around asciifolding, emoji filters or synonyms in there, but this is already a good starting point and should get good results for German text.

When searching for multiple terms we would typically expect (disregarding advanced query relaxation strategies) that all search terms that we specified are contained in our result. So when searching for Lederjacke (leather jacket) in an e-commerce store we expect our products to be *jackets* made out of *leather* and not a random assortment of leather products and jackets.

The way to achieve this is by setting the operator in our search query to AND. So we do that and search for “Lederjacke” (leather jacket) in our products:

```
GET products/_search
{
  "query": {
    "match": {
      "full_text": { 
        "query": "lederjacke",  
        "operator": "and" 
      }
    }
  }
}
# returns all leather products and all jackets
```

Perhaps surprisingly this does not behave as we might expect. We find all products that have *either* leather or jacket in them. This is because the operator gets evaluated before tokenization and the resulting tokens from the token filter get evaluated with an OR.

In order to fix this we need to decompound our terms within our application. We can do this by calling the `_analyze` API first and then passing the decompounded terms to our search query. Because we have already decompounded we are using a search analyzer without the decompounder filter in the filter chain.

```
GET _analyze
{
  "tokenizer": "standard",
  "filter": [
    "lowercase",
    {
      "type": "hyphenation_decompounder",
      "hyphenation_patterns_path": "analysis/hyphenation_patterns.xml",
      "word_list_path": "analysis/word_list.xml",
      "no_sub_matches": true
    }
  ],
  "text": "Lederjacke" 
}

Response: 

["leder", "jacke"]

GET products/_search
{
  "query": {
    "match": {
      "full_text": { 
        "query": "leder jacke",
        "operator": "and",
        "analyzer": "german_analyzer_without_decompounding"
      }
    }
  }
}
# returns only leather jackets
```

## Alternative ways to search decompounded words

While [Elasticsearch Serverless](https://www.elastic.co/guide/en/serverless/current/what-is-elasticsearch-serverless.html) comes with many great advantages for search applications due to its ability to dynamically scale depending on load, at the time of writing this article it is currently not possible to upload files and use the Hyphenation Decompounder in those projects.

### Alternative tools

Alternatives that can be used outside the Elastic stack are [JWordSplitter](https://github.com/danielnaber/jwordsplitter) which is available for Java and the [CharSplit](https://github.com/dtuggener/CharSplit) model or the [CompoundPiece](https://huggingface.co/benjamin/compoundpiece) model which apply a machine learning approach to decompound words without the need for configuration files.

Here's how you can use CompoundPiece with the Hugging Face transformers library:

```
from transformers import pipeline
pipe = pipeline("text2text-generation", model="benjamin/compoundpiece")
result = pipe("Lederjacke", max_length=100)
print(result[0]['generated_text'].split('-'))

STDOUT: ['Leder', 'Jacke']
```

It supports 56 languages and is able to work without configuration files, which is a nice way to get decompounding for multilingual applications.

### Semantic search

Something that we have covered in [many of our articles](https://www.elastic.co/search-labs/blog/multilingual-vector-search-e5-embedding-model) here is semantic search with text embedding models. These are able to interpret the meaning of text and can be searched by turning the documents and query into vectors and finding the closest documents to the query.

Combining lexical search as discussed here with vector search is called [hybrid search](https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-hybrid). This can also help to greatly improve the quality of your results and interpreting the meaning behind those compound words in your texts.

## Conclusion

Decompounding is an essential tool for building effective multilingual search applications - especially when languages such as German are involved. By using tools like the Hyphenation Decompounder, we can ensure that our search can understand the meaning behind compound words, delivering better and more relevant results for users.

As with any adjustment to your search algorithms, it's important to assess its overall impact on your search performance. Learn more about how to objectively measure the quality of your search results by exploring [our article on the \_eval APIs](https://www.elastic.co/blog/made-to-measure-how-to-use-the-ranking-evaluation-api-in-elasticsearch).

### Frequently Asked Questions

#### What is the Hyphenation Decompounder Token Filter?

The Hyphenation Decompounder Token Filter is a Lucene token filter that relies on hyphenation rules to detect potential word splits.

#### How to search languages with compound words?

You can search languages with compound word by using tools like the Hyphenation Decompounder. This tool ensures that your search can understand the meaning behind compound words, delivering better and more relevant results for users.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt29bbbf4463c73d8a/6a6a33fa55755baeaa2bd248/a6563ee307cc2d29722c490b043ee736c46974f3-1280x720.png)

[Jina AI](/search-labs/blog/category/jina-ai)[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

### 56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker

July 27, 2026|[Felix Wang](/search-labs/author/felix-wang)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3382265814939417/6a170df3a929cf1246ae0a61/fceada10b0c09d6a4a372f137bb3040e1ff41fbf-1600x895.png)

[ES|QL](/search-labs/blog/category/esql)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### Hybrid search and multistage retrieval in ES|QL

January 08, 2026|[Ioana](/search-labs/author/ioana-alina-tagirta)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt021070497c8cbd23/6a170aeab0367d782c72bd0e/c506a0f5c0a33ca6f85454d4f742d7cb266a7b78-715x413.png)

[Relevance](/search-labs/blog/category/relevance)

### ES|QL, you know, for Search - Introducing scoring and semantic search

April 16, 2025|[Ioana](/search-labs/author/ioana-alina-tagirta)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt360319cdeac21a74/6a6119f81b1d49b36a6f1823/8aaf734953fe5ae677062bf06aef7352f186657c-1280x720.png)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### AI shopping agents: Why context comes before the query

July 20, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter