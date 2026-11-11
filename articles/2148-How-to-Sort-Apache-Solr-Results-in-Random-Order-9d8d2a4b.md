---
title: 'How to Sort Apache Solr Results in Random Order'
company: Sease
tag: 工程相关
date: 2024-08-26
url: https://sease.io/2024/08/how-to-sort-apache-solr-results-in-random-order.html
account: 
origin: harvest3-202607
---
Usually, when running a query in Solr, the goal is to obtain a set of documents in descending order of relevance.

May sound unusual, but sometimes it is necessary to **obtain a set of documents** randomly sorted, **regardless of their relevance**.  
For example, retrieving some documents to generate a dataset for the fine-tuning of a language model.

Thanks to a specific field type called **[RandomSortField](https://solr.apache.org/guide/solr/latest/indexing-guide/field-types-included-with-solr.html)** this is possible in Solr.

## Schema Configuration

Here is how you need to define it.  
First of all, you need to define the field type *random*:

```
				
					&lt;fieldType name="random" class="solr.RandomSortField" indexed="true"/&gt;
				
			
```

Then, you need to define a dynamic field that is going to use our RandomSortField:

```
				
					&lt;dynamicField name="random_*" type="random"/&gt;
				
			
```

As described in the default schema of Solr:

*The “RandomSortField” is not used to store or search any data. You can declare fields of this type it in your schema to generate pseudo-random orderings of your docs for sorting or function purposes. The ordering is generated based on the field name and the version of the index. As long as the index version remains unchanged, and the same field name is reused, the ordering of the docs will be consistent. If you want different pseudo-random orderings of documents, for the same version of the index, use a dynamicField and change the field name in the request.*

And as described in Solr documentation:

*Does not contain a value. Queries that sort on this field type will return results in random order. Use a dynamic field to use this feature.*

Thanks to its characteristics, if you don’t already have it, **you can add this random field without the need to reindex your entire collection.** You can just modify the schema and use the field.

## Query

```
				
					http://localhost:8983/solr/news/select?q=title:Economia OR category:Lavoro&amp;fl=title, category&amp;sort=random_1423 desc
				
			
```

And its response:

```
				
					"response": {
   "numFound": 28604,
   "start": 0,
   "numFoundExact": true,
   "docs": [
   {
     "title": "Economy",
     "category": "Tourism"
   },
   {
     "title": "Economy",
     "category": "Work"
   },
   {
     "title": "Economy",
     "category": "Energy"
   },
   {
     "title": "Economy",
     "category": "Work"
   },
   {
     "title": "Economy",
     "category": "Industry"
   },
   {
     "title": "Economy",
     "category": "Energy"
   }
]
				
			
```

The documents are ordered randomly. Those matching the query are scattered in the list.

Since ***random*** is a dynamic field, the important thing is to use the prefix **random\_**, then you can choose whatever integer you want as the suffix. In this case, I put 1423. **Using the same integer ensures to have the same ordered list of results (like a seed).**

## Need Help With This Topic?​​

If you’re struggling to obtain a set of documents randomly sorted in Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling to obtain a set of documents randomly sorted in Apache Solr, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)