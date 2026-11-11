---
title: 'How Elasticsearch auto-tunes vector quantization to hit your recall target'
company: Elastic
tag: 索引构建
date: 2026-07-21
url: https://www.elastic.co/search-labs/blog/vector-quantization-auto-calibration-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# How Elasticsearch auto-tunes vector quantization to hit your recall target

Learn the geometric model that lets Elasticsearch predict recall with R² > 0.98 accuracy and auto-select vector quantization parameters from a small data sample.

July 21, 2026

[Thomas Veasey](/search-labs/author/thomas-veasey)[Tommaso Teofili](/search-labs/author/tommaso-teofili)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)

Jump to

Share

## What makes a good vector store?

A vector store that achieves good performance without tuning is more valuable than one that requires expert tuning. In fact, our contention is a data store that can be coaxed to exceptional performance by an expert who spends a week hand-tuning it is less useful than one that beats it consistently out of the box. In other words, easily achieving good performance is a first class property, not a nice to have. We can see this clearly in our telemetry. The great majority of users will never tune the internals of vector search at all, and why should they: it is just an enabler for what they're trying to build.

This is the imperative behind features like auto-calibration. The system as a whole should look at your data and your quality target and choose good parameters for you. Indeed we think this is a win-win, since it has far more nuanced information available to it to make these choices than we expose.

To make "good performance" precise, it helps to name the three attributes that characterize any vector search system, because they trade off against one another and you can't talk about one without fixing the others:

1. Performance: throughput (QPS), latency, and so on.
2. Hardware cost: a fair comparison always holds cost fixed. It's trivial to buy your way to more QPS or better recall by throwing hardware at the problem; the interesting question is what you achieve *per dollar*.
3. Search quality: recall, nDCG, and related measures of whether you're returning the right results.

The three form a frontier. Push one and, at fixed budget, you pay in another. Any honest comparison of approaches pins two down and measures the third. What we describe in this post is the mechanism we're introducing to pick quantization parameters for a fixed recall budget. It is a step on a longer journey towards a vector store that configures itself well across the board.

### Why recall is the right quality metric for vector search

Search quality is tricky, because the "right" results depend on relevance labels you usually don't have at index time. So we lean on recall as a safe proxy. The argument is simple: recall measures how well the approximate index reproduces the results of exact search over the *same embeddings*. If recall is high, you have not degraded search quality relative to what the underlying model can do; you can be confident you’ve faithfully preserved the baseline. You might still wish for a better embedding model, we've got you [covered](https://www.elastic.co/search-labs/blog/jina-embeddings-v5-text), but that's a separate concern from the index not damaging what the model already gives you.

This is why controlling recall matters so much, and why you should be wary of any system that doesn't reliably control it. If a vendor can't control recall, they can silently degrade your search experience, achieving impressive QPS numbers while quietly returning worse results, and you'd have no way to know without a labeled evaluation set. The method in this post is about maximizing performance while keeping a firm, predictable grip on quality**.**

### Why vector quantization parameters must be chosen at index time

What makes the problem genuinely hard is that vectors are quantized *as they are indexed*, so the parameters that govern quality (how many bits, how deep to rerank, whether to [precondition](https://www.elastic.co/search-labs/blog/robust-optimized-scalar-quantization)) have to be evaluated before we've seen the data laid out in its final form. We can't index everything, measure recall, and iterate; by then the quantization is baked in.

So we need to estimate what we'll need from a small sample, cheaply and in advance. Fortunately the Elasticsearch gives us natural moments to do this: segment merges are exactly such an opportunity. When segments are combined we have to rewrite the data anyway and can assess the data and (re)choose parameters. And as we'll see, models fit to small random samples give excellent estimates of the quantities we actually need to control. They’re typically good enough to set parameters once, with a small margin, and trust them as the index grows.

## How vector quantization affects nearest-neighbor recall

With that motivation in place, let's start to dig into the details.

Vector quantization is a critical component for making approximate nearest-neighbor (ANN) search affordable at scale; it's an area we've [innovated](https://www.elastic.co/search-labs/blog/scalar-quantization-optimization) in the past. Instead of storing and comparing full-precision embeddings, we store a lossy, compressed representation and search over that. The catch is the one above: lossy representations move distances around, so the "nearest" neighbors under quantized distances are not always the true nearest neighbors and recall suffers.

The standard fix is to over-retrieve and rerank. We use the cheap quantized distances to pull back the top nnn candidates, then recompute exact distances for those nnn and keep the best kkk. As long as the true top-kkk are present somewhere in the retrieved top-nnn, reranking recovers them exactly.

Reranking isn’t free, we have to fetch high precision vectors from disk. However, we can precisely characterize the performance of reranking based on hardware characteristics alone. This reframes the whole problem. The question is no longer "how much does quantization distort distances?" in the abstract, but something which relates back to the attributes we care about:

> Given a quantization scheme with some error magnitude, and a rerank budget of nnn candidates, what recall@kkk should we expect. As an immediate consequence, what is the *cheapest* set of parameters that hits our recall target?

This post derives a model that answers exactly that. The core of it is a single, surprisingly clean idea: if we can characterize the *distribution of distances to the* kkk*-th nearest neighbor*, and we have a model of the *quantization error distribution*, then we can compute expected recall after reranking in closed form (up to a one-dimensional integral). Everything else – bit counts, rerank depth, whether to precondition – becomes a search over a model we can fit cheaply from a small sample, instead of an expensive empirical sweep over full indices built with those parameters.

We build it up to this in three stages: the geometry of nearest-neighbor distances, the scaling law that falls out of it, and then the recall model that ties quantization error to recall given a reranking budget. Be warned, the following gets a little bit involved, but to give you intuition about what is happening see the video below.

![Animation showing how vector quantization error displaces nearest-neighbor distances and how reranking to depth n recovers recall by re-scoring candidates with exact distances](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt78cc494d516dd35f/6a6119ed258cd202d9c16ec8/4c7a1499f27a3f9ed406e98565bdf8f9c6c7b823-900x506.gif)

Illustration of how quantizing and rerank affects recall

## Quantization error vs. the nearest-neighbor distance gap

Fix a query qqq and rank the database vectors by their true distance to it: R(1)≤R(2)≤…R\_{(1)} \le R\_{(2)} \le \dotsR(1)​≤R(2)​≤…, so R(i)R\_{(i)}R(i)​ is the distance to the iii-th nearest neighbor. Reranking the top nnn succeeds for the true kkk-th neighbor whenever it is not pushed past rank nnn by quantization noise.

Two competing quantities govern this:

* The quantization error that is essentially *fixed* for a given scheme and dataset: it depends on the embedding dimension, the vector distribution, and the number of bits, but not on how big the index is.
* The criticality gap Δk,n=R(n)−R(k)\Delta\_{k,n} = R\_{(n)} - R\_{(k)}Δk,n​=R(n)​−R(k)​, which is the distance between the kkk-th and the nnn-th nearest neighbor. This is the margin we have to absorb error. Crucially, it *shrinks as the index grows*: pack more vectors into the same region and neighbors crowd together.

There’s a detail here we’ll gloss over for the sake of presentation: for IVF style indices, we’re quantizing the residual from a cluster’s centroid. This does in fact couple the quantization error to the index size, but we can handle it much the same way we handle the distance to the iii-th nearest neighbor.

For reranking to recover the recall lost to quantization, we need the error to only rarely exceed the gap. If we can write down the distribution of Δk,n\Delta\_{k,n}Δk,n​ and the distribution of the error, we can make that statement quantitative. The first job is to estimate the distribution of nearest-neighbor distances.

## Deriving the nearest-neighbor distance distribution

Real embeddings don't fill their ambient space; they concentrate on a lower-dimensional [manifold](https://en.wikipedia.org/wiki/Manifold). Near a query, though, we can make a mild local assumption: in a small neighborhood Ω⊂Rd\Omega \subset \mathbb{R}^dΩ⊂Rd around the query, the data density is roughly uniform. Here ddd is the intrinsic dimension of the manifold; it is unknown and generally far smaller than the embedding dimension. How to estimate it is the subject of Section 4.

Let X={Xi}\mathcal{X} = \{X\_i\}X={Xi​} be the NNN vectors falling in Ω\OmegaΩ, modeled as [i.i.d.](https://en.wikipedia.org/wiki/Independent_and_identically_distributed_random_variables) uniform on Ω\OmegaΩ, and define the distance from qqq to its nearest neighbor:

R=min⁡Xi∈X∥Xi−q∥.R = \min\_{X\_i \in \mathcal{X}} \lVert X\_i - q \rVert\text{.}R=Xi​∈Xmin​∥Xi​−q∥.

To get the distribution of RRR we use the standard order-statistics trick: rather than ask where the minimum is, ask for the probability it exceeds some radius rrr. The event {R>r}\{R > r\}{R>r} is exactly the event that every point lands outside the ddd-ball centered on the query Br(q)B\_r(q)Br​(q).

A single point lands inside Br(q)B\_r(q)Br​(q) with probability equal to the ratio of the ball's volume to the region's volume VVV

P(Xi∈Br(q))=ωd rdV,ωd=πd/2Γ(d/2+1),(1)P(X\_i \in B\_r(q)) = \frac{\omega\_d\, r^d}{V}, \qquad \omega\_d = \frac{\pi^{d/2}}{\Gamma(d/2 + 1)}\text{,} \tag{1}P(Xi​∈Br​(q))=Vωd​rd​,ωd​=Γ(d/2+1)πd/2​,(1)

where ωd\omega\_dωd​ is the [volume](https://en.wikipedia.org/wiki/Volume_of_an_n-ball) of the unit ddd-ball. (We assume NNN is large enough that the relevant rrr is small, so the ball doesn't spill outside Ω\OmegaΩ and boundary effects are negligible.) Because the points positions are assumed to be independent, the [survival function](https://en.wikipedia.org/wiki/Survival_function) is

P(R>r)=(1−ωd rdV)N.(2)P(R > r) = \left(1 - \frac{\omega\_d\, r^d}{V}\right)^{N}\text{.} \tag{2}P(R>r)=(1−Vωd​rd​)N.(2)

What we're really interested in is how R behaves on average. To compute this, we use the identity that the expectation of a non-negative random variable is the integral of its survival function, E[R]=∫0∞P(R>r) dr\mathbb{E}[R] = \int\_0^\infty P(R > r)\, drE[R]=∫0∞​P(R>r)dr. Evaluating this with (2) gives the headline result:

E[R]≈(Vωd N)1/d  \boxed{\;\mathbb{E}[R] \approx \left(\frac{V}{\omega\_d\, N}\right)^{1/d}\;}E[R]≈(ωd​NV​)1/d​

(The exact integral carries an extra Γ(1+1/d)\Gamma(1 + 1/d)Γ(1+1/d) factor; it's an O(1)O(1)O(1) constant that we can fold into a fitted coefficient later, so we drop it here.)

### Glacial scaling: why neighbor distances barely change as your index grows

It is interesting to consider what this formula tells us about how distances change with dataset size: E[R]∝N−1/d\mathbb{E}[R] \propto N^{-1/d}E[R]∝N−1/d. The exponent is −1/d-1/d−1/d, and in high intrinsic dimensions that is a *very* small number. This is a property the method leans on, so it's worth plugging in some numbers:

* If d=2d = 2d=2 then doubling NNN multiplies E[R]\mathbb{E}[R]E[R] by 2−1/2≈0.7072^{-1/2} \approx 0.7072−1/2≈0.707, so distances drop by ~30%.
* If d=50d = 50d=50 then doubling NNN multiplies E[R]\mathbb{E}[R]E[R] by 2−1/50≈0.9862^{-1/50} \approx 0.9862−1/50≈0.986, so distances drop by a little over 1%.

In high dimensions, neighbor distances barely move even if you add a lot of data; call it glacial scaling**.** It's the reason we can choose quantization parameters *once* from a tiny sample, with a small safety margin, and trust them to remain valid even after the index grows substantially before the next re-quantization.

## Expected distance to the k-th neighbor and the criticality gap

We actually care about the whole sequence of order statistics R(k)R\_{(k)}R(k)​, R(n)R\_{(n)}R(n)​, not just the minimum. There's a simple way to get them.

Map each radius to the *cumulative volume* it encloses by defining

Ui=ωd RidV.U\_i = \frac{\omega\_d\, R\_i^d}{V}\text{.}Ui​=Vωd​Rid​​.

By (1), each UiU\_iUi​ is exactly the probability of landing within radius RiR\_iRi​, so the {Ui}\{U\_i\}{Ui​} are uniform on [0,1][0,1][0,1]. The order statistics of uniforms are [textbook](https://en.wikipedia.org/wiki/Order_statistic#Order_statistics_sampled_from_a_uniform_distribution): the iii-th smallest of NNN uniforms follows a Beta distribution,

U(i)∼Beta(i,N−i+1),E[U(i)]=iN+1.U\_{(i)} \sim \mathrm{Beta}(i, N - i + 1), \qquad \mathbb{E}[U\_{(i)}] = \frac{i}{N+1}\text{.}U(i)​∼Beta(i,N−i+1),E[U(i)​]=N+1i​.

Inverting the volume map, R(i)∝U(i)1/dR\_{(i)} \propto U\_{(i)}^{1/d}R(i)​∝U(i)1/d​, gives the scaling of the iii-th neighbor distance:

E[R(i)]∝(iN)1/d.\mathbb{E}[R\_{(i)}] \propto \left(\frac{i}{N}\right)^{1/d}\text{.}E[R(i)​]∝(Ni​)1/d.

That's all we need for the expected gap:

E[Δn,k]=E[R(n)]−E[R(k)]≈α((nN)1/d−(kN)1/d)=E[R(k)]((nk)1/d−1).\begin{align\*}
\mathbb{E}[\Delta\_{n,k}]
&= \mathbb{E}[R\_{(n)}] - \mathbb{E}[R\_{(k)}] \\
&\approx \alpha\left(\left(\tfrac{n}{N}\right)^{1/d} - \left(\tfrac{k}{N}\right)^{1/d}\right) \\
&= \mathbb{E}[R\_{(k)}]\left(\left(\tfrac{n}{k}\right)^{1/d} - 1\right)\text{.} \tag{3} \end{align\*}E[Δn,k​]​=E[R(n)​]−E[R(k)​]≈α((Nn​)1/d−(Nk​)1/d)=E[R(k)​]((kn​)1/d−1).​(3)​

The last form is the intuitive one: the gap between the kkk-th and nnn-th neighbors is the distance to the kkk-th neighbor, scaled by ((n/k)1/d−1)\big((n/k)^{1/d} - 1\big)((n/k)1/d−1). Widening the rerank depth nnn relative to kkk opens the gap; higher intrinsic dimension ddd closes it (the exponent 1/d1/d1/d pushes (n/k)1/d(n/k)^{1/d}(n/k)1/d toward 1).

### Why the expected gap is sufficient to predict recall

Working with an expectation is only legitimate if the gap doesn't fluctuate wildly around it. It doesn't because concentration of measure saves us. Applying the [delta method](https://en.wikipedia.org/wiki/Delta_method) to R(k)∝U(k)1/dR\_{(k)} \propto U\_{(k)}^{1/d}R(k)​∝U(k)1/d​ and using Var(U(k))≈k/N2\mathrm{Var}(U\_{(k)}) \approx k/N^2Var(U(k)​)≈k/N2 from the Beta distribution, a little algebra gives

Var(R(k))≈E[R(k)]2d2 k.\mathrm{Var}(R\_{(k)}) \approx \frac{\mathbb{E}[R\_{(k)}]^2}{d^2\, k}\text{.}Var(R(k)​)≈d2kE[R(k)​]2​.

So the [coefficient of variation](https://en.wikipedia.org/wiki/Coefficient_of_variation) is about 1dk\frac{1}{d\sqrt{k}}dk​1​. For any reasonable intrinsic dimension this is negligible, which justifies modeling only the expected distances. (If you're worried about the delta method approximation, you can check the results numerically: the delta-method variance and the resulting 1/(dk)1/(d\sqrt{k})1/(dk​) coefficient of variation match the exact expressions to several significant figures.)

### Extending the model to cosine similarity and inner product search

The derivation is for the Euclidean metric, but the other common metrics reduce to it:

* For cosine similarity, the equidistant surface is the intersection of a sphere around the query with the unit sphere. This is called a [hyperspherical cap](https://en.wikipedia.org/wiki/Spherical_cap), whose volume scales as sin⁡(θ)d−1≈θd−1\sin(\theta)^{d-1} \approx \theta^{d-1}sin(θ)d−1≈θd−1 for small θ\thetaθ. Therefore, the analysis carries over unchanged up to constants, with the dimension reduced by one.
* For MIPS (maximum inner product), some extra care is needed, because nearest neighbors aren't confined to a compact region. A distant vector can still win on inner product if its norm is large enough, so the gap is really governed by the tail of the norm distribution. However, there is a clean fix, which is to use the [Neyshabur–Srebro transformation](https://proceedings.mlr.press/v40/Neyshabur15.pdf). This lifts vectors onto a unit hypersphere in d+1d+1d+1 dimensions. After this operation, it's just the cosine case.

## Fitting intrinsic dimension and scale from a small sample

Equation (3) has a known functional form but two unknown parameters: the intrinsic dimension ddd and the scale α\alphaα. Both are easy to fit, and it's more convenient to fit them from raw neighbor distances than from gaps directly.

Sample several subsets of database vectors {Di}\{D\_i\}{Di​} of sizes Ni=∣Di∣N\_i = |D\_i|Ni​=∣Di​∣ and a set of query vectors QQQ. For each query q∈Qq\in Qq∈Q and each subset, measure ri,j(q)r\_{i,j}(q)ri,j​(q), the distance to the jjj-th nearest neighbor of qqq within DiD\_iDi​. Taking logs of the scaling law E[R(j)]≈α(j / Ni)1/d\mathbb{E}[R\_{(j)}] \approx \alpha (j\,/\,N\_i)^{1/d}E[R(j)​]≈α(j/Ni​)1/d linearises it:

log⁡(1∣Q∣∑q∈Qri,j(q))≈log⁡α+1d(log⁡j−log⁡(Ni/N0)).\log\left(\frac{1}{|Q|}\sum\_{q \in Q} r\_{i,j}(q)\right) \approx \log\alpha + \frac{1}{d}\Big(\log j - \log(N\_i/N\_0)\Big)\text{.}log​∣Q∣1​q∈Q∑​ri,j​(q)​≈logα+d1​(logj−log(Ni​/N0​)).

Specifically, this is linear in log⁡j\log jlogj and log⁡(Ni/N0)\log(N\_i/N\_0)log(Ni​/N0​), so ordinary least squares recovers α^\hat{\alpha}α^ and d^\hat{d}d^. Varying the subset size NiN\_iNi​ is what makes it possible to estimate ddd: it's precisely the rate at which distances shrink with data volume. With the fitted parameters, the whole-index expected gap is

E[Δn,k]≈α^(kN0N)1/d^((nk)1/d^−1).(4)\mathbb{E}[\Delta\_{n,k}] \approx \hat\alpha\left(\frac{kN\_0}{N}\right)^{1/\hat d}\left(\left(\frac{n}{k}\right)^{1/\hat d} - 1\right)\text{.} \tag{4}E[Δn,k​]≈α^(NkN0​​)1/d^((kn​)1/d^−1).(4)

Figure 1 shows how well this fits in practice (and it’s remarkably good): predicted versus actual average distance to the kkk-th neighbor, across a range of datasets and metrics, have R2R^2R2 between 0.996 and 0.999.

![Estimated vs actual nearest-neighbor distances across six datasets and metrics showing vector quantization distance model fit with R² between 0.996 and 0.999](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltdf3e51da370c7099/6a6119eef2e1c4515ffd2a24/325063c65304dfbc414d211065073f6d3334864d-1622x1256.png)

**Figure 1** Goodness of fit of the average distance to the k-th nearest neighbor estimates. Each panel is a different dataset/metric; points are (actual, estimated) mean distances.

## Modeling vector quantization error as Gaussian

With the nearest-neighbor distance model established, the second component is the quantization error distribution. For every metric we use, the quantized distance estimate differs from the true distance by an error that is a sum of many independent per-dimension contributions. By the [Central Limit Theorem](https://en.wikipedia.org/wiki/Central_limit_theorem) that sum tends to Gaussian, so we model the error as normal with a variance we estimate empirically:

σb2=1Z∑q∈Q∑i,j(ri,j(q)−r~i,j(q∣b))2,\sigma\_b^2 = \frac{1}{Z}\sum\_{q \in Q}\sum\_{i,j}\big(r\_{i,j}(q) - \tilde{r}\_{i,j}(q \mid b)\big)^2\text{,}σb2​=Z1​q∈Q∑​i,j∑​(ri,j​(q)−r~i,j​(q∣b))2,

where r~i,j(q∣b)\tilde{r}\_{i,j}(q \mid b)r~i,j​(q∣b) is the quantized distance estimate using bbb-bit vectors and ZZZ is the total number of (query, neighbor) pairs in our sample set. In other words: sample, quantize, measure the squared distance errors, average.

Figure 2 shows the empirical basis for the Gaussian assumption: measured quantization error densities against best-fit Gaussians across a variety of datasets. The fit is good, which is what lets the rest of the model stay analytic.

![Vector quantization error density histograms across six datasets at 1-bit precision with Gaussian fits overlaid, confirming the Central Limit Theorem prediction used in the recall model](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt596d6c8d2f751972/6a6119ef61ff792ec9cd608a/d48a34c93bac53a94a1b164b60362f631285c472-1614x1270.png)

**Figure 2** Quantization error density plots (query bits 1, doc bits 1) with the best-fit Gaussian overlaid. The near-Gaussian shape is what the CLT argument predicts.

We could stop here and take a [minimax](https://en.wikipedia.org/wiki/Minimax) view: threshold the probability that the kkk-th and nnn-th neighbors swap, using the expected gap (4) against the error scale σb\sigma\_bσb​. But that controls a worst-case event, and what we actually want to control is average recall. The outcome would be overly conservative quantization parameters and we'd pay some performance. The next section estimates expected recall properly.

## Predicting expected recall after reranking

Combining the distance model and the error model gives a closed-form estimate of expected recall after reranking. Model the *noisy* distance of the iii-th true neighbor as a Gaussian centered on its true distance:

Xi=N(R(i),σb).X\_i = \mathcal{N}\big(R\_{(i)}, \sigma\_b\big)\text{.}Xi​=N(R(i)​,σb​).

The iii-th neighbor survives reranking, i.e., lands in the retrieved top nnn, if fewer than nnn other vectors have a smaller noisy distance. Condition on Xi=xX\_i = xXi​=x and count the competitors closer than xxx:

S(x)=∑j≠i1(Xj<x).S(x) = \sum\_{j \ne i} \mathbf{1}(X\_j < x)\text{.}S(x)=j=i∑​1(Xj​<x).

Then the probability of recalling neighbor iii integrates over where its own noisy distance lands:

P(recall(i))=∫0∞P(S(x)<n) fXi(x) dx.P(\text{recall}(i)) = \int\_0^\infty P\big(S(x) < n\big)\, f\_{X\_i}(x)\, dx\text{.}P(recall(i))=∫0∞​P(S(x)<n)fXi​​(x)dx.

The terms of S(x)S(x)S(x) are independent Bernoullis but not identically distributed, since every neighbor jjj sits at a different true distance R(j)R\_{(j)}R(j)​, so each has its own probability of intruding on the top-kkk set:

pj(x)=P(Xj<x)=Φ ⁣(x−R(j)σb),(5)p\_j(x) = P(X\_j < x) = \Phi\!\left(\frac{x - R\_{(j)}}{\sigma\_b}\right)\text{,} \tag{5}pj​(x)=P(Xj​<x)=Φ(σb​x−R(j)​​),(5)

with Φ\PhiΦ the standard normal CDF. This makes S(x)S(x)S(x) a [Poisson-binomial](https://en.wikipedia.org/wiki/Poisson_binomial_distribution) variable. Since we sum many of them (because N≫nN \gg nN≫n), the Lyapunov CLT applies and we approximate

S(x)∼N(μS(x) ,σS2(x)),S(x) \sim \mathcal{N}\big(\mu\_S(x)\,, \sigma\_S^2(x)\big)\text{,}S(x)∼N(μS​(x),σS2​(x)),

with the standard Poisson-binomial moments

μS(x)=∑j≠ipj(x),σS2(x)=∑j≠ipj(x)(1−pj(x)).\mu\_S(x) = \sum\_{j \ne i} p\_j(x), \qquad \sigma\_S^2(x) = \sum\_{j \ne i} p\_j(x)\big(1 - p\_j(x)\big)\text{.}μS​(x)=j=i∑​pj​(x),σS2​(x)=j=i∑​pj​(x)(1−pj​(x)).

The survival probability then has a clean closed form:

P(S(x)<n)≈Φ ⁣(n−μS(x)σS(x)).P\big(S(x) < n\big) \approx \Phi\!\left(\frac{n - \mu\_S(x)}{\sigma\_S(x)}\right)\text{.}P(S(x)<n)≈Φ(σS​(x)n−μS​(x)​).

This is where the two halves of the post so far finally meet. We don't need to know the individual R(j)R\_{(j)}R(j)​ because the manifold scaling law from Section 3 supplies them: R(j)=α (jN0/N)1/dR\_{(j)} = \alpha\,(jN\_0/N)^{1/d}R(j)​=α(jN0​/N)1/d. So the moments become explicit sums over ranks, which we truncate at a safe cutoff (say 10n10n10n, since distant neighbors contribute negligibly):

μS(x)≈∑j=110nΦ ⁣(x−α(jN0/N)1/dσb),\mu\_S(x) \approx \sum\_{j=1}^{10n} \Phi\!\left(\frac{x - \alpha(jN\_0/N)^{1/d}}{\sigma\_b}\right)\text{,}μS​(x)≈j=1∑10n​Φ(σb​x−α(jN0​/N)1/d​),

σS2(x)≈μS(x)−∑j=110nΦ ⁣(x−α(jN0/N)1/dσb)2.\sigma\_S^2(x) \approx \mu\_S(x) - \sum\_{j=1}^{10n} \Phi\!\left(\frac{x - \alpha(jN\_0/N)^{1/d}}{\sigma\_b}\right)^{2}\text{.}σS2​(x)≈μS​(x)−j=1∑10n​Φ(σb​x−α(jN0​/N)1/d​)2.

Finally, average recall@kkk given rerank depth nnn sums the per-neighbor recall over the top kkk:

P(recall@k∣n)=∑i=1kP(recall(i)∣n)≈∑i=1k∫0∞Φ ⁣(n−μS(x)σS(x))ϕ ⁣(x−R(i)σb)dx.  \boxed{\;P(\text{recall}@k \mid n) = \sum\_{i=1}^{k} P(\text{recall}(i) \mid n) \approx \sum\_{i=1}^{k} \int\_0^\infty \Phi\!\left(\frac{n - \mu\_S(x)}{\sigma\_S(x)}\right)\phi\!\left(\frac{x - R\_{(i)}}{\sigma\_b}\right) dx.\;}P(recall@k∣n)=i=1∑k​P(recall(i)∣n)≈i=1∑k​∫0∞​Φ(σS​(x)n−μS​(x)​)ϕ(σb​x−R(i)​​)dx.​

Here ϕ\phiϕ is the standard normal density. Each integral is smooth and one-dimensional, so Gauss–Legendre quadrature evaluates it in microseconds. The entire recall prediction for a set of candidate parameters costs a handful of quadrature evaluations, not index build and benchmark run.

Figure 3 validates the end-to-end model: predicted average recall against measured recall across many parameter settings and multiple datasets has R2=0.982R^2 = 0.982R2=0.982.

![Predicted vs actual average vector quantization recall across four datasets with R² = 0.982, validating the end-to-end recall prediction model](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt16ee340b47ddffa8/6a6119ef1f595ca8d3fe72eb/2b6663f167a1f9f08558610c71ca538eef257cb5-1464x1442.png)

**Figure 3** Estimated versus actual average recall across a range of parameter settings and datasets. Points stay close to the ideal diagonal.

## How the recall model selects vector quantization parameters

With a fast recall predictor available, parameter selection becomes a cheap ordered search. Given a target recall and a rerank budget nnn (typically expressed as a multiple of kkk), we can find the *minimum* document and query bit counts, and other knobs, that clear the target. There are a few things to note that are practically important:

1. Glacial scaling gives us some safety because R(k)R\_{(k)}R(k)​ moves so slowly with NNN for even moderate intrinsic dimension. A small margin in the calculation means the chosen parameters stay valid if a lot of vectors are added before parameters are restimated.
2. Small kkk is the worst case if nnn is a fixed multiple of kkk. The gap \mathbb{E}[R\_{(k)}]((n/k)1/d−1)(n/k)^{1/d} - 1)(n/k)1/d−1) is smallest for small kkk so if a parameter choice satisfies the recall target at k=10k = 10k=10 then it will for larger kkk will too.
3. We can treat quantization as a black box because the error model only needs the empirical error variance. This means we can test *any* configuration, including preconditioning, the same way and we can simply order candidate parameter tuples by increasing index and query cost, and stop at the first choice that hits the target recall. For tuples of (query bits, doc bits, rerank depth, precondition) a sensible search sequence increases query precision first, then document precision (1,1)(1,1)(1,1), (2,1)(2,1)(2,1), (3,1)(3,1)(3,1), (4,1)(4,1)(4,1), (2,2)(2,2)(2,2), (3,3)(3,3)(3,3), (4,2)(4,2)(4,2), (4,4)(4,4)(4,4), (7,4)(7,4)(7,4) and (7,7)(7,7)(7,7) each combined (via an outer product ⊗\otimes⊗) with rerank depths like (1.5k, 2k, 3k)(1.5k,\,2k,\,3k)(1.5k,2k,3k) and precondition ∈{true, false}\in \{\text{true},\, \text{false}\}∈{true,false}, exiting as soon as the target is met.

### Results: auto-selected quantization parameters and recall across datasets

In this section, we discuss the results of the initial experiments on the end-to-end behavior. We’ve made some further refinements as part of the work to fully integrate with Elasticsearch that we discuss in our other post.

The table below shows auto-selected parameters targeting recall 0.97, measured with brute-force search, so the number reflects loss due to quantization *alone* (64 query clusters, targeting document clusters of size 384, which matches the settings of [DiskBBQ](https://www.elastic.co/search-labs/blog/diskbbq-elasticsearch-introduction)).

| Dataset | Query bits | Doc bits | Precondition | Depth | Recall |
| --- | --- | --- | --- | --- | --- |
| FiQA E5 small | 4 | 2 | false | 30 | 0.97 |
| FiQA arctic | 2 | 2 | false | 30 | 0.95 |
| FiQA GTE | 2 | 1 | true | 30 | 0.98 |
| MNIST | 3 | 1 | true | 30 | 0.99 |
| Fashion MNIST | 3 | 1 | true | 30 | 0.99 |
| Quora E5 small | 2 | 2 | false | 30 | 0.99 |
| Quora arctic | 2 | 1 | false | 30 | 0.97 |
| Quora GTE | 1 | 1 | false | 30 | 0.98 |
| Dbpedia E5 small | 4 | 2 | false | 30 | 0.99 |
| Dbpedia arctic | 2 | 1 | false | 30 | 0.94 |
| Dbpedia GTE | 2 | 1 | false | 30 | 0.96 |
| Wiki Cohere | 2 | 2 | false | 30 | 0.99 |
| Hotpot E5 small | 4 | 2 | false | 30 | 0.97 |
| Hotpot GTE | 2 | 1 | false | 30 | 0.96 |
| Glove 100 | 4 | 2 | false | 30 | 0.87 |
| Glove 200 | 4 | 2 | false | 30 | 0.89 |
| SIFT128 | 4 | 4 | false | 20 | 0.99 |

There are a few things worth highlighting:

* The recall is very sensitive to rerank depth. This is why we nearly always end up choosing the maximum depth available: a step up in rerank depth from 20 to 30 is typically what pushes us to hit the recall target for fewer bits and we prefer fewer bits. In the real system, we tuned this behavior based on a more representative reranking cost.
* Glove underperforms partly we approximate the query distribution with random samples from the corpus, but Glove is also less well characterized by the model than the other datasets. A plausible explanation is that the approximately uniform local density assumption from Section 2 is less reliable for Glove embeddings, which would show up as higher recall variance between queries. However, Glove embeddings are not representative of the actual vectors we need to store.
* The FiQA GTE preconditioning choice is a knife-edge case: preconditioning produced only a tiny expected recall improvement, but the prediction sat right at the recall cutoff and allows us to drop the query from 3 to 2 bits. If we'd rather only keep preconditioning where its benefit is clear-cut, we can enforce a minimum uplift threshold. This sort of fine-tuning of the decision logic leaves all the heavy lifting to estimate recall unaffected.

## Key takeaways: auto-tuning vector quantization from first principles

We presented a method to pick optimal quantization parameters to achieve a target recall. It rests on two models that compose cleanly:

1. A geometric model of neighbor distances that follows from a local uniform density assumption. We use this to derive the nearest-neighbor distance, the N−1/dN^{-1/d}N−1/d glacial scaling law of the expected distance, and the expected distance profile R(j)=α(jN0/N)1/dR\_{(j)} = \alpha(jN\_0/N)^{1/d}R(j)​=α(jN0​/N)1/d. We show that fitting α\alphaα and ddd by a simple log-linear regression to average distances in small random samples from the corpus gives an extremely accurate predictive model.
2. A Gaussian quantization error model that is justified by the CLT. Its only parameter σb\sigma\_bσb​ is an empirical variance we estimate by comparing quantized and raw vector similarities for a sample of the corpus.

Finally, we show that it is possible to feed the estimated distance model into a Poisson-binomial count of neighbors that intrude on the top-kkk set. Applying the Lyapunov CLT the expected recall@kkk after reranking to depth nnn falls out as a one-dimensional integral we evaluate by quadrature.

The outcome is an accurate (R2>0.95R^2>0.95R2>0.95) predictive model of recall as a function of the quantization parameters. Choosing quantization parameters then becomes an ordered search with a predictive model telling us if we’ve hit the recall constraint. And nicely one that also comes with a built-in argument (glacial scaling) for why the chosen parameters remain safe even when estimated from a relatively small fraction of the data.

We’ve built this entire mechanism into Elasticsearch using segment merges as an opportunity to reassess our quantization choices. Aside from the peace of mind this brings (that you’ll achieve good recall whatever vectors you throw at it), it also allows us to chose near optimal parameters from a performance perspective. This closes the loop on our original objective: near optimal performance out of the box, at least as far as quantization goes. We’re pretty excited about the advantages that model based tuning can bring to vector search and look forward to sharing other work we have in this direction in the near future.

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