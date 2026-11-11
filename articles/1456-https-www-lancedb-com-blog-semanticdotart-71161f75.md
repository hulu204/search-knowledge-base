---
title: 'https://www.lancedb.com/blog/semanticdotart'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/semanticdotart
account: 
origin: en-rss
---
# SemanticDotArt: Rethinking Art Discovery with LanceDB

[Ayush Chaurasia](/author/ayush-chaurasia)

•

October 16, 2025

•

[Applications](/category/applications)

![1456-https-www-lancedb-com-blog-semanticdotart-71161f75-fig-001](../images/1456-https-www-lancedb-com-blog-semanticdotart-71161f75/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

‍[Try it out →](https://www.semantic.art/)

In an age of infinite scroll, we can browse more art than any real-world gallery could hold–yet finding a piece that feels right could still take minutes, or hours. **SemanticDotArt** began with a hunch: meaning lives not in pixels or tags, but in the mood of a painting, the rhythm of a brushstroke, or the metaphors that tie them together. From that intuition grew a multimodal retrieval system we built, with LanceDB at its core. This post traces the journey of how words meet images, and how we taught search to feel a little more human.

## The Vision

Art discovery often begins with a mood, rather than a checklist of traits. We imagine what we’re looking for through thoughts like: “find me something restless but hopeful,” “show me a painting that feels like a quiet storm.” SemanticDotArt is built for that kind of language. It lets you search not just with literal phrases, but with poetry, prose, or the emotions they stir in you. Sometimes, *how* you ask is part of what you’re looking for.

![1456-https-www-lancedb-com-blog-semanticdotart-71161f75-fig-002](../images/1456-https-www-lancedb-com-blog-semanticdotart-71161f75/figure-002.avif)

We wanted:

* A unified art corpus that continually grows across museums, marketplaces, and open archives.
* Metadata which captures both literal content and emotional subtext.
* A retrieval engine that can handle large amounts of text and images, and knows when a query is poetic, prosaic, artistic or literal.
* An interface that feels exploratory, rather than transactional.

LanceDB is used as the multimodal foundation for this system, because it offers the following key features:

* On disk index which allow building large scale multi-feature multi-index retrieval system
* First-class hybrid & full-text search support, fast SQL-style filtering
* Built-in support for various multimodal embedding models, and hooks for creating custom rerankers.
* Being truly multimodal, it doubles as an object store, every artwork’s vectors, text, and JPEG bytes live in the same source table, preventing chaos as we keep adding new features.

## How this works

As with any other retrieval system, the workflow is broken down into two main parts: ingestion and querying.

### Multi-representation

The guiding principle is simple: we create multiple representation of the artworks so the we have different ways of looking at it. For any given piece, we record multiple perspectives: poetic impressions, literal descriptions, mood tags, color palettes, and even stylistic fingerprints. Some become vector columns, some remain as text, and others live on as raw media. LanceDB lets us stitch all of that into a single row of a table so we can keep adding features as the dataset evolves without reindexing the world. The main idea is to offer maximum flexibility at query time, so that we can experiment with different search paths dynamically, as we’ll see in the next section.

#### A single painting, many views

‍

![1456-https-www-lancedb-com-blog-semanticdotart-71161f75-fig-003](../images/1456-https-www-lancedb-com-blog-semanticdotart-71161f75/figure-003.avif)

Take Van Gogh’s **Path Through a Field with Willows**. We keep several parallel interpretations so that whichever language a visitor uses, there is an index ready to meet it. Here are examples of some:

* Poetic caption

> A path winds on beneath a vibrant sky, where sun-warmed grasses whisper secrets. Brushstrokes dance with restless energy, quiet fields hold deep intensity, and a lonely journey is bathed in golden light. Nature breathes both calm and wild, colors sing a song of solitude, and hope lingers where the track ascends.

* Natural caption

> A path meanders under a bright sky as sun-warmed grasses softly rustle and energetic brushstrokes of light and shadow play across quiet fields. The solitary journey glows with golden light, nature around it feels tranquil yet untamed, and the colors evoke solitude while hope follows the upward slope of the path.**‍**

* **Mood keywords** — **`nature`**, **`solitude`**, **`dream`**, **`deep`**, **`track`**, **`intensity`**, **`path`**, **`field`**, **`willows`**,

These ingredients seed separate full-text, vector, and keyword indexes. The corpus keeps expanding, but because the representations belong to the same row, we can add new features, such as palette embeddings, brushstroke fingerprints, provenance signals, without having to refactor our storage solution.

![1456-https-www-lancedb-com-blog-semanticdotart-71161f75-fig-004](../images/1456-https-www-lancedb-com-blog-semanticdotart-71161f75/figure-004.avif)

## Semantic Routing: Matching Feelings with Features dynamically

Because each piece of artwork is over-represented in the data, retrieval turns into a choose-your-own-adventure task. A session might start with text, an image, or both. Semantic routing inspects that intent and helps us choose the dynamic search path that fits poetic vectors when the request feels lyrical, with natural-language embeddings for straightforward descriptions, and visual features when a user starts with image/pixels. Along the way, new features can be added in as they become available. When we blend or rewrite the query, mood hint keywords are used with LanceDB’s SQL-style prefilters to narrow down the search space. Finally, a custom reranker weights the results to surface pieces that echo the emotional signature of the request.

This is our rendition of classic retrieval strategies like query understanding, query rewriting, and multi-index routing. The agent classifies how the visitor is describing the art, rephrases the prompt so it aligns with the chosen representation, and finally selects which LanceDB indices to use. Every new representation we add becomes another branch the router can learn to take. From there, we can switch tactics on the fly depending on the query type and the column that seems most relevant.

With LanceDB, a complex hybrid search with prefiltering and reranking looks is simply:

```
results = (
    table.search(query_type="hybrid", vector_column_name="poetic_vector")
         .vector(query_embedding)
         .text(query_text)
         .where(prefilter_clause, prefilter=True)
         .limit(10)
         .rerank(CustomKeywordRanker(keywords))
)
```

![1456-https-www-lancedb-com-blog-semanticdotart-71161f75-fig-005](../images/1456-https-www-lancedb-com-blog-semanticdotart-71161f75/figure-005.avif)

Here’s how one of those pathways can unfold when someone uploads an image and adds a short poem:

1. **Classify the intent** – Label the request as **`poetic`**, **`natural`**, or another style so downstream steps know which feature column to favor.
2. **Caption the image** – If pixels are present, synthesize a caption in the same style as the intent so image and text signals travel together.
3. **Rewrite the prompt** – Blend the visitor’s words and the generated caption into a single rewritten query that preserves both mood and literal anchors.
4. **Extract mood keywords** – Pull out a keyword set that reflects the emotional signature sitting inside the rewritten query.
5. **Prefilter via SQL support** – Apply a LanceDB filter using those keywords so the search space collapses to artworks that share at least one mood.
6. **Choose search technique** – Switch between full-text, vector, or hybrid search depending on length and style – we over-fetch by roughly 2× so the reranker has room to maneuver.
7. **Rerank** – Score the candidates with a custom keyword ranker that weights overlap between query and artwork moods, then surface the pieces that best echo the request.

‍

The reranker leans on a weighted blend of recall and precision over the keyword sets:

$$ \text{score} = w \cdot \left( 0.7 \cdot \frac{\text{matches}}{|B|} + 0.3 \cdot \frac{\text{matches}}{|A|} \right) $$

Where `matches` is the overlap count between the artwork keyword set (`A`) and the query keyword set (`B`), so the recall term is represented by:

$$
\frac{|A \cap B|}{|B|}
$$

and the precision term by:

$$
\frac{|A \cap B|}{|A|}
$$

This keeps the responses feeling both relevant and surprising without drifting into uncanny matches. LanceDB supports custom rerankers natively, so we can plug in new ranking strategies as the dataset and features evolve.

## Conclusion

AI-generated images are everywhere, but the thrill of discovery still belongs to human-made art. SemanticDotArt uses AI as a bridge: drop in an image a model just imagined, or a photo you took, and it will lead you to the paintings and sculptures shaped by people who *felt* that idea before you did. Whether you search with a poetic cue like “*a quiet optimism painted in the sky*” or with a literal description, the path ends in the same place: human creations that echo your feeling.

![1456-https-www-lancedb-com-blog-semanticdotart-71161f75-fig-006](../images/1456-https-www-lancedb-com-blog-semanticdotart-71161f75/figure-006.avif)

[Try SemanticDotArt →](https://www.semantic.art/)

## Tools used

![1456-https-www-lancedb-com-blog-semanticdotart-71161f75-fig-007](../images/1456-https-www-lancedb-com-blog-semanticdotart-71161f75/figure-007.avif)

* **LanceDB** – Core multimodal store and retrieval engine: vectors, captions, mood keywords, and original JPEGs share one table, with hybrid search and custom rerankers stacking on top.
* **Google Gemini** – Multimodal model powering poetic rewrites, intent classification, and on-demand captioning to keep text and image evidence aligned.
* **Modal Labs** – Managed the backend services and high-throughput batch ingestion pipelines without building new infrastructure.

## Credits

This project was created by Bryan Bischof, Ayush Chaurasia, and Chang She. Kelly Chong and Pavitar Saini designed and implemented the UI. Adam Conway and Mischa Lamoureux assisted with the website.

![1456-https-www-lancedb-com-blog-semanticdotart-71161f75-fig-008](../images/1456-https-www-lancedb-com-blog-semanticdotart-71161f75/figure-008.avif)

[Ayush Chaurasia](/author/ayush-chaurasia)

ML Engineer @ LanceDB

[GitHub](https://github.com/ayushchaurasia)[Linkedin](https://www.linkedin.com/in/ayushchaurasia/)[Twitter](https://x.com/ayushchaurasia)

![1456-https-www-lancedb-com-blog-semanticdotart-71161f75-fig-009](../images/1456-https-www-lancedb-com-blog-semanticdotart-71161f75/figure-009.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1456-https-www-lancedb-com-blog-semanticdotart-71161f75-fig-010](../images/1456-https-www-lancedb-com-blog-semanticdotart-71161f75/figure-010.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1456-https-www-lancedb-com-blog-semanticdotart-71161f75-fig-011](../images/1456-https-www-lancedb-com-blog-semanticdotart-71161f75/figure-011.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb