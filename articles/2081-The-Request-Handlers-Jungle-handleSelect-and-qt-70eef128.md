---
title: 'The Request Handlers Jungle - handleSelect and qt Parameter'
company: Sease
tag: 工程相关
date: 2019-12-06
url: https://sease.io/2019/12/the-request-handlers-jungle-handleselect-and-qt-parameter.html
account: 
origin: harvest3-202607
---
The target of this blog post is to shed some light on the topic of request handlers and their relation with the QT request parameter in recent Apache Solr ( >= 7.0).

## Definitions

A **Request Handler** is defined with a name and a class.  
It defines an API endpoint to handle and process HTTP requests.   
The name of the request handler is referenced with the request to Apache Solr, typically as a path. For example, if Solr is installed at `http://localhost:8983/solr/` and you have a collection named “gettingstarted”, you can make a request that looks like this:

```
				
					http://localhost:8983/solr/gettingstarted/select?q=solr
				
			
```

This query will be processed by the request handler with the name **`/select`**.

Request Handlers are defined in the Solrconfig.xml, they look like this:

```
				
					&lt;requestHandler name="/select" class="solr.SearchHandler"&gt;
  &lt;lst name="defaults"&gt;
    &lt;str name="echoParams"&gt;explicit&lt;/str&gt;
    &lt;int name="rows"&gt;10&lt;/int&gt;
  &lt;/lst&gt;
&lt;/requestHandler&gt;
				
			
```

We’ll focus in this blog post on **Search Handlers**: a class of request handlers that processes search requests.

**N.B.** It’s out of the scope of this blog post, but a request handler can be a complex component that contains advanced logic and append/defaults various request parameters to the user search request, transparently [[1]](https://lucene.apache.org/solr/guide/8_3/requesthandlers-and-searchcomponents-in-solrconfig.html#searchhandlers)

The **qt** parameter is a request parameter supported by the Apache Solr Request Dispatcher.  
Its original scope **was** to pass the request handler to use through a request parameter.  
This parameter is strictly tied to the handleSelect attribute of the Solr Request Dispatcher:

*The first configurable item is the `handleSelect` attribute on the `<requestDispatcher>`element itself. This attribute can be set to one of two values, either “true” or “false”. It governs how Solr responds to requests such as `/select?qt=XXX`. The default value “false” will ignore requests to `/select` if a requestHandler is not explicitly registered with the name `/select`. **A value of “true” will route query requests to the parser defined with the `qt` value**.*  
*In recent versions of Solr, a `/select` requestHandler is defined by default, so a value of “false” will work fine.*Apache Solr Wiki

We have now clarified the definitions and the scope of the blog post, let’s see if this is always true, and what happens in SolrJ.

## More on handleSelect and QT

If handleSelect is TRUE and no QT parameter is passed in the request, Solr will route the /select requests to the default request handler configured in the Solrconfig.xml:

```
				
					&lt;requestHandler name="/myRequestHandler" class="solr.SearchHandler" default="true"&gt;
				
			
```

What about this statement :  
“***A value of “true” will route query requests to the parser defined with the `qt` value***.”  
The forementioned statement is partially true.  
The QT parameter will be applied, routing the requests to the specified request handler

```
				
					&lt;requestDispatcher handleSelect="true"&gt;
        ...
    &lt;/requestDispatcher&gt;
				
			
```

**AND no /select request handler is defined** (N.B. unless you delete it, the /select request handler is defined by default).

In all the other scenarios, **the QT parameter will just be ignored**

## What Happens in SolrJ

In SolrJ it’s possible to specify the request handler to use, calling this setter method:

```
				
					SolrQuery mySolrQuery = new SolrQuery("userId:" + userId); mySolrQuery.setRequestHandler("/myRequestHandler");
				
			
```

And it works fine.

Well, partially… because if you don’t set the request handler SolrJ will use by default the **/select** request handler!  
So the default request handler configured in the Solrconfig.xml of your instance is ignored if you have also the /select defined.  
The reason is hard-coded in the Solrclient:

```
				
					org.apache.solr.client.solrj.impl.HttpSolrClient
...
/**
 * A SolrClient implementation that talks directly to a Solr server via HTTP
 */
public class HttpSolrClient extends BaseHttpSolrClient {

  private static final String UTF_8 = StandardCharsets.UTF_8.name();
  private static final String DEFAULT_PATH = "/select";
...
				
			
```

We are curious now about **what the mySolrQuery.setRequestHandler(“/myRequestHandler”) does then?**

```
				
					public SolrQuery setRequestHandler(String qt) {
    this.set(CommonParams.QT, qt);
    return this;
  }
				
			
```

Oh No! It uses the QT parameter! We have seen how tricky this is!  
But everything works fine if you do this in SolrJ, independently of the considerations we have shown at the beginning of the post on HandleSelect…

To understand why, we can take a look at the source code, but we have a hint, buried in the Apache Solr documentation [[2]](https://lucene.apache.org/solr/guide/8_3/major-changes-in-solr-7.html):

The `handleSelect` parameter in `solrconfig.xml` now defaults to `false` if the `luceneMatchVersion` is 7.0.0 or above. This causes Solr to ignore the `qt` parameter if it is present in a request. If you have request handlers without a leading ‘/’, you can set `handleSelect="true"` or consider migrating your configuration. **The `qt` parameter is still used as a SolrJ special parameter that specifies the request handler (tail URL path) to use**.

Solr Wiki

So it seems it is known that SolrJ uses the parameter differently…

But How?

This bit of code finally clarifies everything:

```
				
					org.apache.solr.client.solrj.request.QueryRequest#getPath
public String getPath() {
    String qt = query == null ? null : query.get( CommonParams.QT );
    if( qt == null ) {
      qt = super.getPath();
    }
    if( qt != null &amp;&amp; qt.startsWith( "/" ) ) {
      return qt;
    }
    return "/select";
  }
				
			
```

That is called by the SolrClient itself:

```
				
					org.apache.solr.client.solrj.impl.HttpSolrClient#createMethod
protected HttpRequestBase createMethod(SolrRequest request, String collection) throws IOException, SolrServerException {
   ...
    String path = requestWriter.getPath(request);
    if (path == null || !path.startsWith("/")) {
      path = DEFAULT_PATH;
    }
				
			
```

Hope this helps some folks!

## Need Help With This Topic?​​

If you’re struggling with request handlers, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with request handlers, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)