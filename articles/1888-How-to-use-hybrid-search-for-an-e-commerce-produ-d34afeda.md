---
title: 'How to use hybrid search for an e-commerce product catalog'
company: Elastic
tag: 召回
date: 2024-11-12
url: https://www.elastic.co/search-labs/blog/hybrid-search-ecommerce
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# How to use hybrid search for an e-commerce product catalog

Learn how to use hybrid search to build an e-commerce product catalog, using faceting, promotions, personalization and behavioral analytics.

November 12, 2024

[Andre Luiz](/search-labs/author/andre-luiz)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

In this article, we will demonstrate how to implement a hybrid search that combines the results of full-text search with vector search. By unifying these two approaches, hybrid search improves the breadth of results, leveraging the best of both search strategies.

In addition to integrating hybrid search, we’ll demonstrate how to add features that make your search solution even more robust. These include faceting and personalized product promotions. Additionally, we’ll show you how to capture user interactions and generate valuable insights using Elastic’s Behavioral Analytics tool.

In this implementation, you will see how to build both the interface that allows users to view and interact with the search results and the API responsible for returning the information. To access the repositories with the source code, the links are provided below:

* <https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/hybrid-search-for-an-e-commerce-product-catalogue/product-store-search>
* <https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/hybrid-search-for-an-e-commerce-product-catalogue/app-product-store>

We have divided this guide into several steps, from creating the index to implementing advanced features such as faceting and result personalization. By the end, you will have a robust search solution ready to be used in an e-commerce scenario.

## Environment setup for e-commerce hybrid search

Before we begin the implementation, we need to set up the environment. You can choose to use a service on Elastic Cloud or a containerized solution to manage Elasticsearch. If you choose containerization, a configuration via Docker Compose can be found in this repository: [docker-compose.yml](https://github.com/andreluiz1987/product-store-search/blob/main/docker/docker-compose.yml).

## Index creation and product catalog ingestion

The index will be created based on a catalog of cosmetic products, which includes fields such as name, description, photo, category, and tags. Fields used for full-text search, like "name" and "description," will be mapped as `text`, while fields used for aggregations, such as "category" and "brand," will be mapped as `keyword` to enable faceting.

The "description" field will be used for vector search, as it provides more context about the products. This field will be defined as `dense_vector,` storing the vector representation of the description.

The index mapping will be as follows:

```
{
   "mappings":{
      "properties":{
         "id":{
            "type":"keyword"
         },
         "brand":{
            "type":"text",
            "fields":{
               "keyword":{
                  "type":"keyword"
               }
            }
         },
         "name":{
            "type":"text"
         },
         "price":{
            "type":"float"
         },
         "price_sign":{
            "type":"keyword"
         },
         "currency":{
            "type":"keyword"
         },
         "image_link":{
            "type":"keyword"
         },
         "description":{
            "type":"text"
         },
         "description_embeddings":{
            "type":"dense_vector",
            "dims":384
         },
         "rating":{
            "type":"keyword"
         },
         "category":{
            "type":"keyword"
         },
         "product_type":{
            "type":"keyword"
         },
         "tag_list":{
            "type":"keyword"
         }
      }
   }
}
```

The script for creating the index can be found [here](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/hybrid-search-for-an-e-commerce-product-catalogue/product-store-search/infra/create_index.py).

## Embedding generation

To vectorize the product descriptions, we use the model all-MiniLM-L6-v2. In this case, the application is responsible for generating the embeddings before indexing. Another option would be to import the model into the Elasticsearch cluster, but for this local environment, we chose to perform the vectorization directly within the application.

We used the cosmetics dataset available on [Kaggle](https://www.kaggle.com/datasets/shivd24coder/cosmetic-brand-products-dataset) to populate the index, and to improve the efficiency of data ingestion, we used batch processing. During this same ingestion stage, we will generate the embeddings for the "description" field and index them into the new field "description\_embeddings".

The complete data ingestion process can be followed and executed directly through the **Jupyter Notebook** available in the repository. The notebook provides a step-by-step guide on how the data is read, processed, and indexed into Elasticsearch, allowing for easy replication and experimentation.

You can access the notebook at the following link: [Ingestion Notebook.](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/hybrid-search-for-an-e-commerce-product-catalogue/product-store-search/ingestion/ingestion.ipynb)

## Hybrid search implementation

Now, let's implement hybrid search. For keyword-based search, we use the [multi\_match](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html) query, targeting the fields "name," "category," and "description." This ensures that documents containing the search term in any of these fields are retrieved.

For vector search, we use the [KNN query](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html). The search term needs to be vectorized before executing the query, and this is done using the method that vectorizes the input term. Note that the same model used during ingestion is also used for the search term.

The combination of both searches is accomplished using the [Reciprocal Rank Fusion (RRF)](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html) algorithm, which merges the results of the two queries and increases search accuracy by reducing noise. RRF allows both keyword-based and vector searches to work together, enhancing the understanding of the user's query.

```
query = {
   "retriever": {
       "rrf": {
           "retrievers": [
               {
                   "standard": {
                       "query": organic_query['query']
                   }
               },
               {
                   "knn": {
                       "field": "description_embeddings",
                       "query_vector": vector,
                       "k": 5,
                       "num_candidates": 20
                   }
               }
           ],
           "rank_window_size": 20,
           "rank_constant": 5
       }
   },
   "_source": organic_query['_source']
}
```

### Comparing results: keyword search vs. hybrid search

Now, let's compare the results of a traditional keyword search with hybrid search. When searching for "foundation for dry skin" using keyword search, we get the following results:

![Comparing results: Keyword search vs. hybrid search](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltcb5405df787bc8f5/6a17023e961e697ca1c4cdb4/52e717aa3c9c1fadfadb639f5fb77cf8e47e3b34-1600x1021.png)

1. **Revlon ColorStay Makeup for Normal / Dry SkinDescription**: Revlon ColorStay Makeup provides longwearing coverage with a lightweight \nformula that won\u2019t cake, fade, or rub off. With Time Release \nTechnology, this oil-free, moisture-balance formula is especially \nformulated for normal or dry skin to continuously provide hydration.Features: Makeup feels comfortable and wears for up to 24 hours\nMedium to full coverage\nComes in a range of beautiful shades
2. **Maybelline Dream Smooth Mousse FoundationDescription**: Why You'll Love ItUnique cream-whipped foundation provides 100% baby-smooth perfection.\n\nSkin looks and feels hydrated for 14 hours - never rough or dry\nLightweight formula provides perfectly moisturizing coverage\nBlends seamlessly and feels fresh all-day\nOil-free, Fragrance-free, Dermatologist Tested, Allergy Tested, Non-comedogenic \u2013 won\u2019t clog pores.\nSafe for sensitive skin.

**Analysis**: When searching for "foundation for dry skin," the results were obtained by the exact match between the search term keywords and the product titles and descriptions. However, this match doesn’t always reflect the best choice. For example, **Revlon ColorStay Makeup for Normal / Dry Skin** is a good option, as it is specifically formulated for dry skin. Even though it is oil-free, its formula is designed to provide continuous hydration. In contrast, we also received **Maybelline Dream Smooth Mousse Foundation**, which, although oil-free and mentioning hydration, is generally more recommended for oily or combination skin, as oil-free products tend to focus on controlling oil rather than providing the extra hydration needed for dry skin. This highlights the limitation of keyword-based searches, which can return products that don’t fully meet the specific needs of people with dry skin.

Now, when performing the same search using the hybrid approach:

![Performing search using the hybrid approach](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt412e38b327cf6a4f/6a17024066c4f94c52f8beb9/13b562a5120619355ba0861976102e208964a49f-1600x1021.png)

1. **CoverGirl Outlast Stay Luminous Foundation Creamy Natural (820):Description**: CoverGirl Outlast Stay Luminous Foundation is perfect for achieving a dewy finish and a subtle glow. It is oil-free, with a non-greasy formula that gives your skin a natural luminosity that lasts all day! This all-day foundation hydrates skin while providing flawless coverage.
   **Analysis:** This product is a relevant match as it emphasizes hydration, which is key for users with dry skin. The terms "hydrates skin" and "dewy finish" align with the user's intent to find a foundation for dry skin. The vector search likely understood the concept of hydration and linked it to the need for a foundation that addresses dry skin.
2. **Revlon ColorStay Makeup for Normal / Dry Skin:Description:** Revlon ColorStay Makeup provides longwearing coverage with a lightweight formula that won’t cake, fade, or rub off. With Time Release Technology, this oil-free, moisture-balance formula is especially formulated for normal or dry skin to continuously provide hydration.
   **Analysis:** This product directly addresses the needs of users with dry skin, explicitly mentioning that it is formulated for normal or dry skin. The "moisture-balance formula" and continuous hydration are well-suited for someone searching for a foundation that caters to dry skin. The vector search successfully retrieved this result, not just because of keyword matching, but due to the focus on hydration and the specific mention of dry skin as a target demographic.
3. **Serum FoundationDescription:** Serum Foundations are lightweight medium-coverage formulations available in a comprehensive shade range across 21 shades. These foundations offer moderate coverage that looks natural with a very lightweight serum feel. They are very low in viscosity and are dispensed with the supplied pump or with the optional glass dropper available for purchase separately if preferred.
   **Analysis:** In this case, the description emphasizes a lightweight serum foundation with a natural feel, which aligns with the needs of people with dry skin, as they often seek products that are gentle, hydrating, and provide a non-cakey finish. The vector search likely picked up on the broader context of lightweight, natural coverage and the serum-like texture, which is associated with moisture retention and a comfortable application, making it relevant for dry skin, even though the term "dry skin" is not explicitly mentioned.

## Facet implementation

Facets are essential for refining and filtering search results efficiently, providing users with more focused navigation, especially in scenarios with a large variety of products, such as e-commerce. They allow users to adjust the results based on attributes like category, brand, or price, making the search more accurate. To implement this feature, we use [terms aggregations](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-terms-aggregation.html) on the `category` and `brand` fields, which were defined as `keyword` during the index creation stage.

```
    query = build_query(term, categories, product_types, brands)
    query["aggs"] = {
        "product_types": {"terms": {"field": "product_type"}},
        "categories": {"terms": {"field": "category"}},
        "brands": {"terms": {"field": "brand.keyword"}}
    }
```

The complete code for the implementation can be found [here](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/hybrid-search-for-an-e-commerce-product-catalogue/product-store-search/api/api.py#L144).

See below the facet results from the search for "foundation for dry skin":

![Facet results from the search for "foundation for dry skin"](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt31080652a60d8600/6a1702416234e0af7ddb18e7/e8907af359c021eaa38ec7a6a53f10c325ee8ade-1146x1248.png)

## Customizing results: pinned queries

In some cases, it may be beneficial to promote certain products in the search results. For this, we use [**Pinned Queries**](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-pinned-query.html), which allow specific products to appear at the top of the results. Below, we will perform a search for the term "Foundation" without promoting any products:

![Search for the term "Foundation" without promoting any products](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt31e75c815262993e/6a170243509168ae42e1b95d/9396c4ed358e7a68eed47f17dd6915d0bad492aa-1600x1157.png)

In our example, we can promote products that have the tag "Gluten Free." By using the product IDs, we ensure that they are prioritized in the search results. Specifically, we will promote the following products: **Serum Foundation** (ID: 1043), **Coverage Foundation** (ID: 1042), and **Realist Invisible Setting Powder** (ID: 1039).

```
{
   "query":{
      "pinned":{
         "ids":[
            "1043",
            "1042",
            "1039"
         ],
         "organic":{
            "bool":{
               "must":[
                  {
                     "multi_match":{
                        "query":"foundation",
                        "fields":[
                           "name",
                           "category",
                           "description"
                        ]
                     }
                  }
               ]
            }
         }
      }
   }
}
```

We use specific product IDs to ensure that they are prioritized in the query results. The query structure includes a list of product IDs that should be "pinned" to the top (in this case, IDs 1043, 1042, and 1039), while the remaining results follow the organic flow of the search, using a combination of conditions such as the text query in the fields "name", "category", and "description". This way, it is possible to promote items in a controlled manner, ensuring their visibility, while keeping the rest of the search based on the usual relevance.

Below, you can see the result of the query execution with the promoted products:

![Result of the query execution with the promoted products](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt53a6d5cbef227f16/6a1702458b73cb68f0189ef3/8c1a547bfe31360c405eae0891c666635051a51b-1600x1039.png)

The complete query code can be found [here](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/hybrid-search-for-an-e-commerce-product-catalogue/product-store-search/api/api.py#L112).

## Analyzing search behavior with behavioral analytics

Up to this point, we have already added functionalities to improve the relevance of search results and facilitate product discoverability. Now, we will finalize our search solution by including a feature that will help us analyze user search behavior, identifying patterns such as queries with or without results and clicks on search results.For this, we will use the **Behavioral Analytics** feature provided by Elastic. With it, in just a few steps, we can monitor and analyze user search behavior, gaining valuable insights to optimize the search experience.

### Creating the behavioral analytics collection

Our first action will be to create a collection, which will be responsible for receiving all behavior analysis events. To create the collection, access the Kibana interface in **Search > Behavioral Analytics**. In the example below, we created the collection named `tracking-search`.

![Behavioral analytics - naming your collection](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt9b4cb5480ab0bfef/6a1702474a531b189936a7e7/c05e533212a3690c5ea9f2d5226cbcdc901c482a-1600x1009.png)

### Integrating behavioral analytics into the interface

Our [front-end](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/hybrid-search-for-an-e-commerce-product-catalogue/app-product-store) application was developed in JavaScript, and to integrate Behavioral Analytics, we will follow the steps described in the official Elastic documentation to install the [**Behavioral Analytics JavaScript Tracker**](https://www.elastic.co/guide/en/elasticsearch/reference/current/behavioral-analytics-start.html#behavioral-analytics-start-ui-integration-js-client).

### Implementing the JavaScript tracker

Now, we will import the tracker client into our application and use the methods `trackPageView`, `trackSearch`, and `trackSearchClick` to capture user interactions.

**Disclaimer**: Although we are using a tool to collect user interaction data, it is essential to ensure compliance with **GDPR**. This means clearly informing users about what data is being collected, how it will be used, and providing the option to opt-out of tracking. Additionally, we must implement strong security measures to protect the collected information and respect user rights, such as data access and deletion, ensuring that all steps adhere to GDPR principles.

**Step 1: Creating the Tracker Instance**

First, we will create the tracker instance that will monitor interactions. In this configuration, we define the target endpoint, collection name, and API key:

```
createTracker({
  endpoint: "https://endpoint:443",
  collectionName: "tracking-search",
  apiKey: "api-key"
});
```

**Step 2: Capturing Page Views**

To track page views, we can configure the `trackPageView` event:

```
    trackPageView({
      page: {
        title: "home-page"
      },
    });
```

For more details about the `trackPageView` event, you can refer to this [documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/behavioral-analytics-event-reference.html#behavioral-analytics-event-reference-pageview-fields).

**Step 3: Capturing Search Queries**

To monitor users' search actions, we will use the `trackSearch` method:

```
      trackSearch({
        search: {
          query: searchTerm,
          results: {
            items: documents,
            total_results: response.data.length,
          },
        },
      });
```

Here we are collecting the search term and the search results.

**Step 4: Tracking Clicks on Search Results**

Finally, to capture clicks on search results, we will use the `trackSearchClick` method:

```
trackSearchClick({
      document: { id: product.id, index: "products-catalog"},
      search: {
        query: searchTerm,
        page: {
          current: 1,
          size: products.length,
        },
        results: {
          items: documents,
          total_results: products.length,
        },
        search_application: "app-product-store"
      },
    });
```

We collect information about the clicked document's ID, as well as the search term and search results.

### Analyzing the data in Kibana

Now that user interaction events are being captured, we can obtain valuable data about search actions. Kibana uses the Behavioral Analytics tool to visualize and analyze this behavioral data.To view the results, simply navigate to **Search > Behavioral Analytics > My Collection**, where an overview of the captured events will be displayed.

![Analyzing the Data in Kibana](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltdab4f4507c5a4732/6a17024860084b34ca3c4411/e219c4af2e01b0ccc1b9079459a07832835abc75-1600x1155.png)

In this overview, we get a general view of the events captured for each action integrated into our interface. From this information, we can gain valuable insights into user search behavior. However, if you want to create personalized dashboards with metrics that are more relevant to your specific scenario, Kibana offers powerful tools for building dashboards, allowing you to create various visualizations of your metrics.

Below, I have created some visualizations and charts to monitor, for example, the most searched terms over time, queries that returned no results, a word cloud highlighting the most searched terms, and finally, a geographic visualization to identify where search access is coming from.

![Visualizations and charts to monitor](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt04ced4406436f942/6a17024a5091685116e1b961/84a2c39dab77a3f9366c258a3a45d2cbc7df125e-1600x689.png)

## Conclusion

In this article, we implemented a hybrid search solution that combines keyword and vector search, delivering more accurate and relevant results for users. We also explored how to use additional features, such as facets and result personalization with Pinned Queries, to create a more complete and efficient search experience.

Additionally, we integrated Elastic's **Behavioral Analytics** to capture and analyze user behavior during their interactions with the search engine. By using methods like `trackPageView`, `trackSearch`, and `trackSearchClick`, we were able to monitor search queries, clicks on search results, and page views, generating valuable insights into search behavior.

## References

Dataset

<https://www.kaggle.com/datasets/shivd24coder/cosmetic-brand-products-dataset>

Transformer

<https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2>

Reciprocal Rank Fusion

<https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html>

<https://www.elastic.co/guide/en/elasticsearch/reference/current/retriever.html#rrf-retriever>

Knn Query

<https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html>

Pinned Query

<https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-pinned-query.html>

Behavioral Analytics APIs

<https://www.elastic.co/guide/en/elasticsearch/reference/current/behavioral-analytics-apis.html>

<https://www.elastic.co/guide/en/elasticsearch/reference/current/behavioral-analytics-overview.html>

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltdfa35fbcbbf4959f/6a1705b9dc55de19a4e00d07/e54132e915217063e9ed0ec45059c6cfc38e31dd-1280x720.png)

[ES|QL](/search-labs/blog/category/esql)[Vector Database](/search-labs/blog/category/vector-database)

### LINQ to Elasticsearch ES|QL: Write C#, query Elasticsearch

April 01, 2026|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt88526af16bafdb7c/6a17d7807f6f15825dc0998d/d11e1ba058784ec92b8953fb8db62e1bad21c210-720x420.jpg)

[Integrations](/search-labs/blog/category/integrations)[Vector Database](/search-labs/blog/category/vector-database)[AI tools](/search-labs/blog/category/ai-tools)

### 4 NVIDIA AI tasks, 1 Elasticsearch API: Embeddings, chat, completion, and rerank

July 21, 2026| [Jan Kazlouski](/search-labs/author/jan-kazlouski)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter