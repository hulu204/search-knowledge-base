---
title: 'Give the height the right weight: Solr quantity detection plugin'
company: Sease
tag: 查询理解
date: 2018-04-13
url: https://sease.io/2018/04/solr-quantity-detection-plugin.html
account: 
origin: harvest3-202607
---
## What is a quantity? And why do we need to detect it?

A quantity, as described by Martin Fowler in his “Analysis Patterns” [[1]](https://martinfowler.com/books/ap.html) is defined as a pair which combines an amount and unit (such as 30 litres, 0.25 cl, or 140 cm). In search-based applications, there are many cases where you may want to classify your searchable dataset using dimensioned attributes because such quantities have a special meaning within the business context you are working on. The first example that comes to my mind?

![Apache Solr Quantity Detection Plugin](https://i0.wp.com/sease.io/wp-content/uploads/2018/04/AAMABADGAAgAAQAAAAAAAAxQAAAAJDBkZDc4YWJkLTMwNzQtNDExNy04MTBjLWM5MzhhOWI2MDliYg.jpg?resize=585%2C185&ssl=1)

Beer is offered in several containers (e.g. cans, bottles); each of them is available in multiple sizes (e.g. 25 cl, 50 cl, 75 cl or 0.25 lt, 0.50 lt, 0.75 lt). A good catalogue would capture this information in dedicated fields, like “container” (bottle, can) and “capacity” (25cl, 50cl, 75cl in the example above): in this way, the search logic can properly make use of them. Faceting (and subsequent filtering) is a good example of what the user can do *after* a first search has been executed: he can filter and refine results, hopefully finding what he was looking for.

But if we start from the beginning of user interaction, there’s no result at all: only the blank textfield where the user is going to type something. “Something” could be whatever, anything (in his mind) related to the product he wants to find: a brand, a container type, a model name, a quantity. In a few words: anything which represents one or more relevant features of the product he’s looking for.

So one of the main challenges, when implementing a search logic, is to get the point about the meaning of the entered terms. This is in general a very hard topic, often involving complicated stuff (e.g. machine learning), but sometimes things move on the easier side, especially when concepts, we want to detect, follow a common and regular pattern: like a quantity.

The main idea behind the quantity detection plugin [[2]](https://github.com/SeaseLtd/solr-quantities-detection-qparsers) we developed at Sease is the following: starting from the user-entered query, first, it detects the quantities (i.e. the amounts and the corresponding units); then, this information will be isolated from the main query and they will be used for boosting up all products relevant to those quantities. Relevancy here can be meant in different ways:

* + **exact match**: all bottles with a capacity of 25cl
  + **range match**: all bottles with a capacity between 50cl and 75cl.
  + **equivalence exact match**: all bottles with a capacity of 0.5 litre (1lt = 100cl)
  + **equivalence range match**: all bottles with a capacity between 0.5 and 1 litre (1lt = 100cl)

The following is a short list with a brief description of all supported features:

* + **variants**: a unit can have a preferred form and (optionally) several variants. This can include different forms of the same unit (e.g. mt, meter) or an equivalent unit in a different metric system (e.g. cl, once)
  + **equivalences**: it’s possible to define an equivalence table so units can be converted at runtime (“beer 0.25 lt” will have the same meaning of “beer 25cl”). An equivalence table maps a unit with a conversion factor.
  + **boost**: each unit can have a dedicated boost, especially useful for weighting multiple matching units.
  + **ranges**: each unit can have a configured gap, which triggers a range query where the detected amount can be in the middle (PIVOT), at the beginning (MIN) or at the end (MAX) of the generated range
  + **multi-fields**: in case we have more than one attribute using the same unit (e.g. height, width, depth)
  + **assumptions**: in case an “orphan” amount (i.e an amount without a unit) is detected, it’s possible to define an assumption table and let Solr guess the unit.

Feel free to have a try, and if you think it could be useful, please share with us your idea and/or your feedback.

## Need Help With This Topic?​​

If you’re struggling with quantities detection in Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with quantities detection in Apache Solr, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)