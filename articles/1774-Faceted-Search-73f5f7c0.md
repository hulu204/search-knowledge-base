---
title: 'Faceted Search'
company: Tunkelang
tag: 搜索相关性
date: 2024-04-11
url: https://queryunderstanding.com/faceted-search-7d053cc4fada
account: 
origin: harvest3-202607
---
# Faceted Search

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--7d053cc4fada---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--7d053cc4fada---------------------------------------)

5 min read

·

Jan 24, 2018

--

2

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D7d053cc4fada&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Ffaceted-search-7d053cc4fada&source=---header_actions--7d053cc4fada---------------------post_audio_button------------------)

Share

[Faceted search](https://en.wikipedia.org/wiki/Faceted_search) is a topic broad enough to deserve its own [book](https://www.amazon.com/Synthesis-Lectures-Information-Concepts-Retrieval/dp/1598299999). It has become a standard feature of all modern search engines, including open-source platforms like [Solr](https://lucene.apache.org/solr/) and [Elastic](https://www.elastic.co/).

In this post, I’ll quickly explain how faceted classification and faceted search work. I’ll then outline how faceted search interacts with some of the query understanding approaches discussed in previous posts.

**Faceted Classification**

Faceted search starts with [faceted classification](https://en.wikipedia.org/wiki/Faceted_classification). Faceted classification uses a collection of independent attributes, called facets, to classify each entry in the searchable collection. In contrast with a [taxonomy](https://en.wikipedia.org/wiki/Taxonomy_(general)) that uses a single hierarchical classification scheme, faceted classification doesn’t impose a rigid ordering of attributes on the searcher.

**A Single Taxonomy is Inflexible**

The best way to understand faceted classification is to see it in contrast with the limitations of using a single taxonomy when it comes to representing independent attributes. Let’s look at an example.

Consider a clothing site with products organized using a single taxonomy. Should the top level of the taxonomy correspond to gender (*Men’s*, *Women’s*, etc.) or to product type (*Shirts*, *Pants*, etc.)? Or to some other attribute?

If gender is the top level, then *Men’s* will have *Men’s Shirts* and *Men’s Pants* as children nodes in the taxonomy, while *Women’s* will have *Women’s Shirts* and *Women’s Pants* as its children. If product type is the top level, then *Shirts* will have *Men’s Shirts* and *Women’s Shirts* as its children, etc.

This choice, which is somewhat arbitrary, has important consequences for searchers. Searchers who browse the product taxonomy will be limited to the taxonomy’s order. If gender is the top level, then the taxonomy won’t have a node corresponding to all shirts. Conversely, if product type is the top level, then it won’t have a node corresponding to all men’s clothing.

If we look beyond this trivial example with just two attributes, we can see that the number of these choices for a single taxonomy grows exponentially (actually, factorially) with the number of independent attributes. While some orderings are more natural than others, any fixed ordering imposes rigidity.

**The Flexibility of Facets**

A more flexible approach is to have two distinct facets for *Gender* and *Product Type*. There is not hierarchical relationship between the two facets: each men’s shirt is assigned the facet values *Gender: Men’s* and *Product Type: Shirts*. Rather than imposing an order on the attributes, faceted classification represents their independence explicitly by modeling each independent attribute as a first-class facet.

There can still be hierarchical relationships within a facet; for example, in the *Product Type* facet, *Shirts* can have child values like *T-Shirts* and *Dress Shirts*. But these are true hierarchical relationships, rather than intersections of independent attributes.

The main benefit of faceted classification it that it allows searchers to traverse the facets in any order they choose. In a faceted classification, it’s possible for searchers to retrieve all products with *Product Type: Shirts* or all products with *Gender: Men’s*. Faceted classification removes the limitations that a single taxonomy imposes by ordering the attributes.

**Faceted Search**

Faceted search takes advantage of faceted classification to support query refinement. For example, someone who searches for *polo* can narrow the search results by selecting *Gender: Men’s* and *Product Type: Shirts*. Combining an initial free-text search with faceted refinement allows the searcher to express a highly specific intent.

In particular, faceted refinement is most useful when the initial search query returns a large result set, often because it is a short query with low specificity. One use of faceted refinement is to clarify ambiguous search queries, e.g. *matrix* -> *Genre: Science Fiction* vs. *matrix* -> *Product Type: Textbooks*. But the best use of faceted search is for queries that are unambiguous but broad.

For example, a search for *shirts* on a clothing site may return thousands of results, overwhelming the searcher. In response to such a query, the search engine presents a set of facets (gender, style, brand, color, etc.) and associated values that organize the results into multidimensional space that the searcher can navigate.

This brief discussion of faceted search glosses over its complexities. In particular, faceted search creates design challenges when there are a large number of facets, or when a facet has a large number of values. For more discussion of these and other issues, I recommend a [book](https://www.amazon.com/Synthesis-Lectures-Information-Concepts-Retrieval/dp/1598299999) that offers a fuller treatment of the subject.

**Query Scoping**

Faceted search interacts naturally with [query rewriting](/query-rewriting-an-overview-d7916eb94b83) — particularly [query scoping](/query-scoping-ed61b5ec8753). Indeed, much of query rewriting and query scoping is an attempt to automate the faceted refinement process by inferring facet values from search queries.

When query segments obtained from [query segmentation](/query-segmentation-2cf860ade503) match facet values, the search engine can rewrite the query by substituting facet values for the corresponding segments. For example, a search for *stretch leather pants* becomes the single-word search *stretch*, refined by the two facet values *Material: Leather* and *Product Type: Pants*. This rewriting is just query scoping, taking advantage of the faceted classification.

In this example, the matches to facet values are exact. But, as we’ve seen in previous posts, we can take advantage of [stemming](/stemming-and-lemmatization-6c086742fe45), [spelling correction](/spelling-correction-471f71b19880), and [query expansion](/query-expansion-2d68d47cf9c8) to match facet values more aggressively.

**Autocomplete**

Another place that facets are useful for query understanding is [autocomplete](/autocomplete-69ed81bba245). Facet values tend to be great autocomplete suggestions, since they hopefully represent a curated collection of unambiguous search intents.

Facet values are good candidates for autocomplete when there isn’t enough data about query popularity and performance to determine autocomplete suggestions from historical search behavior. They’re particularly useful for new search applications, as well as applications that are unlikely to even collect a volume of traffic.

**Related Search Suggestions**

Search queries composed entirely of facet value selections tend to be more reliable than queries composed of arbitrary keywords. For example, a search for the facet value *Product Type: Suits* avoids [precision](https://en.wikipedia.org/wiki/Information_retrieval#Precision) problems (e.g, bathing suits and body suits that match the keyword *suit*, as well as [recall](https://en.wikipedia.org/wiki/Information_retrieval#Recall) problems (e.g.,, tuxedos that don’t match the keyword *suit*).

As discussed, autocomplete provides an opportunity to guide users to queries composed of facet values. But another opportunity for guidance is to present search suggestions along with the search results. For example, a search for *two piece swimsuit* can suggest *Product Type: Bikinis* as a related search.

Related search suggestions can be based on query similarity, content similarity, and historical query reformulation behavior. For an example of a related search suggestion system, see [this post](https://engineering.linkedin.com/search/metaphor-system-related-search-recommendations).

**Summary**

Faceted search has become a standard feature of modern search engines. Faceted classification offers more flexibility than a single taxonomy, and faceted refinement allows searchers to clarify and refine queries with large result sets. Faceted search also plays well with query scoping, autocomplete, and related search suggestions. Faceted search plays well with query understanding, and it’s a good idea to consider their interaction in designing a search experience.

**Previous:** [**Relevance Feedback**](/relevance-feedback-c6999529b92c)

**Next:** [**Search Results Presentation**](https://medium.com/query-understanding/search-results-presentation-7d6c6c384ec1)