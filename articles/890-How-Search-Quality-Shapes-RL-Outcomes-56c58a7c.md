---
title: 'How Search Quality Shapes RL Outcomes'
company: Exa
tag: 搜索
date: 2026-05-13
url: https://exa.ai/blog/rl-search-outcomes
account: 
origin: harvest2-202607
---
## [#](#introduction)Introduction

Search agents have demonstrated dramatic improvements in performance when trained with reinforcement learning (RL). However, existing work often uses Google as the backend. An understudied question is how training on different web search tools impacts RL outcomes.

We compare Exa with a Google baselineaaWe use SERP as a proxy for Google results, as it is widely used for post-training language models today.[1](#citation-2),[2](#citation-3),[3](#citation-4) and find that agents trained with Exa as the search backend during RL reach higher performance with less training compute.

Prior work on search-augmented RL plotted by retrieval source (internal index vs. live web) and whether the search method is held fixed or varies during training. This work studies the understudied live-web, varying-method quadrant.Top-left: live search agents with a single search engine [2, 3, 4, 8, 9]. Top-right (this work): impact of live-web retrieval backend on RL. Bottom-left: RL over offline indexes with fixed retrieval [5, 6, 7]. Bottom-right: ablations over offline retrieval methods [11, 12].Live web corpusOffline corpusFixed retrieval methodAblate retrieval methodLive search agentswith a single search engine

[[1](#citation-2), [2](#citation-3), [3](#citation-4), [7](#citation-8), [8](#citation-9)]

Impact of live-webretrieval backend on RLTHIS WORKRL over offline indexeswith fixed retrieval

[[4](#citation-5), [5](#citation-6), [6](#citation-7)]

Ablations over offlineretrieval methods

[[10](#citation-11), [11](#citation-12)]

Prior research in training search agents with reinforcement learning has often kept the retrieval method fixed.

1. Early research taught models to retrieve over offline corpora[4](#citation-5),[5](#citation-6),[6](#citation-7), learning to reason over multi-hop questions.
2. Later work added live web search to the action space[7](#citation-8),[8](#citation-9), but still fixed the retriever, usually to a SERP-based backend.

Issuing queries across the live web during training can be prohibitively expensive and unpredictable[9](#citation-10), so ablations of the retrieval method for RL usually remain limited to offline indexes[10](#citation-11),[11](#citation-12).
Because Exa has its own search engine and web index, we can study this interaction at scale.

## [#](#how-do-we-do-it)Experimental Design

### [#](#model-and-action-space)Model and Action Space

To isolate the impact of live search during RL, we train two models, one with Exa and one with SERP, and hold all other variables constant.

We train Qwen3-4B-Instruct-2507[12](#citation-13) with LoRA adapters using [Tinker](https://thinkingmachines.ai/tinker/). Prior work has found that LoRA can match full fine-tuning performance, even with small ranks[13](#citation-14).

Both agents use the same system prompt, adapted from Search-R1[4](#citation-5),[14](#citation-15), to avoid prompt-induced behavioral differences. Each search tool call returns 5 live web results, each truncated to a snippet of maximum 2,000 characters. The agent is not aware of the search variant it has access to. This tool configuration was chosen with model context limits in mind, as we initially observed long multi-hop trajectories quickly saturating the context window. Though other harness optimizations are possible, here we focus primarily on the comparison of search providers.

Question“At the end of what year did the tribes from the place where the Rossen culture is located invade the Roman Empire?”

Expected Answer406

Exa Agent Rollout

From the search results:  
The crossing of the Rhine by a mixed group of barbarians (including Vandals, Alans, and Suebi) is traditionally considered to have occurred on 31 December 406, initiating a wave of destruction in northern Gaul.

Correct Answer

406

Query“At the end of what year did the tribes from the place where the Rossen culture is located invade the Roman Empire?”

ResponseI need to find out at the end of what year the tribes from the place where the Rossen culture is located invaded the Roman Empire.
Step 1: Identify the location of the Rossen culture.
Step 2: Determine which tribes are from that location.
Step 3: Find out when those tribes invaded the Roman Empire, specifically the end year of that invasion.
First, I need to identify the location of the Rossen culture.

Tool call{"query": "Rossen culture location"}

Results

1.<https://en.wikipedia.org/wiki/R%C3%B6ssen_culture>

2.<https://en.wikipedia.org/wiki/Rossen_culture>

3.<https://dbpedia.org/page/R%C3%B6ssen_culture>

4.<https://www.historyatlas.com/groups/rossen-culture/>

5.<https://www.archaeologs.com/w/rossen-culture/en>

ResponseI need to identify the location of the Rossen culture to determine which tribes are from that location and when those tribes invaded the Roman Empire.
From the search results:
- The Rossen culture (also spelled Rössen culture) is a Central European culture of the middle Neolithic (4,600–4,300 BC).
- It is named after the necropolis of Rössen (part of Leuna, in the Saalekreis district, Saxony-Anhalt).
- The Rössen culture has been identified in 11 of the 16 states of Germany (it is only absent from the Northern part of the North German Plain), but also in the southeast Low Countries, northeast France, northern Switzerland and a small part of Austria.
- The geographical range is North-Central Europe corresponding roughly to modern-day Germany, Austria and the Low Countries.
So the Rossen culture is located in Central Europe, primarily in Germany, Austria, and the Low Countries.
Now I need to find out which tribes from this location invaded the Roman Empire and at what year, specifically the end year of that invasion.
Let me search for information about tribes from Central Europe (specifically Germany, Austria, or Low Countries) that invaded the Roman Empire and the year of that invasion.

Tool call{"query": "tribes from Central Europe Germany Austria Low Countries invaded Roman Empire year"}

Results

1.<https://en.wikipedia.org/wiki/Chronology_of_warfare_between_the_Romans_and_Germanic_peoples>

2.<https://en.wikipedia.org/wiki/Germanic_tribes>

3.<https://en.wikipedia.org/wiki/Quadi>

4.<http://www.britannica.com/topic/Marcomanni>

5.<https://en.wikipedia.org/wiki/Crossing_of_the_Rhine>

ResponseI need to determine the end year of the invasion by tribes from the Rossen culture location (Central Europe, primarily Germany, Austria, and the Low Countries) into the Roman Empire.
From the search results:
- The Rossen culture is a Central European Neolithic culture (4,600–4,300 BC), so it is ancient and not directly related to invasions of the Roman Empire.
- The Germanic peoples (tribes in Northern Europe during Classical antiquity and Early Middle Ages) are mentioned as having conflicts with the Romans.
- The Marcomanni, a Germanic tribe, invaded Roman territory around 167 AD, penetrating into Italy.
- The crossing of the Rhine by a mixed group of barbarians (including Vandals, Alans, and Suebi) is traditionally considered to have occurred on 31 December 406, initiating a wave of destruction in northern Gaul.
The Rossen culture is from the Neolithic period (4,600–4,300 BC), which is very ancient and predates the Roman Empire. Therefore, tribes from the Rossen culture cannot have invaded the Roman Empire.
However, the question might be referring to tribes from Central Europe (modern-day Germany, Austria, Low Countries) during the Roman era, such as Germanic tribes like the Marcomanni or Suebi.
The Marcomanni invaded Roman territory around 167 AD, but the question asks for the end of the year of the invasion.
The crossing of the Rhine in 406 AD is a significant event in the decline of the Roman Empire, initiated by Germanic tribes.
Given that the Rossen culture is from the Neolithic period and cannot be the source of invasions of the Roman Empire, it is likely there is a misunderstanding or mix-up in the query.
But if we interpret "tribes from the place where the Rossen culture is located" as Central Europe (Germany, Austria, Low Countries) during the Roman era, the most relevant invasion event is the crossing of the Rhine in 406 AD.
The end year of that invasion (crossing of the Rhine) is 406 AD.
Answer: 406

View full trajectory detail →

SERP Agent Rollout

The Goths first invaded the Roman Empire in 376 AD, and they defeated the Romans at the Battle of Adrianople in 378 AD.  
The final answer to the question is 378, as this is when the major battle and defeat occurred, marking the end of the initial phase of the invasion.

Incorrect Answer

378

Query“At the end of what year did the tribes from the place where the Rossen culture is located invade the Roman Empire?”

ResponseTo answer the question about the year when the tribes from the place where the Rossen culture is located invaded the Roman Empire, I need to follow these steps:
1. Identify the location of the Rossen culture.
2. Determine the tribes that originated from this location.
3. Find out when these tribes invaded the Roman Empire.
First, I'll search for information about the Rossen culture and its location to understand where it is situated.
Next, I'll look into the tribes that originated from this location and their historical interactions with the Roman Empire, particularly focusing on any invasions.
Finally, I'll determine the specific year at the end of which such an invasion occurred.
Let me start by searching for information about the Rossen culture and its location.

Tool call{"query": "Rossen culture location and historical background"}

Results

1.<https://en.wikipedia.org/wiki/R%C3%B6ssen_culture>

2.<https://neolithicarchitecture.com/rossen-culture/>

3.<https://arkeonews.net/stone-age-farmers-settled-near-dortmund-airport-7000-years-ago/>

4.<https://westfalen.museum-digital.de/index.php?id=1223&navlang=en&t=tag>

5.<https://celticlifeintl.com/on-the-trail-of-celtic-europe-2/>

ResponseThe Rossen culture is a Central European culture of the middle Neolithic (4,600–4,300 BC). It is located in parts of Germany, Austria, the Low Countries, northeast France, and northern Switzerland. Since it is a Neolithic culture from around 4600 to 4300 BC, it predates the Roman Empire by several millennia.
The Roman Empire existed from around 27 BC to 476 AD, so any invasion by tribes from the Rossen culture location would have occurred after the Neolithic period and during the time of the Roman Empire.
However, the Rossen culture itself was not involved in invasions of the Roman Empire because it existed thousands of years before the Roman Empire. The tribes that later invaded the Roman Empire were not from the Rossen culture era.
I need to search for information about tribes from the region of the Rossen culture that invaded the Roman Empire, and specifically when those invasions occurred.

Tool call{"query": "tribes from Central Europe region of Rossen culture that invaded Roman Empire and when"}

Results

1.<https://www.history.com/articles/goths-and-visigoths>

2.<https://en.wikipedia.org/wiki/Barbarian_invasions_into_the_Roman_Empire_of_the_3rd_century>

3.<https://www.worldhistory.org/Goths/>

4.<https://europe.factsanddetails.com/article/entry-1089.html>

5.<https://www.quora.com/Where-did-the-barbarian-tribes-that-invaded-the-Roman-Empire-come-from>

ResponseThe tribes from the place where the Rossen culture is located (Central Europe) that invaded the Roman Empire were the Goths. The Goths first invaded the Roman Empire in 376 AD, and they defeated the Romans at the Battle of Adrianople in 378 AD.
The question asks for the year at the end of which the invasion occurred. Since the invasion began in 376 AD and the major defeat occurred in 378 AD, the invasion was ongoing during the late 4th century.
However, the key point is that the invasion started in 376 AD and continued, with the Battle of Adrianople in 378 AD marking a major turning point.
The final answer to the question "At the end of what year did the tribes from the place where the Rossen culture is located invade the Roman Empire?" is 378, as this is when the major battle and defeat occurred, marking the end of the initial phase of the invasion.
Answer: 378

View full trajectory detail →

UntrainedTrained

**Figure 1:** Agent rollout example. Within the trained trajectories, both agents make two search calls with the same information. Only Exa retrieves a webpage with the correct information for the question: <https://en.wikipedia.org/wiki/Crossing_of_the_Rhine> (which states the year 406), which is necessary for the agent to synthesize with the first search results. Both untrained agents incorrectly respond with “never” after a single search call.

### [#](#training-and-reward-design)Training and Reward Design

Beyond the agent and its action space, each rollout is shaped by the training data, optimizer, and reward signal applied at the end of the trajectory.

We train on two multi-hop QA datasets, MuSiQue and HotpotQA[15](#citation-16),[16](#citation-17), using Dr. GRPO[17](#citation-18).

The reward is a single binary signal at the end of each trajectory. We initially graded with exact substring matching, but found the agent receiving large gains in reward from formatting its responses differently, rather than improving on accuracybbFor example, the agent learned to output increasingly verbose responses that could match the correct answer by chance, or intentionally list alternative answers. [See the Appendix for an example.](#early-reward-hacking-example). We switched to the LLM grader from SimpleQA[18](#citation-20), and apply a -0.25 penalty when a trajectory exceeds context limits.

After training the models, we evaluate using pass@k[19](#citation-21),ccResearch has shown RL can concentrate probability mass on correct trajectories, reducing diversity and degrading pass@k at higher k. Evaluating across multiple values of k therefore helps distinguish genuine improvements in solution-finding from probability-mass concentration on a narrower set of trajectories.[20](#citation-23),[21](#citation-24),[22](#citation-25) on MuSiQue and HotpotQA test splits and on OOD benchmarks 2WikiMultihopQA, FRAMES, BrowseComp, and SimpleQA[15](#citation-16),[16](#citation-17),[18](#citation-20),[23](#citation-26),[24](#citation-27),[25](#citation-28). As a reference point, we compare against Qwen3-235B-A22B-Instruct-2507[26](#citation-29) with the same toolset. Every variable besides the search backend is fixed.

## [#](#results)Results

### [#](#impact-of-retrieval-backend)Impact of Retrieval Backend

Across evaluations, Exa-trained agents outperform SERP-trained agents. Three patterns stand out:

(i) Post-RL Exa models outperform post-RL SERP models on pass@k across all values of k.

(ii) Training with Exa is more compute efficient than SERP: taking fewer tokens, turns, and search calls to reach the same performance. This also results in lower-token cost inference.

(iii) Exa-trained 4B agents outperform SERP-trained agents on every benchmark and often exceed the larger untrained 235B model.

|  | Exa | | | SERP | | |
| --- | --- | --- | --- | --- | --- | --- |
| 4B Base | 4B+RL | 235B | 4B Base | 4B+RL | 235B |
| SimpleQA | 0.651 | 0.767 | 0.730 | 0.579 | 0.692 | 0.689 |
| 2WikiMultihopQA | 0.500 | 0.839 | 0.774 | 0.461 | 0.798 | 0.747 |
| HotpotQA | 0.521 | 0.694 | 0.632 | 0.491 | 0.684 | 0.620 |
| FRAMES | 0.316 | 0.566 | 0.604 | 0.272 | 0.521 | 0.578 |
| MuSiQue | 0.151 | 0.311 | 0.273 | 0.146 | 0.307 | 0.259 |
| BrowseComp | 0.020 | 0.043 | 0.039 | 0.008 | 0.039 | 0.055 |

**Figure 2:** Pass@1 accuracy with 200 questions and n=200 rollouts per question across QA and retrieval benchmarks. Highest scores per benchmark are highlighted in dark blue, and highest small model results are highlighted in light blue. Exa-trained 4B agents outperform SERP-trained agents on every benchmark and often exceed the larger 235B model.

Average pass@k

SimpleQA, FRAMES, 2WikiMultihopQA, MuSiQue, HotpotQA, BrowseComp

Exa base

SERP base

Exa RL

SERP RL

pass@k

0.300.350.400.450.500.550.600.650.700.75

125102050

k

**Figure 3:** Exa improves pass@k across sampling budgets. Average pass@k across six benchmarks for 4B agents before and after RL with either Exa or SERP as the search backend. The Exa-trained agent achieves the highest performance across all sampling budgets before and after RL. [See the Appendix for per-benchmark plots.](#figure-5-per-benchmark-plots)

### [#](#token-efficiency)Token efficiency

We find that training with Exa requires fewer tokens for the same number of steps. This gap is largely due to the difference in turn count per rollout: during training, the SERP agent makes more search calls per rollout than the Exa agent. Because both agents start from the same base policy, they initially use similar numbers of turns and search calls, but this gap grows over training; in our training setup:

* It took 20% more total tokens to train with SERP to step 100 (1.58B vs. 1.89B).
* The Exa agent took 69% fewer tokens to achieve equal performance with the SERP-trained agent (prefill and decode) to match performance (0.58B vs. 1.89B).
* The Exa agent took 62% fewer search calls and 58% fewer turns to achieve equal performance with the SERP-trained agent (93k vs. 248k, 146k vs. 350k).

Per-rollout cost over training

total tokens / rollout

total tokens / rollout

05000100001500020000250003000035000

0255075100

training step

turns / rollout

turns / rollout

1.522.533.544.5

0255075100

training step

search calls / rollout

search calls / rollout

0.511.522.533.5

0255075100

training step

Exa

SERP

**Figure 4:** Exa training uses fewer tokens and search actions per rollout. Average rollout cost over RL training for agents using Exa or SERP as the search backend. Both agents learn to take more turns and issue more searches over training; the SERP agent's rollouts grow longer, using more total tokens, turns, and search calls per rollout by the end of training.

Average rollout cost before and after RL

total tokens / rolloutSERP +6.6% ± 0.1%02k4k6k8k10k3,7038,5193,6139,082ExaSERPturns / rolloutSERP +15.3% ± 0.1%0123452.133.612.164.16ExaSERPsearch calls / rolloutSERP +17.2% ± 0.1%0.00.51.01.52.02.53.03.54.01.142.711.173.18ExaSERP

Base modelTrained model

**Figure 5:** Average rollout cost before and after RL for agents using Exa or SERP. Base policies have equivalent token, turn, and search-call counts across backends. After training the SERP agent uses more tokens, turns, and search calls per rollout than the Exa agent, increasing inference cost despite lower benchmark performance.

### [#](#search-engine-at-training-vs-inference)Search engine at training vs. inference

To separate training-time and inference-time effects, we evaluate each trained agent with both search backends.

* After using Exa for RL, agents perform better than having used SERP for training, regardless of the final engine used.
* Using Exa makes search agents perform better at inference time, regardless of how they were trained.

Cross-backend pass@k

SimpleQA, FRAMES, HotpotQA, MuSiQue, 2WikiMultihopQA, BrowseComp

Exa-trained · Exa engine

Exa-trained · SERP engine

SERP-trained · Exa engine

SERP-trained · SERP engine

pass@k

0.500.550.600.650.700.75

125102050

k

**Figure 6:** Exa's training benefit transfers across inference backends. Average pass@k across six benchmarks when Exa- and SERP-trained agents are evaluated with matched and swapped retrieval methods at inference time. Using Exa at inference improves performance for both trained agents, and training with Exa outperforms SERP-trained agents regardless of inference backend. [See the Appendix for per-benchmark plots.](#figure-6-per-benchmark-plots)

Cross-engine pass@1SimpleQA, FRAMES, HotpotQA, MuSiQue, 2WikiMultihopQA, BrowseComp354045505560pass@138.257.356.2Exa35.654.354.3SERP

base (untrained)matched (trained on this engine)cross (trained on the other engine)

**Figure 7:** Pass@1 averaged across six benchmarks for (1) untrained agents (2) agents evaluated on the same backend used during RL (3) agents evaluated on the opposite backend at inference time. Exa improves the untrained base policy and yields stronger trained agents at inference time.

We hypothesize that this difference could be attributable to learning with Exa being more sample efficient: Exa retrieves results containing information to arrive at the correct answer in fewer actions than SERP.

In multi-turn agentic RL, higher per-step success makes rewards less sparse and helps the model learn from fewer rollouts. This may be due to the semantic nature of Exa search, which is designed specifically to handle non-keyword natural-language queries.

To measure per-action sample efficiency, we run the same base policy on the same prompts for roughly 240,000 rollouts per engine (480k total) between six benchmarks.

We see that for a search call from the same policy, Exa returns sites that contain the answer +10.7% more often than SERPdd36.1±2.4% compared to 32.6±2.3%; Δ+3.50±1.55pp, and for the first search call in the rollout, +11.5% more oftenee34.0±2.5% compared to 30.5±2.5%; Δ+3.51±1.68pp. We believe this indicates that Exa provides a denser signal per action, as the agent is able to see the correct answer more often in a rollout. This may give the agent more opportunities to see the correct answer and reason over it, which may also lead to a lower overall search count. Retrieval quality appears to matter at training time as much as at inference time: a denser per-step signal compounds over many rollouts.

## [#](#conclusion)Conclusion

In this work, we studied how the search backend shapes RL for large language models.

Holding all else fixed, we compared one agent trained with Exa against one agent trained with a SERP backend. Across our benchmarks, Exa-trained agents achieve higher pass@k at lower training and inference cost. These gains persist when the engine is swapped at inference time, showing that the model may be learning transferable skills for search when training with Exa. Exa also improves inference performance even for agents not trained on Exa, though the strongest results come from using Exa during both training and inference.

### [#](#future-work)Future Work

Here is a list of ongoing questions we hope to address in upcoming research.

* Scaling up training with bigger models, longer runs, and larger batch sizes.
* Interpreting what learned characteristics result in improved search performance, particularly after an initial learning phase.
* Train with a more advanced harness including elements like content fetching, and context pruning.

Our results suggest that the retrieval engine is a crucial component for agents searching over the web, especially when paired with the same tool at inference time. A better search backend can both improve the final performance of a search agent and improve the learning signal during RL.