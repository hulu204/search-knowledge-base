---
title: 'Nested Vectors Search in Apache Lucene'
company: Sease
tag: 召回
date: 2026-05-27
url: https://sease.io/2026/05/nested-vectors-search-in-apache-lucene.html
account: 
origin: harvest3-202607
---
When using Lucene’s parent-child block-join mode, you are dealing with a “one-to-many relationship”. You have a single document (parent) owning multiple vector embeddings (children).  
To search these, Lucene uses the **`DiversifyingChildrenFloatKnnVectorQuery`**. Its job is simple: find the k nearest parent documents by scoring children through HNSW graph traversal, returning at most one child — the best-scoring — per parent.

**The reason why we started this in-depth code analysis and further implementation was to make the entire process faster.**

## What do you need to know before

### Doc IDS vs Document Vector Ordinals

#### DocIDs

A docID is Lucene’s internal identifier for a document within a segment. Every document — whether a parent or a child — gets a sequential integer docID assigned when it is indexed. The block-join layout stores them consecutively:

```
				
					docId 0 → child1
docId 1 → child2
docId 2 → child3
docId 3 → parent1
docId 4 → child1
docId 5 → child2
docId 6 → parent2
				
			
```

#### Document Vector Ordinals

An ordinal is a separate sequential integer assigned only to documents that have a vector for a given field. Not every document has a vector — parents never do, and in sparse indexing, some children may not either. So ordinals form a compact, gap-free sequence over just the vector-bearing documents:

```
				
					docId 0 (child1, has vector) → ordinal 0
docId 1 (child2, has vector) → ordinal 1
docId 2 (child3, has vector) → ordinal 2
docId 3 (parent1, no vector) → no ordinal
docId 4 (child1, has vector) → ordinal 3
docId 5 (child2, has vector) → ordinal 4
docId 6 (parent2, no vector) → no ordinal
				
			
```

#### Why both exist

The HNSW graph uses ordinals as node identifiers — graph edges connect ordinals, not docIDs. When the graph says “node 3 is a neighbor of node 1”, it means the documents at ordinals 3 and 1, which are docIds 4 and 1, respectively.

Everything outside the HNSW graph — the parentBitSet, the collector, and query results — operates on docIDs.   
**[`OrdinalTranslatedKnnCollector`](https://lucene.apache.org/core/10_4_0/core/org/apache/lucene/util/hnsw/OrdinalTranslatedKnnCollector.html)** is the adapter that bridges these two ID spaces. It is a decorator around a regular **`KnnCollector`** that intercepts results coming out of the graph search and translates them from ordinal → docID before forwarding them to the wrapped collector.  
The reverse translation (docID → ordinal) is handled separately by **`docIdToOrdinal`**, which is used when converting external filters or bitsets into the graph’s internal ordinal space before search begins.

### BitSet

The **`parentBitSet`** is not a list of all documents — it’s a bit array over the segment’s docID space, where only parent positions are set to 1, and all child positions are 0. The Lucene block-join layout stores each block as consecutive docIDs with the parent always last:

```
				
					docId 0 → child1 (bit = 0)
docId 1 → child2 (bit = 0)
docId 2 → child3 (bit = 0)
docId 3 → parent1 (bit = 1) ← set
docId 4 → child1 (bit = 0)
docId 5 → child2 (bit = 0)
docId 6 → parent2 (bit = 1) ← set
				
			
```

This kind of data structure allows for quicker access to its elements. There is no hash map lookup, no stored parent pointer per child document, and no auxiliary structure to maintain.

## The Idea

After a discussion with other Lucene committers, we observed that:

* When the typical number of children per parent is small, eagerly translating each visited child back to its parent ordinal is surprisingly expensive. In many cases, it appears more efficient to post-process or “join back” to parent blocks rather than continuously resolving parent ordinals during traversal.
* The heap structure and parent/child translation logic show up significantly in benchmarks. Which is somewhat unexpected.
* When the search encounters a nearest child node during HNSW traversal, instead of treating it as an isolated signal, we could immediately gather and score *all siblings of that child’s parent* (i.e., all children under the same parent ordinal), under the assumption that they are likely to be similarly competitive. This “eager sibling expansion” turns a single graph hit into a localized, dense evaluation over the parent’s full child set.

Immediately bulk-scoring all of that parent’s unvisited siblings, rather than waiting for graph edges to eventually reach them, should:

1. Introduces a dynamic exploration strategy where the algorithm can evaluate minimum, maximum, and average sibling scores per parent, at the cost of extra local scoring but potentially reduced global traversal.
2. Accelerate convergence in best-first search scenarios by more quickly identifying strong parent candidates and raising the pruning threshold earlier.
3. Improve ranking quality; the heap always holds the best-known child per parent, not just the first encountered.

## Step 1 - Codebase audit

Before writing any code, a thorough review of the existing **`DiversifyingChildrenFloatKnnVectorQuery`** stack was carried out.

The conclusion: no bugs, no obvious inefficiencies within the current execution model. Any improvement would require changing the traversal logic itself, not patching the existing one.

## Step 2 - Version 1: First implementation

For implementing our idea, we need to modify the collectors’ behaviour for nested KNN search. The collectors are those components that receive candidate documents during HNSW graph traversal and decide which ones to keep, acting as the gatekeeper between raw graph exploration and the final top-k result set.

Here is a diagram with the involved classes:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/05/sease-6a049ad72a1a8.png?fit=800%2C999&ssl=1)

### DocSiblingExpansion Interface

To score the siblings of a child document found through HNSW, we need a **`findSiblingDocIds(childDocId)`** method that, given a docID, returns the list of the siblings’ docIDs.

`DiversifyingNearestChildrenKnnCollector` is the only object that has access to the document IDs (holds the **`parentBitSet`**), so it is the only place that can answer *“given a docID, what are its siblings?”*, the HNSW graph searcher only works on vector ordinals, and it does not know the parent-child structure.

The design had to respect a strict module boundary:  
the HNSW graph searcher and the **`OrdinalTranslatedKnnCollector`** live in **`core`**; the diversifying collector lives in **`join`**.   
**`lucene/core`** cannot depend on **`lucene/join`**, so the expansion contract was encoded in the **`DocSiblingExpansion`** interface. It lets the **`OrdinalTranslatedKnnCollector`** call **`findSiblingDocIds(docId)`** without knowing anything about how siblings are determined, the join-specific implementation is encapsulated entirely inside the specific **`DiversifyingNearestChildrenKnnCollector`** that implements the method.

#### DocSiblingExpansion

```
				
					public interface DocSiblingExpansion {
  int[] findSiblingDocIds(int childDocId);
  int docIdToOrdinal(int docId);
}
				
			
```

This lives in **`core`** so that **`OrdinalTranslatedKnnCollector`** (also in **`core`**) can call it without creating a circular dependency. The interface is the bridge — **`core`** calls it, **`join`** implements it.

### Implementing DocSiblingExpansion

At this point, **`DiversifyingNearestChildrenKnnCollector`** now implements **`DocSiblingExpansion`**:

* `findSiblingDocIds(childDocId)` walks the **`parentBitSet`** to find the sibling range **`[prevParent+1, parent)`**, returning all docIDs that aren’t the trigger child itself.
* `docIdToOrdinal(docId)` looks up a precomputed **`int[] docToOrd`** array to return the ordinals of a given docID.

This second method is needed because sibling docIDs must be converted back to HNSW vector ordinals before they can be scored. The array is stored in the constructor, which now takes a **`docToOrd[]`** array. **`DiversifyingNearestChildrenKnnCollectorManager`** builds and caches the **`docToOrd[]`**array per segment.

This array is populated through the **`buildDocToOrd()`** method, which iterates the **`DocIdSetIterator`** for the vector field in ascending docID order, assigning

### Scoring Siblings in the HNSW Graph

**`OrdinalTranslatedKnnCollector`** gained two new methods:

* **`isSiblingExpansionCollector()`** — checks whether the wrapped collector implements **`DocSiblingExpansion`**.
* `getSiblingOrdinals(hnswNode, visitedBitSet, siblingOrdinals)` — calls **`findSiblingDocIds`**, translates each sibling docID to its HNSW ordinal, and filters out already-visited nodes and nodes with no vector.

The core mechanism of scoring the siblings is implemented in **`AbstractHnswGraphSearcher.scoreEntryPoints()`**.  
Before collecting an entry point, if the collector is sibling-expansion-aware, siblings are fetched, marked visited, and bulk-scored in one pass:

```
				
					if (results instanceof OrdinalTranslatedKnnCollector collector) {
  if (collector.isSiblingExpansionCollector()) {
    siblingsOrd = collector.getSiblingOrdinals(ep, visited, siblingsOrd);
    for (int ord : siblingsOrd) visited.set(ord);
  }
}
results.collect(ep, score);
if (siblingsOrd.length &gt; 0) {
  siblingScores = scoreHnswNodes(results, scorer, candidates, acceptOrds, siblingsOrd, siblingScores);
}
				
			
```

The new static helper **`scoreHnswNodes()`** bulk-scores sibling nodes, adds competitive ones to the candidate queue, and collects them — continuously updating **`minCompetitiveSimilarity`** after each one, so the threshold tightens as siblings are processed.

## Step 2 - Version 1: Benchmark

A JMH benchmark **`DiversifyingChildrenKnnQueryBenchmark`** was written and run on a single-segment index with 5,000 parents, 128-dim float vectors, DOT\_PRODUCT similarity, 3 forks × 5 measurement iterations.

Three sibling-correlation scenarios were defined to model the range of real-world conditions:

* **Scenario: best**  
  Noise: 0.05 — siblings are nearly identical around a centroid  
  What it represents: Sibling expansion scores all children of a parent in a single HNSW node visit, and since siblings are nearly identical to the query direction, they all score high. The result heap fills with k high-scoring parents quickly, driving **`minCompetitiveSimilarity()`** to a high value early. HNSW prunes aggressively against that threshold and terminates with few graph nodes visited.
* **Scenario: standard**  
  Noise: 0.30 — moderately correlated  
  What it represents: This reflects a realistic use case, e.g., multiple chunks of the same document. Siblings are useful but not redundant. Expansion finds some benefit (potentially rises **`minCompetitiveSImilarity()`**) but also does meaningful extra traversal work. This is the most representative scenario for real-world performance.
* **Scenario: worst**  
  Noise: fully random  
  What it represents: Sibling expansion fires for every visited child, paying the full CPU and memory cost of fetching and scoring siblings, but gains zero recall benefit because the siblings are random. This scenario isolates and measures the pure overhead of the expansion mechanism — the upper bound on the cost you pay when correlation is absent.

### Results

#### Version 1 vs Main Baseline

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| Scenario | Siblings score | Threshold rises | HNSW early exit | Overhead (higher is slower) |
| best | High (nearly identical) | Fast | Yes | Small (~5-12%) |
| standard | Moderate | Moderate | Partial | Medium (~13-60%) |
| worst | Random/low | Barely | No | Large (~12-74%) |

Sibling expansion was slower in every single case.

For a complete list of the results, [see the PR](https://github.com/apache/lucene/pull/16034).

## Step 3 - Version 2: Code Optimisations from Review Feedback

After sharing the initial implementation, *Benjamin* *Trent* and *Alessandro Benedetti’s* reviews identified some areas for improvement.

The main optimisations applied:

1. Removed `ChildrenSiblingExpansion` interface: analysis confirmed it was entirely redundant with **`DocSiblingExpansion`**. A single interface is sufficient.
2. Removed **`numSiblingsToVisit`** variable: the visit budget enforcement through sibling counting was an unnecessary complication; all accepted siblings are always scored.
3. Scratch space reuse for siblingOrdinals: instead of allocating a `new int[]` on every expansion, the buffer is passed back as a return value and only grown when needed.

### Results

#### Version 2 vs Main Baseline

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| Scenario | Siblings score | Threshold rises | HNSW early exit | Previous overhead | **Overhead (higher is slower)** |
| best | High (nearly identical) | Fast | Yes | ~5–12% | **~3–16%** |
| standard | Moderate | Moderate | Partial | ~13–60% | **~9–51%** |
| worst | Random/low | Barely | No | ~12–74% | **~13–77%** |

Scratch space reuse produced a meaningful improvement in the realistic standard scenario at high  
children-per-parent from ~60% overhead down to ~51%. The best-case floor dropped to ~3%. The worst-case ceiling moved from ~74% to ~77%, likely within benchmark variance.

For a complete list of the results, [see the PR](https://github.com/apache/lucene/pull/16034).

However, these are the trends that held across both versions:

* Overhead scales up with more children per parent.
 * Overhead scales up with larger k.
 * Highly correlated siblings partially mitigate overhead because HNSW terminates earlier, thanks to a quick rise of the **`minCompetitiveSimilarity()`**.
 * Random siblings pay the `bulkScore` cost unconditionally, yield the visited-marking benefit unconditionally, and provide a competitive score update only by chance, making expansion low-value.

## Takeaways

**The feature trades latency for recall correctness.** **Parents in the result set are evaluated using their best-known child** rather than whichever child graph traversal happened to reach first. That is a genuine **quality improvement**. But it comes at a **consistent and sometimes substantial latency cost.**

The central finding is that:  
**Sibling expansion is a recall and ranking quality optimisation, not a performance optimisation.**   
The latency overhead is consistent, measurable, and scales with workload size. It cannot be assumed away.

Even if the feature implementation itself is not worth the latency trade-off, one thing worth contributing to, and something we plan to do, is adding the `DiversifyingChildrenKnnQueryBenchmark` benchmark to the project. The benchmark is a standalone, reusable tool covering three sibling-correlation scenarios across a realistic parameter grid. It will be valuable for measuring the impact of future KNN optimisations regardless of whether this feature is merged.

If you have any additional considerations you would like to share with us, we would be happy to discuss!

When using Lucene’s parent-child block-join mode, you are dealing with a “one-to-many relationship”. You have a single document (parent) owning multiple vector embeddings (children).  
To search these, Lucene uses the `DiversifyingChildrenFloatKnnVectorQuery`. Its job is simple: find the k nearest parent documents by scoring children through HNSW graph traversal, returning at most one child — the best-scoring — per parent.

**The reason why we started this in-depth code analysis and further implementation was to make the entire process faster.**

## What do you need to know before

### Doc IDS vs Document Vector Ordinals

**DocIDs**

A docID is Lucene’s internal identifier for a document within a segment. Every document — whether a parent or a child — gets a sequential integer docID assigned when it is indexed. The block-join layout stores them consecutively:

```
docId 0 → child1
docId 1 → child2
docId 2 → child3
docId 3 → parent1
docId 4 → child1
docId 5 → child2
docId 6 → parent2
```

**Document Vector Ordinals**

An ordinal is a separate sequential integer assigned only to documents that have a vector for a given field. Not every document has a vector — parents never do, and in sparse indexing, some children may not either. So ordinals form a compact, gap-free sequence over just the vector-bearing documents:

```
docId 0 (child1, has vector) → ordinal 0
docId 1 (child2, has vector) → ordinal 1
docId 2 (child3, has vector) → ordinal 2
docId 3 (parent1, no vector) → no ordinal
docId 4 (child1, has vector) → ordinal 3
docId 5 (child2, has vector) → ordinal 4
docId 6 (parent2, no vector) → no ordinal
```

**Why both exist**

The HNSW graph uses ordinals as node identifiers — graph edges connect ordinals, not docIDs. When the graph says “node 3 is a neighbor of node 1”, it means the documents at ordinals 3 and 1, which are docIds 4 and 1, respectively.

Everything outside the HNSW graph — the parentBitSet, the collector, and query results — operates on docIDs. `OrdinalTranslatedKnnCollector` sits at the boundary and translates in one direction (from ordinal to docID); `docIdToOrdinal` translates in the other (docIDs to ordinal).  
  
Ale: what’s a ‘`OrdinalTranslatedKnnCollector`‘ ? add references

### BitSet

The `parentBitSet` is not a list of all documents — it’s a bit array over the segment’s docID space, where only parent positions are set to 1, and all child positions are 0. The Lucene block-join layout stores each block as consecutive docIDs with the parent always last:

```
docId 0 → child1 (bit = 0)
docId 1 → child2 (bit = 0)
docId 2 → child3 (bit = 0)
docId 3 → parent1 (bit = 1) ← set
docId 4 → child1 (bit = 0)
docId 5 → child2 (bit = 0)
docId 6 → parent2 (bit = 1) ← set
```

This kind of data structure allows for quicker access to its elements. There is no hash map lookup, no stored parent pointer per child document, and no auxiliary structure to maintain.

## The Idea

After a discussion with other Lucene committers, we observed that:

* When the typical number of children per parent is small, eagerly translating each visited child back to its parent ordinal is surprisingly expensive. In many cases, it appears more efficient to post-process or “join back” to parent blocks rather than continuously resolving parent ordinals during traversal.
* The heap structure and parent/child translation logic show up significantly in benchmarks. Which is somewhat unexpected.
* When the search encounters a nearest child node during HNSW traversal, instead of treating it as an isolated signal, we could immediately gather and score *all siblings of that child’s parent* (i.e., all children under the same parent ordinal), under the assumption that they are likely to be similarly competitive. This “eager sibling expansion” turns a single graph hit into a localized, dense evaluation over the parent’s full child set.

Immediately bulk-scoring all of that parent’s unvisited siblings, rather than waiting for graph edges to eventually reach them, should:

1. Introduces a dynamic exploration strategy where the algorithm can evaluate minimum, maximum, and average sibling scores per parent, at the cost of extra local scoring but potentially reduced global traversal.
2. Accelerate convergence in best-first search scenarios by more quickly identifying strong parent candidates and raising the pruning threshold earlier.
3. Improve ranking quality; the heap always holds the best-known child per parent, not just the first encountered.

## Step 1 — Codebase audit

Before writing any code, a thorough review of the existing `DiversifyingChildrenFloatKnnVectorQuery` stack was carried out.

The conclusion: no bugs, no obvious inefficiencies within the current execution model. Any improvement would require changing the traversal logic itself, not patching the existing one.

## Step 2 — Version 1: First implementation

For implementing our idea, we need to modify the collectors’ behaviour for nested KNN search. The collectors are those components that receive candidate documents during HNSW graph traversal and decide which ones to keep, acting as the gatekeeper between raw graph exploration and the final top-k result set.

Here is a diagram with the involved classes:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/05/sease-6a049ad72a1a8.png?w=800&ssl=1 "image")

### **DocSiblingExpansion Interface**

To score the siblings of a child document found through HNSW, we need a `findSiblingDocIds(childDocId)` method that, given a docID, returns the list of the siblings’ docIDs.

`DiversifyingNearestChildrenKnnCollector` is the only object that has access to the document IDs (holds the `parentBitSet`), so it is the only place that can answer *“given a docID, what are its siblings?”*, the HNSW graph searcher only works on vector ordinals, and it does not know the parent-child structure.

The design had to respect a strict module boundary:  
the HNSW graph searcher and the `OrdinalTranslatedKnnCollector` live in `core`; the diversifying collector lives in `join`.   
`lucene/core` cannot depend on `lucene/join`, so the expansion contract was encoded in the `DocSiblingExpansion` interface. It lets the `OrdinalTranslatedKnnCollector` call `findSiblingDocIds(docId)` without knowing anything about how siblings are determined, the join-specific implementation is encapsulated entirely inside the specific `DiversifyingNearestChildrenKnnCollector` that implements the method.

**DocSiblingExpansion**:

```
public interface DocSiblingExpansion {
  int[] findSiblingDocIds(int childDocId);
  int docIdToOrdinal(int docId);
}
```

This lives in `core` so that `OrdinalTranslatedKnnCollector` (also in `core`) can call it without creating a circular dependency. The interface is the bridge — `core` calls it, `join` implements it.

### Implementing DocSiblingExpansion

At this point, `DiversifyingNearestChildrenKnnCollector` now implements `DocSiblingExpansion`:

* `findSiblingDocIds(childDocId)` walks the `parentBitSet` to find the sibling range `[prevParent+1, parent)`, returning all docIDs that aren’t the trigger child itself.
* `docIdToOrdinal(docId)` looks up a precomputed `int[] docToOrd` array to return the ordinals of a given docID.

This second method is needed because sibling docIDs must be converted back to HNSW vector ordinals before they can be scored. The array is stored in the constructor, which now takes a `docToOrd[]` array. `DiversifyingNearestChildrenKnnCollectorManager` builds and caches the `docToOrd[]`array per segment.

This array is populated through the `buildDocToOrd()` method, which iterates the `DocIdSetIterator` for the vector field in ascending docID order, assigning  
ordinals sequentially — exactly inverting the `ordToDoc` mapping stored on disk at index time.

### Scoring Siblings in the HNSW Graph

`OrdinalTranslatedKnnCollector` gained two new methods:

* `isSiblingExpansionCollector()` — checks whether the wrapped collector implements `DocSiblingExpansion`.
* `getSiblingOrdinals(hnswNode, visitedBitSet, siblingOrdinals)` — calls `findSiblingDocIds`, translates each sibling docID to its HNSW ordinal, and filters out already-visited nodes and nodes with no vector.

The core mechanism of scoring the siblings is implemented in `AbstractHnswGraphSearcher.scoreEntryPoints()`.  
Before collecting an entry point, if the collector is sibling-expansion-aware, siblings are fetched, marked visited, and bulk-scored in one pass:

```
if (results instanceof OrdinalTranslatedKnnCollector collector) {
  if (collector.isSiblingExpansionCollector()) {
    siblingsOrd = collector.getSiblingOrdinals(ep, visited, siblingsOrd);
    for (int ord : siblingsOrd) visited.set(ord);
  }
}
results.collect(ep, score);
if (siblingsOrd.length > 0) {
  siblingScores = scoreHnswNodes(results, scorer, candidates, acceptOrds, siblingsOrd, siblingScores);
}
```

The new static helper `scoreHnswNodes()` bulk-scores sibling nodes, adds competitive ones to the candidate queue, and collects them — continuously updating `minCompetitiveSimilarity` after each one, so the threshold tightens as siblings are processed.

## Step 2 — Version 1: Benchmark

A JMH benchmark `DiversifyingChildrenKnnQueryBenchmark` was written and run on a single-segment index with 5,000 parents, 128-dim float vectors, DOT\_PRODUCT similarity, 3 forks × 5 measurement iterations.

Three sibling-correlation scenarios were defined to model the range of real-world conditions:

* **Scenario: best**  
  Noise: 0.05 — siblings are nearly identical around a centroid  
  What it represents: Sibling expansion scores all children of a parent in a single HNSW node visit, and since siblings are nearly identical to the query direction, they all score high. The result heap fills with k high-scoring parents quickly, driving `minCompetitiveSimilarity()` to a high value early. HNSW prunes aggressively against that threshold and terminates with few graph nodes visited.
* **Scenario: standard**  
  Noise: 0.30 — moderately correlated  
  What it represents: This reflects a realistic use case, e.g., multiple chunks of the same document. Siblings are useful but not redundant. Expansion finds some benefit (potentially rises `minCompetitiveSImilarity()`) but also does meaningful extra traversal work. This is the most representative scenario for real-world performance.
* **Scenario: worst**  
  Noise: fully random  
  What it represents: Sibling expansion fires for every visited child, paying the full CPU and memory cost of fetching and scoring siblings, but gains zero recall benefit because the siblings are random. This scenario isolates and measures the pure overhead of the expansion mechanism — the upper bound on the cost you pay when correlation is absent.

### Results

Version 1 vs Main Baseline

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| Scenario | Siblings score | Threshold rises | HNSW early exit | Overhead (higher is slower) |
| best | High (nearly identical) | Fast | Yes | Small (~5-12%) |
| standard | Moderate | Moderate | Partial | Medium (~13-60%) |
| worst | Random/low | Barely | No | Large (~12-74%) |

Sibling expansion was slower in every single case.

For a complete list of the results, see the PR: <https://github.com/apache/lucene/pull/16034>

## Step 3 — Version 2: Code Optimizations from Review Feedback

After sharing the initial implementation, *Benjamin* *Trent* and *Alessandro Benedetti’s* reviews identified some areas for improvement.

The main optimizations applied:

1. Removed `ChildrenSiblingExpansion` interface: analysis confirmed it was entirely redundant with `DocSiblingExpansion`. A single interface is sufficient.
2. Removed `numSiblingsToVisit` variable: the visit budget enforcement through sibling counting was an unnecessary complication; all accepted siblings are always scored.
3. Scratch space reuse for siblingOrdinals: instead of allocating a `new int[]` on every expansion, the buffer is passed back as a return value and only grown when needed.

### Results

Version 2 vs Main Baseline

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| Scenario | Siblings score | Threshold rises | HNSW early exit | Previous overhead | **Overhead (higher is slower)** |
| best | High (nearly identical) | Fast | Yes | ~5–12% | **~3–16%** |
| standard | Moderate | Moderate | Partial | ~13–60% | **~9–51%** |
| worst | Random/low | Barely | No | ~12–74% | **~13–77%** |

Scratch space reuse produced a meaningful improvement in the realistic standard scenario at high  
children-per-parent from ~60% overhead down to ~51%. The best-case floor dropped to ~3%. The worst-case ceiling moved from ~74% to ~77%, likely within benchmark variance.

For a complete list of the results, see the PR: <https://github.com/apache/lucene/pull/16034>

However, these are the trends that held across both versions:

* Overhead scales up with more children per parent.
* Overhead scales up with larger k.
* Highly correlated siblings partially mitigate overhead because HNSW terminates earlier, thanks to a quick rise of the `minCompetitiveSimilarity()`.
* Random siblings pay the `bulkScore` cost unconditionally, yield the visited-marking benefit unconditionally, and provide a competitive score update only by chance, making expansion low-value.

## Takeaways

**The feature trades latency for recall correctness.** **Parents in the result set are evaluated using their  
best-known child** rather than whichever child graph traversal happened to reach first. That is a genuine  
**quality improvement**. But it comes at a **consistent and sometimes substantial latency cost.**

The central finding is that:  
**Sibling expansion is a recall and ranking quality optimization, not a performance optimization.**   
The latency overhead is consistent, measurable, and scales with workload size. It cannot be assumed away.

Even if the feature implementation itself is not worth the latency trade-off, one thing worth contributing to, and something we plan to do, is adding the `DiversifyingChildrenKnnQueryBenchmark` benchmark to the project. The benchmark is a standalone, reusable tool covering three sibling-correlation scenarios across a realistic parameter grid. It will be valuable for measuring the impact of future KNN optimisations regardless of whether this feature is merged.

---

If you have any additional considerations you would like to share with us, we would be happy to discuss!

## Need Help With This Topic?​​

If you’re struggling with nested vectors search, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimise your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with nested vectors search, don't worry - we're here to help!
Our team offers expert services and training to help you optimise your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)