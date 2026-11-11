---
title: 'Affordances for Conversational Search'
company: Tunkelang
tag: 问答
date: 2023-05-26
url: https://dtunkelang.medium.com/affordances-for-conversational-search-2cc543eae83d
account: Tunkelang
origin: harvest3-202607
---
# Affordances for Conversational Search

In application design, [affordances](https://en.wikipedia.org/wiki/Affordance) are cues that help users discover and explore how to interact with the application. Typical affordances for search applications include buttons and links. Users do not need to be experts to recognize these interface elements and understand how they work.

The excitement around conversational interfaces and [generative AI](https://en.wikipedia.org/wiki/Generative_artificial_intelligence) for search raises an important question: what kind of affordances will such interfaces offer to users? Because, as [Amelia Wattenberger](https://wattenberger.com/) explains in a broad critique of chatbots, “[Text inputs have no affordances.](https://wattenberger.com/thoughts/boo-chatbots)”

### Challenges

Unlike even the early [directory-based web sites of the 1990s](https://webflow.com/blog/90s-website-design), conversational interfaces do not give users much indication of how to start expressing their information needs, or of what content is available. The freedom to type long, natural-language queries into an oversized search box comes with a price: users are on their own. In particular, conversational interfaces do not offer [autocomplete](https://queryunderstanding.com/autocomplete-69ed81bba245?gi=59873d05c85a), a critical if underappreciated tool that users today take for granted in search applications.

Affordances are not just tools to help users start their search interactions. Techniques like [faceted search](https://queryunderstanding.com/faceted-search-7d053cc4fada) and search guides help users refine their initial requests, typically by narrowing a set of results based on structured data attributes. Other common affordances include sorts and filters.

### Potential Solutions

A conversational search application can offer affordances to users.

To address the beginning of the search process, it can provide examples that give users a sense of what is possible to ask. ChatGPT and Bard already do so. The challenge with this strategy is that it is hard to pick a small set of examples that cover the variety of possible requests. While ChatGPT offers a static set of examples, Bard randomly selects examples from a curated set, which allows it to provide more coverage and diversity. While these examples cannot offer as much guidance as a browsing experience, they at least provide some education and help set expectations.

Similarly, a conversational interface can use suggestions as a natural-language analog to the structured refinements of faceted search. For example, if the searcher’s initial request is “What is a good gift for a cat lover?”, good follow-up suggestions include “What are good cat toys?”, “What kinds of cat-themed apparel are there?”, etc. While ChatGPT and Bard do not offer much help here, Shopify’s conversational shopping assistant helpfully asks “Is there a specific occasion or price range you have in mind?” This approach offers at least some of the guidance of faceted search, while still providing the flexibility of natural language input.

### Work in Progress

Conversational search is a work in progress. Despite the excitement around generative AI and the enthusiasm from major search providers like Google, Microsoft, and Amazon, both users and developers are still learning how to make conversational search effective. The freedom of natural language interaction offers incredible potential. At the same time, that freedom puts an enormous burden on users to figure out what they can ask for and how to ask for it. To overcome this burden, we need better affordances.
