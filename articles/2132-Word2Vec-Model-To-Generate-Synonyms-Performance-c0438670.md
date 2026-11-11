---
title: 'Word2Vec\xa0Model\xa0To\xa0Generate\xa0Synonyms\xa0– Performance Testing'
company: Sease
tag: 查询理解
date: 2023-08-03
url: https://sease.io/2023/08/word2vec-model-to-generate-synonyms-performance-tests.html
account: 
origin: harvest3-202607
---
This blog post series explores our contribution to Apache Lucene, which integrates a Word2Vec model with the text analysis pipeline to generate synonyms on the fly. In particular:

* [Introduction to synonym expansion technique](https://sease.io/2023/04/word2vec-model-to-generate-synonyms-on-the-fly-in-apache-lucene-introduction.html) and state of the art in Apache Lucene and Solr
* [Word2Vec algorithm](https://sease.io/2023/06/word2vec-model-to-generate-synonyms-on-the-fly-in-apache-lucene-w2v-algorithm.html) and our implementation
* Our Lucene Contribution, showing some examples at both index and query time [*coming soon…*]

In this blog post, we just want to give you an overview of the performances given by our implementation in terms of time and memory.

## Test Configuration

Our aim is to create a word2vec model that will be trained using the data we want to index. Once the training is complete, the resulting output vectors for each word will be used to identify synonyms.

Our source of documents for training data was the Italian Wikipedia. We employed the [Wikipedia extractor](https://github.com/bwbaugh/wikipedia-extractor), which is a Python tool that extracts plain text from a Wikipedia database dump and eliminates any additional information or annotations such as images, tables, references, and lists present in the Wikipedia pages. A sample document is:

```
				
					&lt;doc id="2" url="http://it.wikipedia.org/wiki/Armonium"&gt; 
Armonium. 
L'armonium (in francese, “harmonium”) è uno strumento musicale azionato con una tastiera, detta manuale. Sono stati costruiti anche alcuni armonium con due manuali. 
... 
... 
&lt;/doc&gt;
				
			
```

Following that, we indexed all the downloaded documents in a Lucene index named *“italian\_wiki\_data”*, where the text of the Italian Wikipedia pages was indexed in the *“text”* field.

We, therefore, trained a Word2Vec model using our Java tool `LuceneWord2VecModelTrainer` and finally, we used the trained models for testing the synonym expansion at both index and query time.

Local tests have been performed using a *Mac OS* laptop.

## Model Training

We set up word2vec using [Deeplearning4j](https://deeplearning4j.konduit.ai/), a deep learning library for the Java virtual machine (JVM), that has an out-of-the-box implementation of word2vec, based on the Continuous Skip-gram model.

A piece of example code (you can find the whole code implementation [here](https://github.com/SeaseLtd/LuceneWord2VecModelTrainer/tree/main/src/main/java/io/sease/tools/word2vec)):

```
				
					public class Config {
    private final String indexPath;
    private final String fieldName;
    private final String modelFilePath;
} #1

FieldValuesSentenceIterator iterator = new FieldValuesSentenceIterator(config); #2

Word2Vec vec = new Word2Vec.Builder() #3
   .layerSize(100)
   .windowSize(5)
   .iterate(iterator) #4
   .build(); 
vec.fit();
				
			
```

**#1** This code snippet defines a Java class called `Config` that has three private instance variables: **indexPath**: path to a Lucene index, “*italian\_wiki\_data*” in our case  
**fieldName**: specific field to fetch the values from, “*text”*in our case  
**modelFilePath**: name of the output model, i.e. *wiki-ita-w2v-model.zip*

These will be the required parameters to be passed to perform the training:

```
				
					java -jar build/libs/LuceneWord2VecModelTrainer.jar -p &lt;index_path&gt; -f &lt;field_name&gt; -o &lt;model_file&gt;
				
			
```

**#2** A FieldValuesSentenceIterator is built to read stored values from the Lucene index.  
In this example, the text of the Italian Wikipedia pages was indexed in the *“text”* field and we, therefore, fetch the sentences and words to be used for training the word2vec model from that field.  
An instance of the Config class is passed to a constructor for a FieldValuesSentenceIterator that uses the configuration settings stored in the Config object to iterate over sentences associated with specific field values in the index.  
**#3** It creates the configuration for word2vec, with a set of parameters (layerSize, windowSize, etc..)  
**#4** It sets word2vec to iterate over the selected corpus, i.e. FieldValuesSentenceIterator is passed to the word2vec’s implementation.

Once the training is finished, the tool generates as output a Word2Vec model named “wiki-ita-w2v-model.zip”, which has a **size** of approximately **375 MB**.  
The model can now be utilized for testing the Lucene indexing and searching process.  
With this new feature, the search engine will be able to learn to generate synonyms from the data it handles.

For more info about the model training, you can have a look at our GitHub project [here](https://github.com/SeaseLtd/LuceneWord2VecModelTrainer).

## Index Time Results

As you should already know, synonyms can be applied both at indexing and query time.

Using synonyms at ***indexing time*** has some **disadvantages**:

* pollution of terms document frequencies in the index (a word will appear in a document even if initially it was not)
* need to reindex if synonyms change or get added
* potential problems with multi-term synonyms and phrase queries
* index size expansion

It is not an entirely bad practice and there may be situations where you want to expand synonyms at index time to manipulate document frequencies; however, doing it at query time is generally the preferred approach.

The use of synonyms at indexing time can be an expensive operation since it requires expanding the synonyms for every single word in your corpus.

In fact, from our experiments, we saw that indexing roughly**25MB** of documents (2.539 pages) required about **4 minutes**; while indexing about 4GB of documents (1.821.573 pages) would take far too many hours and is therefore not recommended.

This is the text analysis we used for the test:

```
				
					Analyzer analyzer = CustomAnalyzer.builder()
         .withTokenizer(ClassicTokenizerFactory.NAME)
         .addTokenFilter(StopFilterFactory.NAME, "words", "stopwords_it.txt", "format", "snowball", "ignoreCase", "true")
         .addTokenFilter(Word2VecSynonymFilterFactory.NAME, "model", "wiki-ita-w2v-model.zip")
         .addTokenFilter(FlattenGraphFilterFactory.NAME)
         .addTokenFilter(LowerCaseFilterFactory.NAME)
         .build();
				
			
```

The heap memory usage of our Java application was tracked using VisualVM, and the accompanying graph displays the changes over the course of its execution, for indexing 25MB data:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-03-07-alle-14.01.01.png?fit=800%2C472&ssl=1)

If we index the same documents without performing the synonym expansion these are the performances:  
25MB data: ~5 seconds  
4GB data: ~7 minutes

The memory profile for indexing 25MB of data without using synonym expansion is presented below:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-03-07-alle-14.26.05.png?fit=800%2C476&ssl=1)

**Our advice is to use the Word2VecSynonymFilterFactory at index time with caution and especially only if you have few documents to index or small fields.**

## Query Time Results

To evaluate the performance of the search functionality, we created a file consisting of 1000 random terms that were used as queries. The objective was to assess the synonyms expansion feature for each term in the file.

This is the text analysis we used for the test:

```
				
					Analyzer analyzer = CustomAnalyzer.builder()
         .withTokenizer(ClassicTokenizerFactory.NAME)
         .addTokenFilter(StopFilterFactory.NAME, "words", "stopwords_it.txt", "format", "snowball", "ignoreCase", "true")
         .addTokenFilter(Word2VecSynonymFilterFactory.NAME, "model", "wiki-ita-w2v-model.zip")
         .addTokenFilter(LowerCaseFilterFactory.NAME)
         .build();
				
			
```

The Java code for this test reads input from the text file containing 1000 query terms, parses each term using a Lucene parser, expands synonyms for each term, and then executes a search using the parsed query. The search returns the top 10 documents matching the query.  
The whole process was executed in **1 minute and 30 seconds** and in particular:

* the custom analyzer builder was executed in ~1 minute
* the average time for synonym expansion was 0.2823 ms
* the average memory for synonym expansion was 458.40 MB
* the average time to find the top 10 hits for a query with synonyms was 6.882 ms

We monitored our Java application using VisualVM and the following is the graph showing the heap memory usage for the duration of this application’s execution:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-03-07-alle-16.05.19.png?fit=800%2C483&ssl=1)

So, you have to keep in mind that more or less the size of the word2vec model (in our case the zip file is 375 MB) will impact almost 1:1 with the memory occupied by Lucene.

Regarding the time required to expand the synonyms of a single term and return the first 10 documents for that query, it took around 0.28 ms and 7 ms, respectively. These are reasonable and usable times.

## We did a talk at Berlin Buzzwords 2022 about this!

Check out the talk about this project at Berlin Buzzwords 2022

[Click Here](https://sease.io/2022/05/sease-at-berlin-buzzwords-2022.html)