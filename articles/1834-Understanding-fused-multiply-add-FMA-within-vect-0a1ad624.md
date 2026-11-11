---
title: 'Understanding fused multiply-add (FMA) within vector similarity computations in Lucene'
company: Elastic
tag: 工程相关
date: 2023-11-20
url: https://www.elastic.co/search-labs/blog/vector-similarity-computations-fma-style
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Understanding fused multiply-add (FMA) within vector similarity computations in Lucene

Learn how to use fused multiply-add (FMA) within vector similarity computations in Lucene and discover how FMA can improve performance.

November 20, 2023

[Chris Hegarty](/search-labs/author/chris-hegarty)

[Lucene](/search-labs/blog/category/lucene)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

In Lucene 9.7.0 we added support that [leverages SIMD instructions](https://www.elastic.co/blog/accelerating-vector-search-simd-instructions) to perform data-parallelization of vector similarity computations. Now we’re pushing this even further with the use of Fused Multiply-Add (FMA).

## What is fused multiply-add (FMA)

Multiply and add is a common operation that computes the product of two numbers and adds that product with a third number. These types of operations are performed over and over during vector similarity computations.

a∗b+ca \* b + c
a∗b+c

Fused multiply-add (FMA) is a single operation that performs both the multiply and add operations in one - the multiplication and addition are said to be “fused” together. FMA is typically faster than a separate multiplication and addition because most CPUs model it as a single instruction.

FMA also produces more accurate results. Separate multiply and add operations on floating-point numbers have two rounds; one for the multiplication, and one for the addition, since they are separate instructions that need to produce separate results. That is effectively,

round(round(a∗b)+c)round(round(a \* b) + c)
round(round(a∗b)+c)

Whereas FMA has a single rounding, which applies only to the combined result of the multiplication and addition. That is effectively,

round(a∗b+c)round(a \* b + c)
round(a∗b+c)

Within the FMA instruction the `a * b` produces an infinite precision intermediate result that is added with `c`, before the final result is rounded. This eliminates a single round, when compared to separate multiply and add operations, which results in more accuracy.

## FMA in Lucene: Under the hood

So what has actually changed? In Lucene we have replaced the separate multiply and add operations with a single FMA operation. The scalar variants now use [Math::fma](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Math.html#fma(float,float,float)), while the Panama vectorized variants use [FloatVector::fma](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.incubator.vector/jdk/incubator/vector/FloatVector.html#fma(jdk.incubator.vector.Vector,jdk.incubator.vector.Vector)).

If we look at the disassembly we can see the effect that this change has had. Previously we saw this kind of code pattern for the Panama vectorized implementation of dot product.

```
vmovdqu32 zmm0,ZMMWORD PTR [rcx+r10*4+0x10]
vmulps zmm0,zmm0,ZMMWORD PTR [rdx+r10*4+0x10]
vaddps zmm4,zmm4,zmm0
```

The `vmovdqu32` instruction loads 512 bits of packed doubleword values from a memory location into the `zmm0` register. The `vmulps` instruction then multiplies the values in `zmm0` with the corresponding packed values from a memory location, and stores the result in `zmm0`. Finally, the `vaddps` instruction adds the 16 packed single precision floating-point values in `zmm0` with the corresponding values in `zmm4`, and stores the result in `zmm4`.

With the change to use `FloatVector::fma`, we see the following pattern:

```
vmovdqu32 zmm0,ZMMWORD PTR [rdx+r11*4+0xd0]
vfmadd231ps zmm4,zmm0,ZMMWORD PTR [rcx+r11*4+0xd0]
```

Again, the first instruction is similar to the previous example, where it loads 512 bits of packed doubleword values from a memory location into the `zmm0` register. The `vfmadd231ps` (this is the FMA instruction), multiplies the values in `zmm0` with the corresponding packed values from a memory location, adds that intermediate result to the values in `zmm4`, performs rounding and stores the resulting 16 packed single precision floating-point values in `zmm4`.

The `vfmadd231ps` instruction is doing quite a lot! It’s a clear signal of intent to the CPU about the nature of the computations that the code is running. Given this, the CPU can make smarter decisions about how this is done, which typically results in improved performance (and accuracy as previously described).

## Performance improvements with FMA

In general, the use of FMA typically results in improved performance. But as always you need to benchmark! Thankfully, Lucene deals with quite a bit of complexity when determining whether to use FMA or not, so you don’t have to. Things like, whether the CPU even has support for FMA, if FMA is enabled in the Java Virtual Machine, and only enabling FMA on architectures that have proven to be faster than separate multiply and add operations. As you can probably tell, this heuristic is not perfect, but goes a long way to making the out-of-the-box experience good. While accuracy is improved with FMA, we see no negative effect on pre-existing similarity computations when FMA is not enabled.

Along with the use of FMA, the suite of vector similarity functions got some (more) love. All of dot product, square, and cosine distance, both the scalar and Panama vectorized variants have been updated. Optimizations have been applied based on the inspection of disassembly and empirical experiments, which have brought improvements that help fill the pipeline keeping the CPU busy; mostly through more consistent and targeted loop unrolling, as well as removal of data dependencies within loops.

It’s not straightforward to put concrete performance improvement numbers on this change, since the effect spans multiple similarity functions and variants, but we see positive throughput improvements, from single digit percentages in floating-point dot product, to higher double digit percentage improvements in cosine. The byte based similarity functions also show similar throughput improvements.

## Wrapping up

In Lucene 9.7.0, we added the ability to enable an alternative faster implementation of the low-level primitive operations used by Vector Search through SIMD instructions. In the upcoming Lucene 9.9.0 we built upon this to leverage faster FMA instructions, as well as to apply optimization techniques more consistently across all the similarity functions. Previous versions of Elasticsearch are already benefiting from SIMD, and the upcoming Elasticsearch 8.12.0 will have the FMA improvements.

Finally, I'd like to call out Lucene PMC member [Robert Muir](https://github.com/rmuir) for continuing to make improvements in this area, and for the enjoyable and productive collaboration.

### Frequently Asked Questions

#### What is fused multiply-add (FMA)?

Fused multiply-add (FMA) is a single operation that performs both the multiply and add operations in one - the multiplication and addition are said to be “fused” together. FMA is typically faster than a separate multiplication and addition and produces more accurate results.

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