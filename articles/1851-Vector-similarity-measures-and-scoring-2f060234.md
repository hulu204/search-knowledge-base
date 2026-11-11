---
title: 'Vector similarity measures and scoring'
company: Elastic
tag: 召回
date: 2024-05-13
url: https://www.elastic.co/search-labs/blog/vector-similarity-measures-and-scoring
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Vector similarity measures and scoring

Explore vector similarity measures​ and scoring in Elasticsearch, including L1 & L2 distance, cosine similarity, dot product similarity and max inner product similarity.

May 13, 2024

[Valentin Crettaz](/search-labs/author/valentin-crettaz)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

When the need for searching free text arises and Ctrl+F / Cmd+F don't cut it anymore, using a lexical search engine is usually the next logical choice that comes to mind. Lexical search engines excel at analyzing and tokenizing the text to be searched into terms that can be matched at search time, but they usually fall short when it comes to understanding and making sense of the true meaning of the text being indexed and searched.

That's exactly where vector search engines shine. They can index the same text in such a way that it can be searched based on both the meaning it represents and its relationships with other concepts having similar or related meaning.

In this blog, we will briefly touch upon how vectors are a great mathematical concept for conveying the meaning of text. We'll then dive deeper into the different similarity techniques supported by Elasticsearch when it comes to searching for neighboring vectors, i.e., searching for vectors carrying a similar meaning, and how to score them.

## What are vector embeddings?

This article doesn't delve deeply into the intricacies of vector embeddings. If you're looking to explore this topic further or need a primer before continuing, we recommend checking out the [following guide](https://www.elastic.co/what-is/vector-embedding).

In a nutshell, vector embeddings are obtained through a machine learning process (e.g. deep learning neural networks) that transforms any kind of unstructured input data (e.g., raw text, image, video, sound, etc.) into numerical data that carries their meaning and relationships. Different flavors of unstructured data require different kinds of machine learning models that have been trained to "understand" each type of data.

Each vector locates a specific piece of data as a point in a multidimensional space and that location represents a set of features the model uses to characterize the data. The number of dimensions depends on the machine learning model, but they usually range from a couple hundred to a few thousand. For instance, [OpenAI Embeddings models](https://platform.openai.com/docs/guides/embeddings) boasts 1536 dimensions, while [Cohere Embeddings models](https://docs.cohere.com/reference/embed) can range from 382 to 4096 dimensions. The Elasticsearch dense\_vector field type supports up to 4096 dimensions as of the latest release.

The true feat of vector embeddings is that data points that share similar meaning are close together in the space. Another interesting aspect is that vector embeddings also help capture relationships between data points.

## How do we compare vectors?

Knowing that unstructured data is sliced and diced by machine learning models into vector embeddings that capture the similarity of the data along a high number of dimensions, we now need to understand how the matching of those vectors works. It turns out that the answer is pretty simple.

Vector embeddings that are **close** to one another represent **semantically similar** pieces of data. So, when we query a vector database, the search input (image, text, etc.) is first turned into a vector embeddings using the same machine learning model that has been used for indexing all the unstructured data, and the ultimate goal is to find the **nearest neighboring vectors** to that query vector. Hence, all we need to do is figure out how to measure the "distance" or "similarity" between the query vector and all the existing vectors indexed in the database - it's that simple.

## Distance, similarity and scoring

Luckily for us, measuring the distance or similarity between two vectors is an easy problem to solve thanks to vector arithmetics. So, let’s look at the most popular distance and similarity functions that are supported by Elasticsearch. Warning, math ahead!

Just before we dive in, let's have a quick look at scoring. Factually, Lucene only allows scores to be positive. All the distance and similarity functions that we will introduce shortly yield a measure of how close or similar two vectors are, but those raw figures are rarely fit to be used as score since they can be negative. For this reason, the final score needs to be derived from the distance or similarity value in a way that ensures the score will be positive and a bigger score corresponds to a higher ranking (i.e. to closer vectors).

### L1 distance

The L1 distance, also called the Manhattan distance, of two vectors A⃗\vec{A}A and B⃗\vec{B}B is measured by summing up the pairwise absolute difference of all their elements. Obviously, the smaller the distance δL1\delta\_{L1}δL1​, the closer the two vectors are. The L1 distance formula (1) is pretty simple, as can be seen below:

δL1(A⃗,B⃗)=∑1≤i≤n∣Ai−Bi∣(1)\tag{1} \delta\_{L1}(\vec{A}, \vec{B}) = \sum\_{\mathclap{1\le i\le n}} \vert A\_i-B\_i \vert
δL1​(A,B)=1≤i≤n∑​∣Ai​−Bi​∣(1)

Visually, the L1 distance can be illustrated as shown in the image below (in red):

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta70afeb37125efa6/6a17da22a292996c47d02b3a/4ab1150149833536fec8e223bcf9be3c3b5d6236-793x708.png)

Computing the L1 distance of the following two vectors A⃗=(12)\vec{A} = \binom{1}{2}A=(21​) and B⃗=(20.5)\vec{B} = \binom{2}{0.5}B=(0.52​) would yield ∣1–2∣+∣2–0.5∣=2.5\vert 1–2 \vert + \vert 2–0.5 \vert = 2.5∣1–2∣+∣2–0.5∣=2.5

**Important:** It is worth noting that the L1 distance function is only supported for [exact vector search](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-script-score-query.html#vector-functions-l1) (aka brute force search) using the `script_score` DSL query, but not for [approximate kNN search](https://www.elastic.co/guide/en/elasticsearch/reference/8.11/dense-vector.html#dense-vector-params) using the [`knn`](https://www.elastic.co/guide/en/elasticsearch/reference/8.11/knn-search.html#approximate-knn) [search option](https://www.elastic.co/guide/en/elasticsearch/reference/8.11/knn-search.html#approximate-knn) or [`knn`](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-knn-query.html) [DSL query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-knn-query.html).

### L2 distance

The L2 distance, also called the Euclidean distance, of two vectors A⃗\vec{A}A and B⃗\vec{B}B is measured by first summing up the square of the pairwise difference of all their elements and then taking the square root of the result. It’s basically the shortest path between two points. Similarly to L1, the smaller the distance δL2\delta\_{L2}δL2​, the closer the two vectors are:

δL2(A⃗,B⃗)=∑1≤i≤n(Ai−Bi)2(2)\tag{2} \delta\_{L2}(\vec{A},\vec{B}) = \sqrt{\sum\_{\mathclap{1\le i\le n}} ( A\_i-B\_i )^2 }
δL2​(A,B)=1≤i≤n∑​(Ai​−Bi​)2​(2)

The L2 distance is shown in red in the image below:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt37a371765a9838a8/6a17da24fbc5f8076f49195b/c41136c8ff5d2b32fefd2a74f80fc3fdcc5493fc-791x702.png)

Let’s reuse the same two sample vectors A⃗\vec{A}A and B⃗\vec{B}B as we used for the δL1\delta\_{L1}δL1​ distance, and we can now compute the δL2\delta\_{L2}δL2​ distance as (1−2)2+(2−0.5)2=3.25≊1.803\sqrt{(1-2)^2 + (2-0.5)^2} = \sqrt{3.25} \approxeq 1.803(1−2)2+(2−0.5)2​=3.25​≊1.803.

As far as scoring goes, the smaller the distance between two vectors, the closer (i.e., the more similar) they are. So in order to derive a score we need to invert the distance measure, so that the smallest distance yields the highest score. The way the score is computed when using the L2 distance looks as shown in formula (3) below:

\_scoreL2(A⃗,B⃗)=11+δL2(A⃗,B⃗)2(3)\tag{3} \\_score\_{L2}(\vec{A},\vec{B}) = \frac{1}{1 + \delta\_{L2}(\vec{A}, \vec{B})^2}
\_scoreL2​(A,B)=1+δL2​(A,B)21​(3)

Reusing the sample vectors from the earlier example, their score would be 14.25≊0.2352\frac{1}{4.25} \approxeq 0.23524.251​≊0.2352. Two vectors that are very close to one another will near a score of 1, while the score of two vectors that are very far from one another will tend towards 0.

Wrapping up on L1 and L2 distance functions, a good analogy to compare them is to think about A and B as being two buildings in Manhattan, NYC. A taxi going from A to B would have to drive along the L1 path (streets and avenues), while a bird would probably use the L2 path (straight line).

### Cosine similarity

In contrast to L1 and L2, cosine similarity does not measure the distance between two vectors A⃗\vec{A}A and B⃗\vec{B}B, but rather their relative angle, i.e., whether they are both pointing in roughly the same direction. The higher the similarity scoss\_{cos}scos​, the smaller the angle α\alphaα between the two vectors, and hence, the "closer" they are and the "similar" their conveyed meaning are.

To illustrate this, let's think of two people out in the wild looking in different directions. In the figure below, the person in blue looks in the direction symbolized by vector A⃗\vec{A}A and the person in red in the direction of vector B⃗\vec{B}B. The more they will direct their eyesight towards the same direction (i.e., the closer their vectors get), the more their field of view symbolized by the blue and red areas will overlap. How much their field of view overlap is their cosine similarity. However, note that person B looks farther away than person A (i.e., vector B⃗\vec{B}B is longer). Person B might be looking at a mountain far away on the horizon, while person A could be looking at a nearby tree. For cosine similarity, that doesn't play any role as it is only about the angle.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte8421ab6607edf0c/6a17da25e8fbce01b53a17cb/cca8547aa9a92337dccae36c55bfbe01b43a8156-492x502.png)

Now let's compute that cosine similarity. The formula (4) is pretty simple, where the numerator consists of the dot product of both vectors and the denominator contains the product of their magnitude (i.e., their length):

scos(A⃗,B⃗)=A⃗⋅B⃗∥A⃗∥×∥B⃗∥(4)\tag{4} s\_{cos}(\vec{A}, \vec{B}) = \frac{\vec{A} \cdot \vec{B}}{\Vert \vec{A} \Vert \times \Vert \vec{B} \Vert}
scos​(A,B)=∥A∥×∥B∥A⋅B​(4)

The cosine similarity between A⃗\vec{A}A and B⃗\vec{B}B is shown in the image below as a measure of the angle between them (in red):

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt4f38d9c13a7c5765/6a17da274b055d695a432096/a546d34d843b8b117db495d4e0e6d820f7091162-791x707.png)

Let's take a quick detour in order to explain what these cosine similarity values mean concretely. As can be seen in the image below depicting the cosine function, values always oscillate in the [−1,1][-1, 1][−1,1] interval.

![cos-function](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc0e4eb98ebb64cf3/6a17da287b54f983818b3783/e31145284b8c27d0bd9e3d2831f811388134fd83-1188x272.png)

Remember that in order for two vectors to be considered similar, their angle must be as acute as possible, ideally nearing a 0°0°0° angle, which would boil down to a perfect similarity of 111. In other words, when vectors are...

1. ...**close** to one another, the cosine of their angle nears 111 (i.e., close to 0°0°0°)

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7a339cd060372477/6a17da2a14800966ebb4860c/5d964818b3a36521bc99ce649b6368a0b558ae38-896x440.png)

1. ...**unrelated**, the cosine of their angle nears 000 (i.e., close to 90°90°90°)

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt2109afacbe5857d3/6a17da2b63baff63ec741b0c/72df4d9c2ac93e8c3c23d7b1b3f6c0eb091a8cec-898x438.png)

1. ...**opposite**, the cosine of their angle nears −1-1−1 (i.e., close to 180°180°180°)

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltdadacd148bd11b00/6a17da2dec0f89d2d45a64b9/9784dd9a617139742d44a56cbb0ade60a827d5cb-898x438.png)

Now that we know how to compute the cosine similarity between two vectors and we have a good idea of how to interpret the resulting value, we can reuse the same sample vectors A⃗\vec{A}A and B⃗\vec{B}B and compute their cosine similarity using the formula (4) we saw earlier.

scos(A⃗,B⃗)=(1⋅2)+(2⋅0.5)(12+22)×(22+0.52)≊34.609≊0.650791s\_{cos}(\vec{A}, \vec{B}) = \frac{(1 \cdot 2) + (2 \cdot 0.5)}{\sqrt{(1^2 + 2^2)} \times \sqrt{(2^2 + 0.5^2)}} \approxeq \frac{3}{4.609} \approxeq 0.650791
scos​(A,B)=(12+22)​×(22+0.52)​(1⋅2)+(2⋅0.5)​≊4.6093​≊0.650791

We get a cosine similarity of 0.6507910.6507910.650791, which is closer to 111 than to 000, meaning that the two vectors are **somewhat similar**, i.e., not perfectly similar, but not completely unrelated either, and certainly do not carry opposite meaning.

In order to derive a positive score from any cosine similarity value, we need to use the following formula (5), which transforms cosine similarity values oscillating within the [−1,1][-1, 1][−1,1] interval into scores in the [0,1][0, 1][0,1] interval:

\_scorecos(A⃗,B⃗)=1+scos(A⃗,B⃗)2(5)\tag{5} \\_score\_{cos}(\vec{A},\vec{B}) = \frac{1 + s\_{cos}(\vec{A}, \vec{B})}{2}
\_scorecos​(A,B)=21+scos​(A,B)​(5)

The score for the sample vectors A⃗\vec{A}A and B⃗\vec{B}B would thus be: 1+0.6507912≊0.8253\frac{1 + 0.650791}{2} \approxeq 0.825321+0.650791​≊0.8253.

### Dot product similarity

One drawback of cosine similarity is that it only takes into account the angle between two vectors but not their magnitude, which means that if two vectors point roughly in the same direction but one is much longer than the other, both will still be considered similar. Dot product similarity, also called scalar or inner product similarity, improves that by taking into account both the angle and the magnitude of the vectors, which provides for a more accurate similarity metric. In order to make the magnitude of the vectors irrelevant, dot product similarity requires that the vectors be normalized first, so we are ultimately only comparing vectors of unit length 1.

Let's try to illustrate this again with the same two people as before, but this time, we put them in the middle of a circular room, so that their sight reach is exactly the same (i.e., the radius of the room). Similarly to cosine similarity, the more they turn towards the same direction (i.e., the closer their vectors get), the more their field of view will overlap. However, in contrary to cosine similarity, both vectors have the same length and both areas have the same surface, which means that the two people look at exactly the same picture located at the same distance. How well those two areas overlap denotes their dot product similarity.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt37ba6732aa34c169/6a17da2e4b055de9a443209a/b3a0535065e0c765625e7311fd8415dc836d2d4a-390x408.png)

Before introducing the dot product similarity formula, let's quickly see how a vector can be normalized. It's pretty simple and can be done in two trivial steps:

1. compute the magnitude of the vector
2. divide each component by the magnitude obtained in 1.

As an example, let's take vector A⃗=(12)\vec{A} = \binom{1}{2}A=(21​). We can compute its magnitude ∥A⃗∥\Vert \vec{A} \Vert∥A∥ as we have seen earlier when reviewing the cosine similarity, i.e. 12+22=5\sqrt{1^2 + 2^2} = \sqrt{5}12+22​=5​. Then, dividing each component of the vector by its magnitude, we obtain the following normalized vector C⃗\vec{C}C:

Anorm⃗=C⃗=(1525)≊(0.440.89)\vec{A\_{norm}} = \vec{C} = \dbinom{\frac{1}{\sqrt{5}}}{\frac{2}{\sqrt{5}}} \approxeq \dbinom{0.44}{0.89}
Anorm​​=C=(5​2​5​1​​)≊(0.890.44​)

Going through the same process for the second vector B⃗=(20.5)\vec{B} = \binom{2}{0.5}B=(0.52​) would yield the following normalized vector D⃗\vec{D}D:

Bnorm⃗=D⃗=(24.250.54.25)≊(0.970.24)\vec{B\_{norm}} = \vec{D} = \dbinom{\frac{2}{\sqrt{4.25}}}{\frac{0.5}{\sqrt{4.25}}} \approxeq \dbinom{0.97}{0.24}
Bnorm​​=D=(4.25​0.5​4.25​2​​)≊(0.240.97​)

In order to derive the dot product similarity formula, we can compute the cosine similarity between our normalized vectors C⃗\vec{C}C and D⃗\vec{D}D using formula (4), as shown below:

scos(C⃗,D⃗)=C⃗⋅D⃗1×1s\_{cos}(\vec{C}, \vec{D}) = \frac{\vec{C} \cdot \vec{D}}{1 \times 1}
scos​(C,D)=1×1C⋅D​

And since the magnitude of both normalized vectors is now 111, the dot product similarity formula (6) simply becomes... you guessed it, a dot product of both normalized vectors:

sdot(C⃗,D⃗)=C⃗⋅D⃗(6)\tag{6} s\_{dot}(\vec{C}, \vec{D}) = \vec{C} \cdot \vec{D}
sdot​(C,D)=C⋅D(6)

In the image below, we show the normalized vectors C⃗\vec{C}C and D⃗\vec{D}D and we can illustrate their dot product similarity as the projection of one vector onto the other (in red).

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltba180cfa5518cfc7/6a17da3057726276721bcac9/a53045fcf6145f8923aac52c0db87b8f0524f173-800x712.png)

Using our new formula (6), we can compute the dot product similarity of our two normalized vectors, which unsurprisingly yields the exact same similarity value as the cosine one:

sdot(C⃗,D⃗)=(15⋅24.25)+(25⋅0.54.25)≊0.650791s\_{dot}(\vec{C}, \vec{D}) = \Big(\frac{1}{\sqrt{5}} \cdot \frac{2}{\sqrt{4.25}}\Big) + \Big(\frac{2}{\sqrt{5}} \cdot \frac{0.5}{\sqrt{4.25}}\Big) \approxeq 0.650791
sdot​(C,D)=(5​1​⋅4.25​2​)+(5​2​⋅4.25​0.5​)≊0.650791

When leveraging dot product similarity, the score is computed differently depending on whether the vectors contain float or byte values. In the former case, the score is computed the same way as for cosine similarity using formula (7) below:

\_scoredot−float(C⃗,D⃗)=1+sdot(C⃗,D⃗)2(7)\tag{7} \\_score\_{dot-float}(\vec{C},\vec{D}) = \frac{1 + s\_{dot}(\vec{C}, \vec{D})}{2}
\_scoredot−float​(C,D)=21+sdot​(C,D)​(7)

However, when the vector is composed of byte values, the scoring is computed a bit differently as shown in formula (8) below, where dimsdimsdims is the number of dimensions of the vector:

\_scoredot−byte(C⃗,D⃗)=0.5+sdot(C⃗,D⃗)32768×dims(8)\tag{8} \\_score\_{dot-byte}(\vec{C},\vec{D}) = \frac{0.5 + s\_{dot}(\vec{C}, \vec{D})}{32768 \times dims}
\_scoredot−byte​(C,D)=32768×dims0.5+sdot​(C,D)​(8)

Also, one constraint in order to yield accurate scores is that all vectors, including the query vector, must have the same length, but not necessarily 1.

### Max inner product similarity

Since release 8.11, there is a new similarity function that is less constrained than the dot product similarity, in that the vectors don't need to be normalized. The main reason for this is explained at length in the [following article](https://www.elastic.co/search-labs/blog/lucene-bringing-maximum-inner-product-to-lucene), but to sum it up very briefly, certain datasets are not very well adapted to having their vectors normalized (e.g., [Cohere embeddings](https://www.elastic.co/search-labs/blog/elasticsearch-cohere-embeddings-support)) and doing so can cause relevancy issues.

The formula for computing max inner product similarity is exactly the same as the dot product one (6). What changes is the way the score is computed by scaling the max inner product similarity using a piecewise function whose formula depends on whether the similarity is positive or negative, as shown in formula (9) below:

\_scoremip(A⃗,B⃗)={11−sdot(A⃗,B⃗)if sdot<01+sdot(A⃗,B⃗)if sdot⩾0(9)\tag{9}
\\_score\_{mip}(\vec{A},\vec{B}) = \begin{cases}
\Large \frac{1}{1 - s\_{dot}(\vec{A}, \vec{B})} &\text{if } s\_{dot} < 0 \\
1 + s\_{dot}(\vec{A}, \vec{B}) &\text{if } s\_{dot} \geqslant 0
\end{cases}
\_scoremip​(A,B)=⎩⎨⎧​1−sdot​(A,B)1​1+sdot​(A,B)​if sdot​<0if sdot​⩾0​(9)

What this piecewise function does is that it scales all negative max inner product similarity values in the [0,1[[0, 1[[0,1[ interval and all positive values in the [1,∞[[1, \infty[[1,∞[ interval.

## In summary

That was quite a ride, mathematically speaking, but here are a few takeaways that you might find useful.

Which similarity function you can use, ultimately depends on whether your vector embeddings are normalized or not. If your vectors are already normalized or if your data set is agnostic to vector normalization (i.e., relevancy will not suffer), you can go ahead and normalize your vectors and use dot product similarity, as it is much faster to compute than the cosine one since there is no need to compute the length of each vector. When comparing millions of vectors, those computations can add up quite a lot.

If your vectors are not normalized, then you have two options:

1. use cosine similarity if normalizing your vectors is not an option
2. use the new max inner product similarity if you want the magnitude of your vectors to contribute to scoring because they do carry meaning (e.g., Cohere embeddings)

At this point, computing the distance or similarity between vector embeddings and how to derive their scores should make sense to you. We hope you found this article useful.

### Frequently Asked Questions

#### What does cosine similarity measure?

Cosine similarity measures the relative angle between two vectors i.e., whether they are both pointing in roughly the same direction.

#### How is the L1 distance measured?

L1 distance is measured by summing up the pairwise absolute difference of all their elements.

#### How is the L2 distance measured?

The L2 distance, also called the Euclidean distance, of two vectors is measured by first summing up the square of the pairwise difference of all their elements and then taking the square root of the result.

#### What is the difference between L1 and L2 distance?

The difference between L1 and L2 distance comes down to how you measure of two vectors. L1 distance is measured by summing up the pairwise absolute difference of all their elements. On the other hand, L2 distance is measured by first summing up the square of the pairwise difference of all their elements and then taking the square root of the result.

#### What is the difference between cosine similarity and cosine distance?

Cosine similarity measures the relative angle of two vectors, i.e., whether they are both pointing in roughly the same direction. On the other hand, cosine distance measures how different their directions are.

#### What is the difference between dot product and cosine similarity?

Dot product measures both length and alignment of vectors, while cosine similarity measures only how aligned their directions are, ignoring length.

#### When should you use dot product vs. cosine similarity?

If f your vectors are normalized (or can be normalized without affecting relevance), use dot product similarity — it’s faster because you don’t need to compute vector lengths. If your vectors are not normalized, use cosine similarity when you only care about direction, or dot product if vector magnitude carries meaning and should influence the score.

#### How do you chose the right distance metric for vector search?

Choose a distance metric based on your vectors and what matters for your search: use L1 or L2 to measure absolute differences, cosine similarity if only direction matters, dot product if both direction and magnitude matter (and vectors are normalized), or max inner product if vectors are unnormalized but magnitude should influence relevance.

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