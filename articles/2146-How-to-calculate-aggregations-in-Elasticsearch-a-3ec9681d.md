---
title: 'How to calculate aggregations in Elasticsearch as percentages?'
company: Sease
tag: 工程相关
date: 2024-08-05
url: https://sease.io/2024/08/how-to-calculate-aggregations-in-elasticsearch-as-percentages.html
account: 
origin: harvest3-202607
---
Hi Elasticsearch users,

Suppose to have a dataset containing 5,000 documents, each representing a unique e-commerce interaction coming from various user devices such as mobile phones, desktop computers, and tablets.  
The aim is not only to find the number of documents per **user device** category but also to calculate their respective percentages.  
**How can this be done in Elasticseach?**

Thanks to the aggregation capabilities in Elasticsearch, you can use the “**terms aggregation**” to get the document count per source and a “**bucket script aggregation**” to calculate the percentages.

In this short ‘tips and tricks’ blog, let’s see in detail how to do it!

## What is a Terms Aggregation?

[Terms aggregation](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-terms-aggregation.html) is a bucket aggregation that allows you to find the unique values for a field across your documents, creating a bucket for every unique term it encounters for the specified field.  
The query will return a set of unique values and their counts for the specific field, specifically one bucket per unique value.

## What is a Bucket Script Aggregation?

[Bucket Script Aggregation](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-pipeline-bucket-script-aggregation.html#search-aggregations-pipeline-bucket-script-aggregation) in Elasticsearch allows the execution of a script that can perform per-bucket computations on specified metrics.  
In simpler terms, it is a way to create a script when it is necessary to perform customized calculations on data after it has been aggregated.

## Example case

The following query is designed to calculate the percentage of different user device types (mobile, desktop, and tablet) among a set of documents:

```
				
					GET /interactions_collection/_search
{
    "size": 0,
    "aggs": {
        "filters_agg": {
            "filters": {
                "filters": {
                    "userDevice_count": {
                        "match_all": {}
                    }
                }
            },
            "aggs": {
                "userDevice_unique_values": {
                    "terms": {
                        "field": "userDevice"
                    }
                },
                "mobile_count_percentage": {
                    "bucket_script": {
                        "buckets_path": {
                            "mobile_count": "userDevice_unique_values['mobile']&gt;_count",
                            "total_count": "_count"
                        },
                        "script": "(params.mobile_count * 100)/params.total_count"
                    }
                },
                "desktop_count_percentage": {
                    "bucket_script": {
                        "buckets_path": {
                            "desktop_count": "userDevice_unique_values['desktop']&gt;_count",
                            "total_count": "_count"
                        },
                        "script": "(params.desktop_count * 100)/params.total_count"
                    }
                },
                "tablet_count_percentage": {
                    "bucket_script": {
                        "buckets_path": {
                            "tablet_count": "userDevice_unique_values['tablet']&gt;_count",
                            "total_count": "_count"
                        },
                        "script": "(params.tablet_count * 100)/params.total_count"
                    }
                }
            }
        }
    }
}
				
			
```

The “bucket\_script” aggregations are used to perform calculations based on the counts obtained in the previous aggregations. These calculations involve determining the percentage of each device type among the total document count.

**RESPONSE**

```
				
					},
    "aggregations": {
        "filters_agg": {
            "buckets": {
                "userDevice_count": {
                    "doc_count": 5000,
                    "userDevice_unique_values": {
                        "doc_count_error_upper_bound": 0,
                        "sum_other_doc_count": 0,
                        "buckets": [
                            {
                                "key": desktop,
                                "doc_count": 1271
                            },
                            {
                                "key": "mobile",
                                "doc_count": 1268
                            },
                            {
                                "key": "tablet",
                                "doc_count": 1244
                            },
                            {
                                "key": " ",
                                "doc_count": 1217
                            }
                        ]
                    },
                    "mobile_count_percentage": {
                        "value": 25.36
                    },
                    "desktop_count_percentage": {
                        "value": 25.42
                    },
                    "tablet_count_percentage": {
                        "value": 24.88
                    }
                }
            }
        }
    }
}
				
			
```

The response to the query provides aggregation results as follows:  
– “userDevice\_count” has a total document count of 5000.  
– “userDevice\_unique\_values” provides unique values of the “userDevice” field along with their document counts.  
– and we then have “mobile\_count\_percentage”, “desktop\_count\_percentage” and “tablet\_count\_percentage” indicating the percentage of documents from each device separately.

## Limitations

The proposed Elasticsearch query requires prior knowledge of the unique values for the `userDevice` field. This approach might be limiting if the values of `userDevice` change over time or are not known in advance.  
If you are running this query as a one-off, knowing the specific unique values (like ‘mobile’, ‘desktop’, ‘tablet’) might be sufficient.

However, if your goal is to perform this analysis automatically and handle any potential unique values of `userDevice` that might appear in the future, the current query structure is not ideal, but it’s recommended to use two separate queries.  
This approach is necessary because, as of the current Elasticsearch functionalities, there is no direct way to automatically create bucket paths for dynamic unique values within a single query.  
This limitation means you need to first identify all unique values present in the `userDevice` field and then construct a query that can calculate percentages based on these identified values.

I hope you have found this post helpful in addressing your specific use cases. Understanding how to leverage Elasticsearch’s aggregation capabilities to analyze and calculate percentages within the data can be a valuable skill to gain insights.

Would you do it differently? Would love your thoughts, please share your opinion in the comments below!

If you have questions or need further guidance, please do not hesitate to contact us.

## Need Help With This Topic?​​

If you’re struggling with How to calculate aggregations in Elasticsearch as percentages, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Elasticsearch search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with How to calculate aggregations in Elasticsearch as percentages, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Elasticsearch search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)