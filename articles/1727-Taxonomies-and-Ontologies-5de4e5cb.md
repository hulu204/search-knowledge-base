---
title: 'Taxonomies and Ontologies'
company: Tunkelang
tag: 查询理解
date: 2017-08-30
url: https://queryunderstanding.com/taxonomies-and-ontologies-8e4812a79cb2
account: 
origin: harvest3-202607
---
# Taxonomies and Ontologies

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--8e4812a79cb2---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--8e4812a79cb2---------------------------------------)

3 min read

·

Jul 27, 2017

--

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D8e4812a79cb2&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Ftaxonomies-and-ontologies-8e4812a79cb2&source=---header_actions--8e4812a79cb2---------------------post_audio_button------------------)

Share

In order to understand queries, it’s important to ground that understanding in a knowledge base. Two common ways to represent a knowledge base are [taxonomies](https://en.wikipedia.org/wiki/Taxonomy_(general)) and [ontologies](https://en.wikipedia.org/wiki/Ontology_(information_science)).

**Taxonomies**

Taxonomies date back to [Aristotle](https://en.wikipedia.org/wiki/Aristotle) as a way to organize knowledge. A taxonomy is a hierarchical classification system: a tree that starts from a universal root concept and progressively divides it into more specific child concepts. The nodes of a taxonomy correspond to concepts, connected by branches or edges directed from the root node towards the leaf nodes.

Perhaps the most famous taxonomy in use today is the [Dewey Decimal System](https://en.wikipedia.org/wiki/Dewey_Decimal_Classification), used by libraries to organize their materials by subject. For example, *butterflies* are classified as *Natural Science (500)* -> *Zoological Sciences (590)* > *Other Invertebrates (595)* -> *Insects (595.7)* -> *Lepidoptera (595.78)* -> *Butterflies (595.789)*.

A proper taxonomy is a strict hierarchy — that is, every node other than the root has precisely one parent. In practice, it’s common to relax this constraint by allowing nodes to have multiple parents. For example, in a consumer product taxonomy, *USB Cables* might be a descendant of both *Computer Accessories* and *Cell Phone Accessories*.

The rigid constraints of a single hierarchy have led many people to use [faceted classification](https://en.wikipedia.org/wiki/Faceted_classification) systems instead. In a faceted classification, a topic is composed from nodes in multiple, independent hierarchies. We’ll discuss faceted classification — and its use in [faceted search](https://en.wikipedia.org/wiki/Faceted_search) — in a future post.

Regardless, it’s a good idea to minimize the amount of shared parentage in a taxonomy, as shared parentage introduces complexity. A little bit can go a long way to model the messiness of the real world. But it’s strictly forbidden to have cyclical relationships, e.g., a concept can’t be its own grandparent. The chain of parents from a node must always lead to the root.

**Ontologies**

Ontologies are somewhat more complex than taxonomies. While taxonomies represent a collection of topics with “is-a” relationships, ontologies make it possible to express a much richer collection of objects and relationships, such as “has-a” and “use-a”. There can be classes, instances of those classes, class attributes, and general relationships among classes instances. Moreover, the relationships aren’t necessarily binary — for example, a *co-worker* relationship might connect three instances: two people and the place where they worked together.

The complexity of ontologies makes them powerful but dangerous. In order to represent a complex domain like medicine and reason over it, it may be necessary to use an ontology like [SNOMED CT](https://en.wikipedia.org/wiki/SNOMED_CT). But to organize products or documents on a site aimed at non-expert consumers, it’s probably best to stick to a simple taxonomy or faceted classification system.

**Query Understanding**

We can implement query understanding by mapping queries to taxonomies or ontologies. The simplest approach is to treat taxonomy nodes as categories and train a classifier to map queries to categories, e.g., mapping the query *knapsack* to the node *Bags and Purses* -> *Backpacks*. A far more complex approach is to parse queries and represent them as networks of relationships in an ontology.

Either approach requires a significant amount of effort and data — whether from explicit human judgments, implicit behavioral judgments, or curated knowledge — to establish a mapping. Just having a taxonomy or ontology as a knowledge base doesn’t tell us how to apply it to queries.

But a knowledge base establishes the platform on which to build query understanding systems. A knowledge base — even it’s just a simple taxonomy — is essential for query understanding.

**Previous:** [**Entity Recognition**](/entity-recognition-763cae840a20)

**Next:** [**Autocomplete**](/autocomplete-69ed81bba245)