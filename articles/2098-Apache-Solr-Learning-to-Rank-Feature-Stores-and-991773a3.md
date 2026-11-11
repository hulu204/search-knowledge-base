---
title: 'Apache Solr Learning to Rank Feature Stores and Models'
company: Sease
tag: 排序
date: 2021-02-25
url: https://sease.io/2021/02/apache-solr-learning-to-rank-feature-stores-and-models.html
account: 
origin: harvest3-202607
---
This short blog post wants to help you manage learning to rank features stores and models in Apache Solr. Here I will list for you the main commands, while in the next post, I will recap the most common errors that can occur during the manipulation of feature stores and models.

## Learning to rank features

##### List

A feature store is a container of features.  
A model uses features from only one feature store.  
A feature store can be used by many models.  
The list of the available feature stores in the “collection1” collection, is available at:

```
				
					https://localhost:8983/solr/collection1/schema/feature-store
				
			
```

The response looks like:

```
				
					{
  "responseHeader": {
       "status": 0,
       "QTime": 160
  },
  "featureStores": [
      "first_store",
      "second_store"
  ]
}
				
			
```

Where **first\_store** and **second\_store** are the available feature stores present in *collection1*.

##### Upload

To upload a feature store to a feature-store of a specific collection, we use the following curl command.

For the *collection1* collection:

```
				
					curl -XPUT "https://localhost:8983/solr/collection1/schema/feature-store/" --data-
binary "@features.json" -H "Content-type:application/json"
				
			
```

Where *features.json* is the file containing the features (the feature store we want to upload).

For example:

```
				
					[
    {
        "store": "first_store",
        "name": "feature_1",
        "class": "org.apache.solr.ltr.feature.ValueFeature",
        "params": {
            "value": "${feature_1}",
            "required": false
        }
    },
    {
        "store": "first_store",
        "name": "feature_2",
        "class": "org.apache.solr.ltr.feature.ValueFeature",
        "params": {
            "value": "${feature_2}",
            "required": false
        }
    },
....
				
			
```

Here “store” is the name of the feature store in the feature-store. It will be visible, after the upload, in the feature-store list.

##### Delete

To delete a feature store called *first\_store* from the *collection1* collection:

```
				
					curl -XDELETE "https://localhost:8983/solr/collection1/schema/feature-store/first_store"
				
			
```

## Learning to rank models

##### List

As mentioned before:  
A **model** uses features **from only one feature store**.  
A **feature store** can be used by **many models**.  
The list of the available models in the *collection1* collection, is at:

```
				
					https://localhost:8983/solr/collection1/schema/model-store
				
			
```

And it is something like:

```
				
					{
  "responseHeader":{
    "status":0,
    "QTime":188},
  "models":[{
      "name":"model_1",
      "class":"org.apache.solr.ltr.model.MultipleAdditiveTreesModel",
      "store":"first_store",
      "features":[{
          "name":"feature_1",
          "norm":{"class":"org.apache.solr.ltr.norm.IdentityNormalizer"}},
        {
          "name":"feature_2",
          "norm":{"class":"org.apache.solr.ltr.norm.IdentityNormalizer"}},
....
      },
      {
      "name":"model_2",
      "class":"org.apache.solr.ltr.model.MultipleAdditiveTreesModel",
      "store":"first_store",
      "features":[{
          "name":"feature_1",
          "norm":{"class":"org.apache.solr.ltr.norm.IdentityNormalizer"}},
        {
          "name":"feature_3",
          "norm":{"class":"org.apache.solr.ltr.norm.IdentityNormalizer"}},
....
				
			
```

Here “name” is the name of the model in the model-store. It will be visible, after the upload, in the model-store list.

##### Upload

To upload a model to a model-store of a specific collection, we use the curl command:

```
				
					curl -XPUT "https://localhost:8983/solr/collection1/schema/model-store" --data-binary "@solr-model.json" -H "Content-type:application/json"
				
			
```

Where *solr-model.json* is the file containing the model we want to upload.

For example:

```
				
					{
    "store": "first_store",
    "name": "model_1",
    "class": "org.apache.solr.ltr.model.MultipleAdditiveTreesModel",
    "features": [
        {
            "name": "feature_1"
        },
        {
            "name": "feature_2"
        },
        {
            "name": "feature_3"
        },
....
				
			
```

##### Delete

To delete a model called *model\_1* from the *collection1* collection:

```
				
					curl -XDELETE "https://localhost:8983/solr/collection1/schema/model-store/model_1"
				
			
```

## Reload

To reload the *collection1* collection:

```
				
					https://localhost:8983/solr/admin/collections?action=RELOAD&amp;name=collection1&amp;wt=xml
				
			
```

###### Warning

In using these methods we can run into some errors.

Don’t lose the [next post to be sure to correctly use every method](https://sease.io/2021/03/common-errors-with-apache-solr-feature-stores-and-models.html)!

## Need Help With This Topic?​​

If you’re struggling to manage learning to rank features stores and models in Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling to manage learning to rank features stores and models in Apache Solr, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)