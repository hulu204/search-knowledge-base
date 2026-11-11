---
title: 'Elasticsearch Disk Space Issue and Rollover Solution'
company: Sease
tag: 工程相关
date: 2022-06-07
url: https://sease.io/2022/06/elasticsearch-disk-space-issue-and-rollover-solution.html
account: 
origin: harvest3-202607
---
Hi readers!

This blog post wants to help all those people who encounter an index writer disk space issue in Elasticsearch.

Let’s start from the first observation, **what do we mean by index writer disk space issue?**

When dealing with a huge amount of data, it is not that unusual to incur a disk-related error. If too many documents are indexed, the disk space can saturate leading to a **BulkIndexError**. This is the log message we would obtain:

```
				
					[ERROR] BulkIndexError: ('500 document(s) failed to index.', [{'index': {'_index': 
'your_index_name', '_type': '_doc', '_id': 'vAAt1H8BpDNDRA5qgPEv', 'status': 403, 'error': 
{'type': 'cluster_block_exception', 'reason': 'index [your_index_name] blocked by: 
[FORBIDDEN/8/index write (api)];’}
				
			
```

**What is this error telling us?**   
The error reports that the writing operation is blocked and therefore no new documents can be indexed in the *your\_index\_name* index. Elasticsearch automatically sets this block when the disk space consumption reaches 80% of the total disk size.

You can check the current index block status through the GET settings API:

```
				
					GET https://localhost:9200/your_index_name/_settings
				
			
```

Here is the parameter to look at in the obtained response:

```
				
					{
    "your_index_name": {
        "settings": {
            "index": {
                ...
                "blocks": {
                    "write": "true"
                },
                "number_of_shards": "2",
                "provided_name": "your_index_name",
                "creation_date": "1650529887595",
                "number_of_replicas": "1",
                "uuid": "2FPWsd-LMHyQSwXaM523GA",
                "version": {
                    "created": "7100299"
                }
            }
        }
    }
}
				
			
```

The aim of this blog post is to answer these two questions:

1. 1. ***How to solve this problem when it arises?***
   2. ***How to prevent the problem from happening again?***

###### TEMPORARY SOLUTION

This wants to be a temporary solution for freeing the disk space and removing the index block.

Here we want to describe an approach that will help you remove unuseful documents in order to free part of the disk and avoid the index block setting.

First of all, we manually remove the index block through this request:

```
				
					PUT /[_all|&lt;your_index_name&gt;]/_settings
{
  "index.blocks.write": null
}
				
			
```

This is necessary because also the delete is a writing operation.

At this point, we can delete some documents. **Be careful and start with a small number of them, since this operation temporarily increases the disk consumption** (until a segment merge happens and the removed documents’ free space is claimed).

After the deletion, we can check the current disk usage through:

```
				
					GET https://localhost:9200/_cat/allocation?v&amp;pretty
				
			
```

Here is the obtained response:

|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `shards` | `disk.indices` | `disk.used` | `disk.avail` | `disk.total` | `disk.percent` | `host` | `ip` | `nod`e |
| `72` | `11.9gb` | `17gb` | `81.2gb` | `98.3gb` | `17` | `x.x..` | `x.x..` | `645784hwe...` |
| `72` | `11.9gb` | `17gb` | `81.2gb` | `98.3gb` | `17` | `x.x..` | `x.x..` | `374562gfi...` |

In case we still need free space, we can repeat this process.  
If the erasing caused the disk consumption to exceed 80%, the lock removal will be necessary again.

We call this a “temporary solution” because it helps us free the disk and remove the index block, but **it doesn’t prevent the error from arising again in the feature.**  
To do that, we recommend automatic management of the index.

###### INDEX LIFECYCLE - ROLLOVER SOLUTION

From Elasticsearch documentation:   
*“The index lifecycle management (ILM)* [[1]](https://www.elastic.co/guide/en/cloud/current/ec-configure-index-management.html) *feature of the Elastic Stack provides an integrated and streamlined way to manage time-based data, making it easier to follow best practices for managing your indices. Compared to index curation, migrating to ILM gives you more fine-grained control over the lifecycle of each index.”*

*“You can configure index lifecycle management (ILM)* [[2]](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-lifecycle-management.html) *policies to automatically manage indices according to your performance, resiliency, and retention requirements. For example, you could use ILM to:*

* + S*pin up a new index when an index reaches a certain size or number of documents*
  + *Create a new index each day, week, or month and archive previous ones*
  + *Delete stale indices to enforce data retention standards*

*You can create and manage index lifecycle policies through Kibana Management or the ILM APIs.”*

This is exactly what we need to avoid our disk issues.   
**We would like to spin up a new index when an index reaches a certain size (I) and delete stale indices (II).**

The first requirement (I) can be achieved thanks to the **rollover strategy** that: *“Rolls over a target to a new index when the existing index meets one or more of the rollover conditions”* [[3]](https://www.elastic.co/guide/en/elasticsearch/reference/current/ilm-rollover.html); while the second requirement (II) can be done through the **definition of a policy**. In the policy, we can define states, actions, and transitions.  
The indexes associated with that policy start from the default state, process the actions in that state, and evaluate the transitions condition. If the condition is true, the indexes will pass to the new state for which again action and transitions will be executed.

From the Elasticsearch documentation: *“An index’s lifecycle policy specifies which phases are applicable, what actions are performed in each phase, and when it transitions between phases”* [[4]](https://www.elastic.co/guide/en/elasticsearch/reference/current/ilm-index-lifecycle.html).

Let’s see together all the necessary steps to create a policy that automates index rollover and deletion. For our example, we are using the Elasticsearch 7.10 version managed by Amazon which includes Open Distro plugins.  
We leverage **Kibana** tools for some of these steps.

###### 1 – Create an index template for Rollover

This template is the one used for rollover. This defines the settings that the newly created index will have.

* + In *index\_patterns* we define the name of the new index. In this case, it starts with *index\_name-* and then an incremental number follows.
  + *index.opendistro.index\_state\_management.rollover\_alias* is the name of the rollover alias. This is associated with the current active index (the one used to index new documents) and will be moved to the new index after the rollover is done.

Here is the request to create the **index template**:

```
				
					PUT /_index_template/template-name
{
  "index_patterns": ["index_name-*"],
  "template": {
   "settings": {
    "index.opendistro.index_state_management.rollover_alias": "rollover-alias-name"
   }
 }
}
				
			
```

**N.B.** If you haven’t Open Distro, these are the equivalent index settings for:  
**Elasticsearch**: index.lifecycle.rollover\_alias  
**Opensearch**: index.plugins.index\_state\_management.rollover\_alias

###### 2 – Create a policy

The second step is the **policy definition**.   
You can add this in Kibana by going into:

Kibana → Index Management → State management policies → Create

At this point, a Policy ID is required, together with the policy definition.

Here is an example:

```
				
					{
    "policy_id": "rollover_policy",
    "description": "Rollover policy for index_name-* indexes.",
    "last_updated_time": 1650529799079,
    "schema_version": 1,
    "error_notification": null,
    "default_state": "hot_state",
    "states": [
        {
            "name": "hot_state",
            "actions": [
                {
                    "rollover": {
                        "min_doc_count": 100
                    }
                }
            ],
            "transitions": [
                {
                    "state_name": "warm_state"
                }
            ]
        },
        {
            "name": "warm_state",
            "actions": [],
            "transitions": [
                {
                    "state_name": "delete_state",
                    "conditions": {
                        "min_index_age": "60d"
                    }
                }
            ]
        },
        {
            "name": "delete_state",
            "actions": [
                {
                    "delete": {}
                }
            ],
            "transitions": []
        }
    ],
    "ism_template": [
        {
            "index_patterns": [
                "index_name-*"
            ],
            "priority": 0,
            "last_updated_time": 1650470897111
        }
    ]
}
				
			
```

This policy has 3 states: *hot\_state*, *warm\_state*, and *delete\_state*.  
Each new index starts with the *default* state which is *hot\_state*.   
Inside the *hot\_state*, the rollover action is defined. It is executed when the *min\_doc\_count* condition is met: when the index contains more than 100 documents.  
After all the actions in *hot\_state* have been done, the transitions are evaluated. In this first *hot\_state*, we automatically decide to pass to the *warm\_state*.   
At this point, the newly created index (in *hot\_state*) is the one in which the new documents will be inserted, while the previous index (in *warm\_state*) evaluates the actions and transitions of its newly assigned state.  
In the *warm\_state* no actions are defined, therefore we directly go to transitions. Here we pass to *delete\_state* when *min\_index\_age* is achieved, therefore when 60 days are passed from the index creation.  
Once in the *delete\_state*, the index is removed.  
In *ism\_template* we define the index name pattern that identifies the indexes to which automatically apply the policy; therefore, this policy will be attached to each newly created index starting with *index\_name-\**.

###### 3 – Create the index (or reindex an existing one)

We can now create the first index. To automatically attach the policy to this index, its name must match the index pattern defined in the *ism\_template* part of the policy.  
In general, here is the name pattern an index should have to apply rollover:

^.\*-\d+$.

We can see that it is important that the name ends with *-some\_digits*. This is because, at each rollover, the newly (automatically) created index will have the same name as the previous one with an increment of 1 in the numerical part.

Here is an example of the index creation:

```
				
					PUT /index_name-000001
				
			
```

###### 4 – Create an alias

###### 

We can now associate an alias with the new index.   
This is used in the rollover phase, therefore **the alias must be the same as the one in the index template (rollover\_alias)**.

```
				
					POST /_aliases
{
    "actions" : [
        { "add" : { "index" : "index_name-000001", "alias" : "rollover-alias-name" } }
    ]
}
				
			
```

The alias can also be specified when creating the index, using the related parameter in the request body:

```
				
					PUT /index-name-000001
{
  "settings": {
	...
  },
  "aliases": {
    "rollover-alias-name": {}
  },
  "mappings": {
    ...
   }
}
				
			
```

###### 5 – Attach the policy to the index (if necessary)

As the final step, we need to attach the policy to the newly created index.   
This is automatically done if the policy is created before the index, otherwise, we need to manually attach the policy.  
Also, this step can be done in Kibana through the Index Management section:

Kibana → Index Management → Indices → Select the index from the list → Apply policy → Select the policy from the list

## Summary

In this blog post, we have seen what is an **index writer disk issue** and how to solve it.

We present two solutions:

1. 1. **Temporary solution:** here we explain how to free space by manually removing the index block to delete unuseful documents. This solution does not avoid the error to appear again.
   2. **Index management solution (with rollover):** here we explain how automatically manage the index in order to avoid the error to appear again. We define a policy that manages a set of indexes (defined by an index name pattern) in order to roll over them when they reach a certain size. The policy will also delete the older indexes to free space.

Thanks for reading and see you in the next blog post!

## Need Help With This Topic?​​

If you’re struggling with an index writer disk issue, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with an index writer disk issue, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)