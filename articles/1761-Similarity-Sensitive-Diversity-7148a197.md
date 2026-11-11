---
title: 'Similarity-Sensitive Diversity'
company: Tunkelang
tag: 排序
date: 2023-08-28
url: https://dtunkelang.medium.com/similarity-sensitive-diversity-16a35d64f48c
account: Tunkelang
origin: harvest3-202607
---
# Similarity-Sensitive Diversity

In my work on search engines and recommender systems, I’ve thought a lot about [entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory)) and [diversity](https://en.wikipedia.org/wiki/Diversity_index). I named my first blog, [The Noisy Channel](https://thenoisychannel.com/), after a seminal idea of [Claude Shannon](https://en.wikipedia.org/wiki/Claude_Shannon), who introduced entropy to [information theory](https://en.wikipedia.org/wiki/Information_theory), from which it spread to [information retrieval](https://en.wikipedia.org/wiki/Information_retrieval) and [machine learning](https://en.wikipedia.org/wiki/Machine_learning).

This post explores a way to measure diversity in the context of search engines and recommender systems. The approach addresses a key weakness of the conventional diversity measures we use in these applications — namely, that these measures treat distinct values as completely unrelated to each other. Instead, a diversity measure should account for similarity among values. To overcome this weakness, we need a similarity-sensitive diversity measure.

The explanation starts with some background on entropy and diversity, and be warned that there’s a bit of math. But I promise that the destination is worth the journey, and I encourage you to ask questions in the comments.

### Entropy

Shannon defined the entropy of a [probability distribution](https://en.wikipedia.org/wiki/Probability_distribution) as the [expected value](https://en.wikipedia.org/wiki/Expected_value) of the [information content](https://en.wikipedia.org/wiki/Information_content) of a value drawn from that distribution.

The information content of a value with probability *p* is *log₂(1/p) = - log₂(p)*. The information content increases by *1* with each halving of *p*: for *p =1/2*, the information content is *1*; for *p = 1/4*, it’s *2*; for *p = 1/8*, it’s *3*, etc. As we can see, rare values carry high information content.

Entropy is the expected value of the information content. Weighing the information content of each value by its probability *p *yields the definition of entropy as the sum *Σ(p * log₂(1/p)) = - Σ(p * log₂(p))*.

Entropy measures how much a probability distribution spreads out over its values. The maximum entropy possible for a distribution that takes on *n* values (e.g., the integers *1* to *n*) comes from a [uniform distribution](https://en.wikipedia.org/wiki/Discrete_uniform_distribution) over those values, where each of the *n* values has probability *1/n*. The entropy of a uniform distribution over *n* values is *log₂(n)*. In contrast, if a single value has a probability close to *1* (e.g., *0.99*), then the entropy will be close to *0*.

Consider the distribution of categories in a set of search results. If all of the results are from the same category, the distribution has an entropy of *0*. If the results are uniformly split across eight categories, the entropy is *3*. But if 93% of the results are in one category and the remaining 7% are uniformly distributed among the remaining seven, then the entropy is equal to *0.93*log₂(1/0.93) + 7*0.01*log₂(1/0.01) = 0.56*.

### Diversity

We define diversity as the exponentiation of entropy: *2^(- Σ(p * log₂(p)))*.

As discussed above, a uniform distribution over *n* values has an entropy of *log₂(n)*. [Exponentiation cancels out the logarithm](https://en.wikipedia.org/wiki/Logarithm), so the diversity of a uniform distribution over *n* values is *n*. And, since a uniform distribution maximizes entropy for a distribution over *n* values, it also maximizes diversity.

Most probability distributions aren’t uniform. But the diversity of a probability distribution allows us to compare any distribution to a uniform distribution with the same diversity. Diversity measures the [effective number](https://en.wikipedia.org/wiki/Diversity_index#Effective_number_of_species_or_Hill_numbers) (also called a Hill number) of values contained in a comparable uniform distribution.

Returning to the previous example, an entropy of *0.56* gives us a diversity of *1.48*. So, despite there being *8* categories, the non-uniform distribution translates to a much smaller effective number of categories.

### Similarity

It’s hard to overstate the importance of entropy and diversity to information theory and computer science generally. Diversity can tell us whether a search query is [broad or ambiguous](https://queryunderstanding.com/broad-and-ambiguous-search-queries-1bbbe417dcc), and it helps determine when and how to present [diverse search results](https://queryunderstanding.com/thoughts-on-search-result-diversity-1df54cb5bf4a). Recommender systems often aim to produce diverse recommendations to hedge their bets when they predict user interests.

Unfortunately, the above definition of diversity has a critical flaw. It treats the values of a probability distribution as either the same or completely distinct, when it should account for similarity among values. Let’s look at an example.

Consider a collection of *100* shirts that come in four different colors. If the shirts are uniformly distributed across the colors, we get an entropy of *2* and a diversity of *4*. But what if the colors are red, light red, dark red, and blue? The variations of red may not be identical, but this still feels more like a *75% / 25%* split over two colors — which would imply a diversity of about *1.75* — than a uniform distribution over four colors. A realistic measure of diversity should return a value closer to *2* than *4*.

What we need a similarity-sensitive measure of diversity.

### Similarity-Sensitive Diversity

Fortunately, there is already a solution to this problem in the [biodiversity](https://en.wikipedia.org/wiki/Biodiversity) literature. In 2012, [Tom Leinster](https://www.maths.ed.ac.uk/~tl/) and [Christina Cobbold](https://www.maths.gla.ac.uk/~cc/) published “[Measuring Diversity: the Importance of Species Similarity](https://www.maths.ed.ac.uk/~tl/mdiss.pdf),” From their abstract:

> Realistic measures of biodiversity should reflect not only the relative abundances of species, but also the differences between them. We present a natural family of diversity measures taking both factors into account.

Leinster elaborates on this approach in Chapter 6 of his 2021 book titled [*Entropy and Diversity: The Axiomatic Approach*](https://arxiv.org/abs/2012.02113), which I highly recommend.

Leinster and Cobbold’s approach requires a pairwise similarity [matrix](https://en.wikipedia.org/wiki/Matrix_(mathematics)) *Z* as an input. This [square matrix](https://en.wikipedia.org/wiki/Square_matrix) describes the similarity between every pair of values covered by the probability distribution. If *Z* is the [identity matrix](https://en.wikipedia.org/wiki/Identity_matrix), with values of *1* along the diagonal and *0* elsewhere, then we treat distinct values as completely unrelated. But if *Z* has non-zero values off the diagonal, they indicate similarities that our diversity measure should account for.

Let’s define *pᵢ* as the probability associated with value *i* in our distribution and* Zᵢⱼ* as the similarity between values *i* and *j*. Then we can adjust our definition of information content to make it similarity-sensitive: *log₂(1 / Σ(Zᵢⱼ* pⱼ))*.

When *Z* is the identity matrix, this reduces to the Shannon definition of information content. Otherwise, the non-zero off-diagonal entries increase the denominator and those lower the information content. Entropy is the expected value of the information content and diversity is the exponentiation of entropy, so the non-zero off-diagonal entries lower the diversity, as desired.

### Similarity Matrix

The above approach is simple and easy to implement, but where does the similarity matrix Z come from? The approach is agnostic about how we define the similarity, but we still need some way to populate the similarity matrix *Z*.

When values have numerical or spatial representations, we can use those to determine similarity. For example, [RGB](https://www.w3schools.com/colors/colors_rgb.asp) representations of colors make it clear that light red and dark red are closer to red than to blue. Indeed, there are a number of ways to measure [color difference](https://en.wikipedia.org/wiki/Color_difference). If our values are locations, we can measure their similarity using the distances between them. If we have distances rather than similarities, we have to perform some kind of conversion, e.g., converting distance *d* to similarity *1/(1+d)*.

If the values are categories, brands, or other kinds of attributes, it may be less straightforward to define a similarity matrix. For example, it’s intuitive that, among watch brands, [Rolex](https://en.wikipedia.org/wiki/Rolex) is more similar to [Cartier](https://en.wikipedia.org/wiki/Cartier_(jeweler)) than to [Casio](https://en.wikipedia.org/wiki/Casio), but how to we quantify this similarity? In this case, we might be able to derive brand similarity from the similarity of the price distributions; since luxury watches cost more than watches from non-luxury brands. More broadly, if we can convert the values to [vectors](https://en.wikipedia.org/wiki/Vector_(mathematics_and_physics)) (i.e., [embeddings](https://en.wikipedia.org/wiki/Word_embedding)), then we can compute the similarity between two vectors using [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) or [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance).

### Summary

The key weakness of conventional diversity measures is they treat all values as either the same or completely distinct. This post addresses this weakness by advocating a similarity-sensitive measure of diversity that accounts for similarity among values. Using it requires populating a similarity matrix, based on inherent properties of the values or on some kind of embedding. A similarity-sensitive measure of diversity provides a better representation of actual diversity for search engine and recommender system applications, which in turn allows us to deliver better user experiences.
