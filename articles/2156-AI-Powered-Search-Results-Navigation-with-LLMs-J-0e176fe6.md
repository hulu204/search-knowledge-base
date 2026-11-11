---
title: 'AI-Powered Search Results Navigation with LLMs & JSON Schema'
company: Sease
tag: 工程相关
date: 2025-08-20
url: https://sease.io/2025/08/ai-powered-search-results-navigation-with-llms-json-schema.html
account: 
origin: harvest3-202607
---
Struggling to identify relevant filters among too many facets and frustrating results navigation?

In this blog post, we explore an **AI-powered Filter Assistant**, designed for the Statistical Data and Metadata eXchange (SDMX) standard to improve User eXperience in navigating search results efficiently and effectively.   
We show **how LLMs can be leveraged to suggest the best filters for natural language queries** by analysing both user input and indexed data, ultimately helping refine search results in Apache Solr.   
We share wins, fails, and lessons learned.

The blog post explores the topics discussed at the [Berlin Buzzwords 2025](https://2025.berlinbuzzwords.de/session/ai-powered-search-results-navigation-with-llms-json-schema/) conference. Our goal is to capture the essence and key points from our presentation, providing a clear and complete summary for those who were unable to attend the conference.

**This project was commissioned by the [Bank of International Settlements](https://www.bis.org/index.htm) (BIS). So, this blog post and the related talk were prepared with the BIS’s kind support.**

## Use Case Review

##### Problem Statement

Traditional keyword-based search systems often struggle to understand user intent. Vocabulary mismatch, missed semantic similarity, or ambiguity usually lead to the same outcome: irrelevant results or, at worst, no results.   
Large Language Models (LLM) capabilities can therefore be leveraged to help overcome these limitations. Specifically, we expect a Large Language Model to:

* Allow for a **Natural Language Search**
* **Disambiguate** the meaning of a user’s natural language query, resolving ambiguities and understanding the actual intent.
* **Map user intent to document content**, bridging the gap between how users express themselves and how content is structured.
* **Extract** the relevant information and use it to **implement a structured Solr (Elasticsearch/etc…) query**.
* Provide search results where **Solr (Elasticsearch/etc…) struggles**, especially in zero-result cases.
* **Provide a rationale** to the end users explaining why certain selections or results are being suggested.
* Support for **multilingual queries**, enabling broader accessibility and inclusivity in diverse linguistic contexts.

##### SDMX Data

The AI-powered Filter Assistant was designed for the Statistical Data and Metadata eXchange (SDMX) standard to improve User eXperience in navigating search results efficiently and effectively within the BIS Data Portal.   
**SDMX (Statistical Data and Metadata eXchange)** is an international initiative that aims to promote more efficient processes for exchanging and sharing statistical data and metadata among international organisations, their constituencies, and data users.   
The BIS Data Portal leverages the SDMX standard to publish and share its statistical datasets in a structured, interoperable format, enabling efficient access, integration, and analysis across institutions.

In the BIS Data Portal, each (Solr) document represents a **timeseries**, a sequence of observations recorded at regular intervals over time.  
Time series are grouped into **dataflows**, which organise related series according to a shared structure and thematic focus.  
Each dataflow corresponds to a specific domain of economic or financial data and acts as a **structured container** for a series on a particular topic. It is defined by a **Data Structure Definition (DSD)**, which specifies its **dimensions** and **attributes**.

##### AI Dimensions Filtering Assistant Example

Let’s take, for example, the natural language query **“What are the office space prices in Rabat”**. It returns no results, highlighting how the current search in the BIS Data Portal struggles to retrieve relevant documents:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/02/Screenshot-2025-05-19-alle-15.29.16.png?fit=875%2C556&ssl=1)

[Search for the same query](https://data.bis.org/search?q=What+are+the+office+space+prices+in+Rabat)

Thanks to the use of the **AI-powered Dimensions Filtering Assistant**, user intent can be automatically interpreted and the most relevant filters identified to refine search results:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/02/Screenshot-2025-05-19-alle-15.57.28.png?fit=1337%2C835&ssl=1)

To do this effectively, the model is provided with **structured information from the dataset**, including available topics, countries, and dimension values, so that it understands the context and the data structure it is querying against.

In this case, the assistant identifies the main **topic** as *Commercial Property Prices* and selects **Morocco** as the relevant *country*, correctly understanding that Rabat is its capital.   
It then determines the appropriate **dimensions** based on the query context:

* Covered area: **Capital city/biggest city/financial centre**
 * Real estate type: **Office & Retail**

These filters are returned in a structured JSON response and can be **automatically pre-applied** in the user interface, eliminating the need for manual selection and significantly improving the user experience.

## LLM-based Search for SDMX Data

##### API Structure

We have designed the process using the components shown in the diagram below:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/02/Component-diagram-Berlin-Talk.drawio.png?fit=629%2C309&ssl=1)

1) The **AI** **Filter** **Assistance (RESTful**) **API**: developed using Python and FastAPI, is the **main component responsible for handling search requests from the user interface**. It accepts a natural language query as input, delegates it to the appropriate APIs for subsequent processing and returns relevant topics and dimensions in a structured format.

2) **SDMX**: at application startup, a series of SDMX endpoints are invoked to **retrieve all the necessary SDMX data and metadata** required for the suggestion system to work properly. The retrieved data is parsed and organised into efficient data structures (such as dictionaries). To optimise performance and avoid redundant network calls at each application restart, these structures are then serialised and stored locally in a **cache file**. This mechanism ensures that the same information is not downloaded repeatedly, significantly improving startup time and reducing the load on external services. An endpoint has also been implemented, which is automatically triggered whenever changes are made to the data, ensuring the cache file is refreshed accordingly.

3) **openAI** (**Large Language Model):** during the runtime phase, the LLM is invoked multiple times to perform specific tasks. Since our implementation relies on OpenAI models, we opted to use their native APIs directly, which proved to be a simple and effective solution. As a result, there was no need to introduce an additional abstraction layer for model inference.

##### Structured Process Flow

The diagram below illustrates the step-by-step process flow implemented by the system:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/02/Screenshot-2025-06-05-alle-11.55.12.png?fit=958%2C458&ssl=1)

###### DATA RETRIEVAL

When the application starts, a set of SDMX endpoints is triggered to retrieve all the data and metadata needed for the Filter Assistance system to operate correctly. This information is then parsed and organised into efficient data structures, such as dictionaries, and saved locally in a cache file to improve performance and avoid repeated network requests.

The dictionaries created in this phase are used both to provide input to the LLM and to build the final JSON response. These include:

* **Topic → Short Description**:   
  a dictionary where keys are topics and values are topic descriptions.   
  Es. `{"Commercial Property Prices": "Tracks developments of office, retail premise and industrial property prices", "Residential property prices": "Tracks developments of residential property prices ...", etc...}`
* **Dataflows → Dimensions (code, label)**:   
  a dictionary where each key represents a dataflow code, and each value is another dictionary mapping the dimension codes (associated with that specific dataflow) to their corresponding human-readable descriptions.   
  Es. `{"Dataflow_1": {"FREQ": "Frequency", "REF_AREA": "Reference area", "COVERED_AREA": "Covered area", ...}, "Dataflow_`2`": {"FREQ": "Frequency", ... }, ...}`
* **(for each dataflow) Dimensions → Values (code, label)**:   
  a dictionary in which each key corresponds to a dataflow code. Each dataflow maps to a dictionary where the keys are dimension codes, and the values are dictionaries mapping each dimension’s possible values to their human-readable descriptions.   
  Es.  `{"Dataflow_1": {"FREQ": { "A": "Annual", "B": "Daily - business week (not supported)", etc...}, etc..}, "Dataflow_`2`": {"REF_AREA": { "1X": "ECB", .. }, etc...}, etc...}`
* **Dataflows → Country-Related Dimensions**:   
  a dictionary where each key is a dataflow code, and the corresponding value is a list of dimension codes that refer to countries.  
  Es. `{"Dataflow_1":["REF_AREA"], "Dataflow_`2`": ["REF_AREA", "REP_CTY"], etc... }`

###### TOPIC SELECTION

In this step, the system is tasked with identifying the most relevant topics based on the user’s query. This is achieved by calling the endpoint:

```
				
					GET /dimensionsAssistant/identifyTopics?query=&lt;user_query&gt;
				
			
```

The primary purpose of this endpoint is to identify one or more topics that help interpret the user’s intent and narrow down the scope of the search. The model is provided with a complete list of available topics, each accompanied by a brief description, from which it can make its selection. Here is the **prompt**:

```
				
					response_topics = client.chat.completions.create(
   model=Config.MODEL_NAME,
   messages=[
      {"role": "system", "content": "You are an expert in financial
       statistical data. You will receive a user query and a dictionary. The
       keys of the dictionary represents a topic or category. The values of
       the dictionary are the related topic' description. \n You are required
       to select the most relevant topic for the given query. If you are
       unsure among a few topics, select at most two or three of them."},
      {"role": "user", "content": "Query: " + natural_language_query + ". \n
       Dictionary:" + str(LLM_topics_to_description)}
   ],
   response_format=json_schema_topics
)
				
			
```

*NOTE: right now, prompt engineering is basically trying to interact with something that we can’t program directly. Instead, we have to rely on writing “rules” into the prompt text, without knowing for sure if they’ll affect the result. You can run tests, but we don’t really know what happens behind the scenes, so it’s not ideal. That said, with structured outputs, we’re starting to move toward something closer to programming, and that’s exciting. Of course, this is just the beginning, and we hope to see meaningful improvements soon.*

When the user submits a free-text query, the system analyses it and returns a JSON response containing:

* **Topics Selected**: up to three suggested topics, which best reflect the focus of the query
* **Reasoning**: which explains why each topic was selected

***Example:***

```
				
					GET /dimensionsAssistant/identifyTopics?query=What are the office space prices in Rabat
				
			
```

***Output*:**

```
				
					{
  "Topics selected by the LLM": [
    "Commercial Property Prices"
  ],
  "Reasoning": "The query 'What are the office space prices in Rabat' specifically pertains to office spaces, which fall under the category of commercial properties. The description for 'Commercial Property Prices' explicitly mentions office developments, making it the most relevant topic to address the query about office space prices"}
				
			
```

###### COUNTRY and DIMENSION SELECTION

Once one or more topics have been identified, the data provided to the model is filtered accordingly, and the second endpoint is invoked:

```
				
					GET /dimensionsAssistant/identifyDimensions?query=&lt;user_query&gt;&amp;dataflow=&lt;dataflow_id&gt;
				
			
```

Since this endpoint operates at the dataflow level, if the model identifies **multiple topics** (each linked to a different dataflow), **multiple calls** to this endpoint will be made—one per dataflow. This approach ensures that only the relevant data associated with each topic is passed to the model, helping reduce noise and improving response accuracy.

Here, the system is tasked with two main objectives:   
1) **Identify** one or more **relevant** **countries** based on the user’s query. The model is provided with a complete list of geographical areas from which it can make its selection. Here is the **prompt**:

```
				
					response_country = client.chat.completions.create(
   model=Config.MODEL_NAME,
   messages=[
      {"role": "system", "content": "You are an expert in financial
       statistical data and geography. You will receive a Query.\n Based on
       the JSON schema provided, which contains a list of geographic area
       names followed by their codes (e.g., 'Euro Area (XM)'), identify and
       return the geographic areas from the given Query.\n Follow these
       rules:\n ..."},
      {"role": "user", "content": "Query: " + natural_language_query}
   ],  response_format=generate_LLM_schema_for_country(dataflow_country_values_list,temperature=0.1
)
				
			
```

2) Once the model identifies one or more countries, the dimension-values are filtered to include only those available for the identified country (or countries). This filtered subset is then passed to the LLM for the second call, which **identifies** the most **relevant** **dimension suggestions** that align with the user’s intent. If no country is identified, no filtering is applied and all dimension-values are considered.   
The model is provided with a predefined JSON schema containing dimensions and their possible values. Here is the **prompt**:

```
				
					response_dimensions = client.chat.completions.create(
   model=Config.MODEL_NAME,
   messages=[
      {"role": "system", "content": "You are an expert in financial
       statistical data. You will receive a user query.\n Based on the JSON
       schema provided, which contains keys representing financial statistical dimensions and their associated values, you are required to extract the most relevant values following these rules:\n ..."}, 
      {"role": "user", "content": "Query: " + natural_language_query}
   ],
   response_format=generate_LLM_schema_for_dimension(LLM_dimensions_dict),
   temperature=0.1
)
				
			
```

Once both calls are completed, the system generates and returns a JSON response containing:

* **Countries Selected**: one or more relevant countries based on the user’s query
 * **Country** **Reasoning**: which explains why each country was selected
 * **Dimensions Selected**: one or more relevant dimensions based on the user’s query
 * **Dimension** **Reasoning**: which explains why each dimension was selected

***Example:***

```
				
					GET /dimensionsAssistant/identifyDimensions?query=
What are the office space prices in Rabat
&amp;dataflow=WS_CPP
				
			
```

***Output*:**

```
				
					{
  "Countries selected by the LLM": {
    "Reference area": [
      "Morocco"
    ]
  },
  "Country Reasoning": "Rabat is the capital city of Morocco. Therefore, the geographic area associated with Rabat is Morocco (MA).",
  "Dimensions selected by the LLM": {
    "Frequency": [],
    "Covered area": [
      "Capital city/biggest city/financial center"
    ],
    "Real estate type": [
      "Office &amp; Retail"
    ],
    "Real estate vintage": [],
    "Compiling agency": [],
    "Priced unit": [],
    "Seasonal adjustment": []
  },
  "Dimension Reasoning": "The user query specifically mentions 'office space prices' and 'Rabat'. Therefore, the relevant values are 'Office &amp; Retail' for the 'Real estate type' as it pertains to office spaces, and 'Capital city/biggest city/financial center' for the 'Covered area' since Rabat is the capital city of Morocco. No other dimensions such as frequency, compiling agency, priced unit, or seasonal adjustment were explicitly mentioned in the query, so they are not selected."}
				
			
```

As you can see, the model returns all the available dimensions for that dataflow, but some of them are left empty. This indicates that the model did not find enough explicit or implicit signals in the query to select values for those dimensions.

##### Limitations and Lessons Learned

**1)** **Prompt instructions are not always strictly followed by the model**:   
Despite significant advancements in instruction-following capabilities, LLMs do not always strictly adhere to prompt instructions, especially when prompts are ambiguous, overly long, or when multiple tasks are combined.

**2) The more relevant the context (shorter and higher quality), the better the model performs:**  LLMs tend to produce better results when the input context is both highly relevant and succinct. Providing too much information, especially if loosely related or redundant, can dilute the focus of the model and introduce noise, leading to less accurate or coherent responses.

**3) Default or Lower Temperature Recommended**:  
In an LLM, the temperature is a parameter that controls the randomness of the output. It ranges from 0 to 2, with a default value of 1. Lower values make the model more deterministic and focused, while higher values increase creativity and variability in responses. We experimented with a low-temperature value, but the responses were **still not consistent or fully deterministic** — they varied from one call to another. On the other hand, using a high temperature led to overly creative outputs, where the model started producing nonsensical text and mixing different languages:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/02/Screenshot-2025-03-11-alle-11.11.48.png?fit=760%2C752&ssl=1)

In this specific context, creativity is not required. The model is expected to strictly adhere to the structured data provided and select only from those options, rather than generating imaginative or unexpected content. Therefore, it’s advisable to either keep the default temperature value or try lowering it slightly to encourage more consistent responses.

##### Solr Query Optimisations

Given the dimensions with values returned by the model, how should the Solr query be executed?   
We have mainly two options:

* **OR** – Filters are applied using the `OR` operator, meaning the query will return documents that match **any** of the specified values across the dimensions. This approach is useful in cases of **zero-results queries**, since it broadens the result set, potentially affecting the ordering of the results.

* **AND** – Filters are applied using the `AND` operator. This approach is effective in cases of **too many results**, as it helps narrow down the result set by including only documents that match all the specified values, making the filtering more restrictive.

## Structured Output and JSON Schema

**Structured output** refers to model responses that follow a predefined, machine-readable format—typically in JSON or another structured data representation. Instead of returning free-form text, the model is instructed to generate output that adheres to a specific structure, such as a dictionary with defined keys, arrays of objects, or nested fields.  
This makes it easier to read, validate, and use the output directly in applications, without needing to clean or interpret the response.

Today, structured output is supported not only by OpenAI models but also by other language models from various providers, including both commercial and open-source solutions. In our case, we used OpenAI’s implementation because the project was already based on these models.

OpenAI’s structured output feature allows us to define a schema and guide the model to produce outputs that match it. Even though GPT-4o has been trained to understand and follow these schemas, it’s still a generative model, so the output isn’t always guaranteed to be valid.  
To address this, OpenAI added a technique called ***constrained sampling or constrained decoding***; this method dynamically restricts the model’s token generation process by converting the schema into a set of grammar rules, ensuring that at each step, the model can only choose tokens that keep the output valid according to the expected structure.  
The result is a much more reliable and schema-compliant output, combining the model’s generative capabilities with a rule-based layer that ensures structure and correctness.

Here is, for example, the JSON schema that defines the expected structure for the country selection task:

```
				
					"type": "json_schema",
    "json_schema": {
        "name": "identified_geographical_areas",
        "schema": {
            "type": "object",
            "properties": {
                "geographical_areas": {
                   "type": "array",
                   "items": {
                      "type": [
                           "string",
                           "null"
                            ],
                     "description": "Geographical areas present in the Query"
                     "enum": ["Indonesia (ID)", etc…, null]
                    }
                },
                "rationale": {
                    "type": "string",
                    "description": "Why these areas were identified" 
                }
            },
            "required": ["geographical_areas","rationale"],
            "additionalProperties": false
        },
        "strict": true
    }
				
			
```

In this task, the model receives a user query and is expected to identify the most relevant country or geographical area from a predefined list. Using the structured output schema, the model must return an object with 2 (required) fields:

* **geographical\_areas**: an array containing strings (or null) representing recognised country or region names from the predefined list (in *enum*). The values must exactly match the options defined in the schema.
 * **rationale**: a string explaining the reasoning behind the selection.

The strict schema ensures that the model produces only the required fields — no additional ones are allowed — and that country selection is restricted to the predefined list in the schema and justified based on the user query.

##### Limitations and Lessons Learned

* **[Documented list of limits](https://platform.openai.com/docs/guides/structured-outputs?api-mode=responses#objects-have-limitations-on-nesting-depth-and-size)**:
  + The total string size of all property names, definition names, enum values, and const values cannot exceed 15,000 characters.
  + A schema can include up to 500 enum values in total; if a single enum property has more than 250 values (as strings), the combined length of all those strings must not exceed 7,500 characters.
  + You should always set `additionalProperties: false` in objects. This makes sure that the object doesn’t include any extra keys that are not defined in the schema.
* **null** needs to be included among the values of the **enum** parameter; otherwise, it won’t be returned.
* **enum** parameter only allows a list of single values, not key-value pairs (as we need for the topic selection).

## Test Framework

We designed our evaluation framework to include both manual and automated testing, each serving a different purpose in assessing the quality and reliability of the model’s output.

##### Manual Evaluation

We developed an automated tool that sends a batch of queries to the API and stores the responses in a structured Excel file. This format was chosen by BIS to facilitate collaborative review and validation by domain experts.

The evaluation was conducted on a curated test set consisting of 24 queries applied across 23 dataflows. For each unique `<query, dataflow>` pair, two types of tests were created:

1. To evaluate the **topic(s)** identified by the model
2. To evaluate the **dimension(s)** suggested for filtering

The resulting Excel file included the following elements for each test:

* **Extracted topics**, along with the model’s reasoning
* **Extracted countries**, including reasoning and relevant input context (to support debugging and explainability)
* **Extracted dimensions**, again with reasoning and input context (to support debugging and explainability)

This evaluation provides clear visibility into the model’s predictions, making it easier to analyse results, provide feedback, and debug unexpected behaviours.

##### Automatic Evaluation

We also implemented an automated testing framework to provide a quantitative view of the model’s performance. Domain experts first selected a subset of 7 dataflows and 12 representative queries to construct the evaluation dataset. Each `<query, dataflow>` pair was again tested for both topic and dimension identification.

Each test passes **only if all expected values** (topics or dimensions) are returned correctly.   
An automated script was built using `pytest` to systematically evaluate the quality of the LLM-generated responses. The framework enables repeated execution of integration tests and provides a consistent, metric-driven assessment of system performance.  
For each run, we computed the following metrics:

* Overall **% of successes in topic** extraction
* Overall **% of successes in dimension extraction**
* Overall **% of successes across all tests**
* For each **specific test % of successes**

##### Evaluation Tool Improvements

Below are some ideas we considered to improve the current test framework and make the evaluation process more robust and informative:

– **From Binary Pass/Fail to Graded Scoring**  
Currently, an integration test fails if even one of the returned dimension values does not exactly match the expected ones. This strict pass/fail logic does not account for partial correctness and may underestimate the performance of the model in cases where it captures most, but not all, of the relevant filters.  
A more nuanced evaluation could involve introducing a scoring mechanism. For example, a score between 0 and 1 could be computed based on the number of correct filters returned out of the total expected.   
A useful metric to consider could be the [Jaccard Index](https://en.wikipedia.org/wiki/Jaccard_index), a statistic used for comparing the similarity and diversity of sample sets. Without going too much into detail, for each query in the test set, we can compute the similarity between the expected structure and the one generated by the LLM by calculating the Jaccard Index of the field sets and then, for each field, the Jaccard Index of their corresponding values. Averaging the results over the entire query set provides an overall similarity score.  
This would allow for a more informative assessment of the model’s performance, especially in edge cases where it performs well but not perfectly.

– **Expanding the Test Set**  
At the moment, only a small set of queries is tested through the evaluation tool.  
To address this, we propose leveraging the LLM itself to automatically generate a broader and more representative set of test queries. The generation process could be guided by contextual data that we provide. Additionally, we could collect and supply queries that users frequently submit, helping the model produce even more relevant and realistic test cases. This approach would allow us to cover a wider range of scenarios and better assess the model’s performance across different types of queries.

##### Model Choice

We initially started the project using the GPT-4o-mini model, which appeared to be a solid choice based on its technical features, cost efficiency, and response time performance.

To evaluate output quality, GPT-4o-mini was compared with other models using a shared set of test queries, as previously discussed. The BIS team preferred the reasoning and responses generated by GPT-4o, leading to its selection at that stage.

More recently, following the release of updated models, a new round of comparisons was conducted. GPT-4.1 was ultimately chosen, offering good performance with slightly lower costs compared to GPT-4o.

*The tables below highlight the differences in terms of features between GPT-4o and GPT-4.1. We also report the average execution times we measured in our tests for the various LLM tasks described above.*

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/02/Screenshot-2025-05-26-alle-16.15.08.png?fit=1000%2C838&ssl=1)

## Future Works

##### Few-shots integration

We have started exploring the integration of few-shot examples by collecting meaningful and validated samples from domain experts for each dataflow. These examples are intended to be included in the prompt to guide the model’s behaviour more effectively. However, we have not yet assessed the actual impact on performance. Since including few-shot examples would significantly increase the number of tokens passed to the model — and therefore the cost — their effectiveness and cost-benefit trade-off need to be carefully evaluated before adoption.

##### Fine-tuning/distillation for the specific task

Our current project has demonstrated the feasibility and effectiveness of leveraging instruction-based large language models (LLMs) to address domain-specific tasks without requiring dedicated fine-tuning. However, for future development and optimisation, an important next step could involve fine-tuning a smaller language model or applying knowledge distillation techniques. By using a larger “teacher” model to guide a smaller “student” model, we could develop a lightweight, task-specialised model with improved inference speed and potentially higher performance on our specific use cases.

##### Enhanced Evaluation Framework

To improve robustness in the evaluation process, we plan to expand our test framework by enriching the query sets. This could involve both automated generation through LLMs and manual curation by domain experts. A more diverse and representative query set will allow for more accurate performance benchmarking and expose edge cases that may not be captured by the current test coverage.

##### UI Integration and User Feedback Collection

Integration of the current solution into the user interface and subsequent production release are planned in the near future. Following deployment, one potential direction could be the systematic collection of both explicit and implicit feedback from internal users, and eventually from public users once the system is publicly released. Establishing such a feedback loop would offer the opportunity to drive continuous improvement and better understand the system’s performance in real-world conditions.

## Need Help with this topic?​

If you're struggling with AI-powered Filter Assistant, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with AI-powered Filter Assistant, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)