---
title: 'Evaluating Solr Vector Search with Quepid'
company: Sease
tag: 评测
date: 2024-10-02
url: https://sease.io/2024/10/evaluating-solr-vector-search-with-quepid.html
account: 
origin: harvest3-202607
---
Hi, information retrieval enthusiasts,

here we are with a blog post about vector search and how to evaluate it.

We explore a practical way to evaluate the performance of vector search in Apache Solr.   
Evaluating this advanced search technology presents unique challenges and often requires creative approaches due to the lack of direct support in existing evaluation tools, such as Quepid.

For this reason, we developed a workaround using a Python script and the [Static Search API](https://opensourceconnections.com/blog/2024/02/08/quepid-features-2023/) recently integrated in Quepid. Throughout this blog, we demonstrate how to effectively use this method to evaluate Solr vector search queries, providing a practical example that you can replicate or adapt to your needs (and search engine!).

A solid and automatic way to measure search engine performance across a set of queries is crucial for understanding and improving search functionality.

## Example Scenario

Suppose to have a *book e-commerce* environment and the goal is to evaluate the effectiveness of the vector search approach before deploying the solution in a production setting.

To reproduce this example scenario, we have used a small portion of a public book dataset that can be found [here](https://github.com/scostap/goodreads_bbe_dataset/tree/main/Best_Books_Ever_dataset) [1].   
The dataset was adjusted to include only specific fields and a defined number of documents; we indexed 10,000 documents in an Apache Solr collection called “books,” selecting these fields:  
**id**, **title**, **author**, **genres**, **description**, and **coverImg** (i.e. URL to cover image).

Since the description is the field with the most content, we decided to encode it into the corresponding **embeddings** using a pre-trained model called [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) (in our previous blog post, you can find Python scripts on [how to generate vectors from text and index them in Apache Solr](https://sease.io/2023/01/apache-solr-neural-search-tutorial.html).)   
These embeddings are then stored in the new field called ***vector\_description***, which serves as a [dense vector field](https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html) for our search.

It is important to note that of all the fields listed above, only the **description** and therefore the ***vector\_description*** is used for vector search. The other fields are only used for document identification and not for searching.

## Actual Limitations

As an evaluation tool, we use [Quepid](https://quepid.com/), an open source tool designed to improve the effectiveness of search applications. It offers a user-interface-driven approach to interact directly with results from Apache Solr (or other search engines), evaluate them by collecting human relevance judgements and use them to generate overall metrics.

At present, it does not yet support vector search with Solr, i.e. there is no direct and immediate way to evaluate it because it does not allow you to configure post query parameters dynamically (and thus pass vectors).

It is also important to remember that Solr cannot currently perform inferences, so each natural language query must be externally encoded and then the resulting vector embeddings must be copied and pasted into Quepid cases.

It is still possible to use Quepid to evaluate vector search, but with a manual system that is rather “cumbersome” and has some limitations:

**1)** Since each textual query has a unique vector, it needs to be entered in the “Add query” block, but as you can see from the following screenshot, this does not seem to work –> you can see it loading but it gets stuck and nothing happens.

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/12/Schermata-2024-05-09-alle-09.37.21.png?fit=1014%2C129&ssl=1)

**2)** The only alternative is therefore to define the query, i.e. the vector, hard-coded in the “Query Sandbox”, as shown here:

![](https://i0.wp.com/sease.io/wp-content/uploads/2024/05/Schermata-2024-05-08-alle-12.27.31-copia.png?fit=453%2C283&ssl=1)

However, this approach introduces additional limitations:  
**–** defining it hard-coded will require different cases for different queries, otherwise, the query in the Sandbox would be the same for all text queries. For example, as illustrated in the image below, the vector input into the “Query Sandbox” corresponds to the text query *“I am looking for science fiction books”*; however, for the query *“I want to read books on personal development”* we will have another vector, which requires the creation of a new case to include it:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/12/Schermata-2024-05-14-alle-15.37.05.png?fit=1909%2C395&ssl=1)

**–** depending on the length of the query (and vector), a “`URI too long`” error may occur. The only way to bypass the issue is to increase the **`requestHeaderSize`**value in the Solr **`server/etc/jetty.xml`** file or to support ***Solr JSON Query API*** as already mentioned [here](https://github.com/o19s/quepid/issues/780) by my colleague [Anna Ruggero](https://sease.io/about/anna-ruggero).

**So, how did we manage the evaluation in an automatic and more easily reproducible way?!**

Executing Solr requests separately using a Python script (and the `pysolr` library) and taking advantage of the new Static Search API integrated into Quepid.

## Static Search API / CSV Static File

As written in Quepid: *“a Static (or Offline) search endpoint is a great way to gather human judgements and leverage Quepid’s existing evaluation tools without requiring a live connection to a search engine.*“

This API involves creating and uploading a CSV file, also called “CSV Static File”. This is the file of queries and document results that you want to evaluate using the Quepid tooling. You can upload that static file and interact with it as if a real search engine was responding.

The CSV file should include headers as follows: **Query Text, Doc ID, Doc Position**, followed by any additional document fields you wish to display. Each of these fields should be represented as columns, with the header reflecting the name of the field. Here is an example:

```
				
					Query Text,Doc ID,Doc Position,BookTitle
star wars,527641,1,Star Wars
star wars,9426,2,Star Wars: The Empire Strikes Back
star wars,1921,3,Star Wars: Return of the Jedi
				
			
```

**So why is using this CSV file the best solution to overcome the current limitation?**

Using this CSV file is considered a good solution to overcome current limitations because it allows for the external definition and execution of queries and their results, centralizing everything needed for evaluation in one case.   
This method is highly adaptable and compatible with any search engine, making it invaluable in environments where access to full databases or the internet is restricted.   
It provides a straightforward way to test search capabilities across different platforms without needing complex infrastructure.

## Example Procedure

**Prerequisites**

To replicate this approach, the prerequisites are as follows:

* A Solr collection with a field that stores the embeddings to perform vector searches (Solr >= 9.0)
* [Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository): required because Quepid is launched using Docker Compose.
* [Quepid](https://github.com/o19s/quepid/wiki/Installation-Guide#installation-procedure): install it on your machine, customize your setup and start Quepid app.
* [Python](https://www.python.org/downloads/): to implement the Python script that performs the Solr vector searches across a list of queries, collect the results and create a CSV file to be uploaded to Quepid

##### 1) Create a List of Queries To Evaluate

It is considered ideal to establish a comprehensive evaluation procedure that includes the evaluation of a consistent set of queries. Evaluating individual queries in isolation might lead to optimizations that work well for specific queries but do not necessarily improve the overall retrieval system’s performance. The selected set of queries must reflect the variety of potential searches that users might conduct on the search engine, thereby providing a more accurate, mediated measure of the system’s effectiveness across different scenarios.

###### How to choose queries?

* **Real Data**: identify important queries from the business and keep track of popular queries the user performs (from search logs).
* **Special Cases**: include some very specific or rare queries to see how your system handles less common situations.
* **Variety**: make sure you have a balanced mix of query types so that you are not biased towards one type.

This blog post aims to showcase the method, and since the quality of the queries isn’t crucial, we simply created a dozen natural language queries for evaluation and saved them in a CSV file.

##### 2) Create the CSV Static File using Python

Instead of directly using Quepid to perform vector searches, we used a Python script designed to interact with an Apache Solr instance.  
The script’s purpose is to process a list of natural language queries, convert them into vector embeddings using a Sentence Transformer model, and then use these embeddings to perform k-Nearest Neighbor (k-NN) searches in Solr. The results are then formatted and saved to a CSV file:

```
				
					import sys
import pysolr
from sentence_transformers import SentenceTransformer
import pandas as pd

# Solr configuration ("books" collection)
SOLR_ADDRESS = 'http://localhost:8983/solr/books'
# Create a client instance
SOLR_INSTANCE = pysolr.Solr(SOLR_ADDRESS, always_commit=True)

def query_embedding(query_text):
    # Load or create a SentenceTransformer model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    # Compute sentence embedding
    embedding = model.encode(query_text)
    vector_embedding = list(embedding)
    return vector_embedding

def add_quepid_fields(df, query, doc_position):
    # The Quepid CSV file should have the headers: Query Text,Doc ID,Doc Position. Then, all the document fields you want displayed follow as columns with the header being the name of the field.
    df["Query Text"] = query
    df["Doc Position"] = doc_position
    df.rename(columns={'id': 'Doc ID'}, inplace=True)
    return df

if __name__ == "__main__":
    # Processes command-line arguments to get the query input file path and output folder
    query_input_file = sys.argv[1]
    output_csv_folder = sys.argv[2]

    # Reads a list of natural language queries from the input CSV file
    query_list = pd.read_csv(query_input_file)

    df_per_query = []
 
    # Iterate over each natural language query
    for query_string in query_list["Query"]:
        # Generate the query vector
        query_vector = query_embedding(query_string)
        # Perform k-NN search on the vector_description field using the query vector
        knn_query = f'{{!knn f=vector_description topK=10}}{query_vector}'
        additional_params = {
            'rows': 10,
            'fl': "id,title,author,genres,coverImg"
        }
        knn_solr_response = SOLR_INSTANCE.search(knn_query, **additional_params)
        df_knn = pd.DataFrame(knn_solr_response)
        # Add the required fields for Quepid
        df_quepid = add_quepid_fields(df_knn, query_string, range(1, len(df_knn) + 1))
        df_per_query.append(df_quepid)

    df_final = pd.concat(df_per_query, ignore_index=True)
    # Save the final dataframe to a CSV
    df_final.to_csv(output_csv_folder + "/csv_for_quepid.csv", index=False)
				
			
```

The Python script takes as input a file containing a list of queries and will output a CSV file containing 10 search results for each query processed. Here are the command-line arguments to be passed:

```
				
					sys.argv[1] = "/path/to/query_input_file.csv"
sys.argv[2] = "/path/to/output/folder"
				
			
```

Here is an example of the `query_input_file.csv` file:

```
				
					Query
I'm looking for science fiction books
I want to read books about personal development
Search for books that talk about artificial intelligence
List of books that have won the Pulitzer Prize
...
				
			
```

The final CSV (`csv_for_quepid.csv`) looks like this:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/12/Schermata-2024-05-09-alle-15.30.41.png?fit=800%2C309&ssl=1)

As can be seen, in addition to the Solr fields, the three fields requested by Quepid were also added:

* **Query Text**: the natural language query to evaluate.
* **Doc ID**: refers to the identifier of the book (id Solr field).
* **Doc Position**: indicates the position or ranking of a document in the search results list for that query (ranges from 1 to 10, as the vector search was conducted with a `topK` setting of 10).

##### 3) Create the Quepid case

Once the CSV Static File has been created, we can easily create the Quepid case and import the file using the “CSV Static File” endpoint, as you can see here:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/12/Schermata-2024-05-08-alle-15.30.42.png?fit=507%2C1024&ssl=1)

Then, we can set up the fields we want to display:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/12/Schermata-2024-05-08-alle-15.31.04.png?fit=622%2C475&ssl=1)

The Title and ID (unique identifier of each document) fields are required, while the ‘Additional Display Fields’ allow us to specify a list of other fields whose values will be displayed in Quepid’s search results, providing additional information about each document that may be useful in the evaluation.

Within seconds, all queries are easily uploaded:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/12/Schermata-2024-05-08-alle-15.31.49.png?fit=2047%2C1035&ssl=1)

and the search results (10 for each query) are ready to be evaluated:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/12/Schermata-2024-05-08-alle-15.39.11.png?fit=800%2C458&ssl=1)

### CSV Static File Limitation

Here we will list what limitations we have encountered in implementing this approach.

Suppose we want to have several judges evaluate the same search service, this means that the same CSV file (i.e. same queries and search results) must be evaluated.

One feature that Quepid offers to do that is through the use of [Teams](https://quepid.com/docs/#teams) and [Snapshots](https://quepid.com/docs/#snapshots).   
**“Teams”** feature allows you to create groups to collaborate on search cases. This enables multiple users to share access to the same cases, facilitating team-based evaluation and improvement of search relevancy.  
“**Snapshots”** are used to capture the state of your search case, including all query ratings, at different times. You can then compare these snapshots to assess how different judges perceive the relevancy of the same search results. This comparison is visual, showing side-by-side scores and results from different snapshots.

**Anyway, using the CSV Static API, it does NOT seem possible to create and compare Snapshots.**

Another option is to create a new Quepid case using the same (an existing) Search Endpoint:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/12/Schermata-2024-05-14-alle-16.11.29.png?fit=594%2C483&ssl=1)

But as can be seen from the image above, **existing Static File endpoints are NOT sharable across cases.** This means that even if you need the same CSV file, it must be reloaded each time you want to reuse it.

We also tried to clone a case:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/12/Schermata-2024-05-14-alle-16.20.51-2.png?fit=800%2C141&ssl=1)

While cloning a case initially seems effective, when the cloned case is shared with a team, **some users may not be able to view the search results of the cloned case** –> further investigation would be necessary!

Also, we noticed that **once a case has been created, it is NOT possible to change the search endpoint**; a new case must be created.

## Conclusion

We hope this blog post has helped you understand how to evaluate vector search results in Apache Solr.  
Our workaround, integrating Python scripting with Quepid’s Static Search API, offers a **unique approach to overcoming the actual limitations of the Quepid evaluation tool**.  
Although we foresee future integrations that could further simplify the process, this method provides a current solution for automatic evaluation.  
By following the practical example provided, you can apply these techniques to your search solutions, ensuring robust evaluation and continuous improvement. We encourage you to experiment with these methods and adapt them to your specific needs, paving the way for more accurate and efficient search experiences.  
Remember that the key to improving search functionality lies in systematic and thorough performance testing.

###### References

[1] Book Dataset: Lorena Casanova Lozano, & Sergio Costa Planells. (2020). [Best Books Ever Dataset](http://doi.org/10.5281/zenodo.4265096) (Version 1.0.0) [Data set]. Zenodo.

## Need Help With This Topic?​​

If you’re struggling with Vector Search evaluation in Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Vector Search evaluation in Apache Solr, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)