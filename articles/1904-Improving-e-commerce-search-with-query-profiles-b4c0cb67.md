---
title: 'Improving e-commerce search with query profiles in Elastic'
company: Elastic
tag: 查询理解
date: 2025-01-09
url: https://www.elastic.co/search-labs/blog/improving-ecommerce-search-with-query-profiles
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Improving e-commerce search with query profiles in Elastic

This blog demonstrates how to improve e-commerce search using query profiles in Elastic.

January 09, 2025

[Han Xiang Choong](/search-labs/author/han-xiang-choong)

[Vector Database](/search-labs/blog/category/vector-database)[AI](/search-labs/blog/category/ai)

Jump to

Share

Implementing semantic search for the e-commerce use case can be tricky since product formatting is far from standardized. In this blog, we tackle this challenge by using query profiles in Elastic - a method that takes multiple metadata fields and transforms them into a piece of text that resembles a user's preferences and requests. Through a practical example, we demonstrate how query profiles can improve e-commerce search.

## Introduction to e-commerce & Elasticsearch

Elasticsearch is naturally suited for e-commerce data, by which I mean large quantities of product definitions, like this [Amazon product dataset](https://www.kaggle.com/datasets/promptcloud/amazon-product-dataset-2020). Let's download the sample file, with 10,000 products, and upload the CSV to an Elastic index (I'm using my Elastic Cloud Deployment) called amazon\_product\_10k.

![Uploading CSV data on Elastic Cloud](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt9a14b96acfe4331a/6a17db2f7f6f15469fc099dc/d00fbf76e47945fe78c61e2d9725aa10d076764a-1488x813.png)

When we look at the data, we see product descriptions like this one, about a superhero themed bobblehead for a character called Black Lightning:

```
{
  "_index": "amazon_product_10k_plain_embed",
  "_id": "F-Qi2JIBnZufN_5vn-sr",
  "_version": 1,
  "_score": 0,
  "_ignored": [
    "Image.keyword",
    "product_specification.keyword",
    "technical_details.keyword"
  ],
  "_source": {
    "selling_price": "$17.75",
    "Category": "Toys & Games | Collectible Toys | Statues, Bobbleheads & Busts | Statues",
    "shipping_weight": "3.7 pounds",
    "product_specification": "ProductDimensions:3x3x12.4inches|ItemWeight:2pounds|ShippingWeight:3.7pounds(Viewshippingratesandpolicies)|DomesticShipping:ItemcanbeshippedwithinU.S.|InternationalShipping:ThisitemcanbeshippedtoselectcountriesoutsideoftheU.S.LearnMore|ASIN:B077SCH3B2|Itemmodelnumber:DEC170420|Manufacturerrecommendedage:15yearsandup",
    "is_amazon_seller": "Y",
    "id": "b4358a38037a7e7fbcd7fe16970e7bff",
    "model_number": "DEC170420",
    "Image": "https://images-na.ssl-images-amazon.com/images/I/41vJ5amvKeL.jpg|https://images-na.ssl-images-amazon.com/images/I/31tr4qwqZmL.jpg|https://images-na.ssl-images-amazon.com/images/I/31-%2BMGqJASL.jpg|https://images-na.ssl-images-amazon.com/images/I/31sgD4%2B0HlL.jpg|https://images-na.ssl-images-amazon.com/images/I/51HbaURPW8L.jpg|https://images-na.ssl-images-amazon.com/images/G/01/x-locale/common/transparent-pixel.jpg",
    "product_name": "DC Collectibles DCTV: Black Lightning Resin Statue",
    "about_product": "Make sure this fits by entering your model number. | From the upcoming DCTV series on The CW | Limited Edition of 5,000 | Measures approximately 12.42\" tall | Sculpted by Alterton",

    "url": "https://www.amazon.com/DC-Collectibles-DCTV-Lightning-Statue/dp/B077SCH3B2",
    "technical_details": "show up to 2 reviews by default Jefferson Pierce returns to the superhero fold as Black Lightning, the star of The CW's upcoming TV series Black Lightning! Limited edition of 5,000. Measures approximately 12.42\" tall. Sculpted by Alterton. | 3.7 pounds (View shipping rates and policies)"
  },
}
```

A search use-case here involves the user looking for a product, making with a request like:

```
Superhero bobbleheads
```

For enthusiasts of semantic search, there is an immediate problem. The main source of searchable text is the product description, which looks like this:

```
 Make sure this fits by entering your model number. 
 | From the upcoming DCTV series on The CW 
 | Limited Edition of 5,000 
 | Measures approximately 12.42\" tall 
 | Sculpted by Alterton
```

Which tells us nothing about the product. A naive approach might be to choose an embedding model, embed the description and then do semantic search over it. This particular product would never appear for a query like "Superhero bobbleheads", regardless of the choice of embedding. Let's try this and see what happens.

## Naive semantic search

Go ahead and deploy elser\_v2 with this command (Make sure ML node autoscaling is enabled):

```
PUT _inference/sparse_embedding/elser_v2
{
  "service": "elser",
  "service_settings": {
    "num_allocations": 4,
    "num_threads": 8
  }
}
```

And let's define a new index called amazon\_product\_10k\_plain\_embed, define the product description as a semantic\_text type using our elser\_v2 inference endpoint, and run a reindex:

```
PUT amazon_product_10k_plain_embed
{
  "mappings": {
    "properties": {
      "about_product": {
        "type": "semantic_text",
        "inference_id": "elser_v2"
      }

    }
  }
}

POST _reindex?slices=auto&wait_for_completion=false
{
  "conflicts": "proceed", 
  "source": {
    "index": "amazon_product_10k",
    "size": 64
  },
  "dest": {
    "index": "amazon_product_10k_plain_embed"
  }
}
```

And run a semantic search:

```
GET amazon_product_10k_plain_embed/_search
{
  "_source": ["about_product.text", "technical_details", "product_name"], 
  "retriever": {
    "standard": {
      "query": {
        "nested": {
          "path": "about_product.inference.chunks",
          "query": {
            "sparse_vector": {
              "inference_id": "elser_v2",
              "field": "about_product.inference.chunks.embeddings",
              "query": "superhero bobblehead"
            }
          }
        }
      }
    }
  },
  "size": 20
}
```

Behold. The product\_names we get back are pretty bad.

```
1.  Idea Max Peek-A-Pet Bobble Heads Flowers Corgi (Tea Cup)
2. Mezco Toyz Sons Of Anarchy 6" Clay Bobblehead
3. Funko Marvel Captain America Pop Vinyl Figure
```

Corgi is not a superhero despite being a bobblehead. The Sons of Anarchy are not superheroes, they are motorcycle enthusiasts, and a Funko Pop is certainly not a bobblehead. So why are the results so awful?

The required information is actually in the category and technical\_details fields:

```
"Category": "Toys & Games | Collectible Toys | Statues, Bobbleheads & Busts | Statues",
"technical_details": "show up to 2 reviews by default Jefferson 
Pierce returns to the superhero fold as Black Lightning, the 
star of The CW's upcoming TV series Black Lightning! 
Limited edition of 5,000. Measures approximately 12.42\" 
tall. Sculpted by Alterton. | 3.7 pounds 
(View shipping rates and policies)"
```

Second problem, only the category tells us that this product is a bobblehead, and only the technical\_details field tells us that this is superhero related. So the next naive thing to do is embed all three fields, then do a vector search over all three, and hope that the average score will place this product near the top of the results.

Other than the obvious tripling of compute and storage cost, we're also taking a leap of faith that the resulting trio of embeddings will not be noisy, because the product description is very irrelevant, and the category and technical\_details each only contain one word relevant to the search query.

## Naive semantic search even harder

Let's just try it anyway and see what happens. Let's embed the three fields:

```
PUT amazon_product_10k_triple_embed_3
{
  "mappings": {
    "properties": {
      "about_product": {
        "type": "semantic_text",
        "inference_id": "elser_v2"
      },
      "technical_details": {
        "type": "semantic_text",
        "inference_id": "elser_v2"
      },
      "Category": {
        "type": "semantic_text",
        "inference_id": "elser_v2"
      }
      
    }
  }
}
POST _reindex?slices=auto&wait_for_completion=false
{
  "conflicts": "proceed", 
  "source": {
    "index": "amazon_product_10k",
    "size": 64
  },
  "dest": {
    "index": "amazon_product_10k_triple_embed_3"
  }
}
```

And run another search using retrievers with Elastic's built-in [reciprocal rank fusion](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html).

```
GET amazon_product_10k_triple_embed_3/_search
{
  "retriever": {
    "rrf": {
      "retrievers": [
        {
          "standard": {
            "query": {
              "nested": {
                "path": "about_product.inference.chunks",
                "query": {
                  "sparse_vector": {
                    "inference_id": "elser_v2",
                    "field": "about_product.inference.chunks.embeddings",
                    "query": "superhero bobblehead"
                  }
                },
                "inner_hits": {
                  "size": 2,
                  "name": "amazon_product_10k_triple_embed_3.about_product",
                  "_source": [
                    "about_product.inference.chunks.text"
                  ]
                }
              }
            }
          }
        },
        {
          "standard": {
            "query": {
              "nested": {
                "path": "Category.inference.chunks",
                "query": {
                  "sparse_vector": {
                    "inference_id": "elser_v2",
                    "field": "Category.inference.chunks.embeddings",
                    "query": "superhero bobblehead"
                  }
                },
                "inner_hits": {
                  "size": 2,
                  "name": "amazon_product_10k_triple_embed_3.Category",
                  "_source": [
                    "Category.inference.chunks.text"
                  ]
                }
              }
            }
          }
        },
        {
          "standard": {
            "query": {
              "nested": {
                "path": "technical_details.inference.chunks",
                "query": {
                  "sparse_vector": {
                    "inference_id": "elser_v2",
                    "field": "technical_details.inference.chunks.embeddings",
                    "query": "superhero bobblehead"
                  }
                },
                "inner_hits": {
                  "size": 2,
                  "name": "amazon_product_10k_triple_embed_3.technical_details",
                  "_source": [
                    "technical_details.inference.chunks.text"
                  ]
                }
              }
            }
          }
        }
      ]
    }
  }
}
```

Behold, the results are actually worse than before:

```
1. Sunny Days Entertainment Bendems Collectible Posable Figures - Bobs Burgers: Bob
2. Star Wars Childs Boba Fett Costume, Medium
3. DIAMOND SELECT TOYS Batman The Animated Series: Ra's Al Ghul Resin Bust Figure
```

I have a colleague who would probably really enjoy Bob from Bob's Burgers coming out as top result for superhero merchandise @Jeff Vestal.

So what now?

## HyDE

Here's a thought. Let's use an LLM to improve the quality of our data, and make vector search a little bit more effective. [There is a technique called HyDE](https://arxiv.org/abs/2212.10496). The proposal is pretty intuitive. The query contains key content, namely the keywords "Superhero" and "Bobblehead". However, it does not capture the form and structure of the documents we are actually searching over. In other words, search queries do not resemble indexed documents in form, though they may have shared content. So with both keyword and semantic search, we match content to content, but we do not match form to form.

HyDE uses an LLM to transform queries into hypothetical documents, which capture relevance patterns but do not contain actual real content that would answer the query. The hypothetical document is then embedded and used for vector search. In short, we match form with form, as well as content with content.

Let's modify the idea a little bit for e-Commerce.

## Query profiles

What I call query profiles is really about taking multiple metadata fields, and transforming them into a piece of text that resembles a user's preferences and likely requests. This Query Profile is then embedded, and subsequent vector searches are done on it. The LLM is instructed to create a document that mimics what a user might ask for when searching for a product. The flow looks like this:

![Query Profiles are a synthesis of multiple fields into a piece of text that mirrors the likely content of a user's search.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt35738b45ac239e41/6a17db31414c6475e994504c/406ccd4dd5348fdd7f491177baaf1c2b9bc2113f-1488x863.png)

I think that there are two main advantages to this method:

1. Consolidate information from multiple fields into a single document.
2. Capture the likely forms of a user's request, and covering as many bases as possible when doing so.

The resulting text is information rich and might give us better results when searched over. Let's implement it and see what happens.

## Implementing query profiles for e-commerce search

We will define a pipeline in Elasticsearch with an LLM processor. I'm going to make use of GPT-4o mini from my company's Azure OpenAI deployment, so let's define the inference endpoint like so:

```
PUT _inference/completion/azure_openai_gpt4omini_completion
{
    "service": "azureopenai",
    "service_settings": {
        "api_key": <YOUR API KEY>
        "resource_name": <YOUR RESOURCE NAME>,
        "deployment_id": "gpt-4o-mini",
        "api_version": "2024-06-01"
    }
}
```

Now, let's define an ingest pipeline containing the query profile prompt.

```
PUT _ingest/pipeline/amazon_10k_query_profile_pipeline
{
  "processors": [
    {
      "script": {
        "source": """
    ctx.query_profile_prompt = 'Given a {product}, create a detailed query 
    profile written from a customers perspective describing what they are 
    looking for when shopping for this exact item. Include key characteristics 
    like type, features, use cases, quality aspects, materials, and target user. 
    Focus on aspects a shopper would naturally mention in their search query. 
    
    Format: descriptive text without bullet points or sections. 
    
    Example: "Looking for a high-end lightweight carbon fiber road bike for 
    competitive racing with electronic gear shifting and aerodynamic frame 
    design suitable for experienced cyclists who value performance and speed."
    
    Describe this product in natural language that matches how real customers 
    would search for it. 
    
    Here are the product details: 
    \\n Product Name:\\n' + ctx.product_name 
    + '\\nAbout Product:\\n' + ctx.about_product 
    + '\\nCategory:\\n' + ctx.category  
    + '\\nTechnical Details:\\n' + ctx.technical_details
    """
      }
    },
    {
      "inference": {
        "model_id": "azure_openai_gpt4omini_completion",
        "input_output": {
          "input_field": "query_profile_prompt",
          "output_field": "query_profile"
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
        "field": "query_profile_prompt"
      }
    }
  ]
}
```

We'll run a reindex to create the new field with our LLM integration:

```
POST _reindex?slices=auto&wait_for_completion=false
{
  "conflicts": "proceed", 
  "source": {
    "index": "amazon_product_10k",
    "size": 32
  },
  "dest": {
    "index": "amazon_product_10k_w_query_profiles",
    "pipeline": "amazon_10k_query_profile_pipeline",
    "op_type": "create"
  }
}
```

And once it's done, we'll define another index with the query profiles set to semantic\_text, and run embedding with Elser. I like to split up the processing into two stages, so I can hang on to the fruits of LLM's labor separately from the embeddings. Call this insurance against an act of God.

```
PUT amazon_product_10k_query_embed
{
  "mappings": {
    "properties": {
      "query_profile": {
        "type": "semantic_text",
        "inference_id": "elser_v2"
      }
    }
  }
}
```

Let's now run the same query again, this time using semantic search over the query profiles, and see what we get:

```
GET amazon_product_10k_qp_embed/_search
{
  "_source": ["about_product.text", "technical_details.text", "product_name"], 
  "retriever": {
    "standard": {
      "query": {
        "nested": {
          "path": "query_profile.inference.chunks",
          "query": {
            "sparse_vector": {
              "inference_id": "elser_v2",
              "field": "query_profile.inference.chunks.embeddings",
              "query": "superhero bobblehead"
            }
          }
        }
      }
    }
  },
  "size": 20
}
```

The results are quite a bit better, actually.

```
1. FOCO DC Comics Justice League Character Bobble, Superman
2. The Tin Box Company Batman Bobble Head Bank, Black
3. Potato Head MPH Marvel Mashup Hawkeye & Iron Man Toy
```

Okay, result number 3 is a potato head. Fine. But 1 and 2 are actual superhero bobble heads, so I'm going to take this as a win.

## Conclusion

Implementing semantic search for an e-Commerce use-case brings unique challenges. The distributed nature of it means that product formatting is far from standardized. As such, embedding specific fields and trying to do semantic search isn't going to work as well as it does for searching articles or other "full" texts.

By using an LLM to create a Query Profile, we can create a piece of text that merges information from multiple fields and simultaneously captures what a user is likely to search for.

By doing this, we change the e-Commerce search problem so that it resembles a typical knowledge base search, which is a problem statement where semantic search performs quite well.

I think this provides a pathway to bringing traditional search use-cases with structured or tabular data into the Semantic/LLM-era, and that's pretty cool.

### Frequently Asked Questions

#### How to improve e-commerce search?

E-commerce search can be improved by using query profiles in Elastic as they tackle semantic search challenges.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltdfa35fbcbbf4959f/6a1705b9dc55de19a4e00d07/e54132e915217063e9ed0ec45059c6cfc38e31dd-1280x720.png)

[ES|QL](/search-labs/blog/category/esql)[Vector Database](/search-labs/blog/category/vector-database)

### LINQ to Elasticsearch ES|QL: Write C#, query Elasticsearch

April 01, 2026|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt88526af16bafdb7c/6a17d7807f6f15825dc0998d/d11e1ba058784ec92b8953fb8db62e1bad21c210-720x420.jpg)

[Integrations](/search-labs/blog/category/integrations)[Vector Database](/search-labs/blog/category/vector-database)[AI tools](/search-labs/blog/category/ai-tools)

### 4 NVIDIA AI tasks, 1 Elasticsearch API: Embeddings, chat, completion, and rerank

July 21, 2026| [Jan Kazlouski](/search-labs/author/jan-kazlouski)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter