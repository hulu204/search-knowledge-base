---
title: 'Building Deep Research: How we Achieved State of the Art'
company: Tavily
tag: 搜索
date: 2025-11-24
url: https://www.tavily.com/blog/research-en
account: 
origin: harvest2-202607
---
![Building Deep Research: How we Achieved State of the Art](https://cdn.sanity.io/images/5tlb0lxv/production/3bf4ce03a477fa3c29606e5f0b6c4b1df8829fcb-390x194.webp?w=1200&q=75&auto=format)

/product·7 min read

# Building Deep Research: How we Achieved State of the Art

Research agents are becoming a cornerstone of modern knowledge work. In this post, we share the technical and philosophical lessons behind building a state-of-the-art deep research agent—covering agent harness design, context engineering, and how we achieved dramatically lower token usage while reaching SOTA performance.

![](https://cdn.sanity.io/images/5tlb0lxv/production/eaf934a5a9a2e3cdb8b857ce5032c20a6d637095-112x112.png?w=64&h=64&q=75&auto=format)

Michael Griff, Dean Sacoransky & Noah Nefsky

Nov 24, 2025

Research agents are rapidly becoming one of the most important applications of AI. Research is a foundational knowledge-work task: collecting, reading, and synthesizing information underpins everything from writing and decision-making to coding itself. Yet human-driven research is constrained by memory, reading speed, and time. AI research agents, by contrast, can process vast amounts of information, synthesize insights instantly, and scale effortlessly. Because of this, research agents are emerging as a top use case for AI today and will soon become a core subcomponent of broader agentic workflows across content generation, coding, sales, and more. In this post, we share the technical and philosophical lessons we’ve learned building a ****state-of-the-art research agent****, and where we believe the field is headed.

## Building for the Future

### Agent Harness

The task of building an [agent harness](https://www.vtrivedy.com/posts/claude-code-sdk-haas-harness-as-a-service?ref=blog.langchain.com) is to create a software layer that enhances a model’s runtime execution through context management, tool invocations, loop control, orchestration, and error handling. Building applications on top of rapidly improving models is, however, a modern engineering challenge. How can we design software today that absorbs the performance gains from future model releases?

This requires forecasting how models will evolve, staying optimistic about their progress, limiting assumptions, and avoiding hand-crafted optimizations.

We learned this the hard way seven months ago, when we had to abandon our first attempt at deep research and rebuild the entire system from scratch. The first architecture was complicated and sophisticated (we thought this was a good thing), but its assumptions became bottlenecks when the next generation of models arrived.

### Models

Over the last seven months, model capabilities have quietly but meaningfully evolved (especially in their tool-calling abilities). This single optimization focus has pushed us from workflows to agents. We believe future models will be trained to solve the current pain points of agent developers. Every model is ultimately consumed by a harness, so models should evolve in service of that harness. We hope to see models improve in high-recall summarization (for context compression), tool-calling reliability, and concision in writing.

### Tools

Similarly, tools should evolve to support LLMs and widely adopted agent harnesses. The best tools should perform some context engineering on the tool side, abstracted away from the agent. They should return only the most relevant data instead of dumping large volumes of tokens into the context window. As a tool provider, we’ve invested heavily in our [advanced search](https://docs.tavily.com/documentation/api-reference/endpoint/search#body-search-depth) feature**,** which has context engineering baked in. This in turn lowers hallucinations and latency for the downstream agent processes.

### Takeaways

To build agents that improve over time, we followed a few guiding principles:

1. Simplify orchestration logic and lean into autonomy.
2. Pay close attention to what models and tools are being optimized for, and leverage their emerging capabilities.
3. Focus on context engineering (more on this in the next section).

## Context Engineering — An Exercise in Curation

Long-horizon research tasks expose a fundamental challenge in current agent design: the task of maintaining a clean, optimized context window over time. If curating context is not a task the engineer pays close attention to, the agent is almost destined for failure. The following outlines our thinking around this concept within the deep research domain.

### Context-Managed Web Retrieval

Using Tavily’s Advanced Search is the natural first step to take in overcoming this challenge, in that it abstracts away the processing of raw web content and returns only the most relevant content chunks from each source. In leveraging this functionality, we let Tavily Search do the heavy lifting and allow Tavily Research to reap the benefit, gathering the most valuable content in a latency-efficient manner.

Ensuring that the agent does not overfit to a single research thread is the next step towards an effective context-gathering pipeline. It is in this regard that global state persistence and source deduplication is paramount, and in our case, it helps threefold:

1. It ensures the agent is exposed only to fresh information.
2. It allows the engineer to recognize when the information scope is narrowing and to prompt the agent to explore untapped relevant domains.
3. It lends to effective source attribution later on in the generation process.

At Tavily, interacting with the web is our bread and butter. Architecting a refined web-retrieval system engineered for deep research was a foundational building block for our deep research agent design as a whole.

### Modeling the Human-Web Interaction

Humans research in an inherently unstructured, iterative way. We start by defining the task: what we’re trying to accomplish and what information we need. We next gather data from our sources, extracting the key insights and holding them in short-term memory, letting these distilled thoughts guide our subsequent actions.

This cycle repeats: collect information, distill it, decide what to do next. Only once we’ve gathered enough understanding to produce the final deliverable do we return to the original sources, using them as references to assemble the finished product.

We believe that deep research agents should be designed in a similar manner, in that tool outputs should be distilled into reflections, and ****only**** the set of past reflections should be used as context for your tool caller. Similar to humans, it is only at the point when your agent begins to prepare the final deliverable that you must provide the raw information as context, so as to ensure there is no information loss.

### Doing More with Less

This approach differs from traditional context structuring in a ReAct agent-based architecture. Typically, tool calls and outputs are propagated through the tool calling loop, with previously retrieved/generated tokens being persisted in the context window on each subsequent iteration. This pattern can be seen in [LangChain’s Open Deep Research](https://github.com/langchain-ai/open_deep_research) agent implementation, and from a token consumption perspective, it can be modeled by the following quadratic series, where ****n**** is the amount of tokens the tool calling model is invoked with on each tool calling iteration, and ****m**** is the number of tool calling iterations.

![ ](https://cdn.sanity.io/images/5tlb0lxv/production/2570b77c179537422012ab716cee332f24c817ea-1402x164.png?w=1200&q=75&auto=format)![ ](https://cdn.sanity.io/images/5tlb0lxv/production/4b5ca6718ea60f4b2d9b79f2da0061a235e94613-2000x1101.png?w=1200&q=75&auto=format)

Contrarily, our proposed method of context engineering removes this token propagation (as the knowledge distillations, even when aggregated, are negligible when compared to the quantity of tokens gathered from web) and can be modeled by the following linear series.

![ ](https://cdn.sanity.io/images/5tlb0lxv/production/ff3eb34bb5c3aa1d0e0483868811131e0391e89d-1400x136.png?w=1200&q=75&auto=format)![ ](https://cdn.sanity.io/images/5tlb0lxv/production/8aceb37a075a9939db3c296774ca9673a077312f-2000x1101.png?w=1200&q=75&auto=format)

When comparing the two approaches, tokens are saved on a per-agent basis by a factor of ****(m+1)/2****, and when extrapolating this over a multi-agent system and with consumption at scale, the absolute value of tokens saved becomes even more significant.

Through this methodology, we were able to ****reduce token consumption by 66%**** (when compared to Open Deep Research) while achieving [SOTA on DeepResearch Bench](https://huggingface.co/spaces/muset-ai/DeepResearch-Bench-Leaderboard) – the intersection of quality and efficiency in full effect.

![ ](https://cdn.sanity.io/images/5tlb0lxv/production/2a2e76971d549f33ce16aaa5f6b85758e3bf3066-704x629.png?w=1200&q=75&auto=format)

Building production-grade agents is a balancing act. We leaned into autonomy to maximize performance and quality, while still meeting strict requirements for latency, cost, and reliability.

### ****Engineering with Non-Determinism****

LLMs are inherently non-deterministic, and we found that giving them guard-railed freedom to reason and iterate produces the strongest results. Autonomy, when gone wrong, can cause agent behavior to go off track. Tools can be called incorrectly, LLMs can overfit to a subtopic, and expected reasoning patterns may break. No single safeguard will catch all of these issues.

A shift in engineering mindset is required: treat failure modes as core design considerations, not afterthoughts. Simple guardrails like tool-call retries or model cascades help, but proactively anticipating anomalies, reinforcing proper patterns in prompting and edge-case testing is what enables production-grade, long-running agents.

![ ](https://cdn.sanity.io/images/5tlb0lxv/production/ce2f30c13fbd95f18ee21bf2edfdfb17b0ca5a01-824x634.png?w=1200&q=75&auto=format)

### ****Optimal Tooling — Less is More****

From our experience, it’s better to expose a small, essential toolset to the agent rather than a large, complex one. We were tempted to over-engineer by adding many tools that seemed useful in theory, but in practice this created new failure modes and made it harder for LLMs to consistently choose the right tool and iterate effectively.

### ****Evals****

We used evals to steer our development process but also recognize their shortcomings. LLM-as-a-judge evals are difficult to trust: current models are non‑deterministic, uninterpretable in their reasoning, and can turn into bottlenecks, especially for long‑running agents where a single experiment can take days to complete.

Rather than optimizing for benchmark scores, we optimized for directional feedback. The core question was always: **did this change make the agent more reliable and more useful in practice?** Evals became a tool for validating that direction, not the optimization target. Intuition and careful agent‑trace monitoring consistently provided higher‑signal feedback than any single eval score.

Overall, the **best** outcome is rarely the highest numerical score. For production systems, improvements like reduced token usage, reliability, lower latency, and fewer failures are more valuable than a one‑point bump on an eval.

If you’re interested in experiencing the result of these findings in practice, you can sign up for early access to ****Tavily Research**** [here](https://deepresearch.tavily.com/).