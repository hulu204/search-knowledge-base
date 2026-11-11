---
title: 'Training LTR models in Elasticsearch with judgement lists based on user behavior data'
company: Elastic
tag: 排序
date: 2025-10-15
url: https://www.elastic.co/search-labs/blog/training-learning-to-rank-models-elasticsearch-ubi-data
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Training LTR models in Elasticsearch with judgement lists based on user behavior data

Learn how to use UBI data to create judgment lists to automate the training of your Learning to Rank (LTR) models in Elasticsearch.

October 15, 2025

[Alexander Dávila](/search-labs/author/alexander-davila)

[Python](/search-labs/blog/category/python-programming)[Elastic Cloud Hosted](/search-labs/blog/category/elastic-cloud-hosted)

Jump to

Share

A big challenge when using [***Learning-to-rank***](https://www.elastic.co/docs/solutions/search/ranking/learning-to-rank-ltr) models is to create a high-quality [***judgment list***](https://www.elastic.co/search-labs/blog/judgment-lists) to train the model on. Traditionally, this process involves a ***manual*** evaluation of query-document relevance to assign a grade to each one. This is a slow process that does not scale well and is hard to maintain (imagine having to update a list with hundreds of entries by hand).

Now, what if we could use real user interactions with our search application to create this training data? Using [***UBI***](https://www.elastic.co/search-labs/blog/elasticsearch-plugin-user-behavior-insights) data lets us do just that. Creating an automatic system that can capture and use our searches, clicks, and other interactions to generate a judgment list. This process can scale and be repeated far more easily than a manual interaction and would tend to yield better results. In this blog, we will explore how we can query UBI data stored in Elasticsearch to calculate meaningful signals to generate a training dataset for an [***LTR***](https://www.elastic.co/search-labs/blog/elasticsearch-learning-to-rank-introduction) model.

***You can find the full experiment*** [***here***](https://github.com/Alex1795/elastic-ltr-judgement_list-blog.git)***.***

## Why UBI data can be useful to train your LTR model

UBI data offers several advantages over a manual annotation:

* **Volume:** Given that UBI data comes from real interactions, we can collect much more data than we can generate manually. This is assuming we have enough traffic to generate this data, of course.
* **Real User intent:** Traditionally, a manual judgment list comes from an expert evaluation of the available data. On the other hand, UBI data reflects real user behavior. This means we can generate better training data that will improve our search system's accuracy, because it's based on how users actually interact with and find value in your content rather than theoretical assumptions about what should be relevant.
* **Continuous updates:** Judgment lists need to be refreshed over time. If we create them from UBI data, we can have current data that results in updated judgment lists.
* **Cost effectiveness:** Without the overhead of manually creating a judgment list, the process can be repeated efficiently any number of times.
* **Natural query distribution**: UBI data represent real user queries, which can drive deeper changes. For example, do our users use natural language to search in our system? If so, we might want to implement a semantic search or hybrid search approach.

It does come with some warnings, though:

* **Bias amplification:** Popular content is more likely to receive clicks, just because it gets more exposure. So this might end up amplifying popular items and possibly drowning out better options.
* **Incomplete coverage:** New content lacks any interactions, so it might be difficult for it to be high in the results. Rare queries can also lack sufficient data points to create meaningful training data.
* **Seasonal variations:** If you expect user behaviour to change drastically over time, historical data might not tell you much about what is a good result.
* **Task ambiguity:** A click doesn’t always guarantee that the user found what they were looking for.

## Grades calculation

### Grades for LTR training

To train LTR models, we need to provide some numerical representation of how relevant a document is for a query. In our implementation, this number is a continuous score going from 0.0 to 5.0+, where higher scores indicate higher relevance.

To show how this grading system works, consider this manually created example:

| Query | Document content | Grade | Explanation |
| --- | --- | --- | --- |
| "best pizza recipe" | "Authentic Italian Pizza Dough Recipe with Step-by-Step Photos" | 4.0 | Highly relevant, exactly what the user is looking for |
| "best pizza recipe" | "History of Pizza in Italy" | 1.0 | Somewhat in topic, it is about pizza but is not a recipe |
| "best pizza recipe" | "Quick 15-Minute Pizza Recipe for Beginners" | 3.0 | Relevant, a good result but it maybe misses the mark on being the “best” recipe. |
| "best pizza recipe" | "Car Maintenance Guide" | 0.0 | Not relevant at all, completely unrelated to the query |

As we can see here, the grade is a numerical representation of how relevant a document is to our sample query of “best pizza recipe”. With these scores, our LTR model can learn which documents should be presented higher in the results.

How to calculate the grades is the core of our training dataset. There are [multiple approaches](https://www.elastic.co/search-labs/blog/judgment-lists) to do this, each with its own strengths and weaknesses. For example, we could assign a binary score of 1 for relevant 0 for not relevant or we could just count the number of clicks in a resulting document for each query.

In this blog post, we will be using a different approach, ***taking into account the user behavior as our input and calculating a grade number as the output***. We will also be correcting bias that could occur from the fact that higher results tend to be more clicked, regardless of the relevancy of the document.

## Calculating the grades - COEC algorithm

The COEC ([Clicks over Expected Clicks](https://www.wsdm-conference.org/2010/proceedings/docs/p351.pdf)) algorithm is a methodology for calculating judgment grades from user clicks.
As we stated earlier, users tend to click on higher-positioned results even if the document is not the most relevant to the query; this is called [Position Bias](https://eugeneyan.com/writing/position-bias/). The core idea for using the COEC algorithm is that not all clicks are equally significant; a click on a document at position 10 indicates that the document is much more relevant to the query than a click on a document at position 1. To quote the research paper about the COEC algorithm (linked above):

*“It is well known that the click-through rate (CTR) of search results or advertisements decreases significantly depending on the position of the results.”*

You can further read about position bias [here](https://www.researchgate.net/publication/200110550_An_experimental_comparison_of_click_position-bias_models).

To address this with the COEC algorithm, we follow these steps:

**1. Establish position baselines:** We calculate the click-through rate (CTR) for each search position from 1 to 10. This means we determine what percentage of users typically click on position 1, position 2, and so on. This step captures the users’ natural position bias.
We calculate the CTR using:

CTRp=CpIpCTRp=CpIpCTRp=CpIp

Where:

p = Position. From 1 to 10
Cp = Total clicks (on any document) at position p across all queries
Ip = Total impressions: How many times any document appeared at the position p across all queries

Here, we expect higher positions to get more clicks.

**2.** **Calculate Expected Clicks (EC)**:

This metric establishes how many clicks a document “should” have received based on the positions it appeared in and the CTR for those positions We calculate EC using:

EC(foradocument)=qQdCTRpos(d,q)EC (for a document) = qQdCTRpos(d,q)EC(foradocument)=qQdCTRpos(d,q)

Where:

Qd = All queries where the document d appeared
pos(d,q)= Position of the document d in the query q results

3. **Count actual clicks:** We count the actual total clicks a document received across all queries where it appeared, hereafter called **A(d).**

4. **Compute the COEC score:** This is the ratio of Actual clicks (A(d)) over the Expected clicks (EC(d)):

COEC=A(d)EC(d)COEC = A(d)EC(d)COEC=A(d)EC(d)

This metric normalizes for position bias like this:

* A score of 1.0 means the document performed exactly as expected given the positions it appeared in.
* A score above 1.0 means the document performed better than expected by looking at its positions. So this document is more relevant for the query.
* A score under 1.0 means the document performed worse than expected by looking at its positions. So this document is less relevant for the query.

***The end result is a grade number that captures what users are looking for, taking into account position-based expectations extracted from real interactions with our search system.***

## Technical implementation

We will be creating a script to create a judgment list to train an LTR model.

The input for this script is the UBI data indexed in Elastic (queries and events).

The output is a judgment list in a CSV file generated from these UBI documents using the COEC algorithm. This judgment list can be used with [Eland](https://www.elastic.co/search-labs/blog/elasticsearch-learning-to-rank-introduction) to extract relevant features and train an LTR model.

### Quick start

To generate a judgment list from the sample data in this blog, you can follow these steps:

1. Clone the repository:

```
git clone https://github.com/Alex1795/elastic-ltr-judgement_list-blog.git  
cd elastic-ltr-judgement_list-blog
```

2. Install required libraries

For this script, we need the following libraries:

* *pandas*: to save the judgment list
* *elasticsearch*: To get the UBI data from our Elastic deployment

We also need Python 3.11

```
pip install -r requirements.txt
```

3. Update the environment variables for your Elastic deployment in a [.env file](https://github.com/Alex1795/elastic-ltr-judgement_list-blog/blob/main/.env-example)

* ES\_HOST
* API\_KEY

To add the environment variables, use:

```
source .env
```

4. Create the ubi\_queries, ubi\_events indices, and upload the sample data. Run the setup.py file:

```
python setup.py
```

5. Run the Python script:

```
python judgement_list-generator.py
```

If you follow these steps, you should see a new file called judgment\_list.csv that looks like this:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt94317eda8f7af194/6a170aa46f7f04542f914821/2531090131ac9fe3e4e1d79de9d156fc47a7825a-782x531.png)

This script calculates the grades applying the COEC algorithm discussed before using the **calculate\_relevance\_grade()** function that is shown below.

## Data architecture

### Ubi queries

Our UBI queries index has information about the queries executed in our search system. This is a sample document:

```
{
          "client_id": "client_002",
          "query": "italian pasta recipes",
          "query_attributes": {
            "search_type": "recipe",
            "category": "food",
            "cuisine": "italian"
          },
          "query_id": "q002",
          "query_response_id": "qr002",
          "query_response_object_ids": [
            "doc_011",
            "doc_012",
            "doc_013",
            "doc_014",
            "doc_015",
            "doc_016",
            "doc_017",
            "doc_018",
            "doc_019",
            "doc_020"
          ],
          "timestamp": "2024-08-14T11:15:00Z",
          "user_query": "italian pasta recipes"
        }
```

Here we can see data from the user (client\_id), from the results of the query (query\_response\_object\_ids), and the query itself (timestamp, user\_query)

### Ubi click events

Our ubi\_events index has data from each time a user clicked a document in the results. This is a sample document:

```
{
          "action_name": "click",
          "application": "recipe_search",
          "client_id": "client_001",
          "event_attributes": {
            "object": {
              "description": "Authentic Italian Pizza Dough Recipe with Step-by-Step Photos",
              "device": "desktop",
              "object_id": "doc_001",
              "position": {
                "ordinal": 1,
                "page_depth": 1
              },
              "user": {
                "city": "New York",
                "country": "USA",
                "ip": "192.168.1.100",
                "location": {
                  "lat": 40.7128,
                  "lon": -74.006
                },
                "region": "NY"
              }
            }
          },
          "message": "User clicked on document doc_001",
          "message_type": "click",
          "query_id": "q001",
          "timestamp": "2024-08-14T10:31:00Z",
          "user_query": "best pizza recipe"
        }
```

## Judgment list generation script

### General script overview

This script automates the generation of the judgment list using UBI data from Queries and Click events stored in Elasticsearch. It executes these tasks:

* Fetches and processes the UBI data in Elasticsearch.
* Correlates UBI events with its queries.
* Calculates the CTR for each position.
* Calculates the expected clicks (EC) for each document.
* Counts the actual clicks for each document.
* Calculates the COEC score for each query-document pair.
* Generates a judgment list and writes it in a CSV file.

Let’s go over each function:

### connect\_to\_elasticsearch()

```
def connect_to_elasticsearch(host, api_key):
    """Create and return Elasticsearch client"""
    try:
        es = Elasticsearch(
            hosts=[host],
            api_key=api_key,
            request_timeout=60
        )
        # Test the connection
        if es.ping():
            print(f"✓ Successfully connected to Elasticsearch at {host}")
            return es
        else:
            print("✗ Failed to connect to Elasticsearch")
            return None
    except Exception as e:
        print(f"✗ Error connecting to Elasticsearch: {e}")
        return None
```

This function returns an Elasticsearch client object using the host and api key.

### fetch\_ubi\_data()

```
def fetch_ubi_data(es_client: Elasticsearch, queries_index: str, events_index: str,
                   size: int = 10000) -> Tuple[List[Dict], List[Dict]]:
    """
    Fetch UBI queries and events data from Elasticsearch indices.

    Args:
        es_client: Elasticsearch client
        queries_index: Name of the UBI queries index
        events_index: Name of the UBI events index
        size: Maximum number of documents to fetch

    Returns:
        Tuple of (queries_data, events_data)
    """
    logger.info(f"Fetching data from {queries_index} and {events_index}")

    # Fetch queries with error handling
    try:
        queries_response = es_client.search(
            index=queries_index,
            body={
                "query": {"match_all": {}},
                "size": size
            }
        )
        queries_data = [hit['_source'] for hit in queries_response['hits']['hits']]
        logger.info(f"Fetched {len(queries_data)} queries")

    except Exception as e:
        logger.error(f"Error fetching queries from {queries_index}: {e}")
        raise

    # Fetch events (only click events for now) with error handling
    try:
        events_response = es_client.search(
            index=events_index,
            body={
                "query": {
                    "term": {"message_type.keyword": "CLICK_THROUGH"}
                },
                "size": size
            }
        )
        events_data = [hit['_source'] for hit in events_response['hits']['hits']]
        logger.info(f"Fetched {len(events_data)} click events")

    except Exception as e:
        logger.error(f"Error fetching events from {events_index}: {e}")
        raise

    logger.info(f"Data fetch completed successfully - Queries: {len(queries_data)}, Events: {len(events_data)}")

    return queries_data, events_data
```

This function is the data extraction layer; it connects with Elasticsearch to fetch UBI queries using a match\_all query and filters UBI events to get ‘CLICK\_THROUGH’ events only.

### process\_ubi\_data()

```
def process_ubi_data(queries_data: List[Dict], events_data: List[Dict]) -> pd.DataFrame:
    """
    Process UBI data and generate judgment list.

    Args:
        queries_data: List of query documents from UBI queries index
        events_data: List of event documents from UBI events index

    Returns:
        DataFrame with judgment list (qid, docid, grade, keywords)
    """
    logger.info("Processing UBI data to generate judgment list")

    # Group events by query_id
    clicks_by_query = {}
    for event in events_data:
        query_id = event['query_id']
        if query_id not in clicks_by_query:
            clicks_by_query[query_id] = {}

        # Extract clicked document info
        object_id = event['event_attributes']['object']['object_id']
        position = event['event_attributes']['object']['position']['ordinal']

        clicks_by_query[query_id][object_id] = {
            'position': position,
            'timestamp': event['timestamp']
        }

    judgment_list = []

    # Process each query
    for query in queries_data:
        query_id = query['query_id']
        user_query = query['user_query']
        document_ids = query['query_response_object_ids']

        # Get clicks for this query
        query_clicks = clicks_by_query.get(query_id, {})

        # Generate judgment for each document shown
        for doc_id in document_ids:
            grade = calculate_relevance_grade(doc_id, query_clicks, document_ids, queries_data, events_data)

            judgment_list.append({
                'qid': query_id,
                'docid': doc_id,
                'grade': grade,
                'query': user_query
            })

    df = pd.DataFrame(judgment_list)
    logger.info(f"Generated {len(df)} judgment entries for {df['qid'].nunique()} unique queries")

    return df
```

This function handles the judgment list generation. It starts processing the UBI data by associating UBI events and queries. Then it calls the calculate\_relevance\_grade() function for each document-query pair to obtain the entries for the judgment list. Finally, it returns the resulting list as a pandas dataframe.

### calculate\_relevance\_grade()

```
def calculate_relevance_grade(document_id: str, clicks_data: Dict,
                              query_response_ids: List[str], all_queries_data: List[Dict] = None,
                              all_events_data: List[Dict] = None) -> float:
    """
    Calculate COEC (Click Over Expected Clicks) relevance score for a document.

    Args:
        document_id: ID of the document
        clicks_data: Dictionary of clicked documents with their positions for current query
        query_response_ids: List of document IDs shown in search results (ordered by position)
        all_queries_data: All queries data for calculating position CTR averages
        all_events_data: All events data for calculating position CTR averages

    Returns:
        COEC relevance score (continuous value, typically 0.0 to 5.0+)
    """

    # If no global data provided, fall back to simple position-based grading
    if all_queries_data is None or all_events_data is None:
        logger.warning("No global data provided, falling back to position-based grading")
        # Simple fallback logic
        if document_id in clicks_data:
            position = clicks_data[document_id]['position']
            if position > 3:
                return 4.0
            elif position >= 1 and position <= 3:
                return 3.0
        if document_id in query_response_ids:
            position = query_response_ids.index(document_id) + 1
            if position <= 5:
                return 2.0
            elif position >= 6 and position <= 10:
                return 1.0
        return 0.0

    # Calculate rank-aggregated click-through rates
    position_ctr_averages = {}
    position_impression_counts = {}
    position_click_counts = {}

    # Initialize counters
    for pos in range(1, 11):  # Positions 1-10
        position_impression_counts[pos] = 0
        position_click_counts[pos] = 0

    # Count impressions (every document shown contributes)
    for query in all_queries_data:
        for i, doc_id in enumerate(query['query_response_object_ids'][:10]):  # Top 10 positions
            position = i + 1
            position_impression_counts[position] += 1

    # Count clicks by position
    for event in all_events_data:
        if event.get('action_name') == 'click':
            position = event['event_attributes']['object']['position']['ordinal']
            if position <= 10:
                position_click_counts[position] += 1

    # Calculate average CTR per position
    for pos in range(1, 11):
        if position_impression_counts[pos] > 0:
            position_ctr_averages[pos] = position_click_counts[pos] / position_impression_counts[pos]
        else:
            position_ctr_averages[pos] = 0.0

    # Calculate expected clicks for this specific document
    expected_clicks = 0.0

    # Count how many times this document appeared at each position for any query
    for query in all_queries_data:
        if document_id in query['query_response_object_ids']:
            position = query['query_response_object_ids'].index(document_id) + 1
            if position <= 10:
                expected_clicks += position_ctr_averages[position]

    # Count total actual clicks for this document across all queries
    actual_clicks = 0
    for event in all_events_data:
        if (event.get('action_name') == 'click' and
                event['event_attributes']['object']['object_id'] == document_id):
            actual_clicks += 1

    # Calculate COEC score
    if expected_clicks > 0:
        coec_score = actual_clicks / expected_clicks
    else:
        coec_score = 0.0

    logger.debug(
        f"Document {document_id}: {actual_clicks} clicks / {expected_clicks:.3f} expected = {coec_score:.3f} COEC")

    return coec_score
```

This is the function that implements the COEC algorithm. It calculates the CTR for each position, then it compares the actual clicks for a document-query pair, and finally calculates the actual COEC score for each one.

### generate\_judgment\_statistics()

```
def generate_judgment_statistics(df: pd.DataFrame) -> Dict:
    """Generate statistics about the judgment list."""
    stats = {
        'total_judgments': len(df),
        'unique_queries': df['qid'].nunique(),
        'unique_documents': df['docid'].nunique(),
        'grade_distribution': df['grade'].value_counts().to_dict(),
        'avg_judgments_per_query': len(df) / df['qid'].nunique() if df['qid'].nunique() > 0 else 0,
        'queries_with_clicks': len(df[df['grade'] > 1]['qid'].unique()),
        'click_through_rate': len(df[df['grade'] > 1]) / len(df) if len(df) > 0 else 0
    }
    return stats
```

It generates useful statistics from the judgment list, such as total queries, total unique documents, or the grade distribution. This is purely informational and does not change the resulting judgment list.

## Results and impact

If you follow the instructions in the Quick start section, you should see a resulting CSV file containing a judgment list with 320 entries (you can see a [sample output](https://github.com/Alex1795/elastic-ltr-judgement_list-blog/blob/main/judgment_list.csv) in the repo). With these fields:

* qid: unique ID of the query
* docid: unique identifier for a resulting document
* grade: the calculated grade for the query-document pair
* query: The user query

Let’s look at the results for the query “Italian recipes”:

| qid | docid | grade | query |
| --- | --- | --- | --- |
| q1-italian-recipes | recipe\_pasta\_basics | 0.0 | Italian recipes |
| q1-italian-recipes | recipe\_pizza\_margherita | 3.333333 | Italian recipes |
| q1-italian-recipes | recipe\_risotto\_guide | 10.0 | Italian recipes |
| q1-italian-recipes | recipe\_french\_croissant | 0.0 | Italian recipes |
| q1-italian-recipes | recipe\_spanish\_paella | 0.0 | Italian recipes |
| q1-italian-recipes | recipe\_greek\_moussaka | 1.875 | Italian recipes |

We can see from the results that for the query “Italian recipes”:

* The risotto recipe is definitely the best result for the query, receiving 10 times more clicks than expected
* Pizza Margherita is a great result too.
* The Greek mousaka (surprisingly) is a good result as well and performs better than its position on the results would suggest. This means a few users looking for Italian recipes got interested in this recipe instead. Maybe these users are interested in Mediterranean dishes in general. At the end, what this tells us is that this could be a good result to be shown under the other two ‘better’ matches we discussed above.

## Conclusion

Using UBI data lets us automate the training of LTR models, creating high-quality judgment lists from our own users. UBI data provides a big dataset that reflects how our search system is being used.By using the COEC algorithm to generate the grades, we account for inherent bias while at the same time, it reflects what a user considers a better result. The method outlined here can be applied to real use cases to provide a better search experience that evolves with real usage trends.

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