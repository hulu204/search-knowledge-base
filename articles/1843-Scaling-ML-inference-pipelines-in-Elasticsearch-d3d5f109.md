---
title: 'Scaling ML inference pipelines in Elasticsearch: How to avoid issues and troubleshoot bottlenecks'
company: Elastic
tag: 工程相关
date: 2024-04-09
url: https://www.elastic.co/search-labs/blog/ml-inference-pipelines-bottlenecks
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Scaling ML inference pipelines in Elasticsearch: How to avoid issues and troubleshoot bottlenecks

Learn strategies to run Machine Learning (ML) inference pipelines in Elasticsearch, troubleshoot bottlenecks and avoid issues when scaling.

April 09, 2024

[Iulia Feroli](/search-labs/author/iulia-feroli)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

**Is it time for Semantic Search Ops?**

Whether you're a veteran search engineer looking to explore the new AI features or an ML expert who wants more of the search infrastructure to enhance semantic similarity models - making the most out of this intersection of fields may require getting familiar with some new concepts.

While Elasticsearch provides some quick startup guides like the [ELSER example notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/03-ELSER.ipynb), when you are looking to scale your inference process, more configuration options are introduced.

In this blog, we will take a look at potential bottlenecks and ways to mitigate growing pains when dealing with more complex workloads.

Following the process of deploying a large language model in your environment, here are a few steps to pay attention to.

## Before downloading the model

### ML node size

The first step to building a project in Elasticsearch with NLP models is to set up the right infrastructure for deploying the models.

The correct [ML Node configuration](https://www.elastic.co/guide/en/machine-learning/current/setup.html) can be the first potential bottleneck, so ensure you are picking the appropriate size for your desired outcome.

The recommended minimum size:

> If deployment autoscaling is turned off, the minimum dedicated ML node size for deploying and using the ELSER model is 4 GB; and 16 GB for natural language processing models.

> Turning on autoscaling is recommended because it allows your deployment to dynamically adjust resources based on demand.

> [See docs.](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-model-ref.html)

### Troubleshooting scenarios you may encounter:

| Potential Bottleneck | Error Message | Solution |
| --- | --- | --- |
| ML Node is not big enough | ApiError(429, 'status\_exception', 'Could not start deployment because no ML nodes with sufficient capacity were found') | Ensure you choose an appropriate size for your ML Node, and ideally enable autoscaling so your deployment can scale when faced with additional requests. |
| Autoscaling limit is not high enough | Autoscaling limits reached. To continue experiencing optimal performance, we recommend increasing your maximum size per zone for the topologies: Machine Learning. | There are also cases where the ML Node is big enough to download the model, but a large throughput of inference calls can still overload the system if not configured properly. Increase size, ensure your allocatoin uses all avialable CPUs, or use smaller data batches to mitigate. |

## Model Configuration

Larger node sizes also allow for more flexibility when choosing the number of [allocations and threads](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-deploy-model.html) for your models.

You need one CPU or vCPU per thread, so for example 8 CPUs would allow you to have 1 allocation with up to 8 threads, up to 8 alloctions with 1 thread each, or other permutations as long as:

> `number_of_allocations * threads_per_allocation <= number of available CPUs`.

Multiple models deployed on the same ML node will be sharing these resources, therefore you can allocate your CPUs amongst them as needed by configuring each model's maximum access.

Additionally, each allocation of a model deployment has a limited queue for inference requests. When too many calls to the same deployment are made and the queue fills up, all following requests are rejected. Consider using [dedicated deployments](https://www.elastic.co/guide/en/elasticsearch/reference/current/start-trained-model-deployment.html#start-trained-model-deployment-deployment-id-example) to prevent this situation.

For each deployment and use case you should consider the following parameters:

| Parameter | Function | Value |
| --- | --- | --- |
| number\_of\_allocations | Increases throughput by allowing more inference requests that can be performed in parallel. This will in turn improve ingest performance. | Defaults to 1; but you should change this so you use all available CPUs. |
| threads\_per\_allocation | Improves the speed of each inference request, and therefore search. | Defaults to 1; but you should change this so you use all available CPUs. |
| queue\_capacity | Controls how many inference requests are allowed in the queue at a time. When the number of requests exceeds the total value, new requests are rejected with a 429 error. | Defaults to 1024. Max allowed value is 1000000. |

The value of this setting must not exceed the number of available allocated processors per node.

See [benchmarking information](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html#_elser_v2_2) on how performance increases for ELSER with the number of allocations as an example.

## While deploying the model

Once the model has been downloaded on your cluster, you can start deploying it, taking into account the previously discussed parameters. At this stage, you can consider using a unique `deployment_id`, if you're planning on deploying multiple instances of the same model.

```
client.ml.start_trained_model_deployment(
    model_id=".elser_model_2", 
    deployment_id="elser_inference_1",
    number_of_allocations=1, 
    threads_per_allocation=8,
    queue_capacity=7000, 
    timeout="1m", 
    wait_for="starting"
)
```

Some potential bottlenecks or errors you can encounter at this stage:

| Bottleneck | Explanation / Error message | Solution |
| --- | --- | --- |
| Timeouts during deployment | Without specifying the wait\_for parameter, it defaults to started, which means you will only get a response when the model has finished downloading and is successfully deployed. However, this process will be quite lengthy, depending on model size, and since the timeout parameter also defaults to only 30s, this can often result in an error. | Use wait\_for="starting" instead, and/or increase the waiting time before throwing an error: timeout="3m" |
| Not running the steps sequentially (see rows below for specific examples) | Running commands before the previous step has finished running will result in errors: | Check on the status of your model with status = client.ml.get\_trained\_models(model\_id=".elser\_model\_2", include="definition\_status") |
| Trying to deploy model before it has been fully downloaded | Model definition truncated. Unable to deserialize trained model definition [.elser\_model\_2] | You should only attempt to deploy the model when status["trained\_model\_configs"][0]["fully\_defined"] == True |
| Trying to run inference on a model that has not been fully deployed | 404, 'resource\_not\_found\_exception', 'Could not find trained model [.elser\_model\_2]' | You can start making calls to the model when status["trained\_model\_stats"][0]["deployment\_stats"]["state"] == "started" |

## Before running inference

Once the model is deployed, you can start making inference calls to it. This can be done via the [Inference API](https://www.elastic.co/guide/en/elasticsearch/reference/current/infer-trained-model.html):

```
response = client.ml.infer_trained_model(
    model_id=model_id, 
    docs=[{"text_field": query}])
```

This inference command also has a default timeout of 10 seconds, which is sufficient when generating embeddings for a few documents at once.

However, for most real use cases there will be a lot of documents that need to be processed; for example, creating embeddings for each document in a large index to enable semantic search capabilities.

You can increase the timeout:

```
response = client.ml.infer_trained_model(model_id=model_id, docs=docs, timeout="5m")
```

However, as mentioned in the previous sections, the model will also have a maximum queue of documents it will accept, depending on the number of allocations, or how many different tasks are sent to the same deployment. So even with a bigger timeout, this method might still not be sufficient for large throughputs.

Another alternative, is to create ingestion pipelines for the inference process. You can also use different deployments for different pipelines: one for generating embeddings when ingesting new data, and one for running inference while searching.
Pipelines also allow you to set custom actions such as renaming fields or using multiple models for different tasks by adding elements in the `processors` list. You can also run longer tasks in the background or on a recurring schedule.

```
client.ingest.put_pipeline(
    id="elser-2-ingest-pipeline-1",
    description="Ingest pipeline for ELSER with a lot more requests",
    processors=[
        # omitting processors code
    ])

client.reindex(
    source={"index": "raw_data"},
    dest={"index": "data_with_embeddings", "pipeline": "elser-2-ingest-pipeline-1"},
    wait_for_completion=False,
)
```

| Bottleneck | Solution |
| --- | --- |
| Timeout | Similarily to the previous steps, the lengthy pipeline process can cause a timeout. Use the wait\_for\_completion = False parameter. |
| Waiting for pipeline to finish | You can use the task\_id you get as a response from the reindex function to track the pipeline progress later via client.tasks.get(task\_id=task\_id). This ID is generated when the wait\_for\_completion argument is used. |

## Monitoring and adjusting

Once you deployed the model and start using the inference service, you can [look at the performance of your configuration](https://www.elastic.co/guide/en/machine-learning/current/ml-trained-models.html). Often, this is the best way to determine the appropriate parameters for your particular use case, and adjust as needed until achieving the desired performance.

Taking a simple example, if you deploy a model without configuring any of the settings discussed above, these will be the default values assigned:

```
{
  "threads_per_allocation" : 1, 
  "number_of_allocations" : 1, 
  "queue_capacity" : 1024
}
```

Let's say that after sending a large queue of documents to this model via an inference pipeline, we notice some warning signs in the thread allocation. The endpoint

> GET \_nodes/hot\_threads

responds with

> ml.allocated\_processors=16
> 100.0% [cpu=3.5%, other=96.5%] cpu usage by thread

The ML node has 16 allocated processors, but we are only leveraging 1 of them with our one instance of the model. Furthermore, the high percentage of utilization reported under `other` rather than `cpu` related tasks means there is a lot of waiting and redundancy in the process, and our documents are spending most of the time being queued.

To optimize performance, you should use all available cores.

You can see more metrics in the Trained Models UI as well or through the command:

> GET \_ml/trained\_models/\_stats

Here you can see more useful information like `average_inference_time_ms`, `number_of_pending_requests`, or `peak_throughput_per_minute`.

As an ilustration, here are two models deployed on the same ML node, running inference on the same pipeline and data, but with different allocation strategies. You can see the inference time is almost halved for the configured model.

| Model ID | Allocation | Average Inference time |
| --- | --- | --- |
| elser\_inference\_configured | 3 \* 8 | 67.80 milliseconds |
| .elser\_model\_2 | 1 \* 1 | 115.58 milliseconds |

## Conclusion

As both a good and potentially hard thing, there are multiple flexible and modular ways to build up your inference architecture to suit your project. Building the best approach for each use case will also go beyond choosing the right configuration or infrastructure setup. You can read more about how a models's [retrieval optimization](https://www.elastic.co/search-labs/blog/introducing-elser-v2-part-2) or even data processing decisions such as [chunking strategies](https://www.elastic.co/search-labs/blog/chunking-via-ingest-pipelines) also influence performance.

Elasticsearch brings together amazing out-of-the-box capabilities and provides the customization options and guidance to help you build the best semantic search solution.

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