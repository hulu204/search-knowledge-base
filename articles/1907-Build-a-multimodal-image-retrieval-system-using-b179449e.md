---
title: 'Build a multimodal image retrieval system using KNN search and CLIP embeddings'
company: Elastic
tag: 召回
date: 2025-01-27
url: https://www.elastic.co/search-labs/blog/multimodal-image-retrieval-with-roboflow
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Build a multimodal image retrieval system using KNN search and CLIP embeddings

Learn how to build a powerful semantic image search engine with Roboflow Inference and Elasticsearch.

January 27, 2025

[James Gallagher](/search-labs/author/james-gallagher)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

In this guide, we are going to walk through how to build an image retrieval system using KNN clustering in Elasticsearch and CLIP embeddings computed with [Roboflow Inference](https://inference.roboflow.com), a computer vision inference server.

[Roboflow Universe](https://universe.roboflow.com), the largest repository of computer vision data on the web with more than 100 million images hosted, uses CLIP embeddings to enable efficient, semantic queries for our dataset search engine.

Without further ado, let’s get started!

## Introduction to CLIP and Roboflow Inference

[CLIP (Contrastive Language-Image Pretraining)](https://blog.roboflow.com/openai-clip/) is a computer vision model architecture and model developed by OpenAI. The model was released in 2021 under an MIT license.

The model was trained “to predict the most relevant text snippet, given an image”. In so doing, CLIP learned to identify the similarity between images and text with the vectors the model uses. CLIP maps images and text into the vector space. This allows vectors to compare and find images similar to a text query, or images similar to another image.

![CLIP (Contrastive Language-Image Pretraining) embeddings diagram](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1db920e5f538c649/6a17f8457b54f95f7a8b3a8d/0fb249f5eba951e06065ca6221f86b7d273b0adb-1662x628.png)

The advancement of multimodal models like CLIP has made it easier than ever to build a semantic image search engine.

Models like CLIP can be used to create “embeddings” that capture semantic information about an image or a text query. Vector embeddings are a type of data representation that converts words, sentences, and other data into numbers that capture their meaning and relationships.

Roboflow Inference is a high-performance computer vision inference server. Roboflow Inference supports a wide range of state-of-the-art vision models, from [YOLO11](https://roboflow.com/model/yolo11) for object detection to [PaliGemma](https://roboflow.com/model/paligemma-2) for visual question answering to CLIP for multimodal embeddings.

You can use Roboflow Inference with a Python SDK, or in a Docker environment.

In this guide, we will use Inference to calculate CLIP embeddings, then store them in an Elasticsearch cluster for use in building an image retrieval system.

## Prerequisites

To follow this guide, you will need:

1. An Elasticsearch instance that supports KNN search
2. [A free Roboflow account](https://app.roboflow.com)
3. Python 3.12+

We have prepared a Jupyter Notebook that you can run on your computer or on Google Colab for use in following along with this guide. Open the [notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/clip-vector-search-roboflow/multimodal-search-clip-embeddings.ipynb).

## Step #1: Set up an Elasticsearch index with KNN support

For this guide, we will use the [Elasticsearch Python SDK](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/index.html). You can install it using the following code:

```
pip install elasticsearch
```

If you don’t already have an Elasticsearch cluster set up, refer to the [Elasticsearch documentation to get started](https://www.elastic.co/guide/en/elasticsearch/reference/current/run-elasticsearch-locally.html).

Once you have installed the SDK and set up your cluster, create a new Python file and add the following code to connect to your client:

```
from elasticsearch import Elasticsearch

client = Elasticsearch(
	"https://localhost:9200",
	 api_key=“your-api-key",
)
```

To run embedding searches in Elasticsearch, we need an index mapping that contains a `dense_vector` property type. For this guide, we will create an index with two fields: a dense vector that contains the CLIP embedding associated with an image, and a file name associated with an image.

Run the following code to create your index:

```
client.indices.create(
	index="knn",
	body={
    	"mappings": {
        	"properties": {
            	"vector": {
                	  "type": "dense_vector",
                	  "dims": 512,
                   "similarity": "cosine",
            	},
            	"filename": {
                	  "type": "keyword",
            	},
        	},
    	},
	}
)
```

The output should look similar to the following:

```
ObjectApiResponse({'acknowledged': True, 'shards_acknowledged': True, 'index': 'knn'})
```

The default index type used with KNN search is L2 Norm, also known as Euclidean distance. This distance metric doesn’t work well for CLIP similarity. Thus, above we explicitly say we want to create a cosine similarity index. CLIP embeddings are best compared with cosine similarity.

For this guide, we will use a CLIP model with 512 dimensions. If you use a different CLIP model, make sure that you set the `dims` value to the number of dimensions of the vector returned by the CLIP model.

## Step #2: Install Roboflow Inference

Next, we need to install Roboflow Inference and supervision, a tool for working with vision model predictions. You can install the required dependencies using the following command:

```
pip install "inference[clip]" supervision
```

This will install both Roboflow Inference and the CLIP model extension that we will use to compute vectors.

With Roboflow Inference installed, we can start to compute and store CLIP embeddings.

## Step #3: Compute and store CLIP embeddings

For this guide, we are going to build a semantic search engine for the COCO 128 dataset. This dataset contains 128 images sampled from the larger Microsoft COCO dataset. The images in COCO 128 are varied, making it an ideal dataset for use in testing our semantic search engine.

To download COCO 128, first [create a free Roboflow account](https://roboflow.com). Then, navigate to the [COCO 128 dataset page on Roboflow Universe](https://universe.roboflow.com/team-roboflow/coco-128/dataset/2), Roboflow’s open computer vision dataset community.

Click “Download Dataset”:

![Compute and store CLIP embeddings part 1](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6ca351104f3bd928/6a17f847e9ea87f4faa9c7b7/9382a8d5d5cba8108720a3923d9afcc896b41692-1020x210.png)

Choose the “YOLOv8” format. Choose the option to show a download code:

![Compute and store CLIP embeddings part 2](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt28e5afc4f5c58e19/6a17f848e3179184cc2d59bb/dce302c1fd0713f47ea7a0039b44b21978508ea2-503x294.png)

Copy the terminal command to download the dataset. The command should look something like this:

```
curl -L "https://universe.roboflow.com…r" > roboflow.zip; unzip roboflow.zip; rm roboflow.zip
```

When you run the command, the dataset will be downloaded to your computer and unzipped.

We can now start computing CLIP embeddings.

Add the following code from your Python file from earlier, then run the full file:

```
from inference.models import Clip
import os

IMAGE_DIRECTORY = "./COCO-128-2/train/images"

# See a full list of supported models at
# https://inference.roboflow.com/foundation/clip/#how-can-i-use-clip-model-in-inference
clip = Clip(model_id="clip/ViT-B-16")

# create index if it doesn't exist for KNN with two fields: vector and file name
for file in os.listdir(IMAGE_DIRECTORY):
	if not file.endswith(".jpg"):
    	continue
 	 
	image_path = os.path.join(IMAGE_DIRECTORY, file)
	vector = clip.embed_image(image_path)

	client.index(
    	index="demo",
    	body={
        	"vector": vector.tolist()[0],
        	"filename": file,
    	}
	)
```

This code will loop through all images in the `train` split of the COCO 128 dataset and run them through CLIP with Roboflow Inference. We then index the vectors in Elasticsearch alongside the file names related to each vector.

It may take 1-2 minutes for the CLIP model weights to download. Your script will pause temporarily while this is done. The CLIP model weights are then cached on your system for future use.

*Note: When you run the code above, you may see a few warnings related to ExecutionProviders. This relates to the optimizations available in Inference for different devices. For example, if you deploy on CUDA the CoreMLExecutionProvide will not be available so a warning is raised. No action is required when you see these warnings.*

## Step #4: Retrieve data from Elasticsearch

Once you have indexed your data, you are ready to run a test query!

To use a text as an input, you can use this code to retrieve an input vector for use in running a search:

```
query_vector = clip.embed_text("coffee")
```

To use an image as an input, you can use this code:

```
query_vector = clip.embed_image(“path/to/image”)
```

For this guide, let’s run a text search with the query “coffee”.

We are going to use a k-nearest neighbours (KNN) search. This search type accepts an input embedding and finds values in our database whose embeddings are similar to the input. KNN search is commonly used for vector comparisons.

KNN search always returns the top k nearest neighbours. If k = 3, Elasticsearch will return the three most similar documents to the input vector.

With Elasticsearch, you can retrieve results from a large vector store in milliseconds.

We can run a KNN search with the following code:

```
import supervision as sv
from PIL import Image

response = client.search(
	index="demo",
	body={
    	"query": {
        	"knn": {
            	"field": "vector",
            	"query_vector": query_vector.tolist()[0],  # The input vector
            	"k": 3
        	}
    	}
	}
)

images = [Image.open(os.path.join(IMAGE_DIRECTORY, i["_source"]["filename"])) for i in response["hits"]["hits"][:3]]

sv.plot_images_grid(images, grid_size=(1, 3))
```

The `k` value above indicates how many of the nearest vectors should be retrieved from each shard. The `size` parameter of a query determines how many results to return. Since we are working with one shard for this demo, the query will return three results.

Our code returns:

![Semantic image search](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc616e4b02f35a241/6a17f84ae3179113ca2d59c3/485c958bfdca283bd4ecce1b1b725cd7243e2d80-1490x454.png)

We have successfully run a semantic search and found images similar to our input query! Above, we can see the three most similar images: a photo of a coffee cup and a cake on a table outdoors, then two duplicate images in our index with coffee cups on tables.

## Conclusion

With Elasticsearch and the CLIP features in Roboflow Inference, you can create a multimodal search engine. You can use the search engine for image retrieval, image comparison and deduplication, multimodal Retrieval Augmented Generation with visual prompts, and more.

Roboflow uses Elasticsearch and CLIP extensively at scale. We store more than 100 million CLIP embeddings and index them for use in multimodal search for our customers who want to search through their datasets at scale. Through the growth of data on our platform from hundreds of images to hundreds of millions, Elasticsearch has scaled seamlessly.

To learn more about using Roboflow Inference, refer to the [Roboflow Inference documentation](https://inference.roboflow.com). To find data for your next computer vision project, check out [Roboflow Universe](https://universe.roboflow.com).

### Frequently Asked Questions

#### What is CLIP (Contrastive Language-Image Pretraining)?

CLIP (Contrastive Language-Image Pretraining) is a computer vision model architecture and model developed by OpenAI. It was trained “to predict the most relevant text snippet, given an image.”

#### What is Roboflow Inference?

Roboflow Inference is a high-performance computer vision inference server.

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