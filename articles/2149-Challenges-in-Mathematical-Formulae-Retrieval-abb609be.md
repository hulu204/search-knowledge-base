---
title: 'Challenges in Mathematical Formulae Retrieval'
company: Sease
tag: 召回
date: 2024-09-04
url: https://sease.io/2024/09/mathematical-formulae-retrieval.html
account: 
origin: harvest3-202607
---
*This is one of several posts written in collaboration with the students in Sease’s Scientific Blog Post seminar at the University of Padova. This post is written in collaboration with the students [Simone Bortolin](https://www.linkedin.com/in/simonebortolin/), [Giovanni Zerbo](https://www.linkedin.com/in/giovanni-zerbo-3bb46b298/), [Gioele Ceccon](https://www.linkedin.com/in/gioele-ceccon-38a1b2244/), [Pietro Renna](https://www.linkedin.com/in/pietro-renna/), Alessandra Pastore and [Gil Czaczkes](https://www.linkedin.com/in/gil-czaczkes-5527b428a/).*

Hello readers!

This blog post focuses on the problems and challenges involved while developing a search engine for **mathematical formulae retrieval**, an important topic often forgotten by the Science, Technology, Engineering and Mathematics (STEM) community.  
We will highlight the main problems one could encounter during the development of such a search engine and how different techniques could solve them.

## Mathematical Formulae and Mathematical Information Retrieval

##### **WHY IS IT IMPORTANT TO BE ABLE TO SEARCH FORMULAE?**

In science, formulae are a concise and unambiguous method of expressing quantitative relationships, properties, and characteristics through specific operations. They provide an intra-language interpretation and people all over the world are able to read the same formula.

A formula consists of 4 elements:

* **coefficients**or **constant variables**
* **operators**: *+, -, =, ×, ∫*
* **variables**: *a, b, x, y, z, α, β*
* **order operators**: *(, ), [, ]*

On the contrary, a document is represented by a sequence of letters forming words separated by spaces and punctuation symbols. This implies that there are various differences and similitudes among them.

![Challenges in Mathematical Formulae Retrieval differences](https://sease.io/wp-content/uploads/2023/05/differences.svg) 

Differences and similarities between sentences and formulae

The last two points are the main problems: **there is still no production-ready search engine to retrieve formulae**.

##### WHY IS IT IMPORTANT TO RETRIEVE MATHEMATICAL FORMULAE IN DOCUMENTS?

Let’s look at a striking case of what happens when one does not know the source of a formula.

![Evolutions of Katan's formula in the literature](https://sease.io/wp-content/uploads/2023/06/katan_vectorial.svg) 

Evolutions of Katan’s formula in the literature

In the literature on explosion safety, the formula known as **modified Fauske** is often used and wrongly attributed. Firstly introduced in 1999 and then modified in 2012, the authors of the CEI guide (Italian Electronics Guidelines for Safety Measures) were unable to find the original formula.

The search for the real author, i.e. Katan and **not Fauske**, took place “by hand”, with the manual look at all the bibliographies that cited the modified Fauske formula, until the original one was found.

If only a dedicated search engine was already accessible and usable, it could have avoided this long process. Numerous other cases could take advantage of a similar search engine, to save valuable time and effort.

## State-of-the-Art

**Mathematical Information Retrieval** (MIR) is a well-known fast-growing research field within the domain of **Natural Language Processing**. The primary goal of a MIR system is to retrieve scientific documents and formulae relevant to a queried formula.

To efficiently retrieve a document from a MIR query, the formulae in the documents should follow certain rules:

* the formulae must be **easily identified** and differentiated from normal text and images;

![](https://sease.io/wp-content/uploads/2023/06/identified.svg)

*Identified formula from a text [[1](https://dl.acm.org/doi/10.1145/2911451.2911503)]*

* the formulae must employ**unambiguous notation**, with clear units of measurement for each unknown variable, to adjust and standardize the present coefficients;

![](https://sease.io/wp-content/uploads/2023/06/speed_unit_l.svg) 

Different documents with the c constant represented with different units of measurement

* the formulae must have a **citation in the document** or else a **caption**. Standard information retrieval techniques can be used to retrieve the description and some contextual information.

![](https://sease.io/wp-content/uploads/2023/06/extract.svg)

*Find contextual information from formula [[1](https://dl.acm.org/doi/10.1145/2911451.2911503)]*

Even following the aforementioned rules, three main problems still arise. **How do we best represent formulae within documents?** Many different standard formats already exist and can be easily indexed, but not all documents use them. Once the formula is identified, **how should we process it?** Similarly to standard information retrieval, where documents are processed into singular tokens, an analyzer must parse and process the formulae into tokens of some kind.

##### FIRST PROBLEM – How to represent formulae

The first problem in Mathematical Formulae Retrieval is the **representation of formulae**. There are many different representation formats: some without loss of information, such as **[TeX/LaTeX](https://www.latex-project.org/)**and**[MathJax](https://www.mathjax.org/)** (which share the same textual markup language), **[UnicodeMath 3.1](https://www.unicode.org/notes/tn28/UTN28-PlainTextMath-v3.1.pdf)** (of Microsoft Word/Office), [**OpenDocument Formula**](https://www.iso.org/standard/43485.html), **[MathML](https://www.w3.org/Math/)** (Mathematical Markup Language), and others with losses, for example, PDF documents, images, or e-ink. In the first case, we can retain the characters only and lose all information on superscripts, subscripts, fractions, and a large part of symbols without repercussions. However, the last two cases represent the formula graphically, thus we cannot easily retrieve a large part of the information.

![Challenges in Mathematical Formulae Retrieval derivative vector](https://sease.io/wp-content/uploads/2023/06/derivate_vectorial.svg) 

Representation of the same mathematical formula in different formats

Fortunately, there are tools, such as **[MathPix](http://mathpix.com/)**, that incorporate features to perform Math OCR (Optical Character Recognition), and other tools such as **[CorTex](https://github.com/dginev/CorTeX)** that allow indexing scientific papers in a format independent of TeX, PDF, Word, etc.

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/05/mathpix.png?fit=1538%2C1244&ssl=1)

*MathPix user interface [[2](http://mathpix.com/)]*

##### SECOND PROBLEM – How to SEARCH formulae

In document-based information retrieval, documents are parsed into words or phrases representing individual tokens. One could see formulae as phrases but then the identification of the single tokens is not an easy task as the identification of words. The principal elements of formulae are coefficients, symbols, and operators and they need to be processed in a specific order. Treating these elements as the tokens of a formula leads to information loss and ambiguity.

To solve the information loss issue, it is possible to use a tree structure that connects the single tokens. This technique is called a subtree-based index. Coefficients, symbols, and operators are found at the nodes, and the edges represent the often implicit order operators. Using a depth-first search leads to the formula.

However, there could be more than one subtree associated with the same equation, thus not solving the ambiguity issue stated before.

![Challenges in Mathematical Formulae Retrieval tree formula](https://sease.io/wp-content/uploads/2023/05/tree.svg) 

Sub-tree parsing of mathematical formula

Linear indexing systems based on **Reverse Polish Notation** are an alternative to tree structures. Reverse Polish Notation is a mathematical notation system, in which operators and coefficients follow their operand pairwise without the need for explicit order operators.

```
				
					5 + (10 * 2) → 5 10 2 * + 
				
			
```

The main idea behind this approach is that the indexing of documents based on information retrieval shouldn’t treat certain words singularly. Taking both operators and operands as a single token, similar to already existing phrase-search systems, and combining the Reverse Polish Notation technique with the subtree-based index, can potentially address both the issues of information loss and ambiguity.

##### THIRD PROBLEM – HOW TO NORMALIZE FORMULAE

Finally, there are many different ways to represent the same formula, and the normalization is difficult, due to:

* **different names** for the same variables (e.g. *x*² + *y*² = *z*² is the same as *a*² + *b*²= *c*² )
* **different unit of measurement** (e.g. meter and foot)
* **different scale factor** for the same unit of measurement (e.g. meter and kilometre)

The use of conversion tables could solve these last two challenges, but the first one remains an open problem.

## Past solutions: some more modern system architectures

In recent decades, many research teams partially solved these challenges. Here we briefly present some of their works:

* **MathDex (2008)**, **EgoMath (2013)**, **[OPMES](https://approach0.xyz/search/) (2016)** are the first equation search engines devised, which primarily use a token-based indexer system.

![MathDex user interface](https://i0.wp.com/sease.io/wp-content/uploads/2023/05/image-1.png?fit=821%2C377&ssl=1)

*MathDex user interface: we can see that there is an input form for mathematical formulae [[3](https://dl.acm.org/doi/10.1145/1378889.1378921)]*

* In the recent **[NTCIR](https://research.nii.ac.jp/ntcir/index-en.html)**([NII](https://www.nii.ac.jp/) Testbeds and Community for Information access Research) **competitions (2013-2023)**, all the participants developed similar search engines. In particular, most of them used a subtree-based index, while some others still relied on the traditional token-based methodology as in standard information retrieval. Regarding the normalization of variables, some teams tried to use a re-ranking system but it never fully solved the problem.
* **[MathUSE](https://journals.sagepub.com/doi/10.1177/01655515221077335) (2020)** is perhaps the best system currently available. It is based on a Neural Language Processing system and the researcher trained it as a neural network based on approximations, therefore it retrieves many similar but unrelated formulae, leading to a loss of performance.

## What’s next?

We conclude this section by presenting some potential new approaches to consider for the development of a working system for mathematical formulae retrieval.

Could we use machine learning and deep learning systems? Deep learning systems such as formula2vec (Formula to Vector) and symbol2vec (Symbol to Vector) reproduce how [word2vec](https://sease.io/2023/04/word2vec-model-to-generate-synonyms-on-the-fly-in-apache-lucene-introduction.html) (Word to Vector) works, but what do these systems find? Are they useful? It is evident that mathematical formulae are complex and rigid structures and for this reason, a model like word2vec could cause more losses than benefits.

**So what should we try next?**

We hope that this topic will find more acknowledgement in the future and that the STEM community will try and test more possible approaches so that this problem will finally find its working solution.

## Summary

In this post, we talked about the importance and complexity of developing a math search engine. We aimed to introduce the challenges it presents and some potential solutions.

However such a system for mathematical formulae is not already available due to the problems we described, but we are confident that someday one will make it to the market.

## Do you want to be published?

This blog post is part of our collaboration with the University of Padua. If you are a University student or professor and want to collaborate, contact us through e-mail.

[Click here](mailto:info@sease.io)

## Do You Want To Be Published?

This blog post is part of our collaboration with the University of Padua. If you are a University student or professor and want to collaborate, contact us through e-mail.

[Click Here](mailto:info@sease.io)