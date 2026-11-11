---
title: 'Benchmark Apache Solr Performance with Apache JMeter'
company: Sease
tag: 工程相关
date: 2023-02-22
url: https://sease.io/2023/02/benchmark-apache-solr-performance-with-apache-jmeter.html
account: 
origin: harvest3-202607
---
If you are familiar with Apache Solr and have no idea how to create a Solr performance test, you are in the right place.

This blog post illustrates how to create Solr benchmarks using the JMeter tool. The purpose is not to be specific and detailed about Jmeter, so we will not describe all the JMeter features, but we just want to give you an overview of how to set up a performance test with JMeter with Apache Solr as a target.

We will stress test Apache Solr query time capabilities by submitting several queries, where the query term (of a specific field) changes each time, to simulate real users sending multiple requests to the server.

## What is Performance Testing

Performance testing is the generic name for tests that check the behavior of your system (website, apps, servers, databases, networks, etc. ) and how it performs under both normal and extreme conditions.

It is considered a critical phase of any software application in order to verify and validate its performance and quality assurance.

Performance testing is a superset of various testing types, such as:

Each test can be used to analyze various factors such as speed, response times, load times, and scalability in order to identify bottlenecks or bugs and decide how to optimize your application.

## What is Apache JMeter

JMeter is an open-source tool, provided by the Apache Software Foundation, able to conduct all performance testing types, including load and stress testing. It is a 100% pure Java Application, therefore you should have no problem running it on every OS where Java is installed.

###### JMeter features:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-10-11-alle-08.24.52.png?fit=300%2C270&ssl=1)

* open source (free of cost)
* easy installation and intuitive GUI (*graphical user interface)*
* able to analyze and measure the performance of a variety of services/different server types
* full multi-threading framework (i.e. several separate thread groups may perform simultaneously)
* able to support multi-protocol and multiple testing strategies
* enormous testing capabilities
* test results can be displayed and saved in different formats

***Note**: This example procedure shows how to install Jmeter and configure a performance test using Mac OS*.

##### Install Apache JMeter

***Prerequisites***: `Java 8+ for Apache JMeter 5.5`

* Download the latest version of JMeter from the [Apache JMeter website](https://jmeter.apache.org/download_jmeter.cgi)
* Verify the integrity of the downloaded file, both *sha512* and *PGP* keys:

```
SHA
1) Click on sha512

2) Open the Terminal from /Applications/Utility/ and enter:
openssl sha512 /path/to/file/apache-jmeter-5.5.zip

3) Verify that the output from the previous command matches the SHA key obtained in step 1

PGP
1) Download the PGP key:
wget -q https://downloads.apache.org/jmeter/binaries/apache-jmeter-5.5.zip.asc

2) Verify the downloaded file against the key:
gpg --verify /path/to/key/apache-jmeter-5.5.zip.asc /path/to/file/apache-jmeter-5.5.zip

3) If you get the error message "No public key" (C4923F9ABFB2F1A06F08E88BAC214CAA0612B399), it means that it is unknown on your local machine, so you need to import it from the PGP servers, e.g:
gpg --keyserver pgpkeys.mit.edu --recv-key C4923F9ABFB2F1A06F08E88BAC214CAA0612B399

Once imported, you should be able to repeat step 2 successfully
```

* Extract the zip file to a location where you want to work with it
* Open the terminal from the /bin folder and enter the following command to open JMeter with GUI:

```
./jmeter.sh
```

You should now be able to see the GUI console and start to configure your *Test Plan*.

## Solr Performance Testing using JMeter

In this blog post, we show a very simple example of Apache Solr performance analysis using JMeter.

**We want to test Solr search requests and measure performance by generating virtual users hitting the server as if they were real users sending multiple requests.**

JMeter allows you to reproduce this type of test by creating several Solr queries (requests), where the query term (of a specific field) changes each time. In this way, we are able to test and evaluate a number of different metrics both on individual requests and as a whole.

To reproduce this test you should have a Solr running locally on port 8983 and a collection on which queries should be executed.

In fact, for this practical example, we have created a collection called *wiki\_ita*, where we have indexed thousands of Wikipedia documents in Italian, and we have tested Solr, making several queries on the “*text*” field.

## Example Test Configuration

The **Test Plan** is the root element of JMeter and can be composed of several elements, designed for specific purposes that allow you to define both variable and default parameters.

In this case, we have set up a minimal test that only consists of a Thread Group, a Sampler, Listeners, and Config Elements; if you are curious you can find the complete list of elements [here](https://jmeter.apache.org/usermanual/test_plan.html).

Everything included in a test plan runs in a defined sequence.

Here are the main steps to configure this example test:

##### 1. Add Thread Group

*Right-click on Test Plan → Add → Threads (Users) → Thread Group*

This is the entry point for all tests and it is important to set up the “Thread Properties” to specify how you want requests to behave:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-10-18-alle-08.11.19.png?fit=800%2C659&ssl=1)

In particular, you should define:

***Number of Threads (Users)***: the number of threads/users connecting to the server

In our case we have set 1000: this value is equal to the number of terms in the CSV file, which we will see shortly.

***Ramp-up period (seconds)***: is used to determine how long JMeter takes to run all threads so it tells JMeter how to distribute the start of the threads (delay between them).

As you can read from the [documentation](https://jmeter.apache.org/usermanual/test_plan.html#thread_group), you can “*start with **Ramp-up = number of threads** and adjust up or down as needed*“.

If you have 1000 threads and 1000 seconds of Ramp-Up time, it means that JMeter takes 1000 seconds to get all 1000 threads running and each thread will start 1 (1000/1000) second after the previous thread was begun.

If you want to perform multiple requests at the same time, you could set the Ramp-up period to 100 seconds, as in this example, so that JMeter adds 10 users each second.

***Loop Count*:** the number of times tests are executed (for the number of users).

In this case, we left the default value, which is 1.

You can also set the action to be taken in case of an error or you can decide to schedule your test specifying the duration time or the start and the end time.

##### 2. Add Configuration Element

Configuration items are used to configure requests sent to the server, allowing us to set default values and declare variables, which are later used by samplers. They are executed at the beginning, then before the actual request.

###### HTTP Request Defaults

*Right-click on Thread Group → Add → Config Element → HTTP Request Defaults*

It is used to define default parameters such as hostname and server port when you need to send multiple requests (of the same type) to the same server.

It is advisable to use it as it makes Jmeter easily maintainable, avoids duplication, and reduces the chance of error if the server name or IP changes over time:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-10-18-alle-08.07.56.png?fit=800%2C244&ssl=1)

For this test, the protocol used is the default, `HTTP`, the server name is `localhost` and the port number is `8983`.

[User manual](https://jmeter.apache.org/usermanual/component_reference.html#HTTP_Request_Defaults)

###### CSV Data Set Config

*Right-click on Thread Group → Add → Config Element → CSV Data Set Config*

If you need to use external data for testing, JMeter provides a configuration element, called ***CSV Data Set Config***, able to use data stored in a .csv file format only. It reads each line of a file and splits it into variables:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-10-18-alle-08.10.11.png?fit=800%2C299&ssl=1)

In our case, we have created a CSV file (*CSVQueryTerms.csv*) that contains 1000 terms. It looks like this:

```
				
					term
computer
relax
stress
shopping
brand
ticket
web
team
...
...
match
				
			
```

Our goal is to use each term in the file as a query term for the test.

In the configuration part, there are a few mandatory fields that you need to configure to run a test:

***Filename*** which defines the name of the file to be read (provide the full path if it is in a different directory than the “Test Plan” (i.e. .jmx file)).

***Variable Names***, which defines the list of variable names separated by a comma; in our case, we can leave this field empty since JMeter supports CSV header lines and the first line of the file is read and interpreted as the list of column names. Therefore, JMeter will treat the first line (*term*) as Variables Name and read the data from the second line.

We left the default values in the other fields.

‘*Sharing Mode* equals *All threads*‘ means that the file is only opened once, and each thread will use a different line of the file.

You can read more about this configuration element in the [JMeter user manual](https://jmeter.apache.org/usermanual/component_reference.html#CSV_Data_Set_Config).

##### 3. Add Controller (Sampler | HTTP Request)

Samplers (a type of JMeter controller) are the components used to send a request to a server and get its response. In our case, we have used the HTTP Request sampler.

*Right-click on Thread Group → Add → Sampler → HTTP Request*

Our purpose is to create requests to the Solr server, such as the following:

```
				
					http://localhost:8983/solr/COLLECTION_NAME/select? q=FIELD_NAME:QUERY_TERM&amp;fl=id,title,text&amp;debug=all
				
			
```

Therefore, in this configuration part, you can enter all the details of the request:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-10-18-alle-08.12.02.png?fit=800%2C248&ssl=1)

In our case, the server name and port number are blank as they are already set in the HTTP Request Defaults Config element.

The method selected is GET and we entered the path: `/solr/wiki_ita/select`

Then you can add the request parameters, and for simplicity we only used:

* + **q: text:${term}** (the main query parameter)

* + **fl: id,title,text** (to select only a specified list of fields in the query response)

* + **debug: all** (return all available debug information about the request: query, timing, score results)

What you can immediately see is that by adding the variable name to the query parser parameter that defines the query (*q*), we will able to use the values extracted from the CSV file:

```
				
					field_name:${variable_name}
				
			
```

Therefore, JMeter will create the following URL request:  
  
*e.g. first line of the CSV file*

```
				
					http://localhost:8983/solr/wiki_ita/select?q=text:computer&amp;fl=id,title,text&amp;debug=all
				
			
```

##### 4. Add Listeners

*Right-click on Thread Group → Add → Listener → View Results Tree | View Results in Table | etc.*

Finally, to view and summarize the test results, you need to add one or more [Listeners](https://jmeter.apache.org/usermanual/listeners).

A listener is a component that displays the results of the samples, so is the most important part of JMeter’s test plan. There are various listeners that show results in different forms such as a table, tree, graph, and log file; you can choose the most suitable and interesting for your specific case.

In this example we have chosen:

###### View Results Tree

The advantage of using this listener is that you can check both requests and responses.

It displays all the samples (succeeded or failed) and all related assertions in the order in which they are generated by the JMeter script.

For each of them (in our case 1000 HTTP Requests) it provides:

**Sampler results**:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-10-18-alle-08.13.00.png?fit=800%2C557&ssl=1)

It contains general response information about load time, latency, and size in bytes.

**Request** (body and headers):

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-10-18-alle-08.13.37.png?fit=800%2C198&ssl=1)

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-10-18-alle-08.13.42.png?fit=800%2C299&ssl=1)

We can check that the term for the *q* parameter for each request is updated with the values extracted from the CSV file used in the CSV Data Set Config, such as:

```
				
					GET http://localhost:8983/solr/wiki_ita/select?q=young&amp;fl=id,title,text&amp;debug=all GET http://localhost:8983/solr/wiki_ita/select?q=text:computer&amp;fl=id,title,text&amp;debug=all GET http://localhost:8983/solr/wiki_ita/select?q=text:relax&amp;fl=id,title,text&amp;debug=all ...
				
			
```

**Response data** (body and headers):

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-10-18-alle-08.16.43.png?fit=800%2C534&ssl=1)

Here is the complete result set that Solr returns to the client in response to a query; by default, it returns 10 documents at a time.

The response can be displayed in different formats, such as Text, Regexp tester, Boundary Extractor Tester, CSS/JQuery Tester, Xpath Tester, JSON Path tester, HTML, HTML Source Formatted, HTML (download resources), Document, JSON, XML, Browser.

###### Summary Report

It’s a table format listener where a row is created for each HTTP request sampler from your test, in our case, it’s just one:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-10-18-alle-08.17.38.png?fit=800%2C179&ssl=1)

It summarizes different performance test metrics of the total number of requests sent to the server during the test duration (i.e. 1000):

* **Samples**: number of requests sent
* **Average**: mean responses time
* **Min**: minimal response time (ms)
* **Max**: maximum response time (ms)
* **Std. Dev.**: shows exceptional cases that deviate from the average response time value. The less, the better
* **Error%**: the percentage of failed requests
* **Throughput**: how many requests per second your server handle (the larger the better)
* **Received** – **Sent KB/Sec**: how many KB per second are received by the client – sent to the server
* **Avg. Bytes**: average response size  
    
    
  This listener is similar to the ‘Aggregated Report’ but consumes less memory since it does not provide percentile values.

###### View Results in Table

If you need something similar to the View Results Tree but in table form, you can use this listener:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-10-18-alle-08.18.17.png?fit=800%2C587&ssl=1)

For each sample, it provides information about execution results, time-related data (latency, connect time, sample time), and bytes.

However, it is not recommended to use it for load tests, but only for functional tests, due to the consumption of a large amount of CPU/memory.

JMeter also provides graphical analyses, adding for example the ‘Graph Results’ or ‘Response Time Graph’ listeners.

##### 5. Run Test and View the results

When everything is configured, you need to save the JMeter test before running the test (by clicking the green play button).

###### What exactly will JMeter do?

For each user (i.e. each term of the CSV file) it will:  
– create a request  
– send it to the server  
– receive and process the server response  
– generate test results in different formats so that they can be analyzed by the tester

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-10-11-alle-08.42.29.png?fit=800%2C432&ssl=1)

***N.B.***

You can use the GUI to set up and test your “Test Plan”, but for huge request volumes, it is recommended to use the [CLI (command-line interface) mode](https://jmeter.apache.org/usermanual/get-started.html#non_gui) to actually run it.

Therefore, it is better to run the test without any listeners; subsequently, the generated results file can be opened using the GUI and imported into any desired listener.

Another plus point of Jmeter is the ability to write the results into a file and save them in different formats.

## Final considerations

I hope this practical example will help you understand how to create Solr benchmarks using the JMeter tool.

An alternative tool for performance testing is [SolrMeter](https://github.com/tflobbe/solrmeter) which was created specifically for Solr, but the project is not maintained anymore and may have some bugs, that’s why it’s better to use JMeter (or other tools).

Try to adapt this practical example according to your case and your schema.

When running performance tests, make sure what you actually want to test and make sure you are using query sets that actually represent your domain and how you are using Solr to get relevant performance analytics.

## Need Help With This Topic?​​

If you’re struggling with apache solr performance testing, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with apache solr performance testing, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)