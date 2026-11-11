---
title: 'Have Neural Networks Killed the Inverted Index?'
company: Sease
tag: 索引构建
date: 2022-04-28
url: https://sease.io/2022/04/have-neural-networks-killed-the-inverted-index.html
account: 
origin: harvest3-202607
---
In the first blog post dedicated to the use of Deep Learning to improve search relevance, we have looked at [how to leverage BERT to perform document reranking](https://sease.io/2021/12/using-bert-to-improve-search-relevance.html). Unfortunately, the cross-entropy architecture presented in that blog post is still too expensive to run on a large number of documents and so we would still need to rely on a solution to perform the retrieval of a certain number of candidates.

In this episode, we are going to talk about DeepImpact [[1]](https://arxiv.org/pdf/2104.12016.pdf), a new document term-weighting scheme suitable for efficient retrieval using a standard inverted index.

## Motivations

As we saw in the previous blog post of this series, DocT5Query is a [document expansion](https://sease.io/2022/01/tackling-vocabulary-mismatch-with-document-expansion.html) method to enrich the original document collection with expansion terms. It can be seen as a two-fold approach. By adding terms that are already part of the document, it rewrites their frequencies. Moreover, it injects into the passage new terms, originally not part of the document, in order to address the vocabulary mismatch problem.

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/01/doct5q.jpg?resize=512%2C143&ssl=1)

Different contributions to effectiveness metrics of DocT5Query on the MSMARCO passage ranking collection.

The table above summarizes the effect of DocT5Query when applied to the MS MARCO passage ranking collection [[2]](https://microsoft.github.io/msmarco/Datasets), and isolates the two contributions. As we can see, the Inject contribution is the one that has a more beneficial effect on recall. This can be explained by the fact that the newly injected terms allow the query to match more documents that are relevant, while the Rewrite components provide a better ranking of the results.

Clearly, the Rewrite does not follow any particular policy on the way the document term frequencies are rewritten, but it mostly depends on the queries predicted by the DocT5Query approach. This motivates the DeepImpact approach, where new terms are first injected leveraging DocT5Query, and then the right impact scores for both old and newly injected terms are learned (instead of relying on simple frequency as for BM25).

## Architecture of DeepImpact

The overall architecture of DeepImpact is depicted below. It consists of a contextualized language model and a Multilayer Perceptron (MLP) with ReLU activations to produce a single-value score for each unique term in the document, representing its impact.

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/01/arch.jpg?resize=800%2C657&ssl=1)

The query-document score is computed as the sum of the impact scores predicted by the model of the document terms that are lexically matching the keywords in the query.

**Training**: The model is trained using triples, consisting of a query, a relevant passage, and a presumed non-relevant passage per sample. For each triple, two scores for the corresponding two documents are computed by converting each document into a list of scores and summing up only the ones corresponding to the document terms matching the query The model is then optimized via pairwise softmax cross-entropy loss over the computed scores of the documents.

**Index generation**: Following the training phase, DeepImpact can leverage the learned term-weighting scheme to predict the semantic importance of each token of the documents without the need for queries. Each document is represented as a list of term-score pairs, which are converted into an inverted index. The score is first quantized and then stored as a replacement for the term frequency.

**Query processing**: The index can then be deployed and searched as usual for efficient query processing but, instead of relying on the term frequency to compute a BM25 score, the query document score can be computed just by summing up each term impact contribution.

## Timeline

The popular BM25 ranking function dates back to 1994 when it was first presented by Robertson et al. [[3]](https://trec.nist.gov/pubs/trec3/papers/city.ps.gz). It is the de-facto standard because of its multiple advantages. First, it does not need any specific training since it computes the relevance by looking at frequencies of terms in documents relative to their overall frequency in the text collection. Furthermore, it is very efficient since computing the query-document relevance score can be done with a handful of arithmetic operations.

The dominance of BM25 has been undisputed for a very long period of time and only recently, with the advent of Deep Learning, things seem to start to be changing. In 2019 DeepCT and DocT5Query came out. The former is also a term weighting scheme, but other than not being very effective, a ground truth term weight for every word is needed, not being able to automatically adapt the training for the downstream objective of identifying relevant documents.

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/01/timeline.jpg?resize=800%2C224&ssl=1)

DeepImpact solves this issue since it relies on pairwise cross-entropy loss, similarly to the fine-tuning approach presented [here](https://sease.io/2021/12/using-bert-to-improve-search-relevance.html). Instead of learning independent term-level scores without taking into account the term co-occurrences in the document, as in DeepCT, or relying on unchanged BM25 scoring, as in DocT5Query, DeepImpact directly optimizes the sum of query term impacts to maximize the score difference between relevant and non-relevant passages for the query.

A few months after DeepImpact was released, other approaches were proposed, such as uniCOIL [[4]](https://arxiv.org/abs/2106.14807) and SPLADEv2 [[5]](https://arxiv.org/abs/2109.10086). These methods, as we are going to see, are more effective than DeepImpact, but their model architecture is also more complex. Both of them not only use document impacts to compute the relevance score, but they leverage query term weights. Furthermore, SPLADEv2 also uses query expansion in addition to document expansion and proposes to train the model with knowledge distillation.

We can group DeepImpact, uniCOIL, and SPLADEv2 in the same category which we named Learned Term Impact (LTI) frameworks.

## Results

The following plot shows a comparison of all the aforementioned methods on MS MARCO Dev Queries, where we can immediately see that the LTI methods outperform all the previous ones by a large margin. SPLADEv2 is present twice since one is the model trained with knowledge distillation. Considering that knowledge distillation could be applied to any of the LTI approaches, for a fair comparison we should look at the results with and without knowledge distillation in separate plots.

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/01/plot-deepimpact.png?resize=800%2C591&ssl=1)

Both uniCOIL and SPLADEv2 rely on a more complex architecture making them more effective but, at the same time, slower. In particular, SPLADEv2 is over ten times slower than DeepImpact, turning to be an unfeasible approach for large-scale production systems.

Furthermore, it is worth mentioning that the quality improvement obtained by uniCOIL and SPLADEv2 is less evident (or even absent) when these methods are used on a very different set of queries, such as the TREC DL 2019 query log. We can see that SPLADEv2 becomes worse than the other two methods and uniCOIL is only negligibly better than DeepImpact while being more than 2 times slower.

This behavior probably originates from the fact that since uniCOIL and SPLADEv2 are more complex models, they tend to overfit the data and give them less ability to generalize on new data.

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/02/trec2019.jpg?resize=800%2C318&ssl=1)

## Conclusions

In this blog post, we have looked at DeepImpact, a new first-stage retrieval method that leverages a combination of a traditional inverted index and contextualized language models for efficient retrieval. By estimating semantic importance, DeepImpact produces a single value impact score for each token of a document collection.

## Implementation of DeepImpact

In this section, we are going to see a simplified implementation of DeepImpact. Specifically, we are going to see how to define the model and what a pairwise training step looks like.

In particular, we are going to see how to define the model and how to compute query-document relevance scores. We are going to use Pytorch [[6]](https://pytorch.org/) and HuggingFace Transformers [[7]](https://github.com/huggingface/transformers).

## Model

In the following snippet, we are going to define our model. We derive our model from the BertPreTrainedModel class provided by the transformers library. The contextualized language model encoder is just a BertModel, while the impact score encoder is defined as a sequence of two linear layers with ReLU activations and a dropout layer in the middle.

```
				
					from transformers import *

class DeepImpact(BertPreTrainedModel):
    def __init__(self, config):
        super(DeepImpact, self).__init__(config)
        self.bert = BertModel(config)
        self.impact_score_encoder = nn.Sequential(
            nn.Linear(config.hidden_size, config.hidden_size),
            nn.ReLU(),
            nn.Dropout(config.hidden_dropout_prob),
            nn.Linear(config.hidden_size, 1),
            nn.ReLU()
        )
        self.init_weights()
				
			
```

## Impact score computation

To compute the query-document relevance score we need to compute a query\_mask, which is a bit vector with bits set to positions where the document terms are matched with the query. The encoded document (composed of input\_ids, attention\_mask, and token\_type\_ids) goes through BERT and the impact score encoder. Finally, the scores generated for all the terms in the document are filtered using the query mask, such that only the scores of the matching terms get summed up.

```
				
					def forward(self, input_ids, attention_mask, token_type_ids, query_mask):
    outputs = self.bert.forward(input_ids, attention_mask=attention_mask, 
token_type_ids=token_type_ids)[0]
    doc_scores = self.impact_score_encoder(outputs)
    return (query_mask * doc_scores).sum(dim=1)
				
			
```

## Need Help With This Topic?​​

If you’re struggling with DeepImpact, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with DeepImpact, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)