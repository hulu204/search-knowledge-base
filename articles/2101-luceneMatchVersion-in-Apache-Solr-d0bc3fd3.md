---
title: 'luceneMatchVersion in Apache Solr'
company: Sease
tag: 工程相关
date: 2021-04-21
url: https://sease.io/2021/04/lucenematchversion-in-apache-solr.html
account: 
origin: harvest3-202607
---
The luceneMatchVersion parameter in the Apache Solr solrconfig.xml specifies a reference Apache Lucene version to use to affect some of the internal components.  
Apache Solr uses Apache Lucene as an internal library, the binaries of an Apache Solr release are coupled with a specific versioned Lucene library.

e.g.  
Apache Solr 8.8.1 release uses Apache Lucene 8.8.1 libraries  
You can find such libraries under: *…/solr-8.8.1/server/solr-webapp/webapp/WEB-INF/lib*  
ls|grep lucene

* + lucene-backward-codecs-8.8.1.jar
  + lucene-classification-8.8.1.jar
  + lucene-codecs-8.8.1.jar
  + lucene-core-8.8.1.jar
  + …

**N.B.** after the Apache Lucene and Solr split of 17/02/2021, versions may not be aligned in the future i.e. Apache Solr X may use Apache Lucene Y

So given that an Apache Solr version is coupled with an exact Apache Lucene version, what’s the meaning and usage of the luceneMatchVersion configuration?

## Supported Values

* + Specific version e.g. 8.8.1 (major.minor.bugfix)
  + LATEST, LUCENE\_CURRENT -> both map to the exact Apache Lucene release included in the Apache Solr binaries

The list of supported versions associated with a Lucene release is listed in this class: *org.apache.lucene.util.Version*

**N.B.** given an Apache Solr release using a specific Apache Lucene version, the supported values for the luceneMatchVersion are back to the major release number version -1  
e.g.  
Apache Solr **8.8.1** uses Apache Lucene **8.8.1** and supports a luceneMatchVersion back to **7.0**  
Apache Solr **7.5** uses Apache Lucene **7.5** and supports a luceneMatchVersion back to **6.0**

If you set an unsupported luceneMatchVersion you’ll find the warning in the logs:  
e.g  
**8.8.1** with <luceneMatchVersion>**6.6.5**</luceneMatchVersion> 6.6.5 < 7.0.0 (8-1)  
*… is using deprecated 6.6.5 emulation. You should at some point declare and reindex to at least 7.0 because 6.x emulation is deprecated and will be removed in 8.0*

## Not Changing the Index Data Structures

A common misconception is that setting <luceneMatchVersion>Y</luceneMatchVersion> in an Apache Solr version X, will make Solr use a Y Lucene Indexing format(using the Y codec and Y data structures).  
**That is not what happens**, Apache Solr version X will always build an Apache Lucene index coupled with the internal library version included in Solr.  
e.g.  
Solr 8.8.1 using Lucene 8.8.1 always builds Lucene 8.8.1 indexes independently of the luceneMatchVersion.  
The luceneMatchVersion is part of various conditional checks in the Solr code, that may change some component behaviours, let’s see them in detail.

## Version Upgrade - Text Analysis

The luceneMatchVersion parameter is primarily a tool to ensure consistent indexing and query behaviour through an upgrade.    
A new release could introduce a different behaviour for the text analysis chain of certain field types(tokenizers, token filters etc…).  
A bug in a tokenizer could be fixed or simply the way a token filter was working could be changed.  
When upgrading your Apache Solr instance to X+1 version, if you want to keep the same logic as an old Lucene version X, to keep consistency with the text analysis chains you were using, it is a good idea to set such version X in the luceneMatchVersion.  
When upgrading a Solr instance from version **X** to **X+1**, it is a good idea to deploy the new version with the **<luceneMatchVersion>X</luceneMatchVersion>**.  
In this way, you keep consistency with the old index **X** and continue to index live new documents minimizing surprises at least for backward compatibility until you can afford to re-index.  
As soon as possible you should proceed upgrading the luceneMatchVersion to **X+1** and run a **re-indexing**.

This is because the new Solr can read up to a certain old index version, so existing index segments will remain in the   
format they are while new segments will be written in the new format.  
If any of the existing segments are merged because of the merge policy, then the new larger segment will be in the new format.

e.g.  
If an index starts out as 6.x, then is run for a while in 7.x, but there are still 6.x segments left(not merged), then that index will not work in 8.0 (independently of the luceneMatchVersion)

## Version Upgrade - Why you Shouldn't Use "LATEST"

If you set **<luceneMatchVersion>LATEST</luceneMatchVersion>** you don’t have control over the exact luceneMatchVersion associated with an Apache Solr collection (it will be the same version of the Solr binary code).  
So if you do an upgrade, **you may end up with un-predicted changes in text analysis and other components** as soon as you upgrade.  
If precise back-compatibility is important you should always specify an exact version.

## Scoring Algorithms (Similarity in Lucene/Solr)

The Similarity algorithm in Apache Lucene implements the logic to assign the score to a search result when ranking happens at query time.  
There are various similarities implemented, you can find them here:  
lucene/lucene/core/src/java/org/apache/lucene/search/similarities  
Currently in Apache Solr Classic Similarity is [TF-IDF](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) and SchemaSimilarity is [BM25.](https://en.wikipedia.org/wiki/Okapi_BM25)  
BM25 has been introduced as the Apache Lucene/Solr default since 6.0 .

In org.apache.solr.search.similarities.SchemaSimilarityFactory#getSimilarity the luceneMatchVersion regulates which Similarity Algorithm to use by default:  
**N.B.** This code snippet is from Solr 6, in current Solr implementations there’s BM25Similarity and LegacyBM25Similarity involved in the conditional check, but the concept is the same.

```
				
					defaultSim = this.core.getSolrConfig().luceneMatchVersion.onOrAfter(Version.LUCENE_6_0_0)
           ? new BM25Similarity()
           : new ClassicSimilarity();
				
			
```

## Need Help With This Topic?​​

If you’re struggling with the lucenematchversion parameter in Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with the lucenematchversion parameter in Apache Solr, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)