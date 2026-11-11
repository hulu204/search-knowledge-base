---
title: 'Improving retrieval with LLM-as-a-judge'
company: Vespa
tag: 评测
date: 2024-07-03
url: https://blog.vespa.ai/improving-retrieval-with-llm-as-a-judge/
account: 
origin: harvest3-202607
---
{
}

[Subscribe](https://vespa.ai/subscribe/)

# Vespa Blog

We Make AI Work

Share

![Jo Kristian Bergum](/assets/avatars/jobergum.jpg)

[Jo Kristian Bergum](/authors/jobergum/ "Jo Kristian Bergum")
[Follow](https://twitter.com/jobergum)
  
Chief Scientist

03 Jul 2024

# Improving retrieval with LLM-as-a-judge

This post demonstrates how to create your own reusable retrieval
evaluation dataset for **your data** and use it to assess your
retrieval system’s effectiveness. A reusable relevance dataset
allows for systematic evaluations of retrieval approaches, moving
beyond basic *Looks-Good-To-Me@10*.

We demonstrate this process by building a large relevance dataset
for our Vespa documentation RAG solution
[search.vespa.ai](https://search.vespa.ai) ([read
more about search.vespa.ai](https://blog.vespa.ai/search-vespa-ai/)). The *TLDR* of the
process:

* Build a small labeled relevance dataset by sampling queries and
  judging retrieved documents
* Prompt an LLM to judge the query and
  document pairs, then align the
  [LLM-as-a-judge](https://arxiv.org/abs/2306.05685) with human
  preferences established by the first step.
* Sample a large set
  of queries and retrieved documents using multiple methods. These
  are judged by the calibrated LLM-as-a-judge
* You now have a large
  relevance dataset that you can use to experiment with retrieval
  methods or parameters tailored for your data and retrieval use case

![ranking correlation](/assets/2024-07-03-improving-retrieval-with-llm-as-a-judge/image3.png "image_tooltip")

*GPT-4 judgments aligned with human judgments for search.vespa.ai*

It may sound straightforward, but some nuances
make it a complex topic. This article has the following major parts:

* Retrieval is short for Information Retrieval (IR)
* Ground truths for evaluation of Information retrieval systems
* Sampling of queries and documents to judge
* Evaluation metrics used to evaluate IR systems
* Towards using *LLM-as-judge* for scaling relevance judgments
* Building a large relevance dataset using *LLM-as-a-judge*
* Evaluation results and summary
* FAQ

Let’s ~~*delve*~~ dive into it.

## Retrieval is short for Information Retrieval (IR)

[Information retrieval](https://nlp.stanford.edu/IR-book/information-retrieval-book.html)(IR) is
an established research area where reliable evaluation of retrieval
systems is central. Reusable relevance test collections (documents,
queries, and relevance judgments) allow researchers to experiment
with methods and parameters.

From [The Philosophy of Information Retrieval
Evaluation](https://www.nist.gov/publications/philosophy-information-retrieval-evaluation)
by *[Ellen M. Voorhees](https://www.nist.gov/people/ellen-m-voorhees)*

> *Evaluation conferences such as TREC, CLEF, and NTCIR are modern
> examples of the [Cranfield evaluation
> paradigm](https://en.wikipedia.org/wiki/Cranfield_experiments). In
> the Cranfield paradigm, researchers **perform experiments on test
> collections to compare the relative effectiveness of different
> retrieval approaches**. The test collections allow the researchers
> to **control the effects of different system parameters**, increasing
> the power and decreasing the cost of retrieval experiments as
> compared to user-based evaluations.*

Our goal with this post is to help you build your own reusable
relevance dataset that you can use to compare the relative effectiveness
of retrieval systems or approaches, **for your data and your type
of queries**.

When you are doing retrieval for augmenting an LLM prompt (RAG),
[you are effectively doing information retrieval](https://blog.vespa.ai/when-you-are-using-vectors-you-are-doing-search/).
While you might be using off-the-shelf [text
embedding](https://docs.vespa.ai/en/embedding.html) representations
for this task, the implementation of retrieval extends far beyond
a single cosine similarity score. A retrieval system can incorporate
various techniques beyond the scope of this post, such as [query
rewriting](https://search.vespa.ai/search?query=query%20rewriting),
[retrieval
fusions](https://blog.vespa.ai/improving-zero-shot-ranking-with-vespa/),
[ColBERT](https://blog.vespa.ai/announcing-colbert-embedder-in-vespa/),
[splade](https://docs.vespa.ai/en/embedding.html#splade-embedder),
[cross-encoders](https://docs.vespa.ai/en/cross-encoders.html),
[phased ranking](https://docs.vespa.ai/en/phased-ranking.html), and
more.

With a reusable dataset, you can quantify effectiveness, iterate
on your approach, observe the impact of different parameters, and
make informed decisions regarding the trade-offs between effectiveness
and deployment cost.

![overview](/assets/2024-07-03-improving-retrieval-with-llm-as-a-judge/image7.png "image_tooltip")

Simply put, we evaluate a retrieval system’s effectiveness by
measuring its ability to retrieve relevant documents for a query.
The relevance of a query-document pair can be assessed by a domain
expert or a relevance assessor following guidelines. By now, you
might already start thinking about IR metrics with fancy names such
as nDCG and MRR, we will get to that, but first, we need labeled
data, or ground truths. Once we have enough labeled data, we can
start measuring effectiveness, quantified by IR evaluation metrics.

## Ground Truths for IR

To build any system that adds intelligence using ML, including those
based on foundational LLMs, we need a sample of ground truths to
evaluate the system. With more labeled data, we can fine-tune the
system, but at a minimum, a ground truth dataset is essential for
testing and evaluation. In the context of retrieval, ground truths
typically consist of a triplet: a query, a passage, and a relevance
judgment.

The relevance judgment could be graded, for example, using a scale
such as irrelevant, relevant, and highly relevant. Alternatively,
these grades could be converted to binary scale: irrelevant versus
relevant. The judgment labels are usually converted to a numeric
utility score; for instance, 0 could represent irrelevant and 1
could represent relevant.

## Creating ground truths for retrieval evaluation

One simple (and boring), but effective way to produce ground truth
labels is; *looking at data*.

Below is a screenshot of the search result page for a real user’s
information need, expressed as the query *[can i set term weights in
yql](https://search.vespa.ai/search?query=can%20i%20set%20term%20weights%20in%20yql&namespace=open-p)*.
In this case, a domain expert has judged the top three retrieved
passages using graded judgments:

![search.vespa.ai](/assets/2024-07-03-improving-retrieval-with-llm-as-a-judge/image2.png "image_tooltip")

The first hit is labeled as highly relevant as it seemingly answers
the query intent fully, with a concrete example of how to set the
term weight using the Vespa YQL query language. The second document
is annotated as relevant, as it covers the same topic, but using
the Vespa simple query language instead of YQL. This label requires
domain knowledge as the simple query language can be referenced via
[userQuery()](https://docs.vespa.ai/en/reference/query-language-reference.html#userquery) in
[YQL](https://docs.vespa.ai/en/reference/query-language-reference.html).

When we use an expert to judge the results of a query that a user
has typed, the expert can not reliably predict what the actual
information needed was, or how satisfied the user was with these
retrieved passages. The user who typed this query might have judged
both hit 2 and 3 as irrelevant. *Relevance is subjective*.

We can add UI elements that allow the user to provide feedback
(albeit sparse and noisy) on each retrieved document. Alternatively,
instead of explicit feedback, many real-world retrieval systems
rely on implicit feedback through user engagement signals, such as
clicks or skips. There is one major problem, the above search
result page displays the full paragraph, so the user does not need
to click the result to determine its relevance to the query, making
it hard to gather reliable labels using clicks. This is a growing
concern among search practitioners. As real-world retrieval systems
evolve towards answering systems, implicit user feedback signals
diminish.

### Sampling of queries and documents to judge

Above, we demonstrated a judgment process with a single query.
However, to evaluate the effectiveness of a system, we’ll need more
examples than a cherry-picked query where the current ranking system
is effective. We need to select more queries to evaluate - options:

* Sample queries from the production system
* If we don’t yet have a production system (or users), one alternative is generating
  [synthetic queries via prompting an
  LLM](https://blog.vespa.ai/improving-text-ranking-with-few-shot-prompting/),
  but this is not a great substitute for real user queries

![real queries](/assets/2024-07-03-improving-retrieval-with-llm-as-a-judge/image1.png "image_tooltip")

*A screenshot of a dashboard, where we can see a sample of queries
performed on search.vespa.ai. Predicting the user’s underlying
information need, given a short query, can be difficult.*

How many queries do we need? Not that many. Most [TREC
collections](https://trec.nist.gov/) have fewer than 100 queries,
and 25 is better than one. More is better.

### Sampling of documents to judge

This is a considerably harder process than sampling queries.
Most of the documents in the collection will be irrelevant for
any query, but we cannot be sure unless we judge every document for
the query. Assuming that it takes 5 seconds to judge a (query,
document) pair and that our collection is 5K documents, a single
person would use 4 hours to label all the documents for a single
query. This process doesn’t scale.

In practice, we need a way to sample documents for queries. One
alternative is to sample from top-k rankings produced by multiple
retrieval techniques to find diverse candidates for every
query. This process is known as pooling in IR evaluations. Typically,
at the start of a TREC conference track, the organizers will publish
the document collection and the queries. Then, participants will submit rankings for the queries,
forming the pool of (query, document) pairs that are candidates for the judgment process.

A
[bias](https://www.nist.gov/publications/bias-and-limits-pooling-large-collections)
is introduced if we only sample from one retrieval technique, like
in the screenshot above, as the labels will not be helpful to evaluate
other retrieval models reliably. This is because other retrieval
models can surface other relevant documents for the same query and
unlabeled (query, document) pairs will by default be assigned as
irrelevant. This makes it difficult to compare retrieval systems
purely by those labels without knowing if there were many “holes”
in the judgments.

## Evaluation metrics used to evaluate information retrieval systems

The way we evaluate a system or method (given the ground truth
triplets) is that for each query in the ground truth set we ask the
system for the top-k ranked documents, then compute the chosen
metric(s). Finally, the overall score of the system is the average
across all queries. You can safely skip the rest of this section
if you already know *P@k*, *R@K*, and *nDCG@k*.

Usually, we use a cutoff k of how far into the ranked list produced
by the system we compare with the ground truth. This cutoff can typically
be 10 for ten blue links search applications and potentially larger for RAG
applications using models with large context windows.

Given the query example from the previous section we had the following
ranked list using highly relevant = 2, relevant = 1, and irrelevant
= 0: [2,1,0]. We also can assume that the ideal ordering would be
[2,2,1] as there is one additional highly relevant document in the
ground truth.

**Precision at k (P@k)** measures the relevance of the top k search
results. It is calculated by dividing the number of relevant results
in the top k positions by k. For example, if we use a grade threshold
of 2 (Highly relevant), the P@3 for the screenshot above would be
0.33. This means that out of the top 3 results, 1 is highly relevant.
The position of the relevant results within the top k does not
matter, so P@3 cannot distinguish between rankings [2,1,0], [2,0,1], and [0,1,2].

**Recall@k** reflects the proportion of relevant documents retrieved
among the top k retrieved documents. In practice, knowing all the relevant documents for a given query is impossible.
Recall@k does not take into account positions within k. With a relevance cutoff
of 2, the recall@3 for the above screenshot would be 0.5 as only 1
out of the 2 were retrieved into the top 3 positions.

**Normalized Discounted Cumulative Gain (nDCG@k)** considers both
the grade (gain) and the position within k, and the gain is discounted (reduced)
with increasing rank position. It’s calculated as the ratio of the actual
DCG@k to the ideal DCG@k. The normalization makes it possible to
have a meaningful average over queries when there are differences
in the number of judgments per query.

For a better explanation of `nDCG` (and other evaluation metrics), see [this
slide deck (pdf)](https://web.stanford.edu/class/cs276/19handouts/lecture8-evaluation-6per.pdf)
from [CS276](https://web.stanford.edu/class/cs276/).

## Towards using LLMs as relevance judges

As human labeling quickly becomes prohibitively costly for the
comprehensive evaluation of a retrieval system, using LLMs as judges
becomes an attractive alternative. However, there is a significant
catch: we need a method to evaluate the *LLM-as-a-judge* to ensure that
its preferences align with human preferences.

Recent research[1](#fn:1) [2](#fn:2) [3](#fn:3) [4](#fn:4), finds that LLMs like GPT-4 can judge the
relevance of passages retrieved for a query with fair correlation
with human ground truths and good correlation in ranking
metrics. All we need to do is to align the prompt with our human
ground truths.

For search.vespa.ai, we established a human-labeled ground truth
dataset of 26 queries, where passages are sampled from a single
method using multiple signals. We use this dataset of 90 triplets
with, on average, 3.5 human judgments per query to judge the *LLM-as-a-judge*.

![Ground Truth](/assets/2024-07-03-improving-retrieval-with-llm-as-a-judge/image6.png "image_tooltip")

Sample of (query passage) relevance judgment triplets. We use a
graded relevance scale where:

* Irrelevant maps to 0
* Relevant maps to 1
* Highly relevant maps to 2

With this small dataset, which takes a few hours to gather, we ask
the LLM to judge the same (query, passage) pair. In our experiments,
we use GPT-4o, and the prompt is inspired by [3](#fn:3). As a modification,
we add two static demonstrations.

```
def get_score(query, passage):
    prompt = f"""Given a query and a passage, you must provide a score on an
    integer scale of 0 to 2 with the following meanings:
    0 = represents that the passage is irrelevant to the query,
    1 = represents that the passage is somewhat relevant to the query,
    2 = represents that the passage is is highly relevant to the query.
    Important Instruction: Assign score 1 if the passage is
    somewhat related to the query, score 2 if
    passage is highly relevant. If none of the
    above satisfies give it score 0.
    Examples:
    Query: what is fast-search
    Passage: By default, Vespa does not build any posting list index structures over attribute fields. 
    Adding fast-search to the attribute definition as shown below will add an in-memory B-tree posting list structure which enables faster search for some cases 
    ##final score: 2
    Query: what is fast-search
    Passage: weakAnd inner scoring The weakAnd query operator uses the following ranking features when calculating the inner score dot product:
    term(n).significance
    term(n).weight
    Note that the number of times the term occurs in the document is not used in the inner scoring calculation.
    ##final score: 0
    Split this problem into steps:
    Consider the underlying intent of the search query.
    Measure how well the passage matches the intent of the query.
    Final score must be an integer value only.
    Do not provide any code or reasoning in result. Just provide the score.
    Query: {query}
    Passage: {passage}
    ##final score: 
    """
    response = client.chat.completions.create(
      model="gpt-4o",
      temperature=0,
      max_tokens=15,
      messages=[
        {"role": "system", "content": "You are a Relevance assessor that judges the relevance of a passage to a query."},
        {"role": "user", "content": prompt}
      ]
    )
    result = response.choices[0].message.content
    try:
        final_score = int(result.strip())
    except ValueError:
        final_score = None
    return final_score
```

Details of the prompt used to judge a (query, passage) pair.

After running this for the 90 (query, passage) pairs, we have both
the ground truth label assigned by the human and the GPT-4 label.
With that data, we can use a confusion matrix to illustrate the
differences and agreements.

![Confusion Matrix](/assets/2024-07-03-improving-retrieval-with-llm-as-a-judge/image10.png "image_tooltip")

*[Confusion matrix](https://en.wikipedia.org/wiki/Confusion_matrix)
comparing GPT-4 labels versus human labels*

There is a fair correlation between our human ground truth labels
and the GPT4 labels. For example, there are few cases where the LLM
disagrees by more than one level. In only 1 case does it assign
irrelevant for something that the human assigned as highly relevant,
and the other way around.

We can also compare the GPT-4 labels to the human labels by
evaluating different retrieval techniques for the queries. Then,
evaluate the ranking metric nDCG using the human and GPT labels.

![Ranking correlation](/assets/2024-07-03-improving-retrieval-with-llm-as-a-judge/image3.png "image_tooltip")

*Nine retrieval methods represented in Vespa. Each point
is the aggregated nDCG@10 score over all 26 queries using a retrieval
method evaluated by human or GPT labels.*

As we can see from the above scatter plot,
there is a good correlation in the *rankings*.
This is encouraging, as it means that we can now start expanding our dataset with more
queries, sample more documents and let GPT be the relevance judge as it’s ranking the documents in a similar way to a human.

## Creating our LLM-judged relevance test collection

With good correlation between the human and GPT rankings, we can
gather more queries and documents for queries to create a larger
collection of judgments. We sample 386 unique queries performed
over the last month on search.vespa.ai. For passages, we sample the
top-10 rankings using six different methods.

We remove duplicate pairs (query, passage) which is the case if
different methods return the same passage in the top-k rankings for
the same query. After this step we are left with 10,372 unique
(query, passage) pairs that we let GPT label.

### Dataset statistics

* Unique queries: 386
* Unique documents: 3014 (with at least one judgment)
* Average judgments per query: 26.9

Label distribution

* Irrelevant 4817
* Relevant 4642
* Highly Relevant 913

This relevance collection allows us to change ranking-related
parameters. We will not detail each of the methods compared here.
We use nDCG@10 as the primary metric since we use graded relevance
labels. We also use Judged@10, which gives information about whether
there are holes in the judgments. A high judged@10 would mean that all
the hits in the top-ranked positions have judgments (relevant or irrelevant).

![ndcg](/assets/2024-07-03-improving-retrieval-with-llm-as-a-judge/image8.png "image_tooltip")
*The nDCG@10 for the different retrieval methods evaluated by GPT-4*
![judged](/assets/2024-07-03-improving-retrieval-with-llm-as-a-judge/image4.png "image_tooltip")
*The Judged@10 for the different retrieval methods evaluated by GPT-4*
![recall](/assets/2024-07-03-improving-retrieval-with-llm-as-a-judge/image9.png "image_tooltip")
*The Recall@10 for the different retrieval methods evaluated by GPT-4*

We use cutoff 2 (Highly Relevant) for Recall@10. Note that all these
metrics are averaged over all queries in the test collection. With
this, we can start evaluating the impact of changing parameters.
Furthermore, it’s also possible to use this dataset to train models
using traditional learning to rank techniques. If we choose to do
that, we also should build another test set that we can use to
evaluate the model.

## Summary

Moving towards LLM-as-a-judge for relevance assessment is an exciting
direction that can enable quicker iterations (feedback loops) and
eventually improved search relevancy for your data. This is important
because traditional methods of evaluating retrieval systems, such
as using human experts, can be costly and time-consuming. Additionally,
when moving from retrieval engines to answer engines, implicit click
feedback signals require that we find different (scalable) ways to
obtain high-quality relevancy feedback.

By using LLM-as-a-judge, it’s possible to quickly and efficiently
evaluate different retrieval methods and parameters, leading to
more informed decisions about relative effectiveness and production
deployment costs. It’s important to note that we need a human in
the loop to ensure that we judge the LLM-as-a-judge quality so that the rankings align.

## FAQ

**Why didn’t you try more LLMs to have more judges, like an ensemble
of judges?**

That is certainly an option, to use majority voting for example.
We found good correlation in the ranking order with one LLM so we
didn’t experiment further.

**Isn’t Recall@K a better metric than nDCG@10 in the context of
RAG?**

The argument is that the order within the context window doesn’t
matter so we should only care about whether we can retrieve all the
relevant information within the K first positions where K is
determined by the context window size budget. For search.vespa.ai
we do display the retrieved passages and instruct the LLM to cite
the sources. If the retriever places the relevant information higher
up, (lower rank), then there is less scrolling to verify the generated
answer. So, in short, we still want to have a precision-oriented
metric that handles both a graded scale and position.

**Any suggestions on how to overcome the sampling biases?**

As the cost of using the LLM as the judge is a fraction of the human
cost, it’s now possible to evaluate more documents per query,
including also evaluating the holes (missing judgments)[4](#fn:4).

This is useful when we introduce new retrieval methods, or; the collection changes over time.

**Can I use your test collection to evaluate my own retrieval
system?**

The main point of this post was to encourage users to create their
own dataset, for your own data and retrieval use case. It doesn’t
need to be fancy. Combine
[ir-measur.es](https://ir-measur.es/en/latest/index.html) with a
tsv file and a scraping routine, and you can get started.

**When you write about retrieval systems, what do you mean by that?
A database, or a search engine, or a vector database?**

All of those could be used as a retrieval system, even `grep` could
be a retrieval system. But, you will likely be better off using a
system that was built for effective information retrieval - a search
engine like [Vespa.ai](https://vespa.ai) where you can represent many different retrieval
and ranking methods.

**Do you think SPLADE works better than BM25 for my use case?**

This is the type of question we have been getting over the last few
years as we have added new and more advanced techniques to Vespa.
We hope that with this post, you can start building your own test
collections and answer these questions for your data and queries.

**What about learning to rank where you try to optimize the ranking,
how does it relate to LLM judges?**

As demonstrated in this post, the LLMs can be used to judge the
relevance. Therefore, we could use the label as the target when training
a model using learning to rank.

**What does this mean for ranking, shouldn’t we just use the LLM
for the ranking task as well?**

Ultimately [yes](https://arxiv.org/abs/2306.17563), one of the
reasons we deeply integrate [generative
LLMs](https://blog.vespa.ai/vespa-and-llms/). We envision that it can
improve lots of search-related tasks:

* Query and document “understanding”
* Categorization and classification
* Ranking (and retrieval)

The biggest challenge is high computational complexity
or cost, but we are sure the price will continue to drop over
the next few years. With some of the techniques explored in this
post, one can optimize ranking without significant cost by distilling
the knowledge of the most powerful LLMs. We let them judge and rate
the results, then distill that knowledge into fine-tuned parameters
to approximate their “optimal” ranking order.

## References

1. [Large language models can accurately predict searcher preferences](https://arxiv.org/abs/2309.10621) [↩](#fnref:1)
2. [Perspectives on Large Language Models for Relevance Judgment](https://arxiv.org/abs/2304.09161) [↩](#fnref:2)
3. [UMBRELA: UMbrela is the (Open-Source Reproduction of the) Bing RELevance Assessor](https://arxiv.org/abs/2406.06519) [↩](#fnref:3) [↩2](#fnref:3:1)
4. [LLMs Can Patch Up Missing Relevance Judgments in Evaluation](https://arxiv.org/abs/2405.04727) [↩](#fnref:4) [↩2](#fnref:4:1)

## Read more

[![PDF Retrieval with Vision Language Models](/assets/2024-07-15-retrieval-with-vision-language-models-colpali/david-travis-aVvZJC0ynBQ-unsplash.jpg)

Photo by [David Travis](https://unsplash.com/@dtravisphd?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash) on [Unsplash](https://unsplash.com/photos/person-holding-eyeglasses-aVvZJC0ynBQ?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash)](/retrieval-with-vision-language-models-colpali/)
[## PDF Retrieval with Vision Language Models

#### Connecting the ColPali model with Vespa for complex document format retrieval.](/retrieval-with-vision-language-models-colpali/)

[![](/assets/logo/vespa-logo.svg)

## Search in Vespa.ai

#### Our own search experience for all Vespa-related content - powered by Vespa, LangChain, and OpenAI’s chatGPT model.](https://search.vespa.ai/ )

[![](/assets/logo/vespa-logo.svg)

## Free Trial

#### Deploy your application for free. Get started now to get $300 in free credits. No credit card required!](https://vespa.ai/free-trial/ )

[« Vespa Newsletter, May 2024](/vespa-newsletter-may-2024/)
[Unlocking Ecommerce Growth: The Power of AI in Personalization and Recommendation »](/unlocking-ecommerce-growth/)

![Vespa Blog](/assets/logo/vespa-logo.svg)   Never miss a **story** from us, subscribe to our newsletter
[Subscribe](https://vespa.ai/subscribe/)