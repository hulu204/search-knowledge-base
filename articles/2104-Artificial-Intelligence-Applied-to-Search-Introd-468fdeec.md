---
title: 'Artificial Intelligence Applied to Search: Introduction'
company: Sease
tag: 工程相关
date: 2021-07-07
url: https://sease.io/2021/07/artificial-intelligence-applied-to-search-introduction.html
account: 
origin: harvest3-202607
---
The main objective of this survey is to explore the state of the art of artificial intelligence (AI) applied to search in the open source world.  
1 – We start with an **introduction**, explaining what AI means in Information Retrieval and how it can improve search systems.  
2 – For the second episode we move to [OpenSearch and its neural search plugin](https://sease.io/2022/12/opensearch-neural-search-plugin-tutorial.html), giving a detailed description of it through our end-to-end experience.  
3 – The third episode explores Apache Solr, showing in practice [how you use Apache Solr to index and search vectors and then run a full end-to-end neural search](https://sease.io/2023/01/apache-solr-neural-search-tutorial.html).  
4 – The fourth episode is about Vespa, which provides a comprehensive tutorial on implementing[Neural Search in this search technology](https://sease.io/2023/02/vespa-neural-search-tutorial.html), from documents and model preparation to embedding creation and k-NN queries.  
5 – In the fifth episode we show in practice how you can use [Elasticsearch to run a full end-to-end neural search](https://sease.io/2023/03/elasticsearch-neural-search-tutorial.html).  
6 – the sixth and last episode explains all the steps required to [implement Text Embedding and Vector Search directly in Elasticsearch](https://sease.io/2023/07/elasticsearch-relevance-engine-combining-ai-with-elastics-text-search.html) in a very simple way.

So, without further ado, let’s start!

## How does Artificial Intelligence impact search?

> Artificial intelligence (AI) is intelligence demonstrated by machines, unlike the natural intelligence displayed by humans and animals, which involves consciousness and emotionality.
>
> Wikipedia
> [Tweet](https://twitter.com/intent/tweet?text=Artificial+intelligence%C2%A0%28AI%29+is%C2%A0intelligence%C2%A0demonstrated+by%C2%A0machines%2C+unlike+the%C2%A0natural+intelligence%C2%A0displayed+by+humans%C2%A0and%C2%A0animals%2C+which+involves+consciousness+and+emotionality.+%E2%80%94+Wikipedia&url=https%3A%2F%2Fsease.io%2F2021%2F07%2Fartificial-intelligence-applied-to-search-introduction.html)

Since computing power has strongly and steadily advanced in the recent past, AI has seen a resurgence lately and it is now used in many domains, including software engineering and Information Retrieval(the science that regulates Search Engines and similar systems).  
  
Being a complex and generic topic, many sub-fields of Artificial Intelligence exist, each of them dealing with different technical considerations, goals, and tools they use.  
We’ll focus particularly on Machine Learning :

> Machine learning (ML) is the study of computer algorithms that improve automatically through experience and by the use of data. It is seen as a part of artificial intelligence. Machine learning algorithms build a model based on sample data, known as "training data", in order to make predictions or decisions without being explicitly programmed to do so.
>
> Wikipedia
> [Tweet](https://twitter.com/intent/tweet?text=Machine+learning+%28ML%29+is+the+study+of+computer+algorithms+that+improve+automatically+through+experience+and+by+the+use+of+data.+It+is+seen+as+a+part+of+artificial+intelligence.+Machine+learning+algorithms+build+a+model+based+on+sample+data%2C+known+as+%22training+data%22%2C+in+order+to+make+predictions+or+decisions+without+being+explicitly+programmed+to+do+so.+%E2%80%94+Wikipedia&url=https%3A%2F%2Fsease.io%2F2021%2F07%2Fartificial-intelligence-applied-to-search-introduction.html)

So what are the problems AI and Machine Learning may help to solve in Search?  
Many actually, let’s see some examples:

– **natural language processing** -> to better understand and model the user information need and corpus of information, text segmentation to target specific passages of information  
– **image/video recognition** -> to extract features and search a multimedia corpus of information  
– **knowledge representation** -> to build better data structures and search algorithms(e.g. vector-based), to identify meaning, synonyms, and relations between terms and concepts, spellcheck  
– **learning** -> to learn relevance ranking functions, to classify query intent and documents, to offer personalized results

To solve these problems and bring interesting new capabilities to your search engine, **deep learning** comes to the rescue:

> Deep learning (also known as deep structured learning) is part of a broader family of machine learning methods based on artificial neural networks with representation learning. Learning can be supervised, semi-supervised or unsupervised.
> Deep-learning architectures such as deep neural networks, deep belief networks, graph neural networks, recurrent neural networks and convolutional neural networks have been applied to fields including computer vision, speech recognition, natural language processing, machine translation, bioinformatics, drug design, medical image analysis, material inspection and board game programs, where they have produced results comparable to and in some cases surpassing human expert performance.
>
> Wikipedia
> [Tweet](https://twitter.com/intent/tweet?text=Deep+learning%C2%A0%28also+known+as%C2%A0deep+structured+learning%29+is+part+of+a+broader+family+of%C2%A0machine+learning%C2%A0methods+based+on%C2%A0artificial+neural+networks%C2%A0with%C2%A0representation+learning.+Learning+can+be%C2%A0supervised%2C%C2%A0semi-supervised%C2%A0or%C2%A0unsupervised.%0ADeep-learning+architectures+such+as%C2%A0deep+neural+networks%2C%C2%A0deep+belief+networks%2C%C2%A0graph+neural+networks%2C%C2%A0recurrent+neural+networks%C2%A0and%C2%A0convolutional+neural+networks%C2%A0have+been+applied+to+fields+including%C2%A0computer+vision%2C%C2%A0speech+recognition%2C%C2%A0natural+language+processing%2C%C2%A0machine+translation%2C%C2%A0bioinformatics%2C%C2%A0drug+design%2C%C2%A0medical+image+analysis%2C+material+inspection+and%C2%A0board+game%C2%A0programs%2C+where+they+have+produced+results+comparable+to+and+in+some+cases+surpassing+human+expert+performance.+%E2%80%94+Wikipedia&url=https%3A%2F%2Fsease.io%2F2021%2F07%2Fartificial-intelligence-applied-to-search-introduction.html)

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/06/AI-vs-ML-vs-Deep-Learning.png?resize=559%2C235&ssl=1)

Applying **deep learning** techniques to solve search problems is often called **Neural Search** (an industry derivation from the academic field of **Neural Information Retrieval**).  
We won’t explore the details of how Neural Networks work nor all the possibilities we can achieve with such a multi-faceted technology, so let’s keep our focus on what deep learning can contribute to search:

* + **a better text representation**: moving away from the [bag-of-words](https://en.wikipedia.org/wiki/Bag-of-words_model) model (where terms are sequences of characters) to a multi-dimensional numerical(vectorized) approach, able to model terms as semantic units of information linked to each other, with meaning [[1]](https://en.wikipedia.org/wiki/Word_embedding)
  + **text generation**: language modeling techniques flourished and reached mainstream news thanks to outstanding results in generating text that is almost indistinguishable from human-made [[2]](https://www.techradar.com/news/china-outstrips-gpt-3-with-even-more-ambitious-ai-language-model)[[3]](https://medium.com/dataseries/six-times-bigger-than-gpt-3-inside-googles-trillion-parameter-switch-transformer-model-6f7a93c6aae)[[4]](https://www.theguardian.com/commentisfree/2020/sep/08/robot-wrote-this-article-gpt-3)  
    Generating text can be useful in many Information Retrieval areas: query auto-completion, query spellchecking, document summarization, search results explainability (summarizing the information that the document contributes to the user information need)…  
    Improvements in this field could bring to completely new types of information retrieval systems that behave like human experts: the system won’t just return a list of documents to satisfy your information need but synthesize a comprehensive natural language response backed by supporting evidence(documents).
  + **a better image/video representation**: extracting semantic features from images and videos (such as the objects and entities involved rather than just pixel and color-related information). [[5]](https://towardsdatascience.com/deep-learning-based-reverse-image-search-for-industrial-applications-33ba4b0d32c4)  
    Using large pre-trained models, finely tuned for your use case (potentially using transfer learning techniques) helps to build the foundation in advanced multimedia retrieval, reducing the effort of continuously supervised metadata tagging.
  + **learning to rank**: currently, the vast majority of search engines identify a set of candidate documents from the corpus of information (*matching*) and order them by relevance to satisfy the user information need(**ranking**).   
    Providing the most useful results first in the ranked list is fundamental: with deep learning is possible to train advanced relevance ranking models from past interactions/judgments to rank documents for a given query (both represented as numerical vectors) [[6]](https://en.wikipedia.org/wiki/Learning_to_rank)
  + **a better machine translation:** having a computer able to translate languages with the quality of human experts has always been a challenge. Deep Learning managed to replace approaches such as rule-based systems and statistical phrase-based methods.[[7]](https://en.wikipedia.org/wiki/Neural_machine_translation) [[8]](https://arxiv.org/pdf/2002.07526.pdf)  
    This brings huge benefits for multi-lingual search: you may query in a language and find documents in many different languages much more efficiently.[[9]](https://www.amazon.science/publications/query-transformation-for-multi-lingual-product-search)

From this introduction, we notice that many of the deep learning contributions to Search require supporting multi-dimensional numerical vectors in our search engine.  
So how can you implement such wonders with currently available open-source technologies?  
What is officially supported? Where do we need third-party plugins?  
Stay tuned!

## Need Help With This Topic?​​

If you’re struggling to implement Neural Search in your search technology, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling to implement Neural Search in your search technology, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)