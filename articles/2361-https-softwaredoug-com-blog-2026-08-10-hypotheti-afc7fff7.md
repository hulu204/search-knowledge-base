---
title: 'https://softwaredoug.com/blog/2026/08/10/hypothetical-classifications.html'
company: softwaredoug
tag: 搜索
date: 
url: https://softwaredoug.com/blog/2026/08/10/hypothetical-classifications.html
account: 
origin: en-rss
---
Using LLMs to classify products, search queries, etc is by now boring. Yet it can still be difficult to constrains the LLM’s output to the legal vocabulary of brands, colors, categories, etc your system allows.

In the Wayfair WANDS e-commerce dataset, for example, you want to classify a query like “wood coffee table” into its most appropriate category. Of which there are hundreds:

```
Furniture / Office Furniture / Desks
Furniture / Living Room Furniture / Coffee Tables & End Tables / Coffee Tables
Furniture / Living Room Furniture / Coffee Tables & End Tables / End & Side Tables
Décor & Pillows / Decorative Pillows & Blankets / Throw Pillows
Furniture / Bedroom Furniture / Dressers & Chests
```

The classic way to implement this would be with structured outputs. You tell your provide it must constrain its outputs to a list of legal values. In Pydantic, you create a giant literal of legal output values:

```
from typing import Literal
from pydantic import BaseModel, Field

FullyQualifiedClassifications = Literal[
 'Furniture / Bedroom Furniture / Beds & Headboards / Beds',
 'Furniture / Living Room Furniture / Chairs & Seating / Accent Chairs',
 'Rugs / Area Rugs',
  ...
  # times 500
]

class QueryClassification(BaseModel):
    """
    Structured representation of a search query for furniture e-commerce.
    Inherits keywords from the base Query model and adds category and sub-category.
    """
    classifications: list[FullyQualifiedClassifications] = Field(
        description="A possible classification for the product."
    )

response = client.responses.parse(
    model="gpt-5.4-mini",
    input="Classify the query: brown coffee table",
    text_format=QueryClassification,
)

print(response.output_parsed.message)
# Outputs: Furniture / Living Room Furniture / Coffee Tables & End Tables / Coffee Tables
```

This works. But there’s a way to do this a lot cheaper with small / dumb models at scale. Not to mention, there’s an [upper limit you can send](https://developers.openai.com/api/docs/guides/structured-outputs)

Luckily, there’s an easy pattern that makes LLM classification pretty seamless.

Just ask a dumb LLM to invent plausible, fake classifications for your query:

```
hallucination_prompt = f"""
Your task is to create novel, never seen before, furniture, home goods, or hardware classification that best fit a search query. 

Product classifications might look like:

Furniture / Living Room Furniture / Coffee Tables & End Tables / Coffee Tables
Décor & Pillows / Decorative Pillows & Blankets / Throw Pillows
Furniture / Bedroom Furniture / Dressers & Chests
Kitchen & Tabletop / Kitchen Organization / Food Storage & Canisters
School Furniture and Supplies / School Furniture / School Chairs & Seating / Stackable Chairs
Baby & Kids / Toddler & Kids Bedroom Furniture / Kids Beds

Here's the query to generate classifications for:

brown coffee table
```

Now we’re not sending the list of legal classifications. We’re instead, asking the LLM to make stuff up:

```
response = client.responses.parse(
    model="gpt-5.4-mini",
    input=hallucination_prompt,
    text_format=list[str],
)
```

It’ll then make up some BS that doesn’t actually exist in your real taxonomy like:

```
Furniture / Living Room / Tables / Coffee
```

Well that’s not very helpful.

Actually it’s extremely helpful. You can now resolve that into the real vocabulary.

It’s very cheap to build an in-memory set of embeddings of the REAL classifications. As I’ve done in [this notebook](https://colab.research.google.com/drive/1ljk72SBRuqWIijuEusCnDbhG1WAfZFcC#scrollTo=RZ-hEr-CSr9T) and [this utility](https://github.com/softwaredoug/cheat-at-search/blob/main/cheat_at_search/enrich/vocabulary.py).

In the notebook, I compute a MiniLM embedding of every real Wayfair classification. I compute the embedding of the fake, hypothetical embedding from the LLM. I then dot product the fake embedding into the real ones to find the most similar. Producing:

```
Furniture / Living Room Furniture / Coffee Tables & End Tables / Coffee Tables
```

You can give these hallucination tasks to dumb / cheap LLMs. And you don’t need to ship the schema over to the LLM every time.

---

### Upcoming events: Vectors Week

 [![Vectors Week: vector retrieval and hybrid search events](/assets/media/2026/vectors-week/image3.png)](/blog/2026/07/29/vectors-week) 

Join me for Vectors Week, a series of events about vector retrieval, hybrid search, and building your own vector database.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---