---
title: 'GLiNER as an Alternative to LLMs for Query Parsing - Evaluation'
company: Sease
tag: 评测
date: 2025-10-27
url: https://sease.io/2025/10/gliner-as-an-alternative-to-llms-for-query-parsing-evaluation.html
account: 
origin: harvest3-202607
---
Hi Information Retrieval community,  
In this series, we will be talking about **[GLiNER](https://arxiv.org/pdf/2311.08526)**, a flexible Named Entity Recognition (NER) model designed to identify any *type of entity*.

This topic will be divided into two blog posts:

* In our first blog post ([GLiNER as an Alternative to LLMs for Query Parsing – Introduction](https://sease.io/2025/10/gliner-as-an-alternative-to-llms-for-query-parsing-introduction.html)), we explored how GLiNER works, highlighting its underlying architecture, its differences from traditional NER models, and its evolution.
* In this second blog post, we will focus on evaluating GLiNER as a potential alternative to Large Language Models (LLMs) for **query parsing tasks**. We will run a comparative example and discuss whether GLiNER might be a better choice: GLiNER as an Alternative to LLMs for Query Parsing – Evaluation

## Could GLiNER be a viable alternative to LLMs for query parsing?

As the authors of the [GLiNER paper](https://arxiv.org/pdf/2311.08526) demonstrate, GLiNER outperforms both ChatGPT (in particular the *gpt-3.5-turbo-0301* model) and fine-tuned LLMs in zero-shot evaluations on various NER benchmarks (using F1-score based on exact matches between predicted and actual entities).

Over the past year, we’ve worked on query parsing tasks for some of our clients using LLMs (you can check out these two blog posts if you’re interested [[1](https://sease.io/2024/08/from-natural-language-to-structured-solr-queries-using-llms.html), [2](https://sease.io/2026/12/ai-powered-search-results-navigation-with-llms-json-schema.html)]). Query parsing aims to transform a natural language query into a structured, executable query by identifying key entities and mapping them to your indexed data. We then wondered whether GLiNER might offer a more efficient and viable alternative.

What follows is a comparison we performed locally between the GLiNER models and large language models, specifically OpenAI’s models, to better understand their respective performance and suitability for our use case.

## NER Examples

Let’s start with this simple input text:

```
				
					Elton John performed in the United States at Madison Square Garden in 2022, with tickets costing 350 USD.
				
			
```

And this is the output we expect:

```
				
					{
“person”: “Elton John”,
“location”: “United States”,
“date”: 2022,
“venue”: “Madison Square Garden”,
“price”: 350 USD,
“event”: “concert”
}
				
			
```

We first use **GLiNER**, specifically the model **`urchade/gliner_medium-v2.1`**, with the following code:

```
				
					from gliner import GLiNER

# Initialize GLiNER with the base model
model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")

# Sample text for entity prediction
text = """ 
Elton John performed in the United States at Madison Square Garden in 2022, with tickets costing 350 USD.
"""

# Labels for entity prediction
labels = ["person", "location", "date", "venue", "price", "event"]

# Perform entity prediction
entities = model.predict_entities(text, labels)

# Display predicted entities and their labels
result = {entity["label"]: [entity["text"]] for entity in entities}
				
			
```

As shown in the code, both the text and the list of expected entity labels are passed to the model. The model then predicts the entities found in the text according to the provided labels.

Here is the result:

```
				
					{
    'person': ['Elton John'], 
    'location': ['United States'], 
    'venue': ['Madison Square Garden'], 
    'date': ['2022'], 
    'price': ['350 USD']
}
Inference Time: 0.16 seconds
				
			
```

The entity label **“event”** is missing from the output, but this was expected given how the model works: the model did not find any match between this entity type and the words present in the input text.

Then we used the bi-encoder model: **`knowledgator/modern-gliner-bi-large-v1.0`**, and this was the output:

```
				
					{
'person': ['Elton John'], 
'location': ['United States'], 
'venue': ['Madison Square Garden'],
'price': ['350 USD']
}

Inference Time: 0.39 seconds
				
			
```

Not only is the **“event”**entity missing (as expected), but the **“date”** entity is also not detected, which was unexpected and highlights a limitation of the bi-encode, we would say.  
A possible explanation for this is that the model uses a **separate encoder** that processes each entity label independently, without full access to the broader context of the sentence. As a result, the connection between the label “date” and the numerical value “2022” can be **weak or ambiguous**.  
This is reflected in the low similarity score (lower than the default threshold of 0.5), which prevents the model from returning the entity:

```
				
					{'end': 74, 'label': 'date', 'score': 0.3884320855140686, 'start': 70, 'text': '2022'}
				
			
```

In contrast, if the entity label had been “year,” the match would have been stronger and successfully detected:

```
				
					{'end': 74, 'label': 'year', 'score': 0.958095908164978, 'start': 70, 'text': '2022'}
				
			
```

A test was also performed where the order of the labels in the list was changed, but the result remained the same.

We then performed the same task using a large language model (LLM), specifically by calling OpenAI’s native APIs directly. The code used for this task is shown below:

```
				
					def parse_with_llm(input_text, entity_types):
    entities_list = "\n".join(f"- {e}" for e in entity_types)

    prompt = f"""Extract the following entities from the text input provided below:
        Entity type:
        {entities_list}

        Text Input:
        {input_text}

        Return the result as a JSON object with keys as entity types and values as the extracted entities.
        """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system",
             "content": "You are an expert Natural Language Processing (NLP) system specializing in Named Entity "
                        "Recognition (NER). You extract structured information from unstructured text"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
				
			
```

Here, different models were tested, starting from an older version and moving to one of the most recent ones, since the model used in the original GLiNER paper is now deprecated.

|  |  |  |
| --- | --- | --- |
| **gpt-3.5-turbo-0125** | {   “person”: [“Elton John”],   “location”: [“United States”],   “date”: [“2022”],   “venue”: [“Madison Square Garden”],   “price”: [“350 USD”],   **“event”: [“Elton John’s performance”]** } | Inference Time: 2.08 seconds |
| **gpt-4.1-mini-2025-04-14** | {   “person”: [“Elton John”],   “location”: [“United States”],   “date”: [“2022”],   “venue”: [“Madison Square Garden”],   “price”: [“350 USD”],   **“event”: [“performance”]** } | Inference Time: 2.28 seconds |
| **gpt-4o**/**gpt-4.1** | {   “person”: [“Elton John”],   “location”: [“United States”],   “date”: [“2022”],   “venue”: [“Madison Square Garden”],   “price”: [“350 USD”],   **“event”: []** } | Inference Time: 2.62 seconds |

As we can see from the table, the GPT-4o and GPT-4.1 models were not able to return the **“event”** label, similar to what happened with GLiNER. In contrast, the older models seemed to be able to grasp the meaning of the sentence and infer the type of event to extract, even though it was not explicitly mentioned in the text.

The flexibility of LLMs, however, lies in the ability to tweak the prompt. By simply adding a sentence such as **“If an entity type is not found, try to infer it,”** we are able to obtain the desired result.

*It’s important to note, however, that writing something in the prompt doesn’t guarantee the model will follow it, as we are essentially relying on prompt-based “rules” without any certainty that they will affect the outcome.*

Another advantage of using LLMs is the ability to return a rationale, providing explainability for the choices made. If shown to the user, this could help them understand the reasoning behind the extracted entities and the model’s decisions.

```
				
					{
  "person": [
    {
      "entity": "Elton John",
      "rationale": "Elton John is a well-known individual, explicitly mentioned as the performer in the sentence."
    }
  ],
  "location": [
    {
      "entity": "United States",
      "rationale": "United States is a country mentioned as the location where the performance took place."
    }
  ],
  "venue": [
    {
      "entity": "Madison Square Garden",
      "rationale": "Madison Square Garden is a famous event venue identified as the place where the performance happened."
    }
  ],
  "date": [
    {
      "entity": "2022",
      "rationale": "2022 is the year in which the performance occurred, making it the date entity."
    }
  ],
  "price": [
    {
      "entity": "350 USD",
      "rationale": "350 USD is explicitly mentioned as the cost of tickets, clearly fitting the price entity."
    }
  ],
  "event": [
    {
      "entity": "Elton John concert",
      "rationale": "Although not explicitly named as an 'event', the context describes a performance by Elton John, which is interpreted as an 'Elton John concert'."
    }
  ]
}

Inference Time: 4.63 seconds
				
			
```

A small-scale local benchmark was performed by running a test on 30 queries in natural language, each requiring the identification of 2 to 4 entities or labels, comparing **gliner\_medium-v2.1** with **gpt-4.1-mini-2025-04-14**.

In terms of **accuracy**, **gpt-4.1-mini-2025-04-14** performed flawlessly, correctly identifying all entities across every query, achieving 100% accuracy. In contrast, with **gliner\_medium-v2.1** the responses were generally fine, but only 16 out of 30 were fully correct — the others were missing some entities.

When it comes to **average response time**, **gliner\_medium-v2.1** was significantly faster, with an average inference time of just 0.08 seconds. On the other hand, **gpt-4.1-mini-2025-04-14** took on average 1.21 seconds to generate a response.

## Query Parsing Example

Let’s now imagine we have the following user query written in natural language:  
*“Cost per square meter for family houses in Rabat”*

And let’s assume we have some statistical data like the following, i.e. fields we have indexed in our search engine along with the possible values they can take.

{  
“**Frequency**“: [“Daily”, “Monthly”, “Quarterly”, “Yearly”],  
“**Covered area**“: [Capital city/financial center”, “Whole country”, “Countryside”, “Small city”],  
“**Real estate type**“: [“Office & Retail”, “Single family house”, “Flat” ]  
“**Priced unit**“: [“Pure price”, “Per square meter”, “Per cubic meter”],  
“**Reference area**“: [“Morocco”, “France”, “Germany”, “Italy”, “United Arab Emirates”]  
}

What we want to do now is not just extract entities from the text, but go a step further and **map those entities directly to the exact values I have in the index**, so that we can build executable queries. The expected output for the query above is:

{  
“**Frequency**“: [],  
“**Covered area**“: [Capital city/financial center”],  
“**Real estate type**“: [“Single family house” ]  
“**Priced unit**“: [“Per square meter”, ],  
“**Reference area**“: [“Morocco”]  
}

As we have already shown in our previous blog posts [[1](https://sease.io/2024/08/from-natural-language-to-structured-solr-queries-using-llms.html), [2](https://sease.io/2026/12/ai-powered-search-results-navigation-with-llms-json-schema.html)], this can be achieved using LLMs, especially OpenAI’s models. More recently, thanks to the introduction of **structured output with JSON schema**, we have also been able to eliminate hallucinations, which represents a significant milestone.

This led us to ask: can the same result be achieved using models like GLiNER?

The first thing we tried to do was to pass our dimensions, i.e. the fields, as entities:

```
				
					user_query = " Cost per square meter for family house in Rabat"

entity_types = ['Frequency', 'Covered area', 'Real estate type', 'Priced unit', 'Reference area']

entities = model.predict_entities(user_query, entity_types)
				
			
```

However, this was the output, using the model **`gliner_medium-v2.1`**:

```
				
					{	
'Real estate type': ['family houses']
}

Time: 0.16 seconds
				
			
```

The model struggles to detect most of the entities, especially when they are not explicitly mentioned or when the text is ambiguous. Even when an entity is detected, the value extracted does not necessarily match the predefined values we have stored in our system.

What we then tried was to pass the **possible values** of the fields as entities (even though this is not conceptually correct). The idea behind this is that, since the model is comparing embeddings, it might actually make sense in practice: by providing the exact values, there’s a higher chance the model can match the right information from the text. And this is what we achieved:

|  |  |  |
| --- | --- | --- |
| **gliner\_medium-v2.1** | { **‘Covered area’: [‘Capital city/financial center’],** } Inference Time: 0.45 seconds | [{‘end’: 48, ‘label’: ‘Capital city/financial center’, ‘score’: 0.8661268949508667, ‘start’: 43, ‘text’: ‘Rabat’}] |
| **gliner\_large-v2.1** | { **‘Covered area’: [‘Capital city/financial center’],** **‘Real estate type’: [‘Single family house’],** **‘Priced unit’: [‘Per square meter’]** } Inference Time: 0.45 seconds | [{‘end’: 48, ‘label’: ‘Capital city/financial center’, ‘score’: 0.9182731509208679, ‘start’: 43, ‘text’: ‘Rabat’}]  [{‘end’: 39, ‘label’: ‘Single family house’, ‘score’: 0.6846156716346741, ‘start’: 26, ‘text’: ‘family houses’}]  [{‘end’: 21, ‘label’: ‘Per square meter’, ‘score’: 0.9654452800750732, ‘start’: 0, ‘text’: ‘Cost per square meter’}] |

In this way, we were able to return more results because the model successfully matched the provided **label**—for example, **“Capital city/financial center”**—with the text **“Rabat”**, assigning it a high similarity score of **0.87**. As a result, the model returned the correct entity even though the label and the text did not literally match.

## Gliner Fine-tuning

Although these test results could be seen as encouraging, and the response times are impressively low, GLiNER does not appear to be well-suited for this type of task (more complex query parsing, where entities must be inferred, aligned with indexed values). In such cases, large language models (LLMs) remain the recommended solution.

However, it is worth noting that **fine-tuning** remains a powerful strategy to adapt a model to a specific domain or set of tasks.  
As shown in the [official repository](https://github.com/urchade/GLiNER/tree/training/data), GLiNER expects the training data in a simple and readable JSON format, where each entry includes a sentence and a list of entities, each defined by its surface form, type, and character-level position:

```
				
					[
  {
    "sentence": "In 2003 , the Stade de France was the primary site of the 2003 World Championships in Athletics .",
    "entities": [
      {
        "name": "Stade de France",
        "type": "location",
        "pos": [14, 29]
      },
      {
        "name": "2003 World Championships in Athletics",
        "type": "event",
        "pos": [58, 95]
      }
    ]
  },
  etc...
]
				
			
```

This structure allows the model to learn from precise annotations and refine its predictions based on the characteristics of the domain it is fine-tuned for. GLiNER can benefit considerably from task-specific fine-tuning, especially when supported by high-quality annotated data.

Although we have not tested it directly, a Python library called `gliner-finetune` is also available to facilitate this process. It provides a streamlined workflow to generate synthetic NER examples (e.g., via GPT-based prompting), convert them into the expected training format, and perform fine-tuning of a GLiNER model on custom datasets. This could be particularly useful when real annotated data is limited or unavailable, and offers a practical entry point for domain adaptation.

## Final Considerations: Which Model to Choose?

In conclusion, the choice between **GLiNER** and a **Large Language Model (LLM)** depends on the specific requirements of the task and the constraints of the system.

* **GLiNER** may be sufficient and cost-effective when the goal is the **extraction of explicit entities** from short and structured texts, such as user queries or single sentences, where no inference is needed. It is particularly suitable in contexts where **low latency**, **cost efficiency**, and **resource constraints** are priorities, as it is **open-source**, **lightweight**, and delivers **faster response times** compared to LLMs. However, its performance is limited by a small context window (512 tokens), and it struggles when more complex reasoning or entity inference is required.
* **LLMs**, on the other hand, are better suited for tasks that involve **inference, deep contextual understanding**, or where **explainability** is important. They can provide rationales along with their answers, helping users understand the reasoning behind the outputs. While LLMs typically involve higher computational costs and longer response times, they are often the preferred choice when **complexity, flexibility, and accuracy** outweigh the need for ultra-fast responses.

## Need Help With This Topic?​​

If you’re struggling with GLiNER, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with GLiNER, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)