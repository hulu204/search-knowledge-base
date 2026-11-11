---
title: 'Preconditioning Vectors: Making Elasticsearch VectorDB Better Binary Quantization work for every vector'
company: Elastic
tag: 索引构建
date: 2026-04-27
url: https://www.elastic.co/search-labs/blog/elasticsearch-bbq-preconditioning-vectors
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Preconditioning Vectors: Making Elasticsearch VectorDB Better Binary Quantization work for every vector

Modern quantization techniques can hurt recall when using older models or embeddings that aren’t normally distributed. Learn how preconditioning fixes these vectors through random orthogonal projection, making BBQ more effective and recovering recall.

April 27, 2026

[John Wagster](/search-labs/author/john-wagster)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

Elasticsearch as a vector database offers comprehensive quantization techniques like [Better Binary Quantization (BBQ)](https://www.elastic.co/search-labs/blog/optimized-scalar-quantization-elasticsearch). BBQ and other similarly modern quantization techniques compress vectors down to as little as a single bit per dimension, reducing memory use while retaining impressively accurate distance approximation. For vectors generated from deep learning models, such as Cohere models, this works really well; however, for other kinds of vectors, such as image data or histogram features, recall can be impacted heavily. Preconditioning fixes this by applying a random orthogonal rotation to your vectors before quantization, redistributing variance evenly across dimensions so every bit captures meaningful signal, in some cases improving recall by almost 75%.

Here, we’ll provide some intuition about the problem and how preconditioning solves it.

## The problem

BBQ quantizes each dimension of a vector independently: Values above the mean become 1, values below it become 0. This works well when every dimension carries roughly the same amount of information. Transformer-based embeddings tend to have this property naturally such that their dimensions are learned representations that distribute variance evenly.

But there are lots of real-world vectors that aren’t like this. Consider a 784-dimension vector representing a grayscale image, like in the Fashion-MNIST dataset. Some pixels near the center of the image, where the clothing actually appears, vary a lot across the dataset. However, other pixels, such as those near the corners, are mostly one color and barely vary at all. When BBQ quantizes these vectors, the high-variance dimensions lose precision because a single bit can't capture their range, while the low-variance dimensions become useless. The resulting quantized vectors are poor approximations of the originals, and recall suffers.

![Grid of sixteen grayscale images of clothing and accessories, each shown with a numeric label indicating its classification category.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte5690d4383e89397/6a17de8c7f6f1550ffc09a35/d7230d6d1067eb8b40f1f3e2e514388dc846473f-767x789.png)

Picture of a representation of Fashion-MNIST images. (credit: [geeksforgeeks.org](https://www.geeksforgeeks.org/deep-learning/how-to-load-fashion-mnist-dataset-using-pytorch/))

## Precondition

To fix the problem, we want to spread the information more evenly across dimensions so that each bit captures roughly the same amount of information.

Preconditioning applies a linear transformation to every vector before quantization. The transformation is an orthogonal rotation that reshuffles how information is distributed across dimensions without changing the distances between vectors. If you want to dig into the math, take a look at this in-depth analysis on [optimized scalar quantization (OSQ) with preconditioners](https://www.elastic.co/search-labs/blog/robust-optimized-scalar-quantization).

Here’s a graphic to help illustrate how preconditioning can help when applying quantization. This simplified two-dimensional diagram illustrates the idea that the orthogonal rotation helps to increase the spread, or range, of information that was previously quite compressed. While this two-dimensional animation is not an exact representation of preconditioning, it gives a good intuition for what roughly happens in higher dimensions where buckets of dimensions are transformed independently and a random projection can greatly improve the distribution. Imagine that the y-axis represents one pixel of our Fashion-MNIST corners that are primarily one shade with very low variance and the x-axis represents a pixel of clothing at the center of the image with very high variance. Without preconditioning, quantizing vectors to a single representative point is not a particularly good discriminator.

![Animated two‑dimensional diagram showing points moving under an orthogonal rotation, illustrating how the spread of values increases before quantization.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt2501f9f4a91b76be/6a17de8eaf47b65e32cdde75/40a3b20218bfd440f9d8f4aca991b31b83df759e-1080x608.gif)

### Let’s look at the data

Today, preconditioning is supported in [DiskBBQ](https://www.elastic.co/search-labs/blog/diskbbq-elasticsearch-introduction). Here’s a benchmark showing the impact when visiting different percentages of the total vector dataset.

Fashion-MNIST Recall (784 dimensions, 60K docs, 5x oversample, k: 10)

| Vectors visited | Baseline recall | Preconditioned recall | % Improvement |
| --- | --- | --- | --- |
| 0.5% | 0.45 | 0.77 | 71% |
| 3% | 0.49 | 0.77 | 57% |
| 5% | 0.50 | 0.87 | 74% |
| 10% | 0.55 | 0.91 | 65% |

GIST (960 dimensions, 1M docs, 5x oversample, k: 10)

| Vectors visited | Baseline recall | Preconditioned recall | % Improvement |
| --- | --- | --- | --- |
| 0.1% | 0.49 | 0.69 | 41% |
| 0.2% | 0.70 | 0.77 | 10% |
| 0.3% | 0.73 | 0.85 | 16% |
| 0.5% | 0.78 | 0.88 | 13% |

SIFT (128 dimensions, 1M documents, 5x oversample, k: 10)

| Vectors visited | Baseline recall | Preconditioned recall | % Improvement |
| --- | --- | --- | --- |
| 0.5% | 0.48 | 0.60 | 25% |
| 1% | 0.59 | 0.71 | 20% |
| 3% | 0.71 | 0.87 | 23% |
| 7% | 0.72 | 0.90 | 25% |

That’s a nice boost in recall; however, this boost comes with a cost. Applying it to all embeddings blindly is inefficient, causing ~2–4% overhead in query latencies with no improvement in recall for datasets that don’t need to be preconditioned. And upwards of 20% additional overhead at index time. For production use cases where you see initially low recall, you may want to evaluate the impact of preconditioning with your specific model and dataset.

## Here’s the how

Preconditioning is available for the `bbq_disk` index type. Simply set `precondition` to `true` in the `index_options`, like so:

```
{
  "mappings": {
    "properties": {
      "my_vector": {
        "type": "dense_vector",
        "dims": 784,
        "index_options": {
          "type": "bbq_disk",
          "precondition": true
        }
      }
    }
  }
}
```

Take a look at the [dense vector mapping](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector#dense-vector-params) docs for more details.

## Conclusion

BBQ is highly effective for deep learning embeddings, but it can be less effective with embeddings that have uneven variance across dimensions, as can occur in feature-engineered vectors. Preconditioning redistributes that variance so quantization can be more effective. On some datasets, like Fashion-MNIST, we see as much as a 74% improvement in recall!

For now, we’ve made preconditioning optional. Hopefully, you feel more capable of knowing when it may be beneficial so you try it out yourself. In the future, we plan to iterate on performance and automatically detect when to apply preconditioning.

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