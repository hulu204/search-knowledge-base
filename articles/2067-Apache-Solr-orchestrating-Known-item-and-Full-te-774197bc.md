---
title: 'Apache Solr: orchestrating Known item and Full-text search'
company: Sease
tag: 查询理解
date: 2018-05-30
url: https://sease.io/2018/05/known-item-search-apache-solr.html
account: 
origin: harvest3-202607
---
## Scenario

You’re working as a search engineer for XYZ Ltd, a company which sells electric components. XYZ provided you the application logs of the last six months, and some business requirements.

##### Two kinds of customers, two kinds of requirements, two kinds of search

The log analysis shows that XYZ has mainly two kinds of customers: the first group, the “expert” users (e.g. electricians, resellers, shops) whose members are querying the system by product identifiers, codes (e.g. SKU, model codes, thinks like Y-M8GB, 140-213/A and ABD9881); it’s clear, at least it seems so, they already know what they want and what they are looking for. However, you noticed a lot of such queries produce no results. After investigating, the problem seems to be that codes and identifiers are hard to remember: queries use a lot of disparate forms for pointing to the same product. For example:

* + y-m8gb (lowercase)
  + YM8GB (no delimiters)
  + YM-8GB (delimiter in the wrong place)
  + Y/M8GB (wrong delimiter)
  + Y M8GB (whitespace instead of delimiter)
  + y M8/gb (a combination of cases above)

This kind of scenario, where there’s only one relevant document in the collection, is usually referred to as “Known Item Search”: our first requirement is to make sure this *“product identifier intent”* is satisfied.

The other group of customers are end-users, like me and you. Being not so familiar with product specs like codes or model codes, the behaviour here is different: they use a plain keyword search, trying to match products by entering terms which represent names, brands, and manufacturers. Here comes the second requirement which can be summarized as follows: people must be able to find products by entering plain free-text queries.

As you can imagine, in this case, search requirements are different from the other scenario: the focus here is more “term-centric”, therefore involving different considerations about the text analysis we’d need to apply.

While the expert group query is supposed to point to one and only one product (we are in a black/white scenario: match or not), the needs on the other side require the system to provide a list of “relevant” documents, according to the terms entered.

*An important thing/assumption before proceeding: for illustration purposes, we will consider those two queries/user groups as disjoint: that is, a given user belongs only to one of the mentioned groups, not both. Better, a given user query will contain product identifiers* ***or*** *terms, not both.*

## Schema & configuration notes

##### The expert group, and the “Known Item Search”

The “product identifier” intent, which is assumed to be implicit in the query behaviour of this group, can be captured, both at index and query time, by applying the following analyzer, which treats the incoming value as a whole, normalizes it to lower case, removes all delimiters and finally collapses everything in a single output token.

```
				
					&lt;fieldtype name="identifier" class="solr.TextField" omitNorms="true"&gt;
    &lt;analyzer&gt;
        &lt;tokenizer class="solr.KeywordTokenizerFactory" /&gt;
        &lt;filter class="solr.LowerCaseFilterFactory" /&gt;
        &lt;filter class="solr.WordDelimiterGraphFilterFactory"
                generateWordParts="0"
                generateNumberParts="0"
                catenateWords="0"
                catenateNumbers="0"
                catenateAll="1"
                splitOnCaseChange="0" /&gt;
    &lt;/analyzer&gt;
&lt;/fieldtype&gt;
&lt;field name="product_id" type="identifier" indexed="true" ... /&gt;
				
			
```

In the following table you can see the analyzer in action with some example:

![](https://i0.wp.com/sease.io/wp-content/uploads/2018/04/AAMAAQDGAAgAAQAAAAAAABAkAAAAJDc3OTQ3M2FkLTg1MDQtNDBmYy1iNjRiLWQ0NWE2OGNjMzZhOQ.png?resize=268%2C300&ssl=1)

As you can see, the analyzer doesn’t declare a *type* attribute because it is supposed to be applied both at index and query time. However, there’s a difference in the incoming value: at index time the analyzer is dealing with a field content (i.e. the value of a field of an incoming document), while at query time the value which flows through the pipeline is composed by one or more terms entered by the user (a query, briefly).

While at index time everything works as expected, at query time the analyzer above requires a feature that has been introduced in Solr 6.5: the “**Split On Whitespace**” flag [[1]](https://lucidworks.com/2017/04/18/multi-word-synonyms-solr-adds-query-time-support). When it is set to “false” (as we need here in this context), it causes the incoming query text to be kept as a single whole unit, when sent to the analyzer.

Prior to Solr 6.5 we didn’t have such control, and the analyzers were receiving “pre-tokenized-by-whitespaces” tokens; in other words, the unit of work of the query-time analysis was the single term: the analyzer chain (including the tokenizer itself) was invoked for each term outputted by that pre-whitespace-tokenization. As a consequence of that our analyzer, at query time, couldn’t work as expected: if we take the example #5 and #6 from the table above, you can see the user entered a whitespace. With the “Split on Whitespace” flag set to true (explicitly, or using a Solr < 6.5), the pre-tokenization described above produces two tokens:

* + #5 = {“Y”, ”M8GB”}
  + #6 = {“y”, “M8/gb”}

so our analyzer would receive 2 tokens (for each case) and there wouldn’t be any match with the single term **ym8gb** stored in the index. So, before Solr 6.5 we had two ways of dealing with this requirement:

* + **client side**: wrapping the whole query with double quotes, escaping whitespaces with “\”, or replacing them with a delimiter like “-“. Easy, but it requires control of the client code, and this is not always possible.
  + **Solr side**: applying to the incoming query the same transformations as above but this time at the query parser level. Easy, if you know some Lucene / Solr internals. In addition, it requires a context where you have permission to install custom plugins in Solr. A similar effect could be obtained also using an UpdateRequestProcessor which would create a new field with the same value as the original field but without any whitespace.

##### The end-users group, and the full-text search query

In this case, we are within a “plain” full-text search context, where the analysis identified a couple of target fields: product names and brands.

Differently from the previous scenario, here we don’t have a unique and deterministic way to satisfy the search requirement. It depends on a lot of factors: the catalogue, the terms distribution, the implementor experience, and the customer expectations in terms of user search experience. All these things can lead to different answers. Just for example, here’s a possible option:

```
				
					&lt;fieldType name="brand" class="solr.TextField" omitNorms="true"&gt;
    &lt;analyzer&gt;
        &lt;charFilter 
                class="solr.MappingCharFilterFactory" 
                mapping="mapping-FoldToASCII.txt"/&gt;
        &lt;tokenizer class="solr.StandardTokenizerFactory"/&gt;
        &lt;filter class="solr.LowerCaseFilterFactory"/&gt;
        &lt;filter class="solr.StopFilterFactory" 
                ignoreCase="true" 
                words="lang/en/brand_stopwords.txt"/&gt;
    &lt;/analyzer&gt;
&lt;/fieldType&gt;

&lt;fieldType name="name" class="solr.TextField"&gt;
    &lt;analyzer&gt;
        &lt;charFilter 
                  class="solr.MappingCharFilterFactory" 
                  mapping="mapping-FoldToASCII.txt"/&gt;
        &lt;tokenizer class="solr.StandardTokenizerFactory"/&gt;
        &lt;filter class="solr.LowerCaseFilterFactory"/&gt;
        &lt;filter 
                class="solr.StopFilterFactory" 
                ignoreCase="false" 
                words="lang/en/product_name_stopwords.txt"/&gt;
        &lt;filter class="solr.EnglishPossessiveFilterFactory"/&gt;
        &lt;filter class="solr.EnglishMinimalStemFilterFactory"/&gt;
        &lt;filter class="solr.RemoveDuplicatesTokenFilterFactory"/&gt;
        &lt;filter class="solr.LengthFilterFactory" min="2" max="50" /&gt;
    &lt;/analyzer&gt;
&lt;/fieldType&gt;
				
			
```

The focus here is not on the schema design itself: the important thing to underline is that this requirement needs a completely different configuration from the “Known Item Search” previously described.

Specifically, let’s assume we ended up following a “term-centric” approach to satisfy the second requirement. The approach requires a different value for the “Split on Whitespace” parameter, which has to be set to true, in this case.

The “**sow**” parameter can be set at *SearchHandler* level, so it is applied at query time. It can be declared within the *solrconfig.xml* and, depending on the configuration, it can be overridden using a named (HTTP) query parameter.

A “split on whitespace” pre-tokenisation leads us to a scenario which is different from the “Known Item Search”, where instead we “should” be in a field-centric search; “should” is double-quoted because if, from one side, we are using a field-centric search, on the other side we are on an edge case where we’re querying one single field with one single query term (the first analyzer in this post **always** outputs one term).

## The implementation

##### Where?

Although one could think the first thing is how to combine those two different query strategies, before that, the question we need to answer is **where to implement the solution**. Regardless the way we will decide to follow, we will have to implement a (search) workflow, which can be summarised in the following diagram:

![Known Item Search in Apache Solr](https://i0.wp.com/sease.io/wp-content/uploads/2018/04/AAMAAQDGAAgAAQAAAAAAAA9MAAAAJGQxYTUzMjBkLWIyNmMtNDBiZi1iYmI3LTkxZDljMTNhNThmNA.png?resize=473%2C142&ssl=1)

On the Solr side, each “search” task needs to be executed in a different *SearchHandler*, so returning to our question: where do we want to implement such workflow? We have three options: outside, between or inside Solr.

##### #1: Client-side implementation

The first option is to implement the flow depicted above in the client application. That assumes you have the required control and programming skills on that side. If this assumption is true, then it’s relatively easy to code the workflow: you can choose one of the client API binding available for your language and then implement the double + conditional search illustrated above.

* + **Pros**: easy to implement. It requires a minimal Solr (functional) knowledge.
  + **Cons**: the search workflow/logic is moved on the client side. Programming is required, so you must be in a context where this can be done and where the client application code is under your control.

##### #2: Man-in-the-middle

Moving things outside the client sphere, another popular option, which can be still seen as a client-side alternative (from the Solr perspective), is a proxy/adapter/facade. Whatever the name you want to give to this stuff, this is a new module which sits between the client application and Solr; it intercepts all requests and it would implement the custom logic by orchestrating the search endpoints exposed in Solr.

Being a new module, it has several advantages:

* + it can be coded using your preferred language
  + it is completely decoupled from the client application, and from Solr as well

but for the same reason, it has also some disadvantages:

* + it must be created: designed, implemented, tested, installed and maintained
  + it is a new piece in your system, which necessarily increases the overall complexity of the architecture
  + Solr exposes a lot of (index & search) services. With this option, all those services should be proxied, therefore resulting in a lot of unnecessary delegations (i.e. delegate services that don’t add any value to the execution chain).

##### #3: In Solr

The last option moves the workflow implementation (and the search logic) to the place where, in my opinion, it should be: in Solr.

Note that this option is usually not only a “philosophical” choice: if you are a search engineer, most probably you will be hired to design, implement and tune the “search side of the cake”. That means it’s perfectly possible that, for a lot of reasons, you must think of the client application as an external (sub)system, where you don’t have any kind of control.

The main drawback of this approach is that, as you can imagine, it requires programming skills plus knowledge about the Solr internals.

In Solr, a search request is consumed by a *SearchHandler*, a component which is in charge of executing the logic associated with a given search endpoint. In our example, we would have the following search handlers matching the two requirements:

```
				
					&lt;!-- Known Item search --&gt;
&lt;requestHandler name="/known_item_search" class="solr.SearchHandler"&gt;
   &lt;lst name="invariants"&gt;
        &lt;str name="defType"&gt;lucene&lt;/str&gt;
        &lt;bool name="sow"&gt;false&lt;/bool&gt; &lt;!-- No whitespace split --&gt;
        &lt;str name="df"&gt;product_id&lt;/str&gt;
   &lt;/lst&gt;
&lt;/requestHandler&gt;

&lt;!-- Full-text search --&gt;
&lt;requestHandler name="/full-text-search" class="solr.SearchHandler"&gt;
    &lt;lst name="invariants"&gt;
         &lt;bool name="sow"&gt;true&lt;/bool&gt; &lt;!--Whitespace split --&gt;
         &lt;str name="defType"&gt;edismax&lt;/str&gt;
         &lt;str name="df"&gt;product_name&lt;/str&gt;
         &lt;str name="qf"&gt;
            product^0.7
            brand^1.5
				
			
```

On top of that, we would need a third component, which would be in charge of orchestrating the two search handlers above. I’ll call this component a *“Composite Request Handler”.*

The composite handler would also provide the public search endpoint called by clients. Once a request is received, the composite request handler implements the search workflow: it invokes all the handlers that compose its chain, and it will stop when one of the invocation targets produces the expected result.

The composite handler configuration looks like this:

```
				
					&lt;requestHandler name="/search" class="....."&gt;
    &lt;str name="chain"&gt;/know_item_search,/full_text_search&lt;/str&gt;
&lt;/requestHandler&gt;
				
			
```

On the client side, that would require only one request because the entire workflow will be implemented in Solr, using the composite request handler. In other words, imagining a GUI with a search bar, the client application, when the search button is pressed, would have to retrieve the term(s) entered by the user and send just one request (to the composite handler endpoint), regardless the intent of the user (i.e. regardless the group the user belongs to).

The composite request handler introduced in this section has been already implemented, you can find it in our Github account, here [[2]](https://github.com/SeaseLtd/invisible-queries-request-handler).

Enjoy and, as usual, any feedback is warmly welcome!

## Need Help With This Topic?​​

If you’re struggling with known item search, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with known item search, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)