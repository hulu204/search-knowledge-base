---
title: 'Automating traditional search with LLMs & Elastic Query DSL'
company: Elastic
tag: 查询理解
date: 2024-09-30
url: https://www.elastic.co/search-labs/blog/elastic-query-dsl-structured-datasets
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Automating traditional search with LLMs & Elastic Query DSL

Learn how to use LLMs to write Elastic Query DSL and query structured data with filters.

September 30, 2024

[Han Xiang Choong](/search-labs/author/han-xiang-choong)

[Query DSL](/search-labs/blog/category/query-dsl)[AI](/search-labs/blog/category/ai)

Jump to

Share

This short article is about uploading structured data to an Elastic index, then converting a plain English query into a query DSL statement, to search for specific criteria with specific filters and ranges. The full code is located in this [Github repo](https://github.com/elastic/elasticsearch-labs/tree/automating-traditional-search/supporting-blog-content/automating-traditional-search).

To get started, run the following command to install dependencies (Elasticsearch and OpenAI):

```
pip install elasticsearch==8.14.0 openai==1.35.13
```

You will need an Elastic Cloud deployment and an Azure OpenAI deployment to follow along with this notebook. For more details, refer to [this readme](https://github.com/elastic/elasticsearch-labs/blob/automating-traditional-search/supporting-blog-content/automating-traditional-search/readme_service_setup.md).

If these are available to you, fill in the [`env.example`](https://github.com/elastic/elasticsearch-labs/blob/automating-traditional-search/supporting-blog-content/automating-traditional-search/env.example) as below and rename it to `.env`:

```
ELASTIC_ENDPOINT=<YOUR ELASTIC ENDPOINT>
ELASTIC_API_KEY=<YOUR ELASTIC API KEY>
ELASTIC_INDEX_NAME=<YOUR ELASTIC INDEX NAME>

AZURE_OPENAI_KEY_1=<AZURE OPEN AI API KEY>
AZURE_OPENAI_KEY_2=<AZURE OPEN AI API KEY>
AZURE_OPENAI_REGION=<AZURE OPEN AI API REGION>
AZURE_OPENAI_ENDPOINT=<AZURE OPEN AI API ENDPOINT>
```

Finally, open the [main.ipynb notebook](https://github.com/elastic/elasticsearch-labs/blob/automating-traditional-search/supporting-blog-content/automating-traditional-search/main.ipynb), and execute each cell in order. Beware that the code will upload about 200,000 datapoints to your chosen Elastic index, which should come to about 400MB.

![Flow: Using LLMs to write Elastic Query DSL & search structured data](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt9372e308e42d6d10/6a17ddf2e9ea872085a9c4b9/bb9a47ca0ae16af91404c419bd2c45516add2959-2366x952.png)

The flow explored in this article

## Problem statement: Structured data limitation in RAG

RAG and Hybrid Search are all the RAGe these days. The prospect of uploading unstructured documents to an index and then querying it, with machine learning present at every step of the process, turns out to be a versatile idea with an enormous number of use-cases.

Now, an enormous number is not infinite. Versatile as RAG is, there are occasions where RAG is either overkill or simply poorly suited to the data. One such example is structured datasets containing datapoints like this one here:

```
{
  'address': {'block': '827',
             'postal_code': '705858',
             'street': 'Commonwealth Avenue',
             'street No.': '756',
             'town': 'Sengkang',
             'unit': '#15-042'},
 'age': 65,
 'blood_type': 'A+',
 'citizenship': 'Singapore PR',
 'country_of_birth': 'Slovakia',
 'cpf_number': 'S8613060M',
 'date_of_birth': '1958-10-05',
 'deceased': False,
 'drivers_license_number': 'S4707782F',
 'education': {'highest_qualification': 'N-Levels',
               'institution': 'Local Polytechnic'},
 'email': 'mjq2n4xlpb@outlook.com',
 'emergency_contact': {'name': 'Deng An Sheng',
                       'phone_number': '+65 8163 9924',
                       'relationship': 'Sibling'},
 'gender': 'Male',
 'height_cm': 166,
 'immigration_status': None,
 'languages': {'spoken': {'Afrikaans': 'Basic', 'Xhosa': 'Native'},
               'written': {'Bengali': 'Native'}},
 'marital_status': 'Married',
 'name': 'Wong Jiu Zhan',
 'national_service': {'rank': 'Captain', 'status': 'NSman'},
 'nric': 'S77385949H',
 'occupation': 'Sociologist',
 'passport_number': 'K8013743A',
 'phone_number': '+65 9395 8462',
 'race': 'Others',
 'religion': 'Taoism',
 'weight_kg': 92
 }
```

To me, it doesn't make much sense to do vector-based RAG with structured data like this. To go about it, you'd probably need to try embedding the field values, but this has a couple of issues.

First off, not all of those individual fields are equal. Depending on use-case, certain fields would be of greater interest and thus should be weighted more highly (blood\_type, age, weight, and deceased, perhaps if you are in the medical field?). Weighting the fields is possible if you embed every field, then do a weighted sum. This would multiply the compute cost of embeddings by however many field you have - In this case about 37x. If you don't do this, then the relevant fields are buried under irrelevant ones and performance will likely be poor. Bad choice.

Second, even if you did embed each field in each datapoint, what exactly are you querying with? A plain English question like "Adult men over the age of 25"? Vectors can't filter for specific criteria like this - They work purely based on statistical correlation, which is hardly explicit. I'd bet money on these queries giving poor results, if at all.

## Sample data

The data we're using doesn't include the profiles of real people. I wrote a data generator to generate fake Singaporeans. It's a series of random choice statements, where each choice picks from a large list of options for occupation, country\_of\_birth, addresses, etc... There are a few functions generating convincing looking passport, phone, and NRIC numbers. Now this fake data generator isn't particularly interesting in and of itself, so I'll refrain from discussing it here. The generator itself is located on the relevant notebook - Feel free to check it out! I generated 352,500 profiles for this test.

![The generated dataset in Elastic Cloud](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte06b0ce734bc7475/6a17ddf3e31791e29e2d570e/68351b75434a6e282e8021788fc02649403deb21-1440x824.jpg)

The generated dataset in Elastic Cloud

## Solution: Using LLMs to write Elastic Query DSL & search structured data

Traditional search is a more efficient choice, with its explicit filters and ranges. Elastic is a fully-featured search engine, with plenty of search capabilities that go way beyond just vectors. This is an aspect of search that is recently overshadowed by discussions around RAG and vectors. I think this represents a missed opportunity for serious gains in relevance (Search engine performance), because of the potential for filtering out large portions of irrelevant data (Which can spawn statistical noise, worsening your results) long before costly vector search comes into play.

However, delivery and form factor are significant hurdles. End-users might not be expected to learn database query languages like SQL or even Elastic Query DSL, especially if they are non-technical to begin with. Ideally, we want to preserve the idea of users querying your data using plain old natural language. Give users the ability to search your database without fiddling with filters or frantically googling how to write a SQL or QDSL query.

The solution to this in the pre-LLM era might have been to write a number of buttons and tag them to specific components of a query. Then you could build a complex query by selecting a list of options. This has the caveat of eventually ballooning into a terribly ugly UI filled with masses of buttons. Wouldn't it be nicer if you just had a chat box to search with?

Yeap, we're going to write a natural language query, pass it to an LLM, generate an Elastic query, and use that to search our data.

## Prompt design

This is a straightforward notion, where the only challenge to solve is prompt writing. We should write a prompt with a few key characteristics:

#### 1. Document schema

It contains the data schema, so the LLM knows which fields are valid and can be queried, and which cannot. Like this:

```
The document schema for the profiles is as follows:

{
  "nric": "string",
  "name": "string",
  "race": "string",
  "gender": "string",
  "date_of_birth": "date",
  "age": "integer",
  "country_of_birth": "string",
  "citizenship": "string",
  "religion": "string" ["Buddhism", "Christianity", "Islam", "Hinduism", "Taoism", "No Religion"],
  "marital_status": "string" ["Single", "Married", "Divorced", "Separated", "Widowed", "Civil Partnership", "Domestic Partnership", "Engaged", "Annulled"],
  "address": {
    "block": "string",
    "street_no": "string",
    "street": "string",
    "unit": "string",
    "town": "string",
    "postal_code": "string"
  },
  "phone_number": "string",
  "email": "string",
  "occupation": "string",
  "cpf_number": "string",
  "education": {
    "highest_qualification": "string",
    "institution": "string"
  },
  "languages": {
    "spoken": {"language":"fluency" ["Basic", "Conversational", "Fluent", "Native"]},
    "written": {"language":"fluency" ["Basic", "Conversational", "Fluent", "Native"]},
  },
  "height_cm": "integer",
  "weight_kg": "integer",
  "blood_type": "string" ["A+", "A-", "B+", "B-", "O+", "O-", "ABß", "AB-"],
  "passport_number": "string",
  "drivers_license_number": "string",
  "national_service": {
    "status": "string",
    "rank": "string"
  },
  "immigration_status": "string",
  "emergency_contact": {
    "name": "string",
    "relationship": "string",
    "phone_number": "string"
  },
  "deceased": "boolean",
  "date_of_death": "date"
}
```

Note that for certain fields like `blood_type` and `religion` and `fluency`, I explictly define valid values to ensure consistency. For other fields such as languages or streetnames, the number of available options is excessive and will cause the prompt to balloon. The best option is to trust the LLM in such cases.

#### 2. Examples

It contains example queries and guidelines, which helps reduce the odds of a nonsense query that doesn't work.

```
Example query:
User: Find all male Singapore citizens between 25 and 30 years old who work as software developers and speak fluent English.

Your response should be:

{
  "query": {
    "bool": {
      "should": [
        { "match": { "gender": "Male" } },
        { "match": { "citizenship": "Singapore Citizen" } },
        { "range": { "age": { "gte": 25, "lte": 30 } } },
        { "match": { "occupation": "Software Developer" } },
        {
          "match": {
            "languages.spoken.English": {
              "query": "Fluent",
              "fuzziness": "AUTO"
            }
          }
        }
      ],
      "minimum_should_match": 2
    }
  }
}
```

#### 3. Special cases

It should contain a few special situations where slightly more advanced queries may be called for:

```
Consider using multi_match for fields that might contain the value in different subfields:
{
  "multi_match": {
    "query": "Software Developer",
    "fields": ["occupation", "job_title", "role"],
    "type": "best_fields",
    "fuzziness": "AUTO"
  }
}

For names or other fields where word order matters, you might want to use match_phrase with slop:
{
  "match_phrase": {
    "full_name": {
      "query": "John Doe",
      "slop": 1
    }
  }
}
```

#### 4. Leniency and coverage

It should contain instructions to avoid over-reliance on exact matches. We want to encourage fuzziness and partial matches, and avoid boolean AND statements. This is to counteract a possible hallucination, which might result in unworkable or unreasonable criteria that ends in an empty search result list.

```
 Generate a JSON query for Elasticsearch. Provide only the raw JSON without any surrounding tags or markdown formatting, because we need to convert your response to an object. 
Use a lenient approach with 'should' clauses instead of strict 'must' clauses. Include a 'minimum_should_match' parameter to ensure some relevance while allowing flexibility. Avoid using 'must' clauses entirely.
All queries must be lowercase.

Use 'match' queries instead of 'term' queries to allow for partial matches and spelling variations. Where appropriate, include fuzziness parameters to further increase tolerance for spelling differences. 
For name fields or other phrases where word order matters, consider using 'match_phrase' with a slop parameter. Use 'multi_match' for fields that might contain the value in different subfields.

If some criteria are strict, please judiciously use term queries and must clauses appropriately.
```

Once we have a prompt that fulfils all these criteria, we're ready to test it out!

## Test procedure

We'll define a class to call our Azure OpenAI LLM:

```
class AzureOpenAIClient:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_KEY_1"),
            api_version="2024-06-01",
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
        )

    def generate_non_streaming_response(self, prompt, model="gpt-4o", system_prompt=""):
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4096
        )
        return response.choices[0].message.content
        
LLM = AzureOpenAIClient()
```

And pass a query to the LLm along with the prompt we've just defined, like so:

```
query="All non-Singaporean men over the age of 25 who are software people living in woodlands" 
response=LLM.generate_non_streaming_response(query, system_prompt=prompt)
es_query=json.loads(response)
pprint(es_query)
```

This line in the prompt should allow us to directly load the LLM's response as a JSON object without any further processing required:

```
Generate a JSON query for Elasticsearch. Provide only the raw JSON without any surrounding tags or markdown formatting, because we need to convert your response to an object.
```

Now let's do some testing and see how it performs:

## Test 1

First, let's test the LLM's ability to handle simple criteria and handle some vagueness. I'm expecting a simple age range, fuzzy matches for male and software related occupations, and a negative match for Singapore citizens.

Query:

All non-Singaporean men over the age of 25 who are software people living in woodlands

Generated Elastic Query:

```
{
  "query": {
    "bool": {
      "minimum_should_match": 3,
      "must_not": [
        {
          "match": {
            "citizenship": "singapore"
          }
        }
      ],
      "should": [
        {
          "match": {
            "gender": "male"
          }
        },
        {
          "range": {
            "age": {
              "gt": 25
            }
          }
        },
        {
          "multi_match": {
            "fields": [
              "occupation"
            ],
            "fuzziness": "AUTO",
            "query": "software",
            "type": "best_fields"
          }
        },
        {
          "match_phrase": {
            "address.town": {
              "query": "woodlands",
              "slop": 1
            }
          }
        }
      ]
    }
  }
}
```

#### Results:

```
Total matches: 7742
Score: 8.3714
Name: Xiao E
Age: 78
Gender: Male
Citizenship: Foreigner
Occupation: Software Developer
Address: {'town': 'Woodlands', 'postal_code': '838414'}
---
Score: 8.3714
Name: Zafran binti Kamaruzaman
Age: 67
Gender: Male
Citizenship: Foreigner
Occupation: Software Developer
Address: {'town': 'Woodlands', 'postal_code': '790670'}
---
Score: 8.3714
Name: Saffuan binti Sofiah
Age: 48
Gender: Male
Citizenship: Foreigner
Occupation: Software Developer
Address: {'town': 'Woodlands', 'postal_code': '352474'}
---
```

Okay. That's basically what we expected. Totally relevant results only. Let's try a harder test.

## Test 2

Let's do a much vaguer query. I'm expecting a more explicit criteria for people with O- bloodtypes, who are currently deceased and born in Singapore.

Query:

Women who are not alive currently, who are universal blood donors born in singapore

Generated Elastic Query:

```
{
  "query": {
    "bool": {
      "minimum_should_match": 3,
      "should": [
        {
          "match": {
            "gender": "female"
          }
        },
        {
          "match": {
            "deceased": true
          }
        },
        {
          "bool": {
            "minimum_should_match": 1,
            "should": [
              {
                "match": {
                  "blood_type": "o-"
                }
              }
            ]
          }
        },
        {
          "match": {
            "country_of_birth": "singapore"
          }
        }
      ]
    }
  }
}
```

#### Results:

```
Total matches: 10000
Score: 7.8673687
Name: Bharat D'Souza
Blood Type: O-
Gender: Female
Country of Birth: Singapore
Deceased: True
---
Score: 7.8673687
Name: Neeti Kochhar
Blood Type: O-
Gender: Female
Country of Birth: Singapore
Deceased: True
---
Score: 7.8673687
Name: Shanta Somani
Blood Type: O-
Gender: Female
Country of Birth: Singapore
Deceased: True
---
```

These results are exactly as expected, and vectors didn't even enter the picture at any step. The natural inclination when you have a hammer is to look for nails to hit. In this case, I don't think embedding the data would have created any positive outcome to justify the added cost and complexity of adding an embedding model.

## Test 3

One last test - Let's see if it can handled nested properties like the languages field.

Query:

People who speak chinese dialects

Generated Elastic Query:

```
{
  "query": {
    "bool": {
      "minimum_should_match": 1,
      "should": [
        {
          "match": {
            "languages.spoken.Chinese": "Fluent"
          }
        },
        {
          "match": {
            "languages.spoken.Mandarin": "Fluent"
          }
        },
        {
          "match": {
            "languages.spoken.Cantonese": "Fluent"
          }
        },
        {
          "match": {
            "languages.spoken.Hokkien": "Fluent"
          }
        },
        {
          "match": {
            "languages.spoken.Teochew": "Fluent"
          }
        },
        {
          "match": {
            "languages.spoken.Hakka": "Fluent"
          }
        },
        {
          "match": {
            "languages.spoken.Hainanese": "Fluent"
          }
        }
      ]
    }
  }
}
```

#### Results:

```
Total matches: 10000
Score: 2.8383636
Name: Hadi binti Saleh
languages: {'spoken': {'Hainanese': 'Fluent', 'Esperanto': 'Fluent', 'Hakka': 'Fluent'}, 'written': {'Slovenian': 'Native', 'Mongolian': 'Basic', 'Dutch': 'Fluent'}}
---
Score: 2.8383636
Name: Liu Zai Su
languages: {'spoken': {'Hainanese': 'Fluent', 'Amharic': 'Native', 'Hakka': 'Fluent'}, 'written': {'Sinhala': 'Fluent'}}
---
Score: 2.8383636
Name: Kamal binti Zarina
languages: {'spoken': {'Zulu': 'Basic', 'Hakka': 'Fluent', 'Hainanese': 'Fluent'}, 'written': {'Armenian': 'Fluent', 'Spanish': 'Fluent'}}
---
```

Here's a significant advantage of using LLMs to define the query: Various Chinese dialects were correctly added to the query without my having to explicitly define them in the prompt. Convenience!

## Discussion

Not all search use-cases in the GenAI era should involve RAG and embeddings. It is straightforward to use traditional structured data to build search engines with the modern convenience of plain language querying. Since the core of this is really just prompt engineering, this approach isn't the best for searching over unstructured data. I do believe that there is a large class of use-cases waiting to be explored, where conventional structured database tables can be exposed to non-technical users for general querying. This was a difficult ask before LLMs were availablefor automatic query generation.

This seems to me like a bit of a missed opportunity.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blta4d95b6134c2a110/6a17f5e6505ac3fd3cad8cbf/13adbc901837835bb56abf15e377127b017cfac8-1536x1024.png)

[Basics](/search-labs/blog/category/basics)[Query DSL](/search-labs/blog/category/query-dsl)

### Unveiling unique patterns: A guide to significant terms aggregation in Elasticsearch

July 07, 2025|[Alexander Dávila](/search-labs/author/alexander-davila)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltda47d75430c4fa7c/6a17f5cae3179149242d5963/d5d04bbcfc3925f48f3487ea4c7e0dd2205316d0-720x420.jpg)

[Basics](/search-labs/blog/category/basics)[Query DSL](/search-labs/blog/category/query-dsl)

### Elasticsearch search by two fields

April 30, 2025|[Kofi Bartlett](/search-labs/author/kofi-bartlett)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter