---
title: 'Introducing layered ranking for RAG applications'
company: Vespa
tag: 排序
date: 2025-06-30
url: https://blog.vespa.ai/introducing-layered-ranking-for-rag-applications/
account: 
origin: harvest3-202607
---
{
}

[Subscribe](https://vespa.ai/subscribe/)

# Vespa Blog

We Make AI Work

Share

![Jon Bratseth](/assets/avatars/bratseth.jpg)

[Jon Bratseth](/authors/bratseth/ "Jon Bratseth")
[Follow](https://twitter.com/jonbratseth)
  
CEO Vespa.ai

30 Jun 2025

# Introducing layered ranking for RAG applications

Your RAG system won’t be better than the information you can supply to the LLM.
There’s a growing realization that the context of the LLM is a sparse resource that must be spent intelligently,
as seen in the sudden popularity of the term [context engineering](https://x.com/karpathy/status/1937902205765607626):

> *in every industrial-strength LLM app, context engineering is the delicate art and science of
> filling the context window with just the right information for the next step.*   
>   
> - Andrej Karpathy

Part of this is retrieving just the right information (the green chunks) to add to the context - no more and no less.

![Layered ranking](../assets/2025-06-30-introducing-layered-ranking-for-rag-applications/layered-ranking.png)

Until now, RAG systems have relied purely on document ranking to populate the LLM context:
The entire top N ranked documents are retrieved to add to the context. In Vespa 8.530 we’re for the first time
changing this paradigm in retrieval systems by introducing layered ranking, where ranking functions can be
used both to score and select the top N documents, and also to select the top M chunks of content within each
of those documents. This second layer ranking happens distributed in parallel on the content nodes storing those
documents, which ensures this scales with constant latency to any query rate and document size.

This allows you to efficiently and flexibly choose the most relevant pieces from a larger set of documents
rather than being forced to choose between fine-grained chunk-level documents missing context, or requiring
the LLM to deal with a large context containing irrelevant information:

|  |  |  |
| --- | --- | --- |
| **Before layered ranking**, you had two options, both bad: | | |
|  | Pro | Con |
| **Chunk-level documents** | * Only the most relevant chunks are selected | * Documents lack context relevant for ranking * Document-level metadata must be duplicated * Expensive due to producing very large document sets |
| **Multi-chunk documents** | * Chunks can be scored with full context * No metadata duplication * No document count explosion | * All chunks of each document are selected, leading to large context   windows with irrelevant information, and excessive bandwidth usage with large documents |
| **With layered ranking**, we get the best of both: | | |
| **Multi-chunk documents** | * Chunks can be scored with full context * No metadata duplication * No document count explosion * Only the most relevant chunks of each document are selected,   leading to optimal use of resources and the LLM context window |  |

Here’s an example Vespa [schema](https://docs.vespa.ai/en/reference/schema-reference.html) using the new layered ranking to select the best chunks of each document
in addition to selecting the best documents:

```
schema docs {
    document docs {

        field embedding type tensor<float>(chunk{}, x[386]) {
            indexing: attribute
        }

        field chunks type array<string> {
            indexing: index | summary
            summary {
                select-elements-by: best_chunks
            }
        }

    }

    rank-profile default {

        function my_distance() {
            expression: euclidean_distance(query(embedding), attribute(embedding), x)
        }

        function my_distance_scores() {
            expression: 1 / (1+my_distance)
        }

        function my_text_scores() {
            expression: elementwise(bm25(chunks), chunk, float)
        }

        function chunk_scores() {
            expression: join(my_distance_scores, my_text_scores, f(a,b)(a+b))
        }
        
        function best_chunks() {
            expression: top(3, chunk_scores)
        }
        
        first-phase {
            expression: sum(chunk_scores())
        }
        
        summary-features {
            best_chunks
        }

    }
}
```

Notice that:

* Ranking scores for both vector similarity and lexical match are calculated per chunk.
* These scores are combined (here:sum) to capture an aggregated score per chunk, and the sum of these makes up the total document score. This could also be a completely different scoring function, not relying on chunk scores.
* The chunks summary field is capped (here to top 3) using the new [select-elements-by summary](https://docs.vespa.ai/en/reference/schema-reference.html#select-elements-by) function, which points to the chunk scoring function used to select them.

Underlying this are new general tensor functions in [Vespa’s tensor computation engine](https://docs.vespa.ai/en/tensor-user-guide.html#) that allow filtering and ordering of tensors:

* [filter\_subspaces(tensor, f(x)(expr))](https://docs.vespa.ai/en/reference/ranking-expressions.html#filter-subspaces)
* [cell\_order(tensor, order)](https://docs.vespa.ai/en/reference/ranking-expressions.html#cell-order)

as well as a new composite tensor function using those:

* [top(n, tensor)](https://docs.vespa.ai/en/reference/ranking-expressions.html#top-t)

and the elementwise bm25 rank feature:

* [elementwise(bm25(field), dimension, cell\_type)](https://docs.vespa.ai/en/reference/rank-features.html#elementwise-bm25)

You can experiment with this in [Tensor Playground](https://docs.vespa.ai/playground/#N4IgZiBcDaoPYAcogMYgDQiZUAXZABLgBYCmBAjgK4CGANgJa4CeBcYB9dBKxVAdgGsAziAC+Y9PGwhSGLFFD9kuAIzy5kELlL9hcAE4AeMHTg1cAPgAUvAYOBiAlDgAMkVQGZ0qyAHZ0ACZIAFZ0Tw8wgBZIT1d0EMhAsXFJaWQ0TGw8QgA5AgZhAgATZn4aAFsGNAkpEERkOSzFEGUtXI1kT1S6hq1MhRxtQjAGfmK2A2LSAzGAczYOFFI6OlFa9K0mwaUVQM7+lboAfUNpg2s1dAIKmgAPJx7N1Hls4a0bmkFyGk-hQQIYEMRDIBAARqRhLgCB0NvUZNs3m1tN1MJptIEjLC0vCMq8WvgPsUDIhOKsCMIqGDhAgaMsimASRUQeRbv8QRZOAZyGB6MI5HC+rJ8UNkbgogdwAw6DoDMdKdTafTLt5AdZhE51U5HoKZAM3oSQDw4BUwWMedLZaQJmyAQB3JjESYMOZjehEXT6AyA4Hcykyp64rYi3ZaXAhSXigBUalSAF0xEA).

We believe this will revolutionize the quality we see in industrial-strength RAG applications,
and our largest production applications where high quality and scale is critical
are already busy putting it to use.

## FAQ

***Can’t I just select the chunks to put into the context from each document in my frontend?***

Yes, at small enough scale you can do anything :-) However, this approach breaks down at larger scale.
Having to send the entire document content, not just the pieces you need, really leads to two
separate scaling problems:

With a high query rate, you consume a large amount of bandwidth when collecting the entire
content of the top N documents on one node which then sends the entire payload to the frontend.

With a large corpus, you’ll have outlier documents which are very large, but which still contain
valuable information - we’ve seen documents as large as entire libraries in real applications.
Having to serialize and send such entire documents takes a long time and lots of resources,
leading to abysmal response times and impacting other queries by consuming too much bandwidth.

Of course, before you get to scaling, there’s also the more practical problem, and wasted cpu and latency,
of having to implement your own chunk scoring algorithm - including tokenization of the chunk text etc.

***We already have a solution for this for humans - dynamic snippets. Can’t the LLMs just use that?***

Unlike humans, LLMs are not continuous learners, they don’t accumulate information by reading their
emails, going to meetings and so on. They are completely dependent on the right contextual
information to make good decisions. Fortunately they are also different in another way: They read much faster than us!

Putting these two together gives us the right solution for LLMs: It’s both necessary and feasible to extract a lot more information from each document for an LLM than a dynamic snippet, and this information should be selected by relevance, not by surface similarity to query words.

***Aren’t you guys also saying that text relevance is a lot more than bm25? I want to select my chunks by some [other set of rank features](https://docs.vespa.ai/en/reference/rank-features.html#feature-list) than bm25 and vector closeness.***

You are right - there’s a lot of textual match information not captured by bm25. Going forwards we’ll
provide elementwisification of all text rank features, as well as allowing chunk-level metadata
to be accessed in chunk scoring functions.

## Read more

[![Perplexity builds AI Search at scale on Vespa.ai](/assets/2025-04-15-perplexity-builds-ai-search-at-scale-on-vespa-ai/perplexity-logo.svg)](/perplexity-builds-ai-search-at-scale-on-vespa-ai/)
[## Perplexity builds AI Search at scale on Vespa.ai

#### Perplexity chose to build on Vespa.ai to provide the world's most used RAG application.](/perplexity-builds-ai-search-at-scale-on-vespa-ai/)

[![Deploying RAG at Scale: Key Questions for Vendors](/assets/2024-10-23-deploying-rag-at-scale/deploying-rag-at-scale.png)](/deploying-rag-at-scale/)
[## Deploying RAG at Scale: Key Questions for Vendors

#### Retrieval-augmented generation (RAG) has emerged as a vital technology for organizations embracing generative AI.](/deploying-rag-at-scale/)

[![](/assets/logo/vespa-logo.svg)

## Free Vespa Cloud Trial

#### Deploy your application for free. Get started now to get $300 in free credits. No credit card required!](https://vespa.ai/free-trial/ )

* [#AI](/tags#AI)
* [#GenAI](/tags#GenAI)
* [#rag](/tags#rag)
* [#ranking](/tags#ranking)
* [#tensors](/tags#tensors)

[« Search me if You Can: Building the Next Generation Advanced RAG Solution in Lifesciences](/Search-Me-If-You-Can-Building-the-next-generation-advanced-RAG-Solution-in-lifesciences/)
[Vespa Newsletter, June 2025 »](/vespa-newsletter-june-2025/)

![Vespa Blog](/assets/logo/vespa-logo.svg)   Never miss a **story** from us, subscribe to our newsletter
[Subscribe](https://vespa.ai/subscribe/)