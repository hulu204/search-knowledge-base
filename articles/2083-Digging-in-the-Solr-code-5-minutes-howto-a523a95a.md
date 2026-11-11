---
title: 'Digging in the Solr code: 5 minutes howto'
company: Sease
tag: 工程相关
date: 2019-12-31
url: https://sease.io/2019/12/digging-in-solr-be-ready-in-5-minutes.html
account: 
origin: harvest3-202607
---
Let’s say you need to write a component, a [request handler](https://sease.io/2019/12/the-request-handlers-jungle-handleselect-and-qt-parameter.html), or, in general, some piece of custom code that needs to be plugged into Solr. Or, you need to have a deeper understanding of some Lucene/Solr internals, following what happens within the code.

I know: unit tests, integration tests, everything to make sure things behave as you would expect; but here I’m talking about something different: while developing, it is (at least for me) very useful a **productive and debug environment** where it is possible, using short dev iterations, to follow step by step what’s happening within the code, taking a deep look at how things work behind the scenes.

In my experience, I found that useful in a couple of scenarios:

* **I have to write some Solr add-ons**: in this case, I want to have a development environment which allows me to write and debug code as fast as possible
* **I have to study some Solr internals**: let’s say for example I need to check what happens at retrieval time when a field is both docValues=”true” and stored=”true”; where does Solr get the field value from?

Let’s see how both of them can be accomplished in a few minutes!

## Step #1: clone our template repository

Clone the following repository [[1]](https://github.com/SeaseLtd/solr-addon-project-skeleton)

Once imported into your favourite IDE, the project layout will look like this:

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/12/template-project-imported-1.png?fit=800%2C800&ssl=1)

As you can see, the template project provides:

* **A custom *TokenFilter*** that simply prints in the standard out the output tokens during the text analysis. **Note this is just an example** (useful if you want to debug an analyzer): I could have created a *SearchComponent,* a *Tokenizer* or whatever I’d need.
* a **sample Solr configuration**, with a minimal set of things configured
* a **Test Supertype layer** (*BaseIntegrationTest*) and **a sample Test** (*Tests*) which loads some data, executes a query and then prints out the results.

**Surprisingly, that’s all! There’s no second step!**

##### Use Case #1: implement, debug and test an add-on

As previously said, in the example repository we already have a simple add-on which consists of a *TokenFilter* that prints in the standard output each token produced in the analysis chain. The filter has been declared in the Solr configuration as part of “text” field type analyzer:

```
				
					&lt;fieldType name="text" class="solr.TextField"&gt;
    &lt;analyzer&gt;
        ...
        &lt;filter class="io.sease.labs.solr.SystemOutTokenFilterFactory"/&gt;
    &lt;/analyzer&gt;
&lt;/fieldType&gt;
				
			
```

The test class triggers that analyzer because it indexes some documents, so if you run it as a plain *JUnit* test, you will see the following output:

```
				
					startOffset=0,endOffset=6,positionIncrement=1,positionLength=1,type=word =&gt; Object
startOffset=7,endOffset=15,positionIncrement=1,positionLength=1,type=word =&gt; Oriented
startOffset=16,endOffset=24,positionIncrement=1,positionLength=1,type=word =&gt; Software
startOffset=25,endOffset=37,positionIncrement=1,positionLength=1,type=word =&gt; Construction
startOffset=0,endOffset=6,positionIncrement=1,positionLength=1,type=word =&gt; Design
startOffset=7,endOffset=16,positionIncrement=1,positionLength=1,type=word =&gt; Patterns:
startOffset=17,endOffset=25,positionIncrement=1,positionLength=1,type=word =&gt; Elements
startOffset=26,endOffset=28,positionIncrement=1,positionLength=1,type=word =&gt; of
startOffset=29,endOffset=37,positionIncrement=1,positionLength=1,type=word =&gt; Reusable
startOffset=38,endOffset=53,positionIncrement=1,positionLength=1,type=word =&gt; Object-Oriented
startOffset=54,endOffset=62,positionIncrement=1,positionLength=1,type=word =&gt; Software
 
DOC 1 
id = 1
title = Object Oriented Software Construction

DOC 2 
id = 2
title = Design Patterns: Elements of Reusable Object-Oriented Software
				
			
```

If you put a breakpoint in the token filter and re-run the *Tests* class in debug mode, the debugger will stop at that line as expected:

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/12/debug-1.png?fit=800%2C656&ssl=1)

##### Use Case #2: debugging Solr internals

In this case there’s no custom code because remember, the goal is to investigate some Solr internals. Specifically, the question I have to answer in this example is: assuming we have a field

```
				
					&lt;field name="myfield" type="string" docValues="true" stored="true"/&gt;
				
			
```

and a request

```
				
					q=...&amp;...&amp;fl=myfield
				
			
```

Where does Solr get the field value from [[1]](https://issues.apache.org/jira/browse/SOLR-8344)?

The first thing I have to do is to change something in the project:

* + **schema.xml**: add the field definition above
  + ***Tests* class**: change the query parameters (adding **fl=myfield**) and add some value for the *myfield* field in the indexed documents.

Now, a premise: since the goal of this blog post is not to answer the question above, we will skip all the investigation phases needed to understand the overall query execution flow and to detect the right place where we will put the breakpoint.

After some investigation, we understand the *RetrieveFieldOptimizer* class plays a fundamental role in that process (*this class – and the optimisation as well – has been introduced in Solr 7.*), so let’s open it and put some breakpoints:

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/12/retrieveFieldOptimizer-1.png?fit=799%2C1024&ssl=1)

As you can see, the name and the intent of that class are quite clear, but I still want to see what happens at runtime: let’s start the *Tests* class in debug mode and, as expected

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/12/debug_1.png?fit=976%2C1344&ssl=1)

I can see the field “myfield” has been collected in the “storedFields” set, while the dvFields (DocValues fields) set is empty, even if the field has the docValues flag enabled. So that probably suggests something…

Moving forward, we arrive at the *optimize* method, where we meet the optimisation described in SOLR-8344 [[3]](https://issues.apache.org/jira/browse/SOLR-8344):

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/12/debug_2.png?fit=1084%2C1134&ssl=1)

Again, this is just an example and the goal here is not to describe the findings; however, briefly, it says that if all requested fields

* + have the *docValues* and *stored* flags enabled
  + are not multivalued

then Solr retrieves the values **only from docValues**.

## Need Help With This Topic?​​

If you’re struggling with the debug environments, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with the debug environments, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)