---
title: 'From Natural Language to Structured Solr Queries using LLMs'
company: Sease
tag: 查询理解
date: 2024-08-16
url: https://sease.io/2024/08/from-natural-language-to-structured-solr-queries-using-llms.html
account: 
origin: harvest3-202607
---
Hi readers,

In this blog post, we explore the usage of AI, especially **Natural Language Processing techniques and Large Language Models** (LLMs), **to enhance Apache Solr data accessibility**.  
We propose translating natural language queries into structured Solr queries using LLM and metadata to improve search and user experience.  
We will explore the results of our experiments, examining both promising aspects and areas for improvement, and conclude with the steps necessary to bring such a project into production.

This blog post explores the topics discussed at [Berlin Buzzwords 2024](https://sease.io/2024/05/sease-at-berlin-buzzwords-2024.html). Here we aim to capture the essence and key points of our presentation, offering a comprehensive overview to those who could not attend the conference.

## What is a Large Language Model?

A Large Language Model (LLM) is an advanced type of artificial intelligence designed to understand and generate human-like text. These models are built using massive neural networks trained on vast amounts of text data. These models are typically based on two main tasks:  
**1. next-token-prediction  
2. masked-language-modeling**

![](https://i0.wp.com/sease.io/wp-content/uploads/2024/05/FosHjMmagAEFqEK.png?fit=571%2C432&ssl=1)

In the **next-token-prediction**, the model’s task is to predict the next term in a sequence given the previous terms.  
In the **masked-language-modeling**, the model predicts a missing term in a context where some terms are intentionally masked.  
Essentially, an LLM estimates the likelihood or probability of each possible word in its vocabulary and uses this probability to predict the next or missing term.  
During the pretraining phase, an LLM is fed an enormous amount of textual data—on the scale of the entire internet. This involves providing the model with vast numbers of documents and sentences, in which some terms are artificially hidden to create a training set aimed at predicting the next token. At the end of this phase, the result is a large mathematical model capable of predicting the probability of a word following another or a word appearing within a given text window.

The beauty of large language models lies in the fact that they can be fine-tuned for specific tasks, which means adjusting these deep neural networks to perform additional computations and making them capable of solving various types of problems (for example: **Following instructions**, Sentence similarity, Summarizing text, Creating content, Translating content and so on.)

In this blog post, we will focus on models fine-tuned for the “following instructions” task, commonly known as **instruct-based LLMs**.  
These models became particularly popular after the November 2022 launch of ChatGPT. They are a type of Large Language Model specifically trained to follow instructions provided by natural language prompts and therefore respond to specific user queries accurately (with natural language responses).  
This approach has gained significant popularity because it allows for versatile interactions with LLMs, making them highly effective in various applications.

## Use Case Overview

### Problem Statement

When dealing with **keyword-based searches** several problems could arise:

##### 1) Vocabulary Mismatch

This can occur when users’ intentions are expressed with different words or phrases that are not present in the vocabulary, resulting in a textual mismatch. Examples:  
– retrieval of false positives (i.e. irrelevant results)  
– false negative/zero result query (when failing to retrieve relevant results).

##### 2) Semantic similarity

This occurs when the search engine fails to recognise different words or phrases that have similar meanings. Example: “*How old are you?*” and “*What is your age?*“

##### 3) Disambiguation

This happens when a word or phrase has several meanings and the search engine is unable to determine which meaning the user wants.  
Example: “apple” can be a fruit or a brand

All the problems described above involve either expressing the same concept with different words or, conversely, expressing different concepts with the same words.  
There are two types of lexical solutions:

* **Manually curated**: Synonyms, Hypernyms, Hyponyms
* **Algorithmic**: Stemming, Lemmatization, Knowledge Base disambiguation

These solutions are expensive (because maintaining them manually requires significant resources) and do not guarantee high-quality results. It is easy for these solutions to become outdated and neglected over time. Additionally, manual updates can introduce inconsistencies, as changes may address specific issues but inadvertently cause new problems elsewhere.

### How to Exploit LLM Capabilities?

There are multiple ways to integrate LLMs with search (like RAG, Retrieval Augmented Generation, or Neural/Vector-based search), however, in this case, we have adopted and experimented with **Query/Document Expansion** and **Query Parsing.**

##### Query/Document Expansion

It can be generative or extractive.

###### Generative approach

The LLM is not given specific boundaries to expand the document or query. For example, we could ask the LLM to expand the document or query in various ways, expressing the same concepts or rephrasing them using different terms.  
This approach may be faster and less costly, but it may not always give optimal results because it does not constrain the expansion to known and relevant terms.

###### Extractive Approach

Involves giving the LLM specific boundaries. For example, we might provide a list of terms derived from index fields or popular search terms and ask the LLM to enrich the query/document using only those terms. This method guarantees a higher probability that the results will match the index.

##### Query Parsing

Another way to leverage LLMs in search is through query parsing, which involves **transforming a natural language query into a structured query.**

For example, consider the natural language query:  
*“**PM10 levels produced by****industries****in the****European Community in May 2015**”*

In our index, we might have fields such as country, pollutant, year, variable and so on.  
From a human perspective, it is relatively easy to assign query entities to the appropriate fields, due to our inherent understanding and knowledge.  
An LLM can be trained to perform this task by mapping each part of the query in natural language to the corresponding fields in the index. This process involves understanding the semantics of the query and accurately identifying and categorising each component. For example:

* The entity “European Community” is mapped to the field **Country**, resulting in the **“European Union (28 countries)#EU28#”** value
* “PM10” is identified as a pollutant (and assigned to the field **Pollutant**), resulting in the **“Particulates (PM10)#PM10#”** value
* The term “industries” is associated with the field **Variable**, resulting in the **“Total man-made emissions#TOT#|Industrial combustion#STAT\_COMB\_IND#”** value.
* The term “May” is mapped to the field **Time Period**, resulting in the **“Second trimester(Q2)”** value.
* The year “2015” would be assigned to the field **Year**.

### Real Case Application

We have been working with some of our clients to exploit an LLM to:

* **disambiguate** the meaning of a user’s natural language query
* **extract** the relevant information
* use the extracted information to **implement a structured Solr query**

Integrating a Large Language Model (LLM) with a search engine (like Apache Solr) can revolutionize user interactions. The primary idea is to allow users to express their search queries in natural language and leverage the LLM’s capability to understand its nuances and the structure of documents within the search index, thereby interpreting and converting these queries into structured ones using the index’s metadata. The LLM will play an intermediary role in enhancing user experience, working behind the scenes to discover relevant documents that might escape conventional search approaches.

## From Natural Language to Structured Queries

For our projects, we have designed the process using the components shown in the diagram below.  
Let’s take a look at each component involved:

![](https://lh7-us.googleusercontent.com/srdS4DMdrbODqFT1qOPAeMNhtPp6KIlt-ITUVMrULVBJWVXl-Klz-rGmDgU316tCEKsXPzDDNL0S_JbqBIwHVBk7dQmWE8X6DU3yBDOxbLSoXtTKhpbq81HjPRVA2CcVJZ7qJFjFpkiN8o8=s2048)

1. The **search API**, developed using Python and Flask, is the main component responsible for handling search requests from the user interface. It accepts a natural language query as input, delegates it to the appropriate APIs for subsequent processing, then builds a structured query, and returns a JSON containing the search results and the filters selected using a Large Language Model.
2. **Large Language Model:**as already mentioned, we used an instruction-based model as a large language model and explored the DSPY library to facilitate interaction with it (for more details on this library, see the following section). The library is used to process the request, generate an appropriate prompt as model input, and pass the response on to the search API.
3. **Apache Solr:**as a search engine we used Apache Solr. The Apache Solr API interacts with the Solr system (to fetch the required data or return the final search results) and delivers them to the search API.

### Architecture

The following architectural diagram illustrates the interaction and sequence of processes, highlighting how and in what order the system’s components interact with each other. Below, we provide a detailed explanation of the steps involved:

![](https://i0.wp.com/sease.io/wp-content/uploads/2029/01/Schermata-2024-05-23-alle-12.17.56.png?fit=800%2C398&ssl=1)

##### 1) FIELD/VALUES RETRIEVAL

The search API sends a request to Apache Solr to retrieve the list of fields and all possible values for each field.  
E.g.

```
				
					{"Topic":[
     "Economy#ECO#",
     "Agriculture#AGR#",
     "Government#GOV#", …],
"Dimension":[
     "Reference area",
     "Time period",
     "Unit of Measure",
     "Year", …],
"Reference Area":[
     "Australia#AUS#",
     "Austria#AUT#", …],
     etc……}
				
			
```

##### 2) USER QUERY

The search API receives search requests (natural language queries) from the user interface (UI).  
E.g.

```
				
					What were the sulfur oxide emissions in Australia in 2013?

				
			
```

##### 3) FILTER EXTRACTION

The search API sends an extractive request to the LLM, providing a dictionary of fields and their values. It asks the LLM to return a subset of the input dictionary containing the most relevant fields and their most relevant values based on the query (filters). In the prompt, we specify how the output should be formatted, including any constraints or specific criteria to be met (in our case a JSON representation):

```
				
					{
  'Topic': ["Environment#ENV#|Air and climate#ENV_AC#"],
  'Country': ["Australia#AUS#"],
  'Variable': ["Total man-made emissions#TOT#"],
  'Pollutant': ["Sulphur Oxides#SOX#"],
  'Year': '2013'
}
				
			
```

##### 4) QUERY REFORMULATION

The search API sends a generative request to the LLM, providing the natural language query and asking the model to return different or additional relevant terms, synonyms, and variations that convey the same meaning. This process, known as query reformulation, helps to improve the search results by expanding the query with multiple expressions of the same intent:

```
				
					['Sulfur dioxide emissions', 'Air pollution','Environmental impact','Fossil fuel combustion','Acid rain']
				
			
```

##### 5) STRUCTURED QUERY

The search API builds the structured Solr query using both the query reformulations and the fields returned by the LLM. It requests Solr to identify (and return) documents that match the selected fields and corresponding values specified by the LLM.  
Note that the query construction process itself is not described in detail in this blog post, as it is highly context-dependent and can be implemented in varying degrees of complexity. The focus is therefore on the construction of the query, rather than its optimisation for optimal performance and relevance:

```
				
					q= title:(Sulfur dioxide emissions Air ... Acid rain)OR topic:"Environment#ENV#|Air and climate#ENV_AC#" OR country:"Australia#AUS#"
OR variable:"Total man-made emissions#TOT#" OR Pollutant:"Sulphur Oxides#SOX#" OR 'Year': '2013'
				
			
```

##### 6) DOC RETRIEVAL

Finally, the search API sends to the UI the retrieved Solr search results:

```
				
					"response":{
  "numFound":1,
  "start":0,
  "numFoundExact":true,
  "docs":[{
    "Title":"Emissions of air pollutants",
    "Dimension":["Country", "Pollutant", "Variable", "Year"]
  }]
}
				
			
```

### DSPy Library

For our projects, we explored the DSPY library to facilitate interaction with the LLMs.

[DSPy](https://dspy-docs.vercel.app/docs/intro) is a framework designed to optimise the use of language models within complex systems.  
It automates the optimization of prompts and weights to improve integration and performance when language models are used one or multiple times within a pipeline.

Interesting aspects of the library:

* **Abstracts the program’s logic into composable modules**, isolating parameters (like LM prompts and weights) from the main program flow.
* **Introduces powerful optimizers**, which are advanced algorithms designed to dynamically adjust LM prompts and weights to optimize for a specific metric.
* Provides a more systematic and scalable approach, seamlessly **integrating language models and their prompts as optimizable components within a larger, adaptive system** capable of learning from data.

We used this library to**handle the requests to the LLM** and specified the behaviour we needed as a [Signature](https://dspy-docs.vercel.app/docs/building-blocks/signatures).  
As written on the documentation page it is “a declarative specification of input/output behaviour**of a DSPy module.** Signatures allow you to tell the LM *what* it needs to do, rather than specify *how* we should ask the LM to do it”.  
A signature called `ExtractRequest` was created to handle the task of extracting relevant field-value pairs from a JSON dictionary based on a given input text. This is how it was defined:

```
				
					class ExtractRequest(dspy.Signature):
"""Given an input text and a JSON dictionary of fields with a list of possible values for each field, extract from the dictionary the most relevant field-values pairs to the given input text. Return only the selected pairs in a JSON format"""

text = dspy.InputField(desc="The natural language query provided by the user")
dictionary = dspy.InputField(desc="A JSON dictionary of fields and their possible values")
selected_pairs = dspy.OutputField(desc="A JSON dictionary containing the most relevant fields with their most relevant values given the natural language query provided by the user")
				
			
```

Through the Signature, we defined the task the LLM has to solve, the inputs it needs to use (*text and dictionary*) and the expected output (*selected\_pairs*).  
DSPy exploits this information to automatically generate the prompt for each request.

**The library’s slogan is *“Programming – not prompting – Language models”*, but is it really as it suggests?!**

From our experience, this goal is partially achieved.  
It doesn’t seem possible to program the model entirely or achieve exactly what we want 100% of the time. It felt more like an effort to create the best possible prompt and then validate the results afterwards.  
Although the library incorporates a validation mechanism, it does not guarantee that it will always work. You can define the desired input and output type, but if the model responds differently, the validation process fails and there is no way to solve it. This means that it is not possible to predetermine what to do in every scenario.

***If anyone has had the opportunity to work on it more than us and wants to share their insights and findings, we are happy to discuss them!***

## Our Findings

##### Model Considerations

We must acknowledge that in selecting our model for this project, we did not opt for the most advanced option available for this task. Furthermore, we were unable to conduct additional evaluations or comparisons with alternative models. Time constraints and limited funding limited our ability to conduct more in-depth analyses.

We wanted to verify the use of Instructor LLM (out of the box) to perform these tasks, and we chose them for their **promising capabilities and quick implementation in practical applications**.

Moving forward, we plan to explore and analyze models specifically fine-tuned for our task. Additionally, we aim to conduct our fine-tuning to optimize model performance and carry out comprehensive model comparisons to ensure the best solution is used.

##### Promising Aspects

Our project experiments showcase the effectiveness of leveraging a large language model to improve the comprehension of queries:

– The task at hand is inherently challenging and complex, yet an out-of-the-box LLM achieves **promising results with a simple and fast implementation**. We are pleased with these early results, which underline the **model’s solid potential and adaptability**.

– Our findings demonstrate that LLMs can effectively **address the challenges of lexical matching** in keyword-based searches by mapping query terms to relevant content within a Solr collection.

E.g.  
**land of kangaroos   →  [Country] AUSTRALIA**  
**tobacco consumption   →    [Topic] RISK FACTORS FOR HEALTH**

– Another promising aspect is the potential to **leverage the explainability of the results**. The LLM response includes the expected result, i.e. the relevant fields and values, and additionally explains the reasoning behind its choices. This is thanks to the use of the *ChainOfThought* prompting technique that teaches the LLM to think step-by-step and reasoning before returning the output response. This could help us understand why certain fields and values were selected by the model or why it struggles to provide the correct answer, giving us the necessary information to achieve better results.

E.g.

```
				
					Reasoning: Let's think step by step in order to produce the selected_pairs.
We need to analyze the input text and identify keywords that match the fields and their possible values in the provided dictionary.
The input text is "cost per square meter for family houses in italy".
From this text, we can extract the following keywords and their potential related fields:
-   "cost per square meter": This suggests we are looking for a value related to pricing or valuation, possibly under fields like 'Priced unit' or 'Value'.
-   "family houses": This indicates the type of property, which could relate to fields like 'Real estate type'.
-   "italy": This is a location, which could relate to fields like 'Reference area' or 'Borrowers' country'.

Now, we will search the dictionary for fields that match these keywords and select the most relevant values for each field.
				
			
```

IDEA!!!!

The explainability snippets can also be displayed to the user, **integrating it as an “Assistant” feature**. This means a pre-filtering assistant that helps users pre-select filters and provides reasons for the chosen options. This tool will offer clear explanations for each recommended filter based on user input and goals, simplifying the selection process and enhancing the user experience.

### Limitations

During our experiments, we encountered a series of limitations that we would like to discuss in this section, along with proposing practical solutions that could be implemented to mitigate them. We have categorized these limitations into two types based on their nature: functional limitations and formal limitations.

#### FUNCTIONAL LIMITATIONS

Functional limitations involve the LLM’s difficulties in interpreting language and queries. They are related to the semantics, i.e. the model has to be able to understand what we are talking about, make the right connections and select fields and values that must be semantically related to the input terms/sequences of terms.

##### 1) Field Ambiguity in Value Similarity

Sometimes the LLM has difficulty distinguishing which field is relevant according to the user’s query when the two (or more) fields have similar values/meanings.

E.g.

**{ “Country“: [“All countries”, “Europe”, “G20”, “Asia”, “Morocco”, …],**  
**“Reporting Country“: [“All countries”, “Europe”, “G20”, “Asia”, “Morocco”, …] }**

##### 2) Expert Knowledge Field Identification

When the knowledge of an expert is required in addition to the query text, the LLM often has difficulty identifying the relevant fields. Unlike a domain expert, who can naturally associate the query terms with the appropriate fields and their values in the corpus, the LLM may not find these connections intuitive or easy to establish.  
E.g.

**– “Marginal lending facility rate”  →  [Reference Area] Europe**  
**– “IMU tax”  →  [Sector] Real Estate**

##### 3) Expected Field Value Retrieval Issue

Sometimes, the model is able to identify the relevant value for the given query (as evidenced by its reasoning process), but does not retrieve it in the final answer. The model claims that the value of the field in question is not present in the input dictionary, even though it actually is.  
E.g.

**User Query   →   green growth in Rabat**  
**Explainability → “Country”: This field includes values that specify different countries, and “Morocco“ would be the relevant value if it were listed, but it is not.**  
***EXPECTED FIELD (not selected):***  
**Country   →   [“All countries”, “Europe”, “G20”, “Asia”, “Morocco“, …]**

###### POSSIBLE SOLUTIONS

**– Improving the quality and the content of the input data to ensure clearer and more accurate processing by the LLM**The use of human-readable field names could facilitate their understanding and differentiation for the large language model: what is human-readable is also LLM-readable, for which reason you should avoid using abbreviations or strings that do not provide any meaningful information to a human or a large language model to further enhance clarity and comprehension.

E.g.

**– “HEDxkkgkqIr”   →   “Category”**  
**– “INST\_NON\_EDU”   →   “Non-educational institutions”**

**– Creating tailored prompts to address specific requests, ensuring accurate data extraction and generation**One option could be to add ambiguous/difficult examples (i.e. user query and expected results) to the prompt to help the model understand how to manage the inputs appropriately.

E.g.

**Few-shots prompting**

Alternatively, another option could be to **efficiently split a large prompt into smaller prompts**, providing the model with less information, thus making the task less complex and hoping for a more accurate response.

E.g.

**– One request for field selection**  
**– One request for field values selection**

– Potentially undertake **our own fine-tuning** to optimize model performance  
It could be a good solution to fine-tune the model for a specific scenario (e.g. financial sector).  
This way, we could provide the model with the extra knowledge required to better disambiguate the queries and perform domain-specific tasks more effectively.

#### FORMAL LIMITATIONS

Formal solutions are the LLM shortcomings in complying with:  
– **the problem definition/rules**: the problem is precisely defined, requiring no deviation from given parameters. It involves creating a second map from a first one, ensuring the keys and their corresponding values in the second map are exactly subsets of those in the first. Although this can be mathematically formalized, we currently define it “verbally”, leading to occasional misunderstandings by the LLM.  
– **the required output format**: a JSON is requested and a JSON response without comments or unusual formats is expected.

Here are some examples:

##### 1) The LLM invents the names of the returned fields

The model often generates incorrect field keys, i.e. the field name does not match the exact string provided in the input request (prompt) to the model.

E.g.

**INPUT MAP KEY = “Type of instruments”**  
**OUTPUT MAP KEY = “Instrument”**

##### 2) The LLM invents the value of the returned fields

The model often generates incorrect field values, i.e. the field values do not match the exact strings provided in the input request (prompt) to the model.

E.g.

**INPUT MAP VALUE = “Year”: “21st century”**  
**OUTPUT MAP VALUE = “Year”: “2000”**

##### 3) The LLM mixes up fields and values

Sometimes the model might incorrectly use a field’s value as a key (field name) or as the value of a different field. This generally occurs with fields that have similar names and may also be due to the long prompt provided to the model, which contains too much information and confuses the model.

E.g.

**– “Total emissions per capita”  is a possible value and not a field name**  
**– “European Union (28 countries)#EU28#”  is a valid value present in  “Country”  but not in the “Reference Area” field**

##### 4) The LLM doesn't always guarantee the desired output format

With some queries, it may happen that the model doesn’t return the required JSON format as output but it adds textual comments at will at the beginning, middle, or end of the JSON. In this case, in order to correctly parse the model responses, a specific study needs to be conducted to address unwanted textual comments in model responses and manage all the possible variations.

E.g.

```
				
					Selected Pairs:
```json
{
"Country": "Australia#AUS#", // land of kangaroos
"Pollutant": "Sulphur Oxides#SOX#",
"Year": "2013"
}
```
These pairs are chosen based on the keywords identified in the input text and the closest matching fields and values from the provided dictionary.

				
			
```

###### POSSIBLE SOLUTIONS

– We need to develop and implement additional **post-processing** strategies to validate, manage, and correct the content and format **of the LLM’s responses.**

– ***A more in-depth study of the DSPy library*** needs to be conducted in order to exploit all its available functionalities and determine whether it can meet our requirements and improve our results. In particular, there are still some features that deserve to be tested, such as **Assertions** (designed to automate the application of computational constraints to language models), **Typed Predictors** (a way to enforce the type constraints on the inputs and outputs of the fields), and **Optimizers** (for prompt optimization).

– The **integration of different libraries specialized for prompt management** and the implementation of different strategies should be evaluated. These could improve the quality of the LLM’s responses and ensure that the expected format is returned.

– ***Fine-tuning the model for the specific******task***: **Information** ***Extraction***. It involves fine-tuning it to accurately select data according to precise mathematical rules, ensuring that the selected subsets of keys and values conform to the given constraints without deviation.

## The Road to Production

Here is a list of what needs to be done (or optimised) to bring such a project into production (this is true for the time being but it may change in the future as these technologies are rapidly changing).

##### [UX] Design the user experience

First of all, we have to design the user experience.  
This involves consulting with the client to understand their preferences for integrating the LLM into their search engine. Two main approaches may be considered by the client:  
1) **AI Assistant to Filters**: use the LLM as an AI assistant that guides users in choosing the most suitable filters. Although the system may occasionally make mistakes, this approach can be considered an experimental feature with room for improvement.  
2) **Transparent Query Parsing:** use the LLM to parse queries behind the scenes without direct user interaction. This requires the system to be highly robust and error-free.

##### [LLM] Select the best model to date

The second aspect is investigating the current state of the art and **finalising the choice of the Large Language Model** (commercial, like OpenAI for example, or an **[open source Large Language Model](https://sease.io/2023/06/how-to-choose-the-right-large-language-model-for-your-domain-open-source-edition.html)**).  
Additionally, with the necessary budget, time, and data, it would be possible (and highly interesting) to **fine-tune promising models specifically for our task** and evaluate their performance.

##### [LLM] Refine the prompts according to the model

The prompt may vary depending on the model selected and must be adjusted accordingly to optimise it for the most accurate responses.

##### [LLM] Implement integration tests with the most common failures

We should start by analyzing example queries and debugging the LLM responses to identify problematic cases. By investigating these issues, we can refine the prompt/optimize the program to correct them. Specific integration tests, for each problematic case, will then be created.

##### [LLM] Study additional libraries

As LLM is a buzzword right now and the field is rapidly evolving, new libraries and tools are constantly emerging or will soon be available.  
Exploring and experimenting with additional libraries could provide significant benefits and help us achieve our goal of making the prompt more systematically programmed and automatically tuned. This approach aims to minimize the reliance on trial-and-error methods, ensuring a more efficient and effective process. The success of this will largely depend on the capabilities and flexibility of the available LLMs, as well as the compatibility and integration of these libraries with the model.

##### [Performance] Stress test the solution

Begin by testing the application in a development environment to thoroughly evaluate its performance. Once satisfied, these benchmarks should be repeated in an environment that closely resembles production (e.g. a staging environment). In addition, stress tests should be conducted to ensure that the application maintains adequate speed when handling large volumes. Only then we can be sure that our results accurately reflect real-world performance.

##### [Quality] Set up queries/expected documents

It is recommended to establish a comprehensive search quality evaluation that assesses a consistent set of queries. Evaluating queries individually might lead to optimizations beneficial for specific cases but fail to advance the general performance of the retrieval system. The evaluation procedure should include the creation of a consistent set of queries paired with a list of relevant results (Rating set), to measure the quality of the application effectively.

## Conclusion

Our exploration of the use of Large Language Models (LLM) to improve the accessibility of Apache Solr data has yielded promising results. By translating natural language queries into structured Solr queries with the help of LLM and metadata, we can significantly improve search functionality and user experience.

Our experiments have highlighted both the strengths and areas for improvement in this approach. We believe that with further refinement and development, these techniques can be effectively brought into production, offering substantial benefits to users.

Given the growing interest in this topic and our ongoing efforts, **we plan to publish more blog posts with updates and new solutions. Stay tuned**!

## Need Help With This Topic?​​

If you’re interested in knowing more about Natural Language Processing techniques and Large Language Models to enhance Apache Solr data accessibility, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're interested in knowing more about Natural Language Processing techniques and Large Language Models to enhance Apache Solr data accessibility, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)