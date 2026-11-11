---
title: 'Configuring recursive chunking for structured documents in Elasticsearch'
company: Elastic
tag: RAG
date: 2025-11-11
url: https://www.elastic.co/search-labs/blog/recursive-chunking-structured-documents-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Configuring recursive chunking for structured documents in Elasticsearch

Learn how to configure recursive chunking in Elasticsearch with chunk size, separator groups, and custom separator lists for optimal structured document indexing.

November 11, 2025

[Daniel Rubinstein](/search-labs/author/daniel-rubinstein)

[Basics](/search-labs/blog/category/basics)[Inside Elastic](/search-labs/blog/category/inside-elastic)[AI](/search-labs/blog/category/ai)

Jump to

Share

Since 8.16, users have been able to configure the chunking strategy used when ingesting long documents into semantic text fields. As of 9.1 / 8.19, we have introduced a new configurable recursive chunking strategy that uses a list of regular expressions to chunk the document. The goal of chunking is to split a long document into sections that encapsulate related content. Our existing strategies will split text up on a granularity of words/sentences, but documents written in structured formats (ex. Markdown) often contain related content within sections that are defined by some separating strings (ex. headers). For these types of documents, we are introducing the recursive chunking strategy to leverage the format of structured documents to create better chunks!

## What is recursive chunking?

Recursive chunking will iterate through a list of provided sections separating patterns to progressively break a document into smaller segments until they meet a desired maximum chunk size.

### How do I configure recursive chunking?

The following are the configurable values provided by the user for recursive chunking:

* (required) `max_chunk_size`: The maximum number of words in a chunk.
* Either one of:

  + `separators`: A list of regex string patterns that will be used to split the document into chunks.
  + `separator_group`: A string that will map to a default list of separators defined by Elastic to use for specific types of documents. Currently, `markdown` and `plaintext` are available.

### How does recursive chunking work?

The process of recursive chunking given an input document, a `max_chunk_size` (measured in words), and a list of separator strings is as follows:

1. If the input document is already within the maximum chunk size, return a single chunk spanning the entire input.
2. Split the text into potential chunks based on occurrences of the separator. For each potential chunk:

   1. If the potential chunk is within the maximum chunk size, add it to the list of chunks to return to the user.
   2. Otherwise, repeat from step 2, using only the text from the potential chunk and splitting using the next separator in the list. If there are no more separators left to try, fall back to sentence-based chunking.

## Examples of configuring recursive chunking

Aside from chunk size, the main configuration for recursive chunking is selecting which separators should be used to split up your documents. If you’re not sure where to start, Elasticsearch offers a few default separator groups that can be used for common use cases.

### Utilizing separator groups

To utilize a separator group, simply provide the name of the group you would like to use when configuring chunking settings. For example:

```
"chunking_settings": {
    "strategy": "recursive",
    "max_chunk_size": 25,
    "separator_group": "plaintext"
}
```

This will give you a recursive chunking strategy that utilizes the separator list `["(?<!\\n)\\n\\n(?!\\n)", "(?<!\\n)\\n(?!\\n)")]`. This works well for generic plain text applications, splitting on 2 newline characters, followed by 1 newline character.

We also offer a separator group `markdown` which will utilize the separator list:

```
[
"\n# ",
       "\n## ",
       "\n### ",
       "\n#### ",
       "\n##### ",
       "\n###### ",
       "\n^(?!\\s*$).*\\n-{1,}\\n",
       "\n^(?!\\s*$).*\\n={1,}\\n"
]
```

This separator list will work well for general markdown use cases, splitting on each of the 6 heading levels and the section-breaking characters.

When creating a resource (inference endpoint/semantic text field), the list of separators corresponding to the separator group at the time will be stored in your configurations. If the separator group is updated at a later date, it will not change the behaviour of your already created resources.

### Utilizing a custom separator list

If one of the predefined separator groups does not work for your use case, you can define a custom list of separators that fits your needs. Note that regular expressions can be provided within the separator list. The following is an example of chunking settings configured with custom separators:

```
"chunking_settings": {
    "strategy": "recursive",
    "max_chunk_size": 25,
    "separators": ["\n\n", "\n", "<my-custom-separator>"]
}
```

The above chunking strategy will split on 2 newline characters, followed by 1 newline character, and lastly on a string `“<my-custom-separator>”`.

## An example of recursive chunking in action

Let’s see an example of recursive chunking in action. For this example, we’ll use the following chunking settings with a custom list of separators that split a markdown document using the top two header levels:

```
"chunking_settings": {
    "strategy": "recursive",
    "max_chunk_size": 25,
    "separators": ["\n# ", "\n## "]
}
```

Let’s take a look at a simple unchunked Markdown document:

![An unchunked Markdown document](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltdb5f41d1bd43ba50/6a17e831e9ea87c1d8a9c5f3/3a5507f4a1288065097231548e5b18e240508785-1302x1446.png)

Now let’s use the chunking settings defined above to chunk the document:

![Chunking a document in Elasticsearch](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltfffda162c7b9c87a/6a17e83296142aefa8eb1b0b/a3313c4c40ff39b8dbcdd7c4878c723f088e6c1a-1600x1187.png)![Splitting on second separator- chunking a document in Elasticsearch](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt96f65346a8e09e3a/6a17e834445de9157b4d015e/79a2921943191ea631df94c9d465818ec8d3e738-1600x1206.png)![Final chunks in a document after sentence based chunking in Elasticsearch](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt28381c8f85aedf07/6a17e836ec0f89801e5a6640/459e695cce7540267422396b9a62ff4ad35f61db-1600x1260.png)

Note: The newline at the end of each chunk (except Chunk 3) is not highlighted but is included within the actual chunk boundaries.

### Get started with recursive chunking today!

For more information on utilizing this feature, view the documentation on [configuring chunking settings](https://www.elastic.co/docs/explore-analyze/elastic-inference/inference-api#chunking-strategies).

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt6d8bd040a15da207/6a17e422414c640e67945116/ef9edded97edd7c919e617e648e62016155cde56-720x420.jpg)

[Basics](/search-labs/blog/category/basics)

### Parsing JSON fields in Elasticsearch

October 17, 2025|[Valentin Crettaz](/search-labs/author/valentin-crettaz)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt373f9290a1371dd7/6a17122e0c48579b2001abba/fd87bff40e296ebce871d631c86fd0245f11c796-1440x960.jpg)

[Javascript](/search-labs/blog/category/javascript-programming)[Basics](/search-labs/blog/category/basics)

### Automatically updating your Elasticsearch index using Node.js and an Azure Function App

June 04, 2024|[Jessica Garson](/search-labs/author/jessica-garson)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1a0bf009f00b1c80/6a1711fa4a531b3db636aa9f/c7c174d6408b23fca482664c608f9e8849243d96-1440x720.jpg)

[Basics](/search-labs/blog/category/basics)

### Adding document level security (DLS) to your internal knowledge search

January 22, 2024|[Sean Story](/search-labs/author/sean-story)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d7e4a5bbd9427c2/6a170e4d0e2e4905b641a1b7/04f1738a38cead88c9a67b0f863171b4b43010ab-1600x913.png)

[Basics](/search-labs/blog/category/basics)

### Elasticsearch plugin for UBI: Analyze user data in Kibana

September 26, 2025|[Eduard Martin](/search-labs/author/eduard-martin)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltc31c3bf0d453d846/6a170e12cdacbfdf6a7d2a7e/3ae41b1f2876d2ad11c8e2b79bbf79955d6902aa-1440x840.png)

[Java](/search-labs/blog/category/java-programming)[Basics](/search-labs/blog/category/basics)

### Testing Elasticsearch. It just got simpler.

March 19, 2026|[Piotr Przybyl](/search-labs/author/piotr-przybyl)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter