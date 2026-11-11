---
title: 'Reconstructing relevance judgments - two scenarios'
company: softwaredoug
tag: 评测
date: 2022-06-20
url: https://softwaredoug.com/blog/2022/06/20/reconstructing-relevance-judgments
account: 
origin: harvest3-202607
---
If you recall from a [previous blog post](https://softwaredoug.com/blog/2022/06/08/deriving-relevance-judgments-from-an-a-b-test) I propose randomly guess relevance labels to simulate likely, correct [relevance judgments](https://softwaredoug.com/blog/2021/02/21/what-is-a-judgment-list) based on the results of an A/B test. In this post, I want to explore the plausibility of this method by looking at two cases - one clear-cut, the other more ambiguous.

The [vmware challenge](https://www.kaggle.com/competitions/vmware-zero-shot-information-retrieval) gives a friendly sandbox to try out ideas. In this challenge, you’re given no labels. Instead, you only get a bunch of test queries, like `what is a hypervisor`. You submit your solution’s top 5 search results for each query. Kaggle then gives you the average [NDCG](https://en.wikipedia.org/wiki/Discounted_cumulative_gain) across each test query in your submission.

I have a range of submissions with their NDCG, like below:

```
ndcgs = {
    'data/noise.csv': 0.00060,
    'data/use_feedback_rrf_turnbull_submission_1653226391886872.csv': 0.16806,
    'data/turnbull_submission_1652544680901428.csv': 0.20911,
    'data/best_compound_form_turnbull_1654044184531847.csv': 0.28790,
    'data/max_passage_rerank_first_remaining_lines_turnbull_1653950500881539.csv': 0.29467,
    'data/pull_out_firstline_turnbull_1653253060074837.csv': 0.29668,
    'data/sum_use_at_50_rerank_turnbull_16538316179778419.csv': 0.29762,
    'data/bm25_raw_text_to_remaining_lines_search_turnbull_16538323991927738.csv': 0.30396,
    'data/with_best_compounds_at_5_only_phrase_search_turnbull_16544332515351.csv': 0.30642,
    'data/rerank_slop_search_remaining_lines_max_snippet_at_5_turnbull_1654439885030507.csv': 0.31574,
    'data/with_best_compounds_at_5_only_phrase_search_turnbull_1654439995765457.csv': 0.31643,
    'data/with_best_compounds_at_50_plus_10_times_use_turnbull_165445182567455.csv': 0.32681,
}
```

Comparing one submission’s results to another, can I guess which individual results were more likely relevant? Assuming if a result shifted up, and the NDCG change was large, then that search result is probably relevant, right?

In my previous blog post I propose an algorithm for doing this: running thousands of simulations. We zero-in on the results that moved up or down. We generate random relevance labels (1=relevant, 0=irrelevant) for each of these results. Then we compute the DCG delta of that simulated change (a label of 1 moving up a lot gives a big, positive DCG delta, for example). If the simulation’s DCG delta matches the observed DCG delta, we consider this simulation plausible. We increment `alpha` every simulation a document was seen as relevant for a query (`beta` for irrelevant). With enough simulations, we hope to converge at plausible relevance labels for any result that shifted. You can deep dive into the [code here if you’re curious.](https://github.com/softwaredoug/vmware/blob/503fa547093e79915434b3ecf994f23dbdd6ea64/vmware/simulate/diff_simulation.py#L146)

Let’s analyze the limits of how effective such a strategy could be.

### The perfect case

Consider for example the [best case scenario below](https://github.com/softwaredoug/vmware/blob/a0132af325de4e4a78a4216501c04f6b95c93b9f/tests/test_simulation.py#L12). Here we have a single query that shifted and a DCG delta corresponding to a single relevant result shifting up in the ranking. There’s simply no other way to explain the observed, positive change in DCG other than the result moved up is relevant.

```
def dcg_weight_at(rank):
    return 1 / (math.log(rank + 1, 2))

@pytest.fixture
def best_case_diff():
    results_before = pd.DataFrame([
        {'QueryId': 1, 'DocumentId': "1234"}, 
        {'QueryId': 1, 'DocumentId': "5678"}  

    ])

    results_after = pd.DataFrame([
        {'QueryId': 1, 'DocumentId': "5678"},
        {'QueryId': 1, 'DocumentId': "1234"}

    ])

    diff = create_results_diff(results_before, results_after)
    actual_dcg_delta = dcg_weight_at(1) - dcg_weight_at(2)
    return diff, actual_dcg_delta
```

(Here actual\_dcg\_delta is the total DCG change over all queries, taken by converting NDCG -> DCG and multiplying by the number of queries observed)

When we run our simulation (from [this test](https://github.com/softwaredoug/vmware/blob/a0132af325de4e4a78a4216501c04f6b95c93b9f/tests/test_simulation.py#L41)):

```
def test_best_case(best_case_diff)
    diff, actual_dcg_delta = best_case_diff
    diff = estimate_relevance(diff, actual_dcg_delta)
```

We should see the result moved up given near perfect relevance:

```
    judgment_1234 = diff[(diff['QueryId'] == 1) & (diff['DocumentId'] == "1234")]
    judgment_5678 = diff[(diff['QueryId'] == 1) & (diff['DocumentId'] == "5678")]
    assert judgment_5678['alpha'].iloc[0] > judgment_1234['alpha'].iloc[0]
    assert judgment_5678['beta'].iloc[0] < judgment_1234['beta'].iloc[0]
    assert judgment_5678['alpha'].iloc[0] - judgment_1234['alpha'].iloc[0] > 0.9,
        "Given the diff is best case, alpha diff should be very high"
    assert judgment_1234['beta'].iloc[0] - judgment_5678['beta'].iloc[0] > 0.9,
        "Given the diff is best case, beta diff should be very high"
```

### An ambiguous case

The more interesting case occurs when DCG corresponds to a single relevant swap, but we see two swaps happen. Only one of these swaps could account for the delta! This [test](https://github.com/softwaredoug/vmware/blob/503fa547093e79915434b3ecf994f23dbdd6ea64/tests/test_simulation.py#L29) demonstrates the case:

```
    results_before = pd.DataFrame([
        {'QueryId': 1, 'DocumentId': "1234"},
        {'QueryId': 1, 'DocumentId': "5678"},
        {'QueryId': 2, 'DocumentId': "1234"},
        {'QueryId': 2, 'DocumentId': "5678"}
    ])

    results_after = pd.DataFrame([
        {'QueryId': 1, 'DocumentId': "5678"}, # SWAPPED UP!
        {'QueryId': 1, 'DocumentId': "1234"},
        {'QueryId': 2, 'DocumentId': "5678"}, # SWAPPED UP!
        {'QueryId': 2, 'DocumentId': "1234"}
    ])

   diff = create_results_diff(results_before, results_after)
   actual_dcg_delta = dcg_weight_at(1) - dcg_weight_at(2)      # ONE SWAP!  
   return diff, actual_dcg_delta
```

This presents an ambiguous case: two queries have results swapped, but the DCG delta only has one relevant result shifting position. Can we reconstruct the relevance labels?

Well running simulation, we do expect either swapped results to be more likely to be relevant. As in [this test](https://github.com/softwaredoug/vmware/blob/main/tests/test_simulation.py#L87) we expect the results moved up to be more relevant than those moved down.

```
       assert judgment_1_5678['alpha'].iloc[0] > judgment_1_5678['beta'].iloc[0] + 0.1,
       "Swapping either query results in the DCG diff, so 5678s should be more relevant"
```

But not overwhelmingly so:

```
   assert judgment_1_5678['alpha'].iloc[0] < 0.8,
       "While most simulations should have this as more relevant, it should have many where it is not the one swapped"
```

In other words, many simulations have query 1’s doc 5678 being swapped up being the difference, but others have it query 2’s doc as the relevant swap. Taken together there’s less certainty and more ambiguity. Only one of these results can be relevant, but we unfortunately are unsure which.

### Thinking through the ambiguity

What does the ambiguity here mean?

In the ambiguous case, only ONE of these documents is relevant, and is labeled as such. However, given the uncertain information in the diff, we label a potentially irrelevant result as a little bit relevant. We can make a couple observations from this:

1. **Some diffs have more information than others**: a handful of results shifted for a large overall DCG change carries more information than many results shifting for a small DCG change. Perhaps we should weigh the resulting alpha and beta based on the amount of information we get?
2. **Combining many diffs could result in more information**: If we see one result shifting up more than others, and we accumulate those (weighted) alpha / betas could we obtain more information about relevance? Can we try every combination of the diffs above to look for changes with more information in them?

I’m continuing to explore ways of combining and weighing based on the amount of information to calibrate my certainty. In the end, while we can mitigate these cases, we can never fully overcome them. Like other sources of relevance evaluation, we can use this as one metric among many to help evaluate whether our solution could be moving in the right direction rather than a ‘ground truth’.

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---