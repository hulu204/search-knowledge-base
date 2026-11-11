---
title: 'SolrCloud exceptions with Apache Zookeeper'
company: Sease
tag: 工程相关
date: 2018-05-31
url: https://sease.io/2018/05/solrcloud-exceptions-with-apache-zookeeper.html
account: 
origin: harvest3-202607
---
At the time we speak ( Solr 7.3.1 ) SolrCloud is a reliable and stable distributed architecture for Apache Solr.  
But it is not perfect and failures happen.

Apache Zookeeper [[1]](https://zookeeper.apache.org) is the system responsible for managing the communications across the SolrCloud cluster.  
It contains the shared collections configurations and it has the view of the cluster status.  
It is part of the brain of the cluster, a keeper that maintains the cluster healthy and functional.

It can answer questions such as :

• Who is the leader of this shard and collection?  
• Is this node down?  
• Is this node recovering?

The Solr nodes communicate with Zookeeper to understand who to contact when running SolrCloud operations.

This lightening blog post will present some practical tips to follow when your client application encounters some classic exceptions dealing with SolrCloud and Apache Zookeeper.  
Special thanks to the Apache Solr user mailing list contributors and the Apache Solr community, this post is an aggregation of recommendations from there and from official code and documentation.

## org.apache.solr.common.SolrException: Could not load collection from ZK:

If you landed here with just that Exception I assume there is a missing :  
“ Caused by: org.apache.zookeeper.KeeperException$SessionExpiredException: KeeperErrorCode = Session expired for /collections/<collection name>/state.json “ ?

Solr’s **zkClientTimeout** is used to set ZooKeeper’s sessionTimeout, and that’s what is exceeded when a session expires.  
When this kind of exception happens, it means something has gone VERY wrong in the Solr-Zookeeper communication, 30 seconds ( the current default [[2]](https://issues.apache.org/jira/browse/SOLR-5565) ) is a REALLY long time when applications are trying to communicate.

**Recommendation**: take care of the different time outs around, don’t keep them too small!  
i.e. for zkClientTimeout assign a value >= 30 seconds**.**

**maxSessionTimeout** (Zookeeper)  
New in 3.3.0: the maximum session timeout in milliseconds that the server will allow the client to negotiate. Defaults to 20 times the tickTime.

**zkClientTimeout** (Solr)  
Controls your client timeout.

Once checked the time outs, let’s explore some possible root causes.  
A session expiry can be caused by:

1. Garbage collection on Solr node/Zookeeper – extreme GC pauses can happen with the heap being too small or VERY large  
2. Slow IO on disk.  
3. Network latency

## Recommendations

1. set up a JVM profiler to monitor closely your Solr and Zookeeper nodes, and pay particular attention to the garbage collection cycles and the memory usage in general: you don’t want Zk to swap too much! ( GCViewer [[3]](https://github.com/chewiebug/GCViewer) could be a nice tool for this)
2. Verify that the Zookeeper node has fast writing access to the disk: Zookeeper needs fast writes and ideally, a separate disk allocated.
3. Monitor your network and make sure the solr nodes can talk effectively to the Zookeeper nodes.

In case the suggestions are not solving your problem, you may be experiencing a Solr bug.  
One of them is [[4]](https://issues.apache.org/jira/browse/SOLR-8868) which unfortunately has not been fixed yet.

## org.apache.solr.client.solrj.SolrServerException: No live SolrServers available to handle this

From the official JavaDoc :

***org/apache/solr/client/solrj/impl/LBHttpSolrClient.java:369***  
“Tries to query a live server from the list provided in Req. Servers in the dead pool are skipped.  
\* If a request fails due to an IOException, the server is moved to the dead pool for a certain period of  
\* time, or until a test request on that server succeeds.  
\*  
\* Servers are queried in the exact order given (except servers currently in the dead pool are skipped).  
\* If no live servers from the provided list remain to be tried, a number of previously skipped dead servers will be tried.  
\* Req.getNumDeadServersToTry() controls how many dead servers will be tried.  
\*  
\* If no live servers are found a SolrServerException is thrown.”

What was the status of the cluster at the moment the exception happened ?  
Was any Solr server UP and running according to Zookeeper knowledge ?

The recommendation is to check the clusterstate.json when the exception happens.  
From the Solr admin UI you can open Cloud->Tree and verify which nodes are up and running.

It could be very much related a node failure ( that could be related to any possible reason including GC)  
I’ve seen situations where it was caused by a specific query, the real exception got hidden by a “No live SolrServers…” client exception.  
Solr logs should help to identify the inner Solr problem and JVM monitoring could discard any memory/gc problem.  
Some people saw this with wildcard queries (when every shard reported a “too many expansions…”  
type error, but the exception in the client response was “No live SolrServers…”.

## org.apache.solr.common.SolrException: Could not find a healthy node to handle the request

Pretty much the same considerations as the “No Live Solr Server”.  
This happens when the load balancer SolrJ side is unable to retrieve an alive node, from the cluster ( based on Zookeeper state).  
This happens before the previous exception, so the request doesn’t even reach the LoadBalancinghttpSolrClient.

## Need Help With This Topic?​​

If you’re struggling with Apache Zookeeper, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Apache Zookeeper, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)