---
title: 'Image Retrieval Using ViT + Generative Pre-trained Transformer (GPT)'
company: Sease
tag: 工程相关
date: 2024-04-18
url: https://sease.io/2024/04/image-retrieval-using-vit-generative-pre-trained-transformer-gpt.html
account: 
origin: harvest3-202607
---
Suppose you have a set of images and you want to retrieve the most relevant ones through a textual query. How to do it?

A popular option is to store in the search engine a textual description of the images and use it for lexical matching with the textual query. Thanks to the latest improvements in Computer Vision and Artificial Intelligence, this description can be generated automatically from the image with what is called **image captioning**.  
In this blog post, we would like to show you an example of this approach. We will start with how to generate an image description exploiting a Vision Transformer (ViT) and a Generative pre-trained Transformer (GPT) and finish with the creation of a Lucene searcher, all accompanied by code examples.

## Feature Extraction With ViT For Image Retrieval

Vision Transformer (ViT) is a pioneering model introduced in 2020 that has significantly transformed the field of Computer Vision. Unlike traditional Convolutional Neural Networks (CNNs), ViT adopts a distinct approach to extracting visual features from input images, leading to remarkable advancements in image understanding.

##### ViT phases for image retrieval

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/05/Immagine1.png?fit=586%2C303&ssl=1) 

ViT Architecture – viso.ai

ViT’s features extraction process encompasses several key steps that enable it to capture meaningful information from images:

* **Input Encoding**: segments the input image into a fixed number of patches. Each patch is linearly projected into a low-dimensional representation called embedding, this refers to a compressed version of data that captures the essential information while reducing the overall dimensionality of the original data. **This segmentation allows ViT to process the image as a sequence of patches that facilitates subsequent analysis**.
* **Positional Encoding**: to preserve the spatial information of each patch, positional encoding is added to the patch embedding, enabling the model to comprehend the relative positions of the patches within the image.**It helps the model gain an understanding of the image’s structure.** The positional encoding scheme typically consists of a set of sinusoidal functions with different frequencies and phases, ensuring its uniqueness.
* **Transformer Encoder**: The patch embeddings and positional encoding are fed into a transformer encoder, comprising multiple layers each containing self-attention mechanisms and feed-forward neural networks. The self-attention mechanism operates by calculating the attention weights between patches and computing the dot product between a query vector, a key vector, and a value vector for each patch. This dot product measures the similarity or relevance between patches. **The self-attention mechanism enables the model to attend to various patches, learn their dependencies, and enhance its ability to discern meaningful visual patterns.**
* **Classification Head**: **the final layer of the transformer produces the class predictions for each patch embedding in the given image.** By leveraging the learned features and contextual information acquired through the transformer encoder, ViT enables accurate image classification and semantic understanding.

## Implementation Of Image Captioning

Let’s dive into the implementation of image captioning. We use the **[vit-gpt2-image-captioning](https://huggingface.co/nlpconnect/vit-gpt2-image-captioning)**pre-trained model provided by Huggingface; which is composed of a Vision Transformer to extract features from images (encoder) and a Generative pre-trained Transformer to convert the features into a textual representation of the input images (decoder).  
In particular, GPT is responsible for creating a description based on the classes returned by ViT.

To do that, we use **Python**.

1. Put the images (e.g. [Flickr Image Dataset](https://www.kaggle.com/datasets/hsankesara/flickr-image-dataset)) you want to transform in an accessible folder (e.g. *images/*)
2. Import the needed dependencies, **pytorch,**and **transformers**:

```
				
					import glob
import torch
import os
from PIL import Image
from transformers import VisionEncoderDecoderModel, GPT2TokenizerFast, ViTImageProcessor
				
			
```

3. Check for the presence of a **CUDA**device, otherwise, use CPU and initialize the *ViT+GPT* *model*, the corresponding *tokenizer*, and *image\_processor*:

```
				
					# check if the CUDA device is available
device = "cuda" if torch.cuda.is_available() else "cpu"

# load the pre-trained model
model = VisionEncoderDecoderModel
        .from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        .to(device)
tokenizer = GPT2TokenizerFast
            .from_pretrained("nlpconnect/vit-gpt2-image-captioning")
image_processor = ViTImageProcessor
                .from_pretrained("nlpconnect/vit-gpt2-image-captioning")
				
			
```

Here:

* *[model](https://huggingface.co/docs/transformers/model_doc/vision-encoder-decoder)* is the ViT + GPT model used for image captioning
* *[tokenizer](https://huggingface.co/docs/transformers/main_classes/tokenizer)* is the component needed by GPT to generate the textual representation of the image
* *[image\_processor](https://huggingface.co/docs/transformers/main_classes/image_processor)* is the component in charge of preparing input features for the vision model. This includes transformations such as resizing, normalization, and conversion to PyTorch, TensorFlow, Flax, and Numpy tensors.

4. Define a function that calls the model methods to get the **caption**from an image:

```
				
					# get description from image
def get_caption(model, image_processor, tokenizer, image_path, device):
    image = Image.open(image_path)
    # preprocess the image
    img = image_processor(image, return_tensors="pt").to(device)
    # generate the description from the returned tensor
    output = model.generate(**img)
    # decode the output of the model
    caption = tokenizer.batch_decode(output, skip_special_tokens=True)[0]
    return caption
				
			
```

5. Process all the images inside a given folder and**create**the **image\_collection.txt file** containing all the corresponding captions that will be indexed in the Lucene searcher. The document format we choose to use is the TREC format:

```
				
					images_path = "images\\*"
    
images_list = [f for f in glob.glob(images_path)]
 
total = len(images_list)
i = 1
for img in images_list:
    text = get_caption(model, image_processor, tokenizer, img, device)
    print("%i/%i - %s" % (i, total, text))
    img_id = os.path.basename(img)
    doc_str = "&lt;DOC&gt;\n&lt;DOCNO&gt;" + i + "&lt;/DOCNO&gt;\n&lt;DOCID&gt;" + img_id + "  
               &lt;/DOCID&gt;\n&lt;TEXT&gt;\n" + text + "\n&lt;/TEXT&gt;\n&lt;/DOC&gt;\n"
    with open("docs/image_collection.txt", "a") as text_file:
        text_file.write("%s" % doc_str)
    i = i + 1
				
			
```

For each image, the output will be a <DOC> element with this format:

```
				
					&lt;DOC&gt;
  &lt;DOCNO&gt;1&lt;/DOCNO&gt;
  &lt;DOCID&gt;image_name.jpg&lt;/DOCID&gt;
  &lt;TEXT&gt;
    image caption text
  &lt;/TEXT&gt;
&lt;/DOC&gt;
				
			
```

Examples of images with respective predicted descriptions:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/05/Immagine2.jpg?fit=262%2C262&ssl=1) 

Dogs and a ball in a yard – hsankesara

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/05/Immagine3-1.jpg?fit=336%2C224&ssl=1) 

A person on a rock with a camera – hsankesara

## Implementation Of An Image Searcher On Lucene

Given the **image\_collection.txt file** with all the docs containing the description of the images and the images’ file names, we need to implement the actual retrieval system. To accomplish this, the implementation leverages the Java library of Lucene, which facilitates the creation of the retrieval system. The main components of the system consist of the *Parser*, *Analyzer*, *Indexer*, and *Searcher*:

* **Parser**: removes tags from the document;
* **Analyzer**: processes the documents’ text into a stream of tokens. Used by Indexer and Searcher;
* **Indexer**: builds the inverted index given the streams of tokens generated by the Analyzer on each parsed document;
* **Searcher**: searches in the index for the documents related to a given analyzed query.

```
				
					// image_collection.txt path folder
final String docPath = "experiment/docs";
// index folder
final String indexPath = "experiment/index_images";
// path to the queries
final String queries = "experiment/queries/queries.txt";
// results folder
final String resultsPath = "experiment/results";
// result file name
String resultID = "result_image_retrieval";

// setup the textual analyzer that will process our description field
final Analyzer textAnalyzer = new EnglishAnalyzer();
// similarity function to use during search
final Similarity sim = new BM25Similarity();
// max number of documents to retrieve
final int maxDocsRetrieved = 1000;

// setup the indexer
final Indexer i = new Indexer(textAnalyzer, sim, indexPath, docPath, Parser.class);
// create the index
i.index(); 

// setup the searcher
final Searcher s = new Searcher(textAnalyzer, sim, indexPath, topics, resultID, resultsPath, maxDocsRetrieved);
// performs the searching
s.search(); 
				
			
```

In the code above *Indexer* and *Searcher* are only placeholder classes for this explanation. You can therefore choose to implement whatever *Indexer* and *Searcher* you like.  
In this case, the program saves the ranked results within the **run\_image\_retrieval.txt file**.  
  
Here is the first result for the query *“Dog running”* using our implementation of *Indexer* and *Searcher*:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/05/Immagine4.jpg?fit=257%2C343&ssl=1) 

Dog running – hsankesara

## Conclusions

In this blog post we have seen how to retrieve images through a textual query. We have described how the Vision Transformer model works and how it can be used, in combination with a Generative pre-trained Transformer, for our task. We have also shown how to do image captioning exploiting a ViT+GPT model and how to implement a Lucene search engine for image retrieval through code examples.

## Do You Want To Be Published?​

This blog post is part of our collaboration with the University of Padua. If you are a University student or professor and want to collaborate, contact us through e-mail.

[Click here](mailto:info@sease.io)

## Do You Want To Be Published?

This blog post is part of our collaboration with the University of Padua. If you are a University student or professor and want to collaborate, contact us through e-mail.

[Click Here](mailto:info@sease.io)