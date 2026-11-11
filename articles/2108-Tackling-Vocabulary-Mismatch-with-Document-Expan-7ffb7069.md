---
title: 'Tackling Vocabulary Mismatch with Document Expansion'
company: Sease
tag: 工程相关
date: 2022-01-31
url: https://sease.io/2022/01/tackling-vocabulary-mismatch-with-document-expansion.html
account: 
origin: harvest3-202607
---
In the previous blogpost of this series, we looked at how to use BERT to improve search relevance by performing document re-ranking. The assumption of this approach is that the set of documents that need to be re-ranked, also known as candidates, contains the largest number of documents relevant to the query. We say that retrieving candidates is a recall-oriented task, since the following step, driven by a complex neural-based approach, is the one in charge of ordering the list from highest to lowest relevance.

Traditional inverted index-based approaches are still widely used in production systems to perform candidate generation, since those are particularly efficient and mature technologies, making them ideal for scaling when dealing with billions of documents.   
Unfortunately, carrying out search efficiently with an inverted index also means being constrained by exact lexical matches between query and document terms. For this reason, these retrieval models fail at matching related terms, causing the **vocabulary mismatch problem**.

## The Vocabulary Mismatch Problem

Vocabulary mismatch [[1]](https://dl.acm.org/doi/10.1145/32206.32212) is that phenomenon that takes place when the **query-document relevance is not correctly estimated** due to missing exact lexical match of the query tokens into the documents. A vocabulary mismatch can happen when users’ intents are expressed using different words from the ones employed by the authors of the relevant documents.

A very severe consequence of the vocabulary mismatch problem is that **it affects the whole retrieval pipeline**. A relevant document that has no overlapping terms with a query will not be retrieved by the above-mentioned candidate generation step, and hence will never be evaluated and reranked by any of the downstream neural models. This causes a dramatic loss in effectiveness for missing semantically relevant documents that the neural reranker would have been able to rank correctly, but that instead, the lexical system has filtered out before.

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Vocabulary-mismatch.png?resize=800%2C418&ssl=1)

In the above figure, we can see how vocabulary mismatch not only filters out a relevant document, but a completely unrelevant one is better matched just based on its lexical similarity with the query. This is a very simple example but gives the idea of the kind of disasters that vocabulary mismatch could generate.

## Query Expansion

Query expansion is a commonly used approach to mitigating the vocabulary mismatch problem. The idea is that the query is expanded to include synonyms and semantically related terms. This is because the way users express concepts differs from the way they appear in the corpus.

However, **query expansion has several disadvantages and problems**. First of all, it **makes the query cost higher**. Running a query with many terms is generally much more expensive and could potentially take too long than what is considered acceptable for the user, so exceeding the service latency constraints.

Another problem is represented by **topic drifting**, that is, the change in the query’s topic to an unintended direction. There could be several reasons causing this issue, such as an erroneous extraction of additional query terms, a biased query term weighting method, or a biased retrieval model.

Finally, the reason why query expansion is generally hard to perform correctly is intrinsic to the characteristics of the average query of a search engine. Queries, in contrast to the documents of the corpus, are small sets of terms that **carry very little context**. It becomes very difficult, even for humans, to extrapolate a context or find semantically related terms from such a short text.

To overcome or reduce some of these problems, methods for query expansion that imply document collection analysis were proposed. As an example, a number of methods judge the top documents retrieved using the unexpanded query and use this feedback information to expand the query with additional terms. This is so-called pseudo-relevance feedback (PRF). As a result, the expansion mechanism can rely on additional longer text to infer the real meaning of a query, but more work is involved making the whole process even slower.

## Document Expansion

An alternative to query expansion is document expansion, which reformulates the text of the documents being searched rather than the text of the query.

Document expansion, in contrast to query expansion, **can be more beneficial**. First, the documents are typically much longer than queries and thus **provide more context** to the language model to select expansion terms. This is true even when dealing with passages or just short sentences as contextualized language models deal better with text written in natural language compared to a bag of keywords.

Furthermore, it **can be performed offline**, while indexing the documents. Document expansion is an embarrassingly parallel task, where each document can be expanded in isolation and does not depend on others, allowing for multi-threaded executions which can be spawned on multiple instances.

Finally, expanding a document with additional terms or sentences translates into inverted indexes with posting lists that are on average longer. Although expanding documents also means slower query processing, thanks to popular early termination and dynamic pruning optimizations for query processing, this effect is much less pronounced than in the query expansion case making the former a **more efficient choice**.

Modern deep-learning models can help with performing document expansion. We present two very recent approaches which make use of **transformer-based neural models to infer additional text** related to the original document.

## Document Expansion by Query Prediction

The first attempt to perform document expansion using a neural network is actually very recent and dates back to 2019. The approach proposed by Nogueira et al. [[2]](https://arxiv.org/pdf/1904.08375.pdf) was initially referred to as **Doc2Query** and the idea is very simple. A model is trained to learn the queries that have the potential to find the document relevant. Basically for each document, the model can produce a list of an undefined number of related queries.

The model used to perform this task is a sequence-to-sequence model, trained with a dataset of relevant **query-document pairs.**   
**The documents of a corpus are expanded by simply appending** at the end a number of generated queries. Then the new documents are indexed and queried as normal using the unchanged pipeline of the search engine. This expansion procedure can be seen as an additional preprocessing step and the new index is just a **drop-in replacement**.

Subsequently, Doc2Query work has been extended and the transformer model used to predict new queries has been replaced with a T5 model, which is a pre-trained encoder-decoder model particularly effective for text generation. We refer to this optimized version of Doc2Query as **Doc2Query-T5** or **DocT5Query** [[3]](https://cs.uwaterloo.ca/~jimmylin/publications/Nogueira_Lin_2019_docTTTTTquery-v2.pdf).

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/dco2query.png?resize=800%2C527&ssl=1)

Doc2Query can be seen as a two-fold approach:

– (**rewrite**) By adding terms that are already part of the document, it rewrites their frequencies.   
– (**inject**) Furthermore, it injects into the document new terms, originally not part of it.

In the table below we can see that both components independently improve the quality of the ranking with respect to standard BM25, but using both in conjunction increases the gap even further.

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Picture1.png?resize=480%2C155&ssl=1)

## Document Expansion by Token Importance Prediction

Doc2Query is not the only method to exploit Deep Learning to perform document expansion.

The idea behind token importance prediction is simple. The Deep model employed takes as input a document and outputs a **token likelihood distribution over the vocabulary**. We can say that, given a text, it **estimates the terms in the vocabulary that are more likely to be related** to the document. For each document, we select the top terms from the vocabulary which do not appear in the original document and append them to the end of it.

The model architecture is composed of a simple linear layer placed on top of a standard contextualized model. The linear layer is there to project the 768-long CLS token embedding into a vector embedding that has the same length as the vocabulary. Each value of the output vector is a floating-point number indicating the importance of the vocabulary term at the corresponding position.

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Untitled-2021-12-13-1817.png?resize=460%2C1024&ssl=1)

This approach was initially introduced by Zhuang and Zuccon in 2021 [[4]](http://ielab.io/publications/pdfs/arvin2021tilde.pdf) and goes under the name of **TILDE**.

## Implementation

In this section, we are going to see how to perform document expansion on a given text by using previously fine-tuned models. In this section, we are not going to see how to fine-tune these models, but just how to leverage the fine-tuned models released by the authors of the two papers. However, It was experimentally observed that these models are quite effective on new data as they generalize quite well.

## DocT5Query

The following is a code snippet to predict queries given a document using the T5-based Doc2Query approach, also referred to as DocT5Query. This code is based on the **T5ForConditionalGeneration** model from the [HuggingFace Transformers library](https://github.com/huggingface/transformers). We also use the official fine-tuned [model](https://huggingface.co/castorini/doc2query-t5-base-msmarco) released by the original authors on the HuggingFace model hub.

```
				
					import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
tokenizer = T5Tokenizer.from_pretrained('castorini/doc2query-t5-base-msmarco')
model = T5ForConditionalGeneration.from_pretrained('castorini/doc2query-t5-base- msmarco')
model.eval().to(device)

# we need set how many questions per document we want to predict
num_queries = 10

# the document content
document = "..."

input_ids = tokenizer.encode(document, return_tensors='pt').to(device)
learned_queries = model.generate( 
    input_ids=input_ids,
    max_length=64,
    do_sample=True,
    num_return_sequences=num_queries)
    
# we need to decode the predicted token IDs to text for learned_query in learned_queries:
    tokenizer.decode(learned_query, skip_special_tokens=True)
				
			
```

## TILDE

In this code snippet, we are going to perform predictions at the token level. The code relies on the **BertLMHeadModel** from the [HuggingFace Transformers library](https://github.com/huggingface/transformers). We also use the official fine-tuned [model](https://huggingface.co/ielab/TILDE) released by the original authors on the HuggingFace model hub.

```
				
					import torch
from transformers import BertLMHeadModel, BertTokenizer
import numpy as np 

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = BertLMHeadModel.from_pretrained("ielab/TILDE")
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model.eval().to(device)

# we need set how many terms per document we want to predict 
num_terms = 100 

# the document content
document = "..."
encode = tokenizer(document, return_tensors='pt').to(device)

with torch.no_grad():
      logits = model(**encode, return_dict=True).logits[:, 0]
      batch_selected = torch.topk(logits, num_terms).indices.cpu().numpy()

for i, selected in enumerate(batch_selected):
      expand_term_ids = np.setdiff1d(selected, encode.input_ids.cpu().numpy()[i], 
assume_unique=True)
      expand_terms = tokenizer.decode(selected)
				
			
```

## Summary

In this blog post, we have looked at how we can **attenuate vocabulary mismatch** leveraging document expansion using two transformer-based approaches. In particular, we have looked at a related-query generation mechanism and a token-based expansion approach.

We have seen how to perform inference of additional content by using fine-tuned models which were released by the original authors of the two methods. Clearly, **fine-tuning on your own data allows you to better exploit the power of these models**, thus we recommend spending some time collecting training data. If you want to know more about document expansion feel free to [get in touch](mailto:info@sease.io).

Finally, if you are interested in hearing more about the use of Deep Learning applied to Search stay tuned for our next episode on learning a ranking function for traditional inverted indexes.

## Need Help With This Topic?​​

If you’re struggling with Document Expansion, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Document Expansion, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)