---
title: 'https://sease.io/2026/07/apache-solr-lexicographical-order-possible-unexpected-behaviors.html'
company: Sease
tag: 搜索
date: 
url: https://sease.io/2026/07/apache-solr-lexicographical-order-possible-unexpected-behaviors.html
account: 
origin: en-rss
---
Hi Information Retrieval community,

This [tips & tricks](https://sease.io/our-blog/tips-and-tricks) blog post comes from a real client question that, sooner or later, those working with a Solr-based search engine may encounter. The client implemented a search query using **[Solr faceting](https://solr.apache.org/guide/solr/latest/query-guide/faceting.html)** and noticed that facet sorting was not behaving as expected, even though the configuration appeared to be correct.

*N.B. The scenario is reproduced using intentionally simplified examples, just to illustrate the issue.*

Given a facet query results like the following:

```
				
					"facet_fields":{
      "brand":["&amp;Beyond",1,
               "10X Vision",1,
               "2Fast",1,
               "AI Labs",1,
               "APPLE",1,
               "Amazon",1,
               "Amazon Music",1,
               "Bose",1,
               "GoPro",1,
               "Google",1,
               "Google-Cloud",1,
               "Google_Ads",1,
               "Huawei",1,
               "LG",1,
               "LG Electronics",1,
               "Lacoste",1,
               "Microsoft",1,
               etc...]
    },
				
			
```

The expected order would have been:

* **Amazon** before **APPLE**
* **Google** before **GoPro**
* **Google\_Ads** before **Google-Cloud**
* **Lacoste** before **LG**
* etc..

The Facet query is executed on the **brand** field with `facet.sort=index`, for example:

```
				
					q=*:*
&amp;facet=true
&amp;facet.field=brand
&amp;facet.sort=index
&amp;rows=0
&amp;facet.limit=100
				
			
```

From the [documentation](https://solr.apache.org/guide/solr/latest/query-guide/faceting.html#field-value-faceting-parameters), we can see that `facet.sort=index` means: *“Return the terms sorted lexicographically. For terms in the ASCII range, this will be alphabetically sorted.*“

So why do we see that result?  
When sorting strings using ASCII rules, characters are compared **from left to right**. The first character that differs determines the order. If one string is a prefix of another, the **shorter string comes first**.  
According to ASCII ordering, characters are sorted in the following sequence:

* Control characters and whitespace *(e.g. Space = 32)*
* Special symbols`(``! " # $ % & ' ( ) * + , - . /`)
* Numbers (`0–9`)
* More symbols (`: ; < = > ? @)`
* Uppercase letters (`A–Z)`
* More symbols (`[ \ ] ^ \_ “)
* Lowercase letters (`a–z)`

This explains the behaviour we are observing, and the resulting order may differ from the expected human-friendly or alphabetical order.

The same behaviour occurs when we sort the search results using the `sort` parameter in a “standard” query, for example `sort=brand asc`.

So, in the following section, we address the two cases separately: the **sort** parameter and the **facet.sort** parameter related to facets.

## Solr Sort Parameter

As we can see from the [Solr documentation](https://solr.apache.org/guide/solr/latest/query-guide/common-query-parameters.html#sort-parameter) about the **sort** parameter, if you want to use a field to specify the order of the returned documents, the field must satisfy one of the following conditions:

1. Single-valued and multi-valued primitive fields (numerics, string, boolean, dates, etc.) which have `docValues="true"` OR `indexed="true"` and `uninvertible=true`
2. Single-valued and multi-valued `SortableTextField`, which implicitly uses `docValues="true"` by default to allow sorting on the original input string.
3. Single-valued `TextField` that has an analyser (such as the `KeywordTokenizer`) that produces only a single term per document, but then a DocValue-like structure has to be built on the fly at runtime.

[DocValues](https://solr.apache.org/guide/solr/latest/indexing-guide/docvalues.html) are an on-disk data structure, built at index time, that store field values per document, enabling efficient query-time operations such as sorting, faceting, grouping, and function queries.

Since `TextField` does not support `docValues`, one way to build a DocValues-like structure at runtime is to configure the field as `indexed="true"`, `docValues="false"`, and `uninvertible="true"`.  
In this case, the field can be *uninverted* at query time, allowing Solr to construct an in-memory data structure that provides document-to-term lookup, functionally similar to DocValues.   
**This approach is not recommended**, as it introduces query latency and can consume large amounts of JVM heap memory. However, if a tokenised field must be used for sorting, uninversion is the only available option.

### Solution

How can we resolve the issue where the ordering does not match the expectations, as we saw above?  
In our case, to achieve the desired result, we must configure a field in Solr to ignore case sensitivity and punctuation. To use a field backed by **docValues**, which is the recommended approach for sorting, a possible solution we can implement is the use of [ICUCollation](https://solr.apache.org/guide/solr/latest/indexing-guide/language-analysis.html#unicode-collation).

ICUCollation is a Solr field type that enables language-sensitive sorting. It leverages the [ICU4J](https://icu.unicode.org/) (International Components for Unicode for Java) library to handle text according to specific cultural and linguistic conventions rather than simple binary (ASCII/Unicode) code point order. For more information, please refer to the [documentation](https://solr.apache.org/guide/solr/latest/indexing-guide/language-analysis.html#icucollationfield-attributes).

Here is how to define the fields in the *schema.xml*:

```
				
					&lt;fieldType name="collate_en" class="solr.ICUCollationField"
    locale="en" strength="primary"/&gt;

&lt;field name="brand" type="string" indexed="true" stored="true" docValues="false"/&gt;
&lt;field name="brand_sort" type="collate_en" indexed="true" stored="false" docValues="true"/&gt;

&lt;copyField source="brand" dest="brand_sort" /&gt;
				
			
```

For display purposes, we use the *raw* `brand` field, while we use the `brand_sort` field (which is of type `ICUCollationField` and specific for English) for sorting:

```
				
					q=*:*&amp;sort=brand_sort&amp;fl=brand
				
			
```

And here is the output:

```
				
					"docs":[{
      "brand":"&amp;Beyond"
    },{
      "brand":"10X Vision"
    },{
      "brand":"2Fast"
    },{
      "brand":"AI Labs"
    },{
      "brand":"Amazon"
    },{
      "brand":"Amazon Music"
    },{
      "brand":"APPLE"
    },{
      "brand":"Bose"
    },{
      "brand":"Google"
    },{
      "brand":"Google_Ads"
    },{
      "brand":"Google-Cloud"
    },{
      "brand":"GoPro"
    etc...
				
			
```

To use this feature, the module [analysis-extras](https://solr.apache.org/guide/solr/latest/indexing-guide/language-analysis.html#analysis-extras-module) has to be enabled, which means starting Solr with:

```
				
					bin/solr start -Dsolr.modules=analysis-extras
				
			
```

And make sure to have this in the *solrconfig.xml*:

```
				
					&lt;lib dir="${solr.install.dir:../../../..}/modules/analysis-extras/lib/solr-analysis-extras-X.Y.Z" regex=".*\.jar" /&gt;
				
			
```

## Solr Facet Sort Parameter

[Faceting](https://solr.apache.org/guide/solr/latest/query-guide/faceting.html) is a feature that is used to group and count the results of a search. Here as well, the recommended best practice is to always use `docValues=true` for the fields used for faceting.

Facet sorting refers to the ordering of the facet values, not to the ordering of the main search results.  
By default, facet values are sorted by `count` (i.e. highest count first) or by `index`, which, as mentioned earlier, means they are sorted lexicographically.  
When using the [JSON Facet API](https://solr.apache.org/guide/solr/latest/query-guide/json-facet-api.html), facets can be also sorted by [Stat Facet Functions](https://solr.apache.org/guide/solr/latest/query-guide/json-facet-api.html#stat-facet-functions).

### Solutions

ICUCollation cannot be used for faceting because the **ICUCollationField** transforms the text into a *binary collation key* (a sequence of unreadable bytes, e.g. *4\*NP*) optimised for mathematical comparison, not for human-readable output. So it is not suitable to display facet values, but it is mainly useful as a sort key.

The simplest and cleanest solutions here are either to perform **pre-processing** and index the field value exactly as needed for sorting or to apply **post-processing** to recreate the expected sort order.

Another acceptable compromise is to structure a text-analysis pipeline that lowercases the input string and produces a single token (using a `KeywordTokenizer`). This inevitably alters the original value; however, as long as the generated token remains readable enough to support result navigation, it provides a consistent representation suitable for faceting and sorting. In practice, this means that if values such as `Amazon` and `APPLE` are normalised to `amazon` and `apple`, and the resulting facet filter correctly retrieves the expected subset of documents, the behaviour is considered acceptable.

We hope this post was helpful. Have any other ideas to deal with this behavior? Let us know… we’re curious to explore different solutions!

## Need Help with this topic?​

If you're struggling with facet sorting, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with facet sorting, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)