---
title: 'Understanding Int4 scalar quantization in Lucene'
company: Elastic
tag: 索引构建
date: 2024-04-25
url: https://www.elastic.co/search-labs/blog/int4-scalar-quantization-in-lucene
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Understanding Int4 scalar quantization in Lucene

This blog explains how int4 quantization works in Lucene, how it lines up, and the benefits of using int4 quantization.

April 25, 2024

[Benjamin Trent](/search-labs/author/benjamin-trent)[Thomas Veasey](/search-labs/author/thomas-veasey)

[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

Jump to

Share

## Introduction to Int4 quantization in Lucene

In our previous blogs, we walked through the [implementation of scalar quantization](https://www.elastic.co/search-labs/blog/scalar-quantization-in-lucene) as a whole in Lucene. We also explored [two specific optimizations for quantization](https://www.elastic.co/search-labs/blog/vector-db-optimized-scalar-quantization). Now we've reached the question: how does `int4` quantization work in Lucene and how does it line up?

## How does `Int4` quantization work in Lucene

### Storing and scoring the quantized vectors

Lucene stores all the vectors in a flat file, making it possible for each vector to be retrieved given some ordinal. You can read a brief overview of this in our [previous scalar quantization blog](https://www.elastic.co/search-labs/blog/scalar-quantization-in-lucene#quantization-per-segment).

Now`int4` gives us additional compression options than what we had before. It reduces the quantization space to only 16 possible values (0 through 15). For more compact storage, Lucene uses some simple bit shift operations to pack these smaller values into a single byte, allowing a possible 2x space savings on top of the already 4x space savings with int8. In all, storing int4 with bit compression is 8x smaller than `float32`.

![int4 byte compression](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3d552363049ed907/6a17d83bfaa91342e493c6f2/fbdc307038f1392daf0b9c270647bcfb1b68c337-1345x786.png)

Figure 1: This shows the reduction in bytes required with `int4` which allows an 8x reduction in size from `float32` when compressed.

`int4` also has some benefits when it comes to scoring latency. Since the values are known to be between `0-15`, we can take advantage of knowing exactly when to worry about value overflow and optimize the dot-product calculation. The maximum value for a dot product is `15*15=225` which can fit in a single byte. ARM processors (like my macbook) have a [SIMD](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data) instruction length of 128 bits (16 bytes). This means that for a Java `short` we can allocate 8 values to fill the lanes. For 1024 dimensions, each lane will end up accumulating a total of `1024/8=128` multiplications that have a max value of `225`. The resulting maximum sum of `28800` fits well within the limit of Java's `short` value and we can iterate more values at a time than. Here is some simplified code of what this looks like for ARM.

```
// snip preamble handling vectors longer than 1024
// 8 lanes of 2 bytes 
ShortVector acc = ShortVector.zero(ShortVector.SPECIES_128);
for (int i = 0; i < length; i += ByteVector.SPECIES_64.length()) {
  // Get 8 bytes from vector a
  ByteVector va8 = ByteVector.fromArray(ByteVector.SPECIES_64, a, i);
  // Get 8 bytes from vector b
  ByteVector vb8 = ByteVector.fromArray(ByteVector.SPECIES_64, b, i);
  // Multiply together, potentially saturating signed byte with a max of 225
  ByteVector prod8 = va8.mul(vb8);
  // Now convert the product to accumulate into the short
  ShortVector prod16 = prod8.convertShape(B2S, ShortVector.SPECIES_128, 0).reinterpretAsShorts();
  // Ensure to handle potential byte saturation
  acc = acc.add(prod16.and((short) 0xFF));
}
// snip, tail handling
```

### Calculating the quantization error correction

For a more detailed explanation of the error correction calculation and its derivation, please see [error correcting the scalar dot-product](https://www.elastic.co/search-labs/blog/vector-db-optimized-scalar-quantization#error-correcting-the-scalar-dot-product).

Here is a short summary, woefully (or joyfully) devoid of complicated mathematics.

For every quantized vector stored, we additionally keep track of a quantization error correction. Back in the [Scalar Quantization 101 blog](https://www.elastic.co/search-labs/blog/scalar-quantization-101#time-to-remember-your-algebra) there was a particular constant mentioned:

α×int8i×min\alpha \times int8\_i \times min
α×int8i​×min

This constant is a simple constant derived from basic algebra. However, we now include additional information in the stored float that relates to the rounding loss.

∑i=0dim−1((i−min)−i′×α)i′×α\sum\_{i=0}^{dim-1} ((i - min) - i'\times\alpha)i'\times\alpha
i=0∑dim−1​((i−min)−i′×α)i′×α

Where iii is each floating point vector dimension, i′i'i′ is the scalar quantized floating point value, and α=max−min(1<<bits)−1\alpha=\frac{max - min}{(1 << bits) - 1}α=(1<<bits)−1max−min​.

This has two consequences. The first is intuitive, as it means that for a given set of quantization buckets, we are slightly more accurate as we account for some of the lossiness of the quantization. The second consequence is a bit more nuanced. It now means we have an error correction measure that is impacted by the quantization bucketing. This implies that it can be optimized.

### Finding the optimal bucketing for int4 quantization

The naive and simple way to do scalar quantization can get you pretty far. Usually, you pick a confidence interval from which you calculate the allowed extreme boundaries for vector values. The default in Lucene and consequently Elasticsearch is 1−1/(dimensions+1)1-1/(dimensions+1)1−1/(dimensions+1). Figure 2 shows the confidence interval over some sampled [CohereV3 embeddings](https://huggingface.co/datasets/Cohere/wikipedia-2023-11-embed-multilingual-v3/viewer/en). Figure 3 shows the same vectors, but scalar quantized with that statically set confidence interval.

![CohereV3 vector dimension distribution](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt4f490eeb86437541/6a17d83dabe0f2831bdfe87d/cef8eb3ecf7b212e81e57fd54e48ebf772535a75-847x428.png)

Figure 2: A sampling of CohereV3 dimension values.

![CohereV3 vector dimension distribution quantized](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt370cd91d65bff7f1/6a17d83e6df73108aa0a0d5e/ca558319a6eee14bfbf7c3ac725b48772119ac23-848x428.png)

Figure 3: CohereV3 dimension values quantized into int7 values. What are those spikes at the end? Well, that is the result of truncating extreme values during the quantization process.

But, we are leaving some nice optimizations on the floor. What if we could tweak the confidence interval to shift the buckets, allowing for more important dimensional values to have higher fidelity. To optimize, Lucene does the following:

* Sample around 1,000 vectors from the data set and calculate their true nearest 10 neighbors.
* Calculate a set of candidate upper and lower quantiles. The set is calculated by using two different confidence intervals: 1−1/(dimensions+1)1 - 1/(dimensions+1)1−1/(dimensions+1) and 1−(dimensions/10)/(dimensions+1)1-(dimensions/10)/(dimensions + 1)1−(dimensions/10)/(dimensions+1). These intervals are on the opposite extremes. For example, vectors with `1024` dimensions would search quantile candidates between confidence intervals `0.99902` and `0.90009`.
* Do a grid search over a subset of the quantiles that exist between these two confidence intervals. The grid search finds the quantiles that maximize the [coefficient of determination](https://en.wikipedia.org/wiki/Coefficient_of_determination) of the quantization score errors vs. the true 10 nearest neighbors calculated earlier.

![Searching the int4 space](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt10282851a4739770/6a17d840033c8de7686bb011/1c8db6e93ab0296fbfa3fe090b5a259c99e52ecc-1000x500.gif)

Figure 3: Lucene searching the confidence interval space and testing various buckets for `int4` quantization.

![The optimal int4 quantization](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7769dddb9cc69304/6a17d842e8fbcee09e3a177b/dbe49e9c2291e1b6e1fcda80ea46ae7d4fba509a-857x428.png)

Figure 4: The best `int4` quantization buckets found for this CohereV3 sample set.

For a more complete explanation of the optimization process and the mathematics behind this optimization, see [optimizing the truncation interval](https://www.elastic.co/search-labs/blog/vector-db-optimized-scalar-quantization#optimizing-the-truncation-interval).

### Speed vs. size for quantization

As I mentioned before, `int4` gives you an interesting tradeoff between performance and space. To drive this point home, here are some memory requirements for CohereV3 500k vectors.

![CohereV3 Memory Requirements](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltcfa648610dd1bd66/6a17d84463173070535858f7/c62f8d0a88e2b07f279986fecb725bf6f6c712a2-1200x742.png)

Figure 5: Memory requirements for CohereV3 500k vectors.

Of course, we see the typical 4x reduction in regular scalar quantization, but then additional 2x reduction with `int4`. Moving the required memory from `2GB` to less than `300MB`. Keep in mind, this is with compression enabled. Decompressing and compressing bytes does have an overhead at search time. For every byte vector, we must decompress them before doing the `int4` comparisons. Consequently, when this is introduced in Elasticsearch, we want to give users the ability to choose to compress or not. For some users, the cheaper memory requirements are just too good to pass up, for others, their focus is speed. `Int4` gives the opportunity to tune your settings to fit your use-case.

![CohereV3 Speed](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte77d904033addae5/6a17d845b1e11334d479f0f2/52e73e53a85587bd852f92e4ac39dfd6b2aef7e4-576x455.png)

Figure 6: HNSW graph search speed comparison for CohereV3 500k vectors.

### Speed part 2: more SIMD in int4

Figure 6 is a bit disappointing in terms of the speed of compressed scalar quantization. We expect performance benefits from loading fewer bytes to the JVM heap. However, this is being outweighed by the cost of decompressing them. This caused us dig deeper. The reason for the performance impact was naively decompressing the bytes separately from the dot-product comparison. This is a mistake. We can do better.

Consequently, we can use SIMD to decompress the bytes and compare them in the same function. This is a bit more complicated than the previous SIMD example, but it is possible. Here is a simplified version of what this looks like for ARM.

```
// the packed vector, each byte contains two values
// for packed value `n`: packed[n] = (raw[n] << 4) | raw[packed.length + n];
ByteVector vb8 = ByteVector.fromArray(ByteVector.SPECIES_64, packed, i + j);
// unpacked, the raw query vector int4 quantized
ByteVector va8 = ByteVector.fromArray(ByteVector.SPECIES_64, unpacked, i + j + packed.length);

// upper side, decompress and multiply
ByteVector prod8 = vb8.and((byte) 0x0F).mul(va8);
ShortVector prod16 = prod8.convertShape(B2S, ShortVector.SPECIES_128, 0).reinterpretAsShorts();
// Ensure to handle potential byte saturation
acc0 = acc0.add(prod16.and((short) 0xFF));

// lower side, decompress and multiply
va8 = ByteVector.fromArray(ByteVector.SPECIES_64, unpacked, i + j);
prod8 = vb8.lanewise(LSHR, 4).mul(va8);
prod16 = prod8.convertShape(B2S, ShortVector.SPECIES_128, 0).reinterpretAsShorts();
// Ensure to handle potential byte saturation
acc1 = acc1.add(prod16.and((short) 0xFF));
```

As expected, this has a significant improvement on ARM. Effectively removing all performance discrepancies on ARM between compressed and uncompressed scalar quantization.

![CohereV3 Speed Improved](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb05f2dea5293ad4a/6a17d8464b055d9f6d432063/607e7609d2bb8edf27bba5af3546836a4464c067-576x455.png)

Figure 7: HNSW graph search comparison with int4 quantized vectors over 500k Coherev3 vectors. This is on ARM architecture.

## The end?

Over the last two large and technical blog posts, we've gone over the math and intuition around the optimizations and what they bring to Lucene. It's been a long ride, and we are nowhere near done. Keep an eye out for these capabilities in a future Elasticsearch version!

### Frequently Asked Questions

#### What is Int4 quantization in Lucene?

Int4 provides additional compression options. It reduces the quantization space to only 16 possible values (0 through 15).

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5d70b25967c2194e/6a17d732b1e11383f879f0ca/13c3c0053e2968fb835ba2f90f34bec3a011b5c0-880x592.webp)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)

### Elasticsearch vs. OpenSearch: Vector Search Performance Comparison

June 26, 2024|[Ugo Sangiorgi](/search-labs/author/ugo-sangiorgi)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt762b38f91bd71c8e/6a170db8b339d547bb76a048/368db71c500e72d20fe225fe44c2c40231e29765-721x420.jpg)

[Lucene](/search-labs/blog/category/lucene)

### Bringing maximum-inner-product into Lucene

September 01, 2023|[Benjamin Trent](/search-labs/author/benjamin-trent)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9ec7a04e3bdbfd9f/6a467b337eb22d59efdfc54d/c07100b6fcc74dba250e6853b1c5ef1edabbedfc-1920x1080.png)

[Lucene](/search-labs/blog/category/lucene)[Index Data](/search-labs/blog/category/index-data)

### How DocValuesSkippers in Lucene 10 make range queries faster without doubling your storage

June 12, 2026|[Alan Woodward](/search-labs/author/alan-woodward)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltf9fcbf843affc566/6a1706b8964ceaea3208bab9/7884e35f40c15fe349379ef7ae4648b21708962f-1070x712.jpg)

[Lucene](/search-labs/blog/category/lucene)

### Concurrency bugs in Lucene: How to fix optimistic concurrency failures

February 07, 2025|[Benjamin Trent](/search-labs/author/benjamin-trent)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt0cccbdeaa4571db2/6a17057dc1e8a52e10f881e0/2fff360ef055df5980c696adffeb49f4b125a268-1913x1182.png)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

### Better Binary Quantization (BBQ) vs. Product Quantization

November 18, 2024|[Benjamin Trent](/search-labs/author/benjamin-trent)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter