---
title: 'https://eugeneyan.com//writing/product-categorization-api-part-2-data-preparation/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/product-categorization-api-part-2-data-preparation/
account: 
origin: en-rss
---
# [eugeneyan](/)

* [Start Here](/start-here/ "Start Here")
* [Writing](/writing/ "Writing")
* [Speaking](/speaking/ "Speaking")
* [Prototyping](/prototyping/ "Prototyping")
* [About](/about/ "About")
* [![](/assets/icon-search.svg)](/search/ "Search")

# Product Classification API Part 2: Data Preparation

[
[machinelearning](/tag/machinelearning/)
[python](/tag/python/)
[🛠](/tag/🛠/)
]
 · 8 min read

This post is part 2 of the series on building a product classification API. The API is available for demo [here](http://datagene.io/). Part 1 available [here](/writing/product-categorization-api-part-1-data-acquisition-and-formatting/); Part 3 available [here](/writing/product-categorization-api-part-3-creating-an-api/). ([Github repositiory](https://github.com/eugeneyan/datagene))

> Update: API discontinued to save on cloud cost.

In part 1, we focused on data acquisition and formatting the categories. Here, we’ll focus on preparing the product titles (and short description, if you want) before training our model.

This is part of a series of posts on building a product classification API:

* [Data acquisition and formatting (part 1)](/writing/product-categorization-api-part-1-data-acquisition-and-formatting/)
* [Data cleaning and preparation (part 2)](/writing/product-categorization-api-part-2-data-preparation/)
* [API development (part 3)](/writing/product-categorization-api-part-3-creating-an-api/)
* [Image classification demo](/writing/image-categorization-is-now-live/)
* [Image search demo](/writing/image-search-is-now-live/)

## Measuring data purity

We’ll have products within our data that are categorized incorrectly. How do we exclude these mis-categorized products from our training set?

Here’s one approach: If two products have the same title but different category, we assume that at least one of the products is mis-categorized (and the data is dirty).

Extending on the above, as we take steps to prepare our data, we’ll be measuring data “purity” at each step. In this instance, purity is defined as:

`Products with the same title and same category / Total number of products`

This measures the proportion of products that have the same title and same category in our data. The higher the purity, the cleaner we can assume our data to be.

At the end of the [data preparation](https://dataladder.com/data-preparation-guide/), we’ll be able to identify which products are “impure”. Given that we’re unable to distinguish between correctly and incorrectly categorized products, we’ll exclude them from the training of the model.

## Preparing the title (and short descriptions)

The titles need a bit of cleaning and preparation before we can train our model on them. In the next steps, we’ll go through some sample data cleaning and preparation procedures.

## Encoding titles as ascii

It’s not uncommon to find non-ascii characters in data, sometimes due to sellers trying to add a touch of class to their product (e.g., Crème brûlée), or due to errors in scraping the data (e.g., `&quot`, `&amp`, `&nbsp`).

Thus, before doing any further processing, we’ll ensure titles are properly encoded so that Crème brûlée -> Creme brulee, åöûëî -> aouei, and " &   -> “ & ‘.

Here’s the approach I took:

```
# Function to encode string
def encode_string(title, parser=HTML_PARSER):
    """ (str) -> str

    Returns a string that is encoded as ascii

    :param title:
    :return:

    >>> encode_string('Crème brûlée')
    'Creme brulee'
    >>> encode_string('åöûëî')
    'aouei'
    >>> encode_string('Crème brûlée " &  ')
    'Creme brulee " & '
    """

    try:
        encoded_title = unicodedata.normalize('NFKD', unicode(title, 'utf-8', 'ignore')).encode('ascii', 'ignore')
        encoded_title = parser.unescape(encoded_title).encode('ascii', 'ignore')
    except TypeError:  # if title is missing and a float
        encoded_title = 'NA'

    return encoded_title
```

There’s quite a bit going on in the code above, so let’s examine it piece by piece:

```
x = 'Cr\xc3\xa8me & br\xc3\xbbl\xc3\xa9e’; print x

# Convert titles into unicode
x = unicode(x, 'utf-8', 'ignore'); print x
>>> Crème & brûlée

# Normalize unicode (errors may crop up if this is not done)
x = unicodedata.normalize('NFKD', x); print x
>>> Crème & brûlée

# Encode unicode into ascii
x = x.encode('ascii', 'ignore'); print x
>>> Creme & brulee

# Parse html
x = HTML_PARSER.unescape(z).encode('ascii', 'ignore'); print x
>>> Creme & brulee
```

## Lowercasing titles

Lowercasing titles is a fairly standard step in text processing. We’ll lowercase all title characters before proceeding.

## Tokenizing titles

One common way to tokenize text is via nltk.tokenize. I tried it and found it to be significantly slower than using regular regex. In addition, writing our own regex tokeniser gives us flexibility in excluding certain characters that are being used as a split character.

For example, we want to exclude the following words/phrases from being tokenised by splitting on the punctuation character in brackets. Intuitively, the punctuation characters provides essential information; empirically, keeping them led to greater accuracy during model training and validation.

* hyphen-words (-)
* 0.9 (.)
* 20% (%)
* black/red (/)

Here’s how we write our own tokeniser:

```
# Tokenize strings
def tokenize_title_string(title, excluded=‘-/.%'):
    """ (str) -> list(str)

    Returns a list of string tokens given a string.
    It will exclude the following characters from the tokenization: - / . %

    :param title:
    :return:

    >>> tokenize_title_string('hello world', '-.')
    ['hello', 'world']
    >>> tokenize_title_string('test hyphen-word 0.9 20% green/blue', '')
    ['test', 'hyphen', 'word', '0', '9', '20', 'green', 'blue']
    >>> tokenize_title_string('test hyphen-word 0.9 20% green/blue', '.-')
    ['test', 'hyphen-word', '0.9', '20', 'green', 'blue']
    >>> tokenize_title_string('test hyphen-word 0.9 20% green/blue', '-./%')
    ['test', 'hyphen-word', '0.9', '20%', 'green/blue']
    """

    return re.split("[^" + excluded + "\w]+", title)
```

### Removing stop words

After tokenising our titles, we can proceed to remove stop words. The trick is in which stop words to remove. For the product classification API, I found a combination of the following to work well:

* Stop words: nltk.corpus.stopwords
* Colours: matplotlib.colors.cnames.keys
* Self-defined: We also define some words that come across as spam, such as “free”, “international”, etc.

At this point, after tokenising the titles, the tokens are stored in a list. We can remove stop words easy and cleanly via list comprehension, like so:

```
# Remove stopwords from string
def remove_words_list(title, words_to_remove):
    """ (list(str), set) -> list(str)

    Returns a list of tokens where the stopwords/spam words/colours have been removed

    :param title:
    :param words_to_remove:
    :return:
    >>> remove_words_list(['python', 'is', 'the', 'best'], STOP_WORDS)
    ['python', 'best']
    >>> remove_words_list(['grapes', 'come', 'in', 'purple', 'and', 'green'], STOP_WORDS)
    ['grapes', 'come']
    >>> remove_words_list(['spammy', 'title', 'intl', 'buyincoins', 'export'], STOP_WORDS)
    ['spammy', 'title']
    """

    return [token for token in title if token not in words_to_remove]
```

## Removing words that are solely numeric

We’ll also remove words that are solely numeric. Intuitively, an iPhone 7, iPhone 8, or iPhone 21 should all be categorized as a mobile phone, and having the numeric suffix does not add any additional useful information to categorize it better. Can you think of a product where removing the numerics would put it in different category?

Similar to above, removing numerics can be accomplished easily via list comprehension:

```
# Remove words that are fully numeric
def remove_numeric_list(title):
    """ (list(str)) -> list(str)

    Remove words which are fully numeric

    :param title:
    :return:

    >>> remove_numeric_list(['A', 'B2', '1', '123', 'C'])
    ['A', 'B2', 'C']
    >>> remove_numeric_list(['1', '2', '3', '123'])
    []
    """

    return [token for token in title if not token.isdigit()]
```

## Removing words with too few characters

We also remove words that have character length below a certain threshold. E.g., if the threshold is two, then single character words are removed; if the threshold is three, then words with two characters are removed.

To an untrained eye (like mine), double character words like “TX”, “AB”, “GT” doesn’t add much informational value to the title—though there are exceptions like “3M”. Via cross-validation, I found that removing these words led to increased accuracy.

Here’s how we remove these double character words—you can change the word length threshold to suit your needs:

```
# Remove words with character count below threshold from string
def remove_chars(title, word_len=2):
    """ (list(str), int) -> list(str)

    Returns a list of str (tokenized titles) where tokens of character length =< word_len is removed.     :param title:     :param word_len:     :return:     >>> remove_chars(['what', 'remains', 'of', 'a', 'word', '!', ''], 1)
    ['what', 'remains', 'of', 'word']
    >>> remove_chars(['what', 'remains', 'of', 'a', 'word', '!', '', 'if', 'word_len', 'is', '2'], 2)
    ['what', 'remains', 'word', 'word_len']
    """

    return [token for token in title if len(token) > word_len]
```

## Removing duplicated words

Next, we exclude duplicated words in titles. Sometimes, titles have duplicate words due to sellers attempting to apply search engine optimisation (SEO) on their products to make them more findable. However, these duplicate words do not provide any additional information to categorizing products.

We can remove duplicate tokens by converting the token list to a token set—yes, this removes any sequential information in the title. However, we’re only doing this step to identify impure products that should not be used in training our model. During the actual data preparation, we will exclude this step.

Converting a list to a set shouldn’t be too difficult right? I’ve leave that for the reader.

## Removing empty titles

Lastly, after performing all the cleaning and preparation above, there may be some titles that have no text left. (This means that those titles only contained stop words, numerics, or words with < 3 character length.) We’ll exclude these products as well.

## Excluding titles that are impure

After doing the above, we’re left with titles in their most informational rich and dense form. In this case, we’re confident that products with identical titles and categories are correctly categorized, while products with identical titles but different categories have at least one error in them (i.e., impure)

Among the impure products, without having ground truth about which are correctly or incorrectly categorized, we’ll discard them and not use them to train our model.

## Conclusion

Whew! That’s a lot of work just to clean titles! Nonetheless, We’re largely done with the data preparation steps.

Next, we’re going to share about the framework to making this product classifier available online, via a simple web UI. This will involve the following:

* Writing a class to take in titles, prepare them, and categorize them.
* Writing a simple flask app

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Dec 2016). Product Classification API Part 2: Data Preparation. eugeneyan.com.
> https://eugeneyan.com/writing/product-categorization-api-part-2-data-preparation/.

or

```
@article{yan2016preparation,
  title   = {Product Classification API Part 2: Data Preparation},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2016},
  month   = {Dec},
  url     = {https://eugeneyan.com/writing/product-categorization-api-part-2-data-preparation/}
}
```

  
Share on: 

![](/assets/icon-twitter.svg)

![](/assets/icon-linkedin.svg)

![](/assets/bluesky.svg)

![](/assets/icon-facebook.svg)

![](/assets/icon-mail.svg)

---

  

Browse related tags: [
[machinelearning](/tag/machinelearning/)
[python](/tag/python/)
[🛠](/tag/🛠/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Strata x Hadoop 2016 - How Lazada Ranks Products](/speaking/shared-about-my-work-in-lazada-at-strata-hadoop-singapore-2016-talk/)
[Image search is now live! »](/writing/image-search-is-now-live/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---