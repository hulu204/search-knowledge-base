---
title: 'https://eugeneyan.com//writing/product-evals/'
company: eugeneyan
tag: 评测
date: 
url: https://eugeneyan.com//writing/product-evals/
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

# Product Evals in Three Simple Steps

[
[eval](/tag/eval/)
[engineering](/tag/engineering/)
[production](/tag/production/)
]
 · 9 min read

After repeating myself for the $n^\text{th}$ time on how to build product evals, I figured I should write it down. There are three basic steps: (i) labeling a small dataset, (ii) aligning our LLM evaluators, and (iii) running the experiment + evaluation harness with each config change.

## First, label some data

It begins with sampling some input and output from our LLM requests, and labeling whether the output meets our evaluation criteria (e.g., faithfulness, relevance, etc). Start simple with a spreadsheet that has columns for input, output, additional metadata that helps evaluate the output, and a new column for the label.

**Focus on binary pass/fail or win/lose labels.** If the criteria are objective—such as whether a summary is faithful to the source, or contains a refusal—use pass/fail labels. For subjective criteria, such as whether one summary is more concise than another, use win/lose/tie comparisons. For the latter, it helps to allow annotators to indicate ties. Forcing them to pick a winner when two outputs are nearly identical introduces noise and prevents us from learning that some differences are negligible.

**What about numeric labels or Likert scales?** While 1-5 scales offer granularity, I’ve found it challenging to calibrate human annotators and LLM-evaluators. The difference between “3” and a “4” is often subtle. Even with detailed labeling rubrics, different human annotators will return different labels. And if it’s a challenge for human annotators to label consistently against a rubric, it will be a challenge for LLM-evaluators too. Binary labels mitigate this issue by forcing a clear decision boundary.

Furthermore, while stakeholders sometimes ask for granular scores so they have flexibilty to adjust the thresholds for what counts as a pass later (e.g., moving from 3 to 4, or from minor error to no error), in my experience, exactly *zero* of them actually do this. They eventually just ask for a recommended threshold so they can report the pass/fail rate. If this is where we’ll end up anyway, it’s simpler to start with binary labels. It leads to faster and more consistent labels from human annotators, and makes it easier to align our LLM-evaluators.

**Aim for 50-100 fail cases.** This depends on the total number of labels, and more importantly, the number of labels we actually care about. For pass/fail evaluations, most of the time, what matters is the “fails” as these are the trust-busting defects. A dataset with hundreds of labels but only five failures isn’t useful to align and evaluate our evaluators on. We need a *balanced* dataset. I usually recommend having at least 50-100 failures out of 200+ total samples.

**How to get fail cases?** I’ve found success using smaller, less capable models to generate outputs. Even when trying their hardest, these models naturally produce “organic” failures. They might struggle with long context, have insufficient reasoning ability, or fail on edge cases—these are the types of failures we’ll encounter in production.

A popular approach is to prompt a strong model to generate synthetic defects. I find these synthetic defects problematic. They tend to be out-of-distribution, either too exaggerated or too subtle in ways that don’t reflect what happens in production. When we align evaluators on these, they may fail to detect the messy, organic issues that actually affect our users. While I understand the need to start somewhere to bootstrap our evals, if our eval dataset consists solely of these, we should make it a priority to add organic samples from production.

We can also apply [active learning](/writing/bootstrapping-data-labels/). Once we have a sufficiently precise evaluator, we can run it on unlabeled data to identify likely failures and prioritize them for human annotation. This helps us build a balanced dataset without needing to label thousands of samples blindly.

## Then, align our LLM-evaluator

With our labeled samples, the next step is to create a prompt template that takes the input and output (and additional metadata), and returns the expected label. We should treat this as a conventional machine learning problem and split the data into development and test sets. For example, use 75% of the samples for alignment (read: iterating on the prompt template) and hold out the remaining 25% as the test set. This ensures we’re measuring how well our evaluator generalizes to new data rather than overfitting to the initial 75% of samples.

**Have one evaluator per dimension.** It’s easier to align an evaluator to a single criterion and achieve high accuracy. One anti-pattern is building a single “God Evaluator” (also see [God Object](https://en.wikipedia.org/wiki/God_object)) that attempts to assess 5 - 10 dimensions—faithfulness, relevance, conciseness, tone, etc.—in one prompt. I’ve never seen this work well. Furthermore, these catch-all evaluators are a nightmare to calibrate because we cannot easily isolate which dimension is misaligned.

Instead, build individual evaluators and combine them via simple heuristics (e.g., the output passes only if all dimensions pass). This approach gives us granular metrics, allowing us to see exactly which dimension is dragging down performance. This also allows us to treat various metrics differently because some are guardrail metrics where not meeting them is a shipblocker, while others are northstar metrics that we aspire to keep improving.

**If evaluating on win/lose, account for position bias.** To do this, run the evaluation twice with the order swapped. I typically use XML tags, such as `<control>` and `<treatment>`, with the output to be evaluated within them. In the first evaluation, have the baseline in `<control>` and the comparison output in `<treatment>`. Then, in the second evaluation, have the comparison output in `<control>` and the baseline in `<treatment>`. This ensures the evaluator is evaluating the content itself, and is not biased by the order or XML tags.

A well-calibrated evaluator should be consistent. If the baseline wins in the first evaluation, it should also win in the second. If the judgment flips, the outputs are perhaps too similar to distinguish, and we can mark these as ties rather than forcing a noisy decision.

**Evaluate these evaluators on precision, recall, and Cohen’s Kappa.** Since we’re using binary labels, evaluation is straightforward. For pass/fail tasks, we can prioritize recall on the “fail” class since we want to be sure we’re catching the defects. We also want decent precision to ensure we’re not flagging too many fails incorrectly. To measure inter-annotator reliability against human-annotated labels, we can look at Cohen’s Kappa. A score of 0.4 - 0.6 indicates substantial agreement while anything above 0.7 is excellent.

**The benchmark is human performance, not perfection.** We sometimes get requirements for 90%+ accuracy. My response is to gently remind folks that human annotators rarely achieve that. I often see human inter-rater reliability (Cohen’s Kappa) being as low as 0.2 - 0.3. And human annotators can miss as many as 50% of the defects due to fatigue after looking at hundreds of samples. Thus, if our LLM-evaluator achieves higher recall and consistency than human annotators, I’d consider that a success.

In my opinion, the true benefit isn’t higher accuracy than human annotators—it’s scalability. A well-aligned evaluator allows us to apply consistent, (super)human-level judgment across hundreds of samples in minutes, 24/7, without being bottlenecked by human review. This allows us to run experiments at scale and thus iterate faster.

## Finally, run our eval harness with each change

Finally, we can combine our individual evaluators into an evaluation harness. The harness should accept a dataset of input-output pairs, run the relevant evaluators in parallel (subject to rate limits), and aggregate the results. I also find it helpful to have a utility function that outputs these metrics as a single-row dataframe. This makes it easy to copy-paste results into Excel (which product managers prefer for tracking). With a bit of conditional formatting, we can easily identify improvements or regressions.

**Integrate the eval harness with the experiment pipeline.** When our eval harness can directly consume the output of our experiments, running experiments and evals at scale becomes simple. We can tweak a config—prompt templates, retrieval parameters, model choice and parameters—generate output, and immediately evaluate it. This tight feedback loop allows us to iterate fast. For example, if we want to assess a model migration from Claude Haiku 3.5 to Haiku 4.5, we make a one-line config change, start the pipeline, get lunch, and check results.

**How many samples should we evaluate?** This depends on the statistical confidence we need. Assume our product requirement is to have a defect rate below 5%. If we run an experiment on 200 samples and observe 3% defects, our 95% confidence interval is roughly 3% ± 2.4%. This gives us a range of 0.6 - 5.4% defect rate. And because the upper bound exceeds 5%, we can’t confidently conclude that the current configuration has met the release requirement.

We can tighten this estimate by having more samples. If we double the output to 400 samples, the interval shrinks to 3% ± 1.7%. Now our upper range of 4.7% is below the requirement of 5%. Note: Because standard error decreases proportionally to the *square root* of sample size, to reduce the margin of error by half, we need to *quadruple* the sample size. Thus, there are diminishing returns to adding more samples. (Also see [Anthropic’s deep dive](https://www.anthropic.com/research/statistical-approach-to-model-evals).)

• • •

I’d like to end with an anecdote of applying evals well. I recently observed a team invest ~4 weeks into building their evaluation harness. This included defining eval criteria, collecting human annotations, aligning evaluators, and building an experiment harness. Stakeholders were initially worried that this was a distraction from building the product itself.

But the payoff was almost immediate. Within the next two weeks, the team ran dozens of experiments across different models, retrieval configurations, and prompt templates to iterate to a working product. And in the next few months, they ran a few hundred more to polish the product, add new features, and improve edge cases. This would have been impossible if they were bottlenecked on human annotations after each config change.

That is the benefit of having product evals; not just to measure and improve the quality of the product, but to tighten the feedback loop and help us iterate faster.

**Update:** [Harrison Chase](https://x.com/hwchase17/status/1995519920734666930?s=20), founder of LangChain/LangSmith, recorded a video on how to build product evals (label data, align evaluators, run eval harness) in LangSmith.

## Additional reading

* [Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/)
* [Using LLM-as-a-Judge For Evaluation: A Complete Guide](https://hamel.dev/blog/posts/llm-judge/)
* [LLM Evals: Everything You Need to Know](https://hamel.dev/blog/posts/evals-faq/)
* [In Defense of AI Evals, for Everyone](https://www.sh-reya.com/blog/in-defense-ai-evals/)
* [Evaluating the Effectiveness of LLM-Evaluators (aka LLM-as-Judge)](/writing/llm-evaluators/)
* [AlignEval: Building an App to Make Evals Easy, Fun, and Automated](/writing/aligneval/)
* [An LLM-as-Judge Won’t Save The Product—Fixing Your Process Will](/writing/eval-process/)

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Nov 2025). Product Evals in Three Simple Steps. eugeneyan.com.
> https://eugeneyan.com/writing/product-evals/.

or

```
@article{yan2025product-evals,
  title   = {Product Evals in Three Simple Steps},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2025},
  month   = {Nov},
  url     = {https://eugeneyan.com/writing/product-evals/}
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
[eval](/tag/eval/)
[engineering](/tag/engineering/)
[production](/tag/production/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Advice for New Principal Tech ICs (i.e., Notes to Myself)](/writing/principal/)
[2025 Year in Review »](/writing/2025-review/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---