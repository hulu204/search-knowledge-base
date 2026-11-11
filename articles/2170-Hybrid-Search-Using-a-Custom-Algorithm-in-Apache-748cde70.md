---
title: 'Hybrid Search Using a Custom Algorithm in Apache Solr'
company: Sease
tag: 召回
date: 2026-03-09
url: https://sease.io/2026/03/hybrid-search-using-a-custom-algorithm-in-apache-solr.html
account: 
origin: harvest3-202607
---
Hello everyone,

If you are here, it is probably because you have already read the first part of this [blog post](https://sease.io/2026/03/hybrid-search-with-reciprocal-rank-fusion-in-apache-solr.html) about the new Solr feature for performing **hybrid search** (Combined Query), and now you are curious to learn how to actually use it by configuring a **custom search results fusion algorithm**, instead of relying on Reciprocal Rank Fusion (RRF), which is the default option.

For simplicity, we use the same Solr collection from the previous tutorial (*ms-marco*) and avoid repeating what has already been covered. Also, to keep things concise, we do not implement a real algorithm or provide full code; instead, the goal is to explain the steps to follow and highlight only the configuration changes required when using a custom algorithm.

## Apache Solr Plugin

As the documentation of the Combine Query feature says, any other custom algorithm can be configured using a Solr plugin.

A **Solr plugin** is a configurable Java component that runs inside Solr to perform part of its work.  
Solr already contains many built-in components (request handlers, search components, query parsers, token filters, etc.), but you can also write your own and register them in the configuration.

So instead of changing the Solr source code and contributing a patch to Solr itself, you provide an external class that Solr loads and executes as one of its internal components at runtime.

As we can see from the Plugin [documentation](https://solr.apache.org/guide/solr/latest/configuration-guide/solr-plugins.html), there are two types of plugins:

* Cluster level: installed once in the Solr node and available to every collection running on that node.
* Collection level: configured inside a specific collection and used only by that collection.

In our case, this is a Collection-level plugin, because it is configured inside the Solr configuration (**`solrconfig.xml`**) of our collection and executed during query processing.

### Jar Creation

The first thing to do is to create a new Java project and implement a specific class, in our case: **`CustomCombiner`**

```
				
					package org.apache.solr.handler.component.combine;

import java.util.List;
import java.util.Map;
import org.apache.lucene.search.Explanation;
import org.apache.solr.common.params.SolrParams;
import org.apache.solr.common.util.NamedList;
import org.apache.solr.common.util.SimpleOrderedMap;
import org.apache.solr.handler.component.ShardDoc;

/**
 * Example implementation of a custom combiner plugin.
 * This class can be used as a template for developing a custom combiner.
 * NOTE: This implementation intentionally does not perform real merging logic.
 * It is only meant as a minimal reference template for plugin development.
 */

public class CustomCombiner extends QueryAndResponseCombiner {

    /** Example parameter loaded from solrconfig.xml */
    private int customInt;

    /**
     * Called once at Solr startup when the plugin is created.
     * Here we read parameters defined inside the &lt;combiner&gt; configuration.
     */
    @Override
    public void init(NamedList&lt;?&gt; args) {
        Object customParam = args.get("customParam");
        if (customParam != null) {
            this.customInt = Integer.parseInt(customParam.toString());
        }
    }

    public int getCustomInt() {
        return customInt;
    }

    /**
     * This is the core method of the combiner.
     * Here is where the developer should implement the merging algorithm:
     * The returned list becomes the final ranked result returned by Solr.
     * NOTE: This example returns an empty list intentionally.
     */
    @Override
    public List&lt;ShardDoc&gt; combine(Map&lt;String, List&lt;ShardDoc&gt;&gt; shardDocMap, SolrParams solrParams) {
        return List.of();
    }

    /**
     * Debug/explain information.
     * This method allows the combiner to expose how the final ranking
     * was produced. The information is returned when debugQuery=true.
     * A real implementation would normally add per-document explanations.
     */
    @Override
    public SimpleOrderedMap&lt;Explanation&gt; getExplanations(
            String[] queryKeys,
            Map&lt;String, List&lt;ShardDoc&gt;&gt; queriesDocMap,
            List&lt;ShardDoc&gt; combinedQueriesDocs,
            SolrParams solrParams) {
        SimpleOrderedMap&lt;Explanation&gt; docIdsExplanations = new SimpleOrderedMap&lt;&gt;();
        docIdsExplanations.add("combinerDetails", Explanation.match(customInt, "This is a test for custom combiner"));
        return docIdsExplanations;
    }
}
				
			
```

***NOTE:** This implementation intentionally does not perform any real merging logic and is only meant as a minimal reference template. Depending on the algorithm you plan to implement, you may also use the [RRF implementation](https://github.com/apache/solr/blob/6cc80a0f39c4155553c25c774e7d9b9462d7639f/solr/core/src/java/org/apache/solr/handler/component/combine/ReciprocalRankFusion.java) as a reference example, as it may contain parts and patterns that can be useful for your own combiner.*

The class to implement the custom logic has to extend the `QueryAndResponseCombiner`, which is an abstract base class that provides a framework for implementing various algorithms used to merge ranked lists and shard documents.

Then the project must include the Solr dependencies matching the Solr version we are targeting (in our case, a version ≥ 9.11 / 10.1); below is an example using Gradle, but the same dependencies must be declared in whichever build system is used:

**`build.gradle`**

```
				
					plugins {
    id 'java-library'
}

repositories {
    mavenCentral()
}

ext {
    solrVersion = "9.11"
}

dependencies {
    compileOnly "org.apache.solr:solr-core:${solrVersion}"
    compileOnly "org.apache.solr:solr-language-models:${solrVersion}"
}
				
			
```

**NOTE**  
*The Combined feature is available in Solr from version 9.11*/*10.1  
If you plan to try it before that release, for the scope of this tutorial, we built Solr directly from the Solr source code that includes the required classes, and published the artefacts locally using: `./gradlew publishToMavenLocal`  
This makes the SNAPSHOT Solr dependencies available in `mavenLocal()`, allowing our plugin project to compile against them*:

```
				
					...
  repositories {
    mavenLocal()
}

ext {
    solrVersion = "11.0.0-SNAPSHOT"
}
...
				
			
```

Once the implementation is finished, compile and package artefacts, using:

```
				
					./gradlew assemble
				
			
```

This will create a JAR file in the **`build/libs`** folder.  
Then copy the generated JAR into the Solr libraries directory:

```
				
					.../solr-9.11/server/solr-webapp/webapp/WEB-INF/lib
				
			
```

## Solr Configuration

Copying the JAR into the Solr classpath is only the installation step. At this point, Solr must be restarted so that it can load the class, but it still does not know when or how to use it. To make the plugin active, it must be registered inside **`solrconfig.xml`**:

```
				
					&lt;requestHandler name="/combined" class="solr.CombinedQuerySearchHandler"&gt;
&lt;/requestHandler&gt;

&lt;searchComponent class="solr.CombinedQueryComponent" name="combined_query"&gt;
    &lt;int name="maxCombinerQueries"&gt;2&lt;/int&gt;
    &lt;lst name="combiners"&gt;
        &lt;lst name="customAlgorithm"&gt;
            &lt;str name="class"&gt;org.apache.solr.handler.component.combine.CustomCombiner&lt;/str&gt;
            &lt;int name="customParam"&gt;15&lt;/int&gt;
        &lt;/lst&gt;
    &lt;/lst&gt;
&lt;/searchComponent&gt;
				
			
```

Within the search component **`CombinedQueryComponent`**, the **`combiners`** parameter allows a custom class to be specified in order to define the merging algorithm. Each combiner is declared by giving it a name and, optionally, a set of configuration parameters required by the algorithm.

In our case:  
– the combiner is registered with the name **`customAlgorithm`**  
– **`org.apache.solr.handler.component.combine.CustomCombiner`** is our implementation class  
– and we pass a parameter (**`customParam`**) only as an example to show how configuration parameters can be provided to the algorithm.

## Combined Query Using Custom Algorithm

Now everything is ready, and we can execute the hybrid query:

```
				
					http://localhost:8983/solr/ms-marco/combined?
{
    "queries": {
        "lexical": {
            "lucene": {
                "query": "text:(tax payment id)"
            }
        },
        "vector": {
            "knn": {
                "f": "vector",
                "topK" :10,
                "query": "[0.0009692322928458452, 0.028254959732294083, -0.005096305627375841, ......., -0.050939954817295074]"
            }
        }
    },
    "limit": 10,
    "fields": ["id", "text", "score"],
    "params": {
        "combiner": true,
        "combiner.query": ["lexical", "vector"],
        "combiner.algorithm": "customAlgorithm"
    }
}
				
			
```

The only thing that changes is the value specified in the `combiner.algorithm` parameter.  
In this case, we set it to the name defined in the configuration, which is **`customAlgorithm`**.  
The RRF-specific parameters do not need to be provided in this case.

Since no real merging algorithm has been implemented, no results will be returned.  
However, based on how we implemented `getExplanations`, we expect to see the debug information produced by the combiner when **`debugQuery=true`**:

```
				
					...
},
    "response": {
        ...
        "docs": []
  },
    "debug": {
        "track": {
            "EXECUTE_QUERY": {
                "http://localhost:8983/solr/ms-marco": {
                    "QTime": "6",
                    ...
                }
            }
        },
        "combinerExplanations": {
            "combinerDetails": "org.apache.lucene.search.Explanation:15 = This is a test for custom combiner\n"
        },
        "json": {
        ...
				
			
```

As we can see, inside **`combinerExplanations`** we find both the value of **`customParam`** passed in the configuration (15) and the message *“This is a test for custom combiner”*.

This confirms that the custom combiner has been invoked and is working as expected.

I hope you found this blog post useful, interesting, and easy to follow. Stay tuned for more exciting updates coming soon!

## Need Help with this topic?​

If you're struggling with Hybrid Search in Apache Solr, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with Hybrid Search in Apache Solr, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)