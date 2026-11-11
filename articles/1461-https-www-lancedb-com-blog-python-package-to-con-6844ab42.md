---
title: 'https://www.lancedb.com/blog/python-package-to-convert-image-datasets-to-lance-type'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/python-package-to-convert-image-datasets-to-lance-type
account: 
origin: en-rss
---
# Python Package to convert image datasets to Lance type

[Vipul Maheshwari](/author/vipul-maheshwari)

•

December 9, 2024

•

[Engineering](/category/engineering)

![1461-https-www-lancedb-com-blog-python-package-to-con-6844ab42-fig-001](../images/1461-https-www-lancedb-com-blog-python-package-to-con-6844ab42/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

A few months ago, I wrote two articles on how the Lance format can supercharge your machine-learning workflows. In the first, I showed how Lance’s columnar storage can make handling large image datasets much more efficient for ML workflows. Then, I followed up with a guide on converting datasets like [cinic](https://www.kaggle.com/datasets/vipulmaheshwarii/cinic-10-lance-dataset) and [mini-imagenet](https://www.kaggle.com/datasets/vipulmaheshwarii/mini-imagenet-lance-dataset) into Lance format using a custom Python script in [Google Colab](https://colab.research.google.com/drive/12RjdHmp6m9_Lx7YMRiat4_fYWZ2g63gx?usp=sharing). While that worked well, it was a bit manual.

Some of my friends are lazy but excited enough to run the Colab and use the Lance formatted datatype for some of their experiments. Being a good friend, I’m excited to share a much easier solution: the `lancify` Python package.

It’s literally just running one command and boom—your image datasets are in Lance format, ready to go. And, just between us, it makes my life a lot easier, too.

![1461-https-www-lancedb-com-blog-python-package-to-con-6844ab42-fig-002](../images/1461-https-www-lancedb-com-blog-python-package-to-con-6844ab42/figure-002.avif)

## Installing the package

Before diving into the conversion process, let’s install the `lancify` package. You can easily install it via pip:

```
pip install lancify
```

## Converting Your Image Dataset to Lance

Once you’ve installed the package, converting any image dataset to the Lance format is as simple as running the following Python code. The `lancify` package abstracts away the complexity of running the Colab notebooks manually:

```
from lancify.converter import convert_dataset

# Define the path to your image dataset
image_dataset_path = 'cards-classification'
resize_dimensions = (256, 256)  # Example resize dimensions
splits = ["train", "test", "valid"]

convert_dataset(
    dataset_path=image_dataset_path,
    batch_size=10,  # You can adjust the batch size as needed
    resize=resize_dimensions,  # Pass resize dimensions if you want to resize images
    splits=splits
)
```

For this demonstration, I have used this [dataset](https://www.kaggle.com/datasets/gpiosenka/cards-image-datasetclassification), which provides flexibility in terms of image resizing and dataset splits. The image resizing is optional; by default, the images are processed with their original dimensions. However, if needed, you can specify a target size, such as 256x256, by passing the desired dimensions. If you prefer to keep the original size, simply pass `None` for the resize parameter. Regarding dataset splits, if the dataset includes predefined divisions like training, testing, and validation sets, you can pass a list specifying the relevant splits.

For [datasets](https://www.kaggle.com/datasets/jehanbhathena/weather-dataset) that do not have predefined splits, the images are organized by classification labels. In such cases, you only need to provide the dataset path and a single lance file will be generated, containing all the images with their corresponding labels. This makes sure that the various kinds of image datasets are handled properly whether they include splits or not.

```
from lancify.converter import convert_dataset

image_dataset_path = 'weather-classification-data'

convert_dataset(
    dataset_path=image_dataset_path,
    batch_size=10,  # You can adjust the batch size as needed
)
```

The `convert_dataset` function automatically handles the following:

1. **Reading the image data**: It reads image files and their metadata (filename, category, data split).
2. **Converting to Lance**: The images are converted into the Lance format with the proper schema.
3. **Saving the Lance files**: Lance files are saved for each dataset split (train, test, validation) if there are splits in the dataset, if not then a single Lance file is saved with the combined data with an adequate schema to segregate the data with the respective labels.

This method is far more concise than manually iterating over directories, creating schemas, and writing to lance files as we did in the previous version using raw Google Colab.

## Install CLI SDK

In addition to using the `lancify` package programmatically through the imported function, you can also leverage the CLI SDK to convert your image datasets. The SDK offers a CLI for the `lancify`.

To use the CLI, all you need to do is install the package with `pip install lancify` and then run the `lancify` command in your terminal and follow the args.

This is how it looks:

*CLI usage for lancify*

## What’s happening behind the scenes?

To give you a better understanding, here’s a brief overview of what happens when you use `lancify`:

* **Image Data**: The package reads images from your dataset directory and converts them into a binary format.
* **Metadata Extraction**: Metadata such as the image’s filename, category (label), and data split (train/test/validation) are automatically extracted.
* **PyArrow RecordBatch**: The image data and metadata are packaged into a PyArrow **`RecordBatch`** for efficient columnar storage.
* **Lance Dataset Creation**: These **`RecordBatch`** objects are then written to Lance datasets optimized for performance and storage.

This process mirrors the manual steps we previously took but in a much more user-friendly manner, significantly reducing the boilerplate code that was necessary before when you had to manually handle the [colab](https://colab.research.google.com/drive/12RjdHmp6m9_Lx7YMRiat4_fYWZ2g63gx?usp=sharing#scrollTo=93qlCg6TpcW-).

## Loading your dataset into pandas

Once your image dataset has been converted into the lance format, you can seamlessly load it into Pandas data frames to do all kinds of stuff. Here’s how to do it for the `card-classification` training lance file.

```
import lance
import pandas as pd

# Load Lance dataset
ds = lance.dataset('cards-classification/cards-classification_train.lance')
table = ds.to_table()

# Convert Lance table to Pandas dataframe
df = table.to_pandas()
print(df.head())
```

This is a simple and efficient way to convert your image datasets to the lance format using the `lancify` package and it integrates smoothly into your deep-learning projects.

Switching to the Lance format speeds up and improves your data pipelines, especially when handling large image datasets. Install the package and run a simple script to convert your datasets—it’s easy and straightforward.

![1461-https-www-lancedb-com-blog-python-package-to-con-6844ab42-fig-003](../images/1461-https-www-lancedb-com-blog-python-package-to-con-6844ab42/figure-003.avif)

Just this small change can really speed up your machine learning workflows—data loading and processing become much quicker, which means your models train faster. If you’re looking for more ideas, there are plenty of other [deep-learning recipes](https://github.com/lancedb/lance-deeplearning-recipes) built on Lance.

Trust me, it’s worth it! 🤗

![1461-https-www-lancedb-com-blog-python-package-to-con-6844ab42-fig-004](../images/1461-https-www-lancedb-com-blog-python-package-to-con-6844ab42/figure-004.avif)

[Vipul Maheshwari](/author/vipul-maheshwari)

ML Engineer and FinTech enthusiast specializing in AI agents, predictive modeling, and financial technology applications.

![1461-https-www-lancedb-com-blog-python-package-to-con-6844ab42-fig-005](../images/1461-https-www-lancedb-com-blog-python-package-to-con-6844ab42/figure-005.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1461-https-www-lancedb-com-blog-python-package-to-con-6844ab42-fig-006](../images/1461-https-www-lancedb-com-blog-python-package-to-con-6844ab42/figure-006.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1461-https-www-lancedb-com-blog-python-package-to-con-6844ab42-fig-007](../images/1461-https-www-lancedb-com-blog-python-package-to-con-6844ab42/figure-007.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb