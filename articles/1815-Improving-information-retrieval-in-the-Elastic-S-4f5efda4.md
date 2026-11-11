---
title: 'Improving information retrieval in the Elastic Stack: Introducing Elastic Learned Sparse Encoder, our new retrieval model'
company: Elastic
tag: 召回
date: 2023-06-21
url: https://www.elastic.co/search-labs/blog/elastic-learned-sparse-encoder-elser-retrieval-performance
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Improving information retrieval in the Elastic Stack: Introducing Elastic Learned Sparse Encoder, our new retrieval model

Learn about the Elastic Learned Sparse Encoder (ELSER), its retrieval performance, architecture, and training process.

June 21, 2023

[Thomas Veasey](/search-labs/author/thomas-veasey)[Quentin Herreros](/search-labs/author/quentin-herreros)

[ML Research](/search-labs/blog/category/ml-research)[AI](/search-labs/blog/category/ai)

Part of the series:

[Improving information retrieval in the Elastic Stack](/search-labs/blog/series/improving-information-retrieval-in-the-elastic-stack)

In this series

Share

In this blog, we discuss the work we've been doing to augment Elastic's out-of-the-box retrieval with a pre-trained language model: the Elastic Learned Sparse Encoder (ELSER).

In our [previous blog post](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-benchmarking-passage-retrieval) in this series, we discussed some of the challenges applying dense models to retrieval in a zero-shot setting. This is well known and was highlighted by the BEIR benchmark, which assembled diverse retrieval tasks as a proxy to the performance one might expect from a model applied to an unseen data set. Good retrieval in a zero-shot setting is exactly what we want to achieve, namely a one-click experience that enables textual fields to be searched using a pre-trained model.

This new capability fits into the Elasticsearch \_search endpoint as just another query clause, a text\_expansion query. This is attractive because it allows search engineers to continue to tune queries with all the tools Elasticsearch already provides. Furthermore, to truly achieve a one-click experience, we've integrated it with the new [Elasticsearch Relevance Engine](https://www.elastic.co/enterprise-search/generative-ai). However, rather than focus on the integration, this blog digs a little into ELSER's model architecture and the work we did to train it.

We had another goal at the outset of this project. The natural language processing (NLP) field is fast moving, and new architectures and training methodologies are being introduced rapidly. While some of our users will keep on top of the latest developments and want full control over the models they deploy, others simply want to consume a high quality search product. By developing our own training pipeline, we have a playground for implementing and evaluating the latest ideas, such as new [retrieval relevant pre-training tasks](https://arxiv.org/pdf/2207.02578.pdf) or more [effective distillation tasks](https://arxiv.org/pdf/2204.13679.pdf), and making the best ones available to our users.

Finally, it is worth mentioning that we view this feature as complementary to the existing model deployment and vector search capabilities in the Elastic Stack, which are needed for those more custom use cases like cross-modal retrieval.

## ELSER performance results

Before looking at some of the details of the architecture and how we trained our model, the [Elastic Learned Sparse Encoder (ELSER)](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html), it's interesting to review the results we get, as ultimately the proof of the pudding is in the eating.

[As we discussed before](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-benchmarking-passage-retrieval), we use a subset of BEIR to evaluate our performance. While this is by no means perfect, and won't necessarily represent how the model behaves on your own data, we at least found it challenging to make significant improvements on this benchmark. So we feel confident that improvements we get on this translate to real improvements in the model. Since absolute performance numbers on benchmarks by themselves aren't particularly informative, it is nice to be able to compare with other strong baselines, which we do below.

The table below shows the performance of Elastic Learned Sparse Encoder compared to Elasticsearch's BM25 with an English analyzer broken down by the 12 data sets we evaluated. We have 10 wins, 1 draw, and 1 loss and an average improvement in NDCG@10 of 17%.

![NDCG@10 for BEIR data sets for BM25 and Elastic Learned Sparse Encoder (referred to as “ELSER” above, note higher is better)](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb686af5ae31c40a7/6a170223cdacbf35b37d2890/36fcb82c7e9e22195e43a5fb93ff3a197cee9e8a-1440x271.png)

NDCG@10 for BEIR data sets for BM25 and Elastic Learned Sparse Encoder (referred to as “ELSER” above, note higher is better)

In the following table, we compare our average performance to some other strong baselines. The Vespa results are based on a linear combination of BM25 and their implementation of ColBERT as reported [here](https://blog.vespa.ai/improving-zero-shot-ranking-with-vespa-part-two/), the Instructor results are from [this](https://arxiv.org/pdf/2212.09741.pdf) paper, the SPLADEv2 results are taken from this [paper](https://arxiv.org/pdf/2109.10086.pdf) and the OpenAI results are reported [here](https://openai.com/blog/new-and-improved-embedding-model). Note that we've separated out the OpenAI results because they use a different subset of the BEIR suite. Specifically, they average over ArguAna, Climate FEVER, DBPedia, FEVER, FiQA, HotpotQA, NFCorpus, QuoraRetrieval, SciFact, TREC COVID and Touche. If you follow that link, you will notice they also report NDCG@10 expressed as a percentage. We refer the reader to the links above for more information on these approaches.

![Average NDCG@10 for BEIR data sets vs. various high quality baselines (higher is better). Note: OpenAI chose a different subset, and we report our results on this set separately.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt00a11c8b4338ade3/6a1702241949f76119e7a896/8ecb29edc0b4b1cd169320de06325d6fa0dd7c59-829x137.png)

Average NDCG@10 for BEIR data sets vs. various high quality baselines (higher is better). Note: OpenAI chose a different subset, and we report our results on this set separately.

Finally, we note it has been widely observed that an ensemble of statistical (a la BM25) and model based retrieval, or hybrid search, tends to outperform either in a zero-shot setting. Already in 8.8, Elastic allows one to do this for text\_expansion with linear boosting and this works well if you calibrate to your data set. We are also working on [Reciprocal Rank Fusion](https://research.google/pubs/pub36196/) (RRF), which performs well without calibration. Stay tuned for our next blog in this series, which will discuss hybrid search.

Having seen how ELSER performs, we next discuss its architecture and some aspects of how it is trained.

## What are learned sparse models and why are they attractive?

We showed [in our previous blog post](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-benchmarking-passage-retrieval) that, while very effective if fine-tuned, dense retrieval tends not to perform well in a zero-shot setting. By contrast [cross-encoder architectures](https://www.sbert.net/examples/applications/cross-encoder/README.html), which don't scale well for retrieval, tend to learn robust query and document representations and work well on most text. It has been [suggested](https://arxiv.org/pdf/2004.12832.pdf) that part of the reason for this difference is the bottleneck of the query and document interacting only via a relatively low dimensional vector “dot product.” Based on this observation, a couple of model architectures have been recently proposed that try to reduce this bottleneck — these are ColBERT and SPLADE.

From our perspective, SPLADE has some additional advantages:

1. Compared to ColBERT, it is extremely storage efficient. Indeed, we find that document passages expand to about 100 tokens on average and we've seen approximate size parity with normal text indices.
2. With some [caveats](https://arxiv.org/pdf/2110.11540.pdf), retrieval can make use of inverted indices for which we already have very mature implementations in Lucene. Compared to ANN, these use memory extremely efficiently.
3. It provides natural controls as it is being trained that allow us to trade retrieval quality for retrieval latency. In particular, the FLOPS regularizer, which we discuss below, allows one to add a term to the loss for the expected retrieval cost. We plan to take advantage of this as we move toward GA.

One last clear advantage compared to dense retrieval is that SPLADE allows one a simple and compute efficient route to highlight words generating a match. This simplifies surfacing relevant passages in long documents and helps users better understand how the retriever is working. Taken together, we felt that these provided a compelling case for adopting the SPLADE architecture for our initial release of this feature.

There are multiple good detailed descriptions of this architecture — if you are interested in diving in, [this](https://europe.naverlabs.com/blog/splade-a-sparse-bi-encoder-bert-based-model-achieves-effective-and-efficient-first-stage-ranking/), for example, is a nice write up by the team that created the model. In very brief outline, the idea is rather than use a distributed representation, say averaging BERT token output embeddings, instead use the token logits, or [log-odds](https://en.wikipedia.org/wiki/Logit) the tokens are predicted, for masked word prediction.

When language models are used to predict masked words, they achieve this by predicting a probability distribution over the tokens of their vocabulary. The BERT vocabulary, for WordPiece, contains many common real words such as cat, house, and so on. It also contains common word endings — things like ##ing (with the ## simply denoting it is a continuation). Since words can't be arbitrarily exchanged, relatively few tokens will be predicted for any given mask position. SPLADE takes as a starting point for its representation of a piece of text the tokens most strongly predicted by masking each word of that text. As noted, this is a naturally disentangled or sparse representation of that text.

![where can i hire canoes](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7d5909f75676faca/6a170225e8fbce0aec39fadb/6409db21d3425d2d8a0b08b79e7825fe8f16d70a-841x469.png)

It is reasonable to think of these token probabilities for word prediction as roughly capturing contextual synonyms. This has led people to view learned sparse representations, such as SPLADE, as something close to automatic synonym expansion of text, and we see this in multiple online explanations of the model.

In our view, this is at best an oversimplification and at worst misleading. SPLADE takes as the starting point for fine-tuning the maximum token logits for a piece of text, but it then trains on a relevance prediction task, which crucially accounts for the interaction between all shared tokens in a query and document. This process somewhat re-entangles the tokens, which start to behave more like components of a vector representation (albeit in a very high dimensional vector space).

We explored this a little as we worked on this project. We saw as we tried removing low score and apparently unrelated tokens in the expansion post hoc that it reduced all quality metrics, including precision(!), in our benchmark suite. This would be explained if they were behaving more like a distributed vector representation, where zeroing individual components is clearly nonsensical. We also observed that we can simply remove large parts of BERT's vocabulary at random and still train highly effective models as the figure below illustrates. In this context, parts of the vocabulary must be being repurposed to account for the missing words.

![Margin MSE validation loss for student models with different vocabulary sizes](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt436f4002c42b0564/6a170227a929cfd31cae0816/76015fb4378bfc66baf343472566bd65424e00ce-1440x902.png)

Margin MSE validation loss for student models with different vocabulary sizes

Finally, we note that unlike say generative tasks where size really does matter a great deal, retrieval doesn't as clearly benefit from having huge models. We saw in the result section that this approach is able to achieve near state-of-the-art performance with only 100M parameters, as compared to hundreds of millions or even billions of parameters in some of the larger generative models. Typical search applications have fairly stringent requirements on query latency and throughput, so this is a real advantage.

## Exploring the training design space for ELSER

In our first [blog](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-search-relevance), we introduced some of the ideas around training dense retrieval models. In practice, this is a multi stage process and one typically picks up a model that has already been pre-trained. This pre-training task can be rather important for achieving the best possible results on specific downstream tasks. We don't discuss this further because to date this hasn't been our focus, but note in passing that like many current effective retrieval models, we start from a [co-condenser pre-trained model](https://arxiv.org/pdf/2108.05540.pdf).

There are many potential avenues to explore when designing training pipelines. We explored quite a few, and suffice to say, we found making consistent improvements on our benchmark was challenging. Multiple ideas that looked promising on paper didn't provide compelling improvements. To avoid this blog becoming too long, we first give a quick overview of the key ingredients of the training task and focus on one novelty we introduced, which provided the most significant improvements. Independent of specific ingredients, we also made some qualitative and quantitative observations regarding the role of the FLOPS regularization, which we will discuss at the end.

When training models for retrieval, there are two common paradigms: contrastive approaches and distillation approaches. We adopted the distillation approach because this was shown to be very effective for training SPLADE in [this](https://arxiv.org/pdf/2109.10086.pdf) paper. The distillation approach is slightly different from the common paradigm, which informs the name, of shrinking a large model to a small, but almost as accurate, “copy.” Instead the idea is to distill the ranking information present in a cross-encoder architecture. This poses a small technical challenge: since the representation is different, it isn't immediately clear how one should mimic the behavior of the cross-encoder with the model being trained. The standard idea we used is to present both models with triplets of the form (query, relevant document, irrelevant document). The teacher model computes a score margin, namely score(query,relevant  document)−score(query  irrelevant  document)score(query, relevant\;document) - score(query\;irrelevant\;document)score(query,relevantdocument)−score(queryirrelevantdocument), and we train the student model to reproduce this score margin using MSE to penalize the errors it makes.

Let's think a little about what this process does since it motivates the training detail we wish to discuss. If we recall that the interaction between a query and document using the SPLADE architecture is computed using the dot product between two sparse vectors, of non-negative weights for each token, then we can think about this operation as wanting to increase the similarity between the query and the higher scored document weight vectors. It is not 100% accurate, but not misleading, to think of this as something like “rotating” the query in the plane spanned by the two documents' weight vectors toward the more relevant one. Over many batches, this process gradually adjusts the weight vectors starting positions so the distances between queries and documents captures the relevance score provided by the teacher model.

This leads to an observation regarding the feasibility of reproducing the teacher scores. In normal distillation, one knows that given enough capacity the student would be able to reduce the training loss to zero. This is not the case for cross-encoder distillation because the student scores are constrained by the properties of a metric space induced by the dot product on their weight vectors. The cross-encoder has no such constraint. It is quite possible that for particular training queries q1q\_1q1​ and q2q\_2q2​ and documents d1d\_1d1​ and d2d\_2d2​ we have to simultaneously arrange for q1q\_1q1​ to be close to d1d\_1d1​ and d2d\_2d2​, and q2q\_2q2​ to be close to d1d\_1d1​ but far from d2d\_2d2​. This is not necessarily possible, and since we penalize the MSE in the scores, one effect is an arbitrary reweighting of the training triplets associated with these queries and documents by the minimum margin we can achieve.

One of the observations we had while working on training ELSER was the teacher was far from infallible. We initially observed this by manually investigating query-relevant document pairs that were assigned unusually low scores. In the process, we found objectively misscored query-document pairs. Aside from manual intervention in the scoring process, we also decided to explore introducing a better teacher.

Following the literature, we were using [MiniLM L-6](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2) from the SBERT family for our initial teacher. While this shows strong performance in multiple settings, there are better teachers, based on their ranking quality. One example is a ranker based on a large generative model: [monot5 3b](https://huggingface.co/castorini/monot5-3b-msmarco-10k). In the figure below, we compare the query-document score pair distribution of these two models. The monot5 3b distribution is clearly much less uniform, and we found when we tried to train our student model using its raw scores the performance saturated significantly below using MiniLM L-6 as our teacher. As before, we postulated that this was down to many important score differences in the peak around zero getting lost with training worried instead about unfixable problems related to the long lower tail.

![Monot5 3b and MiniLM L-6 score distributions on a matched scale for a random sample of query-document pairs from the NQ data set. Note: the X-axis does not show the actual scores returned by either of the models.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc39a226f1a4d90b9/6a170229dc55debf53e00c99/623bdbe08255e706a4db0e56b2f6b54ca07c16c3-819x507.png)

Monot5 3b and MiniLM L-6 score distributions on a matched scale for a random sample of query-document pairs from the NQ data set. Note: the X-axis does not show the actual scores returned by either of the models.

It is clear that all rankers are of equivalent quality up to monotonic transforms of their scores. Specifically, it doesn't matter if we use score(query,document)score(query, document)score(query,document) or f(score(query,document))f(score(query, document))f(score(query,document)) provided f(⋅)f(\cdot)f(⋅) is a monotonic increasing function; any ranking quality measure will be the same. However, not all such functions are equivalently effective teachers. We used this fact to smooth out the distribution of monot5 3b scores, and suddenly our student model trained and started to beat the previous best model. In the end, we used a weighted ensemble of our two teachers.

Before closing out this section, we want to briefly mention the FLOPS regularizer. This is a key ingredient of the improved SPLADE v2 training process. It was proposed in [this](https://arxiv.org/pdf/2004.05665.pdf) paper as a means of penalizing a metric directly related to the compute cost for retrieval from an inverted index. In particular, it encourages tokens that provide little information for ranking to be dropped from the query and document representations based on their impact on the cost for retrieving from an inverted index. We had three observations:

1. Our first observation was that the great majority of tokens are actually dropped while the regularizer is still warming up. In our training recipe, the regularizer uses quadratic warm up for the first 50,000 batches. This means that in the first 10,000 batches, it is no more than 1/25th its terminal value, and indeed we see that the contribution to the loss from MSE in the score margin is orders of magnitude larger than the regularization loss at this point. However, during this period the number of query and document tokens per batch activated by our training data drops from around 4k and 14k on average to around 50 and 300, respectively. In fact, 99% of all token pruning happens in this phase and seems largely driven by removing tokens which actually hurt ranking performance.
2. Our second observation was that we found it contributes to ELSER's generalization performance for retrieval. Both turning down the amount of regularization and substituting regularizers that induce more sparseness, such as the sum of absolute weight values, reduced average ranking performance across our benchmark.
3. Our final observation was that larger batches and diverse batches both positively impacted retrieval quality; we tried by contrast query clustering with in-batch negatives.

So why could this be, since it is primarily aimed at optimizing retrieval cost? The FLOPS regularizer is defined as follows: it first averages the weights for each token in the batch across all the queries and separately the documents it contains, it then sums the squares of these average weights. If we consider that the batch typically contains a diverse set of queries and documents, this acts like a penalty that encourages something analogous to stop word removal. Tokens that appear for many distinct queries and documents will dominate the loss, since the contribution from rarely activated tokens is divided by the square of the batch size. We postulate that this is actually helping the model to find better representations for retrieval. From this perspective, the fact that the regularizer term only gets to observe the token weights of queries and documents in the batch is undesirable. This is an area we'd like to revisit.

## Conclusion

We have given a brief overview of the model, the Elastic Learned Sparse Encoder (ELSER), its rationale, and some aspects of the training process behind the feature we're releasing in a technical preview for the new text\_expansion query and integrating with the new [Elasticsearch Relevance Engine](https://www.elastic.co/enterprise-search/generative-ai). To date, we have focused on retrieval quality in a zero-shot setting and demonstrated good results against a variety of strong baselines. As we move toward GA, we plan to do more work on operationalizing this model and in particular around improving inference and retrieval performance.

Stay tuned for the next blog post in this series, where we'll look at combining various retrieval methods using hybrid retrieval as we continue to explore exciting new retrieval methods using Elasticsearch.

*The release and timing of any features or functionality described in this post remain at Elastic's sole discretion. Any features or functionality not currently available may not be delivered on time or at all.*

*Elastic, Elasticsearch and associated marks are trademarks, logos or registered trademarks of Elasticsearch N.V. in the United States and other countries. All other company and product names are trademarks, logos or registered trademarks of their respective owners.*

* **Part 1:** [Steps to improve search relevance](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-search-relevance)
* **Part 2:** [Benchmarking passage retrieval](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-benchmarking-passage-retrieval)
* **Part 3:** [Introducing Elastic Learned Sparse Encoder, our new retrieval model](https://www.elastic.co/blog/may-2023-launch-information-retrieval-elasticsearch-ai-model)
* **Part 4:** [Hybrid retrieval](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-hybrid)

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