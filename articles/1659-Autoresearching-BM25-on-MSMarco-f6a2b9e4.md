---
title: 'Autoresearching BM25 on MSMarco'
company: softwaredoug
tag: 评测
date: 2026-05-17
url: https://softwaredoug.com/blog/2026/05/17/autoresearching-a-better-msmarco-bm25
account: 
origin: harvest3-202607
---
At [Haystack](http://haystackconf.com) I spoke about autore***search:*** Code generation to optimize search rankers.

Can we use it to improve on BM25?

This article represents my lab notes. My agent starts with a BM25 implementation, proposes changes, and accepts those that improve NDCG. We’ll zero-in on passage retrieval dataset MSMarco.

I won’t claim I’ve found a “better BM25” but I’ve iterated towards a decent tuning regime. All while learning valuable lessons about how validation data can leak.

Let’s walk through what happened.

*(all code can be found in [this notebook](https://github.com/softwaredoug/search-experiments/blob/main/notebooks/codegen/codegen_minimarco.ipynb))*

## The start code

We start with a BM25 implementation. We ask a coding agent to edit until relevance improves.

Our ranking function:

```
def rerank_minimarco(query, fielded_bm25, get_corpus):
    ...
```

As input, we have:

* `query`: The search query. In the case of MSMarco, a question. This function should return the passage that answers the question

We also inject retrieval primitives. The Lego pieces the autoresearcher can build with:

* `fielded_bm25`: Simple BM25 search helper (or, phrase, or and’d).
* `get_corpus` : raw access to the index. The direct stats (term freqs, doc freq, etc.) used to compute whatever BM25 or other lexical scoring we might want

It’s expected this function returns top 10 results, ranked by relevance.

The starting code (found [here](https://github.com/softwaredoug/search-experiments/blob/c772a2e7b6385b0486970f7682b66481bb99cc1c/configs/codegen/codegen_minimarco.yml#L18) tokenizes the query terms using the tokenizer we used to index the passage body:

```
    snowball = corpus["description_snowball"].array
    tokenizer = snowball.tokenizer
    terms = [term for term in tokenizer(query) if term]
```

Further down the starter code implements BM25:

```
    k1 = 0.6
    b = 0.62
    n_docs = len(corpus)
    scores = np.zeros(n_docs)

    for term in terms:
        # term freq array of term in every doc
        term_freqs = snowball.termfreqs(term)

        # doc freq of term
        doc_freq = snowball.docfreq(term)
        if doc_freq == 0:
            continue

        idf = np.log(1.0 + (n_docs - doc_freq + 0.5) / (doc_freq + 0.5))
        denom = term_freqs + k1 * (1.0 - b + b * (doc_lengths / avg_dl))
        scores += idf * (term_freqs * (k1 + 1.0)) / np.where(denom == 0, 1.0, denom)
```

In this code `scores` corresponds to a BM25 score of each document in the corpus. We’re just inefficiently simulating the retrieval under the hood of a lexical search engine. In this case, using the [SearchArray](http://github.com/softwaredoug/searcharray) library to fetch NumPy arrays of termfreqs, doc freq, and compute them with NumPy math.

## The training process

Next we train.

I’ve built my own coding agent, you should too. It’s not that hard. My previous article goes deeper into the [tools I give my agent](https://softwaredoug.com/blog/2025/10/19/agentic-code-generation-to-optimize-a-search-reranker)

Long story short, I don’t use Pi, Claude Code or anything. I talk to OpenAI directly, asking it to submit code patches. Then I programmatically accept/reject if the change improves training + validation data.

I create an agentic loop w/ a [system prompt](https://github.com/softwaredoug/search-experiments/blob/c772a2e7b6385b0486970f7682b66481bb99cc1c/configs/codegen/codegen_minimarco.yml#L62).

I enforce the flow with two primary tools: `try_out_patch` and `apply_patch`. The former to try out ideas without saving them. The other, fully gated, to prevent saving rerankers that violate certain guardrails.

### Evaluating ideas in training sandbox

The agent needs to dork-around to find what works / doesn’t work. That’s exactly what the `try_out_patch` does: measures a change without committing to it.

The agent proposes a change. The tool creates a scratch version of the ranker. It then replays training queries, returning the impact to each training query. As in the diagram below:

![image.png](/assets/media/2026/autoresearching-a-better-msmarco-bm25/image.png)

### Applying the proposed patch

The agent so far has only tinkered. Eventually it wants to save the change.

The agent applies the patch. We need to evaluate the patch more seriously. The most important guardrail: validation data. If a second set of validation queries does not improve, the change will be rejected, rejecting changes overfit to training.

![image.png](/assets/media/2026/autoresearching-a-better-msmarco-bm25/image%201.png)

Eventually the agent finds a change that improves validation. The tool saves the proposed change. Life moves on to new and fun experiments.

![image.png](/assets/media/2026/autoresearching-a-better-msmarco-bm25/image%202.png)

To sum up:

* **Training data:** full visibility - the agent has full access to every query and how its results change
* **Validation data:** the agent has NO visibility into individual queries, only seeing if its change was accepted

### Debugging and more

The agent has a few more tools to help debug and troubleshoot ideas. The agent can:

* Run the current reranker code on a single query with a `run_reranker` tool, returning labeled top N results.
* Use search primitives directly to see how they work (i.e. `fielded_bm25`)
* Revert changes to a prior state.

### Repeating the process

The agent will iterate. Calling tools and eventually arriving at a solution (or two) it likes. It will exit and say “here’s the best I can do” with code saved on disk.

After that, we start a new round. The start code becomes the previous round’s output. The agent proposes edits and changes. We repeat round after round, stopping around 10 or so.

The agent can also grep a directory where the rounds are stored, including reasoning traces of past rounds, to observe what’s worked / not worked.

### Measuring on full MSMarco

You might notice reference to “minimarco” - a smaller sampled MSMarco dataset. That lets the many evals here finish faster than if I used the full MSMarco dataset. Everything I’ve said about training / validation data - that’s happening within the smaller minimarco universe.

My hunch was I’d make progress faster with a smaller dataset. There would be a more constrained set of ways a search query could “mess up” to produce irrelevant results. We wouldn’t exhaust the context just by exploring how one single query could produce different results.

Still, it’s important (as we’ll see) to re-evaluate on the full MSMarco dataset.

## The results

I ran for 8 rounds.

We see a steady increase in Minimarco performance. But a plateauing in MSMarco performance

![image.png](/assets/media/2026/autoresearching-a-better-msmarco-bm25/image%203.png)

![image.png](/assets/media/2026/autoresearching-a-better-msmarco-bm25/image%204.png)

You might see a teeny-tiny improvement on MSMarco towards the end. But really most of the gains occurred in the first round w/ MRR approaching 0.2. What ingenious techniques did the agent employ to get these wins?

You can [inspect the full code here](https://github.com/softwaredoug/search-experiments/tree/main/runs/codegen/minimarco/codegen_minimarco/20260504_033459). To quote ChatGPT’s analysis of the generated code:

> Given a query, it:
>
> 1. Gets the full corpus.
> 2. Tokenizes the query using the tokenizer attached to description\_snowball.
> 3. **(NEW) Optionally removes stop words.**
> 4. Computes a BM25-like score for every document.
> 5. **(NEW) Adds a small phrase/bigram boost.**
> 6. Returns the top k document IDs whose score is positive.

The agent didn’t discover a newer better BM25. It used its extensive, encyclopedic knowledge to do some fairly obvious tuning. I don’t claim any of these results are novel.

For stop words, we accept stop word removal for longer queries (> 3 tokens). Otherwise, we fall back to non-stop word queries.

```
q=[t for t in toks if t not in sw]
toks=q if len(toks)>3 and len(q)>1 and "de" not in q else toks
```

After BM25, the code boosts with a simple 0.8 \* termfreq of each question bigram:

```
s+=sum((.08*a.termfreqs(toks[i:i+2]) 
        for i in range(len(toks)-1)), np.zeros(n))
```

### Why did the solution plateau? Overfit to validation

When you look at the stop words, you notice something funny

```
  sw=set(("what is are was were be as a an the"
          "in to for do doe did can you i me there"
          "where when who why how "
          "which consid achiev mani some word need and"
          "or on with from that call place medicin vacat").split())
```

The two stop words **medicine** and **vacation** listed seem odd. It seems, essentially, on the minimarco sample, it’s useful to ignore these terms.

We overfit to the minimarco sample. That’s a great lesson for running any experiment. Any “gate” you add to a brute force process can leak data into the solution. Here, sneaking funny stop word changes.

That said, the final solutions have some interesting characteristics worth testing

* There’s an extra `+.25*(tf>0)` term after BM25. Add a constant boost when a term occurs in the passage
* A phrase boost on the full query phrase occurring in the document

So not nothing, but not groundbreaking. And I would not assume these insights translate outside MSMarco.

## Still, a useful tuning tool

I don’t want to undersell what happened. After all, most teams care about one dataset. But I think we can improve this training regime. I hope to try out some approaches less prone to overfitting

1. **How do I give the per-query insights without overwhelming context?** - Any relevance engineer can exhaust themselves hunting around individual queries. Relevance tuning can exhaust our limited human contexts :). How do we navigate through trees without losing the forest?
2. **Use the full MSMarco dataset?** - I took a shortcut with a sampled minimarco dataset. That (arguably) helped the agent gain more traction on the problem. But it also likely caused overfitting to this sample. Related to the last question, how do I give the agent the full dataset without getting its context exhausted exploring all the possibilities?

Agents know grep extremely well now. Perhaps the queries, their results, etc. need to be treated similarly to a knowledge base? Perhaps specific subagents could marshall insights / ideas to an orchestrating autoresearch agent to improve results here?

Stay tuned! I’ll share more as I work on this project. Oh and I have a one-day hands-on workshop on [Maven on Autoresearch](http://maven.com/softwaredoug/autoresearch) if that interests you.

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---