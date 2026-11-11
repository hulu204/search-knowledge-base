---
title: 'Is Search Trying Too Hard?'
company: Tunkelang
tag: 工程相关
date: 2024-07-17
url: https://dtunkelang.medium.com/is-search-trying-too-hard-09557c29427f
account: Tunkelang
origin: harvest3-202607
---
# Is Search Trying Too Hard?

Last year, the emergence of ChatGPT and its ability to generate volumes from short prompts led me to speculate about the [compressibility of thought](https://queryunderstanding.com/the-compressibility-of-thought-3dd040eb1e62). In a related vein, I have advocated for an approach to [AI-powered search](https://queryunderstanding.com/ai-powered-search-embedding-based-retrieval-and-retrieval-augmented-generation-rag-cabeaba26a8b) that puts less emphasis on embedding-based retrieval and more on [helping searchers satisfice through query understanding](https://queryunderstanding.com/helping-searchers-satisfice-through-query-understanding-10ac5320fc98).

Putting these two ideas together leads me to ask: is search trying too hard?

Given the weaknesses of today’s search applications, this question may feel counterintuitive. Indeed, shouldn’t search be trying harder? Let us explore the state of search today, and how we might be able to improve it.

### Traditional Keyword Search

First, let us consider traditional keyword search applications.

Despite the excitement about generative AI and natural language interfaces, most search applications still require searchers to express their intent through keywords and respond to queries with a ranked list of results. Although search queries have gotten longer over the years, they are still fairly short — [most containing between one and three words](https://www.statista.com/statistics/269740/number-of-search-terms-in-internet-research-in-the-us/).

It should not surprise us that searchers would rather type less than more, especially when typing on small mobile devices. [Autocomplete](https://queryunderstanding.com/autocomplete-69ed81bba245) can reduce the effort of typing, but it also tends to encourage short queries because those are popular. The result is that many queries have low [specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb), which limits the intent signal available for retrieval and ranking.

Using [AI for query understanding and retrieval](https://queryunderstanding.com/ai-powered-search-embedding-based-retrieval-and-retrieval-augmented-generation-rag-cabeaba26a8b) can improve on traditional token-based methods. However, short, low-specificity queries do not allow search applications to establish fine-grained distinctions among search intents. [Context](https://queryunderstanding.com/contextual-query-understanding-65c78d792dd8) can help but has limited impact. Fundamentally, the signal coming out of [query understanding](https://queryunderstanding.com/introduction-c98740502103) cannot exceed the signal going in.

### Natural Language Search

If keyword search is the problem, then perhaps natural language search is the solution.

For decades, science fiction has depicted a world in which we interact with machines by talking to them. However, we have spent the past few decades learning to compress our intents into short noun phrases so that machines can understand us. This certainly feels unnatural.

Today, AI offers us the opportunity to unlearn this shorthand. Instead of requiring searchers to communicate in a machine-friendly language, [AI-powered search](https://queryunderstanding.com/ai-powered-search-embedding-based-retrieval-and-retrieval-augmented-generation-rag-cabeaba26a8b) can understand intents expressed in natural language.

Natural language interfaces certainly make it easier for searchers to be more expressive. However, it does not follow that natural language interfaces lead to searchers expressing more specific search intents.

For example, it may be more natural for a searcher to ask “I’m looking for a pair of running shoes for men” than to enter “mens running shoes”, but the natural language query conveys the same intent as the keywords — despite containing 3 words rather than 10. Communicating search intent the way we talk to each other may feel more natural, but it does not provide any more signal for retrieval or ranking.

Do natural language interfaces encourage searchers to provide more signal, rather than just using more words? There is [some evidence](https://arxiv.org/pdf/2302.06349v1) that they do, but it is tricky to disentangle this effect from other factors, such as the size of the input interface. Given the effort associated with typing, it seems unlikely that searchers will want to type significantly more than they do today. Perhaps we will replace typing search queries with [speaking](https://queryunderstanding.com/query-understanding-and-voice-interfaces-6cd60d063fca), but that has not yet happened — at least for most search applications.

### Lossy Indexing

Even if interface changes lead searchers to provide more signal — and even if we assume even with perfect query understanding — there are still the challenges of indexing, retrieval, and ranking.

Indexing is the foundation of information retrieval. A search application can only retrieve content using the information it knows about that content. Not only does the signal need to be present in the content, but it must be available for retrieval and ranking. Hence, improving search often requires investment in [content understanding](https://medium.com/content-understanding/what-is-content-understanding-4da20e925974).

However, highly granular indexing yields diminishing returns. A relatively small number of key attributes of a product or document are sufficient to meet the needs of most searchers, but a much larger number of attributes are necessary to address the remainder. It is hard to justify investing in a highly granular content representation when most searchers don’t care.

Unfortunately, this leads to a vicious cycle: indexing uses a lossy content representation to maximize return on investment, while searchers learn that there is no point expressing intents so granular that the index cannot use them for retrieval and ranking. The result is mutual [satisficing](https://en.wikipedia.org/wiki/Satisficing).

### Where To Go From Here

We can try to escape this vicious cycle by pursuing a virtuous one, simultaneously investing in better content and query understanding. The returns may be diminishing, but they are still positive — and they may be worth the additional investment.

Alternatively, we can embrace something like the [bag-of-queries](https://queryunderstanding.com/bags-of-queries-as-sparse-document-representations-bc450db3e814) model, which represents documents by mapping them to the queries for which they are relevant. This bag-of-queries model aims to achieve the best of both worlds: the sparsity of a traditional [inverted index](https://en.wikipedia.org/wiki/Inverted_index) and the holistic representation of dense vectors. At the same time, it focuses on the aspects of content representation that align with searcher demand.

Regardless of what approach we take, we need to remember that better search is about working smarter and not necessarily harder. Search can only use the signal present in content and queries. If search relentlessly looks for a signal that is not in either, then it is trying too hard.
