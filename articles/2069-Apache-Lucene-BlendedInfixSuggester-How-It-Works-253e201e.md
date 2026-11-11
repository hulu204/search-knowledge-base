---
title: 'Apache Lucene BlendedInfixSuggester : How It Works, Bugs And Improvements'
company: Sease
tag: 查询理解
date: 2018-06-05
url: https://sease.io/2018/06/apache-lucene-blendedinfixsuggester-how-it-works-bugs-and-improvements.html
account: 
origin: harvest3-202607
---
The Apache Lucene/Solr suggesters are important to Sease: we explored the topic in the past [with this post about Solr autocomplete](https://sease.io/2015/07/solr-autocomplete-you-complete-me.html) and we strongly believe the autocomplete feature to be vital for a lot of search applications.  
This blog post explores in detail the current status of the Lucene BlendedInfixSuggester, some bugs of the most recent version (with the solution attached) and some possible improvements.

## BlendedInfixSuggester

The **BlendedInfixSuggester** is an extension of the **AnalyzingInfixSuggester** with the additional functionality to weight prefix matches of your query across the matched documents.  
It scores higher if a hit is closer to the start of the suggestion.  
**N.B.** At the current stage, only the first term in your query will affect the suggestion score.

Let’s see some of the configuration parameters from the official wiki:

* + **blenderType**: used to calculate the positional weight coefficient using the **position of the first matching word**. Can be one of the:  

    - **position\_linear**: weightFieldValue\*(1 – 0.10\*position): Matches to the start will be given a higher score (Default)
    - **position\_reciprocal**: weightFieldValue/(1+position): Matches to the start will be given a score which decays faster than linear
    - **position\_exponential\_reciprocal**: weightFieldValue/pow(1+position, exponent): Matches to the start will be given a score which decays faster than reciprocal
      * **exponent**: an optional configuration variable for the position\_reciprocal blenderType used to control how fast the score will increase or decrease. Default 2.0.

| Description |
| --- |
| **Data Structure** | Auxiliary Lucene Index |
| **Building** | For each Document, the **stored content** from the field is **analyzed** according to the *suggestAnalyzerFieldType* and then additionally*EdgeNgram*token filtered*.* Finally an auxiliary index is built with those tokens. |
| **Lookup strategy** | The query is analysed according to the *suggestAnalyzerFieldType*. Than a phrase search is triggered against the **Auxiliary Lucene index** The suggestions are identified starting at the **beginning of each token** in the field content. |
| **Suggestions returned** | The **entire content** of the field . |

This suggester is common nowadays as it allows us to provide suggestions in the middle of a field content, taking advantage of the analysis chain provided with the field. It will be possible in this way to provide suggestions considering **synonyms**, **stop words, stemming**and any other token filter used in the analysis and match the suggestion based on **internal tokens**. Finally, the suggestion is scored, based on the position match. The simple corpus of documents for the examples will be the following:

```
				
					[
      {
        "id":"44",
        "title":"Video gaming: the history"},
      {
        "id":"11",
        "title":"Nowadays Video games are a phenomenal economic business"},
      {
        "id":"55",
        "title":"The new generation of PC and Console Video games"},
      {
        "id":"33",
        "title":"Video games: multiplayer gaming"}]
				
			
```

And a simple **synonym** mapping: multiplayer, online

Let’s see some examples:

| Query to autocomplete | Suggestions | Explanation |
| --- | --- | --- |
| *“gaming”* | * “Video **gami**ng: the history” * “Video **game**: multiplayer gaming” * “Nowadays Video **game**s are a phenomenal economic business” … | The input query is analysed, and the tokens produced are the following : **“game” .** In the Auxiliary Index , for each of the field content we have the EdgeNgram tokens: “v”,”vi”,”vid”… , “g”,”ga”,”gam”,**“game”** . So the match happens and the suggestion are returned. **N.B.**First two suggestions are ranked higher as the matched term happen to be closer to the start of the suggestion |

Let’s explore the score of each Suggestion given various Blender Types:

|  |  |
| --- | --- |
| **Query** | *gaming* |
| Suggestion | First Position Match | Position Linear | Position Reciprocal | Position Exponential Reciprocal |
| Video **gami**ng: the history | *1* | 1-0.1\*position = **0.9** | *1/(1+position) = 1/2 = **0.5*** | *1/(1+position)^2 = 1/4 = **0.25*** |
| Video **game**: multiplayer gaming | *1* | 1-0.1\*position = **0.9** | *1/(1+position) = 1/2 = **0.5*** | *1/(1+position) = 1/4 = **0.25*** |
| Nowadays Video **game**s are a phenomenal economic business | *2* | 1-0.1\*position = **0.8** | *1/(1+position) = 1/3 = **0.3*** | *1/(1+position) = 1/9 = **0.1*** |

The final score of the suggestion will be:

```
				
					long score = (long) (weight * coefficient)
				
			
```

**N.B.** the reason I highlighted the data type is that it’s directly affecting the first bug we discussed.

## Suggestion Score Approximation

The optional **weightField** parameter is extremely important for the Blended Infix Suggester.  
It assigns the value of the suggestion weight (extracted from the mentioned field).  
**e.g.**The suggestion may come from the product name field, but the suggestion weight depends on how profitable the product suggested is.

**<str name=”field”>productName</str>**  
**<str name=”weightField”>profit</str>**

So far, so good, but unfortunately there are two problems with that.

##### Bug 1 - WeightField Not Defined -> Zero suggestion score

**How To Reproduce It**: Don’t define any weightField in the suggester config.  
**Effect**: the suggestion ranking is lost, all the suggestions have a 0 score, position of the match doesn’t matter anymore.  
The weightField is not a mandatory configuration for the BlendedInfixSuggester.  
Your use case could not involve any weight for your suggestions and you are just interested in the positional scoring (the main reason the BlendedInfixSuggester exists in the first place).  
Unfortunately, this is not possible at the moment:  
If the weightField is not defined, each suggestion will have a **weight of 0**.  
This is because the weight associated with each document in the document dictionary is long. If the field to extract the weight from, is not defined (null), the weight returned will just be 0.  
This doesn’t allow us to differentiate when a weight should be 0 (value extracted from the field) or null (no value at all).  
A solution has been proposed here [[3]](https://issues.apache.org/jira/browse/LUCENE-8343).

##### Bug 2 - Bad Approximation Of Suggestion Score For Small Weights

There is a misleading data type casting in the score calculation for the suggestion:

```
				
					long score = (long) (weight * coefficient)
				
			
```

This apparently innocent cast, actually brings very nasty effects if the weight associated with a suggestion is unitary or small enough.

**Weight** =1  
Video **gami**ng: the history  
1-0.1\*position = **0.9 \* 1 =cast= 0***1/(1+position) = 1/2 = **0.5 \* 1 =cast= 0****1/(1+position)^2 = 1/4 = **0.25 \* 1 =cast= 0***

**Weight** =2  
Video **gami**ng: the history  
1-0.1\*position = **0.9 \* 2=cast= 1***1/(1+position) = 1/2 = **0.5 \* 2=cast= 1****1/(1+position)^2 = 1/4 = **0.25 \* 2=cast= 0***

Basically, you risk losing the ranking of your suggestions reducing the score to only a few possible values: 0 or 1 (in edge cases).

A solution has been proposed here [[3].](https://issues.apache.org/jira/browse/LUCENE-8343)

## Multi Term Matches Handling

It is quite common to have multiple terms in the autocomplete query, so your suggester should be able to manage multiple matches in the suggestion accordingly.

Given a simple corpus (composed just by the following suggestions) and the query :  
**“Mini Bar Frid”**

You see these suggestions:

* + **1000 | Mini Bar** something **Frid**ge
  + **1000 | Mini Bar** something else **Frid**ge
  + **1000 | Mini Bar Fridge** something
  + **1000 | Mini Bar Fridge** something else
  + **1000 | Mini** something **Bar Frid**ge

This is because, at the moment, **the first matching term wins all** (and the other positions are ignored).  
This brings a lot of possible ties (1000), that should be broken to give the user a nice and intuitive ranking.

But intuitively I would expect in the results something like (note that allTermsRequired=true and the schema weight field always returns 1000).

* + **Mini Bar Frid**ge something
  + **Mini Bar Frid**ge something else
  + **Mini Bar** something **Frid**ge
  + **Mini Bar** something else **Frid**ge
  + **Mini** something **Bar Frid**ge

Let’s see a proposed Solution [[4]](https://issues.apache.org/jira/browse/LUCENE-8347):

##### Positional Coefficient

Instead of taking into account just the first term position in the suggestion, it’s possible to use all the matching positions from the matched terms [“mini”, “bar”, “fridge”].  
Each position match will affect the score with:

* + How much the matched term position is distant from the ideal position match
    - **Query**: Mini Bar Fri, **Ideal Positions** : [0,1,**2**]
    - **Suggestion 1**: **Mini Bar** something **Fri**dge, **Matched Positions:**[0,1,**3**]
    - **Suggestion 2**: **Mini Bar** something else **Fri**dge, **Matched Positions:**[0,1,**4**]
    - Suggestion 2 will be penalised as “Fri” match happens further (4 > 3) from the ideal position **2**
  + Earlier the mis-position happened, stronger the penalty for the score to pay
    - **Query**: Mini Bar Fri, **Ideal Positions** : [0,1,2]
    - **Suggestion 1**: **Mini Bar** something **Fri**dge, **Matched Positions:**[0,1,**3**]
    - **Suggestion 2**: **Mini** something **Bar** **Fri**dge, **Matched Positions:**[0,**2**,**3**]
    - Suggestion 2 will be additionally penalised as the first mismatch in positions **Bar** happens closer to the beginning of the suggestion .

Considering only the **discontinue position** proved useful:

**Query1**: Bar some  
**Query2**: some  
**Suggestion**: Mini Bar something Fridge  
**Query 1 Suggestion Matched Terms positions** : [1,2]  
**Query 2 Suggestion Matched Terms positions** : [2]

If we compare the suggestion score for both these queries, it would seem unfair to penalise the first one just because it matches 2 terms (consecutive) while the second query has just one match (positioned worse than the first match in query1)

Introducing this advanced positional coefficient calculus helped in improving the overall behaviour of the experimental test created.  
The results obtained were quite promising :

**Query**: Mini Bar Fri  
100 |**Mini Bar Fri**dge something  
100 |**Mini Bar Fri**dge something else  
100 |**Mini Bar Fri**dge a a a a a a a a a a a a a a a a a a a a a a  
26 |**Mini Bar** something **Fri**dge  
22 |**Mini Bar** something else **Fri**dge  
17 |**Mini** something **Bar Fri**dge  
8 |something **Mini Bar Fridge**  
7 |something else **Mini Bar Fridge**

There is still a tie for the exact prefix matches, but let’s see if we can also finalise that improvement.

##### Token Count Coefficient

Let’s focus on the first three ranking suggestions we just saw:

**Query**: Mini Bar Fri  
**100** |**Mini Bar Fri**dge something  
**100** |**Mini Bar Fri**dge something else  
**100** |**Mini Bar Fri**dge a a a a a a a a a a a a a a a a a a a a a a

Intuitively we want this order to break the ties.  
The closer the number of matched terms with the total number of terms for the suggestion, the better.  
Ideally, we want our top-scoring suggestion to just have the matched terms if possible.  
We also don’t want to bring strong inconsistencies for the other suggestions, we should ideally only affect the ties.  
This is achievable by calculating an additional coefficient, dependent on the term counts:  
**Token Count Coefficient** = matched terms count / total terms count.

Then we can scale this value accordingly:  
90% of the final score will derive from the positional coefficient  
10% of the final score will derive from the token count coefficient

**Query**: Mini Bar Fri  
90 \* 1.0 + 10\*3/4 = **97**|**Mini Bar Fri**dge something  
90 \* 1.0 + 10\*3/5 = **96**|**Mini Bar Fri**dge something else  
90 \* 1.0 + 10\*3/25 = **91**|**Mini Bar Fri**dge a a a a a a a a a a a a a a a a a a a a a a

It will require some additional tuning but the overall idea should bring a better ranking function to the BlendedInfix when multiple-term matches are involved!  
If you have any **suggestions,** feel free to leave a comment below!  
Code is available in the Github Pull Request attached to the Lucene Jira issue [[4]](https://issues.apache.org/jira/browse/LUCENE-8347).

## Need Help With This Topic?​​

If you’re struggling with BlendedInfixSuggester, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with BlendedInfixSuggester, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)