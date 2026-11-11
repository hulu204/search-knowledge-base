---
title: 'Implementing clustering workflows in Elastic to enhance search relevance'
company: Elastic
tag: 搜索相关性
date: 2025-02-05
url: https://www.elastic.co/search-labs/blog/elastic-clustering-workflows
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Implementing clustering workflows in Elastic to enhance search relevance

We demonstrate how to integrate custom clustering models into the Elastic Stack by leveraging OpenAI text-ada-002 vectors, streamlining the workflow within Elastic’s ecosystem.

February 05, 2025

[Gus Carlock](/search-labs/author/gus-carlock)[Kirti Sodhi](/search-labs/author/kirti-sodhi)

[ML Research](/search-labs/blog/category/ml-research)[Python](/search-labs/blog/category/python-programming)

Jump to

Share

In this article, we’ll demonstrate how to integrate custom clustering models into the Elastic Stack by leveraging a sample text dataset, streamlining the workflow within Elastic’s ecosystem. You can follow along to create a simple clustering pipeline with this [Jupyter notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/clustering/newsgroup_clustering.ipynb).

## Clustering prologue

The Machine Learning App in Kibana provides a comprehensive suite of advanced capabilities, including anomaly and outlier detection, as well as classification and regression models. It supports the integration of custom models from the scikit-learn library via the [**eland**](https://eland.readthedocs.io/en/v8.17.0/) Python client. While Kibana offers robust machine learning capabilities, it currently does not support clustering analysis in both prebuilt and custom models. Clustering algorithms are crucial for enhancing search relevance by grouping similar queries and for security, where they help identify patterns in data to detect potential threats and anomalies.

Elastic provides the flexibility to leverage custom scikit-learn models, such as k-means, for tasks like clustering—for example, grouping news articles by similarity. While these algorithms aren’t officially supported, you can use the model’s cluster centers as input for the ingest pipeline to integrate these capabilities seamlessly into your Elastic workflow. In the following sections, we’ll guide you through implementing this approach.

## Dataset overview for clustering workflow

For this proof of concept, we utilized the **20 Newsgroups dataset**, a popular benchmark for text classification and clustering tasks. This dataset consists of newsgroup posts organized into 20 distinct categories, covering topics such as sports, technology, religion, and science. It is widely available through the `scikit-learn` library.

In our experiments, we focused on a subset of 5 categories:

* rec.sport.baseball
* rec.sport.hockey
* comp.sys.ibm.pc.hardware
* talk.religion.misc
* sci.med

These categories were chosen to ensure a mix of technical, casual, and diverse topics for effective clustering analysis.

## Feature extraction and generating text embeddings

The text documents were cleaned by removing stop words, punctuation, and irrelevant tokens using scikit-learn’s `feature_extraction` utility, ensuring that the text vectors captured meaningful patterns. These features were then used to generate text embeddings using OpenAI’s language model “text-embedding-ada-002”.

The model, text-embedding-ada-002 stands among the most advanced models for generating dense vector representations of text, capturing the nuanced semantic meaning inherent in textual data. We utilized the Azure OpenAI endpoint to generate the embeddings for our analysis. Instructions to use this endpoint with Elasticsearch can be found at [Elasticsearch open inference API adds Azure AI Studio support](https://www.elastic.co/search-labs/blog/elasticsearch-azure-ai-studio-support).

The embeddings were normalized before training the k-means clustering model to standardize vector magnitudes. Normalization is a critical preprocessing step for k-means since it calculates clusters based on Euclidean distances. Standardized embeddings eliminate magnitude discrepancies, ensuring that clustering decisions rely purely on semantic proximity, thereby enhancing the accuracy of the clustering results.

We trained the k-means model using k=5 to match the dataset’s categories and extracted the cluster centers. These centers served as inputs for Kibana’s ingest pipeline, facilitating real-time clustering of incoming documents. We’ll discuss this further in the next section.

## Dynamic clustering with ingest pipeline’s script processor

After the model is trained in Scikit-learn, an ingest pipeline is used to assign cluster numbers to each record. This ingest pipeline takes three configurable parameters:

* **clusterCenters** – a nested list with one list for each cluster center vector. For this blog, they were generated with Scikit-learn.
* **analysisField** – the field which contains dense vectorized data.
* **normalize** – normalizes the analysisField vectors.

Once the ingest pipeline is added to an index or datastream, all new ingested data will be assigned a closest cluster number.

The image below illustrates the end-to-end workflow of importing clustering in Kibana.

![Importing clustering in Kibana workflow](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1ec095385ca22bfb/6a1707aa1949f7645ee7a970/4fc1962f014221fa1e72ef1da38b23b2594bf997-1200x628.png)

The full ingest pipeline script can be generated using Python, an example is in the “Add clustering ingest pipeline” section of the [notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/clustering/newsgroup_clustering.ipynb). We’ll dive into the specifics of the ingest pipeline below.

The **cluster\_centers** are then loaded as a nested list of floats, with one list for each cluster center.

```
cluster_centers_filepath = 'data/openai_cluster_centers.json'
with open(cluster_centers_filepath, 'r') as f:
    cluster_centers = json.load(f)
```

In the first part of the Painless script, two functions are defined. The first is `euclideanDistance`, which returns a distance between two arrayLists as a float. The second, `l2NormalizeArray` , scales an arrayLists so that the sum of its squared elements is equal to one.

```
script = {
 "script": {
   "lang": "painless",
   "source": """ 
     double euclideanDistance(List array1, List array2) {
       double sum = 0.0;
       for (int i=0; i<array1.length; i++) {
         sum += Math.pow((array1[i]-array2[i]), 2.0);
       }
       return Math.sqrt(sum);
     }

     List l2NormalizeArray(List array) {
       double sumSquared = 0.0;
       for (element in array) {
         sumSquared += Math.pow(element, 2.0)
       }
       double l2Norm = Math.sqrt(sumSquared);
       // create a new array to not overwrite ctx
       List outputArray = new ArrayList();
       for (element in array) {
         outputArray.add(element/l2Norm)
       }
       return outputArray
     }
```

Then the inference step of k-Means is performed. For every cluster center, the distance is taken between a new incoming document vector using the ingest pipeline context (ctx) and the `analysisField` parameter, which selects the field containing the OpenAI text-ada-002 vector. The `closestCluster` number is then assigned to the document based on the closest cluster center, that is, the document which has the shortest distance. Additionally, if the normalize parameter is set to true, the L2 norm of the incoming document vector is taken before doing the distance calculation.

```
     List distances = new ArrayList();
     double minDistance;
     int closestCluster;

     for (int i=0; i<params.clusterCenters.length; i++) {
       double distance;
       if (params.normalize == true) {
         distance = euclideanDistance(params.clusterCenters[i], l2NormalizeArray(ctx[params.analysisField]));
       } else {
         distance = euclideanDistance(params.clusterCenters[i], ctx[params.analysisField]);
       }
       distances.add(distance);
       if (i == 0) {
         minDistance = distance;
         closestCluster = i;
       } else {
         if (distance < minDistance) {
           minDistance = distance;
           closestCluster = i;
         }
       }
     }
```

Then the `closestCluster` and `minDistance` value to that cluster are passed back to the document through the ingest pipeline context.

```
     ctx["ml_clustering.closestCluster"] = closestCluster;
     ctx["ml_clustering.minDistance"] = Collections.min(distances);
   """,
```

There are a few configurable parameters, which are described above but included here for reference. The first is the `clusterCenters`, a nested array of floats, with one array for each cluster center. The second is the `analysisField`, the field which contains the text-ada-002 vectors. Lastly, `normalize` which will L2 `normalize` the document vector. **Note** that the normalize parameter should only be set to **True** if the vectors are also normalized before training the k-Means model.

```
   "params": {
     "clusterCenters": cluster_centers,
     "analysisField": "openai_vector",
     "normalize": True
   }
 }
}
```

Finally, once the pipeline is configured, assign an ID and put it on the cluster.

```
es_client.ingest.put_pipeline(
   id="ml_clustering_5_newsgroup_openai", processors=[script]
)
```

## Clustering results

We expect the clustering results to show each category forming a distinct cluster. While baseball and hockey might overlap due to their shared sports context; technical, religious, and medical categories should form separate and clearly defined clusters. When OpenAI text-ada-002 vectors are viewed with the t-SNE dimensionality reduction algorithm, they show that there is clear separation between these clusters, and that the sports topics are close together:

**Actual newsgroup labels; 2D t-SNE trained on OpenAI text-ada-002 vectors**

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1b421e2cc3fc0d34/6a1707acb339d562d7769f23/d8478d403e6008ee0016d5e562e7ee3e66a73303-512x344.png)

The location of the points indicates clear separation between the groupings, which indicates that the vectorization is capturing the semantic meaning of each article.

As a result, the zero-shot classification results are excellent. Even though no labels were provided in training data to the model, with only the number of clusters provided, on in-sample data a k-means model provides greater than 94% accuracy when assigning cluster numbers:

**Predicted cluster labels; 2D t-SNE trained on OpenAI text-ada-002 vectors**

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt68a0b1a978cd7349/6a1707addc55de7314e00d5f/69cbdc5b132ed34a1a91522aada946ac45d9d3f8-1214x808.png)

Comparing the actual newsgroup labels to the in-sample predicted labels, there is very little difference between the actual newsgroup labels and those predicted by the clustering model. This is represented by the confusion matrix:

**Zero-shot Classification Confusion Matrix on OpenAI text-ada-002 vectors**

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltaf4ba45a4cae3406/6a1707afb0367d189572bc7c/f003858cffc5fed628f5a581ec986abfcd924061-688x563.png)

The diagonal on the confusion matrix represents the in-sample accuracy of each category, the model is predicting the correct label more than 94% of the time for each category.

## Detecting outliers in the clusters

The k-means model can be viewed as an approximation of a Gaussian Mixture Model (GMM) without capturing covariance, where the quantiles of distances from the nearest cluster being an approximation of the distribution quantile. This means that a k-mean model can capture an approximation of the data distribution. With this approach, a large number of clusters can be chosen, in this case 100, and a new model trained. The higher number of clusters, the more flexible the fit of the distribution. So in this case, the goal is not to learn the internal groupings of the data, but rather capture the distribution of the data overall.

The distance quantiles can be computed with a query. In this case, a model was trained with 100 clusters and the 75th percentile distances were chosen as the cutoff for outliers. Starting with the same graph above showing the t-SNE representation of the actual newsgroup labels:

**Actual newsgroup labels; 2D t-SNE trained on OpenAI text-ada-002 vectors**

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta1a3f107677fc9a8/6a1707b14a531ba0d536a8b2/c67fe518d1d99aeae6d0dfa1388c729c3b183a70-1210x812.png)

When adding data in from newsgroups which were not in the training set, the 2D t-SNE representation shows a good fit for the data. Here, orange datapoints are not considered outliers, while those which are dark grey are labelled as outliers:

**Outlier results for k=100; 2D t-SNE trained on OpenAI text-ada-002 vectors**

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3d026d80124ef424/6a1707b37d8d6744d070e682/f9bd4eb4482460c47fdd7626fed7a2ac051b7874-1196x796.png)

## Bringing it all together

In this blog, we demonstrated how to integrate custom clustering models into the Elastic Stack. We developed a workflow that imports scikit-learn clustering models, such as k-means, into the Elastic Stack, enabling clustering analysis directly within Kibana. By using the 20 Newsgroups dataset, we demonstrated how to apply this workflow to group similar documents, while also discussing the use of advanced text embedding models such as OpenAI's “text-embedding-ada-002” to create semantic representations essential for efficient clustering.

The results section showcased clear cluster separation, indicating that the “text-embedding-ada-002” model captures semantic meaning effectively. The k-means model achieved over 94% accuracy in zero-shot classification, with the confusion matrix showing minimal discrepancies between predicted and actual labels, confirming its strong performance.

With this workflow, Elastic users can apply clustering techniques to their own datasets, whether for grouping similar queries in search or detecting unusual patterns for security applications. The solution presented here provides an easy way to integrate advanced clustering functionality into Elastic. We hope this inspires you to explore these capabilities and apply them to your own use cases.

## What’s next?

The clustering results above show that the Painless implementation accurately clusters similar topics, achieving 94% accuracy in performance. Moving forward, our goal is to test the pipeline on a less structured dataset with significantly more noise and a larger number of clusters. This will help evaluate its performance in more challenging scenarios. While k-means has shown decent clustering results, exploring alternatives like Gaussian Mixture Models or Mean Shift for outlier detection might yield better outcomes. These methods could also be implemented using a Painless script or an ingest pipeline.

In the future, we think this workflow can be enhanced with [ELSER](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html), as we could use ELSER to first retrieve relevant features from the dataset, which would then be used for clustering, further improving the model’s performance and relevance in the analysis. Additionally, we would like to address how to properly set the correct number of clusters, and how to effectively deal with model drift.

In the meantime, if you have similar experiments or use cases to share, we’d love to hear about them! Feel free to provide feedback or connect with us through our [community Slack channel](https://ela.st/slack) or [discussion forums](https://discuss.elastic.co/c/security).

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt29bbbf4463c73d8a/6a6a33fa55755baeaa2bd248/a6563ee307cc2d29722c490b043ee736c46974f3-1280x720.png)

[Jina AI](/search-labs/blog/category/jina-ai)[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

### 56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker

July 27, 2026|[Felix Wang](/search-labs/author/felix-wang)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt097721c03648a84e/6a6a33ef0a222b4c70877f32/8f6b95800c65fe389d3e8d8281e8e8dc351f734d-992x342.png)

[ES|QL](/search-labs/blog/category/esql)[ML Research](/search-labs/blog/category/ml-research)[Agentic AI](/search-labs/blog/category/agentic-ai)

### How Elasticsearch detects multiple change points in time series with 0.99 recall

July 24, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt950edbc25d291821/6a6119f01b1d495dc56f181b/31783975126874424fc20c3c96bd95fe28d5f201-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)

### How Elasticsearch auto-tunes vector quantization to hit your recall target

July 21, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9d9912c8d4187096/6a1704f5b0367d30e672bc17/54a6e5197f5721b36fc65f27387d29803ed35589-721x420.jpg)

[ML Research](/search-labs/blog/category/ml-research)[Python](/search-labs/blog/category/python-programming)

### Evaluating search relevance part 1 - The BEIR benchmark

July 16, 2024|[Thanos Papaoikonomou](/search-labs/author/thanos-papaoikonomou)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter