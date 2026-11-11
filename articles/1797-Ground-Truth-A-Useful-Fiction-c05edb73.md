---
title: 'Ground Truth: A Useful Fiction'
company: Tunkelang
tag: 评测
date: 2025-01-14
url: https://dtunkelang.medium.com/ground-truth-a-useful-fiction-720e55acce54
account: Tunkelang
origin: harvest3-202607
---
# Ground Truth: A Useful Fiction

A key concern about AI is that models “[hallucinate](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence))” — technical jargon for saying that they make up things that look right. Keeping AI models grounded in truth is a critical challenge for everyone working in AI.

In machine learning, “ground truth” refers to human-labeled data used for training and testing models, as well as evaluating their accuracy. Sometimes, this training data comes from the [implicit judgments of user behavior](https://queryunderstanding.com/evaluating-search-measuring-searcher-behavior-5f8347619eb0), such as clicks on search results. However, the gold standard for training data is typically a collection of [explicit judgments labeled by people paid to do so](https://queryunderstanding.com/evaluating-search-using-human-judgement-fbb2eeba37d9).

This explicitly labeled data is commonly known as “ground truth.” Once available, it provides application developers with a foundation to train and test machine learning systems.

This approach sounds ideal in theory, especially if you trust humans and distrust machines. Moreover, it has demonstrated merit in practice. Historically, machine learning systems have been plagued by noise, [bias](https://queryunderstanding.com/getting-uncomfortable-with-data-7339e27adf6f), and data quality issues. Humans, while not perfect, are less susceptible to some of the problems that undermine machine learning systems.

However, history is changing before our eyes. As the AI models we develop learn from us on an unprecedented scale, it is increasingly difficult to maintain the fiction that explicit human judgments represent a definitive ground truth against which we can evaluate those models. Indeed, we are increasingly using AI to validate our decisions, rather than the other way around. Moreover, there is [evidence that large language models (LLMs) may be comparable to human judgments for some evaluation tasks](https://arxiv.org/abs/2406.18403v2).

## The Fallibility of Human Judgments

We have always known that people are not perfect judges. Biases, inconsistencies, and subjectivities inevitably influence the labeling process. Additionally, the people performing these evaluations tend to prioritize speed over accuracy, particularly if they are compensated — often poorly — on a per-judgment basis. Even when evaluators try their best to provide robust judgments, their human fallibility is unavoidable.

Moreover, many questions lack a single, absolutely true answer. For instance, can birds fly? The reflexive answer is yes, but the nuanced answer acknowledges exceptions like penguins, ostriches, emus, and kiwis. In such cases, whose judgment would you trust more: a human’s or an LLM’s?

This example is not an outlier. Consider a search for a quart of milk on an e-commerce platform. Should the system show a liter, two pints, or powdered milk? Which of these results are exact, [substitutes](https://queryunderstanding.com/is-similarity-objective-92e1f3a4c236), or neither? Determining the best result requires nuanced judgment.

Requiring a consensus of judges, though more costly, mitigates some of the problems with explicit human judgments but not all of them. For instance, judges often interpret evaluation tasks literally, whereas searchers may be more flexible in pursuing their intent. Searchers decide what they accept as [substitutes](https://queryunderstanding.com/is-similarity-objective-92e1f3a4c236); judges must rely on empathy to approximate this flexibility.

As someone who has worked extensively in e-commerce search, I trust the implicit judgments of searcher behavior far more than the explicit judgments of non-searchers for resolving these kinds of questions. Even the most diligent evaluator lacks the agency to truly empathize with the searcher’s intent. However, searcher behavior is influenced by the site itself — particularly retrieval and ranking. No solution is perfect.

A more significant issue with using human judgments as ground truth is that we uncritically inherit their biases. A canonical example involves [predicting hiring decisions based on labeled outcomes from past hiring data](https://www.reuters.com/article/world/insight-amazon-scraps-secret-ai-recruiting-tool-that-showed-bias-against-women-idUSKCN1MK0AG/). If the labels reflect historical discrimination against certain groups, then the model will replicate those biases. Referring to such labels as “ground truth” obscures and even legitimizes these biases. Moreover, this problem shows up in all domains, not just e-commerce and hiring.

## Is Truth Knowable?

While these practical challenges are significant, they also point to a deeper issue: the philosophical complexities of defining truth itself. It is not just human judgment that can be fallible; the very concept of “truth” is more nuanced than we often assume.

Philosophy challenges our understanding of ‘ground truth’ as an absolute. [Fallibilism](https://en.wikipedia.org/wiki/Fallibilism) asserts that we can accept empirical knowledge even if we cannot prove anything with absolute certainty. [Skepticism](http://Skepticism) takes this further, questioning every link in a chain of reasoning and making certainty impossible. Despite these philosophical hurdles, humans find ways to establish beliefs, driven by the practical need to understand the world well enough to survive.

While we should not accept AI-generated outputs uncritically, we must also acknowledge that our human-derived “ground truth” is a useful fiction. Treating knowledge as sacrosanct just because it originates from people is misguided. Accepting the limits of our knowledge is the first step toward wisdom. As Socrates famously argued, [acknowledging our ignorance is the first step toward wisdom](https://en.wikipedia.org/wiki/I_know_that_I_know_nothing) — a perspective useful for AI developers.

Nonetheless, we need a starting point, and it is best to begin with what we know we know. We learn from the wisdom of others. Having multiple judges evaluate the same data and measuring their agreement can mitigate noise. Addressing systematic bias, however, is more challenging and requires specialized techniques well-documented in the literature.

## A Pragmatic Approach

Ultimately, we cannot and should not discard our “ground truth.” Instead, we should use it with our eyes open, making the most of an imperfect but valuable resource. Reality is messy, for machines and humans alike, and navigating that messiness requires humility and pragmatism.

In short, we must acknowledge the limitations of both human and AI judgments. By incorporating diverse perspectives, cross-validating with multiple models, and addressing biases head-on, we can build systems that approach truth with humility while remaining pragmatic in their utility.

By embracing this approach, we can build more robust AI applications, but also better understand and pursue truth in an ever-changing world.
