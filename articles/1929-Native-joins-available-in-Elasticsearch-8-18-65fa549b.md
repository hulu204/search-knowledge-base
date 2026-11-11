---
title: 'Native joins available in Elasticsearch 8.18'
company: Elastic
tag: 工程相关
date: 2025-04-15
url: https://www.elastic.co/search-labs/blog/elasticsearch-esql-lookup-join
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Native joins available in Elasticsearch 8.18

Exploring LOOKUP JOIN, a new ES|QL command available in tech preview in Elasticsearch 8.18.

April 15, 2025

[Costin Leau](/search-labs/author/costin-leau)

[ES|QL](/search-labs/blog/category/esql)[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

It's my pleasure to announce `LOOKUP JOIN`—a new ES|QL command available in tech preview in Elasticsearch 8.18, designed to perform left [joins](https://en.wikipedia.org/wiki/Join_(SQL)) for data enrichment. With ES|QL, one can query and combine documents from one index with documents from a second index based on a criterion defining how the documents should be paired natively in Elasticsearch. This approach enhances data management by dynamically correlating documents at query time across multiple indices, thus removing duplication.

For instance, the following query connects employee data from one index with their corresponding department information from another index using a shared field key name:

```
FROM employees
| LOOKUP JOIN departments ON dep_id
```

As the name indicates, LOOKUP JOIN performs a complementing, or [left (outer)](https://en.wikipedia.org/wiki/Join_(SQL)#Left_outer_join), join at *query* time between any regular index (employees) - the left side and any *lookup* index (departments) - the right side. All the rows from the left side are returned along with their corresponding equivalent (if any) from the right side.

![Elasticsearch lookup join](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt92b2b469d8e24f57/6a1705912b835f204cf4b10f/cce4f36ecbaa46f398e47dd18f3abc6e941e5514-691x464.png)

The lookup side's index mode must be set to lookup. This means that the underlying index can only have one shard. This current solution addresses the cardinality challenges of one side of the join and the issues that distributed systems like Elasticsearch encounter, which are outlined in the next section.

Apart from using the `lookup` index mode, there are no limitations on the source data or the commands used. Additionally, no data preparation is needed.

The join can be performed before or after the filtering:

```
// associate employees hired in the last year in departments in US and sort by department name
FROM employees
| WHERE hire_date > now() - 1 year
| LOOKUP JOIN departments ON dep_id
| WHERE dep_location == "US"
| KEEP last_name, dep_name, dep_location
| SORT dep_name
```

Be mixed with aggregations:

```
// count employees per country
FROM employees
| STATS c = COUNT(*) BY country_code
| LOOKUP JOIN countries ON country_code
| KEEP c, country_name
| SORT country_name
```

Or be combined with another join:

```
// find the error messages in the last hour alongside their source host name and error description
FROM logs
| WHERE message_type :"error"
| LOOKUP JOIN message_types ON err_code
| LOOKUP JOIN host_to_ips ON src_ip
| WHERE log_date > now() - 1 hour
| KEEP log_date, log_type, err_description, host_name
```

## Executing a Lookup Join in Elasticsearch

Let's illustrate what happens during runtime by looking at a basic query that doesn't include any other commands, such as filter. This will allow us to concentrate on the execution aspect as opposed to the planning phase.

```
FROM employees
| LOOKUP JOIN departments ON dep_id
| KEEP last_name, dep_name, dep_location
```

The **logical plan,** a tree structure representing the data flow and necessary transformations, is the result of translating the query above. This logical plan centers on the semantics of the query.

![Executing an Elasticsearch lookup join](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt29996171b9575af4/6a1705936f7f04fa4f914726/f9de2d111a8fc19f2377e2904b806915fe11c2ee-562x391.png)

To ensure efficient scaling, standard Elasticsearch indices are divided into multiple shards spread across the cluster. In a join scenario, sharding both the left (L) and right (R) sides would result in L\*R partitions. To minimize the need for data movement, lookup joins require the right side (which provides the enriching data) to have a single shard, similar to an enrich index, with the replication dictated by the index settings (default is 1).

This decreases the amount of nodes needed to execute the join, thereby reducing the problem space. As a result, L\*R becomes L\*1, which equals L.

![Elasticsearch indices divided into multiple shards](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf9c65b7d1fd15a73/6a170594b0367d4b4a72bc2d/6a0e86bead3ab536bb87c7d3b356113de74a2583-946x472.png)

Thus, the coordinator needs to dispatch the plan only to the left side data nodes, with the hash join performed locally using the lookup/right index to “build” the underlying hash map while the left side is used for “probing” for matching keys in batches.

![Elasticsearch lookup join data node distribution](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt630133861660370c/6a170596964ceab62608ba97/e2f5d1434b6db26428ba83fa119beae3888fc4b9-911x442.png)

The resulting distributed *physical* plan, which focused on the distributed execution of the query, looks as follows:

![Resulting distributed physical plan focusing on the distributed execution of the query.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltdeaa33b112728e2d/6a17059766c4f9e866f8bf36/553ce52bafb42ebf843faf5b64daa040518fcb24-452x575.png)

The plan consists of two main parts or sub-plans: the physical plan that gets executed on the **coordinator** (generally speaking, the node receiving/responsible for the query completion) and the plan fragment, which is executed on the **data nodes** (the nodes holding the data). Since the coordinator does not have the data, it sends a plan fragment to the relevant data nodes for local execution. The results are then sent back to the coordinator node, which computes the final results.

The communication between the two entities is represented in the plan through the `Exchange` block. The coordinator doesn't have to do much work for this query because most of the processing happens on the data nodes.

The fragment encapsulates the logical subplan, enabling optimization based on the specific characteristics of each shard's data (e.g., missing fields, local minimum and maximum values). This local replanning also helps manage differences in node code that might exist between nodes or between a node and the coordinator, for example, during cluster upgrades.

The **local physical plan** looks something like this:

![Elasticsearch local physical plan](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt216d5fc204c39918/6a170599d7c02204e7de6393/41cdbccb951bf390dad124b2373822db78aced2e-596x848.png)

The plan is designed to reduce I/O by using efficient data extraction methods. The two nodes at the bottom of the tree act as *roots*, supplying the nodes above. Each one outputs references to the underlying Elasticsearch documents (`doc_id`). This is done intentionally to delay the loading of columns (fields) or documents for as long as possible through the designated extraction nodes (in yellow). In this particular plan, loading takes place right before the hash join on each of the joining sides and prior to the final project just before the data exits the node using only the join resulting data.

## Future work on Lookup Join syntax

### Qualifiers

At the moment, the `lookup join` syntax requires the key to have the same name in both tables (similar to `JOIN USING` in some SQL dialects). This can be addressed through `RENAME` or `EVAL` :

```
FROM employees_new
| RENAME dep AS dep_id  // align the names of the group key
| LOOKUP JOIN departments ON dep_id
```

It’s an unnecessary inconvenience that we’re working on removing in the near future by introducing (source) qualifiers.

The previous query could be rewritten as (syntax wip):

```
FROM employees_new e
| LOOKUP JOIN departments ON e.dep == departments.dep_id
```

Notice that the join key was replaced by an equality comparison, where each side is using a field name qualifier, which can be implicit (departments) or explicit (e).

### More join types and performance

We are currently working on enhancing the `lookup join` algorithm to better exploit the data topology with a focus on specializations that leverage the underlying search structures and statistics in Lucene for data skipping.

In the long term, we plan to support additional join types, such as inner join (or intersection, which combines documents that have the same field on both sides) and full outer join (or union, which combines the documents from both sides even when there is no common key).

## Feedback

The path to native JOIN support in Elasticsearch has been a long one, dating back to version 0.90. Early attempts included [nested](https://www.elastic.co/guide/en/elasticsearch/reference/1.4/mapping-nested-type.html) and `[\_parent](https://www.elastic.co/guide/en/elasticsearch/reference/0.90/mapping-parent-field.html) ` field types, with the latter eventually being [rewritten](https://www.elastic.co/guide/en/elasticsearch/reference/2.0/breaking_20_parent_child_changes.html) (in 2.0), [deprecated](https://www.elastic.co/guide/en/elasticsearch/reference/5.0/breaking_50_mapping_changes.html#_literal__parent_literal_field_no_longer_indexed) (in 5.0), and [replaced](https://www.elastic.co/guide/en/elasticsearch/reference/6.0/mapping-parent-field.html) by the `join` field (in 6.0).

More recent features like [Transforms](https://www.elastic.co/guide/en/elasticsearch/reference/7.3/transforms.html) (7.3) and the [Enrich](https://www.elastic.co/guide/en/elasticsearch/reference/7.5/ingest-enriching-data.html) ingest pipeline (7.5) also aimed to address join-like use cases. In the wider Elasticsearch ecosystem, [Logstash](https://www.elastic.co/guide/en/logstash/current/plugins-filters-elasticsearch.html) and [Apache Spark](https://www.elastic.co/guide/en/elasticsearch/hadoop/current/spark.html) (via the [ES-Hadoop](https://www.elastic.co/elasticsearch/hadoop) connector) have provided alternative solutions. [Elasticsearch SQL](https://www.elastic.co/elasticsearch/sql), which debuted in 6.3.0, is also worth mentioning due to the grammar similarity: while it supports a wide range of SQL functionality, native JOIN support has remained elusive.

All these solutions work and continue to be supported. However, we think ES|QL, due to its query language and execution engine, significantly simplifies the user experience!

ESQL `Lookup join` is in tech preview, freely available in Elasticsearch 8.18 and Elastic Cloud—try it out and let us know how it works for you!

### Frequently Asked Questions

#### What is a LOOKUP JOIN in Elasticsearch?

A LOOKUP JOIN is a new ES|QL command available in tech preview in Elasticsearch 8.18, designed to perform left joins for data enrichment.

#### What are LOOKUP JOINS used for?

The LOOKUP JOINS use ES|QL commands to query and combine documents from one index with documents from a second index based on a criterion defining how the documents should be paired natively in Elasticsearch.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbca7a25e3c272aa8/6a17ffb1be60868d100049d2/6494d88d51edf6a5b31a92b8439792354eae7190-1536x1024.png)

[ES|QL](/search-labs/blog/category/esql)[AI](/search-labs/blog/category/ai)

### Using ES|QL COMPLETION + an LLM to write a Chuck Norris fact generator in 5 minutes

August 28, 2025|[Aurélien Foucret](/search-labs/author/aurelien-foucret)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltf69e1ba73bd5d402/6a6a340599442cd9e0df1d94/1794a179d9536e693a0982634da59aff209c9d68-1280x720.png)

[Analytics](/search-labs/blog/category/analytics)[ES|QL](/search-labs/blog/category/esql)[Python](/search-labs/blog/category/python-programming)

### How to instrument your search API with OpenTelemetry and query it with ES|QL

July 22, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt097721c03648a84e/6a6a33ef0a222b4c70877f32/8f6b95800c65fe389d3e8d8281e8e8dc351f734d-992x342.png)

[ES|QL](/search-labs/blog/category/esql)[ML Research](/search-labs/blog/category/ml-research)[Agentic AI](/search-labs/blog/category/agentic-ai)

### How Elasticsearch detects multiple change points in time series with 0.99 recall

July 24, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltdfa35fbcbbf4959f/6a1705b9dc55de19a4e00d07/e54132e915217063e9ed0ec45059c6cfc38e31dd-1280x720.png)

[ES|QL](/search-labs/blog/category/esql)[Vector Database](/search-labs/blog/category/vector-database)

### LINQ to Elasticsearch ES|QL: Write C#, query Elasticsearch

April 01, 2026|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3382265814939417/6a170df3a929cf1246ae0a61/fceada10b0c09d6a4a372f137bb3040e1ff41fbf-1600x895.png)

[ES|QL](/search-labs/blog/category/esql)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### Hybrid search and multistage retrieval in ES|QL

January 08, 2026|[Ioana](/search-labs/author/ioana-alina-tagirta)|[+2](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter