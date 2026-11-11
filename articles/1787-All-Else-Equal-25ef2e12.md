---
title: 'All Else Equal'
company: Tunkelang
tag: 评测
date: 2024-09-10
url: https://dtunkelang.medium.com/all-else-equal-f160d5a026bf
account: Tunkelang
origin: harvest3-202607
---
# All Else Equal

In [*The Three-Body Problem*](https://en.wikipedia.org/wiki/The_Three-Body_Problem_(novel)), [Liu Cixin](https://en.wikipedia.org/wiki/Liu_Cixin) describes how an alien species drives scientists to suicide by making it impossible for them to produce consistent experimental results. Some might find it difficult to relate to the scientists’ existential despair, but I found the premise compelling and chilling.

In this post, I do not tackle anything so sinister or abstract. Rather, I challenge a key assumption of A/B testing — namely, that all else is equal. I hope to inspire curiosity and reflection rather than existential despair.

### A/B Testing: A Simple Example

[A/B testing](https://en.wikipedia.org/wiki/A/B_testing) is the most popular method for online experimentation. It compares two versions of an application to determine which one performs better. Typically, one is the “treatment” we are considering as a change and the other is a “control” that represents the current state of the application.

For example, consider a simple A/B test to determine whether increasing the page size for search results from 10 (control) to 20 (treatment) leads to an increased conversion rate. This is about as simple an A/B test as it gets.

Let us imagine that the test is successful, delivering a statistically significant increase in the conversion rate. What does this tell us?

### The World is Not So Simple

The answer may seem obvious: doubling the page size increases the conversion rate. More precisely, this result only holds if we hold all else equal — since the change in page size might interact with other changes, such as changing the page design. However,.we have to be even more pedantic: the result only holds given the current state of the world.

Consider the factors of screen size and network latency, both of which are determined by the searchers’ devices and locations. Both of these factors interact with page size to affect the experience. Increasing the page size may increase conversion in one set of conditions but decrease it in others.

In the physical world, we do not generally worry about the laws of nature being time-dependent. We treat the law of gravity and the speed of light as constants. However, the digital world changes far more rapidly than the physical one, as does user behavior. That makes it dangerous to assume that the conditions for an experiment hold indefinitely.

### Do Not Despair!

If you rely on AB testing as part of your day job, you might find this state of affairs disheartening. But please do not despair! We have it much better than the scientists in *The Three-Body Problem*. No aliens are out to get us!

Fortunately, there are things we can do to detect changes likely to invalidate our experiments over time. Here are a few:

- **Reverse Testing**. You can revisit an A/B test by reversing it — that is, using the current version as the control and the old version as the treatment. The catch is that maintaining the ability to perform reverse tests requires discipline and can incur [technical debt](https://en.wikipedia.org/wiki/Technical_debt).

- **Long-Term Holdout**. Typical A/B tests are short, e.g., two weeks. Running the control for longer (e.g., three months or a year) hedges against conditions changing during that time.

- **Monitoring**. While it is important to look at metrics when evaluating a change as part of an A/B test, it is also important to look broadly at metrics over time when you are not making any changes. Trends or sudden changes in metrics can tell you when the world is changing.

- **Snapshots**. While monitoring can alert you to unexpected changes in metrics, a more direct approach is to take a snapshot of metrics that hold at the time an A/B is conducted. Changes in those are particularly likely to invalidate the test results.

This list is not exhaustive. Hopefully, it helps you think about ways to keep in mind conditions outside the explicit scope of your experiments.

### The Only Constant is Change

As [Heraclitus](https://en.wikipedia.org/wiki/Heraclitus) said, the only constant is change. When we perform A/B tests, we need to bear in mind that the results assume present conditions that are subject to change. As [Ferris Bueller](https://en.wikipedia.org/wiki/Ferris_Bueller%27s_Day_Off) warned us, “Life moves pretty fast. If you don’t stop and look around once in a while, you could miss it”.
