---
title: 'https://eugeneyan.com//writing/recsys2020/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/recsys2020/
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

# RecSys 2020: Takeaways and Notable Papers

[
[recsys](/tag/recsys/)
[deeplearning](/tag/deeplearning/)
[production](/tag/production/)
[survey](/tag/survey/)
]
 · 16 min read

[RecSys 2020](https://recsys.acm.org/recsys20/) ran from 22nd - 26th September. It was a great opportunity to peek into some of the latest thinking about recommender systems from academia and industry. Here are some observations and notes on papers I enjoyed.

## Emphasis on ethics & bias; More sequences & bandits

There was increased emphasis on ethics and bias this year. Day 1’s keynote was “[4 Reasons Why Social Media Make Us Vulnerable to Manipulation](https://recsys.acm.org/recsys20/keynotes/#content-tab-1-0-tab)” ([Video](https://www.youtube.com/watch?v=BQYveMPwlNg)) while Day 2’s keynote was “[Bias in Search and Recommender Systems](https://recsys.acm.org/recsys20/keynotes/#content-tab-1-1-tab)” ([Slides](https://www.slideshare.net/CatalystDigital/keynote-bias-in-search-and-recommender-systems)).

Two (out of nine) sessions were on “Fairness, Filter Bubbles, and Ethical Concerns” and “Unbiased Recommendation and Evaluation”, discussing papers such as:

* [Deconstructing the Filter Bubble: User Decision-Making & Recommender Systems](https://dl.acm.org/doi/10.1145/3383313.3412246)
* [Debiasing Item-to-Item Recommendations with Small Annotated Datasets](https://dl.acm.org/doi/10.1145/3383313.3412265)
* [The Connection Between Popularity Bias, Calibration, and Fairness](https://dl.acm.org/doi/10.1145/3383313.3418487)

[Inverse propensity scoring](https://arxiv.org/abs/1602.05352) was a popular approach taken to debias recommendations:

* [Unbiased Learning for the Causal Effect of Recommendation](https://dl.acm.org/doi/10.1145/3383313.3412261)
* [Doubly Robust Estimator for Ranking Metrics with Post-Click Conversions](https://dl.acm.org/doi/10.1145/3383313.3412262)
* [Unbiased Ad Click Prediction for Position-aware Advertising Systems](https://dl.acm.org/doi/10.1145/3383313.3412241)

We also saw an increased shift towards sequence models (with [SASRec](https://ieeexplore.ieee.org/abstract/document/8594844) (2018) and [BERT4Rec](https://dl.acm.org/doi/abs/10.1145/3357384.3357895) (2019) being common benchmarks) and bandit and reinforcement learning for recommender systems:

* [SSE-PT: Sequential Recommendation via Personalized Transformer](https://doi.org/10.1145/3383313.3412258)
* [FISSA: Fusing Item Similarity Models with Self-Attention Networks](https://dl.acm.org/doi/10.1145/3383313.3412247)
* [Contextual User Browsing Bandits for Large-Scale Online Mobile Recommendation](https://dl.acm.org/doi/10.1145/3383313.3412234)
* [Learning to Collaborate via Multi-Agent Reinforcement Learning](https://dl.acm.org/doi/10.1145/3383313.3412233)

## Notable: Offline evaluation, MF > MLP, applications

Several papers on offline evaluation highlighted the [nuances and complexities](#towards-more-robust-offline-evaluation-and-study-reproducibility) of assessing recommender systems offline and suggested process improvements. Also, Netflix gave a great talk sharing their [findings from a comprehensive user study](#user-research-on-the-nuances-of-recommendations).

There was also a (controversial?) talk by Google [refuting the findings of a previous paper](#comparing-the-simple-dot-product-to-learned-similarities) where learned similarities via multi-layer perceptrons beat the simple dot product.

Of course, I also enjoyed the many papers sharing how organizations built and deploy [recommender systems in the wild](#industry-applications-context-unexpectedness-interesting-use-cases) (more [here](https://github.com/eugeneyan/applied-ml#recommendation)).

### User research on the nuances of recommendations

Zach Schendel from **Netflix discussed [recommendation complexity and their findings from user research](https://dl.acm.org/doi/10.1145/3383313.3411549)**. There are three sources of recommendation complexity, namely:

* Placement: Where is the recommendation located on the user interface?
* Person: Who is seeing the recommendation? What are her past experiences with the recommendation placement?
* Context: What is going on at that moment? What are the user’s needs?

Netflix found that users have different expectations across different recommendation placements. For example, users have higher expectations of similarity when it’s a 1:1 recommendation (e.g., after completing a show, Netflix would recommend a *single* next title). Such recommendations are risky as there are no backups, and there are no other recommendations to help the user understand similarity.

In contrast, users have lower expectations in 1:many recommendations (e.g., a slate of recommendations), such as when the user is browsing. In the example below, “Queer Eye” might seem far removed from “Million Dollar Beach House”. But with the other recommendations in the slate, it makes sense within the overall theme of reality shows.

![Netflix reality show recommendation slate](/assets/netflix-reality-show-slate.webp "Netflix reality show recommendation slate")

They also found that users have higher expectations in recommendations that result from explicit actions (e.g., search). In general, the greater the user effort (e.g., search, click), the higher the user expectation. Contrast this to lower effort recommendations, such as on the home page, or in recommendation slates when casually browsing.

![Netflix explicit search](/assets/netflix-explicit-search.webp "Netflix explicit search")

The two findings suggest there’s no one-size-fits-all approach for recommendations. Recommenders developed for the home page/email (low user effort) might *not* work similarly if placed on the detail page or search page. Also, 1:1 and 1:many recommendations should be built and evaluated differently.

Netflix also highlighted the importance of understanding users’ context. After finishing a reality show, users are likely to watch *another* reality show, right? Not necessarily. Netflix found that consecutive reality show watching happened only 18% of the time.

![Netflix reality show stats](/assets/netflix-reality-show-stats.webp "Netflix reality show stats")

There are many contexts where similarity is not required or can worsen recommendations. For example, users might want a change of pace or mood from that horror movie they just watched. Also, does the user stick to a specific genre (e.g., Korean dramas) or hop around diverse genres? A better understanding will help improve the user experience.

![Netflix reality show context](/assets/netflix-reality-show-context.webp "Netflix reality show context")

### Towards more robust offline evaluation and study reproducibility

Pablo Castells from the Autonomous University of Madrid shared about **how [different target sampling approaches](https://dl.acm.org/doi/10.1145/3383313.3412259) affect offline evaluation**. There are three ways of creating validation targets: With no unrated data, with all unrated data, and somewhere in between.

![Different ways of creating validation set targets](/assets/evaluation-different-validation-sets.webp "Different ways of creating validation set targets")

Three ways to generate validation set targets.

The relative performance of recommenders could differ based on how the validation set was created. Here’s an example below. On the left (with unrated data), recommendation set A outperforms recommendation set B. But on the right (without unrated data), recommendation set B is superior.

![Relative performance changes when considering rated and unrated ratings](/assets/evaluation-rated-vs-unrated.webp "Relative performance changes when considering rated and unrated ratings")

The relative performance of models differ when considering all unrated vs. no unrated labels.

They also ran several experiments on the MovieLens 1M dataset and demonstrated that the relative precision@10 performance differs with and without unrated data.

![Position swaps for models trained on the MovieLens 1M dataset](/assets/evaluation-bar-cross.webp "Position swaps for models trained on the MovieLens 1M dataset")

The relative performance of recommenders differ with and without unrated data.

Similarly, Zaiqiao Meng from the University of Glasgow showed how [different data splitting strategies](https://dl.acm.org/doi/10.1145/3383313.3418479) (for train and validation) can **affect the relative performance of recommendation systems in offline evaluation**. First, they discussed the four main data splitting strategies:

* Leave-one-last: Leave one last item, leave one last basket/session
* Temporal: Temporal split within each user, temporal split (on same date) globally
* Random: For each user, split interactions into train and test data
* User: Split some users into train, the rest into test

Then, with the three most popular splitting strategies (i.e., leave one last item, leave one last basket, and global temporal split), they ran experiments on the [Ta Feng](http://www.bigdatalab.ac.cn/benchmark/bm/dd?data=Ta-Feng) and [Dunnhumby](https://www.dunnhumby.com/source-files/) datasets. The relative performance of recommenders changed often across splitting strategies (indicated by the rank swaps).

![Position swaps under different data splitting strategies](/assets/evaluation-position-swaps.webp "Position swaps under different data splitting strategies")

They also found certain models to perform better under different splitting strategies: Triple2vec performs better under leave one last item while VBCAR does better under temporal evaluation.

Zhu Sun from Macquarie University **[examined 85 papers on implicit feedback-based top-N recommendations](https://dl.acm.org/doi/10.1145/3383313.3412489) published in the past three years**. Their paper gave a good overview of the different factors that could affect recommendation systems such as data pre-processing (and how data is excluded), objective functions, negative sampling, data splitting approaches, and evaluation metrics.

Among the 85 papers, they found inconsistencies on:

* Data filtering: Some studies excluded users and items with less than 5 ratings while others used a threshold of 10.
* Validation: Some used leave-one-out, others used split by ratio. (They also found 37% of papers tuned hyperparameters on the test set!)
* Negative sampling: Approaches included uniform sampling, low-popularity sampling, and high-popularity sampling.

Unsurprisingly, the relative performance of various models differed with different combinations of pre-processing, negative sampling, evaluation metrics, etc.

Pigi Kouki from Relational AI highlighted one key failing in offline evaluation metrics: They **penalize a model if it does not predict the same product (i.e., identical product ID)**. Thus, near-identical products—which a human might consider relevant—are not counted as hits. She then shared about their [two-step offline evaluation process](https://dl.acm.org/doi/10.1145/3383313.3412235) when building a recommender system.

First, they trained 15 models and selected five which performed best in offline evaluation:

* [SR-GNN](https://arxiv.org/abs/1811.00855): Best hit rate, mean reciprocal rank, and nDCG
* [V-STAN](https://arxiv.org/abs/1910.12781): Best precision, recall, and mean average precision
* [V-SKNN](https://arxiv.org/abs/1803.09587), [GRU4Rec](https://arxiv.org/abs/1511.06939): Best coverage and popularity
* [STAMP](https://www.kdd.org/kdd2018/accepted-papers/view/stamp-short-term-attentionmemory-priority-model-for-session-based-recommend): Satisfactory in all metrics

In the second step, human experts evaluated the recommendations from the five models. 10 experts evaluated the model across three categories in the home improvement domain. The experts had access to title, description, image, and links to the product. They could rate the recommendation as objectively relevant 👍, subjectively relevant ✅, or irrelevant 👎.

![Home Depot Expert Evaluation](/assets/home-depot-expert-evaluation.webp "Home Depot Expert Evaluation")

Recommendations were evaluated as objectively relevant 👍, subjectively relevant ✅, or irrelevant 👎.

In contrast to the offline evaluation metrics, human experts found GRU4Rec to have very relevant recommendations. However, because its recommendations did not match the IDs of products added to cart, GRU4Rec did not perform as well on offline evaluation metrics.

STAMP and GRU4Rec performed best in the second step and STAMP was put through an A/B test. This led to a 15.6% increase in CTR and an 18.5% increase in revenue per session.

Overall, these papers made me rethink my experimentation and offline evaluation workflow. Furthermore, offline evaluation of interactive machine learning systems (e.g., recommendation, search) is tricky as we can’t observe how user behaviour will change.

### Comparing the simple dot-product to learned similarities

Walid Krichene from Google **revisited (and overturned) the findings from the [neural collaborative filtering](https://dl.acm.org/doi/abs/10.1145/3038912.3052569) (NCF; 2017) paper** in his talk [Neural Collaborative Filtering vs. Matrix Factorization Revisited](https://dl.acm.org/doi/10.1145/3383313.3412488).

In the original NCF paper, a multi-layer perceptron (MLP) was suggested to replace the dot product. This was based on experimentation results (where MLP was superior) and the [universal approximation property](https://ai.stackexchange.com/questions/13317/where-can-i-find-the-proof-of-the-universal-approximation-theorem).

![Dot product vs multi-layer-perceptron](/assets/dot-product-vs-mlp.webp "Dot product vs multi-layer-perceptron")

For the current paper, the team ran multiple experiments on the MovieLens 1M and the Pinterest dataset. They found the dot product to be superior to learned similarity approaches (MLP and neural matrix factorization).

![Results from comparing dot product vs multi-layer-perceptron](/assets/dot-product-vs-mlp-results.webp "Results from comparing dot product vs multi-layer-perceptron")

When asked, Walid suggested that one possible reason was better hyperparameters. They found the matrix factorization parameters in the original NCF paper under regularized. Another possible reason could be the addition of explicit biases that have been empirically shown to improve model performance.

The paper also highlighted the practical advantages of the dot product, where retrieval can be done efficiently (linear complexity vs quadratic complexity for MLP). The dot product also doesn’t need to be learned. Thus, for most applications, the dot product should be the default approach.

(Note: In a previous [paper](https://dl.acm.org/doi/10.1145/3159652.3159727), Google had also demonstrated that MLPs/feed-forward networks were inefficient in capturing multiplicative interactions.)

### Industry applications: context, unexpectedness, interesting use cases

Moumita Bhattacharya from Etsy shared about their two approaches to **integrate [search query as context](https://dl.acm.org/doi/pdf/10.1145/3383313.3411480) into their content-based recommender** (image below). The goal is to include user intent (i.e., search query) and seasonality in candidate generation.

![Etsy's content based recommender](/assets/etsy-content-based-rec.webp "Etsy's content based recommender")

Etsy's content based recommender (without context).

For their first approach, they extracted top N queries associated with each listing and then trained embeddings for items and queries. With these embeddings, candidates were generated via approximate nearest neighbours. However, this did not work as well as the second, simpler approach.

![Etsy's first approach to integrating context](/assets/etsy-first-approach.webp "Etsy's first approach to integrating context")

Etsy's first approach to context-based candidate generation.

Here’s their second approach: For each search *query*, a set of items would be shown to the user (i.e., search results)—these are the *target* items. Then, for each target item, other items the user interacted with (in the same search session) become *candidate* items. Thus, for each query-target pair, they would have a set of candidates.

![Etsy's second approach to integrating context](/assets/etsy-second-approach.webp "Etsy's second approach to integrating context")

Etsy's second approach to context-based candidate generation.

Together with a ranker (applied after candidate generation), they improved recall by 12.42% in offline evaluation. In online evaluation, it increased click-through rate by 8 - 23% and conversion rate by 0.25 - 1.16%.

Casper Hansen from the University of Copenhagen shared how Spotify **learns [user preferences based on session history and the current context](https://dl.acm.org/doi/10.1145/3383313.3412248)**. Specifically, by using the sequence of past sessions and the context (at the start of each session), can they predict which tracks will be played in a new session *and context*?

![Distribution of context features for Spotify](/assets/spotify-distribution.webp "Distribution of context features for Spotify")

Users played music in a variety of contexts (time, device).

Music track embeddings (40-dimension vectors) were trained via word2vec. Then, track embeddings were averaged to create three session embeddings (all tracks, played tracks, skipped tracks). Context was represented via categorical variables such as day of week, time of day, device, etc.

They used an RNN-based architecture to jointly learn from historical sequences and context. The key was to *fuse* the context-dependent user embeddings and long-term user embeddings using attention weights.

![Architecture for Spotify CoSeRNN](/assets/spotify-model.webp "Architecture for Spotify CoSeRNN")

Pan Li from New York University shared how Alibaba’s Youku **[introduces freshness and unexpectedness](https://dl.acm.org/doi/10.1145/3383313.3412238) into video recommendations**. He distinguished between two kinds of unexpectedness:

* Personalized: Some users are variety seekers and thus more open to new videos
* Session-based: If a user finishes the first episode of a series, it’s better to recommend the next episode. If the user binged on multiple episodes, it’s better to recommend something different.

Their final utility function combines relevancy (i.e., CTR) and unexpectedness. The proportion of unexpectedness is tuned to ensure that CTR is kept at a certain threshold while introducing unexpectedness.

![Architecture for Youku's video recommender](/assets/youku-model.webp "Architecture for Youku's video recommender")

Two separate models were implemented, one for relevancy and one for unexpectedness.

Results from an A/B test showed an increase in number of videos viewed by each user (3.74%), time spent on platform (4.63%), and CTR (0.80%) while also increasing unexpectedness by 9.74%.

Benjamin Chamberlain from Twitter shared how **it’s a [bad idea to use default parameters](https://dl.acm.org/doi/10.1145/3383313.3418486) for Word2vec-based recommendations**. They quantified the extent of this with experiments on hyperparameter tuning and evaluated on recall@10 and nDCG@10.

Under constrained optimization (i.e., considering limited resources), they got a 138% average improvement in recall (aka hit rate; results below). And by tuning on a 10% data sample, they achieved a 91% average improvement in recall. From these experiments, they increased follow rates from Twitter’s Who To Follow recommender by 15%.

![Results from Twitter's hyperparameter tuning](/assets/twitter-hyperparam-results.webp "Results from Twitter's hyperparameter tuning")

Ehtsham Elahi from Netflix shared **[how to learn representations of recommendation slates](https://dl.acm.org/doi/10.1145/3383313.3418484)**. A slate is a row of recommendations, such as what you would see on the Netflix home screen. In recommendations, we’re often recommending and ranking *slates of items* instead of individual items.

![Recommendation slates on Netflix's home screen](/assets/netflix-home-screen.webp "Recommendation slates on Netflix's home screen")

Recommendation slates on Netflix's home screen.

They demonstrated a way to learn state embeddings by using the distribution of items making up the slate. This is done by summarizing the items in the slates using the mean and covariance matrix of the item embeddings.

By incorporating slate embeddings, they improved on the winning submission for the RecSys 2019 challenge (predicting accommodations clicks in [Trivago](https://www.trivago.com) search results).

Ramanathan R from SBX Corporation shared their approach for **building a [reciprocal recommender system](https://dl.acm.org/doi/10.1145/3383313.3411558) for a matchmaking app**. Recommendations for matchmaking are challenging for the following reasons:

* A successful match requires *both* parties to like each other; in product recommendations, we only need to model one-sided preferences
* Once a match is made, most matched users will stop using the app and thus exclude themselves from the candidate pool
* The dataset is very sparse as users are selective and thus have few interactions
* Too many poor recommendations can lead to high rejection rate and user attrition

![Data available from Tapple's matchmaking app](/assets/tapple.webp "Data available from Tapple's matchmaking app")

Data available from Tapple's matchmaking app.

To learn user embeddings, they used historical match data. If both users liked each other (i.e., match), this was assigned a positive label; if only one user liked (and the other user rejected or ignored), this was assigned a negative label. For new users, pseudo-embeddings were generated based on existing users with similar metadata (e.g., location, interests). These user embeddings were then used in candidate generation.

An interesting challenge was the mismatch between offline and online evaluation. This was due to some recommended users being inactive (e.g., previously matched or stopped using the app). Inactive users did not reciprocate the like, leading to no match/conversion. This was fixed by adding a re-ranking step to have a balance of relevant, new, and active users.

> RecSys2020 (22-26 Sep) gave a peek into recent ideas on recommenders from academia & industry.  
>   
> Some takeaways:  
> • Emphasis on ethics & bias  
> • Offline evaluation is tricky  
> • Dot product > learned similarities  
> • Many examples of real-world recsys  
>   
> More👇 <https://t.co/XAOl8WsU3o>
>
> — Eugene Yan (@eugeneyan) [September 29, 2020](https://twitter.com/eugeneyan/status/1310735542359789568?ref_src=twsrc%5Etfw)

**Thanks** to Yang Xinyi and [Karl Higley](https://twitter.com/karlhigley) for reading drafts of this.

Main conference sessions and papers

### Real-Word Applications

* [Goal-driven Command Recommendations for Analysts](https://dl.acm.org/doi/10.1145/3383313.3412255)
* [SSE-PT: Sequential Recommendation via Personalized Transformer](https://dl.acm.org/doi/10.1145/3383313.3412258)
* [Developing Recommendation System to Provide a Personalized Learning Experience at Chegg](https://dl.acm.org/doi/10.1145/3383313.3411557)
* [Behavior-based Popularity Ranking on Amazon Video](https://dl.acm.org/doi/10.1145/3383313.3411555)
* [A Human Perspective on Algorithmic Similarity](https://dl.acm.org/doi/10.1145/3383313.3411549) ❤️️
* [From the Lab to Production: A Case Study of Session-Based Recommendations in the Home-Improvement Domain](https://dl.acm.org/doi/10.1145/3383313.3412235) ❤️
* [RecSeats: A Hybrid Convolutional Neural Network Choice Model for Seat Recommendations at Reserved Seating Venues](https://dl.acm.org/doi/10.1145/3383313.3412263)
* [In-Store Augmented Reality-enabled Product Comparison and Recommendation](https://dl.acm.org/doi/10.1145/3383313.3412266)
* [Recommending the Video to Watch Next: An Offline and Online Evaluation at YOUTV.de](https://dl.acm.org/doi/10.1145/3383313.3412257)
* [On the Heterogeneous Information Needs in the Job Domain: A Unified Platform for Student Career](https://dl.acm.org/doi/10.1145/3383313.3411554)
* [Balancing Relevance and Discovery to Inspire Customers in the IKEA App](https://dl.acm.org/doi/10.1145/3383313.3411550) ⭐️
* [Learning to Collaborate in Multi-Module Recommendation via Multi-Agent Reinforcement Learning without Communication](https://dl.acm.org/doi/10.1145/3383313.3412233)
* [Exploring Clustering of Bandits for Online Recommendation System](https://dl.acm.org/doi/10.1145/3383313.3412250)
* [Contextual User Browsing Bandits for Large-Scale Online Mobile Recommendation](https://dl.acm.org/doi/10.1145/3383313.3412234)
* [Offline Contextual Multi-armed Bandits for Mobile Health Interventions: A Case Study on Emotion Regulation](https://dl.acm.org/doi/10.1145/3383313.3412244)
* [Building a Reciprocal Recommendation System at Scale from Scratch: Learnings from One of Japan’s Prominent Dating Applications](https://dl.acm.org/doi/10.1145/3383313.3411558) ⭐️

### Evaluating and Explaining Recommendations

* [Ensuring Fairness in Group Recommendations by Rank-Sensitive Balancing of Relevance](https://dl.acm.org/doi/10.1145/3383313.3412232)
* [Keeping Dataset Biases out of the Simulation: A Debiased Simulator for Reinforcement Learning based Recommender Systems](https://dl.acm.org/doi/10.1145/3383313.3412252)
* [On Target Item Sampling in Offline Recommender System Evaluation](https://dl.acm.org/doi/10.1145/3383313.3412259) ⭐️
* [Recommendations as Graph Explorations](https://dl.acm.org/doi/10.1145/3383313.3412269)
* [Making Neural Networks Interpretable with Attribution: Application to Implicit Signals Prediction](https://dl.acm.org/doi/10.1145/3383313.3412253)
* [What does BERT Know about Books, Movies and Music? Probing BERT for Conversational Recommendation](https://dl.acm.org/doi/10.1145/3383313.3412249)

### Fairness, Filter Bubbles, and Ethical Concerns

* [Theoretical Modeling of the Iterative Properties of User Discovery in a Collaborative Filtering Recommender System](https://dl.acm.org/doi/10.1145/3383313.3412260)
* [Deconstructing the Filter Bubble: User Decision-Making and Recommender Systems](https://dl.acm.org/doi/10.1145/3383313.3412246)
* [Global and Local Differential Privacy for Collaborative Bandits](https://dl.acm.org/doi/10.1145/3383313.3412254)
* [Towards Safety and Sustainability: Designing Local Recommendations for Post-pandemic World](https://dl.acm.org/doi/10.1145/3383313.3412251)
* [Revisiting Adversarially Learned Injection Attacks Against Recommender Systems](https://dl.acm.org/doi/10.1145/3383313.3412243)
* [Debiasing Item-to-Item Recommendations with Small Annotated Datasets](https://dl.acm.org/doi/10.1145/3383313.3412265)

### Unbiased Recommendation and Evaluation

* [A Method to Anonymize Business Metrics to Publishing Implicit Feedback Datasets](https://dl.acm.org/doi/10.1145/3383313.3412256)
* [Unbiased Learning for the Causal Effect of Recommendation](https://dl.acm.org/doi/10.1145/3383313.3412261)
* [Doubly Robust Estimator for Ranking Metrics with Post-Click Conversions](https://dl.acm.org/doi/10.1145/3383313.3412262)
* [Unbiased Ad Click Prediction for Position-aware Advertising Systems](https://dl.acm.org/doi/10.1145/3383313.3412241)
* [Are We Evaluating Rigorously? Benchmarking Recommendation for Reproducible Evaluation and Fair Comparison](https://dl.acm.org/doi/10.1145/3383313.3412489) ⭐️
* [Counterfactual Learning for Recommender System](https://dl.acm.org/doi/10.1145/3383313.3411552)

### Understanding and Modeling Preferences

* [TAFA: Two-headed Attention Fused Autoencoder for Context-Aware Recommendations](https://dl.acm.org/doi/10.1145/3383313.3412268)
* [A Ranking Optimization Approach to Latent Linear Critiquing for Conversational Recommender Systems](https://dl.acm.org/doi/10.1145/3383313.3412240)
* [Content-Collaborative Disentanglement Representation Learning for Enhanced Recommendation](https://dl.acm.org/doi/10.1145/3383313.3412239)
* [“Who Doesn’t Like Dinosaurs?” Finding and Eliciting Richer Preferences for Recommendation](https://dl.acm.org/doi/10.1145/3383313.3412267)
* [Neural Collaborative Filtering vs. Matrix Factorization Revisited](https://dl.acm.org/doi/10.1145/3383313.3412488) ⭐️
* [Query as Context for Item-to-Item Recommendation](https://dl.acm.org/doi/10.1145/3383313.3411480) ❤️

### Novel Machine Learning Approaches

* [PURS: Personalized Unexpected Recommender System for Improving User Satisfaction](https://dl.acm.org/doi/10.1145/3383313.3412238) ⭐️
* [Progressive Layered Extraction (PLE): A Novel Multi-Task Learning (MTL) Model for Personalized Recommendations](https://dl.acm.org/doi/10.1145/3383313.3412236)
* [KRED: Knowledge-aware Document Representation for News Recommendations](https://dl.acm.org/doi/10.1145/3383313.3412237)
* [FISSA: Fusing Item Similarity Models with Self-Attention Networks for Sequential Recommendation](https://dl.acm.org/doi/10.1145/3383313.3412247)
* [Investigating Multimodal Features for Video Recommendations at Globoplay](https://dl.acm.org/doi/10.1145/3383313.3411553)
* [The Embeddings that Came in From the Cold: Improving Vectors for New and Rare Products with Content-Based Inference](https://dl.acm.org/doi/10.1145/3383313.3411477) ⭐️
* [Exploiting Performance Estimates for Augmenting Recommendation Ensembles](https://dl.acm.org/doi/10.1145/3383313.3412264) ⭐️
* [Cascading Hybrid Bandits: Online Learning to Rank for Relevance and Diversity](https://dl.acm.org/doi/10.1145/3383313.3412245)
* [MultiRec: A Multi-Relational Approach for Unique Item Recommendation in Auction Systems](https://dl.acm.org/doi/10.1145/3383313.3412242) ⭐️
* [Contextual and Sequential User Embeddings for Large-Scale Music Recommendation](https://dl.acm.org/doi/10.1145/3383313.3412248) ⭐️
* [ImRec: Learning Reciprocal Preferences Using Images](https://dl.acm.org/doi/10.1145/3383313.3411476)

### Expos

* [Netflix: Recent Trends in Personalization at Netflix](https://www.slideshare.net/justinbasilico/recent-trends-in-personalization-at-netflix) ⭐️

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Sep 2020). RecSys 2020: Takeaways and Notable Papers. eugeneyan.com.
> https://eugeneyan.com/writing/recsys2020/.

or

```
@article{yan2020recsys,
  title   = {RecSys 2020: Takeaways and Notable Papers},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2020},
  month   = {Sep},
  url     = {https://eugeneyan.com/writing/recsys2020/}
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
[recsys](/tag/recsys/)
[deeplearning](/tag/deeplearning/)
[production](/tag/production/)
[survey](/tag/survey/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Appreciating the Present](/writing/present/)
[Is Writing as Important as Coding? »](/writing/writing-and-coding/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---