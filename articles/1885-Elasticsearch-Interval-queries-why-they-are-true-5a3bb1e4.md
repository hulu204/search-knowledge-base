---
title: 'Elasticsearch Interval queries: why they are true positional queries & how to transition from Span'
company: Elastic
tag: 召回
date: 2024-11-01
url: https://www.elastic.co/search-labs/blog/interval-vs-span-queries
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsearch Interval queries: why they are true positional queries & how to transition from Span

Explains how Interval queries are true positional queries and how to transition to them from Span queries.

November 01, 2024

[Mayya Sharipova](/search-labs/author/mayya-sharipova)

[Relevance](/search-labs/blog/category/relevance)

Jump to

Share

[Span queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/span-queries.html) have long been a tool for ordered and proximity search. These are especially useful for specific domains, such as legal or patent search. But the relatively new [Interval queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-intervals-query.html) actually fit this job much better. Unlike Span queries, Interval queries are true positional queries that score documents only based on positional proximity (expanded upon below).

Starting from Elasticsearch v8.16, we have brought Interval queries into parity with Span queries. Specifically:

* Interval queries now support "range" and "regexp" rules.
* Interval rules based on multiple terms similar to Span queries can expand up to `indices.query.bool.max_clause_count` terms instead of previous `128` value.

Our future plan is to deprecate Span queries in favor of Intervals queries, which cover the same functional capability but do so in a more user-friendly way.

## Advantages of Interval queries over Span queries

[Interval queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-intervals-query.html) rank documents based on the order and proximity of matching terms. Some advantages of Interval queries:

* True positional queries
* Grounded in academic research, based on the [minimal interval semantics](https://vigna.di.unimi.it/ftp/papers/EfficientLazy.pdf) paper with proven algorithms that scale linearly with the number of positions
* Simpler syntax
* Slightly faster (no need of score calculations based on corpus statistics)
* Ability to use scripts for specialized use cases

Interval queries are true positional queries and only consider positional information while scoring documents (scores are inversely proportional to interval's length). This is unlike Span queries that also consider standard metrics like TF-IDF. Below is an example that illustrates how interval queries can do better ranking.

```
PUT docs
{
  "mappings": {
    "properties": {
      "content": {
        "type": "text"
      }
    }
  }
}

PUT docs/_doc/1
{
  "content" : "She sells beautiful seashells by the seashore, their smooth shapes shining in the sun, catching the light with every curve. The girl’s bright smile is just as inviting, drawing people in as they stop to admire the shells, each one a little piece of the ocean she loves. Her gentle voice, like the sound of the waves, adds to the peaceful charm of the moment."
}

PUT docs/_doc/2
{
  "content" : "She plays; her father sells seashells. "
}
```

We want to find documents where the term "she" is near the term "sells". The desired ranking would return the 1st document followed by the 2nd document, as these terms occur closer to each other in the 1st document than in the second document.

But if we run a Span query, we will get a different ranking: [doc2, doc1], because Span queries in addition to proximity calculations also incorporate corpus stats such as TF and IDF metrics that will distort ranking purely by proximity.

```
GET docs/_search?explain=true
{
  "query": {
    "span_near": {
      "clauses": [
        {
          "span_term": {
            "content": "she"
          }
        },
        {
          "span_term": {
            "content": "sells"
          }
        }
      ],
      "slop": 10,
      "in_order": true
    }
  }
}
```

In contrast, Interval queries calculate scores based on proximity and don't consider corpus stats and length of documents. We will get the desired ranking: [doc1, doc2].

```
GET docs/_search?explain=true
{
  "query": {
    "intervals": {
      "content": {
        "match": {
          "query": "she sells",
          "max_gaps": 10,
          "ordered" : true
        }
      }
    }
  }
}
```

This makes Interval queries an ideal choice for true proximity queries.

Interval queries allow to extract the proximity score as a signal for the overall relevance score. They are optimised to be mixed with other relevance signals like BM25, for instance:

```
GET docs/_search
{
    "query": {
        "bool": {
            "must": {
                "match": {
                    "content": {
                        "query": "she sells",
                        "boost": "{{bm25_boost}}"
                    }
                }
            },
            "should": {
                "intervals": {
                    "content": {
                        "match": {
                            "query": "she sells",
                            "max_gaps": 10
                        },
                        "boost": "{{proximity_boost}}"
                    }
                }
            }
        }
    }
}
```

Note that this could also be applied to rescoring: we can make the first pass with BM25 alone and then add a rescorer with BM25 + Intervals combination.

Note that if we need to model Span queries behaviour in matching and scoring by BM25 and proximity, we can do it by combining interval queries with BM25 queries as must clauses in a boolean query with appropriate boosts set.

## Transition guide

Below we show ways to transition from the following Span queries to the equivalent Interval queries:

* span\_containing
* span\_field\_masking
* span\_first
* span\_multi
* span\_near
* span\_not
* span\_or
* span\_term
* span\_within

```
PUT parks
{
  "mappings": {
    "properties": {
      "park": {
        "type": "text"
      },
      "park_rules": {
        "type": "text"
      }
    }
  }
}

PUT parks/_doc/1
{
  "park" : "Sunny Meadows Park",
  "park_rules" : "Children are encouraged to enjoy our playground equipment, including slides, swings, and climbing structures. Feeding the ducks and fish in the pond is allowed, but only with approved feed available at the park office. Children are not permitted to climb trees or enter the park's fountains and water features. Please do not bring glass containers, sharp objects, or personal sports equipment into the park."
}

PUT parks/_doc/2
{
  "park" : "Greenwood Forest Park",
  "park_rules" : "Children are welcome to explore our nature trails, participate in organized activities, and use the designated picnic areas. Picking flowers, disturbing wildlife, or leaving the designated trails is not allowed. Children must be accompanied by an adult when using the park's grills and fire pits. Please refrain from bringing pets, bicycles, or scooters into the park."
}

PUT parks/_doc/3
{
  "park" : "Happy Haven Playground",
  "park_rules" : "Children can enjoy our sandbox, jungle gym, and seesaws, as well as participate in organized games and activities. Running, shouting, or playing rough games near the playground equipment is not permitted. Children must be supervised by an adult at all times and should use the equipment according to their age and size. Please do not bring food, drinks, or chewing gum into the playground area."
}

PUT parks/_doc/4
{
  "park" : "Lakeside Recreation Park",
  "park_rules" : "Children can enjoy fishing at the lake with an adult, using the sports fields for organized games, and playing in the designated play areas. Swimming, wading, or boating in the lake is strictly prohibited. Children must wear appropriate safety gear when using the sports fields and play equipment. Please do not bring alcohol, tobacco products, or illegal substances into the park."
}

PUT parks/_doc/5
{
  "park" : "Adventure Land Park",
  "park_rules" : "Children are encouraged to use our zip lines, ropes courses, and climbing walls under adult supervision and with proper safety equipment. Running, pushing, or engaging in horseplay near the adventure equipment is not allowed. Children must follow all height, weight, and age restrictions for each activity. Please do not bring personal items, such as cell phones or cameras, onto the adventure equipment."
}
```

## SPAN NEAR

```
GET parks/_search
{
  "query": {
    "span_near": {
      "clauses": [
        {
          "span_term": {
            "park_rules": "prohibited"
          }
        },
        {
          "span_term": {
            "park_rules": "swimming"
          }
        }
      ],
      "slop": 10,
      "in_order": false
    }
  },
  "highlight": {
    "fields": {
      "park_rules": {}
    }
  }
}

GET parks/_search
{
  "query": {
    "intervals": {
      "park_rules": {
        "match": {
          "query": "swimming prohibited",
          "max_gaps": 10,
          "ordered" : false  
        }
      }
    }
  },
  "highlight": {
    "fields": {
      "park_rules": {}
    }
  }
}
```

## SPAN FIRST

```
GET parks/_search
{
  "query": {
    "span_first": {
      "match": {
        "span_term": { "park_rules": "sandbox" }
      },
      "end": 5
    }
  },
  "highlight": {
    "fields": {
      "park_rules": {}
    }
  }
}

GET parks/_search
{
  "query": {
    "intervals" : {
      "park_rules" : {
        "match" : {
          "query" : "sandbox",
          "filter" : {
            "script" : {
              "source" : "interval.end < 5"
            }
          }
        }
      }
    }
  },
  "highlight": {
    "fields": {
      "park_rules": {}
    }
  }
}
```

## SPAN OR

```
GET parks/_search
{
  "query": {
    "span_or" : {
      "clauses" : [
        { "span_term" : { "park_rules" : "prohibited" } },
        { "span_near": {"clauses": [{"span_term": {"park_rules": "not"}}, {"span_term": {"park_rules": "allowed"}}], "in_order": true}},
        { "span_near": {"clauses": [{"span_term": {"park_rules": "not"}}, {"span_term": {"park_rules": "permitted"}}], "in_order": true}}
      ]
    }
  },
  "highlight": {
    "fields": {
      "park_rules": {}
    }
  }
}

GET parks/_search
{
  "query": {
    "intervals" : {
      "park_rules" : {
        "any_of" : {
          "intervals" : [
            { "match" : { "query" : "prohibited"} },
            { "match" : { "query" : "not allowed", "ordered" : true } },
            { "match" : { "query" : "not permitted", "ordered" : true } }
           ]
        }
      }
    }
  },
  "highlight": {
    "fields": {
      "park_rules": {}
    }
  }
}
```

## SPAN CONTAINING

```
GET parks/_search
{
  "query": {
    "span_containing": {
      "little": {
        "span_term": {
          "park_rules": "sports"
        }
      },
      "big": {
        "span_near": {
          "clauses": [
            {
              "span_term": {
                "park_rules": "children"
              }
            },
            {
              "span_term": {
                "park_rules": "park"
              }
            }
          ],
          "slop": 50,
          "in_order": false
        }
      }
    }
  },
  "highlight": {
    "fields": {
      "park_rules": {}
    }
  }
}

GET parks/_search
{
  "query": {
    "intervals": {
      "park_rules": {
        "match": {
          "query": "children park",
          "max_gaps": 50,
          "filter" : {
            "containing" : {
              "match" : {
                "query" : "sports"
              }
            }
          }
        }
      }
    }
  },
  "highlight": {
    "fields": {
      "park_rules": {}
    }
  }
}
```

## SPAN WITHIN

```
GET parks/_search
{
  "query": {
    "span_within": {
      "little": {
        "span_term": {
          "park_rules": "sports"
        }
      },
      "big": {
        "span_near": {
          "clauses": [
            {
              "span_term": {
                "park_rules": "children"
              }
            },
            {
              "span_term": {
                "park_rules": "park"
              }
            }
          ],
          "slop": 50,
          "in_order": false
        }
      }
    }
  },
  "highlight": {
    "fields": {
      "park_rules": {
      }
    }
  }
}

GET parks/_search
{
  "query": {
    "intervals": {
      "park_rules": {
        "match": {
          "query": "sports",
          "filter" : {
            "contained_by" : {
              "match" : {
                "query" : "children park",
                "max_gaps": 50
              }
            }
          }
        }
      }
    }
  },
  "highlight": {
    "fields": {
      "park_rules": {
        "number_of_fragments": 0
      }
    }
  }
}
```

## SPAN NOT

```
GET parks/_search
{
  "query": {
    "span_not": {
      "include": {
        "span_term": { "park_rules": "allowed" }
      },
      "exclude": {
        "span_near": {
          "clauses": [
            { "span_term": { "park_rules": "not" } },
            { "span_term": { "park_rules": "allowed" } }
          ],
          "slop": 0,
          "in_order": true
        }
      }
    }
  },
  "highlight": {
    "fields": {
      "park_rules": {}
    }
  }
}

GET parks/_search
{
  "query": {
    "intervals": {
      "park_rules": {
        "match": {
          "query": "allowed",
          "filter": {
            "not_contained_by": {
              "match": {
                "query": "not allowed",
                "max_gaps": 0,
                "ordered" : true
              }
            }
          }
        }
      }
    }
  },
  "highlight": {
    "fields": {
      "park_rules": {}
    }
  }
}
```

## SPAN\_MULTI

### wildcard

```
GET parks/_search
{
    "query": {
        "span_multi": {
            "match": {
                "wildcard": {
                    "park_rules": {"value": "sand*" }
                }
            }
        }
    }
}

GET parks/_search
{
    "query": {
        "intervals": {
            "park_rules": {
                "wildcard": {
                    "pattern": "sand*"
                }
            }
        }
    }
}
```

### fuzzy

```
GET parks/_search
{
    "query": {
        "span_multi": {
            "match": {
                "fuzzy": {
                    "park_rules": {"value": "sandbo" }
                }
            }
        }
    }
}

GET parks/_search
{
    "query": {
        "intervals": {
            "park_rules": {
                "fuzzy": {
                    "term": "sandbo"
                }
            }
        }
    }
}
```

### prefix

```
GET parks/_search
{
    "query": {
        "span_multi": {
            "match": {
                "prefix": {
                    "park_rules": {"value": "sandbo" }
                }
            }
        }
    }
}

GET parks/_search
{
    "query": {
        "intervals": {
            "park_rules": {
                "prefix": {
                    "prefix": "sandbo"
                }
            }
        }
    }
}
```

### regexp

```
GET parks/_search
{
    "query": {
        "span_multi": {
            "match": {
                "regexp": {
                    "park_rules": {"value": "sand.*" }
                }
            }
        }
    }
}

GET parks/_search
{
    "query": {
        "intervals": {
            "park_rules": {
                "regexp": {
                    "pattern": "sand.*"
                }
            }
        }
    }
}
```

### range

```
GET parks/_search
{
    "query": {
        "span_multi": {
            "match": {
                "range": {
                    "park": {
                        "gte" : "a",
                        "lte": "h"
                    }
                }
            }
        }
    }
}

GET parks/_search
{
    "query": {
        "intervals": {
            "park": {
                "range": {
                    "gte" : "a",
                    "lte" : "h"
                }
            }
        }
    }
}
```

## span\_field\_masking

use `use_field` of Intervals

```
GET parks/_search
{
  "query": {
    "span_near": {
      "clauses": [
        {
          "span_term": {
            "park_rules": "nature"
          }
        },
        {
          "span_field_masking": {
            "query": {
              "span_term": {
                "park_rules.stemmed": "trail"
              }
            },
            "field": "park_rules" 
          }
        }
      ],
      "slop": 5
    }
  }
}

GET parks/_search
{
  "query": {
    "intervals" : {
      "park_rules" : {
        "all_of" : {
          "ordered" : true,
          "max_gaps" : 5, 
          "intervals" : [
            {
              "match" : {
                "query" : "nature"
              }
            },
            {
              "match" : {
                "query" : "trail",
                "use_field" : "park_rules.stemmed"
              }
            }
          ]
        }
      }
    }
  }
}
```

## Conclusion

Interval queries is a powerful tool to do true positional search. Try them with expanded functionalities from 8.16 release.

### Frequently Asked Questions

#### What are interval queries in Elasticsearch?

Elasticsearch interval queries are true positional queries that score documents only based on positional proximity.

#### What are the advantages of interval queries?

They are true positional queries, have a simpler syntax, are slightly faster (no need for score calculations based on corpus statistics) and provide the ability to use scripts for specialized use cases.

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