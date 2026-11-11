---
title: 'Apache Solr the CompositeRequestHandler'
company: Sease
tag: 工程相关
date: 2018-03-20
url: https://sease.io/2018/03/compositesearchhandler.html
account: 
origin: harvest3-202607
---
## What are "Invisible Queries"?

This is an extract of an article [[1]](https://lucidworks.com/blog/2009/08/12/fake-and-invisible-queries) on Lucidworks.com, by Grant Ingersoll, talking about invisible queries:

*“It is often necessary in many applications to execute more than one query for any given user query.  For instance, in applications that require very high precision (only good results, forgoing marginal results), the app. may have several fields, one for exact matches, one for case-insensitve matches and yet another with stemming.  Given a user query, the app may try the query against the exact match field first and if there is a result, return only that set.  If there are no results, then the app would proceed to search the next field, and so on.”*

The sentence above assumes a scenario where the (client) application issues to Solr several and subsequent requests on top of a user query (i.e. **one**user query => **many**search engine queries). What about you don’t have such control? Imagine you’re the search engineer of an e-commerce portal that has been built using Magento, which, in this scenario, acts as the Solr client; someone installed and configured the Solr connector and ok, everything is working: when the user submits a search, the connector forwards the request to Solr, which in turns executes a (single) query according with the configuration.

## The context

Now, imagine that the query above returns no results. The whole request/response interaction is gone, the user will see something like “Sorry, no results for your search”. Although this sounds perfectly reasonable, in this post we will focus on a different approach, based on the “invisible queries” thing you can read in the extract above. The main point here is a precondition: I cannot change the client code; because (for example):

* + I don’t want to introduce custom code in my Magento / Drupal instance
  + I don’t know PHP
  + I’m strictly responsible for the search infrastructure and the frontend developer doesn’t want/is not able to properly implement this feature on the client side
  + I want to move as much as possible the search logic in Solr

What I’d like to do is to provide a single entry point (i.e. one single request handler) to my clients, being able to execute a workflow like this:

![Invisible Queries Apache Solr](https://i0.wp.com/sease.io/wp-content/uploads/2018/04/admin-ajax.php_.png?fit=272%2C400&ssl=1)

## The CompositeRequestHandler

The underlying idea is to provide a *Facade* which is able to chain several handlers; something like this:

```
				
					&lt;requestHandler name="/search" class="...CompositeRequestHandler"&gt;
    &lt;str name="chain"&gt;/rh1,/rh2,/rh3&lt;/str&gt;
&lt;/requestHandler&gt; 
				
			
```

where */rh1*, */rh2* and */rh3* are standard *SearchHandler* instances you’ve already declared, that you want to chain in the workflow described in the diagram above.

The *CompositeRequestHandler*implementation is simple: its *handleRequestBody* method will execute, sequentially, the configured handler references, and it will break the chain after receiving the first positive query response (usually that is a query response with numFound > 0, but the last version of the component allows you to configure also other predicates). The logic would be something like this:

```
				
					chain.stream()
// Get the request handler associated with a given name
.map(refName -&gt; requestHandler(request, refName))
// Only SearchHandler instances are allowed in the chain
.filter(SearchHandler.class::isInstance)
// executes the handler logic
.map(handler -&gt; executeQuery(request, response, params, handler))
.filter(qresponse -&gt; howManyFound(qresponse) &gt; 0)
// Stop the iteration when the first condition above has been satisfied
.findFirst()
// or, if we don't have any positive executions, just returns an empty response.
.orElse(emptyResponse(request, response)));
				
			
```

You can find the source code of CompositeRequestHandler in our Sease GitHub repository [[2]](https://github.com/SeaseLtd/composite-request-handler).   
As usual, any feedback is warmly welcome.

## Need Help With This Topic?​​

If you’re struggling with Invisible Queries in Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Invisible Queries in Apache Solr, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)