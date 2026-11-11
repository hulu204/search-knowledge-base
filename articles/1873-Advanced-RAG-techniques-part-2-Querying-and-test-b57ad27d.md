---
title: 'Advanced RAG techniques part 2: Querying and testing'
company: Elastic
tag: RAG
date: 2024-08-15
url: https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Advanced RAG techniques part 2: Querying and testing

Discussing and implementing techniques which may increase RAG performance. Part 2 of 2, focusing on querying and testing an advanced RAG pipeline.

August 15, 2024

[Han Xiang Choong](/search-labs/author/han-xiang-choong)

[Vector Database](/search-labs/blog/category/vector-database)[AI](/search-labs/blog/category/ai)

Part of the series:

[Advanced RAG techniques](/search-labs/blog/series/advanced-rag-techniques)

In this series

Share

*All code may be found* [*in the Searchlabs repo, in the advanced-rag-techniques branch*](https://github.com/elastic/elasticsearch-labs/tree/advanced-rag-techniques/supporting-blog-content/advanced-rag-techniques)*.*

Welcome to Part 2 of our article on Advanced RAG Techniques! In [part 1 of this series](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-1), we set up, discussed, and implemented the data processing components of the advanced RAG pipeline:

![Advanced RAG pipeline](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt9a4691874a19d8da/6a170b3f47d49c99f22d8a24/72b51ba2ae5e5977b56e5b915674753d6cfd0e56-1440x840.jpg)

The RAG pipeline used by the author.

In this part, we're going to proceed with querying and testing out our implementation. Let's get right to it!

### Table of contents

* [Searching and retrieving, generating answers](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#searching-and-retrieving,-generating-answers)

  + [Enriching queries with synonyms](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#enriching-queries-with-synonyms)
  + [HyDE (Hypothetical Document Embedding)](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#hyde-hypothetical-document-embedding)
  + [Hybrid search](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#hybrid-search)
* [Experiments](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#experiments)

  + [Summary of results](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#summary-of-results)
  + [Test 1: Who audits Elastic?](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#test-1-who-audits-elastic)

    - [AdvancedRAG](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#advancedrag)
    - [SimpleRAG](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#simplerag)
  + [Test 2: total revenue 2023](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#test-2--total-revenue-2023)

    - [AdvancedRAG](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#advancedrag-1)
    - [SimpleRAG](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#simplerag-1)
  + [Test 3: What product does growth primarily depend on? How much?](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#test-3-what-product-does-growth-primarily-depend-on-how-much)

    - [AdvancedRAG](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#advancedrag-2)
    - [SimpleRAG](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#simplerag-2)
  + [Test 4: Describe employee benefit plan](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#test-4-describe-employee-benefit-plan)

    - [AdvancedRAG](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#advancedrag-3)
    - [SimpleRAG](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#simplerag-3)
  + [Test 5: Which companies did Elastic acquire?](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#test-5-which-companies-did-elastic-acquire)

    - [AdvancedRAG](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#advancedrag-4)
    - [SimpleRAG](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#simplerag-4)
* [Conclusion](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#conclusion)
* [Appendix](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#appendix)

  + [Prompts](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#prompts)

    - [RAG question answering prompt](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#rag-question-answering-prompt)
    - [Elastic query generator prompt](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#elastic-query-generator-prompt)
    - [Potential questions generator prompt](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#potential-questions-generator-prompt)
    - [HyDE generator prompt](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#hyde-generator-prompt)
  + [Sample hybrid search query](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2#sample-hybrid-search-query)

## Searching and retrieving, generating answers

Let's ask our first query, ideally some piece of information found primarily in the annual report. How about:

```
Who audits Elastic?"
```

Now, let's apply a few of our techniques to enhance the query.

### Enriching queries with synonyms

Firstly, let's enhance the diversity of the query wording, and turn it into a form that can be easily processed into an Elasticsearch query. We'll enlist the aid of GPT-4o to convert the query into a list of OR clauses. Let's write this prompt:

```
ELASTIC_SEARCH_QUERY_GENERATOR_PROMPT = '''
You are an AI assistant specialized in generating Elasticsearch query strings. Your task is to create the most effective query string for the given user question. This query string will be used to search for relevant documents in an Elasticsearch index.

Guidelines:
1. Analyze the user's question carefully.
2. Generate ONLY a query string suitable for Elasticsearch's match query.
3. Focus on key terms and concepts from the question.
4. Include synonyms or related terms that might be in relevant documents.
5. Use simple Elasticsearch query string syntax if helpful (e.g., OR, AND).
6. Do not use advanced Elasticsearch features or syntax.
7. Do not include any explanations, comments, or additional text.
8. Provide only the query string, nothing else.

For the question "What is Clickthrough Data?", we would expect a response like:
clickthrough data OR click-through data OR click through rate OR CTR OR user clicks OR ad clicks OR search engine results OR web analytics

AND operator is not allowed. Use only OR.

User Question:
[The user's question will be inserted here]

Generate the Elasticsearch query string:
'''
```

When applied to our query, GPT-4o generates synonyms of the base query and related vocabulary.

```
'audits elastic OR 
elasticsearch audits OR 
elastic auditor OR 
elasticsearch auditor OR 
elastic audit firm OR 
elastic audit company OR 
elastic audit organization OR 
elastic audit service'
```

In the `ESQueryMaker` class, I've defined a function to split the query:

```
def parse_or_query(self, query_text: str) -> List[str]:
    # Split the query by 'OR' and strip whitespace from each term
    # This converts a string like "term1 OR term2 OR term3" into a list ["term1", "term2", "term3"]
    return [term.strip() for term in query_text.split(' OR ')]
```

Its role is to take this string of OR clauses and split them into a list of terms, allowing us do a multi-match on our key document fields:

```
["original_text", 'keyphrases', 'potential_questions', 'entities']
```

Finally ending up with this query:

```
 'query': {
    'bool': {
        'must': [
            {
                'multi_match': {
                'query': 'audits Elastic Elastic auditing Elastic audit process Elastic compliance Elastic security audit Elasticsearch auditing Elasticsearch compliance Elasticsearch security audit',
                'fields': [
                    'original_text',
                'keyphrases',
                'potential_questions',
                'entities'
                ],
                'type': 'best_fields',
                'operator': 'or'
                }
            }
      ]
```

This covers many more bases than the original query, hopefully reducing the risk of missing a search result because we forgot a synonym. But we can do more.

[Back to top](#table-of-contents)

### HyDE (Hypothetical Document Embedding)

Let's enlist GPT-4o again, this time to implement [HyDE](https://arxiv.org/abs/2212.10496).

The basic premise of HyDE is to generate a hypothetical document - The kind of document that would likely contain the answer to the original query. The factuality or accuracy of the document is not a concern. With that in mind, let's write the following prompt:

```
HYDE_DOCUMENT_GENERATOR_PROMPT = '''
You are an AI assistant specialized in generating hypothetical documents based on user queries. Your task is to create a detailed, factual document that would likely contain the answer to the user's question. This hypothetical document will be used to enhance the retrieval process in a Retrieval-Augmented Generation (RAG) system.

Guidelines:
1. Carefully analyze the user's query to understand the topic and the type of information being sought.
2. Generate a hypothetical document that:
   a. Is directly relevant to the query
   b. Contains factual information that would answer the query
   c. Includes additional context and related information
   d. Uses a formal, informative tone similar to an encyclopedia or textbook entry
3. Structure the document with clear paragraphs, covering different aspects of the topic.
4. Include specific details, examples, or data points that would be relevant to the query.
5. Aim for a document length of 200-300 words.
6. Do not use citations or references, as this is a hypothetical document.
7. Avoid using phrases like "In this document" or "This text discusses" - write as if it's a real, standalone document.
8. Do not mention or refer to the original query in the generated document.
9. Ensure the content is factual and objective, avoiding opinions or speculative information.
10. Output only the generated document, without any additional explanations or meta-text.

User Question:
[The user's question will be inserted here]

Generate a hypothetical document that would likely contain the answer to this query:
'''
```

Since vector search typically operates on cosine vector similarity, the premise of HyDE is that we can achieve better results by matching documents to documents instead of queries to documents.

What we care about is structure, flow, and terminology. Not so much factuality. GPT-4o outputs a HyDE document like this:

```
'Elastic N.V., the parent company of Elastic, the organization known for developing Elasticsearch, is subject to audits to ensure financial accuracy, 
regulatory compliance, and the integrity of its financial statements. The auditing of Elastic N.V. is typically conducted by an external, 
independent auditing firm. This is common practice for publicly traded companies to provide stakeholders with assurance regarding the company\'s 
financial position and operations.\n\nThe primary external auditor for Elastic is the audit firm Ernst & Young LLP (EY). Ernst & Young is one of the 
four largest professional services networks in the world, commonly referred to as the "Big Four" audit firms. These firms handle a substantial number 
of audits for major corporations around the globe, ensuring adherence to generally accepted accounting principles (GAAP) and international financial 
reporting standards (IFRS).\n\nThe audit process conducted by EY involves several steps. Initially, the auditors perform a risk assessment to identify 
areas where misstatements due to error or fraud could occur. They then design audit procedures to test the accuracy and completeness of financial statements,
 which include examining financial transactions, assessing internal controls, and reviewing compliance with relevant laws and regulations. Upon completion of 
 the audit, Ernst & Young issues an audit report, which includes the auditor’s opinion on whether the financial statements are free from material misstatement 
 and are presented fairly in accordance with the applicable financial reporting framework.\n\nIn addition to external audits by firms like Ernst & Young, 
 Elastic may also be subject to internal audits. Internal audits are performed by the company’s own internal auditors to evaluate the effectiveness of internal 
 controls, risk management, and governance processes.\n\nOverall, the auditing process plays a crucial role in maintaining the transparency and reliability of 
 Elastic\'s financial information, providing confidence to investors, regulators, and other stakeholders.'
```

It looks pretty believable, like the ideal candidate for the kinds of documents we'd like to index. We're going to embed this and use it for hybrid search.

[Back to top](#table-of-contents)

### Hybrid search

This is the core of our search logic. Our lexical search component will be the generated OR clause strings. Our dense vector component will be embedded HyDE Document (aka the search vector). We use KNN to efficiently identify several candidate documents closest to our search vector. We call our lexical search component *Scoring with TF-IDF and BM25* by default. Finally, the lexical and dense vector scores will be combined using the 30/70 ratio recommended by [Wang et al](https://arxiv.org/abs/2407.01219).

```
def hybrid_vector_search(self, index_name: str, query_text: str, query_vector: List[float], 
                         text_fields: List[str], vector_field: str, 
                         num_candidates: int = 100, num_results: int = 10) -> Dict:
    """
    Perform a hybrid search combining text-based and vector-based similarity.

    Args:
        index_name (str): The name of the Elasticsearch index to search.
        query_text (str): The text query string, which may contain 'OR' separated terms.
        query_vector (List[float]): The query vector for semantic similarity search.
        text_fields (List[str]): List of text fields to search in the index.
        vector_field (str): The name of the field containing document vectors.
        num_candidates (int): Number of candidates to consider in the initial KNN search.
        num_results (int): Number of final results to return.

    Returns:
        Dict: A tuple containing the Elasticsearch response and the search body used.
    """
    try:
        # Parse the query_text into a list of individual search terms
        # This splits terms separated by 'OR' and removes any leading/trailing whitespace
        query_terms = self.parse_or_query(query_text)

        # Construct the search body for Elasticsearch
        search_body = {
            # KNN search component for vector similarity
            "knn": {
                "field": vector_field,  # The field containing document vectors
                "query_vector": query_vector,  # The query vector to compare against
                "k": num_candidates,  # Number of nearest neighbors to retrieve
                "num_candidates": num_candidates  # Number of candidates to consider in the KNN search
            },
            "query": {
                "bool": {
                    # The 'must' clause ensures that matching documents must satisfy this condition
                    # Documents that don't match this clause are excluded from the results
                    "must": [
                        {
                            # Multi-match query to search across multiple text fields
                            "multi_match": {
                                "query": " ".join(query_terms),  # Join all query terms into a single space-separated string
                                "fields": text_fields,  # List of fields to search in
                                "type": "best_fields",  # Use the best matching field for scoring
                                "operator": "or"  # Match any of the terms (equivalent to the original OR query)
                            }
                        }
                    ],
                    # The 'should' clause boosts relevance but doesn't exclude documents
                    # It's used here to combine vector similarity with text relevance
                    "should": [
                        {
                            # Custom scoring using a script to combine vector and text scores
                            "script_score": {
                                "query": {"match_all": {}},  # Apply this scoring to all documents that matched the 'must' clause
                                "script": {
                                    # Script to combine vector similarity and text relevance
                                    "source": """
                                    # Calculate vector similarity (cosine similarity + 1)
                                    # Adding 1 ensures the score is always positive
                                    double vector_score = cosineSimilarity(params.query_vector, params.vector_field) + 1.0;
                                    # Get the text-based relevance score from the multi_match query
                                    double text_score = _score;
                                    # Combine scores: 70% vector similarity, 30% text relevance
                                    # This weighting can be adjusted based on the importance of semantic vs keyword matching
                                    return 0.7 * vector_score + 0.3 * text_score;
                                    """,
                                    # Parameters passed to the script
                                    "params": {
                                        "query_vector": query_vector,  # Query vector for similarity calculation
                                        "vector_field": vector_field  # Field containing document vectors
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }

        # Execute the search request against the Elasticsearch index
        response = self.conn.search(index=index_name, body=search_body, size=num_results)
        # Log the successful execution of the search for monitoring and debugging
        logger.info(f"Hybrid search executed on index: {index_name} with text query: {query_text}")
        # Return both the response and the search body (useful for debugging and result analysis)
        return response, search_body
    except Exception as e:
        # Log any errors that occur during the search process
        logger.error(f"Error executing hybrid search on index: {index_name}. Error: {e}")
        # Re-raise the exception for further handling in the calling code
        raise e
```

Finally, we can piece together a RAG function. Our RAG, from query to answer, will follow this flow:

1. Convert Query to OR Clauses.
2. Generate HyDE document and embed it.
3. Pass both as inputs to Hybrid Search.
4. Retrieve top-n results, reverse them so that the most relevant score is the "most recent" in the LLM's contextual memory (Reverse Packing) Reverse Packing Example: Query: "Elasticsearch query optimization techniques" Retrieved documents (ordered by relevance): Reversed order for LLM context: By reversing the order, the most relevant information (1) appears last in the context, potentially receiving more attention from the LLM during answer generation.

   1. "Use bool queries to combine multiple search criteria efficiently."
   2. "Implement caching strategies to improve query response times."
   3. "Optimize index mappings for faster search performance."
   4. "Optimize index mappings for faster search performance."
   5. "Implement caching strategies to improve query response times."
   6. "Use bool queries to combine multiple search criteria efficiently."
5. Pass the context to the LLM for generation.

```
def get_context(index_name, 
                match_query, 
                text_query, 
                fields, 
                num_candidates=100, 
                num_results=20, 
                text_fields=["original_text", 'keyphrases', 'potential_questions', 'entities'], 
                embedding_field="primary_embedding"):

    embedding=embedder.get_embeddings_from_text(text_query)

    results, search_body = es_query_maker.hybrid_vector_search(
        index_name=index_name,
        query_text=match_query,
        query_vector=embedding[0][0],
        text_fields=text_fields,
        vector_field=embedding_field,
        num_candidates=num_candidates,
        num_results=num_results
    )

    # Concatenates the text in each 'field' key of the search result objects into a single block of text.
    context_docs=['\n\n'.join([field+":\n\n"+j['_source'][field] for field in fields]) for j in results['hits']['hits']]

    # Reverse Packing to ensure that the highest ranking document is seen first by the LLM.
    context_docs.reverse()
    return context_docs, search_body

def retrieval_augmented_generation(query_text):
    match_query= gpt4o.generate_query(query_text)
    fields=['original_text']

    hyde_document=gpt4o.generate_HyDE(query_text)

    context, search_body=get_context(index_name, match_query, hyde_document, fields)

    answer= gpt4o.basic_qa(query=query_text, context=context)
    return answer, match_query, hyde_document, context, search_body
```

Let's run our query and get back our answer:

```
According to the context, Elastic N.V. is audited by an independent registered public accounting firm, PricewaterhouseCoopers (PwC). 
This information is found in the section titled "report of independent registered public accounting firm," which states:

"We have audited the accompanying consolidated balance sheets of Elastic N.V. [...] / s / pricewaterhouseco."
```

Nice. That's correct.

[Back to top](#table-of-contents)

## Experiments

There's an important question to answer now. What did we get out of investing so much effort and additional complexity into these implementations?

Let's do a little comparison. The RAG pipeline we've implemented versus baseline hybrid search, without any of the enhancements we've made. We'll run a small series of tests and see if we notice any substantial differences. We'll refer to the RAG we have just implemented as AdvancedRAG, and the basic pipeline as SimpleRAG.

![Simple RAG Pipeline](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf605c8246989df32/6a1711178b73cbc61d18a11d/8da40067835ab8b4dc12fe52a51a6c26858ad32f-1440x1095.jpg)

Simple RAG Pipeline without bells and whistles

#### Summary of results

This table summarizes the results of five tests of both RAG pipelines. I judged the relative superiority of each method based on answer detail and quality, but this is a totally subjective judgement. The actual answers are reproduced below this table for your consideration. With that said, let's take a look at how they did!

SimpleRAG was unable to answer questions 1 & 5. AdvancedRAG also went into far greater detail on questions 2, 3, and 4. Based on the increased detail, I judged the quality of AdvancedRAG's answers better.

| Test | Question | AdvancedRAG Performance | SimpleRAG Performance | AdvancedRAG Latency | SimpleRAG Latency | Winner |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Who audits Elastic? | Correctly identified PwC as the auditor. | Failed to identify the auditor. | 11.6s | 4.4s | AdvancedRAG |
| 2 | What was the total revenue in 2023? | Provided the correct revenue figure. Included additional context with revenue from previous years. | Provided the correct revenue figure. | 13.3s | 2.8s | AdvancedRAG |
| 3 | What product does growth primarily depend on? How much? | Correctly identified Elastic Cloud as the key driver. Included overall revenue context & greater detail. | Correctly identified Elastic Cloud as the key driver. | 14.1s | 12.8s | AdvancedRAG |
| 4 | Describe employee benefit plan | Gave a comprehensive description of retirement plans, health programs, and other benefits. Included specific contribution amounts for different years. | Provided a good overview of benefits, including compensation, retirement plans, work environment, and the Elastic Cares program. | 26.6s | 11.6s | AdvancedRAG |
| 5 | Which companies did Elastic acquire? | Correctly listed recent acquisitions mentioned in the report (CmdWatch, Build Security, Optimyze). Provided some acquisition dates and purchase prices. | Failed to retrieve relevant information from the provided context. | 11.9s | 2.7s | AdvancedRAG |

#### Test 1: Who audits Elastic?

AdvancedRAG

```
According to the context, Elastic N.V. is audited by an independent 
registered public accounting firm, PricewaterhouseCoopers (PwC). 
This information is found in the section titled "report of 
independent registered public accounting firm," which states:
"We have audited the accompanying consolidated balance sheets 
of Elastic N.V. [...] / s / pricewaterhouseco."
```

SimpleRAG

```
According to the provided context, no specific auditing firm 
or company is mentioned as the auditor for Elastic. 
The context provided talks about various features, strengths, 
deployment options, and other details related to Elastic and 
its operations but does not specify which auditing firm is 
responsible for auditing Elastic's financial statements or 
internal controls.
```

**Summary**: SimpleRAG did not identify PWC as the auditor

Okay that's actually quite surprising. That looks like a search failure on SimpleRAG's part. No documents related to auditing were retrieved. Let's dial down the difficulty a little with the next test.

#### Test 2: total revenue 2023

AdvancedRAG

```
### Total Revenue for 2023

According to the provided context, the total revenue for the 
year ended April 30, 2023, was **$1,068,989,000**. This 
information can be found several times in the provided text. 
Specifically, one part states:

"The following table sets forth our results of operations 
for the periods presented in dollars and as a percentage of 
our total revenue. ... year ended April 30, 2023, ... 
total revenue 1,068,989".

Additionally, it is mentioned here as well:

"For the years ended April 30, 2023, 2022, and 2021, 
representing year-over-year growth of 24% for the year 
ended April 30, 2023... total revenue $1,068,989".

Therefore, the total revenue for 2023 is $1.069 billion.
```

SimpleRAG

```
According to the context provided, the total revenue for the fiscal year ended April 30, 2023, is:

$1,068,989,000 (or approximately $1.1 billion).
```

**Summary**: Both RAGs got the right answer: $1,068,989,000 total revenue in 2023

Both of them were right here. It does seem like AdvancedRAG may have acquired a broader range of documents? Certainly the answer is more detailed and incorporates information from previous years. That is to be expected given the enhancements we made, but it's far too early to call.

Let's raise the difficulty.

#### Test 3: What product does growth primarily depend on? How much?

AdvancedRAG

```
### Product Growth Primarily Depends On:
According to the context, "our revenue is derived primarily from 
subscriptions of search, observability and security built into 
the elastic stack." The document mentions various strategies and 
factors contributing to the company’s growth which include investment 
in "elastic cloud," "elastic stack," and the conversion of free 
users to paid subscribers.

### Quantitative Data:
- **Revenue**: The document states, "Our total revenue was $1.1 billion, 
$862.4 million, and $608.5 million for the years ended April 30, 2023, 
2022, and 2021, respectively."
- **Subscription Revenue**: "Subscriptions accounted for 92%, 93%, 
and 93% of our total revenue for the years ended April 30, 2023, 
2022, and 2021, respectively."
- **Elastic Cloud Contribution**: "For the years ended April 30, 2023, 
2022, and 2021, Elastic Cloud contributed 40%, 35%, and 27% of our 
total revenue, respectively."
- **Customer Growth**: The number of customers increased from 
"over 15,000 as of April 30, 2021," to "approximately 20,200 as of 
April 30, 2023."

### Summary:
Product growth for the company primarily depends on the "Elastic Stack" 
(which includes search, observability, and security solutions) and 
particularly the "Elastic Cloud." The Elastic Cloud's growing contribution 
to revenue highlights its significance, which grew from 27% in 2021 to 40% in 2023.
```

SimpleRAG

```
According to the provided context, growth primarily depends on **Elastic Cloud**, 
which is described as the company's "family of cloud-based offerings." 
The context also emphasizes the significance of Elastic Cloud in achieving 
the company's long-term growth potential and its role in increasing subscription revenue.

From the context:

- "Increasing adoption of Elastic Cloud... is an important growth opportunity 
for our business. Organizations are increasingly looking for hosted 
deployment alternatives with reduced administrative burdens."
- "We believe that offering Elastic Cloud is important for achieving 
our long-term growth potential, and we expect Elastic Cloud’s contribution 
to our subscription revenue to continue to increase."

In terms of the contribution to total revenue, here are the specific figures provided:

- Elastic Cloud contributed 40% of the total revenue for the year ended April 30, 2023.
- Elastic Cloud contributed 35% of the total revenue for the year ended April 30, 2022.
- Elastic Cloud contributed 27% of the total revenue for the year ended April 30, 2021.

This progression shows a clear upward trend in the importance and 
contribution of Elastic Cloud to the company's overall revenue.
```

**Summary**: Both RAGs correctly identified Elastic Cloud as the key growth driver. However, AdvancedRAG includes more detail, factoring in subscription revenues and customer growth, and explicitly mentions other Elastic offerings.

#### Test 4: Describe employee benefit plan

AdvancedRAG

```
### Employee Benefit Plan Overview

The provided context outlines various elements of the employee benefit plan at 
Elastic, often referred to as "Elasticians." Here are the key components 
described in the texts:

1. **401(k) Plan**:
   - **Coverage**: The 401(k) plan is available to substantially all U.S. 
   employees who meet minimum age and service requirements.
   - **Contributions**: Elastic makes contributions to the 401(k) plan up to 
   6% of the participating employee’s W-2 earnings and wages.
   - **Expenses**: For the fiscal years ended April 30, Elastic recorded 
   expenses of $17.9 million (2023), $15.2 million (2022), and $11.4 million (2021) 
   related to the 401(k) plan.
   - **Defined-Contribution Plans in Other Countries**: Elastic has 
   defined-contribution plans in various other countries and recorded respective 
   expenses of $9.4 million (2023), $7.2 million (2022), and $5.1 million (2021).

2. **Stock-Based Compensation**:
   - **Types of Awards**: Stock options, restricted stock units (RSUs), 
   and shares under the Employee Stock Purchase Plan (ESPP).
   - **Fair Value Measurement**: Fair value of these stock awards is 
   measured using models like Black-Scholes.
   - **Employee Stock Purchase Plan (2022 ESPP)**: 
     - Started in 2022, it allows employees to acquire ordinary 
     shares at a discount (85% of the market value at the beginning 
     or end of the offering period).
     - Offering periods are approximately six months long.

3. **Total Rewards Compensation**:
   - **Components**: Includes cash compensation as well as equity awards, 
   reflecting a comprehensive interest in the well-being of the employees.
   - **Programs**: Market competitive medical and dental programs, 
   mental health, and holistic well-being programs.
   - **Paid Time Off**: Features 16 weeks of paid leave for new 
   parents and life-planning benefits.

4. **Retirement and Income Protection Plans**:
   - **401(k) Match**: Elastic provides a dollar-for-dollar 
   match up to 6% of eligible earnings up to a plan-limit 
   maximum for U.S.-based employees.
   - **Similar Plans Outside the U.S.**: Competitive retirement 
   plans available for employees based outside the United States.

5. **Flexible Work Environment**: 
   - **Distributed Workforce**: Elastic operates with a global 
   distributed workforce model, allowing employees to work remotely 
   and providing a broad candidate pool.
   
6. **Learning and Development**:
   - **Programs**: Access to on-demand video-based learning, 
   leadership development programs, and other specific training 
   to develop managers and leaders.

7. **Employee Engagement and Surveys**:
   - **Mechanisms**: Annual employee engagement survey and 
   mid-year pulse survey.
   - **Objectives**: To monitor morale, develop action plans, 
   and maintain high engagement scores.

8. **Onboarding Program**:
   - **X-School**: An extensive new-hire orientation program to 
   help new employees meet peers and learn about the company's 
   products and solutions.

In summary, Elastic's employee benefit plan encompasses a broad 
spectrum of financial, health, well-being, and professional development 
benefits designed to support and enhance the lives of its employees. 
The plan is both competitive and comprehensive, aiming to attract,
retain, and engage its global workforce.
```

SimpleRAG

```
The employee benefit plan at the Company includes several key 
components aimed at enhancing the overall well-being and 
professional development of employees, referred to as "Elasticians." 

1. **Compensation and Benefits:**
   - The Company provides market-competitive compensation 
   packages which typically include cash compensation and equity awards.
   - Comprehensive medical and dental programs are offered, 
   emphasizing mental health and holistic well-being.
   - Paid time off programs feature:
     - 16 weeks of paid leave for new parents.
     - Life-planning benefits.
     - Travel reimbursements for certain healthcare services.

2. **Retirement and Income Protection Plans:**
   - In the United States, employees are eligible for a 401k 
   plan with a dollar-for-dollar match by the Company up to 6% 
   of eligible earnings, subject to a plan limit.
   - Similar competitive retirement and income protection plans 
   are available for employees outside the United States.

3. **Work Environment:**
   - The Company offers a flexible work environment, allowing most 
   employees to work from anywhere as often as they would like.
   - Physical offices around the world are available for employees 
   who prefer to work on-site or need a space for face-to-face interactions.

4. **Community Involvement:**
   - The Elastic Cares Program supports charitable organizations 
   that matter to employees on both local and global levels.
   - The program includes:
     - Donation matching.
     - Providing the Company's technology for free to certain 
     nonprofit organizations.
     - Volunteer time off initiative.
```

**Summary**: AdvancedRAG goes into much greater depth and detail, mentioning the 401K plan for US-based employees, as well as defining contribution plans outside of the US. It also mentions Health and Well-Being plans but misses the Elastic Cares program, which SimpleRAG mentions.

#### Test 5: Which companies did Elastic acquire?

AdvancedRAG

```
Elastic acquired several companies over the years to enhance its 
technology and market presence. According to the provided context, 
the specific acquisitions include:

1. **CmdWatch Security Inc.**: Acquired on September 17, 2021. 
The total purchase consideration was $77.8 million.
2. **Build Security Ltd.**: Acquired on September 2, 2021. The 
combined purchase price for Build Security Ltd. and another acquisition was $57.2 million.
3. **Optimyze Cloud Inc.**: Acquired on November 1, 2021. Part 
of the combined purchase price mentioned above with Build Security Ltd.
4. **Endgame, Inc.**: Although the context mentions an amended 
and restated stock incentive plan, it indicates that Endgame, Inc. was 
associated with Elastic, suggesting it could have been acquired at some point.

These acquisitions are part of Elastic's strategy to 
enhance the technology underlying its security and 
observability offerings.
```

SimpleRAG

```
The provided context does not specify any companies that Elastic has acquired. 
Therefore, based on the context, there is no information available about the companies acquired by Elastic.
```

**Summary**: SimpleRAG does not retrieve any relevant info about acquisitions, leading to a failed answer. AdvancedRAG correctly lists CmdWatch, Build Security, and Optimyze, which were the key acquisitions listed in the report.

[Back to top](#table-of-contents)

## Conclusion

Based on our tests, our advanced techniques appear to increase the range and depth of the information presented, potentially enhancing quality of RAG answers.

Additionally, there may be improvements in reliability, as ambiguously worded questions such as `Which companies did Elastic acquire?` and `Who audits Elastic` were correctly answered by AdvancedRAG but not by SimpleRAG.

However, it is worth keeping in perspective that in 3 out of 5 cases, the basic RAG pipeline, incorporating Hybrid Search but no other techniques, managed to produce answers that captured most of the key information.

We should note that due to the incorporation of LLMs at the data preparation and query phases, the latency of AdvancedRAG is generally between 2-5x larger that of SimpleRAG. This is a significant cost which may make AdvancedRAG suitable only for situations where answer quality is prioritized over latency.

The significant latency costs can be alleviated using a smaller and cheaper LLM like Claude Haiku or GPT-4o-mini at the data preparation stage. Save the advanced models for answer generation.

This aligns with the findings of Wang et al. As their results show, any improvements made are relatively incremental. In short, simple baseline RAG gets you most of the way to a decent end-product, while being cheaper and faster to boot. For me, it's an interesting conclusion. For use cases where speed and efficiency are key, SimpleRAG is the sensible choice. For use cases where every last drop of performance needs squeezing out, the techniques incorporated into AdvancedRAG may offer a way forward.

![Wang Pipeline](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt56b7067a9d41d5a8/6a171119acf0886fb4be9c45/ea811706b6adc4731d90b925a9fefa0ac15901b4-1440x1060.jpg)

Results of the study by Wang et al reveal that the use of advanced techniques creates consistents but incremental improvements.

[Back to top](#table-of-contents)

## Appendix

### Prompts

#### RAG question answering prompt

Prompt for getting the LLM to generate answers based on query and context.

```
BASIC_RAG_PROMPT = '''
You are an AI assistant tasked with answering questions based primarily on the provided context, while also drawing on your own knowledge when appropriate. Your role is to accurately and comprehensively respond to queries, prioritizing the information given in the context but supplementing it with your own understanding when beneficial. Follow these guidelines:

1. Carefully read and analyze the entire context provided.
2. Primarily focus on the information present in the context to formulate your answer.
3. If the context doesn't contain sufficient information to fully answer the query, state this clearly and then supplement with your own knowledge if possible.
4. Use your own knowledge to provide additional context, explanations, or examples that enhance the answer.
5. Clearly distinguish between information from the provided context and your own knowledge. Use phrases like "According to the context..." or "The provided information states..." for context-based information, and "Based on my knowledge..." or "Drawing from my understanding..." for your own knowledge.
6. Provide comprehensive answers that address the query specifically, balancing conciseness with thoroughness.
7. When using information from the context, cite or quote relevant parts using quotation marks.
8. Maintain objectivity and clearly identify any opinions or interpretations as such.
9. If the context contains conflicting information, acknowledge this and use your knowledge to provide clarity if possible.
10. Make reasonable inferences based on the context and your knowledge, but clearly identify these as inferences.
11. If asked about the source of information, distinguish between the provided context and your own knowledge base.
12. If the query is ambiguous, ask for clarification before attempting to answer.
13. Use your judgment to determine when additional information from your knowledge base would be helpful or necessary to provide a complete and accurate answer.

Remember, your goal is to provide accurate, context-based responses, supplemented by your own knowledge when it adds value to the answer. Always prioritize the provided context, but don't hesitate to enhance it with your broader understanding when appropriate. Clearly differentiate between the two sources of information in your response.

Context:
[The concatenated documents will be inserted here]

Query:
[The user's question will be inserted here]

Please provide your answer based on the above guidelines, the given context, and your own knowledge where appropriate, clearly distinguishing between the two:
'''
```

#### Elastic query generator prompt

Prompt for enriching queries with synonyms and converting them into the OR format.

```
ELASTIC_SEARCH_QUERY_GENERATOR_PROMPT = '''
You are an AI assistant specialized in generating Elasticsearch query strings. Your task is to create the most effective query string for the given user question. This query string will be used to search for relevant documents in an Elasticsearch index.

Guidelines:
1. Analyze the user's question carefully.
2. Generate ONLY a query string suitable for Elasticsearch's match query.
3. Focus on key terms and concepts from the question.
4. Include synonyms or related terms that might be in relevant documents.
5. Use simple Elasticsearch query string syntax if helpful (e.g., OR, AND).
6. Do not use advanced Elasticsearch features or syntax.
7. Do not include any explanations, comments, or additional text.
8. Provide only the query string, nothing else.

For the question "What is Clickthrough Data?", we would expect a response like:
clickthrough data OR click-through data OR click through rate OR CTR OR user clicks OR ad clicks OR search engine results OR web analytics

AND operator is not allowed. Use only OR.

User Question:
[The user's question will be inserted here]

Generate the Elasticsearch query string:
'''
```

#### Potential questions generator prompt

Prompt for generating potential questions, enriching document metadata.

```
RAG_QUESTION_GENERATOR_PROMPT = '''
You are an AI assistant specialized in generating questions for Retrieval-Augmented Generation (RAG) systems. Your task is to analyze a given document and create 10 diverse questions that would effectively test a RAG system's ability to retrieve and synthesize information from this document.

Guidelines:
1. Thoroughly analyze the entire document.
2. Generate exactly 10 questions that cover various aspects and levels of complexity within the document's content.
3. Create questions that specifically target:
   a. Key facts and information
   b. Main concepts and ideas
   c. Relationships between different parts of the content
   d. Potential applications or implications of the information
   e. Comparisons or contrasts within the document
4. Ensure questions require answers of varying lengths and complexity, from simple retrieval to more complex synthesis.
5. Include questions that might require combining information from different parts of the document.
6. Frame questions to test both literal comprehension and inferential understanding.
7. Avoid yes/no questions; focus on open-ended questions that promote comprehensive answers.
8. Consider including questions that might require additional context or knowledge to fully answer, to test the RAG system's ability to combine retrieved information with broader knowledge.
9. Number the questions from 1 to 10.
10. Output only the ten questions, without any additional text, explanations, or answers.

Document:
[The document content will be inserted here]

Generate 10 questions optimized for testing a RAG system based on this document:
'''
```

#### HyDE generator prompt

Prompt for generating hypothetical documents using HyDE

```
HYDE_DOCUMENT_GENERATOR_PROMPT = '''
You are an AI assistant specialized in generating hypothetical documents based on user queries. Your task is to create a detailed, factual document that would likely contain the answer to the user's question. This hypothetical document will be used to enhance the retrieval process in a Retrieval-Augmented Generation (RAG) system.

Guidelines:
1. Carefully analyze the user's query to understand the topic and the type of information being sought.
2. Generate a hypothetical document that:
   a. Is directly relevant to the query
   b. Contains factual information that would answer the query
   c. Includes additional context and related information
   d. Uses a formal, informative tone similar to an encyclopedia or textbook entry
3. Structure the document with clear paragraphs, covering different aspects of the topic.
4. Include specific details, examples, or data points that would be relevant to the query.
5. Aim for a document length of 200-300 words.
6. Do not use citations or references, as this is a hypothetical document.
7. Avoid using phrases like "In this document" or "This text discusses" - write as if it's a real, standalone document.
8. Do not mention or refer to the original query in the generated document.
9. Ensure the content is factual and objective, avoiding opinions or speculative information.
10. Output only the generated document, without any additional explanations or meta-text.

User Question:
[The user's question will be inserted here]

Generate a hypothetical document that would likely contain the answer to this query:
'''
```

### Sample hybrid search query

```
{'knn': {'field': 'primary_embedding',
  'query_vector': [0.4265527129173279,
   -0.1712949573993683,
   -0.042020395398139954,
   ...],
  'k': 100,
  'num_candidates': 100},
 'query': {'bool': {'must': [{'multi_match': {'query': 'audits Elastic Elastic auditing Elastic audit process Elastic compliance Elastic security audit Elasticsearch auditing Elasticsearch compliance Elasticsearch security audit',
      'fields': ['original_text',
       'keyphrases',
       'potential_questions',
       'entities'],
      'type': 'best_fields',
      'operator': 'or'}}],
   'should': [{'script_score': {'query': {'match_all': {}},
      'script': {'source': '\n                                        double vector_score = cosineSimilarity(params.query_vector, params.vector_field) + 1.0;\n                                        double text_score = _score;\n                                        return 0.7 * vector_score + 0.3 * text_score;\n                                        ',
       'params': {'query_vector': [0.4265527129173279,
         -0.1712949573993683,
         -0.042020395398139954,
        ...],
        'vector_field': 'primary_embedding'}}}}]}},
 'size': 10}
```

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