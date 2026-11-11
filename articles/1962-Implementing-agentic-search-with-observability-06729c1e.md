---
title: ' Implementing agentic search with observability to autotune relevance in Elasticsearch'
company: Elastic
tag: 搜索相关性
date: 2025-11-19
url: https://www.elastic.co/search-labs/blog/agentic-search-relevance-autotuning-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Implementing agentic search with observability to autotune relevance in Elasticsearch

Learn how to implement agentic search in Elasticsearch to automatically train a relevance model from logged user data.

November 19, 2025

[Craig Angulo](/search-labs/author/craig-angulo)[James Williams](/search-labs/author/james-williams)

[Agentic AI](/search-labs/blog/category/agentic-ai)

Jump to

Share

Every search bar is a broken promise. Users type natural language queries, "beachfront paradise in Hawaii with a chef's kitchen" but get back irrelevant results from lexical search. We've solved this with Agentic search and relevance autotuning: a reference architecture that combines natural language understanding with self-improving search that learns from every user interaction. No data scientists needed. No manual tuning. Just search that gets smarter automatically. In this post, I'll show you exactly how to build it.

Who does this help:

* **Insurance companies**: Customers find the right coverage without understanding policy jargon
* **SaaS companies**: Developers find documentation using natural language
* **E-commerce**: Buyers discover products using conversational queries
* **Any business with search**: Turn your search bar from a cost center into a competitive advantage

## Objective

In this blog, we walk through the steps you will need to take to enable an agentic search solution leveraging any LLM you want and the Elastic platform. This search solution will automatically train a Learn-to-Rank model based on user interactions. We will be leveraging a dataset of properties to make a `home-search-agent` that allows users to ask natural language queries “Show me houses for sale in Hawaii that have 3 bedrooms, a pool, and cost under 1 million” and have rich search results returned to them.

## Architecture overview

![Agentic search architecture overview](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt8568f4711b86e555/6a17f45e0b0bed7f50dd36d5/3d4e92f5ac68e7e44f72cf331bf6dfbe95ec650b-1600x725.png)

1. **User asks naturally** → "Show me houses for sale in Hawaii that have 3 bedrooms"
2. **Agent understands** → Translates to optimized Elasticsearch query
3. **Results delivered** → Relevant results, no keyword gymnastics
4. **System learns** → Every interaction teaches the model what users actually want

## Learn-to-Rank (LTR) implementation

The most difficult part of training Learn-to-Rank algorithms is creating judgment lists; this is now handled automatically with Elastic Logging. As searches are run with your home-search-agent those searches, the results, and follow-up questions get logged for training.

* 48 features are looked at in this example, ranging from property attributes (pool, number of rooms) to engagement signals (click-through rate, follow-up questions)
* Once enough conversations have been logged, an XGBoost-based reranking model will be trained on the data and deployed back to Elasticsearch.
* The feedback loop: search → log events → train model → d→ improved search

## Setup and deployment

A detailed step-by-step is provided in the [Github readme section](https://github.com/jwilliams-elastic/agentic-search-o11y-autotune), along with a technical deep dive

1. Ensure you have Node.js, Git, and Python >=3.10, <3.13
2. Clone the provided code repository:<https://github.com/jwilliams-elastic/agentic-search-o11y-autotune>
3. Set up a virtual environment with the requirements.txt provided
4. Create an Elastic Serverless project and copy down the following:

   1. ELASTIC\_URL
   2. ELASTIC\_API\_KEY
5. Create an .env file and provide the credentials from Step 4 (Additionally, you will provide your LLM’s API\_KEY)
6. Open a Terminal in your virtual environment and run `npm run dev`. This will spin up your Mastra server and provide you with a URL like [http://localhost:4111/](http://localhost:4111/workflows)

## What was deployed and how it is used

* Multiple search templates were created during the deployment workflow
* Each one of these search templates provides different configurations from V1-V4
* The home-search-agent has a prompt provided that allows the LLM to fill in search templates
* The LLM is able to convert natural language queries and fill in search templates via an ElasticSearch tool the agent can access

![Tool arguments.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt166e556165f718a6/6a17f45f505ac371b9ad8c90/c0a78ce82c320697a1616e94d290447af281cae3-1080x450.png)

## Demo workflow

1. Open <http://localhost:4111/workflows>
2. Run `elastic-setup-workflow (.env` file has default values, but you can override in Mastra UI)
3. Run `search-autotune-workflow` (LOW and HIGH option generates different simulated search engagement behavior - HIGH = Luxury, LOW = Affordable)
4. Open <http://localhost:4111/agents> and run the "Home Search Agent"
5. Show the difference b/t LTR and no-LTR LLM judgment with a query like "affordable home", "luxury home" and "6 bed, 6 bath single family home near orlando fl with garage and pool under 5M with designer finishes throughout"
6. You can trigger engagement by asking for more detail for a specific result (ex: tell me more about result #20 in v4 results)
7. Open the "Agentic Search Analytics" dashboard - KPIs like CTR, Average Click Position and search template usage.

## Agents in Action

With your Elastic Agents running on the Mastra Framework, you now can choose between the `home-search-agent`, which allows you to run property searches, and the `home-search-agent-ltr-comparison,` which allows you to see the direct benefits of training on personalized data.

### The home-search-agent

![Creating a home search agent](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte650850f91374076/6a17f4616864a44954b688fa/a10e3466d36b135de3c388217ac5b9da17e5ff6b-1600x1016.png)

The home-search-agent-ltr-comparison

![Home search-agent ltr model comparison](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt40cfe4569a45194f/6a17f463fbc5f88054491c09/f03dce0c7fe436618c7175874b7dc30897ecd788-1600x1202.png)

## Why Now?

As users increasingly expect ChatGPT-like search experiences, traditional search engines lose customers to poor relevance and complicated manual tuning. This architecture democratizes access by enabling non-technical users to find what they need without crafting complex queries, while LTR models continuously adapt to individual behavior patterns to increase relevance. Automated retraining keeps results current as trends evolve, and the built-in observability dashboard reveals usage patterns and gaps in your offerings. These insights directly inform feature development and keep you aligned with actual user needs rather than assumptions. Ready to transform your search engine's relevance? Contact us at [elastic.co/contact](http://elastic.co/contact) to find out how your search can begin working for you.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt097721c03648a84e/6a6a33ef0a222b4c70877f32/8f6b95800c65fe389d3e8d8281e8e8dc351f734d-992x342.png)

[ES|QL](/search-labs/blog/category/esql)[ML Research](/search-labs/blog/category/ml-research)[Agentic AI](/search-labs/blog/category/agentic-ai)

### How Elasticsearch detects multiple change points in time series with 0.99 recall

July 24, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blte3979255ddfc7f45/6a17e25ffaa913812f93c7cb/92c517a2e7b36122a18feee317a0215981b62b6b-720x420.jpg)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Operations](/search-labs/blog/category/operations)

### Your agents have been keeping receipts: turning Elastic Agent Builder's built-in OTel traces into token cost dashboards in Kibana

July 28, 2026|[Meghan Murphy](/search-labs/author/meghan-murphy)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltda47d75430c4fa7c/6a17f5cae3179149242d5963/d5d04bbcfc3925f48f3487ea4c7e0dd2205316d0-720x420.jpg)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Integrations](/search-labs/blog/category/integrations)

### One prompt, a complete workflow: Elastic's AI agent writes your automation for you

July 28, 2026|[Tinsae Erkailo](/search-labs/author/tinsae-erkailo)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt360319cdeac21a74/6a6119f81b1d49b36a6f1823/8aaf734953fe5ae677062bf06aef7352f186657c-1280x720.png)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### AI shopping agents: Why context comes before the query

July 20, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3bad6b045392e641/6a170f43a29299c189d010cc/80907fd072e72d6ec902470b449c9f337957a0d7-1280x720.png)

[Agentic AI](/search-labs/blog/category/agentic-ai)

### Managing agentic memory with Elasticsearch

January 16, 2026|[Someshwaran Mohankumar](/search-labs/author/someshwaran-mohankumar)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter