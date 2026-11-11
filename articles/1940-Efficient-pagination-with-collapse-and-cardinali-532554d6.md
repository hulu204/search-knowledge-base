---
title: 'Efficient pagination with collapse and cardinality in Elasticsearch'
company: Elastic
tag: 工程相关
date: 2025-07-04
url: https://www.elastic.co/search-labs/blog/elasticsearch-pagination-with-collapse-and-cardinality
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Efficient pagination with collapse and cardinality in Elasticsearch

Deduplicating product variants in Elasticsearch? Here’s how to determine the correct pagination.

July 04, 2025

[Peter Steenbergen](/search-labs/author/peter-steenbergen)

[Basics](/search-labs/blog/category/basics)

Jump to

Share

In any large catalog, from e-commerce products to article listings, duplicates are inevitable. While Elasticsearch's **collapse** feature is excellent for grouping these variants and presenting a clean UI, it introduces a critical challenge for pagination. The total hit count reflects the original number of documents, not the final number of unique groups, making it impossible to build a reliable pager. This post details the definitive pattern to solve this by pairing collapse with a cardinality aggregation to get the true result count.

## Pagination with collapse and cardinality

In Elasticsearch, a frequent challenge in creating efficient search experiences, particularly in e-commerce, involves deduplication combined with pagination, the process of dividing a large set of data into smaller, manageable pages. For instance, a product catalog might include various versions (sizes, colors, SKUs) of the same product design.

Using the **collapse** feature, we can group hits by a single field to show a single representative result per group. This avoids flooding the UI with near-duplicates. Let’s walk through a practical example.

### Example: Combining SKUs with collapse

Here are some example JSON documents that you can import through Kibana DevTools. These examples are designed to illustrate the scenario described in the article, where you have product variations (sizes and colors) that you want to group.

**Explanation of the JSON Structure**

Each document represents a specific product variant (SKU).

* **product\_id:** A unique identifier for the core product. This is the field you will use for the collapse and cardinality aggregation.
* **sku:** The unique stock keeping unit for the specific variant.
* **name:** The general name of the product.
* **color:** The color of the product variant.
* **size:** The size of the product variant.
* **price:** The price of the specific variant.
* **timestamp:** A timestamp to allow for sorting and selecting the most recent version if needed.

To import the following data, you can copy/paste the lines in Kibana DevTools and press the play button that appears on the screen on the right side of the gray outlined block.

```
POST your-products-index/_bulk
{ "index" : { "_id" : "sku-1001" } }
{ "product_id": "P001", "sku": "sku-1001", "name": "Classic T-Shirt", "color": "White", "size": "S", "price": 19.99, "timestamp": "2025-06-23T10:00:00Z" }
{ "index" : { "_id" : "sku-1002" } }
{ "product_id": "P001", "sku": "sku-1002", "name": "Classic T-Shirt", "color": "White", "size": "M", "price": 19.99, "timestamp": "2025-06-23T10:01:00Z" }
{ "index" : { "_id" : "sku-1003" } }
{ "product_id": "P001", "sku": "sku-1003", "name": "Classic T-Shirt", "color": "White", "size": "L", "price": 19.99, "timestamp": "2025-06-23T10:02:00Z" }
{ "index" : { "_id" : "sku-1004" } }
{ "product_id": "P001", "sku": "sku-1004", "name": "Classic T-Shirt", "color": "Black", "size": "M", "price": 21.99, "timestamp": "2025-06-23T11:00:00Z" }
{ "index" : { "_id" : "sku-2001" } }
{ "product_id": "P002", "sku": "sku-2001", "name": "V-Neck Sweater", "color": "Navy", "size": "M", "price": 49.95, "timestamp": "2025-06-22T14:00:00Z" }
{ "index" : { "_id" : "sku-2002" } }
{ "product_id": "P002", "sku": "sku-2002", "name": "V-Neck Sweater", "color": "Navy", "size": "L", "price": 49.95, "timestamp": "2025-06-22T14:01:00Z" }
{ "index" : { "_id" : "sku-2003" } }
{ "product_id": "P002", "sku": "sku-2003", "name": "V-Neck Sweater", "color": "Grey", "size": "S", "price": 45.95, "timestamp": "2025-06-22T15:00:00Z" }
{ "index" : { "_id" : "sku-3001" } }
{ "product_id": "P003", "sku": "sku-3001", "name": "Running Shorts", "color": "Blue", "size": "32", "price": 35.00, "timestamp": "2025-06-21T09:30:00Z" }
{ "index" : { "_id" : "sku-3002" } }
{ "product_id": "P003", "sku": "sku-3002", "name": "Running Shorts", "color": "Red", "size": "34", "price": 35.00, "timestamp": "2025-06-21T09:31:00Z" }
```

Now we can run the search and collapse on the product\_id.keyword field to get the results back:

```
GET your-products-index/_search
{
    "query": {
        "match_all": {}
    },
    "collapse": {
        "field": "product_id.keyword"
    }
}
```

And this is how the results look like:

```
{
  "took": 1,
  "timed_out": false,
  "_shards": {
    "total": 5,
    "successful": 5,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 9,
      "relation": "eq"
    },
    "max_score": 1,
    "hits": [
      {
        "_index": "your-products-index",
        "_id": "sku-1003",
        "_score": 1,
        "_source": {
          "product_id": "P001",
          "sku": "sku-1003",
          "name": "Classic T-Shirt",
          "color": "White",
          "size": "L",
          "price": 19.99,
          "timestamp": "2025-06-23T10:02:00Z"
        },
        "fields": {
          "product_id.keyword": [
            "P001"
          ]
        }
      },
      {
        "_index": "your-products-index",
        "_id": "sku-2001",
        "_score": 1,
        "_source": {
          "product_id": "P002",
          "sku": "sku-2001",
          "name": "V-Neck Sweater",
          "color": "Navy",
          "size": "M",
          "price": 49.95,
          "timestamp": "2025-06-22T14:00:00Z"
        },
        "fields": {
          "product_id.keyword": [
            "P002"
          ]
        }
      },
      {
        "_index": "your-products-index",
        "_id": "sku-3001",
        "_score": 1,
        "_source": {
          "product_id": "P003",
          "sku": "sku-3001",
          "name": "Running Shorts",
          "color": "Blue",
          "size": "32",
          "price": 35,
          "timestamp": "2025-06-21T09:30:00Z"
        },
        "fields": {
          "product_id.keyword": [
            "P003"
          ]
        }
      }
    ]
  }
}
```

However, there’s an important caveat:

The `hits.total.value` returned still reflects the total number of documents, not the number of unique groups after collapsing. This means relying on `hits.total.value` for pagination breaks the UX and misrepresents the total number of result pages. If the UI is showing 5 results, it would have page 2. But loading page 2 would fail because there are only 3 documents instead of 9.

### Solution: Combine collapse with cardinality

By adding a **cardinality** aggregation on the same **collapse** field, we can accurately compute the number of distinct groups, enabling reliable and predictable pagination.

Here’s an example query:

```
{
    "query": {
    "match_all": {}
},           
"collapse": {
    "field": "product_id.keyword"
 },
 "aggs": {
     "total_uniques": {
         "cardinality": {
             "field": "product_id.keyword"
         }
     }
 },
 "sort": [
    {"timestamp": {"order": "desc"}}
],
    "size": 5,
    "from": 0
}
```

## Conclusion

By now, the challenge of pagination with collapsed search results should be clear, as should the definitive solution. Relying on the default hits.total.value when using the collapse feature inevitably leads to a broken user experience, displaying incorrect page counts and frustrating users.

The key takeaway is the robust pattern of pairing the collapse query with a cardinality aggregation on the very same field.

* **collapse:** Deduplicates results at query-time by grouping on collapseField.
* **cardinality:** Returns an approximate count of unique collapseField values, essential for paginating over grouped results.
* **sort + from:** Still respected, but applied after collapsing.

`hits.total.value`**:** Will reflect total documents—not deduplicated ones. Don't use this for pagination in collapsed queries.

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