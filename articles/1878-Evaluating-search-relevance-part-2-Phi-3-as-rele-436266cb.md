---
title: 'Evaluating search relevance part 2 - Phi-3 as relevance judge'
company: Elastic
tag: 评测
date: 2024-09-19
url: https://www.elastic.co/search-labs/blog/evaluating-search-relevance-part-2
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Evaluating search relevance part 2 - Phi-3 as relevance judge

Using the Phi-3 language model as a search relevance judge, with tips & techniques to improve the agreement with human-generated annotation.

September 19, 2024

[Thanos Papaoikonomou](/search-labs/author/thanos-papaoikonomou)[Thomas Veasey](/search-labs/author/thomas-veasey)

[ML Research](/search-labs/blog/category/ml-research)[Python](/search-labs/blog/category/python-programming)

Part of the series:

[Evaluating search relevance](/search-labs/blog/series/evaluating-search-relevance)

In this series

Share

In our [previous](https://www.elastic.co/search-labs/blog/evaluating-search-relevance-part-1) post we discussed the importance of obtaining deep markups of search results for effective evaluation. We showed that even widely used benchmarks, like those comprising the MTEB retrieval challenge, have relatively few judgments in the top 10 result sets returned by many state of the art retrieval models. Furthermore, we did some exploration regarding how missing judgments can lead to incorrect evaluation of model quality, identifying a high proportion of false negatives in the MS MARCO benchmark for the queries we analyzed.

Large generative models (LLMs) hold the promise of providing many capabilities in a zero- or few-shot fashion. In the context of search relevance, this amounts to providing expert judgments of the relevance of supplied documents to a query. This can help to significantly lower the effort needed to obtain high quality benchmark datasets for your own search systems. However, as with all tasks involving LLMs there are many design choices and these can significantly affect the quality of results one obtains.

In this post, we present a case study of tuning a [Phi-3-mini](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct) pipeline to provide the best possible agreement with human relevance judgments on the same sample of 100 queries we used to explore missing markup in MS MARCO in our previous post.

## Phi models: A short introduction

Phi-3 is a recent generation of Small Language Models (SLMs) from [Microsoft](https://arxiv.org/pdf/2404.14219). It was shown that properly curated collections of publicly available web data combined with LLM-created synthetic data, enabled "small" language models to match the performance of much larger language models (in some cases 25 times larger) trained on regular data.

The release of Phi models under the name "Phi-3" has introduced a family of models of varied sizes. More specifically,

* Phi-3-mini: a 3.8B parameter model trained on approximately 3.3T tokens that follows the transformer decoder architecture. It comes in two different flavors of context sizes, namely: the 4K which is the default and an enlarged version to 128K. Phi-3-mini’s size allows running inference on edge devices like a modern mobile phone.
* Phi-3-small: a 7B parameter model with a default context length of 8192.
* Phi-3-medium: a model with 14B parameters which uses the same tokenizer and architecture as Phi-3-mini and is trained on the same data for slightly more epochs.

Phi-3-mini has also undergone a post-training process in two stages including supervised finetuning and direct preference optimization to further improve performance and safety of the model. Its strong reasoning capabilities and ability to follow instructions makes it a great choice for our purposes. Typically, the information needed to judge relevance is self-contained in the query and document and so general language skills and reasoning are more important than knowledge for this task.

### A note on terminology

[Pairwise](https://en.wikipedia.org/wiki/Learning_to_rank#Pairwise_approach) and [pointwise](https://en.wikipedia.org/wiki/Learning_to_rank#Pointwise_approach) denote two choices of ranking function. A pointwise ranker gets to see the query and one document at a time and decide how relevant that document is to the query. A pairwise ranking function gets to see the query and two documents at a time and decides which is more relevant.

## Our experiment: Evaluating search relevance

As we alluded, there are multiple choices in the prompt and the way an LLM is used that can influence its effectiveness for any given task. These should be evaluated systematically before it is deployed for real. Although details of the optimal prompt wording may change between LLMs, general [principles](https://arxiv.org/pdf/2005.14165) have [emerged](https://arxiv.org/abs/2201.11903) that work for a variety of tasks and models. Furthermore, task specific strategies can transfer to different datasets, much as task specific finetuning does.

For our annotation task we have clearly defined quality metrics: the number of agreements between the relevance judgment (0 or 1) assigned by the LLM and that we assign ourselves. This constitutes a confusion matrix for each design choice. As well as presenting the optimal choices, we perform some ablation studies for the different choices we found. This guides us on where to expend optimization effort when creating judgment lists for different retrieval tasks.

We explore the impact on quality of the following broad design choices:

1. Prompt wording for a zero-shot pointwise approach
2. A pairwise approach where you have one relevant document for each query
3. Few-shot [chain-of-thought](https://arxiv.org/pdf/2201.11903)
4. Ensembling

We note in passing that, although we did not explore this, these approaches are often compatible and we expect certain combinations are likely to achieve further improvements.

## About the annotation task

In our [previous blog post](https://www.elastic.co/search-labs/blog/evaluating-search-relevance-part-1) we touched upon the issue of incomplete markup in the MTEB benchmark and as a proof concept we created a dataset from the dev portion of the MS MARCO dataset. More specifically, we pulled 100 queries and kept the top-5 negative documents (based on the original relevance judgments file) that were retrieved with [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) and reranked with [Cohere-v2](https://docs.cohere.com/reference/rerank). We then manually scored all 500 (query, document) pairs.

Regarding the manual annotation task we decided to go with a strict approach and mark documents as positives when there was high enough confidence. We tried to be consistent by adhering to the following criteria:

1. The retrieved documents are on-topic and contain all the necessary information to address the query.
2. In the case of ambiguous queries we resort to the positive document (labeled through the original relevance judgments supplied with MS MARCO) to infer some additional metadata.

Regarding the second point, we can use as an example the query `age requirements for name change` (MS MARCO query ID 14151) . In this case, most of the returned documents seemed relevant at first glance as they provided on-topic information for name change in different states, but by reviewing the positive document we saw that the age requirements were localized for the state of California. Thus, documents which contained information for other states were finally marked as irrelevant. Given the metadata are not provided to the relevance model, we would not recommend this approach evaluating your own retrieval systems. However, for this task we decided to try as much as possible to stay in agreement with the intentions of the original annotators.

Finally, there were 33 documents we decided to remove. These included queries and their associated documents for which the positive document did not appear to provide any useful information, judgments we did not feel qualified to make and documents which appeared to answer the question, but provided contradictory information to the positive example. We felt these would introduce errors to the evaluation process without providing any additional useful differentiation between design choices.

In summary, out of the 500 pairs considered, our manual annotation gave us:

* 288 relevant documents
* 179 irrelevant documents
* 33 removed documents

We ended up making some revisions to our initial markup based on reviewing the chain-of-thought judgment errors and their rationale and have updated our [previous post](https://www.elastic.co/search-labs/blog/evaluating-search-relevance-part-1) to reflect this process. This underlines how challenging it can be to determine relevance. We discuss the revision process in the context of that experiment.

## About the language model

We decided to work with the [Phi-3-mini-4k-instruct](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct) model using the [transformers](https://huggingface.co/docs/transformers/en/index) library because:

* It contains only 3.8B parameters that when loaded with 4-bit quantization (through [bitsandbytes](https://huggingface.co/docs/bitsandbytes/main/en/index) it can easily fit into a consumer-grade GPU
* As noted in the [technical report](https://arxiv.org/abs/2404.14219):

  + the model performs quite well on reasoning tasks, and
  + the model does not have enough capacity to store too much "factual knowledge" which can be an advantage in the context of retrieval evaluation as we expect a smaller hallucination rate

For details on how we use this model see the [notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/evaluating-search-relevance-part-2/phi3-as-relevance-judge.ipynb).

## Results summary

Our baseline performance was obtained by the simple zero-shot pointwise prompt shown below. We choose to measure the quality of the LLM judge using the micro [F1](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html) score vs the ground truth labeling. Specifically, this is the fraction of correctly labeled (query, document) pairs or overall accuracy. This prompt achieves an F1 score of 0.7002.

```
Estimate the relevance of the retrieved document to the query.
    Query: {query_text}
    Document: {retrieved_text}

You should provide your answer in the form of a boolean value: "Relevant" or "Not Relevant".
```

**This is the baseline prompt where query\_text and retrieved\_text are placeholders for the query and document to judge**

The figure below summarizes the accuracy we obtain from the various techniques we evaluated. In practice, one would typically want to apply these techniques to unseen queries and documents (or else you don’t save any effort). By ‘fine-tuning’ the behavior of the model on a smaller (validation) set we implicitly assume that these improvements will ‘transfer’ well to the test dataset. Whilst this is usually justified, if you have more data it can be useful to hold out a portion for testing the optimisations you make.

**Figure 1. provides a summary of the impact on the accuracy of the various design choices we studied. We discuss these in detail next.**

![prompt-accuracy](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc904c61c17d823e4/6a17dacb5772623b3d1bcad7/9bc288ca40aa7abb968c67e0750659e68ef5001b-665x685.png)

## The role of word choice on prompt performance

Optimizing a prompt for a downstream task can be quite challenging; as others have noted, even small paraphrases can have a drastic effect on [performance](https://arxiv.org/pdf/2309.10621).

Some good general guidelines are that prompts should:

* Maintain consistent style and naming conventions,
* Clearly delineate distinct content
* Unambiguously define the task, and
* Avoid extra verbiage (except for special cases)

Consistent naming of entities minimizes the risk that the LLM becomes confused about task descriptions that reference them. Capitalisation or punctuation can help. In the example below, we always refer to "Query" and "Retrieved Document" making clear that these are proper names we have defined in the context that we reference them.

Keeping separate content clearly delineated helps the attention mechanism avoid confounding content you wish to disambiguate. In the example below we use `#####` to surround the supplied "Query" and "Retrieved Document", keeping them distinct from their definition in the task description.

In general, you should strive to make each sentence clear and concise. Clear unambiguous task definitions are particularly important. One can observe dramatic effects, particularly for weaker models, from accidental typos, contradictory content and missing punctuation in key passages. It is always worth printing and proofreading your prompts. Aside from "bugs", there is often a trade off in precision and conciseness; being too brief can introduce ambiguity. Furthermore, some tasks are intrinsically nuanced and so lack a simple clear definition. Judging relevance is such a task since it can depend on multiple factors some of which are left unsaid. We will return to this topic later.

Aside from certain special phrases, such as those which condition for particular behavior in the LLM, irrelevant content usually simply acts as a distraction and should be avoided.

The best zero shot variant of our baseline prompt is shown below. In particular, the variants we compared excluded pairwise and chain-of-thought strategies, which we will discuss later.

```
You are an expert in information retrieval and your task is to estimate the relevance of a retrieved document to a query.
More specifically, you will be provided with two pieces of information:
- Query, which is the question we want to answer
- Retrieved Document, which is the document we want to evaluate
Your task is to predict "Relevant" if the Retrieved Document contains the information
required to provide an answer to the Query, otherwise you should predict "Not Relevant"
#####
Here are your inputs:
Query: {query_text}
Retrieved Document: {retrieved_text}
#####
Take a step back and reflect carefully on how best to solve your task
You should provide your answer in the form of a boolean value: "Relevant" or "Not Relevant"
```

**This is the best zero-shot pointwise prompt**

The results from this first experiment are shown in the table below:

|  | LLM\Relevant | LLM\Not Relevant |
| --- | --- | --- |
| Human\Relevant | 244 | 44 |
| Human\Not Relevant | 70 | 109 |
| Table 1. Pointwise results |  |  |

The micro F1-score in this case is 0.7559, whereas focusing only on the "Relevant" class we get Precision = 0.7771, Recall = 0.8472 and F1(Relevant class) = 0.8106. It’s worth noting that the LLM output could be parsed without any issues, i.e. the output always contained the tokens either "Relevant" or "Not Relevant".

For the high-level design of the prompt we drew some inspiration from [this](https://arxiv.org/pdf/2406.14117) paper that builds a taxonomy for prompt templates in the context of zero-shot LLM re-rankers and we adapt it to our specific task. The taxonomy is built around the following high-level components:

* **Evidence**: the query and the associated passage(s) to be judged
* **Task Instruction**: The instructions associated with our judging task
* **Output Type**: The instructions that specify the desired format for the output
* **Tone Words**: Positive or negative expressions that aim to steer the performance of the language model e.g. "please", "good luck"
* **Role Playing**: The instructions asking the LM to "impersonate" a role

We used the following prompt template to logically group the prompt components (the element tags are for illustrative purposes and were not used to prime the language model).

```
<Role playing component>
	You are an expert in information retrieval and..
</Role playing component>

<Task Instructions & Output Instructions>
..your task is to estimate the relevance of a retrieved document to a query.
More specifically, you will be provided with two pieces of information:
Query, which is the question we want to answer
Retrieved Document, which is the web page snippet we want to evaluate
	Your task is to predict "Relevant" if the Retrieved Document contains the information
            required to provide an answer to the Query, otherwise you should predict "Not Relevant"
</Task Instructions>

<Evidence>
    #####
    Here are your inputs:
- Query: {query_text}
- Retrieved Document: {retrieved_text}
   #####
</Evidence>
<Task Instruction>
	Take a step back and reflect carefully on how best to solve your task
</Task Instruction>
<Output Instruction>
	You should provide your answer in the form of a boolean value: "Relevant" or "Not
            Relevant".
</Output Instruction>
<Tone words>
 Good luck!
</Tone words>
```

**This is the prompt template structure. The element tags are here just for illustrative purposes, they were not part of the prompt sent to the language model.**

A benefit of adding structure to the prompt template is that it makes it easier to iterate on word choices in a more systematic way. We present some of the results of those experiments below.

### Tone words

We investigated three different choices for the "Tone words" section as presented above. We tried the following versions:

1. `Good luck` which gives a micro-F1 score of 0.7473.
2. A version that urges the LM to produce a good score such as `It's absolutely crucial that you perform well on this task as it will have a direct impact on the quality of the search results for our users`. The micro F1-score in this case was 0.7259
3. Removing the tone words section gave us the best score (0.7559) as depicted above.

### Output instructions

In the prompts above we have set the output instruction as `You should provide your answer in the form of a boolean value: "Relevant" or "Not Relevant"`. We have found that Phi-3 behaves very well and adheres to the output format that we requested with 0 errors. Removing that guideline leads to unparsable output as expected.

### "Take a step back" reasoning

In the prompts presented above we have added a line to steer the model into employing a "step back" reasoning (`Take a step back and reflect carefully on how best to solve your task`). Our experiments show that the role of this component is **absolutely critical**. By removing this line we observed a significant drop in the accuracy as the model entered a **failure mode** over-predicting one class over the other (in this case the "Relevant" class). More specifically, the set of prompts that contained this guideline led to a prediction rate of 68.9% on average for the "Relevant" class whereas in prompts with the guideline removed the rate rose to 85.6% rendering the model unusable. (As a reminder from the [previous blog post](https://www.elastic.co/search-labs/blog/evaluating-search-relevance-part-1) the percentage of "Relevant" data points after manual annotation is ~57%.)

### Role playing

For the role-playing section we didn’t observe a clear pattern regarding its effect. Adding or removing this component yielded small differences in absolute terms (mostly positive but also some negative).

### More precise instructions

In the discussion so far we have implicitly assumed that the language model ‘knows’ how to interpret the task instructions in order to assess the relevance between the query and the document. We also investigated the effect of more detailed instructions following the work of [Thomas et al](https://arxiv.org/pdf/2309.10621). There, the authors elicit a step-by-step reasoning by asking the model to explicitly score two aspects of the problem - namely topicality and trust - prior to deciding on a final score for the query, document pair. Inspired by the methodology of Thomas et al. we incorporated the following guidelines (and variations of it) between the evidence and the output instructions sections:

```
Instructions:
Split this problem into steps:
- Consider the underlying intent of the query
- Measure how well the document matches a likely intent of the query.
- Measure how trustworthy the document is.
- Ensure that the document provides a comprehensive answer to the query

Consider the aspects above and the relative importance of each and provide your answer in the form of a boolean value "Relevant" or "Not Relevant"
```

**Adding instructions**

In this case we didn’t observe a benefit from adding these guidelines in the accuracy metric and the best score we achieved was 0.7238. One common pattern was the tendency of the language model to be more 'hesitant' into predicting the 'Relevant' class which can be attributed to the additional criteria that need to be satisfied. In other words, it seems like a useful ‘knob’ that can be tuned to regulate the behavior of a language model if you are more sensitive to certain classes of error.

## Pairwise

[Pairwise](https://arxiv.org/pdf/2306.17563) [methods](https://arxiv.org/abs/2406.14117) have been considered in the context of LLM reranking, where an LLM is presented with a query and two candidate passages and it is asked to select the better one. After repeating multiple times for different pairs of documents, these intermediate results are aggregated to produce the final ranking of the documents. It has been [shown](https://arxiv.org/abs/2406.14117) that pairwise approaches are usually quite effective and also exhibit low variability in the generated results. The superiority, especially compared to pointwise methods, can be potentially [explained](https://arxiv.org/pdf/2305.02156) by the fact that the extra document(s) provide additional context for making individual relevance judgments. Pairwise comparisons have been also applied more broadly in LLM evaluation setups such as [MT-Bench](https://arxiv.org/pdf/2306.05685) where the LLM acting as judge is presented with a question and two answers and is asked to determine which one is better or declare a tie. This is a good way to enhance stability according to [recent studies](https://www.oreilly.com/radar/what-we-learned-from-a-year-of-building-with-llms-part-i/).

Here, we experiment to see if we can improve accuracy by injecting a positive example. This might sound like it defeats the purpose to reduce manual labeling effort. However, it actually aligns well with the deep mark up scenario: it enables you to "transfer" your judgment on one result to label the top-n. The most relevant work is this [1-shot labeling](https://arxiv.org/pdf/2302.11266) (1SL) study. It explores the effectiveness of extending manual markup with noisy LLM labels using the same pairwise approach. The authors found significant improvements in correlation to full human evaluations of a retrieval system compared to evaluating using single labels alone. This was despite errors in the LLM labels.

The prompt template is adapted as follows:

```
You are an expert in information retrieval and your task is to estimate the relevance of a retrieved document to a query.
More specifically, you will be provided with three pieces of information:
- Query, which is the question we want to answer
- Positive Document, which is a document that contains the correct answer to the query
- Retrieved Document, which is the document we want to evaluate
Your task is to predict "Relevant" if the Retrieved Document contains the information
required to provide an answer to the Query, otherwise you should predict "Not Relevant"
You can take advantage of the information in the Positive Document to identify the correct answer to the Query and then verify that the Retrieved Document contains that piece of information
#####
Here are your inputs:
Query: {query_text}
Positive Document: {positive_text}
Retrieved Document: {retrieved_text}
#####

Take a step back and reflect carefully on how best to solve your task
You should provide your answer in the form of a boolean value: "Relevant" or "Not Relevant".
Good luck!
```

**Pairwise prompting**

The results from this adaptation to the prompt are shown in the table below

|  | LLM\Relevant | LLM\Not Relevant |
| --- | --- | --- |
| Human\Relevant | 246 | 42 |
| Human\Not Relevant | 58 | 121 |
| Table 2. Pairwise results |  |  |

where we observe a micro-F1 score of 0.7859 and focusing on the relevant class we get precision equal to 0.8092, a recall score of 0.8542 and a F1 score of 0.8311

From a high level perspective we ask the language model to perform two sub-tasks before responding:

* Extract the information from the positive document that answers the query
* Look for that piece of information in the retrieved document and respond with a relevance label

Another interesting avenue to explore is to combine this sort of approach with current synthetic data generation techniques like [RAGAS](https://docs.ragas.io/en/stable/concepts/testset_generation.html) to enhance offline evaluation. In these frameworks documents are sampled from the target corpus and are fed to an LLM "asking" it to produce a suitable query. These (query, document) pairs form a test collection that can then be used to evaluate the performance of a QA pipeline or a RAG setup more generally. This process seems likely to also benefit from 1SL.

## Few-shot chain-of-thought

In-context learning (ICL) has been a distinctive characteristic of the current state-of-the-art language models where through a few demonstrations the model can generalize to unseen inputs. A recent [paper](https://arxiv.org/pdf/2212.10559) from Microsoft provides some intuition around this behavior by treating ICL as implicit finetuning where the LLMs act as meta-optimizers that produce meta-gradients according to the demonstration examples. Separately, it has been demonstrated in many contexts that getting LLMs to first generate text that provides some analysis of the task can improve performance. This is particularly important for tasks that require some form of reasoning. There are many variants on this theme, the prototype was [chain-of-thought](https://arxiv.org/pdf/2201.11903) prompting. This asks the LLM to break complex tasks into multiple smaller steps and solve them one-by-one. These two techniques can be combined and we study this strategy below.

Giving the LLM examples of our preferred relevance judgments, using the gradient descent analogy, should cause it to better align with our preferences. In the spirit of [active learning](https://en.wikipedia.org/wiki/Active_learning) these examples can be tailored to errors the LLM is observed to make. Furthermore, since judgments typically require weighing multiple factors, having the LLM clearly explain these to itself before it makes its judgment is a good candidate for chain-of-thought. We decided to steer the steps the LLM uses for its chain-of-thought as follows:

1. Expand the query to try and infer intent
2. Summarize the document to extract the key information it provides
3. Justify the relevance judgment
4. Make the judgment

Note that autoregressive models only get to attend to the tokens they have already generated, so it is vital that the judgment step comes at the end.

An additional advantage of generating rationales is that these can be useful to present to human annotators. [Recent research](https://arxiv.org/pdf/2305.04388) suggests these should not be considered as an explanation of the LLMs "thought process". However, we found in practice that they are still often useful to diagnose error cases. Furthermore, we found them to be consistently useful to understand a point of view for the relevance judgment and this actually caused us to revise some of our original relevance judgments.

There are downsides with this approach:

1. It costs far more in terms of input and output tokens,
2. There is a risk that information is hallucinated in the generation process which misinforms the relevance judgment,
3. Models can place too much emphasis on examples.

The below shows the prompt we evaluated. The choice of examples to supply is important. These were designed to demonstrate a mixture of skills we thought would be useful as well as fix point issues we were observing:

1. Example 1 is a case when matching a synonym, which is often useful, is undesirable because the query intent is rather specific. The user is likely looking for the dictionary definition of a word they do not know, so synonym definitions are not useful. This was responsible for a number of mistakes in our test corpus.
2. Example 2 demonstrates inductive reasoning applied to a relevance judgment. This is often useful, with the assessment having to weigh up the probability the document matches the user’s intent.
3. Example 3 is an example of entity resolution. Queries that mention specific entities usually require examples related to those specific entities and this overrides other considerations.

```
You are an expert in information retrieval and your task is to decide if a retrieved document is relevant to a query or not. You will be provided with two pieces of information:
- QUERY, which is a web search
- DOCUMENT, which is a web page snippet
Your task is to predict "Relevant" if the DOCUMENT contains the information required to provide an answer to the QUERY, otherwise you should predict "Not Relevant".
Solve this task step by step and use the following examples for help.
####
Example 1
QUERY: define interconnected
DOCUMENT: Matching (adjective) corresponding in pattern, color, or design; complementary.
Intent: The query is looking for the dictionary definition of the term "interconnected".
Key Information: The document provides a definition of the term "matching".
Explanation: The term "matching" is closely related to the word "interconnected". However, the query is asking for the dictionary definition of "interconnected", not "matching".
Answer: "Not Relevant"

Example 2
QUERY: what are some good chocolate cake recipes
DOCUMENT: Here are some of the best chocolate cakes to make yourself.
Intent: The query is looking for chocolate cake recipes.
Key Information: The document provides a list of chocolate cakes you can make yourself.
Explanation: The document provides information about chocolate cakes you can make yourself. This makes it very likely that it provides their recipes as well.
Answer: "Relevant"

Example 3
QUERY: enable parental controls on Netflix
DOCUMENT: Here's how to turn on parental controls on Amazon Prime Video:
Intent: The query is looking for instructions on how to enable parental controls on Netflix.
Key Information: The document provides instructions on how to turn on parental controls on Amazon Prime Video.
Explanation: The document provides instructions for how to turn on parental controls for Amazon Prime Video, not Netflix.
Answer: "Not Relevant"
####

To solve your task, first check if any of the examples are useful, then think carefully if Key Information matches the Intent. Use the following format:
Intent: [the intent behind QUERY]
Key Information: [the key information contained in DOCUMENT]
Explanation: [your explanation]
Answer: [your answer]
[your answer] should be either "Relevant" or "Not Relevant".
Here are the QUERY and DOCUMENT for you to evaluate:
QUERY: {query_text}
DOCUMENT: {retrieved_text}
```

**Few-shot Chain-of-thought prompt**

Before discussing the results, it is worth highlighting some of the subtleties involved in making good judgments.

One recurring challenge we found in marking up this small dataset is how to treat documents that only provide links to information that would likely answer the question. In the context of a web search engine this is a relevant response; however, if the snippet were being supplied to an LLM to generate a response it may be less useful. We followed the positive examples in such cases (which were in fact inconsistent in this respect!). In general, we advise you to carefully consider what constitutes relevant in the context of your own datasets and retrieval tasks and suggest that this is often best done by trying to generalize from example queries and their retrieved results.

Another challenge is where to draw the line in what constitutes relevant information. For example, the main helpline for Amazon may not be directly related to a query for "amazon fire stick customer service" but it would likely be useful. Again we were guided by the positive examples when making our own judgments.

The LLM false negative errors we observed fell into several categories. For the sake of brevity we mention the two dominant ones: we define these as pedantry and selective blindness. For pedantry the LLM is correct in a pedantic sense, but in our opinion it fails to properly assess the balance of probability that the document is useful. For selective blindness the LLM seems to miss important details in its reading of the document content. We give examples below.

| pedantry |
| --- |

```
Query: temperature in clearwater florida per month
Retrieved Document: Clearwater: Annual Weather Averages. July is the hottest month in Clearwater with an average temperature of 28 °C (83 °F) and the coldest is January at 14 °C (58 °F) with the most daily sunshine hours at 11 in July.he wettest month is June with an average of 133.3mm of rain. The best month to swim in the sea is in August when the average sea temperature is 30 °C (86 °F).
Explanation: The document contains information about the average temperature in Clearwater, Florida for two months (July and January), but it does not provide the average temperature for each month. However, it does mention the hottest month (July) and the coldest month (January).
```

| blindness |
| --- |

```
Query: the largest company in each state
Retrieved Document:  Click here to see the largest company in each state. While these companies are the largest in their home states, they are not necessarily among the largest in the nation. Exxon Mobil, the largest company in Texas and the second-largest in the U.S., reported revenue of $411.9 billion last year.
Explanation: The document provides information about the largest company in Texas, but it does not provide information about the largest company in each state.
```

**Table 3. Examples of false negative LLM relevance judgments**

Similarly, we saw several interesting false positive categories: we define two of these as confabulations and invented content. For confabulations the LLM fails to distinguish between entities in the query and document. For invented content it typically invents information about either the query or document which misleads the relevance judgment. We include examples below.

| Confabulations |
| --- |

```
Query: how titanic facts
Retrieved Document:  Titan Moon Facts. Titan is the Saturnâs largest moon and is the second largest moon in our solar system. If it were not orbiting Saturn, Titan could be considered a planet as it is larger than Mercury. Titan is covered with a thick atmosphere that some consider to be similar to that of early Earth.
Intent: The query is asking for facts about Titan.
```

| Invented Content |
| --- |

```
Query: how much is a cost to run disneyland
Retrieved Document:  Sixty years ago today, Walt Disney introduced the worldâs very first theme park: Disneyland. How much did a trip to the Happiest Place on Earth cost in 1955? $1 for adults and 50 cents for children. Sixty years ago today, Walt Disney introduced the worldâs very first theme park: Disneyland. How much did a trip to the Happiest Place on Earth cost in 1955? $1 for adults and 50 cents for children.
Intent: The query is asking for the cost of a trip to Disneyland.
```

**Table 4. Examples of false positive LLM relevance judgments**

In the first example, it is interesting that Titanic is misinterpreted as Titan. This is likely in part a side effect of the tokenization: neither titan nor titanic are present in the Phi-3 vocabulary. In the second example, we hypothesize that the question in the retrieved document confuses the LLM regarding what is the actual query. It is possible that better delineation of context could help with this specific problem.

Finally, the process of reading LLM rationales caused us to revise our judgment of 15 cases and exclude one additional example (on the grounds that the positive example was wrong). A typical example is that the LLM includes information which helps us better evaluate relevance itself. We show such a case below. In this context we strongly advise to double check any knowledge beyond the data that the LLM brings since there is risk of hallucination.

```
Query: how to cook string beans
Retrieved Document:  How To Cook Snap Beans. Also known as green beans or string beans, snap beans are grown in gardens across the world. Their name derives from the sound they make when broken or snapped. Fresh snap beans are cooked in a variety of methods (they are eaten pod and all), but boiling and steaming the beans are the most popular. Selecting the right snap beans for cooking will result in the best flavor. Beans picked too late in the growing season will have a tough texture when cooked.
Explanation: The document provides information on how to cook snap beans, which are also known as string beans. It mentions popular cooking methods and tips for selecting the right snap beans for cooking.
```

The final results with the updated markup are provided in the table below. The micro F1-score in this case is 0.773, whereas focusing only on the "Relevant" class we get Precision = 0.7809, Recall = 0.8785 and F1(Relevant class) = 0.8268. In all cases the LLM output could be parsed without any issues, i.e. it always contained either `Answer: "Relevant"` or `Answer: "Not Relevant"`.

|  | LLM\Relevant | LLM\Not Relevant |
| --- | --- | --- |
| Human\Relevant | 253 | 35 |
| Human\Not Relevant | 71 | 108 |
| Table 5. Chain-of-thought results |  |  |

## Ensemble

One common technique to increase the performance of AI systems in language tasks is to first perform multiple inferences over the same set of input data and then aggregate the intermediate results - usually through [majority](https://arxiv.org/pdf/2203.11171) [voting](https://arxiv.org/pdf/2312.11805). Here is also an interesting [paper](https://arxiv.org/pdf/2403.02419) discussing how the number of LM calls and the "hardness" of the queries affect the performance of systems which aggregate LM responses in a similar manner.

We experimented with multiple inferences and majority voting as well: in order to simulate this behavior in our setup we enabled sampling (more in the accompanying [notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/evaluating-search-relevance-part-2/phi3-as-relevance-judge.ipynb)), we increased the temperature to 0.5 and finally we asked the model to return 5 sequences through beam search that were aggregated to output a single response via majority voting. As an extra metric we computed the "majority rate" per data point which is simply the percentage of sequences matching the majority response.

It is worth noting that temperature only affects token selection. Therefore, it can only affect matters after the first token is decoded. Even so this can affect outputs from all our prompts. For example, it can insert an extra token at the start of the sequence or it can deviate into alternative forms like "Not sure". We parse the raw output using a regular expression to match the instructed output and discard votes from runs we were unable to parse.

We investigated both pointwise and pairwise prompts: In the pointwise case, we observed a consistent uplift between 0.6 and 1.5 percentage points (in terms of micro-F1) for 'suboptimal' prompts i.e. whose score was below the optimal (~0.76). On the other hand, majority voting did not give us a better top score. In other words, the gains are larger when you are far from the top but as you get closer you reach a plateau in terms of performance. In the pairwise case the increase was much more modest (~0.2 pp) and less robust as we came across cases where the effect was in fact negative.

Another interesting aspect came from the analysis of the majority rate: as data points with values less than 1.0 surfaced queries that they were either ambiguous (e.g. query ID 1089846 - `the economics is or are`) or "hard to decide" i.e. some of the 33 undefined cases that were eliminated from evaluation.

Overall, such aggregation techniques are becoming more and more common given the performance boost they offer on certain tasks. Nevertheless, it’s an area that requires some additional exploration considering the extra computational cost tied to the additional inference steps. Also bear in mind that the more constrained the output the less scope it has to affect results.

## Conclusion

We set out to explore whether we can use an LLM to bootstrap a search evaluation dataset. We took as a test case a sample of queries from MS MARCO together with the most relevant documents found by a strong retrieval system. We showed using a strong, small and permissively-licensed language model (in our case Phi-3 mini) that we are able to achieve good correlation with human judgments.

At the same time we wanted to explore design choices in the use of the LLM. We tested:

1. The prompt wording,
2. Supplying a known relevant document,
3. Chain-of-thought, and
4. Ensembling multiple generations.

We found significant gains could be obtained just by changing the prompt wording. We suggest some general guidelines for writing effective prompts. However, small details can have noticeable effects. Generally, some trial and error is required and automation [frameworks](https://github.com/stanfordnlp/dspy) can be useful when you have a test set.

Chain-of-thought produced further improvements but comes at the cost of expensive generation. Judgment rationales are interesting in their own right and allowed us to improve our original manual markup.

Our best result was obtained with a pairwise approach which supplied an example positive document. We postulate that part of the gain comes because it better aligns with our evaluation criteria, which was strongly steered by the supplied relevant document. However, other studies have shown improvements over pointwise approaches and we think it represents an interesting strategy for obtaining deep markup from shallow markup.

Finally, we explored using multiple generations, via non-zero temperature. This achieved some modest benefits for our baseline strategy, but we expect the main advantage to be associated with complex outputs such as chain-of-thought. A natural next step would be ensembling of prompts.

In this blog, we really just scratched the surface of using LLMs for evaluating search relevance. Longer term we expect them to have a larger and larger role in multiple aspects of building information retrieval systems and this is something we’re actively exploring at Elastic.

### Frequently Asked Questions

#### What are Phi-3 models?

Phi-3 is a recent generation of Small Language Models (SLMs) from Microsoft. It was shown that properly curated collections of publicly available web data combined with LLM-created synthetic data, enabled "small" language models to match the performance of much larger language models (in some cases 25 times larger) trained on regular data.

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