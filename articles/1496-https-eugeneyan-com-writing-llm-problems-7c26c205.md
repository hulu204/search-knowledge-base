---
title: 'https://eugeneyan.com//writing/llm-problems/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/llm-problems/
account: 
origin: en-rss
---
# [eugeneyan](/)

* [Start Here](/start-here/ "Start Here")
* [Writing](/writing/ "Writing")
* [Speaking](/speaking/ "Speaking")
* [Prototyping](/prototyping/ "Prototyping")
* [About](/about/ "About")
* [![](/assets/icon-search.svg)](/search/ "Search")

# How to Match LLM Patterns to Problems

[
[llm](/tag/llm/)
[production](/tag/production/)
]
 · 6 min read

After my previous write-up on [LLM patterns](/writing/llm-patterns/), I’ve received questions on how to match those patterns to various LLM problems. Thus, in this follow-up, we’ll discuss some potential problems faced when using LLMs and the patterns that help mitigate them.

## External vs. internal LLMs, data vs. non-data patterns

Before we dive into it, I think it’s helpful to distinguish between external vs. internal LLMs.

**External LLMs are models we don’t have full control over.** We can’t fine-tune them, are constrained by rate/token limits, and may have concerns with sending them confidential or proprietary data. Nonetheless, they’re currently the SOTA in terms of quality and safety.

**Internal LLMs are those we develop and host ourselves**. While they may not have the constraints of external LLMs, we incur the cost of developing and hosting these LLMs. Also, we typically build them on top of open LLMs (unless you have a couple million to pre-train your own). Unfortunately, these open LLMs tend to be months, if not years, behind the best 3rd-party provider LLMs.

With regard to patterns, I think it’s useful to understand the role data plays: Is data the main component or a by-product? Or is the pattern minimally related to data?

For example, **evals and fine-tuning are tied to data**. We can’t do evals without gold labels or references; we can’t fine-tune without demonstration data. In contrast, patterns such as **caching, defensive UX, and guardrails have more to do with infra and UI than data**.

On the other hand, patterns such as **RAG and collecting user feedback lie somewhere in the middle.** RAG provides data for in-context learning but needs to be backed by retrieval or search indices. User feedback helps with fine-tuning but needs to be collected via the right UX and refined via analysis and data pipelines.

## Matching patterns to problems

Here are some LLM problems and the patterns that help address them. Since we’ve [previously discussed the patterns extensively](/writing/llm-patterns/), we’ll focus on the problems here.

**Lack of performance metrics for our specific task.** When benchmarking external and internal LLMs, we often want to—rightly or wrongly—summarize performance into a table of numbers. (Note: This is fiendishly difficult, especially for more abstract tasks where there are innumerable good outputs.) And as we tweak our systems via updating prompt templates, fine-tuning models, or improving RAG, we need a way to measure improvements or regressions. Finally, how do we measure if users like or dislike these new LLM-based features, and the impact of our tweaks?

* [Evals](/writing/llm-patterns/#evals-to-measure-performance): To benchmark across models and measure performance with each change
* [Collect user feedback](/writing/llm-patterns/#collect-user-feedback-to-build-our-data-flywheel): To understand what users like or dislike

**External model performing poorly.** This can be due to the model not being trained on recent data (e.g., ChatGPT’s knowledge cutoff of Sept 2021) or proprietary data within your org (e.g., internal code and documents). Other concerns include hallucinations or incorrect responses because the model lacks sufficient or the most recent context.

* [RAG](/writing/llm-patterns/#retrieval-augmented-generation-to-add-knowledge): To provide relevant context, reducing hallucination and improving responses
* [Evals](/writing/llm-patterns/#evals-to-measure-performance): To measure performance improvements while tuning retrieval indices

**Internal model performing poorly.** Open LLMs tend to perform poorly on specific tasks in our specific domain out of the box. This can lead to defects such as poor extraction or summarization, non-factual responses, going off-topic, or simply lack of fluency. These LLMS may also return harmful responses that we want to minimize. While the patterns that apply to external LLMs are also relevant, because it’s an internal model, we have a few more tricks at our disposal.

* [Fine-tuning](/writing/llm-patterns/#fine-tuning-to-get-better-at-specific-tasks): To improve performance on specific tasks in our domain
* [Collect user feedback](/writing/llm-patterns/#collect-user-feedback-to-build-our-data-flywheel): To use as user preference data for fine-tuning

**Constraints on external models.** These constraints can be technical (e.g., rate limits, latency, models being excessively fine-tuned), legal (e.g., not sending confidential or user private data, copyright over and use of external LLM output), and financial (i.e., high cost of API calls). AFAIK, there are two viable solutions: Either negotiate a contract with your external LLM provider or develop and self-host your own LLMs. I suggest saintly patience for the former and the patterns below for the latter.

* [Fine-tuning](/writing/llm-patterns/#fine-tuning-to-get-better-at-specific-tasks): To improve performance of internal models on our specific tasks
* [Evals](/writing/llm-patterns/#evals-to-measure-performance): To track progress of internal LLMs and compare them against external LLMs
* [Collect user feedback](/writing/llm-patterns/#collect-user-feedback-to-build-our-data-flywheel): For fine-tuning and evaluation data

**Latency exceeds UX requirements**. Certain use cases require the entire LLM output to be available within a few hundred milliseconds, including running guardrails on the output. While streaming output helps a ton with the UX, it may not be viable for certain user experiences and interfaces (no, I’m not referring to chat).

* [Caching](/writing/llm-patterns/#caching-to-reduce-latency-and-cost): Figuring out smart ways to generate (either in batch or asynchronously) and cache responses *other* than via semantic similarity (e.g., item IDs)

**Unreliable or unusable model output.** I categorize these as syntactic vs. semantic errors. Syntactic errors occur when the model doesn’t adhere to a specific format such as JSON or a specific sentence structure, or the generated code or SQL doesn’t run. Semantic errors occur when the model output is harmful, non-factual, off-topic, or simply incoherent.

* [Guardrails](/writing/llm-patterns/#guardrails-to-ensure-output-quality) (guidance + syntax checks): Guide LLM outputs; check for syntax errors
* [Guardrails](/writing/llm-patterns/#guardrails-to-ensure-output-quality) (semantic checks): Check for content safety, factuality, on-topic, etc.

**Customer experience paper cuts.** Machine learning models aren’t perfect—they will produce inaccurate output. The same goes for LLMs. Thus, after we’ve built a new LLM product/feature, how do we make it easy for users to explore and increase adoption? Also, how do we acknowledge that errors will happen, mitigate them, and earn trust over time?

* [Defensive UX](/writing/llm-patterns/#defensive-ux-to-anticipate--handle-errors-gracefully) (for onboarding): Anchor on familiarity and set the right expectations
* [Defensive UX](/writing/llm-patterns/#defensive-ux-to-anticipate--handle-errors-gracefully) (for paper cuts): Set the right expectations, support efficient dismissal and correction, and provide suitable attribution where available
* [Collect user feedback](/writing/llm-patterns/#collect-user-feedback-to-build-our-data-flywheel): To understand which features work and don’t work, and to collect data for fine-tuning and evals to improve the next iteration

**Lack of visibility on customer impact.** How do we know if our models are helping or hurting? Someone shared an anecdote of running an LLM-based customer support solution in prod for two weeks before discontinuing it—an A/B test showed that losses were 12x more when using an LLM as a substitute for their support team!

* [Monitoring](/writing/practical-guide-to-maintaining-machine-learning/#monitor-models-for-misbehaviour-when-retraining): Track metrics such as feature usage, user opt-outs, daily users, etc.
* [Collect user feedback](/writing/llm-patterns/#collect-user-feedback-to-build-our-data-flywheel): Make it easy for customers to provide positive or negative feedback, and also analyze implicit feedback as a proxy for user engagement

• • •

Are there any key problems I’ve missed? **Please [let me know!](https://twitter.com/eugeneyan)**

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Aug 2023). How to Match LLM Patterns to Problems. eugeneyan.com.
> https://eugeneyan.com/writing/llm-problems/.

or

```
@article{yan2023llm-problems,
  title   = {How to Match LLM Patterns to Problems},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2023},
  month   = {Aug},
  url     = {https://eugeneyan.com/writing/llm-problems/}
}
```

  
Share on: 

![](/assets/icon-twitter.svg)

![](/assets/icon-linkedin.svg)

![](/assets/bluesky.svg)

![](/assets/icon-facebook.svg)

![](/assets/icon-mail.svg)

---

  

Browse related tags: [
[llm](/tag/llm/)
[production](/tag/production/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Patterns for Building LLM-based Systems & Products](/writing/llm-patterns/)
[Evaluation & Hallucination Detection for Abstractive Summaries »](/writing/abstractive/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---