---
title: 'Combining sparse, dense and geo fields in Elasticsearch'
company: Elastic
tag: 召回
date: 2024-07-03
url: https://www.elastic.co/search-labs/blog/combining-sparse-dense-and-geo-fields
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Combining sparse, dense and geo fields in Elasticsearch

Explore Elasticsearch data fields, such as sparse, dense & geo fields, and how to combine them to produce in-depth analytics on your data.

July 03, 2024

[Madhusudhan Konda](/search-labs/author/madhusudhan-konda)

[Basics](/search-labs/blog/category/basics)

Jump to

Share

## How to combine multiple sparse, dense and geo fields in custom ways

Elasticsearch is a scalable data store and vector database, powerful for searching and analyzing data in near realtime. As developers, we often encounter datasets with various types of diverse fields. Some fields are mandatory or contain more than average populated data while others are barely populated. The fields with many missing values are called "Sparse" fields, while those with most values present are called "Dense" fields. Of course, we also have those geo-location fields representing geographical location data.

In this article, we look at how we can query data with diverse fields. We will explore the integration of sparse, dense, and geo fields to enhance your search functionalities. We'll walk through hands-on examples (using my favourite `books` index :) ), ingesting sample data into Elasticsearch via Kibana DevTools and performing lexical and geo searches.

Let's define these fields before we jump into details of how we can combine such fields to extract deeper analytical capabilities.

## Sparse fields

Sparse fields are fields that are not present in every document.

For instance, consider the `books` index consisting of various types of books. The `special_edition` field in our `books` index is sparse because not all books are released as special editions. Similarly, there might be other fields such as `category` or `sales_info` that might not necessarily be available for all books. Sparse fields are useful for filtering results based on attributes that only a subset of the dataset possesses.

## Dense fields

Conversely, dense fields are those expected to appear in all or most documents. Fields such as `title`, `author`, `number_of_pages`, and `publication_date` in our `books` index are considered dense fields. They are available for most if not all books and are core to each document. They help provide solid search queries.

## Geo fields

Geo fields allow for the indexing of geographic data which enables searches based on locations or geographic areas. In our `books` index, `topic_location` is a geo field that could represent various location-based attributes. Examples include the the location of the author, the place of the book's original print etc.

## Combining diverse fields

Combining these fields in custom ways can significantly enhance search capabilities and provide more relevant results. There are ample use cases where we would like to query the combination of sparsely populated fields with dense fields as well as geo-fields.

The power of Elasticsearch comes from its ability to handle complex queries combining various data types. By understanding the characteristics of sparse, dense and geo-location fields, we can craft focused search queries that cater to specific user needs.

Let's see how we can work with the diverse data fields by running through hands-on examples.

## Creating "books" index

First, let's define a `books` index with diverse field types that could apply to an online bookstore.

As you can see in the PUT request below, the mappings for the `books` index consist of some standard book attributes. However, you can also find some fields that might not apply to every book, for example:

* `available_copies`
* `special_edition`

These attributes are considered sparse as they aren't necessarily expected to be populated for every book. The other fields `title`, `author`, `publication_date` fields etc are expected to be present for every (or most) book.

And we expect combine these field with a geo-point field that could represent the location of the book's topic:

```
# Creating books mapping schema

PUT /books
{
  "mappings": {
    "properties": {
      "title": { "type": "text" },
      "author": { "type": "text" },
      "price": { "type": "float" },
      "tags": { "type": "keyword" },
      "publication_date": { "type": "date" },
      "available_copies": { "type": "integer" },
      "special_edition": { "type": "boolean" },
      "topic_location": { "type": "geo_point" },
      "genre": { "type": "keyword" },
      "language": { "type": "keyword" }
    }
  }
}
```

The above snippet code shows us the mapping schema for the `books` index. It consists of a mix of diverse fields - sparse, dense and geo-location fields.

Copy the code snippet and paste it into the Kibana console. Executing it will create our `books` index.

Now that we have created our mappings, let's index some sample data.

## Indexing sample data

We want to index a few books with data that represents our needs. The following sample documents add books with a mix of these attributes:

```
# Omitting special_edition and technology
# Note the location is Silicon Valley

POST /books/_doc/1
{
  "title": "Head First Java: A Brain-Friendly Guide",
  "author": " Kathy Sierra, Bert Bates, Trisha Gee",
  "price": 43.99,
  "tags": ["programming", "Java", "advanced"],
  "publication_date": "2024-03-20",
  "available_copies": 10,
  "topic_location": { "lat": 37.3861, "lon": -122.0839 },
  "genre": "Technology",
  "language": "English",
  "technology": "Java"
}

# Omitting 'special_edition'
# Note the location is London

POST /books/_doc/2
{
  "title": "Elasticsearch in Action 2e",
  "author": "Madhusudhan Konda",
  "price": 39.99,
  "tags": ["Elasticsearch", "Search", "Technology", "2nd Edition"],
  "publication_date": "2022-07-01",
  "available_copies": 10,
  "topic_location": { "lat": 51.5074, "lon": -0.1278 },
  "genre": "Technology",
  "special_edition": true,
  "language": "English",
  "technology": "Elasticsearch"
}

# Omitting 'available_copies', 'special_edition', and 'topic_location'
POST /books/_doc/3
{
  "title": "Functional Programming in Java",
  "author": "Venkat Subramaniam",
  "price": 36.99,
  "tags": ["Java", "Functional Programming", "Software Development"],
  "publication_date": "2018-03-15",
  "genre": "Technology",
  "language": "English",
  "technology": "Java"
}
```

As you can see, we've got four different books, each indexed with a few fields missing - thus demonstrating the concept of sparse fields.

With the data preparation out of the way, the next step is to write queries effectively making these diverse fields yield cool analytical insights.

We will write the following queries:

* Finding Java Books Near a Specific Location
* Fetching Special Edition Search Technology Books
* Searching for latest IT Books in Multiple Languages

The remainder of the article explains how to create queries combining the sparse, dense and geo fields.

## Finding Java books near a tech hub

Let's say we want to find Java books available near a location, say, SFO. We want to write a `bool` query to match the Java book within a geographic area. The following query does this job:

Here, we look for Java-related books near Silicon Valley:

```
# Searching for Java books in Silicon Valley

GET /books/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "technology": "Java" } }
      ],
      "filter": [
        { "geo_distance": { "distance": "100km", "topic_location": { "lat": 37.7749, "lon": -122.4194 } } }
      ]
    }
  }
}
```

Executing this query will return you the "Java" books in or around "Silicon Valley" - about a 100km radius. In this case, "Head First Java" will be returned.

The query combines the field types to achieve a targeted search objective. The query looks for books that specifically relate to "Java" - a `technology` field - which may not be relevant for all entries in the index. This is a sparse field scenario as not all the books have the `technology` field populated.

This example demonstrates how Elasticsearch can integrate diverse data types into a cohesive search strategy.

## Querying for special edition search technology books

Let's say our goal is to identify books within our database that are special edition books and pertain to search technology like Elasticsearch. This query extracts the books that might be particularly relevant to a specific audience interested in learning the technology in depth.

We again use a `bool` query to filter for special edition books related to search technologies:

```
# Special edition Technology books

GET /books/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "special_edition": true } },
        { "match": { "technology": "Elasticsearch" } }
      ],
      "should": [
        { "match": { "language": "English" } }
      ],
      "must_not": [
        { "range": { "publication_date": { "lt": "2015-01-01" } } }
      ],
      "minimum_should_match": 1
    }
  }
}
```

This query filters books based on the `special_edition` field (sparse) and a `genre` field (dense). The query becomes more universally applicable across the dataset since `genre` is a field that likely exists in every book document, making it a dense field.

In addition to the above requirements, we prefer the books to be published in English (though this is not a strict requirement due to `minimum_should_match` set to 1). This means books will not be excluded from the search results if they are not published in English. However, if they are published in English, those books will be ranked higher in the search results.

For completeness, I've added the `must_not` clause too - that'll exclude the books published before 2015. This allows us to focus on more recent publications.

In essence, this query provides a balanced search approach:

* Stringent criteria are used to filter books by their edition and genre,
* A preference is set for the English language to boost relevancy, and
* Not recent (published before 2015) books are filtered out to ensure recent copies only.

## Searching for latest IT books available in multiple languages

Let's say our users might be looking for the latest resources (books) to stay updated in the tech field but require materials accessible in their native (specific) languages. It's a common scenario in educational environments, multinational companies, or regions with bilingual populations. Although I don't read technical books in "Telugu" (a language of South India - where I'm originally from :)), I know a few of my friends would like tech stuff explained in their mother tongue.

Suppose we want to find the most recent IT books available in both English and Spanish, which might indicate broader educational value:

```
# Recent IT Books Available in Multiple Languages

GET /books/_search
{
  "query": {
    "bool": {
      "must": [
        { "range": { "publication_date": { "gte": "now-2y" } } }
      ],
      "filter": [
        { "terms": { "language": ["English", "Spanish"] } },
        { "match": { "genre": "Technology" } }
      ]
    }
  }
}
```

Let me explain the query in the context of "combined/diverse" fields:

The `publication_date` is likely a dense field because it's a standard attribute expected in every book record. By using the range query, we focus on books published within the last two years.

Similarly, `genre` is typically a dense field in book databases, as books are generally categorized into genres. The query filters for books specifically within the "Technology" genre. This ensures relevant books related to IT topics.

The `language` field can be considered sparse depending on the dataset. In a global dataset, books might be available in multiple languages, but not all books will be available in more than one language.

By filtering with the `terms` query for multiple languages - in this case, English and Spanish - we're fetching books that cater to a multilingual audience.

## Wrap up

That's a wrap. In this article, we've learned about diverse data fields - such as sparse, dense and geo fields - and mechanisms of combining them to produce in-depth analytics on our data.

### Frequently Asked Questions

#### What are dense fields in Elasticsearch?

Dense fields are those expected to appear in all or most documents. They help provide solid search queries.

#### What are sparse fields in Elasticsearch?

Sparse fields are fields that are not present in every document. Those fields are useful for filtering results based on attributes that only a subset of the dataset possesses.

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