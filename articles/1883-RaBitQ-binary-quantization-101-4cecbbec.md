---
title: 'RaBitQ binary quantization 101'
company: Elastic
tag: 索引构建
date: 2024-10-22
url: https://www.elastic.co/search-labs/blog/rabitq-explainer-101
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# RaBitQ binary quantization 101

Understand the most critical components of RaBitQ binary quantization, how it works and its benefits. This guide also covers the math behind the quantization and examples.

October 22, 2024

[John Wagster](/search-labs/author/john-wagster)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

Jump to

Share

## Introduction

As we have discussed previously in [Scalar Quantization 101](https://www.elastic.co/search-labs/blog/scalar-quantization-101) most embedding models output float32float32float32 vector values, which is often excessive to represent the vector space. Scalar quantization techniques greatly reduce the space needed to represent these vectors. We've also previously talked about [Bit Vectors In Elasticsearch](https://www.elastic.co/search-labs/blog/bit-vectors-in-elasticsearch) and how binary quantization can often be unacceptably lossy.

With binary quantization techniques such as those presented in the [RaBitQ paper](https://arxiv.org/pdf/2405.12497) we can address the problems associated with naively quantizing into a bit vector and maintain the quality associated with scalar quantization by more thoughtfully subdividing the space and retaining residuals of the transformation. These newer techniques allow for better optimizations and generally better results over other similar techniques like [product quantization (PQ)](http://hal.archives-ouvertes.fr/docs/00/51/44/62/PDF/paper_hal.pdf) in distance calculations and a 32x level of compression that typically is not possible with scalar quantization.

Here we'll walk through some of the core aspects of binary quantization and leave the mathematical details to the [RaBitQ paper](https://arxiv.org/pdf/2405.12497).

## Building the Bit Vectors

Because we can more efficiently pre-compute some aspects of the distance computation, we treat the indexing and query construction separately.

To start with let's walk through indexing three very simple 2 dimensional vectors, v1v\_1v1​, v2v\_2v2​, and v3v\_3v3​, to see how they are transformed and stored for efficient distance computations at query time.

v1=[0.56,0.82]v\_1 = [0.56, 0.82]v1​=[0.56,0.82]

v2=[1.23,0.71]v\_2 = [1.23, 0.71]v2​=[1.23,0.71]

v3=[-3.28,2.13]v\_3 = [\text{-}3.28, 2.13]v3​=[-3.28,2.13]

Our objective is to transform these vectors into much smaller representations that allow:

* A reasonable proxy for estimating distance rapidly
* Some guarantees about how vectors are distributed in the space for better control over the total number of data vectors needed to recall the true nearest neighbors

We can achieve this by:

* Shifting each vector to within a hyper-sphere, in our case a 2d circle, the unit circle
* Snapping each vector to a single representative point within each region of the circle
* Retaining corrective factors to better approximate the distance between each vector and the query vector

Let's unpack that step by step.

### Find a Representative Centroid

In order to partition each dimension we need to pick a pivot point. For simplicity, we'll select one point to use to transform all of our data vectors.

Let's continue with our vectors, v1v\_1v1​, v2v\_2v2​, and v3v\_3v3​. We pick their [centroid](https://en.wikipedia.org/wiki/Centroid) as the pivot point.

v1=[0.56,0.82]v2=[1.23,0.71]v3=[-3.28,2.13] c=[(0.56+1.23+-3.28)/3,(0.82+0.71+2.13)/3] c=[-0.49,1.22]v\_1 = [0.56, 0.82]
\newline
v\_2 = [1.23, 0.71]
\newline
v\_3 = [\text{-}3.28, 2.13]
\newline
~\\
c = [(0.56 + 1.23 + \text{-}3.28) / 3, (0.82 + 0.71 + 2.13) / 3]
\newline
~\\
c = [\text{-}0.49, 1.22]v1​=[0.56,0.82]v2​=[1.23,0.71]v3​=[-3.28,2.13] c=[(0.56+1.23+-3.28)/3,(0.82+0.71+2.13)/3] c=[-0.49,1.22]

Here's all of those points graphed together:

![2D Three Vectors with Centroid Illustration](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt667e3369a777fca4/6a17e5d5dbb4ff5868fb568c/5c1636541a2ae86307c00e726fe481320555641b-1440x1362.jpg)

Figure 1: graph of the example vectors and the derived centroid of those three vectors.

Each residual vector is then [normalized](https://en.wikipedia.org/wiki/Unit_vector). We'll call these vc1v\_{c1}vc1​, vc2v\_{c2}vc2​, and vc3v\_{c3}vc3​.

vc1=(v1−c)/∥v1−c∥vc2=(v2−c)/∥v2−c∥vc3=(v3−c)/∥v3−c∥v\_{c1} = (v\_1 - c) / \|v\_1 - c\|
\newline
v\_{c2} = (v\_2 - c) / \|v\_2 - c\|
\newline
v\_{c3} = (v\_3 - c) / \|v\_3 - c\|
\newlinevc1​=(v1​−c)/∥v1​−c∥vc2​=(v2​−c)/∥v2​−c∥vc3​=(v3​−c)/∥v3​−c∥

Let's do the math for one of the vectors together:

vc1=(v1−c)/∥v1−c∥ v1−c=[0.56,0.82]−[-0.49,1.22]=[1.05,-0.39] ∥v1−c∥=1.13 vc1=(v1−c)/∥v1−c∥=([1.05,-0.39])/∥[1.05,-0.39]∥=([1.05,-0.39])/1.13=[0.94,-0.35]v\_{c1} = (v\_1 - c) / \|v\_1 - c\|
\newline
~\\
\begin{align\*}
v\_1 - c &= [0.56, 0.82] - [\text{-}0.49, 1.22]
\newline
&= [1.05, \text{-}0.39]
\end{align\*}
\newline
~\\
\|v\_1 - c\| = 1.13
\newline
~\\
\begin{align\*}
v\_{c1} &= (v\_1 - c) / \|v\_1 - c\|
\newline
&= ([1.05, \text{-}0.39]) / \|[1.05, \text{-}0.39]\|
\newline
&= ([1.05, \text{-}0.39]) / 1.13
\newline
&= [0.94, \text{-}0.35]
\end{align\*}
\newlinevc1​=(v1​−c)/∥v1​−c∥ v1​−c​=[0.56,0.82]−[-0.49,1.22]=[1.05,-0.39]​ ∥v1​−c∥=1.13 vc1​​=(v1​−c)/∥v1​−c∥=([1.05,-0.39])/∥[1.05,-0.39]∥=([1.05,-0.39])/1.13=[0.94,-0.35]​

And for each of the remaining vectors:

vc2=[0.96,-0.28]vc3=[-0.95,0.31]v\_{c2} = [0.96, \text{-}0.28]
\newline
v\_{c3} = [\text{-}0.95, 0.31]vc2​=[0.96,-0.28]vc3​=[-0.95,0.31]

Let's see that transformation and normalization all together:

![2D Three Vectors with Centroid Transformed to Unit Circle Illustration](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt14c222dfe7df8038/6a17e5d82f4a5cdd18fa889e/ea368e14e59f32cca3db3abfe6d01f3645199dc1-854x480.gif)

Figure 2: Animation of the example vectors and the derived centroid transformed within the unit circle.

As you may be able to see our points now sit on the unit circle around the centroid as if we had placed the centroid at 0,0.

### 1 Bit, 1 Bit Only Please

With our data vectors centered and normalized, we can apply standard [binary quantization](https://www.elastic.co/search-labs/blog/bit-vectors-in-elasticsearch) encoding each transformed vector component with a 0 if it is negative and 1 if it is positive. In our 2 dimensional example this splits our unit circle into four quadrants and the binary vectors corresponding to v1cv\_{1c}v1c​, vc2v\_{c2}vc2​, and vc3v\_{c3}vc3​ become r1=[1,0],r2=[1,0],r3=[0,1]r\_1 = [1, 0], r\_2 = [1, 0], r\_3 = [0, 1]r1​=[1,0],r2​=[1,0],r3​=[0,1], respectively.

We finish quantizing each data vector by snapping it to a representative point within each region specifically picking a point equidistant from each axis on the unit circle: ±1d\pm \frac{1}{\sqrt{d}}±d​1​

We'll denote each quantized vector as v‾1\overline{v}\_1v1​, v‾2\overline{v}\_2v2​, and v‾3\overline{v}\_3v3​.

So for instance if we snap vc1v\_{c1}vc1​ to its representative point within its region r1r\_1 r1​we get:

v‾1=1d(2r1−1)=12[1,−1]=[12,−12]\begin{align\*}
\overline{v}\_1 &= \frac{1}{\sqrt{d}} (2 r\_1 - 1)
\newline
&= \frac{1}{\sqrt{2}} [1, -1]
\newline
&= [\frac{1}{\sqrt{2}}, -\frac{1}{\sqrt{2}}]
\end{align\*}v1​​=d​1​(2r1​−1)=2​1​[1,−1]=[2​1​,−2​1​]​

And here are the quantized forms for the other data vectors, v2v\_2v2​ and v3v\_3v3​:

v‾2=[12,−12]v‾3=[−12,12]\overline{v}\_2 = [\frac{1}{\sqrt{2}}, -\frac{1}{\sqrt{2}}]
\newline
\overline{v}\_3 = [-\frac{1}{\sqrt{2}}, \frac{1}{\sqrt{2}}]v2​=[2​1​,−2​1​]v3​=[−2​1​,2​1​]

Picking these representative points has some nice mathematical properties as outlined in the [RaBitQ paper](https://arxiv.org/pdf/2405.12497). And are not unlike the codebooks seen in [product quantization (PQ)](http://hal.archives-ouvertes.fr/docs/00/51/44/62/PDF/paper_hal.pdf).

![Binary Quantization of 2D Three Vectors Illustration](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt03d88f7d3ed35e03/6a17e5d93e9e454c5cba1448/3d69b2f781385558edea55ddbf50b853c3cfecc8-854x480.gif)

Figure 3: Binary quantized vectors within a region snapped to representative points.

At this point we now have a 1 bit approximation; albeit a somewhat fuzzy one that we can use to do distance comparisons. Clearly, v‾1\overline{v}\_1v1​ and v‾2\overline{v}\_2 v2​are now identical in this quantized state, which is not ideal and is a similar problem experienced when we discussed encoding float vectors as [Bit Vectors In Elasticsearch.](https://www.elastic.co/search-labs/blog/bit-vectors-in-elasticsearch)

The elegance of this is that at query time we can use something akin to a dot product to compare each data vector and each query vector rapidly for an approximation of distance. We'll see that in more detail when we discuss handling the query.

### The Catch

As we saw above, a lot of information is lost when converting to bit vectors. We'll need some additional information to help compensate for the loss and correct our distance estimations.

In order to recover fidelity we'll store the distance from each vector to the centroid and the projection (dot product) of the vector (e.g vc1v\_{c1}vc1​) with its quantized form (e.g. v1‾\overline{v\_1}v1​​) as two float32float32float32 values.

The [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance) to the centroid is straight-forward and we already computed it when quantizing each vector:

∥v1−c∥=1.13∥v2−c∥=1.79∥v3−c∥=2.92\|v\_1 - c\| = 1.13
\newline
\|v\_2 - c\| = 1.79
\newline
\|v\_3 - c\| = 2.92∥v1​−c∥=1.13∥v2​−c∥=1.79∥v3​−c∥=2.92

Precomputing distances from each data vector to the centroid restores the transformation of centering the vectors. Similarly, we'll compute the distance from the query to the centroid. Intuitively the centroid acts as a go-between instead of directly computing the distance between the query and data vector.

The dot product of the vector and the quantized vector is then:

vc1⋅v‾1=vc1⋅12(2r1−1)=[0.94,-0.35]⋅[12,−12]=0.90\begin{align\*}
v\_{c1} \cdot \overline{v}\_1 &= v\_{c1} \cdot \frac{1}{\sqrt{2}} (2 r\_1 - 1) \\
&= [0.94, \text{-}0.35] \cdot \left[\frac{1}{\sqrt{2}}, -\frac{1}{\sqrt{2}}\right] \\
&= 0.90
\end{align\*}vc1​⋅v1​​=vc1​⋅2​1​(2r1​−1)=[0.94,-0.35]⋅[2​1​,−2​1​]=0.90​

And for our other two vectors:

vc2⋅v‾2=0.95vc3⋅v‾3=0.89v\_{c2} \cdot \overline{v}\_2 = 0.95
\newline
v\_{c3} \cdot \overline{v}\_3 = 0.89vc2​⋅v2​=0.95vc3​⋅v3​=0.89

The dot product between the quantized vector and the original vector, being the second corrective factor, captures for how *far away* the quantized vector is from its original position. In section 3.2 the [RaBitQ paper](https://arxiv.org/pdf/2405.12497) shows there is a bias correcting the dot product between the quantized data and query vectors in a naive fashion. This factor exactly compensates it.

Keep in mind we are doing this transformation to reduce the total size of the data vectors and reduce the cost of vector comparisons. These corrective factors while seemingly large in our 2d example become insignificant as vector dimensionality increases. For example, a 1024 dimensional vector if stored as float32float32float32 requires 4096 bytes. If stored with this bit compression and corrective factors, only 136 bytes are required.

To better understand why we use these factors refer to the [RaBitQ paper](https://arxiv.org/pdf/2405.12497). It gives an in-depth treatment of the math involved.

## The Query

q=[0.68,-1.72]q = [0.68, \text{-}1.72]q=[0.68,-1.72]

To be able to compare our quantized data vectors to a query vector we must first get the query vector into a quantized form and shift it relative to the unit circle. We'll refer to the query vector as qqq, the transformed vector as qcq\_cqc​, and the scalar quantized vector as q‾\overline{q}q​.

q−c=(0.68−-0.49),(-1.72−1.22)=[1.17,−2.95] qc=(q−c)/∥q−c∥=[1.17,−2.95]/3.17=[0.37,−0.92]\begin{align\*}
q - c &= (0.68 - \text{-}0.49), (\text{-}1.72 - 1.22)
\newline
&= [1.17, −2.95]
\end{align\*}
\newline
~\\
\begin{align\*}
q\_c &= (q - c) / \|q - c\|
\newline
&= [1.17, −2.95] / 3.17
\newline
&= [0.37, −0.92]
\end{align\*}q−c​=(0.68−-0.49),(-1.72−1.22)=[1.17,−2.95]​ qc​​=(q−c)/∥q−c∥=[1.17,−2.95]/3.17=[0.37,−0.92]​

Next we perform [Scalar Quantization](https://www.elastic.co/search-labs/blog/scalar-quantization-101) on the query vector down to 4 bits; we'll call this vector q‾ \overline{q}q​. It's worth noting that we do not quantize down to a bit representation but instead maintain an int4int4int4 scalar quantization, q‾\overline{q}q​ as an int4 byte array, for estimating the distance. We can take advantage of this asymmetric quantization to retain more information without additional storage.

lower=-0.92upper=0.37 width=(upper−lower)/(24−1);=(0.37−-0.92)/15;=0.08 q‾=⌊(qc−lower)/width⌉=⌊([0.37,−0.92]−[-0.92,-0.92])/0.08⌉=[15,0]lower = \text{-}0.92
\newline
upper = 0.37
\newline
~\\
\begin{align\*}
width &= (upper - lower) / (2^4 - 1);
\newline
&= (0.37 - \text{-}0.92) / 15;
\newline
&= 0.08
\end{align\*}
\newline
~\\
\newline
\begin{align\*}
\overline{q} &= \lfloor{(q\_c - lower) / width}\rceil
\newline
&= \lfloor{([0.37, −0.92] - [\text{-}0.92, \text{-}0.92]) / 0.08}\rceil
\newline
&= [15, 0]
\end{align\*}lower=-0.92upper=0.37 width​=(upper−lower)/(24−1);=(0.37−-0.92)/15;=0.08​ q​​=⌊(qc​−lower)/width⌉=⌊([0.37,−0.92]−[-0.92,-0.92])/0.08⌉=[15,0]​

![Query Transformed Illustration](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt343e90530cd80e9e/6a17e5db0b0bed51b6dd3558/32f8c449b1bfad796169863fe93068ace864cf7d-854x480.gif)

Figure 4: Query with centroid transformation applied.

As you can see because we have only 2 dimensions our quantized query vector now consists of two values at the ceiling and floor of the int4int4int4 range. With longer vectors you would see a variety of int4 values with one of them being the ceiling and one of them being the floor.

Now we are ready to perform a distance calculation comparing each indexed data vector with this query vector. We do this by summing up each dimension in our quantized query that's shared with any given data vector. Basically, a plain old dot-product, but with bits and bytes.

q‾⋅r1=[15,0]⋅[1,0]=15\begin{align\*}
\overline{q} \cdot r\_1 &= [15, 0] \cdot [1, 0]
\newline
&= 15
\end{align\*}q​⋅r1​​=[15,0]⋅[1,0]=15​

We can now apply corrective factors to unroll the quantization and get a more accurate reflection of the estimated distance.

To achieve this we'll collect the upper and lower bound from the quantized query, which we derived when doing the scalar quantization of the query. Additionally we need the distance from the query to the centroid. Since we computed the distance between a vector and a centroid previously we'll just include that distance here for reference:

∥q−c∥=3.17\|q - c\| = 3.17∥q−c∥=3.17

### Estimated Distance

Alright! We have quantized our vectors and collected corrective factors. Now we are ready to compute the estimated distance between v1v\_1v1​ and qqq. Let's transform our [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance) into an equation that has much more computationally friendly terms:

dist(v1,q)=∥v1−q∥=∥(v1−c)−(q−c)∥2=∥v1−c∥2+∥q−c∥2−2×∥v1−c∥×∥q−c∥×(qc⋅vc1)\begin{align\*}
dist(v\_1, q) &= \|v\_1 - q\|
\newline
&= \sqrt{\|(v\_1 - c) - (q - c)\|^2}
\newline
&= \sqrt{\|v\_1 - c\|^2 + \|q - c\|^2 - 2 \times \|v\_1 - c\| \times \|q - c\| \times (q\_c \cdot v\_{c1})}
\end{align\*}dist(v1​,q)​=∥v1​−q∥=∥(v1​−c)−(q−c)∥2​=∥v1​−c∥2+∥q−c∥2−2×∥v1​−c∥×∥q−c∥×(qc​⋅vc1​)​​

In this form, most of these factors we derived previously, such as ∥v1−c∥\|v\_1-c\|∥v1​−c∥, and notably can be pre-computed prior to query or are not direct comparisons between the query vector and any given data vector such as v1v\_1v1​.

We however still need to compute qc⋅vc1q\_c \cdot v\_{c1}qc​⋅vc1​. We can utilize our corrective factors and our quantized binary distance metric q‾⋅r1\overline{q} \cdot r\_1q​⋅r1​ to estimate this value reasonably and quickly. Let's walk through that.

qc⋅vc1≈(qc⋅v‾1)/(vc1⋅v‾1)q\_c \cdot v\_{c1} \approx (q\_c \cdot \overline{v}\_1) / (v\_{c1} \cdot \overline{v}\_1)qc​⋅vc1​≈(qc​⋅v1​)/(vc1​⋅v1​)

Let's start by estimating qc⋅v‾1q\_c \cdot \overline{v}\_1qc​⋅v1​ which requires this equation which essentially unrolls our transformations using the representative points we defined earlier:

qc⋅v‾1≈(lower+width⋅q‾)⋅(1d(2r1−1))q\_c \cdot \overline{v}\_1 \approx (lower + width \cdot \overline{q}) \cdot (\frac{1}{\sqrt{d}}(2r\_1 - 1))qc​⋅v1​≈(lower+width⋅q​)⋅(d​1​(2r1​−1))

Specifically, 1d(2r1−1)\frac{1}{\sqrt{d}}(2r\_1-1)d​1​(2r1​−1) maps the binary values back to our representative point and lower+width⋅q‾lower + width \cdot \overline{q}lower+width⋅q​ undoes the shift and scale used to compute the scalar quantized query components.

We can rewrite this to make it more computationally friendly like this.

First, though, let's define a couple of helper variables:

* total number of 1's bits in r1r\_1r1​ as v‾b1\overline{v}\_{b1}vb1​, 111 in this case
* total number of all quantized values in q‾b\overline{q}\_bq​b​ as q‾b\overline{q}\_bq​b​, 151515 in this case

qc⋅v‾1≈2×widthd×(q‾⋅r1)+2×lowerd×v‾b1−widthd×q‾b−d×lower≈2×0.082×15+2×-0.922×1−0.082×15−2×-0.92≈0.92\begin{align\*}
q\_c \cdot \overline{v}\_1 &\approx \frac{2 \times width}{\sqrt{d}} \times (\overline{q} \cdot r\_1) + \frac{2 \times lower}{\sqrt{d}} \times \overline{v}\_{b1} - \frac{width}{\sqrt{d}} \times \overline{q}\_b - \sqrt{d} \times lower
\newline
&\approx \frac{2 \times 0.08}{\sqrt{2}} \times 15 + \frac{2 \times \text{-}0.92}{\sqrt{2}} \times 1 - \frac{0.08}{\sqrt{2}} \times 15 - \sqrt{2} \times \text{-}0.92
\newline
&\approx 0.92
\end{align\*}
\newlineqc​⋅v1​​≈d​2×width​×(q​⋅r1​)+d​2×lower​×vb1​−d​width​×q​b​−d​×lower≈2​2×0.08​×15+2​2×-0.92​×1−2​0.08​×15−2​×-0.92≈0.92​

With this value and vc1⋅v‾1v\_{c1} \cdot \overline{v}\_1vc1​⋅v1​, which we precomputed when indexing our data vector, we can then plug those values in to compute an approximation of qc⋅vc1q\_c \cdot v\_{c1}qc​⋅vc1​:

qc⋅vc1≈(qc⋅v‾1)/(vc1⋅v‾1)≈0.92/0.90≈1.01\begin{align\*}
q\_c \cdot v\_{c1} &\approx (q\_c \cdot \overline{v}\_1) / (v\_{c1} \cdot \overline{v}\_1)
\newline
&\approx 0.92 / 0.90
\newline
&\approx 1.01
\end{align\*}qc​⋅vc1​​≈(qc​⋅v1​)/(vc1​⋅v1​)≈0.92/0.90≈1.01​

Finally, let's plug this into our larger distance equation noting that we are using an estimate for qc⋅vc1q\_c \cdot v\_{c1}qc​⋅vc1​:

dist(v1,q)=∥v1−c∥2+∥q−c∥2−2×∥v1−c∥×∥q−c∥×(qc⋅vc1)est\_dist(v1,q)=1.132+3.172−2×1.13×3.17×1.01dist(v\_1, q) = \sqrt{\|v\_1-c\|^2 + \|q-c\|^2 - 2 \times \|v\_1-c\| \times \|q-c\| \times (q\_c \cdot v\_{c1})}
\newline
est\\_dist(v\_1, q) = \sqrt{1.13^2 + 3.17^2 − 2 \times 1.13 \times 3.17 \times 1.01}dist(v1​,q)=∥v1​−c∥2+∥q−c∥2−2×∥v1​−c∥×∥q−c∥×(qc​⋅vc1​)​est\_dist(v1​,q)=1.132+3.172−2×1.13×3.17×1.01​

With all of the corrections applied we are left with a reasonable estimate of the distance between two vectors. For instance in this case our estimated distances between each of our original data vectors, v1v\_1v1​, v2v\_2v2​, v3v\_3v3​, and qqq compared to the true distances are:

est\_dist(v1,q)=2.02est\_dist(v2,q)=1.15est\_dist(v3,q)=6.15 est\\_dist(v\_1, q) = 2.02
\newline
est\\_dist(v\_2, q) = 1.15
\newline
est\\_dist(v\_3, q) = 6.15
\newline
~\\est\_dist(v1​,q)=2.02est\_dist(v2​,q)=1.15est\_dist(v3​,q)=6.15

eucl\_dist(v1,q)=2.55eucl\_dist(v2,q)=2.50eucl\_dist(v3,q)=5.52eucl\\_dist(v\_1, q) = 2.55
\newline
eucl\\_dist(v\_2, q) = 2.50
\newline
eucl\\_dist(v\_3, q) = 5.52eucl\_dist(v1​,q)=2.55eucl\_dist(v2​,q)=2.50eucl\_dist(v3​,q)=5.52

For details on how the linear algebra is derived or simplified when applied refer to the [RaBitQ paper](https://arxiv.org/pdf/2405.12497).

### Re-ranking

As you can see from the results in the prior section, these estimated distances are indeed estimates. Binary quantization produces vectors whose distance calculations are, even with the extra corrective factors, only an approximation of the distance between vectors. In our experiments we were able to achieve high recall by involving a multi-stage process. This confirms the findings in the [RaBitQ paper](https://arxiv.org/pdf/2405.12497).

Therefore to achieve high quality results, a reasonable sample of vectors returned from binary quantization then must be re-ranked with a more exact distance computation. In practice this subset of candidates can be small achieving typically high > 95% recall with 100 or less candidates for large datasets (>1m).

With RaBitQ results are re-ranked continually as part of the search operation. In our experiments to achieve a more scalable binary quantization we decoupled the re-ranking step. While RaBitQ is able to maintain a better list of top NNN candidates by re-ranking while searching, it is at the cost of constantly paging in full float32float32float32 vectors, which is untenable for some larger production-like datasets.

## Conclusion

Whew! You made it! This blog is indeed a big one. We are extremely excited about this new algorithm as it can alleviate many of the pain points of Product Quantization (e.g. code-book building cost, distance estimation slowness, etc.) and provide excellent recall and speed.

### Frequently Asked Questions

#### What are the benefits of binary quantization?

Quantization allows for vectors to be encoded in a lossy manner, thus reducing fidelity slightly with huge space savings.

#### How does binary quantization work?

Binary quantization takes each vector and transforms it relative to a prototypical set of sample vectors creating a smaller representation that can be used to approximate distances at great space and computation savings.

#### Does binary quantization create codebooks similar to PQ?

Binary quantization does not really create codebooks and instead compresses each data vector down to a 1 bit representation that is the inclusion in a region around a centroid. The authors of the RaBitQ paper (https://arxiv.org/pdf/2405.12497), that is a large driver for our understanding and implementation of binary quantization, mention how the codebooks in PQ are related to the regions around any given centroid so if it's more intuitive to think of these regions as codebooks then yes.

#### Are the query vectors converted to 1 bit prior to comparison with the codebook / regions created from the data vectors?

Binary quantization relies on finding regions first. Query vectors similarly are transformed into this space using the same centroid that allowed transformation into the region that was used to quantize the data vectors. This is what allows the distance estimation comparison to happen.

#### Are there multiple centroids?

Yes, if the number of vectors justifies it. Although, even for millions of vectors, we have found that only one centroid is sufficient for many datasets and models.

#### Are the centroids converted to a 1 bit representation as well?

No, since very few centroids are required they can be maintained in their float32 form without concern for scaling.

#### The author's of the RaBitQ paper (https://arxiv.org/pdf/2405.12497) mention transforming the data with a random orthogonal matrix P why do you not include it here?

We've found so far that we can reduce complexity, both algorithmically and performance-wise, by removing this random transformation. While some vectors may be favored, traditionally reranking a reasonable set of data, which is required to achieve reasonable recall, seems to negate the need for this in practice.

#### The author's of the RaBitQ paper (https://arxiv.org/pdf/2405.12497) mention using multiple centroids but you focus on a single centroid here. Why only one centroid?

We've found so far that a single centroid for most production datasets works well. Additionally when talking about how binary quantization works we can focus on a single centroid at a time. As you have more vectors, >100m, you may find that recall is impacted. When using Elasticsearch these large datasets can be pre-partitioned and multiple centroids will naturally be used.

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