---
title: 'Rated Ranking Evaluator: Help the poor (Search Engineer)'
company: Sease
tag: 评测
date: 2018-07-10
url: https://sease.io/2018/07/rated-ranking-evaluator.html
account: 
origin: harvest3-202607
---
A Software Engineer is always required to give his customers concrete evidence about deliverables quality. A Search Engineer deals with a specialisation of such generic Software Quality, which is called **Search Quality**.

What is Search Quality? And why is it so important in a search infrastructure? After all, the “Software Quality” should be omni-comprehensive, it should always include everything (and it is), but when we are dealing with search systems, the quality is a very abstract term, which is very hard to define in advance.

The functional correctness of a search infrastructure (assuming the correctness is the only factor which influences the system quality – and it isn’t) is naturally associated with human judgments, with opinions, and unfortunately, we know opinions can be different among people.

The business stakeholders, which will get value from a search system, can belong to different categories, can have different expectations, and can have in mind a different idea about the expected system correctness.

In this scenario a Search Engineer is facing many challenges in terms of choices, and at the end, he has to **provide concrete evidence about the functional coverage of those choices**.

This is the context where we developed the Rated Ranking Evaluator (hereafter **RRE**).

## What it Rated Ranking Evaluator?

The Rated Ranking Evaluator (RRE) [[1]](https://github.com/SeaseLtd/rated-ranking-evaluator) is a search quality evaluation tool which evaluates the quality of results coming from a search infrastructure.

It helps a Search Engineer in his daily job. Are you a Search Engineer? Are you tuning/implementing/changing/configuring a search infrastructure? Do you want to have something that gives you evidence about the improvements between changes? RRE could give you a hand on that.

RRE formalises how well a search system satisfies the user information needs, at the “technical” level, combining a rich tree-like domain model with several evaluation measures, but also at the “functional” level, providing human-readable outputs that could target the business stakeholders.

It encourages an incremental/iterative/immutable approach during the development and the evolution of a search system: assuming we’re starting our system from version x.y: when it’s time to apply some relevant change to its configuration, instead of applying changes to x.y, is better to clone it and apply those changes to the new fresh version.

In this way, RRE will execute the evaluation process on all available versions, it will provide the delta/trend between subsequent versions, so you can immediately get a fine-grained picture of where the system is going, in terms of relevance.

This post is only a summary of RRE. You can find more detailed information in the project Wiki [[2]](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki).

## What can I get from RRE?

You can configure RRE as a compounding part of your project build cycle. That means, every time a build is triggered, an evaluation process will be executed.

RRE is not tied to a given search platform: it provides a mini-framework [[3]](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki/Search%20Platform%20Framework) for plugging in different search platforms. At the moment we have two available bindings: Apache Solr and Elasticsearch [[4]](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki/Supported%20Versions).

The output evaluation data will be available:

* + as a **JSON file**: for further elaborations
  + as a **spreadsheet**: for delivering the evaluation results to someone else (e.g. a business stakeholder)
  + in a **Web Console** [[5]](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki/RRE%20Server) where metrics and their values get refreshed in real-time (after each build)

![](https://i0.wp.com/sease.io/wp-content/uploads/2018/07/42096917-edefdd50-7bb6-11e8-9d1a-21356b453192.png?fit=800%2C357&ssl=1)

## How does RRE work?

RRE provides a rich, composite, tree-like, domain model [[6]](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki/Domain%20Model), where the evaluation concept can be seen at different levels.

![RRE Domain Model](https://i0.wp.com/sease.io/wp-content/uploads/2018/07/42093124-8e89a2a2-7bab-11e8-8f7c-8c4c917b91f2.png?fit=800%2C582&ssl=1)

The **Evaluation** at the top level is just a container of the nested entities. Note that all entity relationships are **1 to many**. In this context, a **Corpus** is defined as a test dataset. RRE will use it for executing the evaluation process; in a single evaluation process, you can have multiple datasets.

A **Topic** is an information need: it defines a functional requirement from the end-user perspective. Within a topic, we can have several queries, which express the same need but close to a technical layer. RRE provides a further abstraction in the middle: query groups. A **Query Group** is a group of queries which are supposed to produce the same results (and therefore are associated with the same judgments set).

Queries, which are the technical leaves of the RRE domain model, are further decomposed in several perspectives, one for each available version of our system. A query itself is of course a single entity, but during an evaluation session, its concrete execution happens several times, one for each available version. That is because RRE needs to measure the search results (i.e. the query executions) against all versions.

For each version, we will finally have one or more metrics, depending on the configuration. Last but not least, even if metrics are computed at the query/version level, RRE will aggregate those values at upper levels (see the dashed vertical lines in the diagram) so each entity/level in the domain model will offer an aggregate perspective of all available metrics (i.e I could be interested in the NDCG for a given query, or I could just stop my analysis at a topic level).

## Input

To execute an evaluation process, RRE needs the following things:

* + One or more **corpus/test collection** [[7]](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki/What%20We%20Need%20To%20Provide#corpus): these are the representative datasets of a specific domain, that will be used for populating and querying a target search platform
  + One or more **configuration sets** [[8]](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki/What%20We%20Need%20To%20Provide#configuration-sets): although there’s nothing against having one single configuration, a minimum of two versions are required to provide a comparison between evaluation measures.
  + One or more **ratings sets** [[9]](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki/What%20We%20Need%20To%20Provide#ratings): this is where judgments are defined, in terms of relevant documents for each query group.

## Output

The RRE concrete output depends on the runtime container where it is running. The RRE core itself is just a library, so when used programmatically within a project, it outputs a set of objects corresponding to the domain model described above.

When it is used as a Maven plugin, it primarily outputs the same structure in JSON format [[10]](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki/The%20Evaluation%20Output). This data is then used for producing further outputs, like a spreadsheet. The same payload can be sent to another module called RRE Server, which offers an AngularJS-based web console that gets automatically refreshed.

The RRE console is very useful when we are doing internal iterations / tries around some issue, which usually requires very short *edit-and-immediately-check* cycles. Imagine if you can have a couple of monitors on your desk: on the first, there’s your favourite IDE, where you change things, and run builds. In the second there’s the RRE Console (see below). After each build, just have a look at the console to get immediate feedback on your changes.

![](https://i0.wp.com/sease.io/wp-content/uploads/2018/07/rre-spreadsheet.png?fit=800%2C170&ssl=1)

![](https://i0.wp.com/sease.io/wp-content/uploads/2018/07/42096917-edefdd50-7bb6-11e8-9d1a-21356b453192.png?fit=800%2C357&ssl=1)

## Where can I start?

The project repository [[1]](https://github.com/SeaseLtd/rated-ranking-evaluator) in GitHub offers all that you need: detailed documentation about how it works and how to quickly start with RRE.

If you need some help, feel free to contact us! We appreciate any feedback, suggestions and, last but not least, contribution.

## Future works

As you can imagine, the topic is quite huge. We have a lot of interesting ideas about platform evolution.

These are some examples:

* + integration with some tool for building the relevance judgments. That could be some UI or a more sophisticated user interaction collector [[11]](https://www.slideshare.net/AndreaGazzarini/search-quality-evaluation-a-developer-perspective/30) (which will automatically generate the rating sets on top of computed online metrics like click through rate, and sales rate)
  + Jenkins plugin [[12]](https://www.slideshare.net/AndreaGazzarini/search-quality-evaluation-a-developer-perspective/31): for better integration of RRE into the popular CI tool
  + Gradle plugin
  + Apache Solr Rank Eval API [[13]](https://www.slideshare.net/AndreaGazzarini/search-quality-evaluation-a-developer-perspective/32): using the RRE core we could implement a Rank Eval endpoint in Solr, similar to the Rank Eval API [[14]](https://www.elastic.co/guide/en/elasticsearch/reference/6.3/search-rank-eval.html) provided in Elasticsearch
  + ??? Other? Any suggestion is warmly welcome

Some of these ideas are finally live! Check out the [Rated Ranking Evaluator Enterprise](https://sease.io/rated-ranking-evaluator-enterprise).

## Need Help With This Topic?​​

If you’re struggling with RRE, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with RRE, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)