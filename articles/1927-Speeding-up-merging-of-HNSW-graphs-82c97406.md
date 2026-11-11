---
title: 'Speeding up merging of HNSW graphs'
company: Elastic
tag: 索引构建
date: 2025-04-07
url: https://www.elastic.co/search-labs/blog/hnsw-graphs-speed-up-merging
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Speeding up merging of HNSW graphs

Explore the work we’ve been doing to reduce the overhead of building multiple HNSW graphs, particularly reducing the cost of merging graphs.

April 07, 2025

[Thomas Veasey](/search-labs/author/thomas-veasey)[Mayya Sharipova](/search-labs/author/mayya-sharipova)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)

Jump to

Share

In the past, [we discussed](https://www.elastic.co/search-labs/blog/multi-graph-vector-search) some of the challenges of having to search multiple [HNSW graphs](https://www.elastic.co/search-labs/blog/hnsw-graph) and how we were able to mitigate them. At that time we alluded to some further improvements we had planned. This post is the culmination of that work.

You might ask, why use multiple graphs at all? This is a side effect of an architectural choice in Lucene: immutable segments. As with most architectural choices there are pros and cons. For example, we’ve recently GA’d Serverless Elasticsearch. In this context, we’ve gained very significant benefits from immutable segments including efficient index replication and the ability to decouple index and query compute and autoscale them independently. For vector quantization, segment merges give us the opportunity to update parameters to adapt them to data characteristics. Along these lines, we think there are other advantages that having opportunities to measure data characteristics and revisit indexing choices affords.

In this post we will discuss the work we’ve been doing to significantly reduce the overhead of building multiple HNSW graphs and in particular to reduce the cost of merging graphs.

### Background

In order to maintain a manageable number of segments Lucene periodically checks to see if it should merge segments. This amounts to checking if the current segment count exceeds a target segment count, which is determined by the base segment size and the merge policy. If the count is exceeded, Lucene merges groups of segments while the constraint is violated. This process has been described in detail [elsewhere](https://blog.mikemccandless.com/2011/02/visualizing-lucenes-segment-merges.html).

Lucene elects to merge similar sized segments because this achieves logarithmic growth in the write amplification. In the case of a vector index, write amplification is the number of times a vector will be inserted into a graph. Lucene will try to merge segments in groups of approximately 10. Consequently, vectors are inserted into a graph roughly 1+910log⁡10(nn0)1+\frac{9}{10}\log\_{10}\left(\frac{n}{n\_0}\right)1+109​log10​(n0​n​)times, where nnn is the index vector count and n0n\_0n0​ is the expected base segment vector count. Because of the logarithmic growth, write amplification is single digits even for huge indices. However, the total time spent merging graphs is linearly proportional to the write amplification.

When merging HNSW graphs we already make a small optimization: retaining the graph for the largest segment and inserting vectors from the other segments into it. This is the reason for the 9/10 factor above. Below we show how we are able to do significantly better by using information from all the graphs we are merging.

### HNSW Graph merging

Previously we retained the largest graph and inserted vectors from the others ignoring the graphs that contain them. The key insight we make use of below is that each HNSW graph we discard contains important proximity information about the vectors it contains. We would like to use this information to accelerate inserting, at least some, of the vectors.

We focus on the problem of inserting a smaller graph Gs=(Vs,Es)G\_s=(V\_s,E\_s)Gs​=(Vs​,Es​) into a larger graph Gl=(Vl,El)G\_l=(V\_l,E\_l)Gl​=(Vl​,El​), since this is an atomic operation we can use to build any merge policy.

The strategy is to find a subset of vertices of J⊂VsJ\subset V\_sJ⊂Vs​ to insert into the large graph. We then use the connectivity of these vertices in the small graph to accelerate inserting the remaining vertices Vs∖JV\_s \setminus JVs​∖J. In the following, we use Ns(u)N\_s(u)Ns​(u) and Nl(u)N\_l(u)Nl​(u) to denote the neighbors of a vertex uuu in the small and large graph, respectively. Schematically the process is as follows.

`MERGE-HNSW`

`Inputs` GsG\_sGs​ `and` GlG\_lGl​

`1`    \;\;`Find` J⊂VsJ\subset V\_sJ⊂Vs​ `to insert into` GlG\_lGl​ `using COMPUTE-JOIN-SET`
`2`    \;\;`Insert each vertex` u∈Ju\in Ju∈J `into` GlG\_lGl​
`3`    \;\;`for` u∈Vs∖Ju\in V\_s \setminus Ju∈Vs​∖J `do`
`4`        Ju←J∩Ns(u)\;\;\;\;J\_u\leftarrow J\cap N\_s(u)Ju​←J∩Ns​(u)
`5`        Eu←∪v∈JuNl(u)\;\;\;\;E\_u\leftarrow \cup\_{v\in J\_u} N\_l(u)Eu​←∪v∈Ju​​Nl​(u)
`6`        W← \;\;\;\;W\leftarrow\,W←`FAST-SEARCH-LAYER`(Ju,Eu)(J\_u, E\_u)(Ju​,Eu​)
`7`        neighbors← \;\;\;\;neighbors \leftarrow\,neighbors←`SELECT-NEIGHBORS-HEURISTIC`(u,W)(u, W)(u,W)
`8`        J←J∪{u}\;\;\;\;J\leftarrow J \cup \{u\}J←J∪{u}

We compute the set JJJ using a procedure we discuss below (line 1). Then we insert every vertex in JJJ into the large graph using the standard HNSW insertion procedure (line 2). For each vertex we haven’t inserted we find its neighbors that we have inserted and their neighbors in the large graph (lines 4 and 5). We use a `FAST-SEARCH-LAYER` procedure seeded with this set (line 6) to find the candidates for the `SELECT-NEIGHBORS-HEURISTIC` from the HNSW [paper](https://arxiv.org/pdf/1603.09320) (line 7). In effect, we’re replacing `SEARCH-LAYER` to find the candidate set in the `INSERT` method (Algorithm 1 from the paper), which is otherwise unchanged. Finally, we add the vertex we just inserted into JJJ (line 8).

It's clear that for this to work every vertex in Vs∖JV\_s \setminus JVs​∖J must have at least one neighbor in JJJ. In fact, we require that for every vertex in u∈Vs∖Ju\in V\_s \setminus Ju∈Vs​∖J that ∣J∩Ns(u)∣≥ku|J\cap N\_s(u) |\geq k\_u∣J∩Ns​(u)∣≥ku​ for some ku<Mk\_u<Mku​<M, the maximum layer connectivity. We observe that in real HNSW graphs we see quite a spread of vertex degrees. The figure below shows a typical cumulative density function of vertex degree for the bottom layer of an Lucene HNSW graph.

![HNSW graph: Example vertex degree distribution](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc815e1a9c3bb0d06/6a17e178ec0f89308a5a6564/44f001b3a1bc6627e172fed5c52a02cfdcb4cd66-1324x898.png)

Example vertex degree distribution

We explored using a fixed value for kuk\_uku​ as well as making it a function of the vertex degree. This second choice leads to larger speedups with minimal impact on graph quality so went with the following

ku=max⁡(2,14∣Ns(u)∣)k\_u=\max\left(2,\frac{1}{4}|N\_s(u)|\right)ku​=max(2,41​∣Ns​(u)∣)

Note that ∣Ns(u)|N\_s(u)∣Ns​(u)| is equal to the degree of the vertex uuu in the small graph by definition. Having a lower limit of two means that we will insert every vertex whose degree is less than two.

A simple counting argument suggests that if we choose JJJ carefully we need only insert around 15∣Vs∣\frac{1}{5}|V\_s|51​∣Vs​∣ into GlG\_lGl​ directly. Specifically, we color an edge of the graph if we insert exactly one of its end vertices into JJJ. Then we know that for every vertex in Vs∖JV\_s \setminus JVs​∖J to have at least kuk\_uku​ neighbors in JJJ we need to color at least ∑u∈Vs∖Jku\sum\_{u\in V\_s\setminus J} k\_u∑u∈Vs​∖J​ku​ edges. Furthermore, we expect that

∑u∈Vs∖Jku≈(∣Vs∣−∣J∣)14EU[∣Ns(U)∣]\sum\_{u\in V\_s\setminus J} k\_u\approx \left(|V\_s|-|J|\right)\frac{1}{4}\mathbb{E}\_U\left[|N\_s(U)|\right]u∈Vs​∖J∑​ku​≈(∣Vs​∣−∣J∣)41​EU​[∣Ns​(U)∣]

Here, EU[Ns(U)∣]\mathbb{E}\_U\left[N\_s(U)|\right]EU​[Ns​(U)∣] is the average vertex degree in the small graph. For each vertex u∈Ju\in Ju∈J we color at most ∣Ns(u)∣|N\_s(u)|∣Ns​(u)∣ edges. Therefore, the total number of edges we expect to color is at most ∣J∣ EU[∣Ns(U)∣]|J|\, \mathbb{E}\_U\left[|N\_s(U)|\right]∣J∣EU​[∣Ns​(U)∣]. We hope by choosing JJJ carefully we will color close to this number of edges and so in order to cover all the vertices ∣J∣|J|∣J∣ needs to satisfy

∣J∣ EU[∣Ns(U)∣]=(∣Vs∣−∣J∣)14EU[∣Ns(U)∣]|J|\, \mathbb{E}\_U\left[|N\_s(U)|\right] =\left(|V\_s|-|J|\right)\frac{1}{4}\mathbb{E}\_U\left[|N\_s(U)|\right]∣J∣EU​[∣Ns​(U)∣]=(∣Vs​∣−∣J∣)41​EU​[∣Ns​(U)∣]

This implies that ∣J∣=14(∣Vs∣−∣J∣)=4514∣Vs∣=15∣Vs∣|J|=\frac{1}{4}(|V\_s|-|J|)=\frac{4}{5}\frac{1}{4}|V\_s|=\frac{1}{5}|V\_s|∣J∣=41​(∣Vs​∣−∣J∣)=54​41​∣Vs​∣=51​∣Vs​∣.

Providing `SEARCH-LAYER` dominates the runtime this suggests we could achieve up to a 5×5\times5× speed up in merge time. Given the logarithmic growth of the write amplification, this means even for very large indices we would typically only double the build time compared to building one graph.

The risk in this strategy is that we damage the graph quality. We initially tried with a no-op `FAST-SEARCH-LAYER`. We found this degrades graph quality to the extent that recall as a function of latency was impacted, particularly when merging down to a single segment. We then explored various alternatives using a limited search of the graph. In the end, the most effective choice was the simplest. Use `SEARCH-LAYER` but with a low `ef_construction`. With this parameterisation we were able to achieve excellent quality graphs and still decrease the merge time by a little over 30% on average.

### Computing the join set

Finding a good join set can be formulated as an HNSW graph covering problem. A greedy heuristic is a simple and effective heuristic for approximating optimal graph covers. The approach we take picks vertices one at a time to add to JJJ in decreasing gain order. The gain is defined as follows:

Gain(v)=max⁡(kv−c(v),0)+∑u∈Ns(v)∖J1{c(u)<ku}Gain(v)=\max(k\_v-c(v),0)+\sum\_{u\in N\_s(v)\setminus J} 1\left\{c(u)<k\_u\right\}Gain(v)=max(kv​−c(v),0)+u∈Ns​(v)∖J∑​1{c(u)<ku​}

Here, c(v)c(v)c(v) denotes the count of neighbors of a vector vvv in JJJ and 1{⋅}1\{\cdot\}1{⋅} is the indicator function. The gain includes the change in the count of the vertex we added to JJJ, i.e. max⁡(kv−c(v),0)\max(k\_v-c(v),0)max(kv​−c(v),0), since we get closer to our goal by adding a less covered vertex. The gain calculation is illustrated in the figure below for the central orange vertex.

![Vertex gain to add to join set J in HNSW graph](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7a353d56fa09af5f/6a17e17a2f4a5c33f7fa8825/fe11cd55a7d94d9e0b0f4d47ea309a99075c355d-540x474.png)

Vertex gain to add to join set J

We maintain the following state for each vertex vvv:

1. Whether it is stale,
2. Its gain Gain(v)Gain(v)Gain(v),
3. The count of adjacent vertices in JJJ denoted c(v)c(v)c(v),
4. A random number in the range [0,1] that is used for tie breaking.

The pseudo code for computing the join set is as follows.

`COMPUTE-JOIN-SET`

`Inputs` GsG\_sGs​

`1`    C←∅\;\;C\leftarrow\emptysetC←∅
`2`    Gainexit←0\;\;Gain\_{exit}\leftarrow 0Gainexit​←0
`3`    \;\;`for` u∈Gsu\in G\_su∈Gs​ `do`
`4`        C←C∪{(false,ku+deg(u),0,rand in [0,1])}\;\;\;\;C\leftarrow C \cup \{(\text{false}, k\_u+deg(u), 0, \text{rand in }[0,1])\}C←C∪{(false,ku​+deg(u),0,rand in [0,1])}
`5`        Gainexit←Gainexit+ku\;\;\;\;Gain\_{exit}\leftarrow Gain\_{exit}+k\_uGainexit​←Gainexit​+ku​
`6`    Gaintot←0\;\;Gain\_{tot}\leftarrow 0Gaintot​←0
`7`    \;\;`while` Gaintot<GainexitGain\_{tot}<Gain\_{exit}Gaintot​<Gainexit​ `do
8`        v∗← \;\;\;\;v^\*\leftarrow\,v∗← `maximum gain vertex in` CCC
`9`        \;\;\;\;`Remove the state for` v∗v^\*v∗ `from` CCC
`10`      \;\;\;`if` v∗v^\*v∗ `is not stale then`
`11`          J←J∪{v∗}\;\;\;\;\;J\leftarrow J\cup\{v^\*\}J←J∪{v∗}
`12`          Gaintot←Gaintot+Gain(v∗)\;\;\;\;\;Gain\_{tot}\leftarrow Gain\_{tot}+Gain(v^\*)Gaintot​←Gaintot​+Gain(v∗)
`13`          \;\;\;\;\;`for` u∈Ns(v∗)u \in N\_s(v^\*)u∈Ns​(v∗) `do`
`14`              \;\;\;\;\;\;\;`mark` uuu `as stale if` c(v∗)<kv∗c(v^\*)<k\_{v^\*}c(v∗)<kv∗​
`15`              \;\;\;\;\;\;\;`mark neighbors of` uuu `stale if` c(u)=ku−1c(u)=k\_u-1c(u)=ku​−1`16`              c(u)←c(u)+1\;\;\;\;\;\;\;c(u)\leftarrow c(u)+1c(u)←c(u)+1`17`      \;\;\;`else
18`          Gain(v∗)←max⁡(kv−c(v∗),0)+∑u∈Ns(v∗)∖J1{c(u)<ku}\;\;\;\;\;Gain(v^\*)\leftarrow \max(k\_v-c(v^\*),0)+\sum\_{u\in N\_s(v^\*)\setminus J} 1\left\{c(u)<k\_u\right\}Gain(v∗)←max(kv​−c(v∗),0)+∑u∈Ns​(v∗)∖J​1{c(u)<ku​}`19`          \;\;\;\;\;`if` Gain(v∗)>0Gain(v^\*)>0Gain(v∗)>0 `then
20`              C←C∪{(false,Gain(v∗),c(v∗),copy rand)}\;\;\;\;\;\;\;C\leftarrow C \cup \{(\text{false},Gain(v^\*),c(v^\*),\text{copy rand})\}C←C∪{(false,Gain(v∗),c(v∗),copy rand)}`21`    \;\;`return` JJJ

We first initialize the state in lines 1-5.

In each iteration of the main loop we initially extract the maximum gain vertex (line 8), breaking ties at random. Before making any change, we need to check if the vertex’s gain is stale. In particular, each time we add a vertex into JJJ we affect the gain of other vertices:

1. Since all its neighbors have an additional neighbor in JJJ their gains can change (line 14)
2. If any of its neighbors are now fully covered all their neighbors’ gains can change (lines 14-16)

We recompute gains in a lazy fashion, so we only recompute the gain of a vertex if we want to insert it into JJJ (lines 18-20). Since gains only ever decrease we can never miss a vertex we should insert.

Note that we simply need to keep track of the total gain of vertices we’ve added to JJJ to determine when to exit. Furthermore, whilst Gaintot<GainexitGain\_{tot}<Gain\_{exit}Gaintot​<Gainexit​ at least one vertex will have non-zero gain so we always make progress.

### Results

We ran experiments on four datasets that together cover our three supported distance metrics (Euclidean, cosine and inner product):

1. quora-E5-small: 522931 documents, 384 dimensions and uses cosine similarity,
2. cohere-wikipedia-v2: 1M documents, 768 dimensions and uses cosine similarity,
3. gist: 1M documents, 960 dimensions and uses Euclidean distance, and
4. cohere-wikipedia-v3: 1M documents, 1024 dimensions and uses maximum inner product.

For each dataset we evaluate two quantization levels:

1. int8 – which uses a 1-byte integer per dimension and
2. BBQ – which uses a single bit per dimension.

Finally, for each experiment we evaluated search quality at two retrieval depths and examine after building the index and then after force merging to a single segment.

In summary, we achieve consistent substantial speedups in indexing and merging while maintaining graph quality and so search performance in all cases.

#### Experiment 1: int8 quantization

The average speedups from the baseline to the candidate, the proposed changes, are:

Index Time Speedup: **1.28**×\times×

Force Merge Speedup: **1.72**×\times×

This corresponds to the following breakdown in run times

![Index and merge times for the baseline and candidate merge strategies](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt8422be122ef1a9c9/6a17e17bbe6086522e00467d/5f9f6d487b4c74c4998aa47465912c1a9743e928-734x479.png)

Index and merge times for the baseline and candidate merge strategies

For completeness the exact times are

|  | Index |  | Merge |  |
| --- | --- | --- | --- | --- |
| Dataset | baseline | candidate | build | candidate |
| quora-E5-small | 112.41s | 81.55s | 113.81s | 70.87s |
| wiki-cohere-v2 | 158.1s | 122.95s | 425.20s | 239.28s |
| gist | 141.82s | 119.26s | 536.07s | 279.05s |
| wiki-cohere-v3 | 211.86s | 168.22s | 654.97s | 414.12s |

Below we show the recall vs latency graphs that compare the candidate (dashed lines) to the baseline at two retrieval depths: recall@10 and recall@100 for indices with multiple segments (the final result of our default merge strategy after indexing all vectors) and after force merging to a single segment. A curve that is higher and further to the left is better, which means higher recall at lower latency.

As you can see, for multiple segment indices the candidate is better for the Cohere v3 dataset and slightly worse, but almost comparable, for all other datasets. After merging to a single segment recall curves are almost identical for all cases.

![Recall @10 and @100 vs latency after building the index](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf674622469bf6a90/6a17e17dfbc5f874a84919c9/9195297f19f90b172d832ba56bdada7b0d8a768b-985x392.png)

Recall @10 and @100 vs latency after building the index

![Recall @10 and @100 vs latency after merging to a single segment](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltde89f7e94ac823f4/6a17e17fe9ea876429a9c507/c866f32d579ae2b841e92ca733dd29c0e214ac6b-986x386.png)

Recall @10 and @100 vs latency after merging to a single segment

#### Experiment 2: BBQ quantization

The average speedups from the baseline to the candidate are:

Index Time Speedup: **1.33**×\times×

Force Merge Speedup: **1.34**×\times×

This corresponds to the following breakdown in run times

![Index and merge time for the baseline and candidate merge strategies](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt5b0eb305222fa5c2/6a17e18125daab514f08a18c/11be0cf6b63480dc703409329357ea4847b55051-740x415.png)

Index and merge time for the baseline and candidate merge strategies

For completeness the exact times are

|  | Index |  | Merge |  |
| --- | --- | --- | --- | --- |
| Dataset | baseline | candidate | build | candidate |
| quora-E5-small | 70.71s | 58.25s | 59.38s | 40.15s |
| wiki-cohere-v2 | 203.08s | 142.27s | 107.27s | 85.68s |
| gist | 110.35s | 105.52s | 323.66s | 202.2s |
| wiki-cohere-v3 | 313.43s | 190.63s | 165.98s | 159.95s |

For multiple segment indices the candidate is better for almost all datasets, except cohere v2 where the baseline is slightly better. For the single segment indices recall curves are almost identical for all cases.

![Recall @10 and @100 vs latency after building the index](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb12174abeadbcdd1/6a17e1822f4a5c4cc2fa8829/7da1be27bab5a7f5f9c9a1882ea35761a4a0ba5c-973x383.png)

Recall @10 and @100 vs latency after building the index

![Recall @10 and @100 vs latency having merged to a single segment](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf1b88d4f7fec9905/6a17e184414c64a8de9450b4/a26af30a56c55a12addee7e4fb7e8f606f366668-979x386.png)

Recall @10 and @100 vs latency having merged to a single segment

### Conclusion

The algorithm discussed in this blog will be available in the upcoming Lucene 10.2, and in the Elasticsearch release that is based on it. Users will be able to take advantage of the improved merge performance and reduced index build time in these new versions. This change is a part of our continuous effort to make Lucene and Elasticsearch fast and efficient for vector and hybrid search.

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