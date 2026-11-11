---
title: 'Generating filters and facets using ML'
company: Elastic
tag: 查询理解
date: 2025-04-03
url: https://www.elastic.co/search-labs/blog/filters-facets-using-ml
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Generating filters and facets using ML

Exploring the pros and cons of automating the creation of filters and facets in a search experience using ML models vs the classical hard-coded approach.

April 03, 2025

[Andre Luiz](/search-labs/author/andre-luiz)

[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

Jump to

Share

Filters and facets are mechanisms used to refine search results, helping users find relevant content or products more quickly. In the classical approach, rules are manually defined. For example, in a movie catalog, attributes such as genre are pre-defined for use in filters and facets. On the other hand, with AI models, new attributes can be automatically extracted from the characteristics of movies, making the process more dynamic and personalized. In this blog, we explore the pros and cons of each method, highlighting their applications and challenges.

## Filters vs facets

Before we begin, let's define what filters and facets are. **Filters** are predefined attributes used to restrict a set of results. In a marketplace, for example, filters are available even before a search is performed. The user can select a category, such as **"Video games"**, before searching for **"PS5"**, refining the search to a more specific subset instead of the entire database. This significantly increases the chances of obtaining more relevant results.

![Filters](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0a77b38aae238938/6a170b821949f72a52e7aa51/5ed8868fa5017d034e1273e35c884a5430afdf3c-1600x937.png)

**Facets** work similarly to filters but are only available after the search is performed. In other words, the search returns results, and based on them, a new list of refinement options is generated. For example, when searching for a PS5 console, facets such as storage **capacity**, **shipping cost**, and **color** may be displayed to help users choose the ideal product.

![Facets ](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt166e356b80d423ef/6a170b840e2e494ca341a10f/c5633fcc5b6fbb916110faf32144d8d43572e33a-1600x937.png)

Now that we have defined filters and facets, let's discuss the impact of the classical and Machine Learning (ML)-based approaches on their implementation and usage. Each method has advantages and challenges that influence search efficiency.

## Classical approach to filters and facets

In this approach, filters and facets are manually defined based on predefined rules. This means that the attributes available for refining the search are fixed and planned in advance, considering the catalog structure and user needs.

For example, in a marketplace, categories such as "Electronics" or "Fashion" may have specific filters like brand, format and price range. These rules are created statically, ensuring consistency in the search experience but requiring manual adjustments whenever new products or categories emerge.

Although this approach provides predictability and control over the displayed filters and facets, it can be limited when new trends arise that demand dynamic refinement.

**Pros:**

* **Predictability and control:** Since filters and facets are manually defined, management becomes easier.
* **Low complexity:** No need to train models.
* **Ease of maintenance:** As rules are predefined, adjustments and corrections can be made quickly.

**Cons**:

* **Reindexing required for new filters:** Whenever a new attribute needs to be used as a filter, the entire dataset must be reindexed to ensure that documents contain this information.
* **Lack of dynamic adaptation:** Filters are static and do not automatically adjust to changes in user behavior.

### Implementation of filters/facets – Classical approach

In **Dev Tools, Kibana**, we will create a demonstration of filters/facets using the **classical approach**.

First, we define the mapping to structure the index:

```
PUT videogames
{
  "mappings": {
    "properties": {
      "name": { "type": "text" },
      "brand": { "type": "keyword" },
      "storage": { "type": "keyword" },
      "price": { "type": "float" },
      "description": { "type": "text" }
    }
  }
}
```

The **brand** and **storage** fields are set as **keyword**, allowing them to be used directly in aggregations (**facets**). The **price** field is of type **float**, enabling the creation of **price ranges**.

In the next step, the product data will be indexed:

```
POST videogames/_bulk
{ "index": { "_id": 1 } }
{ "name": "Play Station 5", "brand": "Sony", "storage": "1TB", "price": 499.99, "description": "Stunning Gaming: Marvel at stunning graphics and experience the features of the new PS5. Breathtaking Immersion: Discover a deeper gaming experience with support for haptic feedback, adaptive triggers, and 3D Audio technology. Slim Design: With the PS5 Digital Edition, gamers get powerful gaming technology in a sleek, compact design. 1TB of Storage: Have your favorite games ready and waiting for you to play with 1TB of built-in SSD storage. Backward Compatibility and Game Boost: The PS5 console can play over 4,000 PS4 games. With Game Boost, you can even enjoy faster, smoother frame rates in some of the best PS4 console games." }
{ "index": { "_id": 2 } }
{ "name": "Xbox Series X", "brand": "Microsoft", "storage": "1TB", "price": 499.99, "description": "Fastest, most powerful Xbox console ever. Play thousands of titles: Every game looks and plays better on Xbox Series X. At the heart of Series X is the Xbox Velocity. Architecture, which combines a custom SSD and built-in software to significantly reduce load times in and out of game. Switch between multiple games in an instant with Quick Resume. Explore new worlds and experience the action like never before with an unparalleled 12 teraflops of graphics processing power. Enjoy 4K gaming at up to 120 frames per second, premium advanced 3D sound, and more. 4K at 120 FPS: requires compatible content and display X version - with disc drive" }
{ "index": { "_id": 3 } }
{ "name": "Nintendo Switch", "brand": "Nintendo", "storage": "512GB", "price": 299.99, "description": "SHARPER, VIBRANT VISUALS. The new 7-inch screen on the Nintendo Switch OLED takes your gaming to the next level: vibrant colors with sharp contrasts for every moment. INTEGRATED GAMEPLAY. Enjoy the console's many multiplayer modes and connect with other players. Online or locally, the fun on the Nintendo Switch is guaranteed. ENJOY IMMERSION FOR LONGER. In addition to delivering an unparalleled experience, thanks to its improved audio, the Nintendo Switch has a rechargeable battery while you play. From 4.5 hours to 9 hours of battery life. INCLUDES SUPER MARIO BROS. WONDER. Transform your world with the phenomenal flowers in this new Mario game, full of amazing adventures, power-ups and new abilities. NINTENDO SWITCH ONLINE SUBSCRIPTION. Access online games, play with friends and enjoy the exclusive benefits of the Nintendo Switch Online subscription." }
{ "index": { "_id": 4 } }
{ "name": "Steam Deck", "brand": "Valve", "storage": "512GB", "price": 399.99, "description": "You can save games, apps, photos and videos without worrying about space. High-Level Performance: The 4-core processor and graphics ensure a dynamic experience and fast responses. High-Definition Images: Smooth transitions and sharp images provide complete immersion in the game. Wireless Connectivity: Wi-Fi technology allows you to play wherever you want, without wires or cables limiting your fun" }
{ "index": { "_id": 5 } }
{ "name": "Nintendo Switch Lite", "brand": "Nintendo", "storage": "512GB", "price": 299.99, "description": "MADE TO BE PORTABLE. Nintendo Switch Lite is designed specifically for portable gaming. The console lets you jump into your favorite games wherever you are. COMPACT AND LIGHTWEIGHT. With its sleek, lightweight design, this console is ready to hit the road wherever you are. COMPATIBLE GAMES. The Nintendo Switch Lite system plays the library of Nintendo Switch games that work in handheld mode. A WORLD OF COLOR TO CHOOSE FROM. Available in a variety of vibrant and unique colors, Nintendo Switch Lite lets you bring even more personality wherever you go." }
```

Now, let's retrieve classic facets by grouping the results by brand, storage, and price range. In the query, size:0 was defined. In this scenario, the goal is to retrieve only the aggregation results without including the documents corresponding to the query.

```
POST videogames/_search
{
  "size": 0,
  "aggs": {
    "brands": {
      "terms": { "field": "brand" }
    },
    "storage_sizes": {
      "terms": { "field": "storage" }
    },
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          { "to": 300 },   
          { "from": 300, "to": 500 },  
          { "from": 500 }  
        ]
      }
    }
  }
}
```

The response will include counts for **Brand**, **Storage**, and **Price**, helping to create filters and facets.

```
"aggregations": {
   "brands": {
     "doc_count_error_upper_bound": 0,
     "sum_other_doc_count": 0,
     "buckets": [
       {
         "key": "Microsoft",
         "doc_count": 1
       },
       {
         "key": "Nintendo",
         "doc_count": 1
       },
       {
         "key": "Sony",
         "doc_count": 1
       },
       {
         "key": "Valve",
         "doc_count": 1
       }
     ]
   },
   "storage_sizes": {
     "doc_count_error_upper_bound": 0,
     "sum_other_doc_count": 0,
     "buckets": [
       {
         "key": "1TB",
         "doc_count": 2
       },
       {
         "key": "512GB",
         "doc_count": 2
       }
     ]
   },
   "price_ranges": {
     "buckets": [
       {
         "key": "*-300.0",
         "to": 300,
         "doc_count": 1
       },
       {
         "key": "300.0-500.0",
         "from": 300,
         "to": 500,
         "doc_count": 3
       },
       {
         "key": "500.0-*",
         "from": 500,
         "doc_count": 0
       }
     ]
   }
 }
```

## Machine learning/AI-based approach to filters and facets

In this approach, Machine Learning (ML) models, including Artificial Intelligence (AI) techniques, analyze data attributes to generate relevant filters and facets. Instead of relying on predefined rules, ML/AI leverages indexed data characteristics. This enables the dynamic discovery of new facets and filters.

**Pros**:

* **Automatic updates:** New filters and facets are generated automatically, without the need for manual adjustments.
* **Discovery of new attributes:** It can identify **previously unconsidered** data characteristics as filters, enriching the search experience.
* **Reduced manual effort:** The team does not need to constantly define and update filtering rules as AI learns from available data.

**Cons:**

* **Maintenance complexity:** The use of models may require pre-validation to ensure the consistency of the generated filters.
* **Requires ML and AI expertise:** The solution demands qualified professionals to fine-tune and monitor model performance.
* **Risk of irrelevant filters:** If the model is not well-calibrated, it may generate facets that are not useful for users.
* **Cost:** The use of ML and AI may require third-party services, increasing operational costs.

It's worth noting that even with a well-calibrated model and a well-crafted prompt, the generated facets should still go through a review step. This validation can be manual or based on moderation rules, ensuring that the content is appropriate and safe. While not necessarily a drawback, it is an important consideration to ensure the quality and suitability of the facets before they are made available to users.

### Implementation of filters/facets – AI approach

In this demonstration, we will use an AI model to automatically analyze product characteristics and suggest relevant attributes. With a well-structured prompt, we extract information from the catalog and transform it into filters and facets. Below, we present each step of the process.

Initially, we will use the **Inference API** to register an endpoint for integration with an ML service. Below is an example of integration with **OpenAI's service**.

```
PUT _inference/completion/generate_filter_ia
{
   "service": "openai",
   "service_settings": {
       "api_key": "your-key",
       "model_id": "gpt-4o-mini"
   }
}
```

Now, we define the pipeline to execute the prompt and obtain the new filters generated by the model.

```
PUT /_ingest/pipeline/generate_filter_ai
{
   "processors": [
     {
       "script": {
         "source": """ctx.prompt = "You are an expert in data organization for search and product categorization. Your task is to analyze the following product and identify the best dynamic facets that can be used in an e-commerce search experience. Product: " + ctx.name + "description: " + ctx.description + "Instructions: - Analyze the product name and description. - Extract only the dynamic facets (technological features or product characteristics that can be inferred from the description, try to create max 3 facets by characteristics found). Put the values into an array. Using key and value, e.g. dynamic_facets: [{ \"name\": \"Gaming Experience\", \"value\": \"Haptic Feedback\" },{ \"name\": \"Gaming Experience\", \"value\": \"Adaptive Triggers\" } - Return only a JSON."
         """
       }
     },
     {
       "inference": {
         "model_id": "generate_filter_ia",
         "input_output": {
           "input_field": "prompt",
           "output_field": "result"
         }
       }
     },
     {
       "gsub": {
         "field": "result",
         "pattern": "```json",
         "replacement": ""
       }
     },
     {
       "json" : {
         "field" : "result",
         "strict_json_parsing": false,
         "add_to_root" : true
       }
     },
     {
       "remove": {
         "field": "result"
       }
     },
     {
       "remove": {
         "field": "prompt"
       }
     }
   ]
}
```

Running a simulation of this pipeline for the "PlayStation 5" product, with the following description:

*Stunning Gaming: Marvel at stunning graphics and experience the features of the new PS5.*

*Breathtaking Immersion: Discover a deeper gaming experience with support for haptic feedback, adaptive triggers, and 3D Audio technology.*

*Slim Design: With the PS5 Digital Edition, gamers get powerful gaming technology in a sleek, compact design.*

*1TB of Storage: Have your favorite games ready and waiting for you to play with 1TB of built-in SSD storage.*

*Backward Compatibility and Game Boost: The PS5 console can play over 4,000 PS4 games. With Game Boost, you can even enjoy faster, smoother frame rates in some of the best PS4 console games.*

Let's observe the prompt output generated from this simulation.

```
{
 "docs": [
   {
     "doc": {
       "_index": "index",
       "_version": "-3",
       "_id": "1",
       "_source": {
         "name": "Play Station 5",
         "result": """```json
{
 "dynamic_facets": [
   { "name": "Storage Capacity", "value": "1TB SSD" },
   { "name": "Graphics Technology", "value": "Stunning Graphics" },
   { "name": "Audio Technology", "value": "3D Audio" }
 ]
}
```""",
         "description": "Stunning Gaming: Marvel at stunning graphics and experience the features of the new PS5. Breathtaking Immersion: Discover a deeper gaming experience with support for haptic feedback, adaptive triggers, and 3D Audio technology. Slim Design: With the PS5 Digital Edition, gamers get powerful gaming technology in a sleek, compact design. 1TB of Storage: Have your favorite games ready and waiting for you to play with 1TB of built-in SSD storage. Backward Compatibility and Game Boost: The PS5 console can play over 4,000 PS4 games. With Game Boost, you can even enjoy faster, smoother frame rates in some of the best PS4 console games.",
         "model_id": "generate_filter_ia",
         "prompt": """You are an expert in data organization for search and product categorization. Your task is to analyze the following product and identify the best dynamic facets that can be used in an e-commerce search experience. Product: Play Station 5description: Stunning Gaming: Marvel at stunning graphics and experience the features of the new PS5. Breathtaking Immersion: Discover a deeper gaming experience with support for haptic feedback, adaptive triggers, and 3D Audio technology. Slim Design: With the PS5 Digital Edition, gamers get powerful gaming technology in a sleek, compact design. 1TB of Storage: Have your favorite games ready and waiting for you to play with 1TB of built-in SSD storage. Backward Compatibility and Game Boost: The PS5 console can play over 4,000 PS4 games. With Game Boost, you can even enjoy faster, smoother frame rates in some of the best PS4 console games.Instructions: - Analyze the product name and description. - Extract only the dynamic facets (technological features or product characteristics that can be inferred from the description, try create max 3 facets by characteristics found). Put the values like arrays. Using key and value, e.g. dynamic_facets: [{ "name": "Gaming Experience", "value": "Haptic Feedback" },{ "name": "Gaming Experience", "value": "Adaptive Triggers" } - Return only a JSON."""
       },
       "_ingest": {
         "timestamp": "2025-03-19T22:14:32.0161803Z"
       }
     }
   }
 ]
}
```

Now a new field, **dynamic\_facets**, will be added to the new index to store the facets generated by the AI.

```
PUT videogames_1
{
 "mappings": {
   "properties": {
     "name": { "type": "text" },
     "brand": { "type": "keyword" },
     "storage": { "type": "keyword" },
     "price": { "type": "float" },
     "description": { "type": "text" },
     "dynamic_facets": { "type": "nested",
     "properties": { "name": { "type": "keyword" },
                     "value": { "type": "keyword" } } }
   }
 }
}
```

Using the **Reindex API**, we will reindex the **videogames** index to **videogames\_1**, applying the **generate\_filter\_ai** pipeline during the process. This pipeline will automatically generate dynamic facets during indexing.

```
POST _reindex?wait_for_completion=false
{
 "source": {
   "index": "videogames"
 },
 "dest": {
   "index": "videogames_1",
   "pipeline": "generate_filter_ai"
 }
}
```

Now, we will run a search and get the new filters:

```
GET videogames_1/_search
{
 "size": 0,
 "query": {
   "match": {
     "name": "nintendo"
   }
 },
 "aggs": {
   "dynamic_facets": {
     "nested": {
       "path": "dynamic_facets"
     },
     "aggs": {
       "facets": {
         "terms": {
           "field": "dynamic_facets.name"
         },
         "aggs": {
           "facets": {
             "terms": {
               "field": "dynamic_facets.value"
             }
           }
         }
       }
     }
   }
 }
}
```

Results:

```
"aggregations": {
   "dynamic_facets": {
     "doc_count": 3,
     "facets": {
       "doc_count_error_upper_bound": 0,
       "sum_other_doc_count": 0,
       "buckets": [
         {
           "key": "Frame Rate",
           "doc_count": 1,
           "facets": {
             "doc_count_error_upper_bound": 0,
             "sum_other_doc_count": 0,
             "buckets": [
               {
                 "key": "120 FPS",
                 "doc_count": 1
               }
             ]
           }
         },
         {
           "key": "Gaming Resolution",
           "doc_count": 1,
           "facets": {
             "doc_count_error_upper_bound": 0,
             "sum_other_doc_count": 0,
             "buckets": [
               {
                 "key": "4K",
                 "doc_count": 1
               }
             ]
           }
         },
         {
           "key": "Graphics Processing Power",
           "doc_count": 1,
           "facets": {
             "doc_count_error_upper_bound": 0,
             "sum_other_doc_count": 0,
             "buckets": [
               {
                 "key": "12 Teraflops",
                 "doc_count": 1
               }
             ]
           }
         }
       ]
     }
   }
 }
```

To symbolize the implementation of the facets, below is a simple front-end:

![implementation of the facets](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb0d6aa40caf7a91a/6a170b86ab7f0839afdb9eb6/12b6d9d4f4d0985848d92841545fd22b7253ae6d-1600x1288.png)

The UI code presented is [here](https://gist.github.com/andreluiz1987/06d9ec1b381e942e9def0e969bd811a0).

## Conclusion

Both approaches to creating filters and facets have their benefits and points of concern. The classic approach, based on manual rules, offers control and lower costs but requires constant updates and does not dynamically adapt to new products or features.

On the other hand, the AI ​​and Machine Learning-based approach automates facet extraction, making the search more flexible and allowing the discovery of new attributes without manual intervention. However, this approach can be more complex to implement and maintain, requiring calibration to ensure consistent results.

The choice between the classic and AI-based approaches depends on the needs and complexity of the business. For simpler scenarios, where data attributes are stable and predictable, the classic approach can be more efficient and easier to maintain, avoiding unnecessary costs with infrastructure and AI models. On the other hand, the use of ML/AI to extract facets can add significant value, improving the search experience and making filtering more intelligent.

The important thing is to evaluate whether automation justifies the investment or whether a more traditional solution already meets the business needs effectively.

### Frequently Asked Questions

#### What are filters?

Filters are predefined attributes used to restrict a set of results.

#### What are facets?

Facets are a new list of refinement options that is generated after a search is performed.

#### What is the classical approach to filters and facets?

In the classical approach to filters and facets, the attributes available for refining the search are fixed and planned.
The approach is good for predictability but has a lack of dynamic adaptation and requires new filters to be created for reindexing.

#### What is the machine learning (ML) approach to filters and facets?

The machine learning (ML) approach to filters and facets is mainly AI-based. ML models analyze data attributes to generate relevant filters and facets. Instead of relying on predefined rules, ML/AI leverages indexed data characteristics.

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