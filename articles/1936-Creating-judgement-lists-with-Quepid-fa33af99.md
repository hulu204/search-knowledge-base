---
title: 'Creating judgement lists with Quepid'
company: Elastic
tag: 评测
date: 2025-05-26
url: https://www.elastic.co/search-labs/blog/quepid-judgement-lists
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Creating judgement lists with Quepid

Learn how to create judgement lists in Quepid using a collaborative human rater process and use the benchmarks to tune your relevance.

May 26, 2025

[Daniel Wrigley](/search-labs/author/daniel-wrigley)

[Relevance](/search-labs/blog/category/relevance)

Jump to

Share

The creation of [judgement lists](https://www.elastic.co/search-labs/blog/judgment-lists) is a crucial step in optimizing search result quality, but it can be a complicated and difficult task. A judgement list is a curated set of search queries paired with relevance ratings for their corresponding results, also known as a test collection. Metrics computed using this list act as a benchmark for measuring how well a search engine performs. To help streamline the process of creating judgement lists, the [OpenSource Connections](https://opensourceconnections.com/) team developed [Quepid](https://quepidapp.com/). Judgement can either be explicit or based on implicit feedback from users. This blog will guide you through setting up a collaborative environment in Quepid to effectively enable human raters to do explicit judgements, which is the foundation of every judgement list.

Quepid supports search teams in the search quality evaluation process:

* Build query sets
* Create judgement lists
* Calculate search quality metrics
* Compare different search algorithms/rankers based on calculated search quality metrics

For our blog, let's assume that we are running a movie rental store and have the goal of improving our search result quality.

## Prerequisites

This blog uses the data and the mappings from the [es-tmdb repository](https://github.com/o19s/es-tmdb). The data is from [The Movie Database](https://www.themoviedb.org/). To follow along, set up an index called tmdb with the mappings and index the data. It doesn’t matter if you set up a local instance or use an Elastic Cloud deployment for this - either works fine. We assume an Elastic Cloud deployment for this blog. You can find information about how to index the data in the [README of the es-tmdb repository](https://github.com/o19s/es-tmdb/blob/master/README.md).

Do a simple match query on the title field for `rocky` to confirm you have data to search in:

```
GET tmdb/_search
{
 "query": {
   "match": {
     "title": "rocky"
   }
 }
}
```

You should see 8 results.

```
{
 "took": 2,
 "timed_out": false,
 "_shards": {
   "total": 1,
   "successful": 1,
   "skipped": 0,
   "failed": 0
 },
 "hits": {
   "total": {
     "value": 8,
     "relation": "eq"
   }
…
}
```

## Log into Quepid

[Quepid](https://github.com/o19s/quepid) is a tool that enables users to measure search result quality and run offline experiments to improve it.

You can use Quepid in two ways: either use the free, publicly available hosted version at <https://app.quepid.com>, or set up Quepid on a machine you have access to. This post assumes you are using the free hosted version. If you want to set up a Quepid instance in your environment, follow the [Installation Guide](https://github.com/o19s/quepid/wiki/Installation-Guide).

Whichever setup you choose, you’ll need to create an account if you don’t already have one.

## How to set up a Quepid case

Quepid is organized around "Cases." A Case stores queries together with relevance tuning settings and how to establish a connection to your search engine.

* For first-time users, select **Create Your First Relevancy Case**.
* Returning users can select **Relevancy Cases** from the top-level menu and click **+ Create a case**.

Name your case descriptively, e.g., "Movie Search Baseline," as we want to start measuring and improving our baseline search.

![Setting up a Quepid case](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte2913d344c42cd24/6a17e6477b54f906b48b38bd/8f9e480d9aae0d706cfc5371e41f19c706dd452a-594x251.png)

Confirm the name by selecting **Continue**.

Next, we establish a connection from Quepid to the search engine. Quepid can connect to a variety of search engines, including Elasticsearch.

The configuration will differ depending on your Elasticsearch and Quepid setup. To connect Quepid to an Elastic Cloud deployment, we need to enable and configure CORS for our Elastic Cloud deployment and have an API key ready. Detailed instructions are in the corresponding [how-to on the Quepid docs](https://quepid-docs.dev.o19s.com/2/quepid/49/how-to-connect-quepid-to-elastic-cloud).

Enter your Elasticsearch endpoint information (`https://YOUR_ES_HOST:PORT/tmdb/_search`) and any additional information necessary to connect (the API key in case of an Elastic Cloud deployment in the **Advanced** configuration options), test the connection by clicking on **ping it** and select **Continue** to move to the next step.

![Setting up an Elasticsearch endpoint with Quepid.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltcc068309bdc094ae/6a17e6480b0bed14cddd356a/267339dfaecae2740eb2ee2739bdc971608bdb5f-588x1169.png)

Now we define which fields we want to see displayed in the case. Select all that help our human raters later assess the relevance of a document for a given query.

Set `title` as the *Title Field*, leave `_id` as the *ID Field*, and add `overview, tagline, cast, vote_average, thumb:poster_path` as *Additional Display Fields*. The last entry displays small thumbnail images for the movies in our results to visually guide us and the human raters.

Confirm the display settings by selecting the **Continue** button.

![Defining which fields we want to see displayed in the case for Quepid human raters.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc910bdf5aa7680b3/6a17e64ae8fbce710b3a1906/02c58aae8c2ebb6d31f538b27462b4c65428fdc3-594x493.png)

The last step is adding search queries to the case. Add the three queries *star wars*, *harrison ford*, and *best action movie* one by one via the input field and **Continue**.

Ideally, a case contains queries that represent real user queries and illustrate different types of queries. For now, we can imagine *star wars* being a query representing all queries for movie titles, *harrison ford* a query representing all queries for cast members, and *best action movie* a query representing all queries that search for movies in a specific genre. This is typically called a query set.

![Adding search queries to a Quepid case](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt46122bb45e1063e4/6a17e64b505ac36510ad8af8/baccfe96766319aa7255e9bff08913ac87d1517f-595x326.png)

In a production scenario, we would sample queries from event tracking data by applying statistical techniques like [Probability-Proportional-to-Size sampling](https://opensourceconnections.com/blog/2022/10/13/how-to-succeed-with-explicit-relevance-evaluation-using-probability-proportional-to-size-sampling/) and import these sampled queries into Quepid to include queries from the head (frequent queries) and tail (infrequent queries) relative to their frequency, which means we bias towards more frequent queries without excluding rare ones.

Finally, select **Finish** and you will be forwarded to the case interface where you see the three defined queries.

## Queries and information needs

To arrive at our overarching goal of a judgement list, human raters will need to judge a search result (typically a document) for a given query. This is called a query/document pair.

Sometimes, it seems easy to know what a user wanted when looking at the query. The intention behind the query `harrison ford` is to find movies starring Harrison Ford, the actor. What about the query `action`? I know I’d be tempted to say the user’s intention is to find movies belonging to the action genre. But which ones? The most recent ones, the most popular ones, the best ones according to user ratings? Or does the user maybe want to find all movies that are called “Action”? [There are at least 12 (!) movies called “Action” in The Movie Database](https://www.themoviedb.org/search/movie?query=Action) and their names mainly differ in the number of exclamation marks in the title.

Two human raters may differ in interpreting a query where the intention is unclear. Enter the Information Need: An [Information Need](https://en.wikipedia.org/wiki/Information_needs) is a conscious or unconscious desire for information. Defining an information need helps human raters judge documents for a query, so they play an important role in the process of building judgement lists. Expert users or subject matter experts are good candidates for specifying information needs. It is good practice to define information needs from the perspective of the user, as it's their need the search results should fulfill.

Information needs for the queries of our “Movies Search Baseline” case:

1. **star wars**: The user wants to find movies or shows from the Star Wars franchise. Potentially relevant are documentaries about Star Wars.
2. **harrison ford**: The user wants to find movies starring the actor Harrison Ford. Potentially relevant are movies where Harrison Ford has a different role, like narrator.
3. **best action movie**: The user wants to find action movies, preferably the ones with high average user votes.

## How to define information needs in Quepid

To define an information need in Quepid, access the case interface:

1. Open a query (for example s*tar wars*) and select *Toggle Notes.*

2. Enter the Information Need in the first field and any additional notes in the second field:

![Defining information and query needs in Quepid.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte57395f64f6e5fab/6a17e64d6864a40fd6b68771/e01d3d5242a350d8797faa665eb3170039f5dfa2-1483x559.png)

3. Click **Save**.

For a handful of queries, this process is fine. However, when you expand your case from three to 100 queries (Quepid cases are often in the range of 50 to 100 queries) you may want to define information needs outside of Quepid (for example, in a spreadsheet) and then upload them via **Import** and select **Information Needs**.

## Create a team in Quepid and share your case

Collaborative judgements enhance the quality of relevance assessments. To set up a team:

1. Navigate to **Teams** in the top-level menu.

![Creating a team in Quepid.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt45c51d1a0e05a80d/6a17e64fe8fbcede793a190f/797706e8d130b474a95d30b6fa22ecaf36f98c03-613x58.png)

2. Click **+ Add New**, enter a team name (for example, "Search Relevance Raters"), and click **Create**.

3. Add members by typing their email addresses and clicking **Add User**.

4. In the case interface, select **Share Case**.

5. Choose the appropriate team and confirm.

## Create a book of judgements in Quepid

A Book in Quepid allows multiple raters to evaluate query/document pairs systematically. To create one:

1. Go to **Judgements** in the case interface and click **+ Create a Book**.

![Creating a book of judgements in Quepid.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3543c00e0b834b3f/6a17e650e9ea87f57fa9c598/6a077f26225961150b7414463d7db04f090b68d6-896x365.png)

2. Configure the book with a descriptive name, assign it to your team, select a scoring method (for example, DCG@10), and set the selection strategy (single or multiple raters). Use the following settings for the Book:

* **Name**: “Movies Search 0-3 Scale”
* **Teams to Share this Book With**: Check the box with the Team you created
* **Scorer**: DCG@10

3. Click **Create Book.**

The name is descriptive and contains information about what is searched in (“Movies”) and also the scale of the judgements (“0-3”). The selected Scorer DCG@10 defines the way the search metric will be calculated. “DCG” is short for [Discounted Cumulative Gain](https://en.wikipedia.org/wiki/Discounted_cumulative_gain) and“@10” is the number of results from the top taken into consideration when the metric is calculated.

In this case, we are using a metric that measures the information gain and combines it with positional weighting. There may be other search metrics that are more suitable for your use case and [choosing the right one is a challenge in itself](https://opensourceconnections.com/blog/2020/02/28/choosing-your-search-relevance-metric).

## Populate the book with query/document pairs

In order to add query/document pairs for relevance assessment, follow these steps:

1. In the case interface, navigate to "Judgements."

![Populate the book with query/document pairs in Quepid.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0e98583138535cc3/6a17e6520b0bed4f51dd3571/d717c5b06ae6cb42ed2b9e771486a12f738a9890-1041x218.png)

2. Select your created book.

3. Click "Populate Book" and confirm by selecting "Refresh Query/Doc Pairs for Book."

This action generates pairs based on the top search results for each query, ready for evaluation by your team.

## Let your team of human raters judge

So far, the completed steps were fairly technical and administrative. Now that this necessary preparation is done, we can let our team of judges do their work. In essence, the judge’s job is to rate the relevance of one particular document for a given query. The result of this process is the judgement list that contains all relevance labels for the judged query document pairs. Next, this process and the interface for it are explained in further detail.

### Overview of the Human Rating interface

![How Quepid human raters interface judge information in documents and queries.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt553afb07d8080421/6a17e654505ac30514ad8afc/be3016091b49655dab3354d84e6dc638f3468390-1283x664.png)

Quepid's Human Rating interface is designed for efficient assessments:

* **Query:** Displays the search term.
* **Information Need:** Shows the user's intent.
* **Scoring Guidelines:** Provides instructions for consistent evaluations.
* **Document Metadata:** Presents relevant details about the document.
* **Rating Buttons:** Allows raters to assign judgements with corresponding keyboard shortcuts.

### Using the Human Rating interface

As a human rater, I access the interface via the book overview:

1. Navigate to the case interface and click **Judgements**.

![Using the Quepid Human Rating interface ](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0e98583138535cc3/6a17e6520b0bed4f51dd3571/d717c5b06ae6cb42ed2b9e771486a12f738a9890-1041x218.png)

2. Click on **More Judgements are Needed!**.

The system will present a query/document pair that has not been rated yet and that requires additional judgements. This is determined by the Book’s selection strategy:

* *Single Rater*: A single judgement per query/doc pair.
* *Multiple Raters*: Up to three judgements per query/doc pair.

### Rating query/doc pairs

Let’s walk through a couple of examples. When you are following this guide, you will most likely be presented with different movies. However, the rating principles stay the same.

Our first example is the movie “Heroes” for the query *harrison ford*:

![How to populate a book in Quepid with query/document pairs.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta248e787b5e0a670/6a17e656ec0f89612d5a65ee/c1e14b0d8b04dd579471932dbe4ff72ae5692a02-981x571.png)

We first look at the query, followed by the information need and then judge the movie based on the metadata given.

This movie is a relevant result for our query, since Harridson Ford is in its cast. We may regard more recent movies as more relevant subjectively but this is not part of our information need. So we rate this document with “Perfect” which is a 3 in our graded scale.

Our next example is the movie “Ford v Ferrari” for the query *harrison ford*:

![An example of the movie “Ford v Ferrari” for the query harrison ford in Quepid.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf5d86aac918a1e96/6a17e657414c64833e945152/052af7894506d7a765af156ba8e26ceec3559973-981x789.png)

Following the same practice, we judge this query/doc by looking at the query, the information need and then how well the document’s metadata matches the information need.

This is a poor result. We probably see this result as one of our query terms, “ford”, matches in the title. But Harrison Ford plays no role in this movie, nor any other role. So we rate this document “Poor” which is a 0 in our graded scale.

Our third example is the movie “Action Jackson” for the query *best action movie*:

![An example of the movie “Action Jackson” for the query best action movie:](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt2cee335ddd1e6a92/6a17e6596df731d1f40a0ed7/247ab862fbc7435537709f8c96619cb331133d09-985x606.png)

This looks like an action movie, so the information need is at least partially met. However, the vote average is 5.4 out of 10. And that makes this movie probably not the best action movie in our collection. This would lead me as a judge to rate this document “Fair,” which is a 1 in our graded scale.

These examples illustrate the process of rating query/doc pairs with Quepid in particular, on a high level and also in general.

## Best practices human raters

The shown examples might make it seem straightforward to get to explicit judgements. But setting up a reliable human rating program is no easy feat. It’s a process filled with challenges that can easily compromise the quality of your data:

* Human raters can become fatigued from repetitive tasks.
* Personal preferences may skew judgements.
* Levels of domain expertise vary from judge to judge.
* Raters often juggle multiple responsibilities.
* The perceived relevance of a document may not match its true relevance to a query.

These factors can result in inconsistent, low-quality judgements. But don’t worry - there are proven best practices that can help you minimize these issues and build a more robust and reliable evaluation process:

* **Consistent Evaluation:** Review the query, information need, and document metadata in order.
* **Refer to Guidelines:** Use scoring guidelines to maintain consistency. Scoring guidelines can contain examples of when to apply which grade which illustrates the process of judging. Having a check in with human raters after the first batch of judgements proved to be a good practice to learn about challenging edge cases and where additional support is needed.
* **Utilize Options:** If uncertain, use "I Will Judge Later" or "I Can’t Tell," providing explanations when necessary.
* **Take Breaks:** Regular breaks help maintain judgement quality. Quepid helps with regular breaks by popping confetti whenever a human rater finishes a batch of judgements.

By following these steps, you establish a structured and collaborative approach to creating judgement lists in Quepid, enhancing the effectiveness of your search relevance optimization efforts.

## Next steps

Where to go from here? Judgement lists are but one foundational step towards improving search result quality. Here are the next steps:

### Calculate metrics and start experimenting

Once judgement lists are available, leveraging the judgements and calculating [search quality metrics](https://opensourceconnections.com/blog/2020/02/28/choosing-your-search-relevance-metric/) is a natural progression. Quepid automatically calculates the configured metric for the current case when judgements are available. Metrics are implemented as “Scorers” and you can provide your own when the supported ones do not include your favorite!

Go to the case interface, navigate to **Select Scorer**, choose *DCG@10* and confirm by clicking on **Select Scorer**. Quepid will now calculate DCG@10 per query and also average overall queries to quantify the search result quality for your case.

![How to quantify search result quality in Quepid. ](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0d059c959b842139/6a17e65be8fbceb29b3a1913/0ff3b9918342071744d681a43d542102e927abd3-1163x551.png)

Now that your search result quality is quantified, you can run first experiments. Experimentation starts with generating hypotheses. Looking at the three queries in the screenshot after doing some rating makes it obvious that the three queries perform very differently in terms of their search quality metric: *star wars* performs pretty well, *harrison ford* looks alright but the greatest potential lies in *best action movie*.

Expanding this query we see its results and can dive into the nitty gritty details and explore why documents matched and what influences their scores:

![Experimenting with different queries to see how they perform for different search metrics in Quepid.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt35227761f4524a1e/6a17e65cb1e11325c579f25a/c45c6cae085a492198c0f8b7060a1a7204e3724e-1131x691.png)

By clicking on “Explain Query” and entering the “Parsing” tab we see that the query is a DisjunctionMaxxQuery searching across three fields: *cast*, *overview* and *title*:

![Explaining query parsing](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0966653b9ab3cc9c/6a17e65efaa913171f93c84c/4a1e1bb2a9cd28e9c48e0ba16357d17ed9d3a5cf-894x557.png)

Typically, as search engineers we know some domain-specifics about our search platform. In this case, we may know that we have a *genres* field. Let’s add that to the query and see if search quality is improved.

We use the **Query Sandbox** that opens when selecting **Tune Relevance** in the case interface. Go ahead and explore this by adding the *genres* field you search in:

```
{
  "query": {
    "multi_match": {
      "query": "#$query##",
      "type": "best_fields",
      "fields": [
        "title^10",
        "overview",
        "cast",
        "genres"
      ]
    }
  }
}
```

Click Rerun My Searches! And view the results. Have they changed? Unfortunately not. We now have a lot of options to explore, basically all query options Elasticsearch offers:

* We could increase the field weight on the genres field.
* We could add a function that boosts documents by their vote average.
* We could create a more complex query that only boosts documents by their vote average if there is a strong genres match.
* …

The best thing about having all these options and exploring them in Quepid is that we have a way of quantifying the effects not only on the one query we try to improve but all queries we have in our case. That prevents us from improving one underperforming query by sacrificing search result quality for others. We can iterate fast and cheap and validate the value of our hypothesis without any risk, making offline experimentation a fundamental capability of all search teams.

### Measure inter-rater reliability

Even with task descriptions, information needs, and a human rater interface like the one Quepid provides, human raters can disagree.

Disagreement per se is no bad thing, quite the contrary: measuring disagreement can surface issues that you may want to tackle. Relevance can be subjective, queries can be ambiguous, and data can be incomplete or incorrect. [Fleiss’ Kappa](https://en.wikipedia.org/wiki/Fleiss%27_kappa) is a statistical measure for the agreement among raters and there is an example notebook in Quepid you can use. To find it, select **Notebooks** in the top-level navigation and select the notebook **Fleiss Kappa.ipynb** in the **examples** folder.

![How to find the Fleiss’ Kappa statistical measure for the agreement among raters notebook in Quepid.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt92d52b30f1fb19c1/6a17e660abe0f2224bdfe9bb/f0669ae96371368ef4d84bb28669560ef09d755c-624x61.png)

## Conclusion

Quepid empowers you to tackle even the most complex search relevance challenges and continues to evolve: [as of version 8 Quepid supports AI-generated judgements](https://github.com/o19s/quepid/blob/main/CHANGELOG.md#800----2024-02-14), which is particularly useful for teams who want to scale their judgement generation process.

Quepid workflows enable you to efficiently create judgement lists that are scalable–which ultimately results in search results that truly meet user needs. With judgement lists established, you have a robust foundation for measuring search relevance, iterating on improvements, and driving better user experiences.

As you move forward, remember that relevancy tuning is an ongoing process. Judgement lists allow you to systematically evaluate your progress, but they are most powerful when paired with experimentation, metric analysis, and iterative improvements.

## Further reading

* Quepid docs:

  + [Relevancy is a Team Sport](https://quepid-docs.dev.o19s.com/2/quepid/32/relevancy-is-a-team-sport)
  + [Quepid for Human Raters](https://quepid-docs.dev.o19s.com/2/quepid/18/quepid-for-human-raters)
  + [How to Connect Quepid to Elastic Cloud](https://quepid-docs.dev.o19s.com/2/quepid/49/how-to-connect-quepid-to-elastic-cloud)
* [Quepid Github repository](https://github.com/o19s/quepid)
* [Meet Pete, a blog series on improving e-commerce search](https://opensourceconnections.com/blog/2020/07/07/meet-pete-the-e-commerce-search-product-manager/)
* [Relevance Slack](https://opensourceconnections.com/slack): join the #quepid channel

**Partner with** [**Open Source Connections**](https://opensourceconnections.com/) to transform your search and AI capabilities and empower your team to continuously evolve them. Our proven track record spans the globe, with clients consistently achieving dramatic improvements in search quality, team capability, and business performance. [Contact us today](https://opensourceconnections.com/contact/) to learn more.

### Frequently Asked Questions

#### What is Quepid?

Quepid is a tool that enables users to measure search result quality and run offline experiments to improve it.

#### What types of search result quality experiments can you create in Quepid?

There are many experiments you can run in Quepid, including building query sets, creating judgement lists, calculating search quality metrics, comparing different search algorithms/rankers based on calculated search quality metrics to improve search relevancy.

#### How to use Quepid and Elasticsearch?

The Query Sandbox allows you to iterate fast and cheaply. You can add field weights, boost scores, or change query logic and immediately see how it impacts your search quality metrics (like nDCG or DCG@10) for your data in Elasticsearch.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt29bbbf4463c73d8a/6a6a33fa55755baeaa2bd248/a6563ee307cc2d29722c490b043ee736c46974f3-1280x720.png)

[Jina AI](/search-labs/blog/category/jina-ai)[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

### 56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker

July 27, 2026|[Felix Wang](/search-labs/author/felix-wang)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3382265814939417/6a170df3a929cf1246ae0a61/fceada10b0c09d6a4a372f137bb3040e1ff41fbf-1600x895.png)

[ES|QL](/search-labs/blog/category/esql)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### Hybrid search and multistage retrieval in ES|QL

January 08, 2026|[Ioana](/search-labs/author/ioana-alina-tagirta)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt021070497c8cbd23/6a170aeab0367d782c72bd0e/c506a0f5c0a33ca6f85454d4f742d7cb266a7b78-715x413.png)

[Relevance](/search-labs/blog/category/relevance)

### ES|QL, you know, for Search - Introducing scoring and semantic search

April 16, 2025|[Ioana](/search-labs/author/ioana-alina-tagirta)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt360319cdeac21a74/6a6119f81b1d49b36a6f1823/8aaf734953fe5ae677062bf06aef7352f186657c-1280x720.png)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### AI shopping agents: Why context comes before the query

July 20, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter