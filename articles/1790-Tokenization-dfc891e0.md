---
title: 'Tokenization'
company: Tunkelang
tag: 查询理解
date: 2024-11-16
url: https://queryunderstanding.com/tokenization-c8cdd6aef7ff
account: 
origin: harvest3-202607
---
# Tokenization

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--c8cdd6aef7ff---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--c8cdd6aef7ff---------------------------------------)

3 min read

·

Dec 17, 2016

--

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dc8cdd6aef7ff&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Ftokenization-c8cdd6aef7ff&source=---header_actions--c8cdd6aef7ff---------------------post_audio_button------------------)

Share

Now that we can handle [characters](/character-filtering-76ede1cf1a97#.h0acrul23), let’s move on to words.

A critical task for query and document understanding is breaking up the text into a sequence of words. We call these words tokens — but as we’ll see in a moment, tokens include strings that aren’t necessarily words that appear in a conventional dictionary. [Tokenization](http://nlp.stanford.edu/IR-book/html/htmledition/tokenization-1.html) converts a string of characters into a sequence of tokens.

Tokenization is deceptively subtle. You might think it’s as simple as splitting text on spaces, something you could accomplish using the split method in [Java](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html#split-java.lang.String-) or [Python](https://docs.python.org/2/library/stdtypes.html#str.split). At the very least, you’ll at want to split all white space characters — after all, [some people prefer tabs to spaces](https://www.youtube.com/watch?v=SsoOG6ZeyUI).

**Punctuation**

It may seem innocuous to treat punctuation marks like white space — for example, we expect the same search results for a comma-separated string *apple, oranges, pears* as for the corresponding space-separated string *apples oranges pears*. We’re unlikely to encounter end-of-sentence punctuation in search queries unless users ask natural-language questions ending in question marks, but even then we can probably get away with treating those marks as white space.

**Hyphens and Apostrophes**

Hyphens are tricky. Words with true hyphens, like *twenty-five*, should be considered single tokens. In contrast, words connected by grammatically required hyphens, such as in the compound modifier *California-based*, should be considered multiple tokens.

Apostrophes are even trickier. We encounter them in contractions (e.g., *we’re here*) and possessives (e.g., *women’s rights*). For contractions, we’d ideally tokenize the query as if it were uncontracted (*we are here*) both in queries and in documents. For possessives, logic would have separate out the *’s* as a separate token. But many people are careless about using apostrophes — just think of how often people confuse [*its* and *it’s*](http://grammarist.com/spelling/its-its/). Our job in query understanding is not to be grammarians, but rather to optimize for capturing the searcher’s intent.

**Multiple Tokenizations**

Hence, a reasonable strategy for apostrophes is to compute multiple tokenizations, e.g. tokenizing *women’s* as both *womens* and *women’s*. We improve recall by allowing for multiple tokenization, but we also maintain precision by avoiding tokenizations like *women s* that would retrieve documents containing the letter s as a token. This strategy doesn’t always work, but it is a decent compromise. We can also use it for hyphens.

**Beyond English**

All of the above discussion has focused on tokenization is English. Other languages are just as important, and some raise challenges we don’t usually encounter in English.

Some languages, most notably German, make extensive use of compound words. In these languages, it’s important to decompound words into their components as part of tokenization, e.g., tokenizing the German *Fruchtsalat* as *Frucht* (fruit) *Salat* (salad). Again we can use a multiple tokenization strategy (*Fruchtsalat*, *Frucht* *Salat)*to optimize for recall.

The situation is even harder in Chinese and Japanese text, where there are generally no spaces between words. In these cases, it’s necessary to employ a word segmentation algorithm specific to that language.

Multilingual search engines generally include tools for decompounding and word segmentation. But you should be aware that not all languages are as easy to tokenize as English. Be prepared to handle the inevitable bugs.

**Tokens that Aren’t Words**

Numbers and other symbols require special care.

Standalone numbers like *42* can be treated as tokens. But numbers are often part of larger tokens, e.g., *EC2*, *2x4*. In these cases, we want to be resilient to spacing variations, e.g., we shouldn’t distinguish between *EC2* and *EC* *2*. And some number sequences, like telephone numbers and part numbers, require specialized algorithms to recognize and tokenize them.

Other symbols can also create challenges. For example, we sometimes treat the *@* symbol as a separator, but we don’t want to do so when it occurs in the middle of an email address. Similarly, we want to tokenize *C++* as a single token. You may find that you need to customize your tokenizer to handle these cases.

**No Tokenization Approach is Perfect**

As with every aspect of query understanding, tokenization represents a set of tradeoffs. A highly literal tokenization of the query is likely to be good for precision, but bad for recall; while a more aggressive approach using multiple tokenizations will improve recall at the expense of precision. Handling special cases like strings that combine letters and numbers introduces complexity, but that complexity may be important for your use cases. No approach is perfect, so you’ll need to decide how to manage the trade-offs.

**Previous:** [**Character Filtering**](/character-filtering-76ede1cf1a97#.uagwqp7li)

**Next:** [**Spelling Correction**](/spelling-correction-471f71b19880#.sablpn369)