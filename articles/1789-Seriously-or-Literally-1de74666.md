---
title: 'Seriously or Literally?'
company: Tunkelang
tag: 查询理解
date: 2024-09-18
url: https://dtunkelang.medium.com/seriously-or-literally-da5c1bb90318
account: Tunkelang
origin: harvest3-202607
---
# Seriously or Literally?

The other day, I posted about the need for search applications to [take searchers seriously, not literally](https://queryunderstanding.com/take-searchers-seriously-not-literally-146df479cb0d). This need holds even when searchers practically ask to be taken literally.

### Quotation Marks

By using quotation marks, a searcher — already signaling a relatively advanced knowledge of search engines — explicitly asks the application to only retrieve results with those exact words in that order. This seems an incontrovertible case for taking the searcher literally. Or is it?

What if the quoted phrase is [misspelled](https://queryunderstanding.com/spelling-correction-471f71b19880)? Should a search for the quoted phrase “luois viutton” include results for Louis Vuitton? What about [stemming and lemmatization](https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45)? Should a search for “dress shirt” retrieve different results than a search for “dress shirts” or rank them differently depending on whether the noun is singular or plural? After all, the quoting may be more to ensure that the application does not retrieve [shirt dresses](https://en.wikipedia.org/wiki/Shirtdress).

Situations like these call for nuance. On one hand, a search application should enable searchers to retrieve results containing a seemingly misspelled word (e.g., “[solr](https://en.wikipedia.org/wiki/Apache_Solr)”) or a word with a particular ending. On the other hand, a [Bayesian](https://en.wikipedia.org/wiki/Bayesian_statistics) perspective argues for considering the prior. In particular, the searcher may have used quotation marks to specify the word order or to avoid the word being optionalized through [query relaxation](https://queryunderstanding.com/query-relaxation-342bc37ad425) without realizing that doing so might override [spelling correction](https://queryunderstanding.com/spelling-correction-471f71b19880).

A compromise is for the search application to show results for one query interpretation and offer a “did you mean” [clarification dialogue](https://queryunderstanding.com/clarification-dialogues-69420432f451) for the other interpretation. Which interpretation should be primary? Ideally, that decision should be a Bayesian probability calculation. However, given the challenge of calculating this probability, it might be better to provide a consistent experience and always treat the literal interpretation as the primary one. Or to experiment and learn from searcher behavior.

### Known-Item Search

While most search queries today are short and generic (e.g., “mens shoes”), some queries are much longer — particularly when the searcher is trying to find a document or product by name.

For example, a comparison shopper might copy and paste a product name from one site into another’s search box, leading to queries like “Gaggia Brera Super-Automatic Espresso Machine, Small, 40 fluid ounces, Silver” (the unofficial sponsor of my waking hours) or “Faceted Search (Synthesis Lectures on Information Concepts, Retrieval, and Services, 5)”. Or one of my fans might search on LinkedIn for “Dan Tunkelang”.

On one hand, recognizing these queries as instances of [known-item search](https://en.wikipedia.org/wiki/Known-item_search) suggests a conservative retrieval approach that emphasizes [precision](https://queryunderstanding.com/precision-recall-and-desirability-0384a11d916b) and takes the query literally. On the other hand, it is clear from these examples that a product, document, or person can have many name or title variants.

Ironically, [query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8) and [relaxation](https://queryunderstanding.com/query-relaxation-342bc37ad425), despite their primary association with increasing [recall](https://queryunderstanding.com/precision-recall-and-desirability-0384a11d916b), can be critical for matching the [specific](https://queryunderstanding.com/query-specificity-a6156f4043eb) intent of known-item search queries to the results they target. For example, if someone searches for “Dan Tunkelang”, the application should return my profile page rather than a result that happens to include the words “Dan” and “Tunkelang” in its body text. Likewise, copy-and-paste product searches for my espresso maker or faceted search book should retrieve the intended result on any site that carries them, regardless of the title variant.

### Seriously, Don’t Take Searchers Literally!

I hope these examples reinforce the need to take searchers seriously rather than literally. And we have not even touched on messier issues like handling numbers. Searchers may know exactly what they want, but they cannot ensure that their queries exactly match the content representation in the search index. So, regardless of the temptation to take searchers literally, serious search applications require [query understanding](https://queryunderstanding.com/introduction-c98740502103).
