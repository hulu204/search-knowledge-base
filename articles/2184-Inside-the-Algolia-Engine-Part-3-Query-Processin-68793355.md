---
title: 'Inside the Algolia Engine Part 3 — Query Processing'
company: Algolia
tag: 查询理解
date: 2016-05-24
url: https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-3-query-processing
account: 
origin: harvest3-202607
---
- [* English](#)
  [* Deutsch](/de/search/ "Switch to ")
  [* français](/fr/search/ "Switch to ")
- [* English](#)
  [* German](# "Switch to ")
  [* French](# "Switch to ")
  [* Brazilian Portuguese](# "Switch to ")
  [* Spanish](# "Switch to ")
  [* Italian](# "Switch to ")

[Join us: 
Algolia DevCon 2026: Sep 30 - Oct 1, 2026 — VIRTUAL

Register Now](https://www.algolia.com/devcon?utm_cta=topbannerpromo)

[NEW: 
Algolia CEO on BBC: The Future of AI Search for Retail

Read more](https://www.algolia.com/resources/asset/video-bbc-interview?utm_cta=topbannerpromo)

* [Company](/about)
* [Partners](/partprog)
* [Support](https://support.algolia.com/)
* [![](/files/live/sites/algolia-assets/files/icons/person_blue.svg)
  Login](https://dashboard.algolia.com/users/sign_in)
* [![](/files/live/sites/algolia-assets/files/icons/Check%20Square.svg)
  Logout](https://dashboard.algolia.com/users/sign_out)

[Algolia mark white

Algolia logo white](https://www.algolia.com/)

CLOSE

* Products

  [![navigation image](/files/live/sites/www/files/ad-banners/Screenshot%202026-05-29%20at%201.29.21%e2%80%afPM.png)](https://www.algolia.com/resources/asset/infographic-value-of-choosing-algolia?utm_cta=navigationpromo)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/search.svg)

  ##### AI Search & Retrieval

  + [Overview](/products)
  + [Search

    Show users what they're looking for with AI-driven results.](/products/ai-search)

    [Search](/products/ai-search)

    Show users what they're looking for with AI-driven results.
  + [Recommendations

    Use behavioral cues to drive higher engagement.](/products/ai-recommendations)

    [Recommendations](/products/ai-recommendations)

    Use behavioral cues to drive higher engagement.
  + [Personalization

    Show each user what they need across their journey.](/products/features/personalization)

    [Personalization](/products/features/personalization)

    Show each user what they need across their journey.
  + [Analytics

    All your insights in one dashboard.](/products/features/analytics)

    [Analytics](/products/features/analytics)

    All your insights in one dashboard.
  + [Browse

    Move customers down the funnel with curated category pages.](/products/ai-browse)

    [Browse](/products/ai-browse)

    Move customers down the funnel with curated category pages.

  ![](/files/live/sites/algolia-assets/files/icons/navigation/ai.svg)

  ##### Artificial Intelligence

  + [OVERVIEW](https://www.algolia.com/products?utm_cta=aioverview)
  + [Agent Studio

    Create, test, and deploy AI agents, fast.](/products/ai/agent-studio)

    [Agent Studio](/products/ai/agent-studio)

    Create, test, and deploy AI agents, fast.
  + [Generative Experiences

    Build conversational solutions with retrieval augmented generation (RAG).](/products/ai/generative-experiences)

    [Generative Experiences](/products/ai/generative-experiences)

    Build conversational solutions with retrieval augmented generation (RAG).
  + [Ask AI

    Deliver conversational answers—right from your search bar.](/products/ai/ask-ai)

    [Ask AI](/products/ai/ask-ai)

    Deliver conversational answers—right from your search bar.
  + [MCP Server

    Search, analyze, or monitor your index within your agentic workflow.](/developers/lp-mcp)

    [MCP Server](/developers/lp-mcp)

    Search, analyze, or monitor your index within your agentic workflow.

  ![](/files/live/sites/algolia-assets/files/icons/navigation/intelligence.svg)

  ##### Intelligent Data Kit

  + [Overview](/products/intelligent-data-kit)
  + [Data Enrichment

    Modify, enhance, or restructure data as it’s indexed for search.](/products/features/data-enrichment)

    [Data Enrichment](/products/features/data-enrichment)

    Modify, enhance, or restructure data as it’s indexed for search.
  + [Data Transformation

    Streamline data preparation and enhance data quality.](/products/features/data-transformation)

    [Data Transformation](/products/features/data-transformation)

    Streamline data preparation and enhance data quality.
  + [Integrations

    Connect to your existing stack via pre-built libraries and APIs.](/developers/integrations)

    [Integrations](/developers/integrations)

    Connect to your existing stack via pre-built libraries and APIs.

  ![](/files/live/sites/algolia-assets/files/icons/navigation/infra.svg)

  ##### Infrastructure

  + [Overview](/distributed-secure/global-infrastructure)
  + [Data Centers

    Choose from 70+ data centers across 17 regions.](/distributed-secure/global-infrastructure)

    [Data Centers](/distributed-secure/global-infrastructure)

    Choose from 70+ data centers across 17 regions.
  + [Security & Compliance

    Built for peace of mind.](https://trust.algolia.com/)

    [Security & Compliance](https://trust.algolia.com/)

    Built for peace of mind.
* Solutions

  [![navigation image](/files/live/sites/www/files/homepage-carousel/cropped-foreground-gartner-magic-quadrant.png)](https://www.algolia.com/lp/gartner-magic-quadrant-2026?utm_cta=navigationpromo)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/industry_icon.svg)

  ##### Industries

  + [SEE ALL](/industries)
  + [Auto Parts](/industries/auto-parts)

    [Auto Parts](/industries/auto-parts)
  + [B2B Commerce](/industries/b2b-ecommerce)

    [B2B Commerce](/industries/b2b-ecommerce)
  + [Ecommerce](/industries/ecommerce)

    [Ecommerce](/industries/ecommerce)
  + [Fashion](/industries/fashion)

    [Fashion](/industries/fashion)
  + [Grocery](/industries/grocery)

    [Grocery](/industries/grocery)
  + [Higher Education](/industries/higher-education)

    [Higher Education](/industries/higher-education)
  + [Media](/industries/media)

    [Media](/industries/media)
  + [Marketplaces](/industries/marketplaces)

    [Marketplaces](/industries/marketplaces)
  + [SaaS](/industries/saas)

    [SaaS](/industries/saas)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/usecase_icon.svg)

  ##### Use Cases

  + [SEE ALL](/use-cases)
  + [Documentation search](/use-cases/documentation-search)

    [Documentation search](/use-cases/documentation-search)
  + [Enterprise search](/use-cases/enterprise)

    [Enterprise search](/use-cases/enterprise)
  + [Headless commerce](/use-cases/headless-commerce)

    [Headless commerce](/use-cases/headless-commerce)
  + [Image search](/use-cases/image-search)

    [Image search](/use-cases/image-search)
  + [Merchandising Studio](/industries/ecommerce/digital-merchandising)

    [Merchandising Studio](/industries/ecommerce/digital-merchandising)
  + [Retail Media Network](/use-cases/retail-media-network)

    [Retail Media Network](/use-cases/retail-media-network)
  + [Site search](/use-cases/site-search)

    [Site search](/use-cases/site-search)
  + [Visual search](/use-cases/visual-search)

    [Visual search](/use-cases/visual-search)
  + [Voice search](/use-cases/voice-search)

    [Voice search](/use-cases/voice-search)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/team_icon.svg)

  ##### Departments

  + [Digital Experience](/department/digital-experience)

    [Digital Experience](/department/digital-experience)
  + [Ecommerce](/department/ecommerce)

    [Ecommerce](/department/ecommerce)
  + [Engineering](/department/engineering)

    [Engineering](/department/engineering)
  + [Merchandising](/department/merchandisers)

    [Merchandising](/department/merchandisers)
  + [Product Management](/department/product-management)

    [Product Management](/department/product-management)
* [Pricing](/pricing)
* Developers

  [![navigation image](/files/live/sites/www/files/Screenshot%202026-06-25%20at%2010.37.59%e2%80%afAM.png)](https://www.algolia.com/devcon?utm_cta=topbannerpromo)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/get-started_icon.svg)

  ##### Get started

  + [Developer Hub](/developers)

    [Developer Hub](/developers)
  + [Documentation](https://www.algolia.com/doc/)

    [Documentation](https://www.algolia.com/doc/)
  + [Integrations](/developers/integrations)

    [Integrations](/developers/integrations)
  + [UI Components](/developers/search-ui)

    [UI Components](/developers/search-ui)
  + [Autocomplete](/products/features/search-autocomplete)

    [Autocomplete](/products/features/search-autocomplete)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/resources_iconv2.svg)

  ##### Resources

  + [Code Exchange](/developers/code-exchange)

    [Code Exchange](/developers/code-exchange)
  + [Engineering Blog](/blog/engineering)

    [Engineering Blog](/blog/engineering)
  + [MCP](/developers/lp-mcp)

    [MCP](/developers/lp-mcp)
  + [Discord](https://alg.li/discord)

    [Discord](https://alg.li/discord)
  + [Webinars & Events](/events)

    [Webinars & Events](/events)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/links_icon.svg)

  ##### Quick Links

  + [Quick Start Guide](https://www.algolia.com/doc/guides/getting-started/quick-start/)

    [Quick Start Guide](https://www.algolia.com/doc/guides/getting-started/quick-start/)
  + [For Open Source](/for-open-source)

    [For Open Source](/for-open-source)
  + [API Status](https://status.algolia.com/)

    [API Status](https://status.algolia.com/)
  + [Support](https://support.algolia.com/hc/en-us)

    [Support](https://support.algolia.com/hc/en-us)
* Resources

  [![navigation image](/files/live/sites/www/files/ad-banners/llm-leaderboard-nav-banner.avif)](https://www.algolia.com/llm-leaderboard/?utm_cta=navigationpromo)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/discover_icon.svg)

  ##### Discover

  + [Algolia Blog](/blog)

    [Algolia Blog](/blog)
  + [Resource Center](/resources)

    [Resource Center](/resources)
  + [Customer Stories](/customers)

    [Customer Stories](/customers)
  + [Webinars & Events](/events)

    [Webinars & Events](/events)
  + [Newsroom](/about/news)

    [Newsroom](/about/news)
  + [AI Search Newsletter](/lp/subscription-newsletter)

    [AI Search Newsletter](/lp/subscription-newsletter)
  + [Product Demo Videos](https://www.algolia.com/resources?contentType=Product%20Demos)

    [Product Demo Videos](https://www.algolia.com/resources?contentType=Product%20Demos)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/resources_icon.svg)

  ##### Customers

  + [Customer Hub](/customer-hub)

    [Customer Hub](/customer-hub)
  + [What's New](https://changelog.algolia.com/)

    [What's New](https://changelog.algolia.com/)
  + [Knowledge Base](https://support.algolia.com/hc/en-us)

    [Knowledge Base](https://support.algolia.com/hc/en-us)
  + [Documentation](https://www.algolia.com/doc)

    [Documentation](https://www.algolia.com/doc)
  + [Algolia Academy](https://academy.algolia.com)

    [Algolia Academy](https://academy.algolia.com)
  + [Professional Services](/professional-services-support)

    [Professional Services](/professional-services-support)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/tools_icon.svg)

  ##### Tools

  + [Search Grader](https://www.algolia.com/ai-search-grader/)

    [Search Grader](https://www.algolia.com/ai-search-grader/)
  + [Profit Simulator](https://www.algolia.com/profit-simulator/)

    [Profit Simulator](https://www.algolia.com/profit-simulator/)
  + [Ecommerce Search Audit](https://www.algolia.com/search-audit)

    [Ecommerce Search Audit](https://www.algolia.com/search-audit)
  + [LLM Leaderboard](https://www.algolia.com/llm-leaderboard)

    [LLM Leaderboard](https://www.algolia.com/llm-leaderboard)
  + [Agentic Readiness Assessment](https://www.algolia.com/dev-agentic-readiness)

    [Agentic Readiness Assessment](https://www.algolia.com/dev-agentic-readiness)

Quick Access

+ [![](/files/live/sites/algolia-assets/files/icons/apartment_blue.svg)

  Company](/about)
+ [![](/files/live/sites/algolia-assets/files/icons/handshake_blue.svg)

  Partners](/partprog)
+ [![](/files/live/sites/algolia-assets/files/icons/support_blue.svg)

  Support](https://support.algolia.com/)
+ [![](/files/live/sites/algolia-assets/files/icons/person_blue.svg)

  Login](https://dashboard.algolia.com/users/sign_in)
+ [![](/files/live/sites/algolia-assets/files/icons/Check%20Square.svg)

  Logout](https://dashboard.algolia.com/users/sign_out)

[Fix your search](/demorequest)

[Get started](https://dashboard.algolia.com/users/sign_up)

Search or Ask AI

Close

[Fix your search](/demorequest)

[Get started](https://dashboard.algolia.com/users/sign_up)

✨
AI mode

Filter by source

✨
How will Algolia improve our search experience and conversions?

✨
How do I integrate Algolia search into my app?

✨
Can Algolia help shoppers find products faster and increase sales?

✨
Will Algolia scale with our traffic and data size?

Suggestions

Products & Resources

✨
Algolia Assist

New chat
Back to results

[AI powered by Algolia](https://algolia.com/products/ai/agent-studio)

[Clear All Filters](javascript:void(0))

## Algolia Assist

[Schedule a call](/demorequest/)
[Sign up today](/users/sign_up?ssnav=start)

## How can I help you today?

I search through your content to help you find answers to your questions, fast.

AI powered by Algolia

![](/files/live/sites/algolia-assets/files/icons/algolialogo.svg)

Looking for our logo?

We got you covered!

[Brand guidelines](https://algolia.frontify.com/)

[Download logo pack](https://www.algolia.com/algolia-logo-pack.zip  )

Engineering

# Inside the Algolia Engine Part 3 — Query Processing

Published: 
August 02, 2023

![](/files/live/sites/algolia-assets/files/blogs/bannerimages/inside-the-algolia-engine.webp)

[Back to all blogs](/blog/engineering)

Inside the Algolia Engine Part 3 — Query Processing

Today most search engines on the market come with a large set of features that developers can use to create their query processing pipeline, but this task is far more difficult than it seems and most people never manage to achieve a good result. In this post, we will cover the classical approaches and how we are handling it in the Algolia engine.

## Introduction to query processing

To be able to find results, a search engine has to be able to understand deeply what was asked. That’s the role of the query processing: to analyse the query, and eventually transform it to make it easier to process by the search engine.

And to do so, a search engine will process the query in two big steps, both of which can be very challenging.

1. **Detect words in the query**: this process is called tokenization and identifies what is a word by answering questions like: `“is t-shirt one word or two?”`
2. **Search for alternatives on this set of words**: the goal of this step is to be less rigid by adding alternative corrections or synonyms, to avoid missing results that don’t contain exactly what was searched, but something equivalent. It decreases the need to reformulate the query to find what you want.
3. ## Why is tokenization complex?

   The process of detecting words involves a set of rules to determine what is a word. It is applied both on the query and when indexing the words, to ensure both have the same format of words, which makes them easier to match.

   This process seems simple at first – at least for alphabet-based languages – but as often, complexity creeps in when you consider the edge cases. And you soon realize that it’s way harder than it seemed, with no easy solutions.

   To give you an idea of the complexity of tokenization, here is a non-exhaustive list of tokenization issues:

   * **Symbols:**You cannot simply ignore symbols. C, C++ and C# are different words. And there are expressions that are composed of symbols only like the [“!!!”](https://en.wikipedia.org/wiki/!!!) band!
   * **Compound words**: some languages like Dutch and German can aggregate words to form one expression. For example in Dutch, the word `"arbeidsongeschiktheidsverzekering"` means `"disability insurance"` and is composed of 3 words: arbeid (labour) + ongeschiktheid (inaptitude) + verzekering (insurance). Of course you would like to have a document containing this long expression match on the `"verzekering"` (insurance) query
   * **Agglutination**: some languages like Japanese, Chinese and Korean don’t  have separators between words (i.e. spaces). Those languages require a statistical approach that helps to detect words in the sequence of ideograms, the search engine also needs to be reliable to an error of word recognition. As with compound words, you want to be able to search for a document with just one of the words.
   * **Acronyms with Punctuation**: you want to find a record containing U.S.A with the USA query and vice versa
   * **Common words containing periods**: sometimes the period can have an importance like for domain names (.com, .net, .org), titles (mr., dr.) or abbreviations (st.)
   * **Hyphenated words**: the hyphen is not an easy case as it can be sometimes considered as a separator like in `"forty-two"` or `"San francisco-based"` but sometimes it is important like in `"pre-processing"`
   * **Apostrophes**: they can be used for clitic contractions (we’re ⇒ we are), as genitive markers (Carl’s haircut) or as quotative markers
   * **CamelCase**: pretty common practice of writing compound words or phrases such that each word or abbreviation begins with a capital letter. You probably want to find your `"#AskGaryVee"` tag via the `"Gary Vee"` query
   * **Others**: HTML entities, dates, time, measures, phone numbers, etc.

   To know what to search for, the engine needs to know which words compose the query. But all of these exceptions make the process of detecting words pretty challenging. Not an easy problem to solve.

## Why is searching for alternatives also complex?

Once the query is tokenized, you have a set of words that will be searched in your documents. We will now enrich the query by searching for alternative words: by expanding the set of words we’ll be able to find matches that are close to the query but not exactly identical.

This process is only performed on the query and not when we index the record. (In a future post, we’ll explain why doing so on indexing is a bad idea.).

If you do not apply this process, you’ll have two problems:

1. You will miss some results if there is a small difference between the words in your records and the query (for example a singular versus plural). You can also have typos or errors in your query that cause those records to be unmatched.
2. The words in the record can be different than the query and lead to a different segmentation. For example, a record that contains ‘hispeed’ will produce one token whereas the query ‘hi speed’ will produce two tokens. This difference is pretty big as we cannot simply search for records containing the query terms anymore.

That’s when it becomes complex. As you can see in this last example, searching for alternatives can potentially change the number of words in the query, which is always a bit of a mess to manage!

We can distinguish four different types of alternatives that can be added to expand the query:

1. **An alternative word on a query word**: your query contains `"egg"` and your record contains `"eggs"`.
2. **A multi-word alternative on a query word**: your query contains `"NY"` and your record contains `"New York"` or if your query contains `"iphone"` and your record contains `"i phone"`.
3. **A word expression as alternative of several query words**: your query contains `"New York"` and you search for a record containing `"NY"` or if your query contains `"i phone"` and want to search for a record containing `"iphone"`
4. **A multi-words expression as alternative of several query words**: this is the most complex one to handle, this is the case if you add a synonym set containing `['NY', 'New York', 'New York City']`. In this case, if your query is `"hotel new york city"`, it will be extended in:

   ```
   OR(AND("hotel","New York"),
      AND("hotel","NY"),
      AND("hotel","new","york"))
   ```

The first type is properly handled in any search engine as it is just an OR between several terms but very few engines handle natively the last three cases which often require a lot of custom code.

## Algolia’s way of tokenizing

Our approach of tokenization was always to keep it as simple as possible. In the end, most challenges of tokenization can be solved via an alternative added at query time! That said, there are some cases which require a special processing at indexing time to be perfect:

1. **Some abbreviation & apostrophes**: If you have `"U.S.A"` in your record, it is very unlikely that you want to have it match for the query `"a"`. Which means you just want to have the token `"usa"` to avoid noise that could break the relevance. It is the same for the `"we're"` expression, in this case you just want to have one token. There are of course exceptions, for example `"l'hotel"` (French expression meaning `"the hotel"`) needs to be found as `"hotel"` and we do not want a token “lhotel”. All those cases are handled automatically by our engine without having to configure anything!
2. **Agglutinative languages**: For languages such as Chinese, Japanese and Korean we use a word dictionary with frequencies to split a sequence of ideograms in several tokens. We also detect the change of alphabet as a new token (this is useful, for example, in Japanese to produce a new token when we move from Hiragana to Kanji). All this processing is done automatically and we improve this segmentation all the time based on our user feedback.
3. **Symbols (&, +, \_ …)**: This part is the only one that is configurable since it depends on the use case and cannot be packaged in a generic way. We have a configuration setting to let you specify the symbols which are important for you. For example we used this approach on a website that helps students. They have to index mathematica formulas and make the difference between `"2x - 1"` and `"2x + 1"`. In this case we have indexed all mathematical symbols (addition, subtraction, multiplication, …)
4. **Compounded words and camel case**: A part of this processing has to be done at indexing if your record contains a compounded word like `"AskGaryVee"` and you want to be able to retrieve this record via the `"Gary Vee"` query. That’s the only step that we do not have today in production but which is on our roadmap. (You can expect to see this in the future!)

At first sight, the process of tokenization can be perceived as simple. But as you have seen it is pretty complex in practice and requires quite a lot of work. We constantly work on improving it.

We only address a few of the tokenization challenges described at the beginning of this article. We actually solve most of them via alternatives added after tokenization. The next section describes those alternatives in details.

## Algolia’s way of searching for alternatives

When we launched the engine in 2013, we had only typo tolerance as an alternative. But since then, we have improved the ability of the engine to find your records even with complex mistakes.

Today the engine expands a query via six different types of alternatives:

1) **Typo tolerance on words**: after tokenization, we look for potential approximations of each query word in the index dictionary (it contains all words used in this index). In practice, we compute a [Damerau-Levenshtein](https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance) edit-distance between the query word and each word of the dictionary and accept the alternative if the number of typos is acceptable.

This Damerau-Levenshtein edit distance represents the number of letters inserted, deleted, substituted or transposed to change the query word to the dictionary word. For example the distance between `"mickael"` and `"mikcael"` is 1 as there is one transposition between `"ck"` and `"kc"` (transposition corresponds to a common typing mistake, two letter are inverted in the word).

In practice, we simplify the process. By looking at the maximum distance that is acceptable for each word, we apply a recursive scan on the dictionary ([represented as a radix tree](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-2-the-indexing-challenge-of-instant-search/)). Then we prune the branches: optimizing the scan by re-evaluating on the fly what doesn’t need to be scanned.

By default we accept a maximum distance of 2 if the query word contains at least 8 letters and a maximum distance of 1 if the query word contains at least 4 letters (although those values are configurable).

Last but not least, the typo-tolerance function is able to correct a prefix, which is important in an instant search scenario. For example `"mikc"` will be considered as one typo of `"mick"` which is the prefix of `"mickael"` (In this case the dictionary does not contains the word `"mick"` but only the word `"mickael"`)

In our engine, typos are tolerated on words and prefix of words natively, without having to configure extra processes like ngram computation. This native approach has also the big advantage of being very efficient at indexing and producing an exact computation of relevance. You can learn more about the way we store our dictionary and prefixes in [part 2](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-2-the-indexing-challenge-of-instant-search/) of this series.

2) **Concatenation**: Typo tolerance on a tokenized query is already a challenge for performance but this is unfortunately not enough: the query tokenization can be different than the one performed at indexing time. This is the case if the query contains `"i phone"` and the record contains `"iphone"` and you would like to have an alternative with the concatenation of query terms! We automatically compute a concatenation for all pairs of terms plus a general concatenation of all the query terms. Which means, for example, that the query `"i phone case"` will generate the query:

```
OR(AND("i","phone","case"),
   AND("iphone","case"),
   AND("i","phonecase"),
   "iphonecase")
```

In order to avoid polluting the results by doing an approximation on an approximation, we do not apply typo tolerance on those new alternatives; they need to be identical in the dictionary. In this query the typo tolerance is only applied on each words of the `AND("i", "phone", "case")` part.

3)**Split of query tokens**: Concatenation is a very good added value of the engine but it unfortunately cannot catch all the cases. The word can be concatenated in the query and split in the record, and in this case you have no other choice than splitting the query term in several words. You have this issue if the query contains the hash tag #searchengine and your record contains `"search engine"`. The Algolia engine will automatically try to split all your query terms in two words using the dictionary. In this case we know the frequency of the “searchengine” term and the frequency of all possible splits. We look at all the possible ways to split the words and select the one that has the best score for `min(freq(word1),freq(word2))`. In this case we take the best score between: `min(freq(s), freq(earchengine))`, `min(freq(se), freq(archengine))`,  … , `min(freq(search), freq(engine))`, … , `min(freq(searchengin), freq(e))`. It is obvious that the maximum will be obtained for the split in `"search"` + `"engine"` and we will extend the query term `"searchengine"` with a phrase query between `"search"` and `"engine"`. (Phrase query means that the terms `"engine"` need to be just after `"search"` in the record to match.)

4) **Transliteration**: All of the approaches we have described before work well for alphabet-based languages but can’t be applied on ideogram-based languages such as Chinese, Japanese and Korean. For these languages we use an extension file of the unicode standard called `"Unihan_variants"` that contains links between ideograms. For example those two lines contains a mapping between a simplified Chinese and traditional Chinese character:

> U+673A  kTraditionalVariant     U+6A5F
>
> U+6A5F  kSimplifiedVariant      U+673A

This unicode file also contains a [Z-variant](https://en.wikipedia.org/wiki/Z-variant) of the same ideogram (share the same etymology but have slightly different appearances), for example:

> U+3588 kZVariant U+439B
>
> U+439B kZVariant U+3588

The unicode format goes even further by containing ideogram with overlapping meanings, for example:

> U+349A kSemanticVariant U+7A69<kFenn,kMatthews
>
> U+349A kSpecializedSemanticVariant U+6587<kFenn
>
> U+6587 kSpecializedSemanticVariant U+349A<kFenn U+7A69<kFenn
>
> U+7A69 kSemanticVariant U+349A<kMatthews

The engine will consider all those transliteration as one or two typo for ideogram-based languages. You will be able to search for simplified Chinese using a traditional Chinese query and vice versa!

5) **Lemmatisation**: Typo tolerance is pretty efficient in tolerating most differences between singular and plural forms. There are of course exceptions like `"city/cities"` or `"foot/feet"`. But the most important thing is that you probably don’t want to consider those small differences as a typo. This is why we have packaged a dictionary that contains singular/plurals form of words in 88 languages. This dictionary is called a lemmatizer and is exposed with the ignorePlural setting. You can simply add singular/plural alternatives without having to care about building such a resource.

6) **Synonyms:**The last type of alternative added in a query are synonyms. We have a pretty powerful synonym feature that handles all types of synonyms:

* Add an alternative on a query term (the alternative can be a single word or a multi-word expression)
* Add an alternative on a multi-term query expression. The alternative can be a multi-word expression and can contain any number of words
* Add a placeholder token in your text that matches a list of words. You can, for example, add <streetnumber> in your record and configure it to match any numeric expression from 1 to 2000. Of course the record will not be found on the `"streetnumber"` query, but `“<streetnumber> Downing Street”` will be found for the query `“10 Downing Street”`.

All those synonyms can be handled with a correct highlighting (`“iPhone”` will be correctly highlighted for the query `"iphine"`, despite the typo) with a correct handling of proximity between expressions. This part is pretty complex and not correctly handled by most engines, we will explain how we handle it in a future post!

We do not package synonyms with the engine. The reason is that synonyms are tightly linked to a domain and most of the time you just need a few of them to increase a lot the quality of your search. For example, I saw the synonym `"t-shirt"` = `"tee"` on several e-commerce website. This synonym makes sense as we see users typing `"tee"` to search for t-shirt, but it can be dangerous if you have sports articles (`"tee ball"` or `"gold tee"`).

The main issue behind that is the [polysemy](https://en.wikipedia.org/wiki/Polysemy) of natural languages and the various specificities of each website. Our take is to handle automatically all the potential typos that few search engines handle automatically (like t-shirt = tshirt = t shirt) and use synonyms as a domain specific tuning you can perform to refine it when needed.

## Building a good query processing takes time!

We have built all those query processing steps over the last four years and of course new ones will come! Our first users only had typo tolerance at the beginning but they have seen the benefits of each improvement! Better: it did not have any negative impact on their relevance due to [our way of handling ranking](https://www.algolia.com/blog/engineering/how-algolia-tackled-the-relevance-problem-of-search-engines/). We also managed to bring all those improvements without sacrificing performance! Before each added alternative, we have implemented a new optimization in the engine to counterbalance the cost of our alternatives!

We recommend to read the other posts of this series:

* [Part 1 – indexing vs. search](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-1-indexing-vs-search/)
* [Part 2 – the indexing challenge of instant search](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-2-the-indexing-challenge-of-instant-search/)
* [Part 4 – Textual Relevance](https://www.algolia.com/blog/engineering/inside-the-algolia-enginepart-4-textual-relevance/)
* [Part 5 – Highlighting, a Cornerstone of Search UX](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-5-highlighting-a-cornerstone-to-search-ux/)
* [Part 6 – Handling Synonyms the Right Way](https://www.algolia.com/blog/engineering/inside-the-engine-part-6-handling-synonyms-the-right-way/)
* [Part 7 – Better relevance via dedup at query time](https://www.algolia.com/blog/engineering/inside-the-engine-part-7-better-relevance-via-dedup-at-query-time/)
* [Part 8 – Handling Advanced Search Use Cases](https://www.algolia.com/blog/engineering/inside-the-engine-part-8-handling-advanced-search-use-cases/)

ABOUT THE AUTHOR

# Recommended Content

Powered by Algolia AI Recommendations

![](/files/live/sites/algolia-assets/files/header_section_1%20(1)%20(2).svg)
![](/files/live/sites/algolia-assets/files/footer-banner-mobile-2023.svg)

## Get the AI search that shows users what they need

[Request demo](/demorequest)

[Get started](https://dashboard.algolia.com/users/sign_up)

[

](/files/live/sites/www/files/homepage-carousel/ai-retrieval-carousel-bg-720.mp4)

![](/files/live/sites/www/files/homepage-carousel/overlay-analyst-recognition.png)

Analyst recognition

## Agentic intelligence layer powering commerce discovery

Recognized by IDC, Gartner, Forrester, and Paradigm B2B, Algolia helps enterprises turn search into a growth engine for AI-native experiences.

[Evaluate Algolia](https://www.algolia.com/demorequest?utm_cta=homepagecarousel)

![](/files/live/sites/www/files/homepage-carousel/cropped-foreground-analyst-recognition.png)

![](/files/live/sites/www/files/homepage-carousel/overlay-gartner-magic-quadrant.png)

Gartner 2026 Magic Quadrant for Search and Product Discovery

## A leader for the third consecutive year

Algolia is recognized as a Leader in the 2026 Gartner® Magic Quadrant™ for Search and Product Discovery as the market shifts toward AI-powered, agentic discovery.

[Read the announcement](https://www.algolia.com/about/news/algolia-recognized-as-a-leader-in-the-2026-gartner-magic-quadrant?utm_cta=homepagecarousel)

[See Algolia in action](https://www.algolia.com/demorequest?utm_cta=homepagecarousel)

![](/files/live/sites/www/files/homepage-carousel/cropped-foreground-gartner-magic-quadrant.png)

![](/files/live/sites/www/files/homepage-carousel/overlay-forrester-tei.png)

Forrester Total Economic Impact™

## Increased Operating Profit and Improved Efficiency

A Forrester Consulting study found Algolia delivered $3.1M NPV over three years, helping commerce teams improve relevance, automate merchandising, and grow revenue

[Download the TEI study](https://www.algolia.com/lp/algolia-forrester-tei-report-2026?utm_cta=homepagecarousel)

![](/files/live/sites/www/files/homepage-carousel/cropped-foreground-forrester-tei.png)

![](/files/live/sites/www/files/homepage-carousel/overlay-idc-marketscape.png)

IDC MarketScape

## Named a leader in knowledge discovery

IDC recognized Algolia as a leader in general-purpose knowledge discovery software, citing the growing role of search in AI-powered workflows and enterprise knowledge experiences

[Read the IDC announcement](https://www.algolia.com/about/news/algolia-named-a-leader-in-idc-marketscape-for-general-purpose-knowledge-discovery-software?utm_cta=homepagecarousel)

![](/files/live/sites/www/files/homepage-carousel/cropped-foreground-idc-marketscape.png)

![](/files/live/sites/www/files/homepage-carousel/overlay-paradigm-b2b-combine.png)

PARADIGM B2B COMBINE

## Top scores across every B2B category

Algolia earned 12 medals across 12 categories in Paradigm B2B’s 2025 Enterprise Combine for Search and Discovery, with customers praising speed, transparency, analytics, and ease of use

[Learn more](https://www.algolia.com/resources/asset/report-paradigm-b2b-enterprise?utm_cta=homepagecarousel)

![](/files/live/sites/www/files/homepage-carousel/cropped-foreground-paradigm-b2b-combine.png)

✕

Hi there 👋 Need assistance? Click [here](javascript:void(0);) to allow functional cookies to launch our chat agent.

![Chat](/files/live/sites/www/files/agentforce/FacadeIcon.png)

1

✕

Thanks for visiting! 👋 I can help answer any questions about Algolia.

Hey! 👋 Got questions about pricing or plans?

Want to skip the form and book some time with our team right now?

Hey there! Would you like to book a meeting with our sales team now?

Thanks for visiting! 👋 I can help answer any questions about Algolia.