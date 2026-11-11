---
title: 'Online Search Quality Evaluation With Kibana – Visualization Examples'
company: Sease
tag: 评测
date: 2023-06-16
url: https://sease.io/2023/06/online-search-quality-evaluation-with-kibana-visualization-examples.html
account: 
origin: harvest3-202607
---
To keep the blog post manageable, organized, and easy to follow, it has been divided into two parts.  
The introductory section can be found in the [first post](https://sease.io/2023/03/online-search-quality-evaluation-with-kibana-introduction.html), while in this one we focus only on how to create visualizations and dashboards to compare different ranking models, through practical examples.

As already mentioned, our current scenario involves book e-commerce; consequently, the model evaluation illustrations we describe relate to this domain and represent some of the most effective examples for understanding and evaluating online performance.

## Visualization Examples

In Kibana, there are multiple editors available for creating panels of your data and each editor offers various features and aggregation options.   
For this implementation, we used the following:

* [AGGREGATION-BASED](https://www.elastic.co/guide/en/kibana/current/add-aggregation-based-visualization-panels.html) (DATA TABLE and VERTICAL BAR)
* [TIME SERIES VISUAL BUILDER (TSVB)](https://www.elastic.co/guide/en/kibana/current/tsvb.html) (TABLE)
* [VEGA](https://www.elastic.co/guide/en/kibana/current/vega.html) (VERTICAL BAR)

For each of them, we provide a brief description and demonstrate how they were used for the model evaluation.

##### AGGREGATION-BASED - DATA TABLE

The data table is a visualization tool that presents raw data in a table format, showcasing various aggregations and pre-calculated metrics.

###### EVALUATION EXAMPLE

###### 1) PER MODEL INTERACTIONS DAILY COUNT

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-02-07-alle-12.26.27.png?fit=800%2C263&ssl=1)

The table serves as a tool for assessing the distribution of data by model and day.  
It is focused on `modelA` and records the total number of interactions collected daily, along with specific details on the total number of impressions, clicks, and add-to-carts.  
You can remove the filter if you want to check the same information for both models or create another similar visualization and filter `modelB` interactions.

**IMPLEMENTATION**

**Table Rows (Buckets):**  
– Terms aggregation on `testGroup` field  
– Date Histogram Sub aggregation (per day) on `timestamp` field

**Table Columns (Metrics)**:  
– **Count**: Count aggregation (i.e. total number of interactions)  
– **Sum of impression**: Sum aggregation on `impression` field  
– **Sum of click**: Sum aggregation on `click` field  
– **Sum of addToCart**: Sum aggregation on `addToCart` field

**Filter**:  
– `testGroup: modelA`

**GOAL**

This visualization allows us to easily see the total number of interactions collected each day for a model, which can be helpful in identifying patterns or trends over time.  
Furthermore, the table provides specific details on the number of impressions, clicks, and add-to-carts for each day. This level of detail can be useful for identifying which days a model performed better in terms of engagement or user behavior.

Also, the table can provide valuable insights into whether the testing process is distributing the models equally (or in the desired percentage). It can also help detect any imbalances or disruptions that may affect the model’s performance or compromise the testing results. By identifying any irregularities during the testing process, adjustments can be made to ensure that each model has a fair and equal opportunity to perform.

##### AGGREGATION-BASED – VERTICAL BAR

A vertical bar chart is a visual representation of comparative values of categorical information.

The bars are positioned vertically along the Y-axis, and the values represented by the bars are on the X-axis. The X-axis is used to categorize the data (**aggregated data** i.e. buckets) and the Y-axis represents the quantity of the data within each category (**predefined** **metric** calculation).

###### EVALUATION EXAMPLE

###### 1) PER MODEL QUERY COUNT DISTRIBUTION

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-02-07-alle-15.11.45-2.png?fit=800%2C401&ssl=1)

This visualization shows how the impressions are distributed among the queries for a specific model (`modelA` in this case). The Y-axis represents the number of impressions, while the X-axis displays the different queries (`queryId` in our case). The bars are vertical and their height indicates the number of impressions for each query.

**IMPLEMENTATION**

This is a sample setup for a vertical bar chart in Kibana, which allows you to specify the **metrics** to be displayed on the Y-axis, such as counts, averages, sums, or other calculations based on your data and the **buckets** to be displayed on the X-axis, such as date ranges, terms, or other categories that your data can be grouped by:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-02-07-alle-15.13.06.png?fit=800%2C372&ssl=1)

In particular:

**The X-axis (Buckets):**  
– Terms aggregation on `queryId` field  
– Sorted (Descending) by Sum of impression

**The Y-axis (Metrics)**:  
– **Sum of impression**: Sum aggregation on `impression` field

You can also configure the formatting of the Y and X axes and set the overall size of the chart, customizing its appearance.

It is also possible to limit the data that is displayed in the chart, based on specific conditions or criteria:

**Filter**:  
– `testGroup: modelA`

**GOAL**

The purpose of this visualization is to provide an easily understandable representation of the number of impressions that have been recorded for each query.  
By representing the data visually, it is possible to quickly identify which queries are generating the most impressions and which ones are not performing as well; you can gain insights into what types of queries are most common, and use that information to make further analysis.

##### TIME SERIES VISUAL BUILDER (TSVB) – TABLE

It displays aggregation results in a tabular format but, compared to the aggregation-based editor, allows for the calculation of several **custom metrics** (such as ClickThroughRate and AddToCartRate in this case), which require a specific formula to implement.

###### EVALUATION EXAMPLE

###### 1) GENERAL MODEL EVALUATION

This table is used for the **overall evaluation of the models**. In this case, it represents the performance of two models, `modelA` and `modelB`, compared on common metrics, both pre-calculated (such as the total number of impressions, clicks, and add-to-carts) and customized ones (such as ClickThroughRate and AddToCartRate).

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-02-06-alle-16.30.02.png?fit=800%2C296&ssl=1)

**IMPLEMENTATION**

**Table Rows:**  
– Group by `testGroup` field (*term aggregation*)  
– Rows to display: 2

**Table Columns**:  
– **Total Impressions**: Sum aggregation on `impression` field  
– **Total Clicks**: Sum aggregation on `click` field  
– **Total AddToCarts**: Sum aggregation on `addToCart` field  
– **ClickThroughRate**: Sum aggregation on `click` DIVIDED BY Sum aggregation on `impression`  
– ****AddToCart**Rate**: Sum aggregation on `addToCart` DIVIDED BY Sum aggregation on `click`

**How is it possible to calculate and set up custom metrics like the ClickThroughRate (CTR)?**  
Here is an example:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-02-07-alle-10.27.11.png?fit=800%2C426&ssl=1)

To calculate CTR, we need to first determine the number of clicks and impressions (or views) that a document (or product) has received. This involves using sum aggregation on each field separately and assigning the results to a variable. We can then use the Bucket Script aggregation to implement the CTR formula, specifying the variables’ names (e.g. `params.clicks`) in the Painless Script, allowing us to perform the necessary calculations.

**GOAL**

This visualization allows different models to be evaluated using common metrics that are based on specific requirements for the domain; the use of common metrics ensures that they are being evaluated against the same standards, allowing for fair comparisons.

When setting up the table, you can specify the number of rows to be displayed (usually equal to the number of models to be compared… in this case, 2). If you choose to display more than two rows, this visualization can also aid in **identifying bugs** in the **online testing setup**. By grouping the data based on the ‘`testGroup`‘ field, it may be possible to discover a row with an invalid model name, indicating a problem with the frontend application that is passing a nonexistent model.

###### 2) SINGLE PRODUCT EVALUATION

Another interesting application of this panel type is the evaluation of model performance on **specific products** (books in this case); it is useful to see how the model performs on a product of interest such as a best-seller, new product, most reviewed product, sponsored product, on sale promotional item, etc.

The configuration of the visualization table is exactly the same as in the general evaluation model except for the data filtering. Here we use the ‘*Panel filter*‘ to create a table using only interactions related to a specific product, in this case with `bookId: 9`:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-02-07-alle-10.26.12.png?fit=434%2C450&ssl=1)

###### 3) PER MODEL TOP5 QUERIES

This panel type can also be used to assess the performance of a model on **specific queries**:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-02-07-alle-15.11.24.png?fit=800%2C449&ssl=1)

The table presents multiple metrics for each query and for `modelA`.  
Our focus is on the top 5 queries with the highest number of total interactions. To view this information, we sorted the rows based on query frequency (value count aggregation) and only displayed the first 5 rows.

**IMPLEMENTATION**

**Table Rows:**  
– Group by `queryId` field (*term aggregation*)  
– Rows to display: 5  
– Sorted (Descending) by Frequency

**Table Columns**:  
– **Frequency**: Value Count aggregation on `queryId` field  
N.B. the creation of the other metrics is the same as above, so there is no need to rewrite them

**Filter**:  
– Panel filter: `testGroup: modelA`

**GOAL**

This visualization enables us to determine the most popular queries among users and easily compare them on specific metrics. This allows for a fair comparison and helps to identify which queries are performing better than others.

##### VEGA

Vega is a more complex and powerful panel type. This editor allows users to create highly customized and interactive visualizations.

This popular visualization language allows users to construct complex search queries and aggregations using a JSON-based syntax, making it easy to interact with data stored in Elasticsearch. The results of the query can be visualized in a wide range of visualizations, such as bar charts, line graphs, and scatter plots, and can be combined with other data sources to create complex visualizations in Kibana.

###### EVALUATION EXAMPLE

###### 1) MODEL EVALUATION BASED ON QUERIES’ FREQUENCY

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-02-07-alle-16.02.01.png?fit=800%2C538&ssl=1)

The bar chart displays the “Add to Cart rate” (ATR) for a particular set of queries that has a total impression count of 180 or less.  
Focusing on `modelB`, it showcases only six `queryId`, and use a red line and red text to highlight the average ATR (calculated as the mean of the ATRs of the selected queries).

**IMPLEMENTATION**

**The X-axis:**  
– Terms aggregation on `queryId` field

**The Y-axis**:  
– AddToCart Rate (ATR)

**Filter**:  
– `testGroup: model`B  
– total impression count <= 180

**Marks**:  
– Rule (i.e. red line): average AddToCart Rate (ATR)  
– Text (i.e. red number): average AddToCart Rate (ATR)  
– Text (i.e. blue number): distinct `queryId`

Here is the code to implement this visualization:

```
				
					{
  $schema: https://vega.github.io/schema/vega-lite/v4.json
  title: ATR queries &lt;= 180 impressions

  // Define the data source
  data: {
    url: {

      // Apply dashboard context filters when set
      %context%: true
      %timefield%: timestamp

      // Which index to search
      index: interactions_index
      body: {
        size: 0
        aggs: {
          queryId_by_range: {
            terms: {
              size: 65535
              field: "queryId"
              order: { "_count": "desc" }
            }
            aggs: {
              total_impression: {
                sum: {
                  field: impression
                }
              }
              total_click: {
                sum: {
                  field: click
                }
              }
              total_addToCart: {
                sum: {
                  field: addToCart
                }
              }
              rangeUpto180: {
                bucket_selector: {
                  buckets_path: {
                    doc_count: "_count"
                    impression_count: "total_impression"
                    click_count: "total_click"
                    addToCart_count: "total_addToCart"
                  }
                  script: "params.impression_count &lt;= 180 &amp;&amp; params.click_count &gt;= params.addToCart_count"}
              }
              AddToCartRate: {
                bucket_script: {
                  buckets_path: {
                    clicks: "total_click"
                    addToCarts: "total_addToCart"
                  }
                  script: {source: "params.addToCarts / params.clicks"}
                }
              }
            }
          }
        }
      }
    }

    format: {property: "aggregations.queryId_by_range.buckets"}
  }

  layer: [{
    mark: bar
    encoding: {
      x: {
        field: key
        type: nominal
        axis: {
          title: "Query id"
          labels:false
        }
      }
      y: {
        field: AddToCartRate.value
        type: quantitative
        axis: {title: "AddToCart rate"}
      }
    }
  }
  {
    mark: rule
    encoding: {
      y: {
        aggregate: mean
        field: AddToCartRate.value
        type: quantitative
      }
      color: {value: "red"}
      size: {value: 3}
    }
  }
  {
    mark: {
     type: text
     baseline: line-bottom
    }
    encoding: {
      text:{
        aggregate: mean
        field: AddToCartRate.value
        type: quantitative
      }
      color: {value: "red"}
      size: {value: 30}
    }
  }
  {
    mark: {
     type: text
     baseline: line-top
    }
    encoding: {
      text: {
        aggregate: distinct
        field: key
        type: quantitative
      }
      color: {value: "blue"}
      size: {value: 30}
    }
  }
  ]
}
				
			
```

This is a Vega-Lite visualization specification written in JSON format.  
It defines a bar chart to show the “AddToCart rate” (ATR) for a specific group of queries, with the data coming from an Elasticsearch index (i.e. `interactions_index`).

Let’s explain each piece of code:

```
				
					aggs: {
  queryId_by_range: {
    terms: {
      size: 65535
      field: "queryId"
      order: { "_count": "desc" }
    }
    aggs: {
      total_impression: {
        sum: {
          field: impression
        }
      }
      total_click: {
        sum: {
          field: click
        }
      }
      total_addToCart: {
        sum: {
          field: addToCart
        }
      }
				
			
```

This is an**aggregation query** that computes several metrics for each unique value of the `queryId` field in the index. The first aggregation level “queryId\_by\_range” groups the data by `queryId` values and sorts them in descending order based on their frequency of occurrence. Within each `queryId` group, there are three sub-aggregations that calculate the total number of impressions, clicks, and add-to-cart events associated with each query.

```
				
					rangeUpto180: {
  bucket_selector: {
    buckets_path: {
      doc_count: "_count"
      impression_count: "total_impression"
      click_count: "total_click"
      addToCart_count: "total_addToCart"
    }
    script: "params.impression_count &lt;= 180 &amp;&amp; params.click_count &gt;= params.addToCart_count"
  }
}
				
			
```

A **bucket selector query** is used to filter the aggregation results produced by the previous query on two conditions: the total number of impressions associated must be less than or equal to 180, and the total number of clicks must be greater than or equal to the total number of add-to-cart events associated with that bucket (to remove invalid interactions because in general, it is not expected for there to be more “add to cart” actions than clicks on a single query).

```
				
					AddToCartRate: {
  bucket_script: {
    buckets_path: {
      clicks: "total_click"
      addToCarts: "total_addToCart"
    }
    script: {source: "params.addToCarts / params.clicks"}
  }
}
				
			
```

A **bucket script aggregation** is used to calculate the “AddToCart rate” (ATR) for each bucket in the previous aggregation pipeline by dividing the total number of add-to-cart events by the total number of clicks.

```
				
					layer: [{
  mark: bar
  encoding: {
    x: {
      field: key
      type: nominal
      axis: {
        title: "Query id"
        labels:false
      }
    }
    y: {
      field: AddToCartRate.value
      type: quantitative
      axis: {title: "AddToCart rate"}
    }
  }
}
				
			
```

This is the part where the **bar chart** is defined; the x-axis is mapped to the “key” field, which contains the `queryId` extracted with the bucket selector, while the y-axis is mapped to the “AddToCartRate.value” field, which contains the calculated ATR for each `queryId` value.

The chart also includes several **layer elements**, such as a red line for the average ATR (i.e. calculating the mean of the ATRs of the 6 selected queries):

```
				
					{
  mark: rule
  encoding: {
    y: {
      aggregate: mean
      field: AddToCartRate.value
      type: quantitative
    }
    color: {value: "red"}
    size: {value: 3}
  }
}
				
			
```

a red text for the average ATR value:

```
				
					{
  mark: {
    type: text
    baseline: line-bottom
  }
  encoding: {
    text:{
      aggregate: mean
      field: AddToCartRate.value
      type: quantitative
    }
    color: {value: "red"}
    size: {value: 30}
  }
}
				
			
```

and a blue text for the number of unique `queryId`:

```
				
					{
  mark: {
    type: text
    baseline: line-top
  }
  encoding: {
    text: {
      aggregate: distinct
      field: key
      type: quantitative
    }
    color: {value: "blue"}
    size: {value: 30}
  }
}
				
			
```

**GOAL**

The visualization is useful for evaluating the performance of models on **queries grouped according to the search demand curve**. The search demand curve can be thought of as a representation of the popularity of different queries among users. Usually, there are few queries very often searched by users and many queries that are rarely searched by users. By grouping queries based on their level of demand, search engines can provide more relevant and useful results to users.

It might be more interesting to focus on the model performance of the most frequent queries, and this analysis might help to consider alternative approaches such as using multiple models.

###### 2) MODEL EVALUATION BASED ON QUERIES’ RESULTS/HITS

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-02-07-alle-16.16.01.png?fit=800%2C522&ssl=1)

The bar chart displays the “Add to Cart rate” (ATR) for a specific group of queries that have 10 or fewer total search results or query hits.  
Focusing on `modelB`, it showcases only three `queryId` and uses a red line and red text to highlight the average ATR, calculated as the mean of the ATRs of the selected queries.

**IMPLEMENTATION**

**The X-axis:**  
– Terms aggregation on `queryId` field

**The Y-axis**:  
– AddToCart Rate (ATR), sum aggregation on `addToCart` DIVIDED BY sum aggregation on `click`

**Filter**:  
– `testGroup: model`B  
– `queryResultCount` <= 10

**Marks**:  
– Rule (i.e. red line): average AddToCart Rate (ATR)  
– Text (i.e. red number): average AddToCart Rate (ATR)  
– Text (i.e. blue number): distinct `queryId`

The code to implement this visualization is nearly identical to the previous example, with the exception of the absence of the ‘`rangeUpto180`‘ bucket selector, since in this case, you do not want to filter by query frequency.  
Instead, a filter was applied using the “Add filter” pop-up to exclude documents where `queryResultCount` is greater than 10:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-02-08-alle-09.25.39.png?fit=800%2C349&ssl=1)

The related *Elasticsearch Query DSL* is:

```
				
					{
  "query": {
    "range": {
      "queryResultCount": {
        "gte": null,
        "lte": 10
      }
    }
  }
}
				
			
```

**GOAL**

This visualization can be used to assess the performance of models on **queries grouped by the number of search results returned**.

It might be more interesting to focus on the model performance of queries with a larger number of results because, with a low number of search results (such as 1 or 3), we expect the difference between models to be neglectable, as minor variations in search outcomes (i.e. different order) are unlikely to cause significant changes in user behavior.

## Dashboard Examples

Kibana dashboards are used to display data stored in Elasticsearch in a user-friendly and interactive way, making it easy to gain insights and make data-driven decisions. It is a collection of visualizations that you can arrange, resize, and edit.

Simply go to the “Dashboard” tab, create a new dashboard (or edit an existing one), click on the “Add” button to add the visualization to the dashboard, and position and size the visualization as desired.

Here are examples of 2 dashboards:

**1) Global evaluation of both models on different devices**

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-02-06-alle-16.41.08.png?fit=800%2C116&ssl=1)

The above dashboard is related to the general evaluation of the models (previously discussed).  
In this case, we created two visualizations, one that selects only interactions with the desktop device (Panel options | Panel filter -> `userDevice: desktop`) and one that selects only interactions with the mobile device (Panel options | Panel filter -> `userDevice: mobile`).

We then arrange them side by side in a dashboard so that we can quickly get a comprehensive view of the data and make it easier to evaluate the performance of models on *different devices*.

**2) Global evaluation of both models across various ranges of query results**

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2023-02-07-alle-15.27.21.png?fit=800%2C338&ssl=1)

The second dashboard is related to the model evaluation based on query hits (previously discussed).  
We have created a unique dashboard that displays 6 visualizations side by side, each based on a different range of query results. The visualizations are organized as follows:

* The first row is solely dedicated to visualizations related to `modelA`, while the second row is dedicated to those related to `modelB`.
* The visualizations on the left showcase the average ATR for queries with less than or equal to 10 search results/hits.
* The visualizations in the center display the average ATR for queries with search results between 10 and 50.
* The visualizations on the right present the average ATR for queries with search results higher than 50.

The dashboard is incredibly valuable as it provides a comprehensive view of the data at a glance, making it easier to assess the performance of both models (on ATR) across various ranges of query results.

## Summary

The purpose of these two blog posts was to showcase the effectiveness of utilizing Kibana in analyzing the results of online search quality evaluations when comparing different ranking models with live users.

Our goal was to simplify the understanding of concepts for users and enable them to efficiently and effectively implement them through Kibana’s user-friendly graphical interface.

We hope you enjoyed it and if you have any questions please feel free to leave a comment below!

## Need Help with this topic?​

If you're struggling with Kibana, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)