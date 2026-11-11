---
title: 'Scalar quantization optimized for vector databases'
company: Elastic
tag: 索引构建
date: 2024-04-25
url: https://www.elastic.co/search-labs/blog/vector-db-optimized-scalar-quantization
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Scalar quantization optimized for vector databases

Optimizing scalar quantization for the vector database use case allows us to achieve significantly better performance for the same retrieval quality at high compression ratios.

April 25, 2024

[Thomas Veasey](/search-labs/author/thomas-veasey)[Benjamin Trent](/search-labs/author/benjamin-trent)

[ML Research](/search-labs/blog/category/ml-research)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

## Introduction

We talked [before](https://www.elastic.co/search-labs/blog/scalar-quantization-in-lucene) about the scalar quantization work we've been doing in Lucene. In this two part blog we will dig a little deeper into how we're optimizing scalar quantization for the vector database use case. This has allowed us to unlock very nice performance gains for int4 quantization in Lucene, as we'll discuss in the second part. In the first part we're going to dive into the details of how we did this. Feel free to [jump ahead](https://www.elastic.co/search-labs/blog/int4-scalar-quantization-in-lucene) to learn about what this will actually mean for you. Otherwise, buckle your seatbelts, because Kansas is going bye-bye!

## Scalar quantization recap

First of all, a quick refresher on scalar quantization.

Scalar quantization was introduced as a mechanism for accelerating inference. To date it has been mainly studied in that setting. For that reason, the main considerations were the accuracy of the model output and the performance gains that come from reduced memory pressure and accelerated matrix multiplication (GEMM) operations. Vector retrieval has some slightly different characteristics which we can exploit to improve quantization accuracy for a given compression ratio.

The basic idea of scalar quantization is to truncate and scale each floating point component of a vector (or tensor) so it can be represented by an integer. Formally, if you use bbb bits to represent a vector component xxx as an integer in the interval [0,2b−1][0,2^b-1][0,2b−1] you transform it as follows

x↦⌊(2b−1)clamp(x,a,b)b−a⌉x \mapsto \left\lfloor \frac{(2^b-1)\text{clamp}(x,a,b)}{b-a} \right\rceil
x↦⌊b−a(2b−1)clamp(x,a,b)​⌉

where clamp(⋅,a,b)\text{clamp}(\cdot,a,b)clamp(⋅,a,b) denotes min⁡(max⁡(⋅,a),b)\min(\max(\cdot, a),b)min(max(⋅,a),b) and ⌊⋅⌉\lfloor\cdot\rceil⌊⋅⌉ denotes round to the nearest integer. People typically choose aaa and bbb based on percentiles of the distribution. We will discuss a better approach later.

If you use int4 or 4 bit quantization then each component is some integer in the interval [0,15], that is each component takes one of only 16 distinct values!

## Novelties introduced to scalar quantization

In this part, we are going to describe in detail two specific novelties we have introduced:

1. A first order correction to the dot product when it is computed using integer values.
2. An optimization procedure for the free parameters used to compute the quantized vector.

Just to pause on point 1 for a second. What we will show is that we can continue to compute the dot product directly using [integer arithmetic](https://www.elastic.co/search-labs/blog/scalar-quantization-101). At the same time, we can compute an additive correction that allows us to improve its accuracy. So we can improve retrieval quality without losing the opportunity of using [extremely optimized](https://www.elastic.co/search-labs/blog/vector-similarity-computations-ludicrous-speed) implementations of the integer dot product. This translates to a clear cut win in terms of retrieval quality as a function of performance.

### 1. Error correcting the scalar dot product

Most embedding models use either cosine or dot product similarity. The good thing is if you normalize your vectors then cosine (and even Euclidean) is equivalent to dot product (up to order). Therefore, reducing the quantization error in the dot product covers the great majority of use cases. This will be our focus.

The vector database use case is as follows. There is a large collection of floating point vectors from some black box embedding model. We want a quantization scheme which achieves the best possible recall when retrieving with query vectors which come from a similar distribution. Recall is the proportion of true nearest neighbors, those with maximum dot product computed with float vectors, which we retrieve computing similarity with quantized vectors. We assume we've been given the truncation interval [a,b][a,b][a,b] for now. All vector components are snapped into this interval in order to compute their quantized values exactly as we discussed before. In the next part we will discuss how to optimize this interval for the vector database use case.

To movitate the following analysis, consider that for any given document vector, if we knew the query vector ahead of time , we could compute the quantization error in the dot product exactly and simply subtract it. Clearly, this is not realistic since, apart from anything else, the query vector is not fixed. However, maybe we can achieve a real improvement by assuming that the query vector is drawn from a distribution that is centered around the document vector. This is plausible since queries that match a document are likely to be in the vicinity of its embedding. In the following, we formalize this intuition and actually derive a correction term. We first study the error that scalar quantization introduces into the dot product. We then devise a correction based on the expected first order error in the vicinity of each indexed vector. To do this requires us to store one extra float per vector. Since realistic vector dimensions are large this results in minimal overhead.

We will call an arbitrary vector in our database x\mathbf{x}x and an arbitrary query vector y\mathbf{y}y. Then

xty=(a+x−a)t(a+y−a)=ata+at(y−a)+at(x−a)+(y−a)t(x−a)\begin{align\*}
\mathbf{x}^t\mathbf{y} &= (\mathbf{a}+\mathbf{x}-\mathbf{a})^t(\mathbf{a}+\mathbf{y} - \mathbf{a}) \\
&= \mathbf{a}^t\mathbf{a}+\mathbf{a}^t(\mathbf{y}-\mathbf{a})+\mathbf{a}^t(\mathbf{x}-\mathbf{a})+(\mathbf{y}-\mathbf{a})^t(\mathbf{x}-\mathbf{a})
\end{align\*}
xty​=(a+x−a)t(a+y−a)=ata+at(y−a)+at(x−a)+(y−a)t(x−a)​

On the right hand side, the first term is a constant and the second two terms are a function of a single vector and can be precomputed. For the one involving the document, this is an extra float that can be stored with its vector representation. So far all our calculations can use floating point arithmetic. Everything interesting however is happening in the last term, which depends on the interaction between the query and the document. We just need one more bit more notation: define α=b−a2b−1\alpha = \frac{b-a}{2^b-1}α=2b−1b−a​ and ⋆q=clamp(⋆,a,b)α\star\_q=\frac{\text{clamp}(\star, \mathbf{a}, \mathbf{b})}{\alpha}⋆q​=αclamp(⋆,a,b)​ where we understand that the clamp function broadcasts over vector components. Let's rewrite the last term, still keeping everything in floating point, using a similar trick:

(y−a)t(x−a)=(αyq+y−a−αyq)t(αxq+x−a−αxq)=α2yqtxq−αyqtϵx+αxqtϵy+O(∥ϵ∥2)\begin{align\*}
(\mathbf{y}-\mathbf{a})^t(\mathbf{x}-\mathbf{a}) &= (\alpha \mathbf{y}\_q + \mathbf{y} -\mathbf{a} - \alpha\mathbf{y}\_q)^t(\alpha \mathbf{x}\_q + \mathbf{x} -\mathbf{a} - \alpha\mathbf{x}\_q) \\
&= \alpha^2\mathbf{y}\_q^t\mathbf{x}\_q - \alpha\mathbf{y}\_q^t\mathbf{\epsilon}\_x + \alpha\mathbf{x}\_q^t\mathbf{\epsilon}\_y + \text{O}(\|\mathbf{\epsilon}\|^2)
\end{align\*}
(y−a)t(x−a)​=(αyq​+y−a−αyq​)t(αxq​+x−a−αxq​)=α2yqt​xq​−αyqt​ϵx​+αxqt​ϵy​+O(∥ϵ∥2)​

Here, ϵ⋆=⋆−a−⋆q\mathbf{\epsilon}\_{\star} = \star - \mathbf{a}- \star\_qϵ⋆​=⋆−a−⋆q​ represents the quantization error. The first term is just the scaled quantized vector dot product and can be computed exactly. The last term is proportional in magnitude to the square of the quantization error and we hope this will be somewhat small compared to the overall dot product. That leaves us with the terms that are linear in the quantization error.

We can compute the quantization error vectors in the query and document, ϵy\mathbf{\epsilon}\_yϵy​ and ϵx\mathbf{\epsilon}\_xϵx​ respectively, ahead of time. However, we don't actually know the value of x\mathbf{x}x we will be comparing to a given y\mathbf{y}y and vice versa. So we don't know how to calculate the error in the dot product quantities exactly. In such cases it is natural to try and minimize the error in expectation (in some sense we discuss below).

If x\mathbf{x}x and y\mathbf{y}y are drawn at random from our corpus they are random variables and so too are xq\mathbf{x}\_qxq​ and yq\mathbf{y}\_qyq​. For any distribution we average over for xq\mathbf{x}\_qxq​ then Ex[αxqtϵy]=αEx[xq]tϵy\mathbb{E}\_x[\alpha\mathbf{x}\_q^t \mathbf{\epsilon}\_y]=\alpha\mathbb{E}\_x[\mathbf{x}\_q]^t \mathbf{\epsilon}\_yEx​[αxqt​ϵy​]=αEx​[xq​]tϵy​, since α\alphaα and ϵy\mathbf{\epsilon}\_yϵy​ are fixed for a query. This is a constant additive term to the score of each document, which means it does not change their order. This is important as it will not change the quality of retrieval and so we can drop it altogether.

What about the αyqtϵx\alpha\mathbf{y}\_q^t \mathbf{\epsilon}\_xαyqt​ϵx​ term? The naive thing is to assume that the yqt\mathbf{y}\_q^tyqt​ is a random sample from our corpus. However, this is not the best assumption. In practice, we know that the queries which actually match a document will come from some region in the vicinity of its embedding as we illustrate in the figure below.

![query distribution](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt024876c2ac564037/6a17f6203e9e45495aba1622/8527486b84735a02176f13ec635b606faccd146b-742x539.png)

Schematic query distribution that is expected to match a given document embedding (orange) vs all queries (blue plus orange).

We can efficiently find nearest neighbors of each document x\mathbf{x}x in the database once we have a proximity graph. However, we can do something even simpler and assume that for relevant queries Ey[yq]≈xq\mathbb{E}\_y[\mathbf{y}\_q] \approx \mathbf{x}\_qEy​[yq​]≈xq​. This yields a scalar correction αxqtϵx\alpha\mathbf{x}\_q^t\mathbf{\epsilon}\_xαxqt​ϵx​ which only depends on the document embedding and can be precomputed and added on to the at(x−a)\mathbf{a}^t(\mathbf{x}-\mathbf{a})at(x−a) term and stored with the vector. We show later how this affects the quality of retrieval. The anisotropic correction is inspired by [this](https://arxiv.org/pdf/1908.10396.pdf) approach for reducing product quantization errors.

Finally, we note that the main obstacle to improving this correction is we don't have useful estimates of the joint distribution of the query and document embedding quantization errors. One approach that might enable this, at the cost of some extra memory and compute, is to use low rank approximations of these errors. We plan to study schemes like this since we believe they could unlock accurate general purpose 2 or even 1 bit scalar quantization.

### 2. Optimizing the truncation interval

So far we worked with some specified interval [a,b][a,b][a,b] but didn't discuss how to compute it. In the context of quantization for model inference people tend to use quantile points of the component distribution or their minimum and maximum. Here, we discuss a new method for computing this based on the idea that preserving the order of the dot product values is better suited to the vector database use case.

First off, why is this not equivalent to minimizing the magnitude of the quantization errors? Suppose for a query y\mathbf{y}y the top-k matches are xi\mathbf{x}\_ixi​ for i∈[k]i \in [k]i∈[k]. Consider two possibilities, the quantization error is some constant ccc, or it is is normally distributed with mean 000 and standard deviation c10\frac{c}{10}10c​. In the second case the expected error is roughly 10 times smaller than the first. However, the first effect is a constant shift, which preserves order and has no impact on recall. Meanwhile, if 1k∑i=1k∣yt(xi−xi+1)∣<c10\frac{1}{k}\sum\_{i=1}^k \left|\mathbf{y}^t(\mathbf{x}\_i-\mathbf{x}\_{i+1})\right| < \frac{c}{10}k1​∑i=1k​∣yt(xi​−xi+1​)∣<10c​ it is very likely the random error will reorder matches and so affect the quality of retrieval.

Let's use the previous example to better motivate our approach. The figure below shows the various quantities at play for a sample query y\mathbf{y}y and two documents xi\mathbf{x}\_ixi​ and xi+1\mathbf{x}\_{i+1}xi+1​. The area of each blue shaded rectangle is equal to one of the floating point dot products and the area of each red shaded rectangle is equal to one of the quantization *errors*. Specifically, the dot products are ∥y∥∥Pyxi∥\|\mathbf{y}\|\|P\_y\mathbf{x}\_i\|∥y∥∥Py​xi​∥ and ∥y∥∥Pyxi+1∥\|\mathbf{y}\|\|P\_y\mathbf{x}\_{i+1}\|∥y∥∥Py​xi+1​∥, and the quantization errors are ∥y∥∥Py(xi−a−xi,q)∥\|\mathbf{y}\|\|P\_y(\mathbf{x}\_i-\mathbf{a}-\mathbf{x}\_{i,q})\|∥y∥∥Py​(xi​−a−xi,q​)∥ and ∥y∥∥Py(xi+1−a−xi+1,q)∥\|\mathbf{y}\|\|P\_y(\mathbf{x}\_{i+1}-\mathbf{a}-\mathbf{x}\_{i+1,q})\|∥y∥∥Py​(xi+1​−a−xi+1,q​)∥ where Py=yyt∥y∥2P\_y=\frac{\mathbf{y}\mathbf{y}^t}{\|\mathbf{y}\|^2}Py​=∥y∥2yyt​ is the projection onto the query vector. In this example the errors preserve the document order. This follows because the right blue rectangle (representing the exact dot product) and union of right blue and red rectangles (representing the quantized dot product) are both larger than the left ones. It is visually clear the more similar the left and right red rectangles the less likely it is the documents will be reordered. Conversely, the more similar the left and right blue rectangles the more likely it is that quantization will reorder them.

![quantization error](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt583236ddb9e7f0b5/6a17f6232f4a5c9329fa8a88/43a7f28d530ddb8f84c3cb17c204412d17542c62-1440x763.png)

Schematic of the dot product values and quantization error values for a query and two near neighbor documents. In this case, the document order is preserved by quantization.

One way to think of the quantized dot product is that it models the floating point dot product. From the previous discussion we want to minimize the variance of this model's residual error, which should be as similar as possible for each document. However, there is a second consideration: the density of the floating point dot product values. If these values are close together it is much more likely that quantization will reorder them. It is quite possible for this density to change from one part of the embedding space to another and higher density regions are more sensitive to quantization errors.

A natural measure which captures both the quantization error variance and the density of the dot product values is the [coefficient of determination](https://en.wikipedia.org/wiki/Coefficient_of_determination) of the quantized dot product with respect to the floating point dot product. A good interval [a,b][a,b][a,b] will maximize this in expectation over a representative query distribution. We need a reasonable estimator for this quantity for the database as a whole that we can compute efficiently. We found the following recipe is both fast and yields an excellent choice for parameters aaa and bbb:

1. Sample 1000 random document vectors from the index.
2. For each sample vector find its 10 nearest neighbors.
3. Maximize the average coefficient of determination of the quantized dot product between the sampled vectors and their nearest neighbors with respect to the interval [a,b][a,b][a,b].

This optimization problem can be solved by any black box solver. For example, we used a variant of the adaptive [LIPO algorithm](https://arxiv.org/pdf/1703.02628.pdf) in the following. Furthermore, we found that our optimization objective was well behaved (low [Lipschitz constant](https://en.wikipedia.org/wiki/Lipschitz_continuity)) for all data sets we tested.

## Proof of principle for int4 quantization

Before deciding to implement this scheme for real we studied how it behaves with int4 quantization.

Below we show results for two data sets that are fairly typical of passage embedding model distributions on real data. To generate these we use [e5-small-v2](https://huggingface.co/intfloat/e5-small-v2) and Cohere's [multilingual-22-12](https://huggingface.co/datasets/Cohere/wikipedia-22-12-en-embeddings) models. These are both fairly state-of-the-art text embedding models. However, they have rather different characteristics. The e5-small-v2 model uses cosine similarity, its vectors have 384 dimensions and very low angular variation. The multilingual-22-12 model uses dot product similarity, its vectors have 768 dimensions and it encodes information in their length. They pose rather different challenges for our quantization scheme and improving both gives much more confidence it works generally. For e5-small-v2 we embedded around 500K passages and 10K queries sampled from the MS MARCO passage data set. For multilingual-22-12 we used around 1M passages and 1K distinct passages for queries sampled from the [English Wikipedia](https://huggingface.co/datasets/Cohere/wikipedia-22-12-en-embeddings) data set.

First of all, it is interesting to understand the accuracy of the int4 dot product values. The figure below shows the int4 dot product values compared to their float values for a random sample of 100 documents and their 10 nearest neighbors taken from the set we use to compute the optimal truncation interval for e5-small-v2. The orange “best fit” line is y=x−0.017y=x-0.017y=x−0.017. Note that this underlines the fact that this procedure can pick a biased estimator if it reduces the residual variance: in this case the quantized dot product is systematically underestimating the true dot product. However, as we discussed before, any constant shift in the dot product is irrelevant for ranking. For the full 1k samples we achieve an R2R^2R2 of a little less than 0.995, i.e. the int4 quantized dot product is a very good model of the float dot product!

![int4 dot product](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltae06cf79b863c5c9/6a17f624ec0f89f5c75a67a6/5258bbe0bda22485625cf68365375357172caf50-972x602.png)

Comparison of int4 dot product values to the corresponding float values for a random sample of 100 documents and their 10 nearest neighbors.

While this is reassuring, what we really care about is the impact on retrieval quality. Since one can implement brute force nearest neighbor search in a few lines, it allows us to quickly test the impact of our design choices on retrieval. In particular, we are interested in understanding the expected proportion of true nearest neighbors we retrieve when computing similarities using int4 quantized vectors. Below we show the results for an ablation study of the dot product correction and interval optimization.

In general, one can boost the accuracy of any quantization scheme by gathering more than the requested vector count and reranking them using their floating point values. However, this comes with a cost: it is significantly more expensive to search graphs for more matches and the floating point vectors must be loaded from disk or it defeats the purpose of compressing them. One way of comparing alternatives is therefore to understand how many vectors must be reranked to achieve the same recall. The lower this number is, the better. In the figures below we show average recall curves as a function of the number of candidates we rerank for different combinations of the two improvements we have discussed:

1. “Baseline” sets [a,b][a,b][a,b] to the 1−1d+11-\frac{1}{d+1}1−d+11​ central confidence and applies no correction to the dot product,
2. “No correction” optimizes the interval [a,b][a,b][a,b] by maximizing R2R^2R2 but applies no correction to the dot product,
3. “No optimization” sets [a,b][a,b][a,b] to the 1−1d+11-\frac{1}{d+1}1−d+11​ central confidence but applies the linear correction to the dot product, and
4. “Our scheme” optimizes the interval [a,b][a,b][a,b] by maximizing R2R^2R2 and applies the linear correction to the dot product.

Note that we used ddd to denote the vector dimension.

![e5-small-v2 recall curves](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltbe9b2bc61be57579/6a17f626577262f8b61bcd78/8873a7ad11232a6302203bbd88ef89c6be6ba65b-784x500.png)

Average recall@10 curves for e5-small-v2 embeddings as a function of the number of candidates reranked for different combinations of the two improvements we discussed.

![multilingual-22-12 recall curves](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta12e0a45b454ee81/6a17f627148009666db488e1/d37e7e3fcc420ddee6431598f14a1e9db3a7fe38-785x500.png)

Average recall@10 curves for multilingual-22-12 embeddings as a function of the number of candidates reranked for different combinations of the two improvements we discussed.

For e5-small-v2 embeddings we roughly halve the number of vectors we need to rerank to achieve 95% recall compared to the baseline. For multilingual-22-12 embeddings we reduce it by closer to a factor of three. Interestingly, the impact of the two improvements is different for the different data sets. For e5-small-v2 embeddings applying the linear correction has a significantly larger effect than optimizing the interval [a,b][a,b][a,b] whilst the converse is true for multilingual-22-12 embeddings. Another important observation is the gains are more significant if one wants to achieve very high recall: to achieve close to 99% recall one has to rerank at least 5 times as many vectors for both data sets in the baseline versus our improved quantization scheme.

## Conclusion

We have discussed the theoretical and empirical motivation behind two novelties we introduced to achieve high quality int4 quantization, as well as some preliminary results that indicate it'll be an effective general purpose scheme for in memory vector storage for retrieval. This is all well and good, but how well does it work in a real vector database implementation? In the [companion blog](https://www.elastic.co/search-labs/blog/int4-scalar-quantization-in-lucene) we discuss our implementation in Lucene and compare it to other storage options such as floating point and int7, which Lucene also provides.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt29bbbf4463c73d8a/6a6a33fa55755baeaa2bd248/a6563ee307cc2d29722c490b043ee736c46974f3-1280x720.png)

[Jina AI](/search-labs/blog/category/jina-ai)[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

### 56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker

July 27, 2026|[Felix Wang](/search-labs/author/felix-wang)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt097721c03648a84e/6a6a33ef0a222b4c70877f32/8f6b95800c65fe389d3e8d8281e8e8dc351f734d-992x342.png)

[ES|QL](/search-labs/blog/category/esql)[ML Research](/search-labs/blog/category/ml-research)[Agentic AI](/search-labs/blog/category/agentic-ai)

### How Elasticsearch detects multiple change points in time series with 0.99 recall

July 24, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt950edbc25d291821/6a6119f01b1d495dc56f181b/31783975126874424fc20c3c96bd95fe28d5f201-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)

### How Elasticsearch auto-tunes vector quantization to hit your recall target

July 21, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9d9912c8d4187096/6a1704f5b0367d30e672bc17/54a6e5197f5721b36fc65f27387d29803ed35589-721x420.jpg)

[ML Research](/search-labs/blog/category/ml-research)[Python](/search-labs/blog/category/python-programming)

### Evaluating search relevance part 1 - The BEIR benchmark

July 16, 2024|[Thanos Papaoikonomou](/search-labs/author/thanos-papaoikonomou)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter