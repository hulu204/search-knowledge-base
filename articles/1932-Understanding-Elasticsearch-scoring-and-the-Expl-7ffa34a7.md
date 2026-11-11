---
title: 'Understanding Elasticsearch scoring and the Explain API'
company: Elastic
tag: 搜索相关性
date: 2025-05-05
url: https://www.elastic.co/search-labs/blog/elasticsearch-scoring-and-explain-api
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Understanding Elasticsearch scoring and the Explain API

Learn about Elasticsearch scoring mechanisms and the practical scoring function to audit search relevance and improve document ranking with the Explain API.

May 05, 2025

[Kofi Bartlett](/search-labs/author/kofi-bartlett)

[Basics](/search-labs/blog/category/basics)

Jump to

Share

Elasticsearch is a powerful search engine that provides fast and relevant search results by calculating a score for each document in the index. This score is a crucial factor in determining the order of the search results. In this article, we will delve into the scoring mechanism of Elasticsearch and explore the Explain API, which helps in understanding the scoring process.

## Scoring mechanisms in Elasticsearch

Elasticsearch uses a scoring model called the Practical Scoring Function (BM25) by default. This model is based on the probabilistic information retrieval theory and takes into account factors such as term frequency, inverse document frequency, and field-length normalization. Let’s briefly discuss these factors:

1. **Term Frequency (TF):** This represents the number of times a term appears in a document. A higher term frequency indicates a stronger relationship between the term and the document.
2. **Inverse Document Frequency (IDF):** This factor measures the importance of a term in the entire document collection. A term that appears in many documents is considered less important, while a term that appears in fewer documents is considered more important.
3. **Field-length Normalization**: This factor accounts for the length of the field in which the term appears. Shorter fields are given more weight, as the term is considered more significant in a shorter field.

## Using the Explain API

The Explain API in Elasticsearch is a valuable tool for understanding the scoring process. It provides a detailed explanation of how the score for a specific document was calculated. To use the Explain API, you need to send a GET request to the following endpoint:

```
GET /<index>/_explain/<document_id>
```

In the request body, you need to provide the query for which you want to understand the scoring. Here’s an example:

```
{
  "query": {
    "match": {
      "title": "elasticsearch"
    }
  }
}
```

The response from the Explain API will include a detailed breakdown of the scoring process, including the individual factors (TF, IDF, and field-length normalization) and their contributions to the final score. Here’s a sample response:

```
{
  "_index": "example_index",
  "_type": "_doc",
  "_id": "1",
  "matched": true,
  "explanation": {
    "value": 1.2,
    "description": "weight(title:elasticsearch in 0) [PerFieldSimilarity], result of:",
    "details": [
      {
        "value": 1.2,
        "description": "score(doc=0,freq=1.0 = termFreq=1.0\n), product of:",
        "details": [
          {
            "value": 2.2,
            "description": "idf, computed as log(1 + (docCount - docFreq + 0.5) / (docFreq + 0.5)) from:",
            "details": [
              {
                "value": 1,
                "description": "docFreq",
                "details": []
              },
              {
                "value": 1,
                "description": "docCount",
                "details": []
              }
            ]
          },
          {
            "value": 0.5,
            "description": "tfNorm, computed as (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * fieldLength / avgFieldLength)) from:",
            "details": [
              {
                "value": 1,
                "description": "termFreq=1.0",
                "details": []
              },
              {
                "value": 1.2,
                "description": "parameter k1",
                "details": []
              },
              {
                "value": 0.75,
                "description": "parameter b",
                "details": []
              },
              {
                "value": 1,
                "description": "avgFieldLength",
                "details": []
              },
              {
                "value": 1,
                "description": "fieldLength",
                "details": []
              }
            ]
          }
        ]
      }
    ]
  }
}
```

In this example, the response shows that the score of 1.2 is a product of the IDF value (2.2) and the tfNorm value (0.5). The detailed explanation helps in understanding the factors contributing to the score and can be useful for fine-tuning the search relevance.

## Conclusion

Elasticsearch scoring is a critical aspect of providing relevant search results. By understanding the scoring mechanisms and using the Explain API, you can gain insights into the factors affecting the search results and optimize your search queries for better relevance and performance.

### Frequently Asked Questions

#### What is scoring in Elasticsearch?

Scoring is the process of providing fast and relevant search results by calculating a score for each document in the index. This score is a crucial factor in determining the order of the search results.

#### How does the Explain API work?

To use the Explain API, you send a GET request to the /<index>/\_explain/<document\_id> endpoint with the query in the request body. It returns a detailed breakdown showing the individual factors (TF, IDF, and field-length normalization) and their contributions to the final score.

#### What are the benefits of using the Explain API?

The Explain API is a valuable tool for understanding the scoring process. It provides insights into the factors affecting search results, which is useful for fine-tuning search relevance and optimizing queries for better performance.

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