---
title: 'Elasticsearch plugin for UBI: Analyze user behavior from search queries'
company: Elastic
tag: 评测
date: 2025-08-01
url: https://www.elastic.co/search-labs/blog/elasticsearch-plugin-user-behavior-insights
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsearch plugin for UBI: Analyze user behavior from search queries

Discover how to use the UBI plugin to capture search queries and events in Elasticsearch to learn about user behavior.

August 01, 2025

[Eduard Martin](/search-labs/author/eduard-martin)

[Basics](/search-labs/blog/category/basics)

Part of the series:

[UBI Plugin](/search-labs/blog/series/ubi-plugin-elasticsearch)

In this series

Share

[*UBI (User Behavioral Insights)*](https://www.ubisearch.dev/)is an emerging standard to help search engineers capture and track usage events from search applications, from the front end all the way to the search engine. In this article, we will explore the UBI standard and explain how to capture analytics using the Elasticsearch plugin.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt9f2fa13f77f58c13/6a17f51abe608660500048e6/506903901cd5feeacf9c46a7f73b548edf185e64-324x321.png)

*Source:* [*https://www.ubisearch.dev/*](https://www.ubisearch.dev/)

## UBI explained

UBI can be used to understand what the user is doing on the application and provide information about what the user is searching, where on the site the user is interacting (search bar, search results, add to cart button, etc.), what result(s) the user is clicking, which results are coming back in that moment for that query, along with any other metadata you find useful to tune your search experience.

The most common metrics to capture and use are:

* ***Top search queries*****:** What is being searched for the most
* ***No result queries***: Queries that return no results
* ***Most clicked*****:** Results with the most clicks

Some examples of how the captured UBI can be used are:

* [**Visualizations**](https://www.elastic.co/docs/explore-analyze/dashboards/create-dashboard-of-panels-with-web-server-data)**:** Creating dashboards with the analytics data to make strategic decisions.
* [**Relevance tuning**](https://www.elastic.co/what-is/search-relevance)**:** Applying [*query rules*](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/searching-with-query-rules) or [*synonyms*](https://www.elastic.co/search-labs/blog/phrase-synonyms-api) based on your no-result queries, or adjusting queries.
* [**LTR**](https://www.elastic.co/docs/solutions/search/ranking/learning-to-rank-ltr)**:** Using UBI to create[*judgment lists*](https://www.elastic.co/docs/solutions/search/ranking/learning-to-rank-ltr#learning-to-rank-judgement-list) to feed the LTR model and boost results based on criteria like clicks/views or other business requirements.

UBI is [maintained on GitHub](https://github.com/o19s/ubi) under the [Apache 2.0 license.](https://en.wikipedia.org/wiki/Apache_License)

## UBI schemes

UBI proposes schemas for **queries**, which are triggered when a user searches, and for **events**, which are triggered by other interactions within the context of that search.

For instance, if a user searches for “shoe”, a query-type document is captured. Then, when the user clicks a result, an event-type document is created—correlated with the query-type document.

### Query schema

The query schema stores the search text and result shown to users. It includes the following fields:

* application
* query\_id
* client\_id
* user\_query ***Required***
* query\_attributes
* object\_id\_field
* timestamp
* query\_response\_id
* query\_response\_hit\_ids

A good starting point is storing `user_query`, `timestamp`, `query_id,` which will give you the time a query was executed, and the ID you can use to correlate with search events.

For more details on these attributes, check out the latest [schema](https://o19s.github.io/ubi/docs/html/latest/query.request.schema.html).

### Event schema

The event schema captures all users' actions that follow a search, such as clicks and purchases. It includes the following fields:

* application
* action\_name ***Required***
* query\_id
* session\_id
* client\_id
* user\_id
* timestamp ***Required***
* message\_type
* message
* user\_query
* event\_attributes

You can find the definition of each field [here](https://o19s.github.io/ubi/docs/html/latest/event.schema.html).

## UBI in Elasticsearch

Since UBI is a standard and not a tool or library, we just need two components to implement it in Elasticsearch:

1. ***Application***: We need to produce usage events that comply with the UBI standard from an application
2. ***Index***: We need Elasticsearch indices to hold the data, and we can visualize the events with Kibana later on

The UBI team created an [Elasticsearch plugin](https://github.com/o19s/user-behavior-insights-elasticsearch) that automatically produces the indices and stores queries on them based on the `_search` requests the cluster receives. We will go this route. Alternatively, you can build your own events collector and send them with the right schemas to Elasticsearch.

To start capturing UBI events, we will go through the following steps:

1. [Install the Elasticsearch plugin for UBI](https://www.elastic.co/search-labs/blog/elasticsearch-plugin-user-behavior-insights#install-the-elasticsearch-plugin-for-ubi)
2. [Load sample data](https://www.elastic.co/search-labs/blog/elasticsearch-plugin-user-behavior-insights#load-sample-data)
3. [Test the plugin](https://www.elastic.co/search-labs/blog/elasticsearch-plugin-user-behavior-insights#test-the-plugin)

A future article will cover the visualization part. Stay tuned!

## Install the Elasticsearch plugin for UBI

The [User Behavior Insights (UBI) plugin for Elasticsearch](https://github.com/o19s/user-behavior-insights-elasticsearch) is designed to capture search queries and develop a better understanding of user behavior. While this plugin focuses on capturing server-side queries, the [o19s/ubi](https://github.com/o19s/ubi) repository handles client-side event capture.

The way it works is by accepting an additional `ext` parameter in the search query body, which allows sending a UBI event. When searching, it will internally create a document with the query executed and any other fields from the schema you put within `ext.ubi`.You can use the `query_id` field to correlate different events from the same search.

### Compile the plugin

Start by cloning the repository:

```
git clone https://github.com/o19s/user-behavior-insights-elasticsearch.git
```

Build the jar package with the plugin:

```
./gradlew build
```

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6a9e93dcb497ba0a/6a17f51b96142a653feb1c66/a9b900ba5675d49c701f3c68e430e13a5ee89c77-1591x424.png)

The bundle is created under the ***/build/distributions*** folder and is a zip file like ***elasticsearch-ubi-1.0.0-SNAPSHOT.zip.*** *Save it for the next steps.*

### Install plugin

We are going to install the plugin on an Elastic Cloud instance. For self-managed deployments, you can follow the steps in the [documentation](https://www.elastic.co/docs/reference/elasticsearch/plugins/plugin-management#managing-plugins-for-self-managed-deployments).

1. Log in to Elastic Cloud, and go to [*Extensions*](https://cloud.elastic.co/deployment-features/extensions):

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltbd9c7d156ce4b762/6a17f51d148009ad6db488bc/0f10fa7e4f1a1f8fca20ff44d41d22bc5d82411e-1124x740.png)

2. Click “***Upload extension,***” select the ***elasticsearch-ubi-1.0.0-SNAPSHOT.zip*** file,and fill in the details. At the time of writing, ***the plugin Elasticsearch version is 8.15.2, so you must use that version or compile for a different one***. You can check the Elasticsearch version of the latest code of the plugin by looking at the [gradle.properties file](https://github.com/o19s/user-behavior-insights-elasticsearch/blob/main/gradle.properties).

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt9c24f0f2f7eef29f/6a17f51e57726277341bcd46/cf0db81fe68dcd9f73dde51e71f31f77e4ee4bc7-445x809.png)

3. After successfully uploading the extension, click on the ***Elastic logo*** to go to Elastic’s Cloud main page

4. On your working deployment, click ***Manage***

5. Click on the ***Actions*** dropdown, then click on ***Edit deployment***

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc8f754cf823708e7/6a17f520e9ea8750c7a9c74e/a7086805c7a62d08ef87b181e079cc08e858e64a-1522x702.png)

6. Under Elasticsearch, click the ***Manage user settings and extensions*** link

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt5a2a6e8078f2fdb5/6a17f522505ac3714ead8c9e/0448a69d37b3761dbae23064f4120f0b487c2801-1520x884.png)

7. Click on the***Extensions*** tab and select the recently installed extension. In this case, it is ubi8. Then, click “Back” and save the changes.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltdfe6adcef831dd5c/6a17f5245772624b681bcd4a/384ed848739ae7385b49f7d9b253aa392db55545-1600x712.png)

## Load sample data

Run the following command in the Kibana DevTools Console to load a couple of books to test the plugin. This will create a new index named “books” for this example.

```
POST /_bulk
{ "index" : { "_index" : "books" } }
{"name": "Snow Crash", "author": "Neal Stephenson", "release_date": "1992-06-01", "page_count": 470, "price": 14.99, "url": "https://www.amazon.com/Snow-Crash-Neal-Stephenson/dp/0553380958/", "image_url": "https://m.media-amazon.com/images/I/81p4Y+0HzbL._SY522_.jpg", "_extract_binary_content": true, "_reduce_whitespace": true, "_run_ml_inference": true}
{ "index" : { "_index" : "books" } }
{"name": "Revelation Space", "author": "Alastair Reynolds", "release_date": "2000-03-15", "page_count": 585, "price": 16.99, "url": "https://www.amazon.com/Revelation-Space-Alastair-Reynolds/dp/0441009425/", "image_url": "https://m.media-amazon.com/images/I/61nC2ExeTvL._SY522_.jpg", "_extract_binary_content": true, "_reduce_whitespace": true, "_run_ml_inference": true}
{ "index" : { "_index" : "books" } }
{"name": "1984", "author": "George Orwell", "release_date": "1985-06-01", "page_count": 328, "price": 12.99, "url": "https://www.amazon.com/1984-Signet-Classics-George-Orwell/dp/0451524934/", "image_url": "https://m.media-amazon.com/images/I/71rpa1-kyvL._SY522_.jpg", "_extract_binary_content": true, "_reduce_whitespace": true, "_run_ml_inference": true}
{ "index" : { "_index" : "books" } }
{"name": "Fahrenheit 451", "author": "Ray Bradbury", "release_date": "1953-10-15", "page_count": 227, "price": 11.99, "url": "https://www.amazon.com/Fahrenheit-451-Ray-Bradbury/dp/1451673310/", "image_url": "https://m.media-amazon.com/images/I/61sKsbPb5GL._SY522_.jpg", "_extract_binary_content": true, "_reduce_whitespace": true, "_run_ml_inference": true}
{ "index" : { "_index" : "books" } }
{"name": "Brave New World", "author": "Aldous Huxley", "release_date": "1932-06-01", "page_count": 268, "price": 12.99, "url": "https://www.amazon.com/Brave-New-World-Aldous-Huxley/dp/0060850523/", "image_url": "https://m.media-amazon.com/images/I/71GNqqXuN3L._SY522_.jpg", "_extract_binary_content": true, "_reduce_whitespace": true, "_run_ml_inference": true}
{ "index" : { "_index" : "books" } }
{"name": "The Handmaid's Tale", "author": "Margaret Atwood", "release_date": "1985-06-01", "page_count": 311, "price": 13.99, "url": "https://www.amazon.com/Handmaids-Tale-Margaret-Atwood/dp/038549081X/", "image_url": "https://m.media-amazon.com/images/I/61su39k8NUL._SY522_.jpg", "_extract_binary_content": true, "_reduce_whitespace": true, "_run_ml_inference": true}
```

## Test the plugin

When calling the `_search` API, you can send an additional `ext` parameter—an object containing the fields described at the beginning of the article.

### Indexing queries

Let’s write a query and use the plugin to capture behavioral metadata.

```
GET books/_search
{
  "query": {
    "match": {
      "name": "Snow"
    }
  },
  "ext": {
    "ubi": {
      "object_id_field": "url",
      "user_query": "snow",
      "client_id": "web_application",
      "query_attributes": {
        "app_component": "global_header"
      }
    }
  }
}
```

**object\_id\_field:** Is the field we want to use to identify our results and store them on the `ubi_queries` index as a result set.
**user\_query:** What the user typed in the search bar.
**client\_id:** Originator of the query
**query\_attributes:** Arbitrary key/values.

Along with the results, the response will include a `query_id` that we can use to inspect the `ubi_queries` index:

```
{
  "ext": {
    "ubi": {
      "query_id": "cb26ba2c-27ab-4af3-905b-00aff928cf50"
    }
  },
  "hits": {
    "total": {
      "value": 1,
      "relation": "eq"
    },
    "max_score": 1.5904956,
    "hits": [
      {
        "_index": "books",
        "_id": "Ep2h4ZcBDN5ljpdU06rw",
        "_score": 1.5904956,
        "_source": {
          "name": "Snow Crash",
          "author": "Neal Stephenson",
          "release_date": "1992-06-01",
          "page_count": 470,
          "price": 14.99,
          "url": "https://www.amazon.com/Snow-Crash-Neal-Stephenson/dp/0553380958/",
          "image_url": "https://m.media-amazon.com/images/I/81p4Y+0HzbL._SY522_.jpg",
          "_extract_binary_content": true,
          "_reduce_whitespace": true,
          "_run_ml_inference": true
        }
      }
    ]
  }
}
```

The document stored in `ubi_queries` will look like this:

```
  {
        "_index": "ubi_queries",
        "_id": "HJ204ZcBDN5ljpdUKKo2",
        "_score": 4.7303333,
        "_source": {
            "query_response_id": "59474463-5862-4941-992e-50cafc294274",
            "user_query": "snow",
            "query_id": "cb26ba2c-27ab-4af3-905b-00aff928cf50",
            "query_response_object_ids": [
                "https://www.amazon.com/Snow-Crash-Neal-Stephenson/dp/0553380958/"
            ],
            "query": """{
                "query": {
                    "match": {
                        "name": {
                            "query": "Snow"
                        }
                    }
                },
                "ext": {
                    "query_id": "cb26ba2c-27ab-4af3-905b-00aff928cf50",
                    "user_query": "snow",
                    "client_id": "web_application",
                    "object_id_field": "url",
                    "query_attributes": {
                        "app_component": "global_header"
                    }
                }
            }""",
            "query_attributes": {
                "app_component": "global_header"
            },
            "client_id": "web_application",
            "timestamp": 1751838369845
        }
    }
```

The document will contain the query executed by Elasticsearch, the metadata we provided, the list of documents matched, and also an additional identifier for the query response.

With this data, we can now analyze trends like top queries, top queries with no results, top documents in the results set, and apply filters on things such as client application, application component, and time-base filters.

### Capturing events

Let’s imagine that during that same search, the user clicked one of the results, and we want to capture that event and correlate it with the query we just indexed. To capture client-side events (e.g, clicks on the results), the application must send the event to the `ubi_events` index:

```
POST ubi_events/_doc
{
  "action_name": "click",
  "query_id": "cb26ba2c-27ab-4af3-905b-00aff928cf50",
  "client_id": "web_application",
  "timestamp": "2025-05-09T19:56:55.579Z",
  "message_type": "CLICK_THROUGH",
  "message": "Clicked Snow Crash",
  "user_query": "snow",
  "event_attributes": {
    "object": {
      "object_id": "Ep2h4ZcBDN5ljpdU06rw"
    },
    "position": {
      "ordinal": 1
    }
  }
}
```

Now we’ve captured the document, the click on that search, the position (`position.ordinal`), and the original value of `id` *(object\_id).*

This event allows us to identify the most clicked documents, the user’s queries that generate the most clicks, and whether users are clicking results in the top positions or not.

### Insights analysis

We can use ES|QL to analyze our data. Let’s look for the top 5 queries by counting the `ubi_queries` index documents by `user_query`:

```
POST /_query?format=txt
{
  "query": """
    FROM ubi_queries
    | STATS count = COUNT(*) BY user_query
    | SORT count DESC
    | LIMIT 5
  """
}
```

You will get your results formatted as a table:

```
     count     |  user_query   
---------------+---------------
54             |fahrenheit         
14             |snow           
9              |summer books         
4              |top seller        
2              |alastair
```

## Conclusion

In this article, we learned how to capture UBI queries and events using the Elasticsearch plugin, and how to work with the basic fields needed to extract meaningful insights.

In the next article, we’ll take this further by capturing richer metadata, writing more advanced ES|QL queries, and building Kibana dashboards to help us better understand our users and deliver an improved search experience.

**Note:** The o19s User Behavior Insights (UBI) plugin mentioned in this article is a third-party, community-maintained plugin and is not officially supported by Elastic. For questions or issues related to this plugin, please refer to the o19s UBI project repository at <https://github.com/o19s/ubi>.

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