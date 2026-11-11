---
title: 'Beyond vectors: Intelligent hybrid search with LLM agents in Elasticsearch'
company: Elastic
tag: 召回
date: 2025-03-10
url: https://www.elastic.co/search-labs/blog/llm-agents-intelligent-hybrid-search
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Beyond vectors: Intelligent hybrid search with LLM agents in Elasticsearch

Vector search alone does not account for time, space, or intention, limiting its effectiveness. Thankfully, a solution lies in combining Elastic's traditional search features with LLM agents.

March 10, 2025

[Han Xiang Choong](/search-labs/author/han-xiang-choong)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)

Jump to

Share

Today, we'll be making a case for adopting an agentic LLM approach to improving search relevancy and addressing difficult use-cases, and using a Know-Your-Customer (KYC) use-case to demonstrate these benefits.

This is the follow-up article to the Agentic RAG article [previously published on Elasticsearch Labs,](https://www.elastic.co/search-labs/blog/rag-agent-tool-elasticsearch-langchain) which covered the implementation of agents for RAG use-cases, and introduced the necessary background. That implementation has been expanded here and integrated with a streamlit UI, which looks like this:

![Agentic search UI - Hybrid search with LLM agents](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6ae2fe1ec040a7ed/6a17e244b1e11351e479f1ed/eee357b26d08a76d32443226979b09d1c3fb76e7-2552x1268.png)

Intelligent hybrid search UI. Key point of interest is the agent thought/action on the left, which highlights how the agent crafts a more sophisticated query.

The full code is located in this [Github repo.](https://github.com/elastic/elasticsearch-labs/tree/intelligent-hybrid-search/supporting-blog-content/intelligent_hybrid_search_chatapp)

To get started, run the following command to install dependencies:

```
pip install elasticsearch==8.17.1 langchain==0.3.15 streamlit==1.37.1
```

And run the following to spin up the app:

```
streamlit run news_search_agent.py
```

Please refer to the [original blog](https://www.elastic.co/search-labs/blog/rag-agent-tool-elasticsearch-langchain) for more details about the setup and the data.

Let's get to it!

## Introduction

I have an index with 756,880 news articles, taken from the [POLITICS Dataset](https://github.com/launchnlp/POLITICS?tab=readme-ov-file).

I've generated embeddings for all of the text content in those articles, and now I would like to do [Retrieval-Augmented-Generation](https://www.elastic.co/search-labs/blog/retrieval-augmented-generation-rag) with it, as you do. Perhaps following the process documented in [other searchlabs articles](https://www.elastic.co/search-labs/blog/semantic-search-simplified-semantic-text)

Let's ask a query, do a vector search with it, pass the search results to the LLM (in this case, GPT 4o mini hosted on Azure OpenAI), and ask for answer. No bells and whistles, just pure RAG.

Let's think of a query to ask... How about this?

### Query 1:

```
Review Singapore's economic state in 2020
```

Perfect! What answer do we get?

### Answer 1:

`The context provided does not contain specific information about Singapore's economic state in 2020. Therefore, I am unable to provide a review of Singapore's economy for that year based on the given context. If you have more specific information or another document, I would be happy to help with that.`

Huh. That's weird. Let's take a look at the search results...

### Search results 1:

```
Result 1:
Singapore's trade-driven economy shrank for the first time since 2003 
in the fourth quarter as weak manufacturing dragged on growth. 
Momentum is expected to weaken further in 2008.

Result 2:
DUBLIN--(BUSINESS WIRE)--Jan 11, 2019--The “The Payments Landscape 
in Singapore: Opportunities & Risks to 2022” report has been added 
to ResearchAndMarkets.com’s offering. 

Result 3:
World markets retreated Tuesday after the International Monetary 
Fund trimmed its global outlook for 2019 and 2020.
```

It seems that the articles are all from the wrong time period. How unpleasant! Maybe it's a fluke. Let's try a different query.

### Query 2:

```
Investor centric review of magnachip, 2018
```

Is the answer any better?

### Answer 2:

`In 2018, Microchip Technology Inc. (NASDAQ: MCHP) faced significant challenges following its acquisition of Microsemi Corp. for approximately $10.15 billion, which was completed on May 29, 2018. The acquisition was presented as a strategic move that would be "immediately accretive" to Microchip's earnings.`

Okay, so the date is fine, and the subject matter is somewhat relevant. But it's the wrong company, which is perturbing. A quick glance at the results confirms that no search result is related to MagnaChip.

That's weird. What's going on?

## Search has a problem with scale

![Search problem with scale that can be resolved with agentic llm​](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltfe089e5165ce3c07/6a17e246b1e11316cc79f1f1/6f6431f5a842a483eafc73de2b8a3381b40f8107-1926x824.png)

These are both passages from an annual report. Without the labels, could you have told that one was from 2023, and the other from 2024? Probably not. Neither would an LLM, and vectors wouldn't help.

We might venture a few guesses as to why vector search performed poorly. Most prominently, there is no concept of time, and nothing to prevent the retrieval of news articles that are semantically similar but from the wrong time. For example, you may search for a bank's yearly financial report, with several in your index. Each of these reports is likely to share similar content and "voice", making it likely that search results will contain content from all three reports. This intermingled content is basically asking for an LLM hallucination. Less than ideal.

As significant as the temporal aspect is, it is only part of a larger problem.

In this example, we have 756,880 pairs of articles from news websites like Bloomberg, Huffpost, Politico, etc., and generated embeddings for each of them. As the number of articles increases, it becomes likelier and likelier that there will be pairs of documents with overlapping semantic content. This could be common terminology, phrasing, grammatical forms, subject matter etc... Perhaps they reference the same individuals or events over and over. Perhaps they even share similar voice and tone.

And as the quantity of such similar sounding articles increases, the distances between their vectors become less and less reliable as a measure of similarity, and the quality of search degenerates. We can expect this problem to generally worsen as more articles are added.

To summarize: Search quality worsens as data size increases, because irrelevant documents interfere with the retrieval of relevant documents.

Okay. If a preponderance of irrelevant documents is the issue, why don't we just remove them at search time? Bing bong, so simple (Not really, it turns out.)

## Solution: Enhanced data processing

![Data enrichment using llm agents​](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0df311291b99ac7d/6a17e2484b055d4144432128/a78a48262f8c282e9e79f88424ff4cded6a86c70-3566x1608.png)

Enriching data with additional metadata allows us to improve search relevance using filters, ranges, and other traditional search features.

Elasticsearch started life as a fully featured search engine. Date [ranges](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-range-query.html) and filters, [geometric/geospatial search](https://www.elastic.co/guide/en/elasticsearch/reference/current/geospatial-analysis.html), [keyword, term and fuzzy matches with boolean operators](https://www.elastic.co/guide/en/elasticsearch/reference/current/full-text-queries.html), and the ability to finetune search relevance by boosting specific fields. The list of capabilities goes on and on. We can rely on these to refine and finetune search, and we can apply them even with documents that are just text articles.

In the past, we would have had to apply a suite of NLP capabilities to extract entities, categorize text, perform sentiment analysis, and establish relationships between lexical segments. This is a complex task requiring a host of different components, several of which are likely to be specialized deep learning models based on transformer architectures.

Elastic allows you to [upload such models with Eland](https://www.elastic.co/guide/en/elasticsearch/client/eland/current/overview.html) and then make use of their [NLP capabilities within ingest pipelines](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp.html) With LLMs, the task is much simpler.

I can define an LLM inference endpoint like this:

```
PUT _inference/completion/azure_openai_gpt4o_completion
{
    "service": "azureopenai",
    "service_settings": {
        "api_key": "------------",
        "resource_name": "ca-shared",
        "deployment_id": "gpt-4o",
        "api_version": "2024-06-01"
    }
}
```

And then add it to an ingest pipeline, allowing me to extract interesting metadata from my articles. In this case, I'll extract a list of entities, which could be people, organizations, and events. I'll extract geographic locations too, and I'll try to categorize the article. All it requires is prompt engineering where I define a prompt in the document context, and an inference processor where I call the LLM and apply it to the prompt, like so:

```
PUT _ingest/pipeline/bignews_pipeline
{
  "processors": [
    {
      "script": {
        "source": """
    ctx.entities_prompt = 'Instructions: - Extract the top 1 to 20 
    most significant entities from the news story. 
    ...
    Return your answer in this format: Entity1, Entity2,...,nEntity10  
    Example: Jane Doe, TechCorp, Tech Expo 2023  
    If there are less than 20 of such entities, then stop when appropriate. 
    Anywhere from 1 to 20 entities is acceptable.   
    News Story: [News Story] ' + ctx.text
    """
      }
    },
    {
      "inference": {
        "model_id": "azure_openai_gpt4omini_completion",
        "input_output": {
          "input_field": "entities_prompt",
          "output_field": "entities"
        },
        "on_failure": [
          {
            "set": {
              "description": "Index document to 'failed-<index>'",
              "field": "_index",
              "value": "failed-{{{ _index }}}"
            }
          }
        ]
      }
    },
    ...
    {
      "script": {
        "source": """
        ctx.categories_prompt = 'Here is a list of categories: 
        Politics, Business, Technology, Science, Health, ... 
        **Instructions:** - Extract between 1 and 20 
        most important categories from the news story.
         - **Use only the listed categories**. - 
        Return your answer in this format:  Category1 
        Category2 Category3 Category4 Category5  
        **Example:** Technology Business Innovation 
        Economics Marketing  **News Story:** [News Story] ' + ctx.text
    """
      }
    },
    ...
    {
      "script": {
        "source": """
        ctx.geographic_location_prompt = 'Instructions:  
        - Extract geographic locations from the news story:  - 
        For each location, provide:   - The **location name** 
        as precisely as possible (include city, state/province, country, etc.).
          - Return your answer in this format:  London, United Kingdom, 
          Paris, France, Berlin, Germany  **News Story:** [News Story] ' + ctx.text
    """
      }
    },
    ...
```

I can set it running with a reindex like this:

```
POST _reindex?slices=auto&wait_for_completion=false
{
  "conflicts": "proceed", 
  "source": {
    "index": "bignews",
    "size": 24
  },
  "dest": {
    "index": "bignews_enriched",
    "pipeline": "bignews_pipeline",
    "op_type": "create"
  }
}
```

And after a short while, end up with enriched documents, containing useful metadata that can be used to refine and improve my search results. For example:

```
title: "Kane Co. president John Kane on giving - Innovations"
categories: "Philanthropy, Business, Education, Human Interest"
entities: "Tom Heath, John Kane, Kane Co. "
geographic_location: "Maryland, Washington DC, United States"
date: "2011-11-20T00:00:00.000Z"
text: ...
```

Fortunately, this dataset that I'm using comes with timestamps. If it did not, I might try asking the LLM to infer approximate dates based on content. I could further enrich the metadata with coordinates using open-source datasets or apps like [Google's Geocoding API](https://developers.google.com/maps/documentation/geocoding/overview). I could add descriptions to the entities and categories themselves, or I could cross-correlate with other sources of data in my possession, like databases and data terminals. The possibilities are limitless and varied.

![Enriched documents - llm agents​](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt722677fba92ae6d3/6a17e24a414c6427f49450cb/ac7acb45911d7b49a9a30f31192629dab0520abb-3188x1468.png)

Document view and mappings after enrichment.

After chunking and embedding the documents with `semantic_text`, the process of which is [well-documented](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-search-semantic-text.html), the question remains: How do I actually make use of this new metadata?

## Beyond vector search: Complex queries

A standard vector search may look like this. Assuming that I've already chunked and embedded my data with `semantic_text` and [ELSER\_V2](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html), I can make use of a sparse vector query like this:

```
GET bignews_final/_search
{
  "query": {
      "nested": {
        "path": "text.inference.chunks",
        "query": {
          "sparse_vector": {
            "inference_id": "elser_v2",
            "field": "text.inference.chunks.embeddings",
            "query": "what weather event happened 
                       in the caribbean in 2012"
          }
        },
        "inner_hits": {
          "size": 2,
          "name": "bignews_embedded.text",
          "_source": false
        }
      }
    }
  }
```

And that gives me search results with these titles:

```
Hurricane Matthew to Smash into Gitmo by Tuesday Evening (2016 Oct)
AP Fact Check: Clinton on Hurricane Matthew, climate change (2016 Oct)
As Matthew churns toward U.S., more than 1 million ordered 
evacuated in S.C. (2016 Oct)
Tropical Storm Isaias: Americans should start preparing for 'winds, 
heavy rainfall and storm surge,' hurricane center says (2020 Jul)
```

Okay. It's all the wrong dates, and also, the wrong hurricanes (I'm looking for Isaac and Sandy). This vector search isn't good enough, and can be improved by filtering over a date range, and searching over my new metadata fields. Perhaps the query needed actually looks more like this:

```
GET bignews_final/_search
  {
    "query": {
      "bool": {
        "must": [
          {
            "range": {
              "date": {
                "gte": "2012-01-01",
                "lte": "2012-12-31"
              }
            }
          },
          { 
              "match": {
                "categories": "Climate, Weather"
              }
          },
          { 
              "match": {
                "geographic_location": "Caribbean"
              }
          },
          {
            "nested": {
              "path": "text.inference.chunks",
              "query": {
                "sparse_vector": {
                  "inference_id": "elser_v2",
                  "field": "text.inference.chunks.embeddings",
                  "query": "what weather event happened 
                            in the caribbean in 2012"
                }
              },
              "inner_hits": {
                "size": 2,
                "name": "bignews_embedded.text",
                "_source": false
              }
            }
          }
          ]
      }
    }
  }
```

And these are the search results I get:

```
Tropical Storm Isaac poses potential threat (2012 Jul)
A look at Caribbean damage from Hurricane Sandy (2012 Oct)
Green Stories Of 2012: Environmental News In Review (2012 Dec)
```

It's better. Exactly the news reports that were being searched for.

Realistically speaking, how would you generate that more complex query on the fly? The criteria changes based on what exactly the user asks. Maybe some user questions specify dates, while others lack them. Maybe specific entities are mentioned, maybe not. Maybe it is possible to infer details like article categories, or not. A uniform Elastic Query DSL requrest may not work so well, and it may need to adapt dynamically based on requirements and contexts.

There is another blog about generating [Query DSL with LLMs](https://www.elastic.co/search-labs/blog/elastic-query-dsl-structured-datasets). This approach, though effective, always presents the possibility of a misplaced bracket or malformed request. It takes a long time to execute because of the complexity and length of the query DSL, and that detracts from the user experience.

Why don't we use an agent?

## The agentic LLM model

To recap, an agent is an LLM given a degree of decision making capability. Provide a set of tools, define the parameters by which each tool might be used, establish the purpose and scope, and allow the LLM to dynamically select each tool in response to a situation.

A tool can be a knowledge base, or a traditional database, or a calculator, or a webcrawler, whatever. The possibilities are endless. Our goal is to provide an interface where the agent can interact with the tool in a structured manner, and then make use of the tool's outputs.

## Creating complex query DSL with agents (intelligent hybrid search)

![Intelligent hybrid search with LLM agents](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt628b309fd7b30df5/6a17e24cec0f89d0eb5a657e/bc546bc977dbb8ce5cbb399fe2b79c713f3bcb74-3626x1864.png)

Intelligent Hybrid Search in practice - By narrowing down the search space, we are able to more effectively converge on relevant search results and increase the likelihood of a relevant RAG output.

With [Langchain](https://python.langchain.com/docs/introduction/), we can define tools as python functions. Here, I have a function that takes in a few parameters, which the LLM will provide, and then builds an Elasticsearch query and sends it off using the [python client](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/index.html). If each variable exists, it is added to a clause, and then the clause is appended to a list of clauses. These clauses are then assembled into a single Elasticsearch query, with a vector search component, then sent off as part of a search request.

```
def rag_search(query: str, dates: str, categories: str, geographic_location: str, entities: str):
    if es_client is None:
        return "ES client is not initialized."
    else:
        try:
            # Build the Elasticsearch query
            should_clauses = []
            must_clauses = []
            # If dates are provided, parse and include in query
            if dates:
                # Dates must be in format 'YYYY-MM-DD' or 'YYYY-MM-DD to YYYY-MM-DD'
                date_parts = dates.strip().split(' to ')
                if len(date_parts) == 1:
                    # Single date
                    start_date = date_parts[0]
                    end_date = date_parts[0]
                elif len(date_parts) == 2:
                    start_date = date_parts[0]
                    end_date = date_parts[1]
                else:
                    return "Invalid date format. Please use YYYY-MM-DD or YYYY-MM-DD to YYYY-MM-DD."
                date_range = {
                    "range": {
                        "date": {
                            "gte": start_date,
                            "lte": end_date
                        }
                    }
                }
                must_clauses.append(date_range)
            supplementary_query=[]
            if categories: 
                supplementary_query.append(categories)
                lst=[i.strip() for i in categories.split(',')]
                for category in lst:
                    category_selection = { 
                        "match": {
                        "categories": category
                        }
                    }
                    should_clauses.append(category_selection)
            if geographic_location: 
                supplementary_query.append(geographic_location)
                lst=[i.strip() for i in geographic_location.split(',')]
                for location in lst:
                    geographic_location_selection = { 
                        "match": {
                        "geographic_location": location
                        }
                    }
                    should_clauses.append(geographic_location_selection)
            if entities: 
                supplementary_query.append(entities)
                lst=[i.strip() for i in entities.split(',')]
                for entity in lst:
                    entity_selection = { 
                        "match": {
                        "entities": entity
                        }
                    }
                    should_clauses.append(entity_selection)
            # Add the main query clause
            main_query = {
                "nested": {
                    "path": "text.inference.chunks",
                    "query": {
                        "sparse_vector": {
                            "inference_id": "elser_v2",
                            "field": "text.inference.chunks.embeddings",
                            "query": query + ' ' + ', '.join(supplementary_query)
                        }
                    },
                    "inner_hits": {
                        "size": 2,
                        "name": "bignews_final.text",
                        "_source": False
                    }
                }
            }
            must_clauses.append(main_query)
            es_query = {
                "_source": ["text.text", "title", "date"],
                "query": {
                    "bool": {
                        "must":must_clauses,
                        "should":should_clauses
                    }
                },
                "size": 10
            }
            response = es_client.search(index="bignews_final", body=es_query)
            
            ... ... ...
```

The search results are then formatted, concatenated into a block of text, which serves as context for the LLM, and then finally returned.

```
result_docs = []
for hit in hits:
    source = hit["_source"]
    title = source.get("title", "No Title")
    text_content = source.get("text", {}).get("text", "")
    date = source.get("date", "No Date")
    categories = source.get("categories", "No category")
    
    # Create result document
    doc = {
        "title": title,
        "date": date,
        "categories":categories,
        "content": text_content
    }
    
    # Add to session state
    st.session_state.search_results.append(doc)
    
    # Create formatted string for return value
    formatted_doc = f"Title: {title}\nDate: {date}\n\n {text_content}\n"
    result_docs.append(formatted_doc)
return "\n".join(result_docs)
```

The tool / function has a clear purpose; It allows the agent to interact with the Elasticsearch cluster in a well-defined and controlled manner. There is dynamic behavior, because the agent controls the parameters used for the search. There is definition and guardrail, because the broad structure of the query is predefined. No matter what the agent outputs, there will not be a malformed request that breaks the flow, and there will be some degree of consistency.

So when I ask the agent a query like: `Concise summary of developments related to Elastic NV in the second half of the 2010s`, it will choose to use the RAG tool previously defined. It will call the tool with a set of parameters like this:

```
{ 
  "query ":  "Elastic NV developments 2010s ",  
  "dates ":  "2015-07-01 to 2019-12-31 ",  
  "categories ":  "Business, Technology, Finance ",  
  "geographic_location ":  "Global ",  
  "entities ":  "Elastic NV "
}
```

And that will result in a query that looks like this:

```
GET bignews_final/_search
{
  "query ": {
    "bool ": {
      "must ": [
        {
          "range ": {
            "date ": {
              "gte ": "2015-07-01 ",
              "lte ": "2019-12-31 "
            }
          }
        },
        {
          "nested ": {
            "path ": "text.inference.chunks ",
            "query ": {
              "sparse_vector ": {
                "inference_id ": "elser_v2 ",
                "field ": "text.inference.chunks.embeddings ",
                "query ": "Elastic NV developments 2010s Business, Technology, Finance, Global, Elastic NV "
              }
            },
            "inner_hits ": {
              "size ": 2,
              "name ": "bignews_final.text ",
              "_source ": false
            }
          }
        }
      ],
      "should ": [
        {
          "match ": {
            "categories ": "Business "
          }
        },
        {
          "match ": {
            "categories ": "Technology "
          }
        },
        {
          "match ": {
            "categories ": "Finance "
          }
        },
        {
          "match ": {
            "geographic_location ": "Global "
          }
        },
        {
          "match ": {
            "entities ": "Elastic NV "
          }
        }
      ]
    }
  },
  "size ": 10
}
```

With luck, this query will give us better search results, and provide more satisfying answers than vector search alone could provide.

Let's test it out!

## Testing the agentic versus vector search for Know-Your-Customer applications

One of the most impactful use-cases I can think of it Know-Your-Customer (KYC) for financial services and regulatory institutions. This application involves enormous amounts of manual research and number crunching, and is generally difficult for vector search alone to accomplish, due to its focus on specific entities, time periods, and subject matter. I think it is a use-case that is better served with an agentic approach rather than a 'pure' vector search approach.

The dataset is well suited for it, containing millions of news articles scraped from American news media. This is a possible implementation of such a use-case; collecting huge amounts of data into a single index and then searching it on-demand.

Tests are performed with GPT-4o-mini deployed on Azure OpenAI as the LLM and ELSER\_V2 as the embedding model. We ask queries, search our Elasticsearch index with either vector search or agentic search, then compare the answers and search results.

User query and LLM generated answer is shown, along with selected search results. Agent function calls are also shown with the agent's answer.

### Test 1: Singapore economy in review 2020

This is the first query we asked, and it represents is a very broad and open-ended query that traditionally has been difficult for vector-based RAG based systems to handle. Not unless there is an article in the knowledge base on the specific topic. We're hoping to get a range of articles that are at least somewhat relevant, and then string them together into a coherent summary

**Vector search answer:**

The vector search was able to retrieve relevant documents, subject matter wise. However, none of the documents were from the correct time period. Hence, the LLM cannot give an answer.

```
** LLM Answer **
I couldn't find specific articles that provide a comprehensive review 
of Singapore's economy for the year 2020.

** Search Results **  
Singapore cuts 2012 growth forecast, outlook dour (2012 Nov)
Singapore's economy shrinks for first time since 2003 (2008 Mar)
In Singapore, Central Bank Eases Currency Policy (2015 Jan)
```

**Agentic answer:**

The agentic search was able to retrieve relevant documents from the correct time period, then string them together into a coherent answer. That's what we were looking for!

```
** LLM Answer **
In 2020, Singapore's economy faced significant challenges primarily 
due to the impact of the COVID-19 pandemic. 
Here are some key highlights from the year:

Singapore Airlines Rescue Package: In March 2020, Singapore Airlines (SIA) 
secured a massive rescue package of up to $19 billion...

Government Support Measures: The Singapore government announced over S$30 
billion in measures to support businesses and households...

Interest Rate Cuts in the Region: In response to the economic downturn, 
central banks in the region, including the Monetary Authority of Singapore, 
indicated they had room to ease monetary policy...

Economic Contraction: The pandemic led to a significant contraction in 
economic activity. Analysts predicted that the economic growth for the 
region could slow down considerably due to the effects of the virus...

Impact on Tourism and Exports: The tourism sector, a vital part of 
Singapore's economy, was severely affected, with a drastic decline in 
visitor arrivals...

Stock Market Volatility: The stock market experienced fluctuations 
throughout the year, influenced by global economic conditions and 
the ongoing pandemic...

Overall, 2020 was a tumultuous year for Singapore's economy,
marked by unprecedented challenges due to the global pandemic, 
leading to significant government intervention and support measures 
to stabilize the economy.`

** Search Results ** 
Singapore Airlines Obtains $13 Billion Rescue Package Amid Coronavirus Shock (2020 Mar)
Asian Economies Cut Rates, Move to Blunt Impact of Virus (2020 Feb)
Asian shares rise after US stocks set records as fears fade (2020 Jan)

** Agent Function Call ** 
{
  'query': 'Singapore economy review 2020', 
  'dates': '2020-01-01 to 2020-12-31', 
  'categories': 'Economy', 
  'geographic_location': 'Singapore', 
  'entities': ''
}
```

### Test 2: Summarize microsoft strategy in the second half of the last decade

The query has the same open-endedness as the first query, with additional difficulty due to having to infer the correct date range.

**Vector search answer:**

This is a plausible sounding and more detailed answer, with one caveat—most of it is inaccurate. Almost all search results are from the wrong time period, leading to, for example, facts from a 2008 article about cloud computing appearing in an answer that is supposed to be about 2015 - 2020. Upon closer examination, the contents are also generic and lacking detail. The only relevant and useful fact is the appointment of a new Chief Strategy Officer.

```
** LLM Answer **
In the second half of the last decade, Microsoft implemented 
a multifaceted strategy focused on cloud computing, 
organizational restructuring, and adapting to changing market demands.

Cloud Computing Focus: Microsoft significantly shifted its strategy 
towards cloud services, particularly with its Azure platform. This 
included substantial investments in data centers and a commitment to 
transitioning from traditional software sales...

Organizational Restructuring: In 2017, Microsoft announced a major 
restructuring...

Leadership Changes: The appointment of Mark Penn as Chief Strategy 
Officer in 2014 marked a significant shift in Microsoft's executive 
leadership, emphasizing a strategic approach...

Financial Performance: Throughout this period, Microsoft experienced 
strong financial growth, particularly in its cloud services... 

** Search Results **  
Microsoft Moves To Weather Time Of Slow Growth (2003 July)
Microsoft airs strategy for 'cloud computing' (2008 October)
Microsoft reveals permanent work-from-home policy (2020 Mar)
```

**Agentic answer:**

This is a much more satisfying and complete answer, with more detailed specifics. The search results are not only relevant, but from the correct time period. A fact check reveals that each point comes from one of the articles in the search results.

```
** LLM Answer **
n the second half of the last decade, Microsoft underwent a 
significant strategic transformation under CEO Satya Nadella, 
focusing on cloud computing and enterprise services, 
which revitalized the company's market position and financial performance.

Shift to Cloud Computing: Microsoft moved away from its traditional 
reliance on the Windows operating system and personal computer sales, 
which had been declining. By 2019, cloud services accounted for 
nearly a third of Microsoft's total revenue, marking a substantial 
growth area for the company.

Business-Oriented Services: The company emphasized long-term contracts 
with business customers, enhancing its offerings in enterprise software, 
including Office 365 and LinkedIn...

Financial Performance: Microsoft's strategic pivot led to impressive 
financial results. For instance, in July 2019, the company reported 
a quarterly profit of $13.2 billion, driven largely by its cloud business, 
which saw a 19% revenue increase year-over-year... 

Partnerships and Acquisitions: Microsoft sought partnerships with 
other tech companies and made strategic acquisitions to bolster its 
cloud capabilities. For example, it partnered with AT&T to migrate 
infrastructure to its cloud platform...

Philanthropic Initiatives: In addition to its business strategy, 
Microsoft also committed to social responsibility by earmarking 
$1 billion for public cloud projects aimed at non-profits and 
educational institutions...

Sustainability Efforts: Microsoft made significant investments 
in renewable energy, including large wind energy purchases 
to power its data centers, aligning its operations with 
broader environmental goals.

** Search Results ** 
Microsoft cloud growth beats expectations (2019 Jul)
Microsoft surpasses Apple as most valuable public company (2018 Nov)
Microsoft earmarks $1B for public cloud projects (2016 Jan)

** Agent Function Call ** 
{
  'query': 'Microsoft strategy second half of the last decade', 
  'dates': '2015-07-01 to 2019-12-31', 
  'categories': 'Business, Technology, Corporate Strategy', 
  'geographic_location': 'Global', 
  'entities': 'Microsoft'
}
```

### Test 3: Elastic nv investor review 2010-2023

Why not ask about Elastic itself? Let's use a bigger date range too.

**Vector search answer:**

This query yielded exactly two articles of interest about leadership changes. It seems quite limited and probably wouldn't be satisfying for this use case.

```
** LLM Answer **
The search for news articles specifically related to "Elastic NV investor review" 
from 2010 to 2023 yielded limited results. H
owever, here are some relevant articles that mention Elastic NV:

Elastic Announces Transition of Chief Revenue Officer (February 26, 2020)

Elastic N.V. announced that its Chief Revenue Officer, Aaron Katz, 
transitioned to an advisory role. The company is searching for his successor, 
and CEO Shay Banon expressed confidence in the sales leadership team to 
manage the transition without disruption...

Elastic Nominates Alison Gleeson to Board of Directors (November 12, 2019)

Elastic N.V. nominated Alison Gleeson, a former Senior Vice President 
at Cisco, to its Board of Directors. Gleeson’s extensive experience 
in go-to-market strategies is expected to benefit Elastic as it seeks 
to grow and deepen customer relationships. The nomination is subject
 to a shareholder vote.

These articles provide insights into Elastic NV's leadership changes 
and strategic direction, which are relevant for investors 
reviewing the company's performance and governance.

** Search Results ** 
Elastic Announces Transition of Chief Revenue Officer (2020 Feb)
Elastic Nominates Alison Gleeson to Board of Directors (2019 Nov)
```

**Agentic answer:**

This is a more complete answer, bringing in articles about ECS and a success story with the Missouri National Guard. It seems like the agentic approach, with more comprehensive search queries, brings about a qualitative improvement to search relevancy.

```
** LLM Answer **
Here is a summary of notable events and developments related to 
Elastic NV from 2010 to 2023 based on the news articles:

Leadership Changes:

In February 2020, Elastic announced the transition of its Chief Revenue Officer, 
Aaron Katz, to an advisory role, with Shay Banon, the CEO, 
expressing confidence in the leadership team to manage the transition without disruption.

Board of Directors:

In November 2019, Alison Gleeson was nominated to join Elastic's Board of Directors. 
Gleeson, a former Cisco executive, was expected to contribute significantly 
to Elastic's growth strategy.

Partnerships and Innovations:

In January 2019, Elastic partnered with ECS to enhance security and analytics 
capabilities using the Elastic Stack, showcasing its technology's versatility across various sectors.

The Missouri National Guard's cybersecurity team, utilizing Elastic's technology, 
won the 2018 Government Innovation Award for their RockNSM project, which 
improved network security monitoring.

Elastic has maintained a strong commitment to the open-source community, 
which is a core part of its business model, allowing users to leverage 
its technology for various applications.

This summary encapsulates key developments and strategic moves by Elastic NV over the years, 
reflecting its growth trajectory and the challenges it has navigated in the tech landscape.

** Search Results ** 
Elastic Customer, Missouri National Guard Cybersecurity Team, 
Wins 2018 Government Innovation Award for Public Sector Innovation (2018 Nov)
ECS Announces Partnership with Real-Time Search Company Elastic (2019 Jan)
Elastic Announces Transition of Chief Revenue Officer (2020 Feb)
Elastic Nominates Alison Gleeson to Board of Directors (2019 Nov)

** Agent Function Call ** 
{
  'query': 'Elastic NV investor review', 
  'dates': '2010-01-01 to 2023-12-31', 
  'categories': 'Finance, Business, Technology', 
  'geographic_location': 'Global', 
  'entities': 'Elastic NV'
}
```

## Conclusion

From testing, we see that vector search isn't able to account for temporal domains, and doesn't necessarily effectively emphasize crucial components of search queries, which can amplify relevance signals and improve overall search quality. We also see the degenerative impact of scaling, where an increasing amount of semantically-similar articles can result in poor or irrelevant search results. This can cause a non-answer at best, and a factually incorrect answer at worst.

The testing also shows that crafting search queries via an agentic approach can go a long way in improving overall search relevance and quality. It does this by effectively trimming down the search space, reducing noise by reducing the number of candidates in consideration, and it does so by making use of traditional search features that have been available since the earliest days of Elastic.

I think that's really cool!

There are many avenues that can be explored. For example, I would like to try out a use-case that depends on geospatial searches. Use-cases which can make use of a wider variety of metadata to narrow down relevant documents are likely to see the greatest benefits from this paradigm. I think this represents a natural progression from the traditional RAG paradigm, and I'm personally excited to see how far it can be pushed.

Well, that's all I had for today. Until next time!

## Appendix

The full ingestion pipeline used to enrich the data, to run within the Elastic dev tools console.

```
PUT _ingest/pipeline/bignews_pipeline
{
  "processors": [
    {
      "script": {
        "source": """
    ctx.entities_prompt = 'Instructions: - Extract the top 1 to 20 most significant entities from the news story. These can be organizations, people, events - For each entity, provide:   - The entitys name - Do not include geographic locations; they will be handled separately.  - Return your answer in this format: Entity1, Entity2,...,nEntity10  Example: Jane Doe, TechCorp, Tech Expo 2023  If there are less than 20 of such entities, then stop when appropriate. Anywhere from 1 to 20 entities is acceptable.   News Story: [News Story] ' + ctx.text
    """
      }
    },
    {
      "inference": {
        "model_id": "azure_openai_gpt4omini_completion",
        "input_output": {
          "input_field": "entities_prompt",
          "output_field": "entities"
        },
        "on_failure": [
          {
            "set": {
              "description": "Index document to 'failed-<index>'",
              "field": "_index",
              "value": "failed-{{{ _index }}}"
            }
          }
        ]
      }
    },
    {
      "remove": {
        "field": "entities_prompt"
      }
    },
    {
      "script": {
        "source": """
        ctx.categories_prompt = 'Here is a list of categories: Politics, Business, Technology, Science, Health, Sports, Entertainment, World News, Local News, Weather, Education, Environment, Art & Culture, Crime & Law, Opinion & Editorial, Lifestyle, Travel, Food & Cooking, Fashion, Autos & Transportation, Real Estate, Finance, Religion, Social Issues, Obituaries, Agriculture, History, Geopolitics, Economics, Media & Advertising, Philanthropy, Military & Defense, Space & Astronomy, Energy, Infrastructure, Science & Technology, Health & Medicine, Human Interest, Natural Disasters, Climate Change, Books & Literature, Music, Movies & Television, Theater & Performing Arts, Cybersecurity, Legal, Immigration, Gender & Equality, Biotechnology, Sustainability, Animal Welfare, Consumer Electronics, Data & Analytics, Education Policy, Elections, Employment & Labor, Ethics, Family & Parenting, Festivals & Events, Finance & Investing, Food Industry, Gadgets, Gaming, Health Care Industry, Insurance, Internet Culture, Marketing, Mental Health, Mergers & Acquisitions, Natural Resources, Pharmaceuticals, Privacy, Retail, Robotics, Startups, Supply Chain, Telecommunications, Transportation & Logistics, Urban Development, Vaccines, Virtual Reality & Augmented Reality, Wildlife, Workplace, Youth & Children  **Instructions:** - Extract between 1 and 20 most important categories from the news story. - **Use only the listed categories**. - Return your answer in this format:  Category1 Category2 Category3 Category4 Category5  **Example:** Technology Business Innovation Economics Marketing  **News Story:** [News Story] ' + ctx.text
    """
      }
    },
    {
      "inference": {
        "model_id": "azure_openai_gpt4omini_completion",
        "input_output": {
          "input_field": "categories_prompt",
          "output_field": "categories"
        },
        "on_failure": [
          {
            "set": {
              "description": "Index document to 'failed-<index>'",
              "field": "_index",
              "value": "failed-{{{ _index }}}"
            }
          }
        ]
      }
    },
    {
      "remove": {
        "field": "categories_prompt"
      }
    },
    {
      "script": {
        "source": """
        ctx.geographic_location_prompt = 'Instructions:  - Extract geographic locations from the news story:  - For each location, provide:   - The **location name** as precisely as possible (include city, state/province, country, etc.).  - Return your answer in this format:  London, United Kingdom, Paris, France, Berlin, Germany  **News Story:** [News Story] ' + ctx.text
    """
      }
    },
    {
      "inference": {
        "model_id": "azure_openai_gpt4omini_completion",
        "input_output": {
          "input_field": "geographic_location_prompt",
          "output_field": "geographic_location"
        },
        "on_failure": [
          {
            "set": {
              "description": "Index document to 'failed-<index>'",
              "field": "_index",
              "value": "failed-{{{ _index }}}"
            }
          }
        ]
      }
    },
    {
      "remove": {
        "field": "geographic_location_prompt"
      }
    }
  ]
}
```

### Frequently Asked Questions

#### What is an agent?

An agent is an LLM given a degree of decision-making capability.

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