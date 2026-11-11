---
title: 'Argument Retrieval for Controversial Questions'
company: Sease
tag: 召回
date: 2023-05-04
url: https://sease.io/2023/05/argument-retrieval-for-controversial-questions.html
account: 
origin: harvest3-202607
---
Hello readers!  
In this blog post, we discuss a possible approach to solve the big challenge of **argument retrieval for controversial questions**. This challenge has been proposed as one of the possible tasks by [CLEF](https://clef2022.clef-initiative.eu/) in 2022.  
For more information, you can refer to our published [paper](https://ceur-ws.org/Vol-3180/paper-249.pdf).

## Introduction to the Problem

Nowadays, most of us use Search Engines on a daily basis to retrieve any kind of information. Even though they have been studied a lot, there still exist challenges such as retrieving arguments for controversial questions.  
For example, given the question “Is human activity primarily responsible for global climate change?”, we want to retrieve relevant arguments that can be either supporting or opposing the question’s topic.

In [Task 2](https://touche.webis.de/clef22/touche22-web/argument-retrieval-for-controversial-questions.html) proposed by CLEF in 2022, the goal is to retrieve relevant pairs of coherent sentences (both sentences in each pair **must have the same stance**) from a collection of arguments given some input topics. It is also essential that the pairs of retrieved sentences contain evidence pertaining to the topic. An example of a topic is given below:

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/12/topic.png?fit=800%2C210&ssl=1)

**Figure 1**: An example of a topic titled “*Should teachers get tenure?*”

The collection can be found at this [link](https://zenodo.org/record/6873574#.Y3JG0XVKg5k) while the topics can be downloaded [here](https://zenodo.org/record/6801440/files/topics.xml?download=1).

## How a Search Engine Works

First of all, we need to understand how a Search Engine generally works. Therefore we provide here a brief overview.

The aim of a Search Engine is to retrieve a ranked list of documents given a query such that the retrieved documents are relevant according to the input query.

In a Search Engine, there are various components that work together forming a **pipeline**.  
The collection of documents is firstly parsed transforming it into structured data. Data are then processed through an Analyzer and finally indexed by means of an **Inverted Index**. The Inverted Index is a data structure containing mappings from terms to documents.

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/11/wp1.png?fit=800%2C136&ssl=1)

**Figure 2**: From the Collection of documents to the processed Indexed Collection

Once the collection is indexed, it is possible to retrieve information through **queries**. Queries will usually undergo the same processing steps as the collection with the possible addition of other techniques (e.g. Query Expansion). The query terms are matched against the ones of the Inverted Index and the corresponding documents will be retrieved.

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/11/wp-2.png?fit=745%2C143&ssl=1)

**Figure 3**: From the Query to the ranked list of relevant documents

## Our System

The system we designed is divided into different components which are:

* Parser
* Analyzer
* Indexer
* Searcher

We will now discuss the techniques used in each of the components.

##### The Parser

The **Parser**needs to extract as much information as possible in a structured way. We decided to parse each document obtaining these fields:

* Document id
* Hash-table of premise ids and their texts
* Premise stances
* Hash-table of conclusion ids and their texts
* Context

In particular, we combined the power of **Regular Expressions** and [Jackson JSON](https://github.com/FasterXML/jackson) library to parse the data.  
Here we show an example of a document composed of **5 fields**: id, conclusion, premises, context, and sentences (notice that the context has been cut to make the document representation more readable).

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/12/document_example-1.png?fit=800%2C208&ssl=1)

**Figure 4**: An example of a document about the war in Iraq

As you can see it’s a Json-like document but not well formatted so the parsing phase requires more advanced data processing.

##### The Analyzer

We implemented a parametric Analyzer in such a way that it can perform different combinations of operations such as **Tokenization**, **Stemming**, usage of **Stop-Lists**, and **Filtering**.  
We created our Stop-Lists by inspecting the whole collection and retrieving the most frequent 100 terms in the Context field and in the Sentences field of the corpus. Thus we created 2 different Stop-Lists for contexts and sentences respectively.

##### The Indexer

We indexed the collection into 2 separate folders:

* *First folder*: it contains document contexts and sentences ids
* *Second folder*: it contains sentence ids and values

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/11/wp-3.png?fit=800%2C352&ssl=1)

**Figure 5**: From each Parsed Document to its structured indexed version into 2 separate folders

This has been done to drastically reduce the size of the indexed collection avoiding repeating the context for each sentence.

We also noticed that in the collection there were sentences containing only noise (e.g. random characters, emojis, Arabic words…), therefore we wanted to avoid indexing them. To do so, we thought that we could only keep sentences that are written in English. Thus we decided to apply [Apache OpenNLP](https://opennlp.apache.org/) to detect each sentence’s language and keep only the ones resulting to be English. In this way, we detected approximately 100’000 sentences that could be marked as **spam**and thus not indexed.

##### The Searcher

The Searcher aims at retrieving the best coherent pairs of sentences for each topic. It uses techniques such as **Query Expansion**, **Term Weighting** and **Document Re-Ranking**.  
In particular, we process each topic’s title creating 2 different queries with specific duties:

* *First query*: retrieve relevant sentences based only on contexts
* *Second query*: retrieve relevant sentences based on their content

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/11/wp-5.png?fit=800%2C310&ssl=1)

**Figure 6**: Given a Topic, return a ranked list of sentences supporting or opposing that Topic

Here we propose the **pseudocode**illustrating how we combined the results of the 2 queries together to obtain the most relevant 2000 sentences that will then be combined into pairs:

```
				
					function getBest2000RankedSentences() :
    
    # retrieved sentences from the collection's contexts field with their
    # corresponding weights
    listSentences1 ← firstQuery.execute()
    
    # retrieved sentences from the collection's sentences field with their
    # corresponding weights
    listSentences2 ← secondQuery.execute() 
    
    W1 ← weight parameter for contexts
    W2 ← weight parameter for sentences
    
    # the final ranked list of 2000 sentences
    finalListSentences ← empty

    ∀ sentence ∈ listSentences2 :
        if sentence ∈ listSentences1 :

            # if the sentence has been retrieved from both the queries then
            # we increase its weight according to the parameters
            sentence.weight ← sentence.weight * W2 +  
            listSentences1.get(sentence).weight * W1
        
        finalListSentences.add(sentence)

    # order the sentences
    finalListSentences.orderByDescendingWeight()

    # keep only the first 2000 sentences
    finalListSentences=finalListSentences.keepOnlyFirst2000()
    
    return finalListSentences
				
			
```

The weights ***W1***and***W2***in the pseudocode are hyper-parameters. We thought that generally, sentences should have more importance with respect to contexts, so **we decided to set the weights manually, respectively to 0.8 and 1**.

## Query Expansion

We used the [Wordnet](https://wordnet.princeton.edu/) thesaurus to find **synonyms**related to terms in the queries.

We applied the **POS-Tagger** provided by [Apache OpenNLP](https://opennlp.apache.org/) (**en-pos-maxent.bin** that can be found [here](https://opennlp.sourceforge.net/models-1.5/)) to obtain the Part-Of-Speech for each term. In this way, we can find the correct synonyms from the [Wordnet](https://wordnet.princeton.edu/) thesaurus and add them to the query with different weights forming a Boolean Query.

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/11/wp-6.png?fit=800%2C280&ssl=1)

**Figure 7**: From each analyzed term, extract a list of synonyms and build a weighted Boolean Query

## Term Weighting

Before processing every query with the Analyzer, we wanted to assign to each query term a **weight**based on its discriminant power in the collection.  
To do so, we created our own coefficient called **I-Coefficient** which gives more importance to terms appearing many times in a small number of documents. It can be calculated in the following way:

```
𝐼𝑐𝑜𝑒f (𝑡𝑜𝑘𝑒𝑛𝑖) = ( 1 – #𝑑𝑜𝑐(𝑡𝑜𝑘𝑒𝑛𝑖) / 𝑡𝑜𝑡𝑑𝑜𝑐 ) · [ 1 – #𝑑𝑜𝑐(𝑡𝑜𝑘𝑒𝑛𝑖) / (2* #𝑡𝑜𝑘𝑒𝑛𝑖 ) ]
```

with

***#*𝑑𝑜𝑐(𝑡𝑜𝑘𝑒𝑛𝑖)** = *number of documents in the collection containing the term*𝑡𝑜𝑘𝑒𝑛𝑖  
**𝑡𝑜𝑡𝑑𝑜𝑐** = *total number of documents in the collection*  
***#*𝑡𝑜𝑘𝑒𝑛𝑖** = *total number of occurrences of*𝑡𝑜𝑘𝑒𝑛𝑖 *in the collection*

## Document Re-Ranking

Document **Re-Ranking** involves applying different operations to rank the set of retrieved document once again and keep only a **smaller subset** composed of the most relevant ones.

We used IBM [Project Debater](https://research.ibm.com/interactive/project-debater/), which is an AI system developed by IBM, to re-rank our sentences by means of the following APIs:

* *Pro/Cons API*: This API is used to understand if a sentence most strongly opposes the topic or most strongly supports it. We applied it to get the stances of the sentences.
* *Evidence Detection API*: This API is used to determine if a sentence is likely to contain evidence relating to a topic and vice versa. This was employed to reassign weights to our sentences and rank them once again.

## Our Set-up

You can find the repository of the project at this [link](https://bitbucket.org/upd-dei-stud-prj/seupd2122-intseg/src/master/).

To test our system we used a machine with the following specs:

* *CPU*: Intel i5-8600k not overclocked
* *GPU*: Zotac Nvidia Gtx 1060 AMP 6 GB
* *RAM*: 32 GB ddr4 3000 MHz
* *SSD*: Samsung 960 evo 1 TB nvme, sequential read: 3,200MB/s, sequential write: 1,900MB/s

## Results for the 2022 Task

The system was initially tested with the 2021 topics that can be found [here](https://zenodo.org/record/6873566#.Y3KdinbMKUk). This allowed us to try different configurations of the parameters to understand which could work better before the actual submission for this year’s Task.

The submitted system configurations are the following:

![](https://i0.wp.com/sease.io/wp-content/uploads/2024/02/result1.jpg?fit=800%2C364&ssl=1)

**Table 1**: The runs submitted to CLEF

Here we provide the results obtained by the best systems proposed by the participants in the 2022 task (our team is named **Daario Naharis** since it was required to name it after an actor or superhero):

![](https://i0.wp.com/sease.io/wp-content/uploads/2024/02/results2.jpg?fit=800%2C229&ssl=1)

**Table 2**: Best-scoring run of each team for relevance evaluation

![](https://i0.wp.com/sease.io/wp-content/uploads/2024/02/results3.jpg?fit=800%2C214&ssl=1)

**Table 3**: Best-scoring run of each team for quality evaluation

![](https://i0.wp.com/sease.io/wp-content/uploads/2024/02/results4.jpg?fit=800%2C223&ssl=1)

**Table 4**: Best-scoring run of each team for coherence evaluation

As we can see, our system performed quite well placing itself second, first, and first according to the relevance, quality, and coherence evaluations. For the complete rankings visit this [website](https://touche.webis.de/clef22/touche22-web/argument-retrieval-for-controversial-questions.html).

## Statistical Analysis

To see if the configurations of our system were significantly different according to some evaluation measures, we performed Statistical Analysis by means of ANOVA.

We provide the plots obtained by ANOVA considering the configurations provided to CLEF:

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/11/wp-7.png?fit=800%2C384&ssl=1)

**Figure 8**: ANOVA tables (the means of runs 2 and 5 in the X-axis are significantly different)

## Discussion of the Results and possible improvements

Our system is far from perfect. To improve it we consider extracting information also by each topic’s description in such a way that we don’t introduce too many noisy terms.

Moreover, we can apply a**pseudo-relevance feedback** approach, in which after a first search phase the best-ranked documents retrieved by our systems are used to reformulate the query introducing important terms, thus possibly increasing the effectiveness of our system.

Finally introducing large language models like [BERT](https://arxiv.org/abs/1810.04805) in our pipeline could improve our performance since **machine learning** will probably be a key factor in further improving all the IR systems.

## Summary

In this post, we saw a possible system to solve the challenge of argument retrieval for controversial questions and how the system performed according to the corresponding Task proposed by CLEF in 2022.

## Do You Want To Be Published?

This blog post is part of our collaboration with the University of Padua. If you are a University student or professor and want to collaborate, contact us through e-mail.

[Click Here](mailto:info@sease.io)