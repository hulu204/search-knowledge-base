---
title: 'Scalar quantization 101'
company: Elastic
tag: 索引构建
date: 2023-10-25
url: https://www.elastic.co/search-labs/blog/scalar-quantization-101
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Scalar quantization 101

Understand what scalar quantization is, how it works and its benefits. This guide also covers the math behind quantization and examples.

October 25, 2023

[Benjamin Trent](/search-labs/author/benjamin-trent)

[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

Jump to

Share

## Introduction to scalar quantization

Most embedding models output float32float32float32 vector values. While this provides the highest fidelity, it is wasteful given the information that is actually important in the vector. Within a given data set, embeddings never require all 2 billion options for each individual dimension. This is especially true on higher dimensional vectors (e.g. 386 dimensions and higher). Quantization allows for vectors to be encoded in a lossy manner, thus reducing fidelity slightly with huge space savings.

## Understanding buckets in scalar quantization

Scalar quantization takes each vector dimension and buckets them into some smaller data type. For the rest of the blog, we will assume quantizing float32float32float32 values into int8int8int8. To bucket values accurately, it isn't as simple as rounding the floating point values to the nearest integer. Many models output vectors that have dimensions continuously on the range [−1.0,1.0][-1.0, 1.0][−1.0,1.0]. So, two different vector values 0.123 and 0.321 could both be rounded down to 0. Ultimately, a vector would only use 2 of its 255 available buckets in int8int8int8, losing too much information.

![Quantization illustration](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb6b4eaba7138c23e/6a17d983445de996cd4cff80/f18da238f2f48542bae1731272600b18ba897708-1254x540.png)

Figure 1: Illustration of quantization goals, bucketing continuous values from −1.0-1.0−1.0 to 1.01.01.0 into discrete int8int8int8 values.

The math behind the numerical transformation isn't too complicated. Since we can calculate the minimum and maximum values for the floating point range, we can use [min-max normalization](https://en.wikipedia.org/wiki/Feature_scaling#Rescaling_(min-max_normalization)) and then linearly shift the values.

int8≈127max−min×(float32−min)int8 \approx \frac{127}{max - min} \times (float32 - min)
int8≈max−min127​×(float32−min)

float32≈max−min127×int8+minfloat32 \approx \frac{max - min}{127} \times int8 + min
float32≈127max−min​×int8+min

Figure 2: Equations for transforming between int8int8int8 and float32float32float32. Note, these are lossy transformations and not exact. In the following examples, we are only using positive values within int8. This aligns with the Lucene implementation.

## The role of statistics in scalar quantization

A [quantile](https://en.wikipedia.org/wiki/Quantile) is a slice of a distribution that contains a certain percentage of the values. So, for example, it may be that 99%99\%99% of our floating point values are between [−0.75,0.86][-0.75, 0.86][−0.75,0.86] instead of the true minimum and maximum values of [−1.0,1.0][-1.0, 1.0][−1.0,1.0]. Any values less than -0.75 and greater than 0.86 are considered outliers. If you include outliers when attempting to quantize results, you will have fewer available buckets for your most common values. And fewer buckets can mean less accuracy and thus greater loss of information.

![Quantile illustration](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt61c68f220ef4af50/6a17d984445de975274cff84/874fc0d61224d74b705d43cf853c629636b8ba4b-1241x682.png)

Figure 3: Illustration of the 99%99\%99% [confidence interval](https://en.wikipedia.org/wiki/Confidence_interval) and the individual quantile values. 99%99\%%99% of all values fall within the range [−0.75,0.86][-0.75, 0.86][−0.75,0.86].

This is all well and good, but now that we know how to quantize values, how can we actually calculate distances between two quantized vectors? Is it as simple as a regular [dot\_product](https://en.wikipedia.org/wiki/Dot_product)?

## The role of algebra in scalar quantization

We are still missing one vital piece, how do we calculate the distance between two quantized vectors. While we haven't shied away from math yet in this blog, we are about to do a bunch more. Time to break out your pencils and try to remember [polynomials](https://en.wikipedia.org/wiki/Polynomial) and basic algebra.

The basic requirement for [dot\_product](https://en.wikipedia.org/wiki/Dot_product) and [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) is being able to multiply floating point values together and sum up their results. We already know how to transform between float32float32float32 and int8int8int8 values, so what does multiplication look like with our transformations?

float32i×float32i′≈(max−min127×int8i+min)×(max−min127×int8i′+min)float32\_i \times float32'\_i \approx (\frac{max - min}{127} \times int8\_i + min) \times (\frac{max - min}{127} \times int8'\_i + min)
float32i​×float32i′​≈(127max−min​×int8i​+min)×(127max−min​×int8i′​+min)

We can then expand this multiplication and to simplify we will substitute α\alphaα for max−min127\frac{max - min}{127}127max−min​.

α2×int8i×int8i′+α×int8i×min+α×int8i′×min+min2\alpha^2 \times int8\_i \times int8'\_i + \alpha \times int8\_i \times min + \alpha \times int8'\_i \times min + min^2
α2×int8i​×int8i′​+α×int8i​×min+α×int8i′​×min+min2

What makes this even more interesting, is that only one part of this equation requires both values at the same time. However, dot\_product isn't just two floats being multiplied, but all the floats for each dimension of the vector. With vector dimension count dimdimdim in hand, all the following can be pre-calculated at query time and storage time.

dim×α2dim\times\alpha^2dim×α2 is just dim×(max−min127)2dim\times(\frac{max-min}{127})^2dim×(127max−min​)2 and can be stored as a single float value.

∑i=0dim−1min×α×int8i\sum\_{i=0}^{dim-1}min\times\alpha\times int8\_i∑i=0dim−1​min×α×int8i​ and ∑i=0dim−1min×α×int8i′\sum\_{i=0}^{dim-1}min\times\alpha\times int8'\_i∑i=0dim−1​min×α×int8i′​ can be pre-calculated and stored as a single float value or calculated once at query time.

dim×min2dim\times min^2dim×min2 can be pre-calculated and stored as a single float value.

Of all this:

dim×α2×dotProduct(int8,int8′)+∑i=0dim−1min×α×int8i+∑i=0dim−1min×α×int8i′+dim×min2dim \times \alpha^2 \times dotProduct(int8, int8') + \sum\_{i=0}^{dim-1}min\times\alpha\times int8\_i + \sum\_{i=0}^{dim-1}min\times\alpha\times int8'\_i + dim\times min^2
dim×α2×dotProduct(int8,int8′)+i=0∑dim−1​min×α×int8i​+i=0∑dim−1​min×α×int8i′​+dim×min2

The only calculation required for dot\_product is just dotProduct(int8,int8′)dotProduct(int8, int8')dotProduct(int8,int8′) with some pre-calculated values combined with the result.

## Ensuring accuracy in quantization

So, how is this accurate at all? Aren't we losing information by quantizing? Yes, we are, but quantization takes advantage of the fact that we don't need all the information. For learned embeddings models, the distributions of the various dimensions usually don't have [fat-tails](https://en.wikipedia.org/wiki/Fat-tailed_distribution). This means they are localized and fairly consistent. Additionaly, the error introduced per dimension via quantization is independent. Meaning, the error cancels out for our typical vector operations like dot\_product.

## Conclusion

Whew, that was a ton to cover. But now you have a good grasp of the technical benefits of quantization, the math behind it, and how you can calculate the distances between vectors while accounting for the linear transformation. Look next at how we implemented this in Lucene and some of the unique challenges and benefits available there.

### Frequently Asked Questions

#### What are the benefits of scalar quantization?

Quantization allows for vectors to be encoded in a lossy manner, thus reducing fidelity slightly with huge space savings.

#### How does scalar quantization work?

Scalar quantization takes each vector dimension and buckets them into some smaller data type.

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