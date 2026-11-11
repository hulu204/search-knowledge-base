---
title: 'Apache Solr Multivalued Vectors Tutorial'
company: Sease
tag: 召回
date: 2026-02-17
url: https://sease.io/2026/02/apache-solr-multivalued-vectors-tutorial.html
account: 
origin: harvest3-202607
---
Hi Jesiel, sorry for the late reply. I was not even able to create a Solr collection from the files in the GitHub repository (I looked into the solrconfig file, and you used external jars in your pipeline, which I do not have; this might be the reason). I wanted to try to create a collection that can be good with the data that you uploaded to the repo. Here is what I did:  
– I copied the default configuration, removed RemoveBlankFieldUpdateProcessorFactory from the solrconfig update processor pipeline, and added the following fields to the managed-schema file (to be in line with your data):  
`fieldType name="knn_vector" class="solr.DenseVectorField" vectorDimension="768" similarityFunction="cosine"  
field name="vector_multivalued" type="knn_vector" indexed="true" stored="true" multiValued="true"  
field name="title" type="text_general" indexed="true" stored="true"  
field name="author" type="text_general" indexed="true" stored="true"  
field name="format" type="string" indexed="true" stored="true"  
field name="publishDate" type="pdate" indexed="true" stored="true"`

– Trying to index, I got an error. This is due to the fact that, since you are dealing with multivalued vectors, Solr tries to unpack the list of vectors that you send to it. This is a problem in the document with id “1”, since you are basically sending a list of floats. In this case, to fix the error, you should wrap the vector of the document with id “1” into another set of square brackets, i.e., [[-0.027840303257107735,…,-0.035133495926856995]].  
After doing what’s listed above, I was able to index all the documents properly. I don’t know about your specific configuration since I cannot create the collection. I suggest investigating each component that is different from the default ones, to understand if it’s 100% necessary, and add one by one to see which one is giving problems with your configuration. I hope I have been exhaustive enough. If you have other questions, feel free to reach out!

Loading...

[Reply](#comment-10105)