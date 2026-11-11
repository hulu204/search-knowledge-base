---
title: 'Understanding optimized scalar quantization'
company: Elastic
tag: 索引构建
date: 2024-12-19
url: https://www.elastic.co/search-labs/blog/scalar-quantization-optimization
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Understanding optimized scalar quantization

In this post, we explain a new form of scalar quantization we've developed at Elastic that achieves state-of-the-art accuracy for binary quantization.

December 19, 2024

[Thomas Veasey](/search-labs/author/thomas-veasey)

[ML Research](/search-labs/blog/category/ml-research)[Basics](/search-labs/blog/category/basics)

Jump to

Share

At Elastic we continue to work on innovations that improve the cost and performance of our vector indices. In this post we’re going to discuss in detail the implementation and intuition for a new version of scalar quantization we’ve been working on which we’re calling optimized scalar quantization or OSQ. This provides a further enhancement to our [BBQ index format](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch). Indeed, we set new state-of-the-art performance for 32×\times× compression.

It also allows us to get very significant improvements in accuracy compared to naive scalar quantization approaches while retaining similar index compression and query performance. We plan to roll out 2, 4 and 7 bit quantization schemes and indeed unify all our index compression options to use this same underlying technique. Furthermore, we anticipate that with 7 bit quantization we should be able to discard the raw floating point vectors and plan to evaluate this thoroughly.

#### Measuring success

For any compression scheme we need to worry about its impact on the query behavior. For nearest neighbor queries there is a metric that much prior art focuses on. This is the recall at kkk. Specifically, one measures the fraction of true nearest neighbor vectors that a query returns.

In fact, we already exploit the relaxation that we don't find the true nearest neighbors, even when we search with uncompressed vectors in Lucene. Linear complexity is unavoidable if one wants to find the true nearest neighbors in a high dimensional vector space. The data structure that Lucene uses to index vector data is an [HNSW graph](https://en.wikipedia.org/wiki/Hierarchical_navigable_small_world), which allows it to run approximate nearest neighbor queries significantly faster than a linear scan.

In this blog we study a metric that we’ll abbreviate as recall@k∣nk|nk∣n, which is the recall at kkk retrieving n≥kn\geq kn≥k candidates and reranking them using the uncompressed vector distance calculation. Note that if n=kn=kn=k then it's simply equal to the recall at kkk. We also look at the quality of the approximation of the uncompressed vector distances.

We’ll discuss all this in more detail when we discuss our results.

#### Motivation

Scalar quantization, as we’ve discussed [before](https://www.elastic.co/search-labs/blog/scalar-quantization-101), is an approach which allows one to represent floating point vectors by integer vectors. There are two reasons to do this:

1. It allows you to reduce the amount of memory needed to represent a vector, by using fewer than 32 bits per integer, and
2. It allows you to accelerate the distance calculation between vectors, which is the bottleneck for performing nearest neighbor queries in vector databases.

Recently, a [paper](https://arxiv.org/pdf/2405.12497), which we’ve discussed [before](https://www.elastic.co/search-labs/blog/rabitq-explainer-101), proposed an approach called RaBitQ that is able to achieve good recall using only 1 bit per component. This is exciting because 32×\times× compression is competitive with [Product Quantization](https://inria.hal.science/inria-00514462v2/document) (PQ), which was the previous state-of-the-art approach when compression was paramount. A key advantage of RaBitQ is that it’s relatively straightforward to accelerate distance calculations with SIMD operations. Certainly, when it is compared to PQ that uses lookups to compute distance, for which it is much harder to exploit hardware parallelism. The authors performed extensive experiments and showed they were able to achieve consistently higher recall as a function of query latency than PQ using the same compression ratio with an IVF index.

Although the RaBitQ approach is conceptually rather different to scalar quantization, we were inspired to re-evaluate whether similar performance could be unlocked for scalar quantization. In our companion piece we will discuss the result of integrating OSQ with HNSW and specifically how it compares to the baseline BBQ quantization scheme, which is inspired by RaBitQ. As an incentive to keep reading this blog we note that we were able to achieve systematically higher recall in this setting, sometimes by as much as 30%. Another advantage of OSQ is it immediately generalizes to using nnn bits per component. For example, we show below that we’re able to achieve excellent recall in all cases we tested using minimal or even no reranking with only a few bits per component.

This post is somewhat involved. We will take you through step-by-step the innovations we’ve introduced and explain some of the intuition at each step.

#### Dot products are enough

In the following we discuss only the dot product, which would translate to a MIP query in Elasticsearch. In fact, this is sufficient because well known reductions exist to convert the other metrics Elasticsearch supports, Euclidean and cosine, to computing a dot product. For the Euclidean distance we note that

∥y−x∥2=∥x∥2+∥y∥2−2xty\|y-x\|^2 = \|x\|^2 + \|y\|^2 - 2x^ty∥y−x∥2=∥x∥2+∥y∥2−2xty

and also that ∥x∥\|x\|∥x∥ and ∥y∥\|y\|∥y∥ can be precomputed and cached, so we need only compute the dot product ytxy^t xytx in order to compare two vectors. For cosine we simply need to normalize vectors and then

ytx∥y∥∥x∥=ytx\frac{y^t x}{\|y\|\|x\|} = y^t x∥y∥∥x∥ytx​=ytx

### Scalar quantization refresher

Scalar quantization is typically defined by the follow componentwise equation

x^i=round(2n−1b−a(clamp(xi,a,b)−a))\hat{x}\_i = \text{round}\left(\frac{2^n-1}{b-a} \left(\text{clamp}(x\_i, a, b) - a\right)\right)x^i​=round(b−a2n−1​(clamp(xi​,a,b)−a))

Here, clamp(⋅,a,b)=max⁡(min⁡(⋅,b),a)\text{clamp}(\cdot, a, b) = \max(\min(\cdot, b), a)clamp(⋅,a,b)=max(min(⋅,b),a). The quantized vector x^\hat{x}x^ is integer valued with values less than or equal to 2n−12^n-12n−1, that is we’re using nnn bits to represent each component. The interval [a,b][a,b][a,b] is called the quantization interval.

We also define the quantized approximation of the original floating point vector, which is our best estimate of the floating point vector after we’ve applied quantization. We never directly work with this quantity, but it is convenient to describe the overall approach. This is defined as follows

xˉ=a1+b−a2n−1x^\bar{x} = a 1 + \frac{b-a}{2^n-1} \hat{x}xˉ=a1+2n−1b−a​x^

Here, 111 denotes a vector whose components are all equal to one. Note that we abuse notation here and below by using 111 to denote both a vector and scalar and we rely on the context to make the meaning clear.

### The need for speed

A key requirement we identified for scalar quantization is that we can perform distance comparisons directly on integer vectors. Integer arithmetic operations are more compute efficient than floating point ones. Furthermore, higher throughput specialized hardware instructions exist for performing them in parallel. We’ve [discussed how to achieve](https://www.elastic.co/search-labs/blog/vector-similarity-computations-ludicrous-speed) this in the context of scalar quantization before.

Below we show that as long as we cache a couple of corrective factors we can use a different quantization interval and number of bits for each vector we quantize and still compute the dot product using integer vectors. This is the initial step towards achieving OSQ.

First of all observe that our best estimate of the dot product between two quantized vectors is

ytx=(ay1+by−ay2ny−1y^)t(ax1+bx−ax2nx−1x^)y^t x = \left(a\_y 1 + \frac{b\_y-a\_y}{2^{n\_y} - 1}\hat{y}\right)^t \left(a\_x 1 + \frac{b\_x-a\_x}{2^{n\_x} - 1}\hat{x}\right)ytx=(ay​1+2ny​−1by​−ay​​y^​)t(ax​1+2nx​−1bx​−ax​​x^)

Expanding we obtain

y^tx^=ayax1t1+by−ay2ny−1ax1ty^+bx−ax2nx−1ay1tx^+by−ay2ny−1bx−ax2nx−1y^tx^\hat{y}^t \hat{x} = a\_y a\_x 1^t 1 + \frac{b\_y-a\_y}{2^{n\_y} - 1} a\_x 1^t \hat{y} + \frac{b\_x-a\_x}{2^{n\_x} - 1} a\_y 1^t \hat{x} + \frac{b\_y-a\_y}{2^{n\_y} - 1} \frac{b\_x-a\_x}{2^{n\_x} - 1} \hat{y}^t \hat{x}y^​tx^=ay​ax​1t1+2ny​−1by​−ay​​ax​1ty^​+2nx​−1bx​−ax​​ay​1tx^+2ny​−1by​−ay​​2nx​−1bx​−ax​​y^​tx^

Focusing on the vector dot products, since these dominate the compute cost, we observe that 1t11^t 11t1 is just equal to the vector dimension, and 1ty^1^t\hat{y}1ty^​ and 1tx^1^t\hat{x}1tx^ are the sums of the quantized query and document vector components, respectively. For the query this can be computed once upfront and for the documents these can be computed at index time and stored with the quantized vector. Therefore, we need only compute the integer vector dot product y^tx^\hat{y}^t\hat{x}y^​tx^ per comparison.

### The geometry of scalar quantization

To build a bit more intuition about OSQ we digress to understand more about how scalar quantization represents a vector. Observe that the set of all possible quantized vectors lie inside a cube centered on the point a+b21\frac{a+b}{2}12a+b​1 with side length b−ab−ab−a. If only 1 bit is being used then the possible vectors lie at the 2d2^d2d corners of the cube. Otherwise, the possible vectors lie on a regular grid with 2nd2^{nd}2nd points.

By changing aaa and bbb, we are only able to expand or contract the cube or slide it along the line spanned by the 111 vector. In particular, suppose the vectors in the corpus are centered around some point mmm. We can decompose this into a component parallel to the 111 vector and a component perpendicular to it as follows

m=11tdm+(I−11td)mm = \frac{1 1^t}{d} m + \left(I - \frac{1 1^t}{d}\right) mm=d11t​m+(I−d11t​)m

If we center the cube on the point at 1tmd1\frac{1^t m}{d}1d1tm​1 then it must still expand it to encompass the offset m−1tmd1m-\frac{1^t m}{d}1m−d1tm​1 before it covers even the center of the data distribution. This is illustrated in the figure below for 2 dimensions.

![The geometry of scalar quantization](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltbfcc49535a9a0f21/6a17e3af25daab1e7608a1c3/8b8bb24bdc6c5718d564fd2b19f9694c3a84712e-1262x1006.png)

Since the quantization errors will be proportional on average to the side length of the cube, this suggests that we want to minimize ∥m−1tmd1∥\| m-\frac{1^t m}{d}1 \|∥m−d1tm​1∥. An easy way to do this is to center the query and document vectors before quantizing. We show below that if we do this we can still recover the dot product between the original vectors.

Note that

ytx=(y−m+m)t(x−m+m)=(y−m)t(x−m)+mty+mtx−mtm\begin{align\*}
y^t x &= (y - m + m)^t (x - m + m) \\
&= (y - m)^t (x - m) + m^t y + m^t x - m^t m
\end{align\*}ytx​=(y−m+m)t(x−m+m)=(y−m)t(x−m)+mty+mtx−mtm​

The values mtym^t ymty and mtxm^t xmtx, which are the inner product between the query and document vector and the centroid of the vectors in the corpus, can be precomputed and in the case of the document vector cached with its quantized representation. The quantity mtmm^t mmtm is a global constant.

This means we only need to estimate (y−m)t(x−m)(y−m)^t(x−m)(y−m)t(x−m) when comparing a query and document vector. In other words, we can quantize the centered vectors and recover an estimate of the actual dot product.

### The distribution of centered vectors

So far we’ve shown that we can use a different bit count and a different quantization interval per vector. We next show how to exploit this to significantly improve the accuracy of scalar quantization. We propose an effective criterion and procedure for optimizing the choice of the constants aaa and bbb. However, before discussing this it is useful to see some examples of the component distribution in real centered embedding vectors.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt184a2a7baee30ff9/6a17e3b0631730261d585a0a/738c391304dd314986abe4c7cd7de978149f234e-2530x942.png)

We observe that the values are all fairly normally distributed and will use this observation to choose our initial quantization interval.

Looking at these plots one might guess it would be beneficial to scale components. Specifically, it seems natural to standardize the component distributions of the Cohere v2 and the gte-base-en-v1.5 embeddings. In general, this would amount to applying a scaling matrix to the document vectors before quantization as follows

Diag(σ)−1(x−m)\text{Diag}(\sigma)^{-1} (x - m)Diag(σ)−1(x−m)

Here, Diag(σ)\text{Diag}(\sigma)Diag(σ) is a diagonal matrix whose diagonal entries are the standard deviations of the components for the corpus as a whole. We can apply this operation and still compute the dot product efficiently because we simply need to apply the inverse transformation to the query vector before quantizing it

(y−m)t(x−m)=(Diag(σ)(y−m))t(Diag(σ)−1(x−m))(y - m)^t (x - m) = \left(\text{Diag}(\sigma) (y - m)\right)^t \left(\text{Diag}(\sigma)^{-1} (x - m)\right)(y−m)t(x−m)=(Diag(σ)(y−m))t(Diag(σ)−1(x−m))

The effect is not symmetric because, as we’ll discuss below, we use a higher bit count for the query.

Referring back to our geometric picture this would amount to stretching the different edges of the cube. We tried this but found it didn’t measurably improve effectiveness once we optimize the interval directly for each vector so avoid the extra complexity.

### Initializing the quantization interval

Let’s consider a natural criterion for setting a global quantization interval for normally distributed data. If we pick a vector, XXX, at random from the corpus then the quantization error is given by

∥X−x(a,b)∥2=∑i=1d(Xi−(a+b−a2n−1x^i))2\| X - x(a,b)\|^2 = \sum\_{i=1}^d \left(X\_i - \left(a+\frac{b-a}{2^n-1}\hat{x}\_i\right)\right)^2∥X−x(a,b)∥2=i=1∑d​(Xi​−(a+2n−1b−a​x^i​))2

By assumption, and as we showed empirically is often the case, each component of XXX is normally distributed or Xi∼N(0,σi)X\_i \sim N(0,\sigma\_i)Xi​∼N(0,σi​). In such a scenario it is reasonable to minimize the expected square error. Specifically, we seek

a∗,b∗=argmin⁡a,b  EX[∑i=1d(Xi−(a+b−a2n−1x^i))2]a^\*,b^\* = arg\min\_{a,b} \; \mathbb{E}\_{X} \left[ \sum\_{i=1}^d \left(X\_i - \left(a+\frac{b-a}{2^n-1}\hat{x}\_i\right)\right)^2 \right]a∗,b∗=arga,bmin​EX​[i=1∑d​(Xi​−(a+2n−1b−a​x^i​))2]

Since the expectation is a linear operator it distributes over the summation and we can focus on a single term. Without loss of generality we can assume that XiX\_iXi​​ is a unit normal since we can always rescale the interval by the data standard deviation.

To compute this expectation we make use of the following quantity

I(x,c)=12π∫x(t−c)2e−t2/2dt=12(c2+1)erf(x2)+12πe−x2/2(2c−x)+constant\begin{align\*}
I(x,c) &= \frac{1}{\sqrt{2\pi}} \int^x (t-c)^2 e^{-t^2 / 2} dt \\
&= \frac{1}{2}\left(c^2+1\right) \text{erf}\left(\frac{x}{\sqrt{2}}\right) + \frac{1}{\sqrt{2\pi}} e^{-x^2/2} (2c-x) + \text{constant}
\end{align\*}
I(x,c)​=2π​1​∫x(t−c)2e−t2/2dt=21​(c2+1)erf(2​x​)+2π​1​e−x2/2(2c−x)+constant​

This is the expectation of the square error when rounding a normally distributed value to a fixed point ccc expressed as an indefinite integral, alternatively, before we’ve determined the range the value can take.

In order to minimize the expected quantization error we should snap floating point values to their nearest grid point. This means we can express the expected square quantization error as follows

Errore(a,b  |  n)=  I(a+s2,a)−I(−∞,a)  +∑i=12n−2I(a+2i+12s,a+is)−I(a+2i−12s,a+is)+I(∞,b)−I(a+2n+1−32s,b)\begin{align\*}
Error\_e\left(a,b\; \middle| \; n\right) =& \; I(a+\frac{s}{2}, a) - I(-\infty, a)\;+ \\
& \sum\_{i=1}^{2^n-2} I\left(a+\frac{2i+1}{2}s, a+is\right) - I\left(a+\frac{2i-1}{2}s, a+is\right) + \\
& I(\infty, b) - I\left(a+\frac{2^{n+1}-3}{2}s, b\right)
\end{align\*}Errore​(a,b∣n)=​I(a+2s​,a)−I(−∞,a)+i=1∑2n−2​I(a+22i+1​s,a+is)−I(a+22i−1​s,a+is)+I(∞,b)−I(a+22n+1−3​s,b)​

Where we defined s=b−a2n−1s=\frac{b−a}{2^n−1}s=2n−1b−a​​. The integration limits are determined by the condition that we snap to the nearest grid point.

We now have a function, in terms of the interval endpoints aaa and bbb, for the expected square quantization error using a reasonable assumption about the vector components’ distribution. It is relatively straightforward to show that this quantity is minimized by an interval centered on the origin. This means that we need to search for the value of a single variable zzz which minimizes Errore(−z,z  |  n)Error\_e\left(-z,z\; \middle| \; n\right)Errore​(−z,z∣n). The figure below shows the error as a function of zzz for various bit counts.

![Initializing the quantization interval in scalar quantization](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt109f8431eaaca8d0/6a17e3b2414c64e66f9450fb/03e858f7d4a6b277a296b83370a0af54137ef861-866x339.png)

Optimizing this function numerically for various choices of nnn gives the following quantization intervals

[a(1),b(1)]=[−0.798,0.798][a(2),b(2)]=[−1.493,1.493][a(3),b(3)]=[−2.051,2.051][a(4),b(4)]=[−2.514,2.514][a(7),b(7)]=[−3.611,3.611]\begin{align\*}
\left[a\_{(1)}, b\_{(1)}\right] &= [-0.798, 0.798] \\
\left[a\_{(2)}, b\_{(2)}\right] &= [-1.493, 1.493] \\
\left[a\_{(3)}, b\_{(3)}\right] &= [-2.051, 2.051] \\
\left[a\_{(4)}, b\_{(4)}\right] &= [-2.514, 2.514] \\
\left[a\_{(7)}, b\_{(7)}\right] &= [-3.611, 3.611] \\
\end{align\*}[a(1)​,b(1)​][a(2)​,b(2)​][a(3)​,b(3)​][a(4)​,b(4)​][a(7)​,b(7)​]​=[−0.798,0.798]=[−1.493,1.493]=[−2.051,2.051]=[−2.514,2.514]=[−3.611,3.611]​

We’re denoting the interval for nnn bits [a(n),b(n)]\left[a\_{(n)}, b\_{(n)}\right][a(n)​,b(n)​].

Finally, we need to map these fixed intervals to the specific interval to use for a vector xxx. To do this we shift by the mean of its components mxm\_xmx​​ and scale by their standard deviation σx\sigma\_xσx​​. It’s clear that we should always choose a≥xmina\geq x\_{min}a≥xmin​​ and b≤xmaxb\leq x\_{max}b≤xmax​. Therefore, our initial estimate for the quantization interval for a vector xxx using nnn bits per component is

[max⁡(mx+a(n)σx,xmin),min⁡(mx+b(n)σx,xmax)]\left[\max\left(m\_x+a\_{(n)}\sigma\_x, x\_{min}\right), \min\left(m\_x+b\_{(n)}\sigma\_x, x\_{max}\right)\right][max(mx​+a(n)​σx​,xmin​),min(mx​+b(n)​σx​,xmax​)]

### Refining the quantization interval

The initialization scheme actually works surprisingly well. We present the results of quantizing using this approach alone as one of the ablation studies when we examine the performance of OSQ. However, we can do better.

It has been [noted](https://arxiv.org/pdf/1908.10396) in the context of PQ that targeting minimum square quantization error is not actually the best criterion when you care about recall. In particular, you know you’re going to be running nearest neighbor queries on the corpus and the nearest neighbors of a query are very likely to be fairly parallel to the query vector. Let’s consider what this means.

Suppose we have query vector y∣∣y\_{||}y∣∣​ for which the document is relevant. Ignoring the quantization of the query vector, we can decompose the square of the error in the dot product into a component that is parallel to and a component which is perpendicular to the document vector as follows

(y∣∣t(x−xˉ))2=((xxt∥x∥2y∣∣)txxt∥x∥2(x−xˉ)+((I−xxt∥x∥2)y∣∣)t(I−xxt∥x∥2)(x−xˉ))2\left(y\_{||}^t (x - \bar{x})\right)^2 = \left(\left(\frac{x x^t}{\|x\|^2}y\_{||}\right)^t \frac{x x^t}{{\|x\|^2}}(x - \bar{x}) + \left(\left(I - \frac{x x^t}{\|x\|^2}\right) y\_{||}\right)^t \left(I - \frac{x x^t}{\|x\|^2}\right) (x - \bar{x}) \right)^2(y∣∣t​(x−xˉ))2=((∥x∥2xxt​y∣∣​)t∥x∥2xxt​(x−xˉ)+((I−∥x∥2xxt​)y∣∣​)t(I−∥x∥2xxt​)(x−xˉ))2

Now we expect ∥(I−xxt∥x∥2)y∣∣∥≪∥xxt∥x∥2y∣∣∥\left\|\left(I-\frac{x x^t}{\|x\|^2}\right) y\_{||}\right\| \ll \left\|\frac{x x^t}{\|x\|^2}y\_{||}\right\|​(I−∥x∥2xxt​)y∣∣​​≪​∥x∥2xxt​y∣∣​​. Furthermore, we would like to minimize the error in the dot product in this specific case, since this is when the document is relevant and our query should return it.

Let ∥(I−xxt∥x∥2)y∣∣∥=λ∥xxt∥x∥2y∣∣∥\left\|\left(I-\frac{x x^t}{\|x\|^2}\right) y\_{||}\right\| = \sqrt{\lambda} \left\|\frac{x x^t}{\|x\|^2}y\_{||}\right\|​(I−∥x∥2xxt​)y∣∣​​=λ​​∥x∥2xxt​y∣∣​​ for some λ≪1\lambda \ll 1λ≪1. We can bound our quantization error in the dot product as follows

(y∣∣t(x−xˉ))2≤∥xxt∥x∥2y∣∣∥2∥xxt∥x∥2(x−xˉ)+λ(I−xxt∥x∥2)(x−xˉ)∥2\left(y\_{||}^t (x - \bar{x})\right)^2 \leq \left\|\frac{x x^t}{\|x\|^2}y\_{||}\right\|^2 \left\|\frac{x x^t}{\|x\|^2}(x - \bar{x})+\sqrt{\lambda} \left( I - \frac{x x^t}{\|x\|^2}\right)(x - \bar{x}) \right\|^2(y∣∣t​(x−xˉ))2≤​∥x∥2xxt​y∣∣​​2​∥x∥2xxt​(x−xˉ)+λ​(I−∥x∥2xxt​)(x−xˉ)​2

Whatever way we quantize we can’t affect the quantity ∥xxt∥x∥2y∣∣∥\left\|\frac{x x^t}{\|x\|^2}y\_{||}\right\|​∥x∥2xxt​y∣∣​​ so all we care about is minimizing the second factor. A little linear algebra shows that this is equal to

Error(a,b  |  λ)=(xˉ(a,b)−x)t(xxt∥x∥2+λ(I−xxt∥x∥2))(xˉ(a,b)−x)Error \left(a, b\; \middle| \; \lambda \right) = \left(\bar{x}(a,b) - x\right)^t \left( \frac{x x^t}{\|x\|^2} + \lambda \left(I-\frac{x x^t}{\|x\|^2}\right)\right) \left(\bar{x}(a,b) - x\right)Error(a,b∣λ)=(xˉ(a,b)−x)t(∥x∥2xxt​+λ(I−∥x∥2xxt​))(xˉ(a,b)−x)

Here, we’ve made the dependence of this expression on the quantization interval explicit.

So far we’ve proposed a natural quantity to minimize in order to reduce the impact of quantization on MIP recall. We now turn our attention to how to efficiently minimize this quantity with respect to the interval [a,b][a,b][a,b].

There is a complication because the assignment of components of the vector to grid points depends on aaa and bbb while the optimal choice for aaa and bbb depends on this assignment. We use a [coordinate descent](https://en.wikipedia.org/wiki/Coordinate_descent) approach, which alternates between computing the quantized vector x^\hat{x}x^ while holding aaa and bbb fixed, and optimizing the quantization interval while holding x^\hat{x}x^ fixed. This is described schematically as follows.

1     \;\; a0,b0←max⁡(mx+a(n)σx,xmin),min⁡(mx+b(n)σx,xmax)a\_0,b\_0 \leftarrow \max\left(m\_x+a\_{(n)}\sigma\_x, x\_{min}\right), \min\left(m\_x+b\_{(n)}\sigma\_x, x\_{max}\right)a0​,b0​←max(mx​+a(n)​σx​,xmin​),min(mx​+b(n)​σx​,xmax​)
2     \;\; for k∈{1,2,...,rounds}k \in \{1,2,...,rounds\}k∈{1,2,...,rounds} do
3         \;\;\;\; compute x^(k)\hat{x}\_{(k)}x^(k)​ from ak−1a\_{k-1}ak−1​ and bk−1b\_{k-1}bk−1​
4         \;\;\;\; ak,bk←argmin⁡a,b  Error(a,b  |  λ,x^(k))a\_k,b\_k \leftarrow arg\min\_{a,b}\; Error\left(a,b\; \middle| \; \lambda, \hat{x}\_{(k)} \right)ak​,bk​←argmina,b​Error(a,b​λ,x^(k)​)
5         \;\;\;\; if Error(ak,bk  |  λ,x^(k))>Error(ak−1,bk−1  |  λ,x^(k−1))Error\left(a\_k,b\_k\; \middle| \; \lambda, \hat{x}\_{(k)} \right) > Error\left(a\_{k-1},b\_{k-1}\; \middle| \; \lambda, \hat{x}\_{(k-1)} \right)Error(ak​,bk​​λ,x^(k)​)>Error(ak−1​,bk−1​​λ,x^(k−1)​) then break

First we’ll focus on line 3. The simplest approach to compute x^\hat{x}x^ uses standard scalar quantization

x^(k),i=round(2n−1bk−1−ak−1(clamp(xi,ak−1,bk−1)−ak−1))\hat{x}\_{(k), i} = \text{round}\left(\frac{2^n-1}{b\_{k-1}-a\_{k-1}} \left(\text{clamp}(x\_i, a\_{k-1}, b\_{k-1}) - a\_{k-1}\right)\right)x^(k),i​=round(bk−1​−ak−1​2n−1​(clamp(xi​,ak−1​,bk−1​)−ak−1​))

Specifically, this would amount to snapping each component of xxx to the nearest grid point. In practice this does not minimize Error(a,b  |  λ)Error\left(a,b\; \middle| \; \lambda\right)Error(a,b∣λ) as we illustrate below.

![Refining the quantization interval - Optimized scalar quantization](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt056167c4736e32ca/6a17e3b47f6f155ceac09a90/2b79f406fbb4a5453d4e75ebe203f522653a64ec-1204x832.png)

Unfortunately, we can’t just enumerate grid points and find the minimum error one since there are 2nd2^{nd}2nd candidates; therefore, we tried the following heuristic:

1. Snap to the nearest grid point,
2. Coordinate-wise check if rounding in the other direction reduces the error.

This isn’t guaranteed to find the global optimum, which in fact isn’t guaranteed to be one of the corners of the grid square containing the floating point vector. However, in practice we found it meant the error almost never increased in an iteration of the loop over kkk. By contrast, when snapping to the nearest grid point the loop frequently exits due to this condition.

The heuristic yields a small but systematic improvement in the brute force recall. On average it amounted to +0.3% compared to just snapping to the nearest grid point. Given the impact is so small we decided it wasn’t worth the extra complexity and increased runtime.

We now turn our attention to line 4. This expression decomposes as follows

Error(a,b  |  λ,x^)=1−λ∥x∥2(xt(xˉ(a,b)−x))2+λ(xˉ(a,b)−x)t(xˉ(a,b)−x)Error\left(a,b\; \middle| \; \lambda, \hat{x} \right) = \frac{1-\lambda}{\|x\|^2} \left(x^t(\bar{x}(a,b)-x)\right)^2 + \lambda \left(\bar{x}(a,b)-x\right)^t \left(\bar{x}(a,b)-x\right)Error(a,b∣λ,x^)=∥x∥21−λ​(xt(xˉ(a,b)−x))2+λ(xˉ(a,b)−x)t(xˉ(a,b)−x)

It’s fairly easy to see that this is a convex quadratic form of aaa and bbb. This means it has a unique minimum where the partial derivatives w.r.t. aaa and bbb vanish. We won’t show the full calculation but give a flavor. For example, we can use the chain rule to help evaluate the first term

∂∂a(xt(xˉ(a,b)−x))2=2xt(xˉ(a,b)−x)∂xtxˉ(a,b)∂a\frac{\partial}{\partial a} \left(x^t(\bar{x}(a,b)-x)\right)^2 = 2 x^t(\bar{x}(a,b)-x) \frac{\partial x^t\bar{x}(a,b)}{\partial a}∂a∂​(xt(xˉ(a,b)−x))2=2xt(xˉ(a,b)−x)∂a∂xtxˉ(a,b)​

then

∂xtxˉ(a,b)∂a=∂∂a∑i=1dxi(a+b−a2n−1x^i)=∑i=1dxi(1−12n−1x^i)=∑i=1dxi(1−si)\frac{\partial x^t\bar{x}(a,b)}{\partial a} = \frac{\partial}{\partial a} \sum\_{i=1}^d x\_i \left(a + \frac{b-a}{2^n-1}\hat{x}\_i\right) = \sum\_{i=1}^d x\_i \left(1-\frac{1}{2^n-1}\hat{x}\_i\right) = \sum\_{i=1}^d x\_i (1-s\_i)∂a∂xtxˉ(a,b)​=∂a∂​i=1∑d​xi​(a+2n−1b−a​x^i​)=i=1∑d​xi​(1−2n−11​x^i​)=i=1∑d​xi​(1−si​)

Where we’ve defined si=12n−1x^is\_i = \frac{1}{2^n-1}\hat{x}\_isi​=2n−11​x^i​. The final result is that the optimal interval satisfies

[1−λ∥x∥2(∑ixi(1−si))2+λ∑i(1−si)21−λ∥x∥2(∑ixi(1−si))∑ixisi+λ∑i(1−si)si1−λ∥x∥2(∑ixi(1−si))∑ixisi+λ∑i(1−si)si1−λ∥x∥2(∑ixisi)2+λ∑isi2][ab]=[∑ixi(1−si)∑ixisi]\footnotesize \left[ \begin{matrix}
\frac{1-\lambda}{\|x\|^2}\left(\sum\_i x\_i(1-s\_i)\right)^2+\lambda \sum\_i (1-s\_i)^2 & \frac{1-\lambda}{\|x\|^2}\left(\sum\_i x\_i(1-s\_i)\right)\sum\_i x\_i s\_i+\lambda \sum\_i(1-s\_i)s\_i \\
\frac{1-\lambda}{\|x\|^2}\left(\sum\_i x\_i(1-s\_i)\right)\sum\_i x\_i s\_i+\lambda \sum\_i(1-s\_i)s\_i & \frac{1-\lambda}{\|x\|^2}\left(\sum\_i x\_i s\_i\right)^2 + \lambda \sum\_i s\_i^2
\end{matrix} \right]
\left[\begin{matrix}a \\ b\end{matrix}\right]=
\left[\begin{matrix}\sum\_i x\_i(1-s\_i) \\ \sum\_i x\_i s\_i \end{matrix}\right] [∥x∥21−λ​(∑i​xi​(1−si​))2+λ∑i​(1−si​)2∥x∥21−λ​(∑i​xi​(1−si​))∑i​xi​si​+λ∑i​(1−si​)si​​∥x∥21−λ​(∑i​xi​(1−si​))∑i​xi​si​+λ∑i​(1−si​)si​∥x∥21−λ​(∑i​xi​si​)2+λ∑i​si2​​][ab​]=[∑i​xi​(1−si​)∑i​xi​si​​]

which is trivial to solve for aaa​ and bbb​. Taken together with the preprocessing and interval initialization steps this defines OSQ.

### The query and document vectors are different

We noted already that each vector could choose its bit count. Whilst there are certain technical disadvantages to using different bit counts for different document vectors, the query and the document vectors are different. In particular, the compression factor the quantization scheme yields only depends on the number of bits used to represent the document vectors.

There are side effects from using more bits to represent the query, principally that it can affect the dot product performance. Also there’s a limit to what one can gain based on the document quantization error. However, we get large recall gains by using asymmetric quantization for high compression factors and this translates to significant net wins in terms of recall as a function of query latency. Therefore, we always quantize the query using at least 4 bits.

### How does it perform?

In this section we compare the brute force recall@k∣nk|nk∣n and the correlation between the estimated and actual dot products for OSQ and our baseline BBQ quantization scheme, which was an adaptation of RaBitQ to use with an HNSW index. We have previously evaluated this baseline scheme and its accuracy is commensurate with RaBitQ. The authors of RaBitQ did extensive comparisons with alternative methods showing its superiority; we therefore consider it sufficient to simply compare to this very strong baseline.

We also perform a couple of ablation studies: against a global interval and against the per vector intervals calculated by our initialization scheme. To compute a global interval we use the OSQ initialization strategy, but compute the mean and variance of the corpus as a whole. For low bit counts, this is significantly better than the usual fixed interval quantization scheme, which tends to use something like the 99th percentile centered confidence interval. High confidence intervals in such cases often completely fail because the grid points are far from the majority of the data.

We evaluate against a variety of embeddings

* [e5-small-v2](https://huggingface.co/intfloat/e5-small-v2)
* [arctic-embed-m](https://huggingface.co/Snowflake/snowflake-arctic-embed-m)
* [gte-base-en-v1.5](https://huggingface.co/Alibaba-NLP/gte-base-en-v1.5)
* [Cohere v2](https://docs.cohere.com/v2/docs/cohere-embed)
* [Gist descriptors](https://people.csail.mit.edu/torralba/code/spatialenvelope/)

and datasets

* [Quora](https://huggingface.co/datasets/mteb/quora)
* [FiQA](https://huggingface.co/datasets/mteb/fiqa)
* A sample of around 1M passages from the English portion of [wikipedia-22-12](https://huggingface.co/datasets/Cohere/wikipedia-22-12)
* [GIST1M](http://corpus-texmex.irisa.fr/)

The embedding dimensions vary from 384 to 960. E5, Arctic and GTE use cosine similarity, and Cohere and GIST using MIP. The datasets vary from around 100k to 1M vectors.

In all our experiments we set λ=0.1\lambda=0.1λ=0.1, which we found to be an effective choice.

First off we study 1 bit quantization. We report brute force recall in these experiments to take any effects of the indexing choice out of the picture. As such we do not compare recall vs latency curves, which are very strongly affected by both the indexing data structure and the dot product implementation. Instead we focus on the recall at 10 reranking the top n hits. In our next blog we’ll study how OSQ behaves when it is integrated with Lucene's HNSW index implementation and turn our attention to query latency. The figures below show our brute force recall@10∣n10|n10∣n for n∈{10,20,30,40,50}n\in\{10,20,30,40,50\}n∈{10,20,30,40,50}.

![How does it perform? Scalar quantization](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt54828356e6184ae0/6a17e3b6faa913944e93c7f4/e0fb0c335b72783a5699a426d424d501194212db-2466x842.png)

Rolling these up into the average recall@10∣n10|n10∣n for the 8 retrieval experiments we tested we get the table below.

| n | Baseline average recall@10|n | OSQ average recall@10|n | Global average recall@10|n | Initialization average recall@10|n |
| --- | --- | --- | --- | --- |
| 10 | 0.71 | 0.74 | 0.54 | 0.65 |
| 20 | 0.88 | 0.90 | 0.69 | 0.81 |
| 30 | 0.93 | 0.94 | 0.76 | 0.86 |
| 40 | 0.95 | 0.96 | 0.80 | 0.89 |
| 50 | 0.96 | 0.97 | 0.82 | 0.90 |

Compared to the baseline we gain 2% on average in recall. As for the ablation study, compared to using a global quantization interval we gain 26% and compared to our initial per vector quantization intervals we gain 10%.

The figure below shows the floating point dot product values versus the corresponding 1 bit quantized dot product values for a sample of 2000 gte-base-en-v1.5 embeddings. Visually the correlation is high.

![1 bit dot product - optimized scalar quantization](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta7501b52cd7618ea/6a17e3b7414c643031945102/a3329e3c0aac799fadc92f5d315c35f96239bca9-1090x852.png)

We can quantify this by computing the R2R^2R2 between the floating point and quantized dot products. For each dataset and model combination we computed the average R2R^2R2 for every query against the full corpus. We see small but systematic improvement in R2R^2R2 comparing OSQ to the baseline. The table below shows the R2R^2R2 values broken down by the dataset and model combinations we tested.

| Dataset | Model | Baseline R2 | OSQ R2 |
| --- | --- | --- | --- |
| FiQA | e5-small | 0.849 | 0.865 |
| FiQA | arctic | 0.850 | 0.863 |
| FiQA | gte | 0.925 | 0.930 |
| Quora | e5-small | 0.868 | 0.881 |
| Quora | arctic | 0.817 | 0.838 |
| Quora | gte | 0.887 | 0.897 |
| Wiki | Cohere v2 | 0.884 | 0.898 |
| GIST1M | - | 0.953 | 0.974 |

Interestingly, when we integrated OSQ with HNSW we got substantially larger improvements in recall than we see for brute force search, as we’ll show in our next blog. One hypothesis we have is that the improvements we see in correlation with the true floating point dot products are more beneficial for graph search than brute force search. For many queries the tail of high scoring documents are well separated from the bulk of the score distribution and are less prone to being reordered by quantization errors. By contrast we have to navigate through regions of low scoring documents as we traverse the HNSW graph. Here any gains in accuracy can be important.

Finally, the table below compares the average recall for 1 and 2 bit OSQ for the same 8 retrieval experiments. With 2 bits we reach 95% recall reranking between 10 and 20 candidates. The average R2R^2R2 rises from 0.893 for 1 bit to 0.968 for 2 bit.

| n | 1 bit OSQ average recall@10|n | 2 bit OSQ average recall@10|n |
| --- | --- | --- |
| 10 | 0.74 | 0.84 |
| 20 | 0.90 | 0.97 |
| 30 | 0.94 | 0.99 |
| 40 | 0.96 | 0.995 |
| 50 | 0.97 | 0.997 |

### Conclusion

We’ve presented an improved automatic scalar quantization scheme which allows us to achieve high recall with relatively modest reranking depth. Avoiding deep reranking has significant system advantages.

For 1 bit quantization we compared it to a very strong baseline and showed it was able to achieve systematic improvements in both recall and the accuracy with which it approximates the floating point vector distance calculation. Therefore, we feel comfortable saying that it sets new state-of-the-art performance for at 32×\times× compression of the raw vectors.

It also allows one to simply trade compression for retrieval quality using the same underlying approach and achieves significant performance improvements compared to standard scalar quantization techniques.

We are working on integrating this new approach into Elasticsearch. In our next blog we will discuss how it is able to enhance the performance of our existing BBQ scalar quantization index formats.

### Frequently Asked Questions

#### What is scalar quantization?

Scalar quantization is an approach which allows one to represent floating point vectors by integer vectors.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt04da2f4a75f879e7/6a17e3f86317309992585a18/60125a0e77fefce769db569472e1994a167487b2-1792x1024.jpg)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)

### Smokin' fast BBQ with hardware accelerated SIMD instructions

December 04, 2024|[Chris Hegarty](/search-labs/author/chris-hegarty)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt589d74e8ad4bdf30/6a17dc50e8fbce95c13a17f7/cb5b6797a34e71fb655214aee8bcb501f8cff6a0-1694x855.png)

[Lucene](/search-labs/blog/category/lucene)[Vector Database](/search-labs/blog/category/vector-database)

### Better Binary Quantization (BBQ) in Lucene and Elasticsearch

November 11, 2024|[Benjamin Trent](/search-labs/author/benjamin-trent)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt8198de5d9f8a294e/6a17e5dd2f4a5c785cfa88a2/7a8ead8b46e4ec9e0fc2a7188756661a7e412054-500x282.jpg)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

### RaBitQ binary quantization 101

October 22, 2024|[John Wagster](/search-labs/author/john-wagster)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt0cccbdeaa4571db2/6a17057dc1e8a52e10f881e0/2fff360ef055df5980c696adffeb49f4b125a268-1913x1182.png)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

### Better Binary Quantization (BBQ) vs. Product Quantization

November 18, 2024|[Benjamin Trent](/search-labs/author/benjamin-trent)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltb382d99ffac9992c/6a17d991b1e113640179f12c/dc07f16d347a68476bded5df9adb831452f61278-1024x1024.jpg)

[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

### Understanding scalar quantization in Lucene

November 11, 2023|[Benjamin Trent](/search-labs/author/benjamin-trent)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter