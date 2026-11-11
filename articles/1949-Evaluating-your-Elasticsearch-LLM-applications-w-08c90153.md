---
title: 'Evaluating your Elasticsearch LLM applications with Ragas'
company: Elastic
tag: 评测
date: 2025-08-21
url: https://www.elastic.co/search-labs/blog/elasticsearch-ragas-llm-app-evaluation
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Evaluating your Elasticsearch LLM applications with Ragas

Assessing the quality of a RAG solution using Ragas metrics and Elasticsearch.

August 21, 2025

[Jessica Garson](/search-labs/author/jessica-garson)

[Python](/search-labs/blog/category/python-programming)[AI](/search-labs/blog/category/ai)

Jump to

Share

[Ragas](https://docs.ragas.io/en/stable/) is an evaluation framework that enables you to gain a deeper understanding of how your LLM applications are performing. It provides established metrics and scoring to create a quantitative analysis of your LLM application’s overall performance. Evaluation frameworks, such as Ragas, reveal issues in LLM systems and provide standardized metrics to guide enhancements and pinpoint where potential issues may be.

Using a framework like Ragas is helpful since it can help eliminate the guesswork of working with LLM systems and enable you to measure and improve upon past performance. It can be helpful for letting you know if your application is prone to hallucination in certain areas, or if your application is generating answers or if your retrieval is pulling irrelevant information.

This blog post guides you through an example of assessing the quality of a Retrieval-Augmented Generation (RAG) solution using Ragas metrics and Elasticsearch. You can find the full code and related resources on [GitHub](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/using-ragas-with-elasticsearch).

## Overview of the solution

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt318527fec3c6ccdd/6a17efc425daab3bd908a323/bc3adf341af1019f9e31c8e6bf6c3f28437cb789-1341x1038.png)

The solution, discussed in this blog post, first uploads a dataset from a JSON file into Elasticsearch. The dataset used is [books.json](https://github.com/JessicaGarson/Using-Ragas-with-Elasticsearch/blob/main/books.json), a subset of 25 books from Goodreads, including the book title, the author's name, book description, publication year, and a Goodreads URL.

After the book data is loaded, the next step is to store the index with vector embeddings in Elasticsearch. You can then create evaluation questions and use them to retrieve the relevant context through vector search.

Once the contexts are retrieved for each question, you can generate both answers and ground truths. Ground truths are essentially ideal answers. Using GPT-4o, you can create answers based on the retrieved context, while a separate function will generate ground truths applying scoring logic to rank and select the most relevant books from the retrieved results, generating recommendations that can serve as the evaluation benchmark. Basically, attempting to figure out what you are really looking for, trying to find a response that is the best match, and explaining to you the reason why.

Finally, you'll evaluate performance by comparing the generated answers against the ground truths using Ragas metrics and viewing the results.

## Prerequisites

* The version of Python that is used is Python 3.12.1, but you can use any version of Python higher than 3.10.
* This example uses Elasticsearch version 9.0.3, but you can use any version of Elasticsearch that is higher than 8.10.
* You will need an OpenAI API Key, which you can find on the API keys page in [OpenAI's developer portal](https://platform.openai.com/api-keys).
* You will also need a base level of knowledge regarding vector databases and RAG. If you aren’t already familiar with vector search concepts in Elastic, you may want to first check out the following resources:

  + [Our documentation on RAG](https://www.elastic.co/docs/solutions/search/rag)
  + [Navigating an Elastic Vector Database](https://www.elastic.co/search-labs/blog/elastic-vector-database-practical-example)
  + [The big ideas behind retrieval augmented generation](https://www.elastic.co/blog/retrieval-augmented-generation-explained)

## Metrics

The metrics used in this example are context precision, faithfulness, and context recall.

* [Context precision](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_precision/) refers to the relevance of the generated answer to the actual question or topic, measuring the proportion of the retrieved context used in the answer that is actually relevant to answering the question.
* [Faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/) is a way to determine if your LLM is hallucinating and indicates the accuracy of the generated answer.
* [Context recall](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/context_recall/#llm-based-context-recall) measures how many of the relevant documents were successfully retrieved, focusing on not missing important results.
* For `context_precision`, high precision scores mean that the generated answer is found in the context. High scores for faithfulness mean the generated answer is accurate and aligns with the reference. High scores for `context_recall` mean the generated answer uses all or most of the relevant context.

The reason these three metrics were chosen is that they provide an actionable signal about both retriever and generator performance. They allow you to determine if your RAG system retrieved the right things, answer what you retrieved, and assess if your answer is correct or supported.

These are only three of the available metrics from Ragas. You can learn more about other metrics available in the [Ragas documentation](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/#agents-or-tool-use-cases).

## Setting up

You will first want to install the packages required for this application. These include the following:

* The [Elasticsearch Python client](https://www.elastic.co/docs/reference/elasticsearch/clients/python) – helpful for authenticating and connecting to Elasticsearch and for vector search.
* [Ragas](https://docs.ragas.io/en/stable/) – used for evaluating the quality of the LLM applications using standard metrics.
* The Hugging Face library [datasets](https://huggingface.co/docs/datasets/en/index) – used to create a robust evaluation dataset.
* [Langchain-OpenAI](https://python.langchain.com/api_reference/openai/llms/langchain_openai.llms.base.OpenAI.html) – used both for generating answers to user questions and for evaluation.

```
!pip install -q elasticsearch ragas datasets langchain-openai
```

After installing the required packages, you can now import `os`, which you be using for setting environment variables and other related tasks, `json` for parsing a JSON file containing books, `getpass` for passing in sensitive values like API keys and tokens, the Elasticsearch Python client, `ragas` for evaluation, and `ragas.metrics` for the metrics used to evaluate the rag application, as well as datasets for creating an evaluation dataset and `langchain_openai` for model chat capabilities.

```
import os
import json
from getpass import getpass
from elasticsearch import Elasticsearch
from ragas import evaluate
from ragas.metrics import faithfulness, context_recall, context_precision
from datasets import Dataset
from langchain_openai import ChatOpenAI
```

## Creating the Elasticsearch index and vector search

Now, you will want to create a variable called `es`, where you can pass in your Elasticsearch host address and your Elasticsearch API key.

```
es = Elasticsearch(
   getpass("Host: "),
   api_key=getpass("API Key: "),
)
```

You will also need to create a variable called `index_name` that can be set to whatever name you want to give your index. For this example, you can name your index ragas-books.

```
index_name = "ragas-books"
```

To add vector embeddings to the dataset, you will want to create a function that takes a query string and turns it into a vector using the Elastic machine learning model .`multilingual-e5-small-x86_64`. Be sure to check out our [documentation on E5](https://www.elastic.co/docs/explore-analyze/machine-learning/nlp/ml-nlp-e5) models to learn more. If you run into any issues, you may need to [deploy the model](https://www.elastic.co/docs/explore-analyze/machine-learning/nlp/ml-nlp-deploy-model) first before the code can run properly.

```
def embed_query(text: str):
  
   res = es.ml.infer_trained_model(
       model_id=".multilingual-e5-small_linux-x86_64",
       body={"docs": [{"text_field": f"query: {text}"}]}
   )
  
   vec = res["inference_results"][0]["predicted_value"]
  
   return vec
```

Now, you should check if you have an existing index with the same name. If you do, you will delete the older index. After that, you can create a new index with the proper mappings. Since the dataset used is a snippet of books from Goodreads, the mappings will match the headers from that example.

```
if es.indices.exists(index=index_name):
   es.indices.delete(index=index_name)
   print(f"Deleted existing index '{index_name}'")

es.indices.create(index=index_name, body={
   "mappings": {
       "properties": {
           "book_title": {"type": "text"},
           "author_name": {"type": "text"},
           "book_description": {"type": "text"},
           "rating_score": {"type": "float"},
           "embedding": {
               "type": "dense_vector",
               "dims": 384,
               "index": True,
               "similarity": "cosine"
           }
       }
   }
})
print(f"Created index '{index_name}'")
```

At this point, you will want to extract the data from the `books.json` file, loop through it, generate an embedding for the book descriptions, and load that into the Elasticsearch index. Since the original dataset contains book title, the author's name, book description, publication year, and a Goodreads URL, the book description is the best candidate for generating embeddings because it contains meaning beyond keywords. You can check out this [Linkedin post](https://www.linkedin.com/posts/ashishtiwari93_not-every-field-in-your-json-document-is-activity-7356927125980905472-dtSt?utm_source=share&utm_medium=member_desktop&rcm=ACoAAA1aSysBfU-WAyaUfqKgpJanCsFtyVhbacs) to learn more about what fields are good candidates for semantic search.

While it’s possible to generate embeddings from multiple fields such as title and description, using the description alone is a more simple approach that avoids noise from a shorter field like title. There is a tradeoff since you may miss some title-specific matches.

```
with open("books.json") as f:
   books = json.load(f)

for i, book in enumerate(books, 1):
   try:
       book["embedding"] = embed_query(book["book_description"])
       es.index(index=index_name, document=book)
       print(f"Indexed {i}: {book['book_title']}")
   except Exception as e:
       print(f"Failed to index '{book.get('book_title', 'Unknown')}': {e}")
```

Now that the data is loaded into Elasticsearch, you can create a function called `vector_search` to perform a k-nearest neighbors (KNN) search. 3 was chosen for the `top_k` value, since it is how many nearest-neighbor context chunks are retrieved from Elasticsearch for each question. It tends to be small enough to keep context relevant. Still, large enough to give the model multiple options and avoid missing something due to retrieval errors. `top_k` is a value that could be adjusted if you are seeing that your results aren't accurate results from your RAG application. To learn more about what K value to choose, be sure to check out our [blog post](https://www.elastic.co/search-labs/blog/elasticsearch-knn-and-num-candidates-strategies) on the subject.

This function first generates an embedding for the input query using the `embed_query` function. It performs the search on the specified index, returns the results, and creates a context based on the book title. Finally, it returns both the text contexts for RAG and the metadata for the books.

```
def vector_search(query, top_k=3):
  
   query_vector = embed_query(query)
  
   body = {
       "knn": {
           "field": "embedding",
           "k": top_k,
           "num_candidates": 100,
           "query_vector": query_vector
       },
       "_source": ["book_title", "author_name", "book_description", "rating_score"]
   }
  
   res = es.search(index=index_name, body=body)
   hits = res["hits"]["hits"]
   contexts, books_info = [], []
  
   for hit in hits:
       book = hit["_source"]
       context = f"{book['book_title']} by {book['author_name']}: {book['book_description']}"
       contexts.append(context)
       books_info.append(book)
  
   return contexts, books_info
```

## Implementing the RAG generation component

At this point, you will want to check if an environment variable is set for your OpenAI API Key, and if not, you will want to put one using getpass.

After obtaining the OpenAI API Key, you can create a variable called `chat_llm` that will be used for RAG, which calls ChatOpenAI with the model you want to use, the `temperature` which controls the randomness/creativity of the LLM’s output (lower values tend to be a safer choice), and your OpenAI API key. While this example is using `gpt-4o`, you can easily change the model to another by adjusting the parameter model=”model name”.

```
if "OPENAI_API_KEY" not in os.environ:
   os.environ["OPENAI_API_KEY"] = getpass("OPENAI_API_KEY: ")

API_KEY = os.environ["OPENAI_API_KEY"]

chat_llm = ChatOpenAI(
   model="gpt-4o",
   temperature=0.1,
   api_key=API_KEY
)
```

Next, you can create a function called `generate_answer` that first joins the context strings into a single block of text. After, you can make a prompt that instructs the LLM only to use the provided context, and give that prompt to the LLM to get the response. After, you'll need to strip the whitespace from that response. This function represents the generation in RAG.It plays a key role when using Ragas to evaluate the quality of generated answers.

```
def generate_answer(question, contexts):
  
   context_text = "\n\n".join(contexts)
  
   prompt = f"""You are a helpful assistant that recommends books.
Use only the information from the context below to answer the question.
Do not include any books, authors, or details that are not explicitly present in the context.

Repeat the exact book title and author from the context in your answer.

Context:
{context_text}

Question:
{question}

Answer:"""
   response = chat_llm.invoke(prompt)
  
   return response.content.strip()
```

Before you can create ground truths that represent a known correct answer, you can use a function that extracts intent patterns and other key attributes from user questions. The function `analyze_question_intent` is designed to identify genres, extract quality preferences, and determine whether the question is author-specific from book-related data.

```
def analyze_question_intent(question):
    question_lower = question.lower()
    
    intent_patterns = {
        'genre_specific': {
            'science fiction': ['science fiction', 'sci-fi', 'space', 'future', 'alien', 'technology'],
            'fantasy': ['fantasy', 'magic', 'dragon', 'wizard', 'medieval', 'kingdom'],
            'mystery': ['mystery', 'detective', 'crime', 'murder', 'investigation', 'thriller'],
            'romance': ['romance', 'love', 'relationship', 'romantic'],
            'horror': ['horror', 'scary', 'ghost', 'supernatural', 'fear'],
            'historical': ['historical', 'history', 'war', 'period', 'ancient'],
            'biography': ['biography', 'memoir', 'life story', 'autobiography'],
            'non-fiction': ['non-fiction', 'nonfiction', 'factual', 'real', 'educational']
        },
        'quality_indicators': {
            'high_rating': ['high rating', 'highly rated', 'best rated', 'top rated', 'excellent'],
            'popular': ['popular', 'bestseller', 'well-known', 'famous', 'acclaimed'],
            'award_winning': ['award', 'prize', 'winner', 'acclaimed', 'celebrated'],
            'classic': ['classic', 'timeless', 'masterpiece', 'legendary'],
            'recent': ['recent', 'new', 'latest', 'modern', 'contemporary']
        },
        'author_focus': ['author', 'writer', 'by', 'written by']
    }
    
    detected_genres = []
    for genre, keywords in intent_patterns['genre_specific'].items():
        if any(keyword in question_lower for keyword in keywords):
            detected_genres.append(genre)
    
    quality_preferences = []
    for quality_type, keywords in intent_patterns['quality_indicators'].items():
        if any(keyword in question_lower for keyword in keywords):
            quality_preferences.append(quality_type)
    
    author_focused = any(keyword in question_lower for keyword in intent_patterns['author_focus'])
    
    return {
        'genres': detected_genres,
        'quality_preferences': quality_preferences,
        'author_focused': author_focused,
        'question_lower': question_lower,
        'genre_keywords': intent_patterns['genre_specific']
    }
```

You will also want to score a book against a user’s query based on intent data. You will get back a numeric score, where the higher the score means a better match, a list of reasons explaining the score and the book’s rating and metadata.

```
def calculate_book_score(book, intent_data):
    score = 0
    reasons = []
    
    rating = float(book.get('rating_score', 0))
    score += rating * 10
    
    book_title = book.get('book_title', '').lower()
    book_desc = book.get('book_description', '').lower()
    author_name = book.get('author_name', '')
    
    for genre in intent_data['genres']:
        genre_keywords = intent_data['genre_keywords'][genre]
        if any(keyword in book_desc or keyword in book_title for keyword in genre_keywords):
            score += 30
            reasons.append(f"matches {genre} genre")
            break
    
    if 'high_rating' in intent_data['quality_preferences'] and rating >= 4.0:
        score += 20
        reasons.append("high rating")
    
    if 'popular' in intent_data['quality_preferences'] and len(book_desc) > 200:
        score += 15
        reasons.append("comprehensive description suggests popularity")
    
    if intent_data['author_focused'] and author_name:
        score += 10
        reasons.append("has clear author attribution")
    
    stop_words = ['a', 'an', 'the', 'is', 'are', 'what', 'can', 'you', 'me', 'i', 'book', 'books']
    question_words = [word for word in intent_data['question_lower'].split() if word not in stop_words]
    
    desc_matches = sum(1 for word in question_words if word in book_desc)
    if desc_matches > 0:
        score += desc_matches * 5
        reasons.append(f"description matches {desc_matches} key terms")
    
    return {
        'book': book,
        'score': score,
        'reasons': reasons,
        'rating': rating
    }
```

To create ground truths, you will want to begin by setting up a fallback option if no books are found. If books are available, it selects the top-ranked result and generates a recommendation based on the detected intent. It will prioritize genre matches first, then high rating preferences, then popularity preferences, followed by author-specific requests. If none of these apply, it falls back to a general recommendation. This function will favor higher-rated books when possible and it will include a second book as an additional suggestion if its score is close to the top book’s score.

While the function below is a good starting point since it uses retrieval context rather than external knowledge, applies business logic such as rating preferences and genre matching, and generates consistent, reasonable responses, manually generating ground truths won’t scale well. In production environments, you would want to consider having your ground truths be semi-automated with human review, or LLM-generated with validation.

```
def generate_ground_truth_response(top_books, intent_data):
    if not top_books:
        return "No relevant books found."
    
    top_book = top_books[0]
    book = top_book['book']
    title = book['book_title']
    author = book['author_name']
    rating = top_book['rating']
    
    detected_genres = intent_data['genres']
    quality_preferences = intent_data['quality_preferences']
    author_focused = intent_data['author_focused']
    
    if detected_genres:
        genre = detected_genres[0]
        if 'high_rating' in quality_preferences or rating >= 4.0:
            response = f"For a highly-rated {genre} book, I recommend '{title}' by {author} (rating: {rating:.1f})."
        else:
            response = f"A good {genre} book from the available options is '{title}' by {author}."
    
    elif 'high_rating' in quality_preferences:
        response = f"Among the highest-rated books available, '{title}' by {author} stands out with a {rating:.1f} rating."
    
    elif 'popular' in quality_preferences:
        response = f"'{title}' by {author} appears to be a popular choice based on the comprehensive information available."
    
    elif author_focused:
        response = f"I recommend '{title}' by the author {author}."
    
    else:
        if rating >= 4.0:
            response = f"I recommend '{title}' by {author}, which has a strong rating of {rating:.1f}."
        else:
            response = f"Based on the available books, '{title}' by {author} would be a good choice."
    
    if len(top_books) > 1 and top_books[1]['score'] > top_books[0]['score'] * 0.8:
        second_book = top_books[1]['book']
        response += f" You might also consider '{second_book['book_title']}' by {second_book['author_name']}."
    
    return response
```

## Running the demo

Finally, you are now ready to run the demo. This function is similar to a `main` function, where it ties all the other functions together to generate an evaluation. First, you will define some demo questions to evaluate the RAG application. After that, you can initialize the lists and loop through each question. After looping through each question, you want to generate an answer using the retrieved context and create ground truths using the best-matching books. Next, you will collect the data for evaluation and create a dataset for Ragas evaluation. Once the evaluation dataset is created, you can run the evaluation, print the results, and save them to a CSV file.

```
def run_ragas_demo():
   print("🚀 Demo:\n")

   demo_questions = [
       "What's a good science fiction book with high ratings?",
       "Can you suggest a fantasy book by a popular author?",
       "What's a highly rated mystery novel?",
       "Recommend a book with good reviews"
   ]

   questions, contexts_list, answers, ground_truths = [], [], [], []

   for i, question in enumerate(demo_questions, 1):
       print(f"\n📚 Question {i}: {question}")
      
       try:
           contexts, books_info = vector_search(question, top_k=3)
           if not contexts:
               print(f"No contexts found for question {i}")
               continue
              
           answer = generate_answer(question, contexts)
           print(f"Answer: {answer[:100]}...")
           ground_truth = create_dynamic_ground_truth(question, books_info)
           print(f"Ground Truth: {ground_truth}")
           questions.append(question)
           contexts_list.append(contexts)
           answers.append(answer)
           ground_truths.append(ground_truth)
          
       except Exception as e:
           print(f"Error processing question {i}: {e}")
           continue

   if not questions:
       print("\nNo valid Q&A pairs generated.")
       return None

   eval_dataset = Dataset.from_dict({
       "question": questions,
       "contexts": contexts_list,
       "answer": answers,
       "ground_truth": ground_truths,
   })

   print("\n✨ Running Ragas evaluation...")
   try:
       result = evaluate(
           dataset=eval_dataset,
           metrics=[context_precision, faithfulness, context_recall],
           llm=chat_llm,
           embeddings=None
       )
      
       df = result.to_pandas()
      
       print("\n✨ Ragas Evaluation Results:")
       print(df)
      
       print("\✨ Averages:")
      
       for metric, value in df.mean(numeric_only=True).items():
           print(f"{metric}: {value:.3f}")
          
       df.to_csv("ragas_evaluation.csv", index=False)
       print("\nResults saved to 'ragas_evaluation.csv'")
       return result
      
   except Exception as e:
       print(f"Ragas evaluation failed: {e}")
       return None
```

Finally, we can run the demo with some additional error handling.

```
try:
    results = run_ragas_demo()
    if results:
        print("\n🎉 Demo completed successfully!")
    else:
        print("\nDemo completed with issues.")
        
except Exception as e:
    print(f"\nError during demo: {e}")
    import traceback
    traceback.print_exc()
```

## Examining the output

In LLM applications, scores above 0.8 on these metrics typically show strong performance, but this could differ depending on the dataset, domain, and use case. More information on each metric is available in the [documentation](https://docs.ragas.io/en/stable/concepts/metrics/overview/#metric-design-principles).

In the output below, the average `faithfulness` score is 0.750, indicating that most answers generally remained consistent with the retrieved context. The `context_recall` average of 0.500 shows that the system retrieved enough information for a complete answer only half the time. Meanwhile, the `context_precision` average of 0.625 suggests that a fair portion of the generated content directly matched the retrieved context, but there’s still room for improvement.

When you take a look at the individual questions, both Question 0 and Question 3 scored well on both faithfulness and context precision. This shows an alignment between retrieval and generation. Question 1 had strong recall but only moderate precision, which means that some details were likely added beyond the retrieved context. Question 2 scored low on both precision and recall, showing gaps in retrieval and that the generated content drifted away from the provided context.

To improve these results, you could focus on enhancing retrieval quality by experimenting with different embedding models, refining chunking strategies, or applying context engineering to better match user queries. On the generation side, using stricter prompts and other prompt engineering tactics could be helpful in reducing hallucination, and ensuring that evaluation ground truths are tightly aligned with retrieved content will lead to more accurate scoring.

```
✨ Ragas Evaluation Results:
                                          user_input  \
0  What's a good science fiction book with high r...   
1  Can you suggest a fantasy book by a popular au...   
2               What's a highly rated mystery novel?   
3                 Recommend a book with good reviews   

                                  retrieved_contexts  \
0  [Light of the Jedi by Charles Soule: Two hundr...   
1  [Alien Warrior's Mate by Vi Voxley: He's damn ...   
2  [The Island of Doctor Moreau by H.G. Wells: Ra...   
3  [The Island of Doctor Moreau by H.G. Wells: Ra...   

                                            response  \
0               "Light of the Jedi" by Charles Soule   
1              The Book of Time by Guillaume Prévost   
2                   "Human Nature" by Jonathan Green   
3  "The Island of Doctor Moreau" by H.G. Wells is...   

                                           reference  context_precision  \
0  For a highly-rated science fiction book, I rec...                1.0   
1  A good fantasy book from the available options...                0.5   
2  For a highly-rated mystery book, I recommend '...                0.0   
3  Based on the available books, 'The Island of D...                1.0   

   faithfulness  context_recall  
0           1.0             0.0  
1           0.5             1.0  
2           0.5             0.0  
3           1.0             1.0  
\✨ Averages:
context_precision: 0.625
faithfulness: 0.750
context_recall: 0.500

Results saved to 'ragas_evaluation.csv'

🎉 Demo completed successfully!
```

## Common challenges with evaluation frameworks like Ragas

While evaluation frameworks such as Ragas can serve as useful baselines, they are only guidelines and are designed to be part of a broader evaluation strategy rather than definitive measures of system quality.

There are some common issues with evaluation frameworks, which include overly simplistic ground truths that don't provide the whole picture, small sample sizes, and problems with circularity with LLMs evaluating LLMs.

Additionally, there is sometimes a disconnect between evaluation results and actual performance in the real world. Systems that achieve high evaluation scores may perform inconsistently in actual user scenarios and uncommon situations. Frameworks such as this one can focus heavily on specific dimensions such as factual accuracy or relevance while potentially underweighting others, like user experience, response latency, or handling of ambiguous queries.

To mitigate these challenges, you may want to explore A/B testing with real users, using human-in-the-loop reviews or LLM-as-a-judge ensembles as a way of reducing evaluator bias.

## Next steps

The example in this blog post is a starting point for working with Ragas. There are also some key considerations to think about for adapting a solution like this at scale:

* Regularly re-index your content in Elasticsearch whenever the source data changes
* Use a broad, realistic evaluation set to track real-world performance
* Measure and optimize your system’s speed and cost at production scale to avoid bottlenecks or budget issues.

## Conclusion

Using evaluation methods, such as the Ragas framework, can help you determine if your LLM application is performing as intended and provide a sense of its accuracy. It can help guide you in deciding whether to pivot to another model if it's not performing as well as expected, and can be used for side-by-side comparisons of different models to evaluate how well each model works for your purposes.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltf69e1ba73bd5d402/6a6a340599442cd9e0df1d94/1794a179d9536e693a0982634da59aff209c9d68-1280x720.png)

[Analytics](/search-labs/blog/category/analytics)[ES|QL](/search-labs/blog/category/esql)[Python](/search-labs/blog/category/python-programming)

### How to instrument your search API with OpenTelemetry and query it with ES|QL

July 22, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltd05627be20e89dfb/6a17d7c6414c640256944fdb/de886289dcb56494920875303b622b030b9b810f-720x420.jpg)

[Python](/search-labs/blog/category/python-programming)[ES|QL](/search-labs/blog/category/esql)

### Elasticsearch geospatial search with ES|QL

August 12, 2024|[Craig Taverner](/search-labs/author/craig-taverner)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltb1808f6b0c1b0ed3/6a17d7bcec0f89c6c35a644e/1b32822c3bf2ad216b21d819c5795f080b6e6cbf-500x500.png)

[ES|QL](/search-labs/blog/category/esql)[Python](/search-labs/blog/category/python-programming)

### From ES|QL to native Pandas dataframes in Python

September 05, 2024|[Quentin Pradet](/search-labs/author/quentin-pradet)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9d9912c8d4187096/6a1704f5b0367d30e672bc17/54a6e5197f5721b36fc65f27387d29803ed35589-721x420.jpg)

[ML Research](/search-labs/blog/category/ml-research)[Python](/search-labs/blog/category/python-programming)

### Evaluating search relevance part 1 - The BEIR benchmark

July 16, 2024|[Thanos Papaoikonomou](/search-labs/author/thanos-papaoikonomou)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1acb1d84387a6310/6a17d7726df7314a250a0d48/274867ef7971390c5d1d4f535c76e50a9f4a8224-1206x1522.png)

[ES|QL](/search-labs/blog/category/esql)[Python](/search-labs/blog/category/python-programming)

### An Elasticsearch Query Language (ES|QL) analysis: Millionaire odds vs. hit by a bus

August 20, 2024|[Baha Azarmi](/search-labs/author/baha-azarmi)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter