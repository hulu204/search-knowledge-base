---
title: 'How we rebuilt autocomplete for ES|QL'
company: Elastic
tag: 工程相关
date: 2025-05-22
url: https://www.elastic.co/search-labs/blog/esql-autocomplete-rebuilt
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# How we rebuilt autocomplete for ES|QL

Discover how we rearchitected an autocomplete engine for ES|QL to support language evolution instead of resisting it.

May 22, 2025

[Drew Tate](/search-labs/author/drew-tate)

[Inside Elastic](/search-labs/blog/category/inside-elastic)[ES|QL](/search-labs/blog/category/esql)

Jump to

Share

It’s easy for us developers to take good autocomplete for granted. It just works—until you try building it yourself.

This post is about a recent rearchitecture we performed to support continued evolution in ES|QL.

## A little about ES|QL

In case you haven’t heard, ES|QL is Elastic’s new query language. It is super powerful and we see it as the future of how AI agents, applications, and humans will talk to Elastic. So, we provide an ES|QL editing experience in several places in Kibana including the Discover and Dashboard applications.

![ES|QL in Discover](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb0645e9ac6213dd3/6a17db6c1d1b83477d93e356/b0da440495a6f7fa71b9f5defefe32817c7d3e91-1600x490.png)

ES|QL in Discover

To understand the rearchitecture, it’s key to understand a few language components.

An ES|QL query consists of a series of *commands* chained together to perform a pipeline of operations.

Here, we are joining the data from one index to another index:

```
FROM firewall_logs-* METADATA _index
  | LOOKUP JOIN threat_list ON source.IP
  | SORT _index
```

In the example above, `FROM`, `LOOKUP JOIN`, and `SORT` are the commands.

Commands can have major subcomponents (call them subcommands), generally identified by a second keyword before the next pipe character (for example, `METADATA` in the example above). Like commands, subcommands have their own semantic rules governing what comes after the keyword.

ES|QL also has *functions* which look like you’d expect. See `AVG` in the example below:

```
FROM logs-* | STATS AVG(bytes) BY agent.name
```

Autocomplete is an important feature for enabling users to learn ES|QL.

## Autocomplete 1.0

Our autocomplete engine was originally built with a few defining characteristics.

* **Declarative** — Used static declarations to describe commands
* **Generic** — Relied heavily on generic logic meant to apply to most/all language contexts
* **Reified subcommands** — Treated subcommands as first-class abstractions with their own logic

Within the top-level suggestion routine, our code analyzed the query, detecting the general area of the user’s cursor. It then branched into one of several subroutines, corresponding to language subcomponents.

![ESQL autocomplete engine characteristics.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt4c1a9e09a91fa69c/6a17db6e3e03d722d04f2b39/804fd1033fb8b927ce84e813d2b5a4da8e137529-1600x1300.png)

The semantics of both commands and subcommands were described declaratively using a “command signature.” This defined a pattern of things that could be used after the command name. It might say “accept any number of boolean expressions,” or “accept a string field and then a numeric literal.”

If the first analysis identified the cursor as being within a command or subcommand, the corresponding branch would then try to match the (sub)command signature with the query and figure out what to suggest in a generic way.

## The cracks start to show

At first, this architecture worked. Early on, commands in ES|QL were relatively uniform. They looked basically like:

```
COMMAND arg[, arg] SUB_COMMAND arg[, arg]
```

But, as time went on, they started to get more bespoke.

A couple of issues showed up and grew with every new command.

* **Code complexity**—the autocomplete code became large, complicated, and difficult to follow. It wasn’t clear which parts of the logic applied to which commands.
* **Lack of orthogonality**—a change in the behavior in one area of the language often had side-effects in other parts of the language. For example, adding a comma suggestion to the field list in `KEEP`, accidentally created a comma suggestion after the field in `DISSECT` — which is invalid.

The problem was that new syntax and behaviors led our “generic” code to need more and more command-specific branches, and our command definitions to need more and more “generic” settings (that really only applied to a single command).

Gradually, the idea that we could describe the nuances of each command’s structure and behavior with a declarative interface started to look a bit idealistic.

## Timing the investment

When is it time to invest in a refactor? The answer is very contextual. You have to weigh the upsides against the cost. Truth be told, you can generally keep paying the price of inefficiencies for quite awhile— and it can make sense.

One way to stave off a refactor is by treating the symptoms. We did this for months. We treated our code complexity with verbose comments. We treated our lack of orthogonality with better test coverage and careful manual testing.

But there comes a point where the cost of patching outweighs the cost of change. Ours came with the introduction of a fabulous new ES|QL feature, filtering by aggregation.

The `WHERE` command has existed since the early days, but this new feature added the ability to use `WHERE` as a *sub*command in `STATS`.

```
... | STATS COUNT(*) WHERE <expression>
```

This may look like a small change, but it broke the architecture’s careful delineation between commands and subcommands. Now, we had a command that could also be a subcommand.

With this fundamental abstraction break added to all the existing inefficiencies, we decided it was time to invest.

## Autocomplete 2.0

ES|QL isn’t a generic language, it is a query language. So we decided it was time to accept that commands are bespoke by design (in accordance with grand query language tradition).

The new architecture needed to be flexible and adaptive and it needed to be clear what code belonged to which command. This meant a system that was:

* **Imperative** — Instead of declaring what was acceptable after the command name and separately interpreting the declaration, we write the logic to check the correctness of the command directly.
* **Command-specific** — Each command gets its own logic. There is no generic routine that is supposed to work for all the commands.

![esql autocomplete 2.0](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt65bcac5eb4c1f15d/6a17db6f6df73186210a0dc3/9fa5755a6075cf7efe2a588ce4fc02821b68fab2-970x1600.png)

In Autocomplete 1.0, the up-front triage did a lot of work. Now, it just decides whether or not the cursor is already within a command. If within a command, it delegates straight to the command-specific `suggest` method. The bulk of the work now happens within the command’s logic, which is given complete control over suggestions within that command.

This doesn’t mean that commands don’t share logic. They often delegate suggestion creation and even some triage steps to reusable subroutines (for example, if the cursor is within an ES|QL function). But, they retain the flexibility to customize the behavior in any way.

Giving each command its own suggestion method improves isolation and reduces side effects, while making it obvious what code applies to which command.

## It’s still about the user

There is no question that this refactor has resulted in a better developer experience. Everyone who interacted with both systems can attest that this is a breath of fresh air. But, at the end of the day, we made this investment in service of our users.

First of all, some ES|QL features couldn’t be reasonably supported without it. Our users expect quality suggestions when they are writing ES|QL. Now, we can deliver in more contexts.

The old system made it easy to introduce regressions. Now, we expect fewer of these.

One of our team’s biggest roles is adding support for upcoming commands. Now, we can do this much faster.

The work isn’t over, but we’ve created a system that supports change instead of resisting it. With this investment, we’ve laid a solid foundation to keep the language and the editor evolving into the future, side by side.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1092d0334a5b571c/6a572545f71286c608af57e4/3e67c4eeaa3d9411e97ee8b2ae74078a8177a911-2048x1143.avif)

[Operations](/search-labs/blog/category/operations)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Your compliance posture just got an upgrade: Elasticsearch now supports FIPS 140-3

July 07, 2026|[Fabio Busatto](/search-labs/author/fabio-busatto)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt975c900958571074/6a17d7c0abe0f277e2dfe85d/fd800d12d1c12abf68ccb7e8dd80ad7b62bec38c-1440x840.png)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### GenAI for customer support — Part 4: Tuning RAG search for relevance

August 22, 2024|[Antonio Schönmann](/search-labs/author/antonio-schonmann)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbeb5dbab80ffb03d/6a17d7104202290f4229f449/7fce63922298d2a0fcc8a5f292db74d2e0fae0a1-720x420.jpg)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Elastic Support Hub starts using semantic search

November 16, 2023|[Chris Blaisure](/search-labs/author/chris-blaisure)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt27b746cc1995e6b7/6a170efda29299de8ad010c6/e6d3186f609dd56dc5ffe33d70fa9e5cfa05b51f-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Adaptive early termination for HNSW in Elasticsearch

March 02, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltd17ed30cb6a59275/6a46944fde977731a4ca54b5/e7a1b50ef019d1b5a12d49c7457d63a026e1edd0-727x496.png)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### How we doubled vector search throughput on Elasticsearch Serverless

May 28, 2026|[Chris Hegarty](/search-labs/author/chris-hegarty)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter