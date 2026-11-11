---
title: 'https://www.lancedb.com/blog/a-primer-on-text-chunking-and-its-types-a420efc96a13'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/a-primer-on-text-chunking-and-its-types-a420efc96a13
account: 
origin: en-rss
---
# A Primer on Text Chunking and Its Types

[Prashant Kumar](/author/prashant-kumar)

•

October 24, 2023

•

[Community](/category/community)

![1453-https-www-lancedb-com-blog-a-primer-on-text-chun-2216b01b-fig-001](../images/1453-https-www-lancedb-com-blog-a-primer-on-text-chun-2216b01b/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

Text chunking is a technique in natural language processing that divides text into smaller segments, usually based on the parts of speech and grammatical meanings of the words. Text chunking can help extract important information from a text, such as noun phrases, verb phrases, or other semantic units.

In this blog, We’ll see some Text Chunking strategies, why they are important for building LLM-based systems like RAG, and How to use them.

## Why is Text Chunking Important?

There are various reasons why text chunking becomes important when working with LLMs, and in this post, we’ll share a few examples that have a significant impact on the results.

Say you have a document of 15 pages full of text and you want to perform summarization and question-answering on the document. The first and foremost step is to extract embeddings of the full document. It’s from here that all the problems related to text processing begin.

1. When you extract embeddings for an entire document at once, you may capture the overall context, but you risk losing valuable information about specific topics. This can lead to imprecise results and missing details when working with large language models (LLMs).
2. Regardless of the embedding model provider, you need to be aware of their context window limit, to pick the right chunk size. Although OpenAI GPT-4 has a 32K token window, which sounds reasonably large, it’s still a good practice to think about the right chunk size from the outset.

Not using text chunking correctly when it’s needed can cause problems that impact retrieval quality, which further affects the downstream task. If the chunk size is too large, the relevant piece of information in the retrieved chunk may be buried under a mountain of other irrelevant text. If the chunk size is too small, it can scatter the relevant information across several pieces of retrieved information, in a way that order isn’t preserved (which affects semantics).

## Text Chunking Strategies

There are different Text Chunking Strategies, Here we’ll discuss them with their strengths and weaknesses and the right scenarios where they can be applied.

### Sentence Splitting Using Classical Methods

#### 1. Naive method

The most naive method of sentence splitting is using a *split function* that splits text on a given character.

```
text = "content.of.document." #input text
chunks = text.split(".")
print(chunks)
```

This gives:

```
['content', 'of', 'document', '']
```

#### 2. NLTK text splitter

NLTK is a library used for working with Language data. It provides a sentence tokenizer that can split the text into sentences, helping to create more meaningful chunks.

```
import nltk

input_text ="Much of refactoring is devoted to correctly composing methods. In most cases, excessively long methods are the root of all evil. The vagaries of code inside these methods conceal the execution logic and make the method extremely hard to understand"

sentences = nltk.sent_tokenize(input_text)
print(sentences)
```

Here, we have not used any character to split sentences. Further, many other chunking techniques can be used, like tokenizing, POS tagging, etc.

Output:

```
['Much of refactoring is devoted to correctly composing methods.',
    'In most cases, excessively long methods are the root of all evil.',
    'The vagaries of code inside these methods conceal the execution logic and make the method extremely hard to understand']
```

#### 3. SpaCy text splitter

spaCy is a popular NLP library is used for performing various tasks of NLP. The text splitter in spaCy creates text splits, preserving contexts of resultant splits.

```
import spacy
input_text ="Much of refactoring is devoted to correctly composing methods. In most cases, excessively long methods are the root of all evil. The vagaries of code inside these methods conceal the execution logic and make the method extremely hard to understand"

nlp = spacy.load("en_core_web_sm")
doc = nlp(input_text)
for s in doc.sents:
    print(s)
```

Output:

```
Much of refactoring is devoted to correctly composing methods.
In most cases, excessively long methods are the root of all evil.
The vagaries of code inside these methods conceal the execution logic and make the method extremely hard to understand
```

spaCy uses tokenization and a dependency parser under the hood and offers more sophisticated techniques for detecting sentence boundaries for splitting.

### Recursive Splitting

Recursive Splitting splits the input text into small chunks in iterative matter using a set of separators. If, in the starting steps, chunks are not created of the desired size, it will recursively try different separators or criteria to achieve the desired size of the chunk.

Here is an example of using Recursive Splitting using LangChain.

```
# input text
input_text ="Much of refactoring is devoted to correctly composing methods. In most cases, excessively long methods are the root of all evil. The vagaries of code inside these methods conceal the execution logic and make the method extremely hard to understand"

from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 100, #set desired text size
    chunk_overlap  = 20 )

chunks = text_splitter.create_documents([input_text])
print(chunks)
```

Output:

```
[Document(page_content='Much of refactoring is devoted to correctly composing methods. In most cases, excessively long'),
Document(page_content='excessively long methods are the root of all evil. The vagaries of code inside these methods'),
Document(page_content='these methods conceal the execution logic and make the method extremely hard to understand')]
```

### Specialized Structured Splitting

#### 1. HTML Text Splitter

HTML Splitter is a *structure-aware* chunker that splits text at the HTML element level and adds metadata for each header relevant to any given chunk.

Given this input HTML string:

```
html_string ="""
<!DOCTYPE html>
<html>
<body>
    <div>
        <h1>Foo</h1>
        <p>Some intro text about Foo.</p>
        <div>
            <h2>Bar main section</h2>
            <p>Some intro text about Bar.</p>
            <h3>Bar subsection 1</h3>
            <p>Some text about the first subtopic of Bar.</p>
            <h3>Bar subsection 2</h3>
            <p>Some text about the second subtopic of Bar.</p>
        </div>
        <div>
            <h2>Baz</h2>
            <p>Some text about Baz</p>
        </div>
        <br>
        <p>Some concluding text about Foo</p>
    </div>
</body>
</html>
"""
```

We can process it as follows:

```
from langchain.text_splitter import HTMLHeaderTextSplitter

headers_to_split_on = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
    ("h3", "Header 3"),
]

html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

html_header_splits = html_splitter.split_text(html_string)
print(html_header_split)
```

The HTML header will extract only the headers mentioned in *header\_to\_split\_on*.

```
[Document(page_content='Foo'),
Document(page_content='Some intro text about Foo.  \nBar main section Bar subsection 1 Bar subsection 2', metadata={'Header 1': 'Foo'}),
Document(page_content='Some intro text about Bar.', metadata={'Header 1': 'Foo', 'Header 2': 'Bar main section'}),
Document(page_content='Some text about the first subtopic of Bar.', metadata={'Header 1': 'Foo', 'Header 2': 'Bar main section', 'Header 3': 'Bar subsection 1'}),
Document(page_content='Some text about the second subtopic of Bar.', metadata={'Header 1': 'Foo', 'Header 2': 'Bar main section', 'Header 3': 'Bar subsection 2'}),
Document(page_content='Baz', metadata={'Header 1': 'Foo'}),
Document(page_content='Some text about Baz', metadata={'Header 1': 'Foo', 'Header 2': 'Baz'}),
Document(page_content='Some concluding text about Foo', metadata={'Header 1': 'Foo'})]
```

#### 2. Markdown text splitting

Markdown Splitting is used to chunk based on Markdown syntax like heading, bash code, images, and lists. It can also structure-aware chunker.

```
#input markdown string
markdown_text = '# Foo\n\n ## Bar\n\nHi this is Jim  \nHi this is Joe\n\n ## Baz\n\n Hi this is Molly'

from langchain.text_splitter import MarkdownHeaderTextSplitter
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
md_header_splits = markdown_splitter.split_text(markdown_text)
print(md_header_splits)
```

`MarkdownHeaderTextSplitter` splits markdown text based on *headers\_to\_split\_on*.

Output:

```
[Document(page_content='Hi this is Jim\nHi this is Joe', metadata={'Header 1': 'Foo', 'Header 2': 'Bar'}),
Document(page_content='Hi this is Molly', metadata={'Header 1': 'Foo', 'Header 2': 'Baz'})]
```

#### 3. LaTex text splitting

LaTex text splitting is another *code-splitting* chunker that parses LaTex commands to create chunks that are the logical organization, like sections and subsections, leading to more accurate and contextually relevant results.

```
#input latex string
latex_text = """
\documentclass{article}

\begin{document}

\maketitle

\section{Introduction}
Large language models (LLMs) are a type of machine learning model that can be trained on vast amounts of text data to generate human-like language. In recent years, LLMs have made significant advances in a variety of natural language processing tasks, including language translation, text generation, and sentiment analysis.

\subsection{History of LLMs}
The earliest LLMs were developed in the 1980s and 1990s, but they were limited by the amount of data that could be processed and the computational power available at the time. In the past decade, however, advances in hardware and software have made it possible to train LLMs on massive datasets, leading to significant improvements in performance.

\subsection{Applications of LLMs}
LLMs have many applications in industry, including chatbots, content creation, and virtual assistants. They can also be used in academia for research in linguistics, psychology, and computational linguistics.

\end{document}
"""

from langchain.text_splitter import LatexTextSplitter
latex_splitter = LatexTextSplitter(chunk_size=100, chunk_overlap=0)

latex_splits = latex_splitter.create_documents([latex_text])
print(latex_splits)
```

In the above example you can see that \*overlap is 0, \*it is because when we are working with code splits at that time overlapping codes totally change the meaning of it. So overlapping should be 0.

```
[Document(page_content='\\documentclass{article}\n\n\x08egin{document}\n\n\\maketitle\n\n\\section{Introduction}\nLarge language models'),
    Document(page_content='(LLMs) are a type of machine learning model that can be trained on vast amounts of text data to'),
    Document(page_content='generate human-like language. In recent years, LLMs have made significant advances in a variety of'),
    Document(page_content='natural language processing tasks, including language translation, text generation, and sentiment'),
    Document(page_content='analysis.\n\n\\subsection{History of LLMs}\nThe earliest LLMs were developed in the 1980s and 1990s,'),
    Document(page_content='but they were limited by the amount of data that could be processed and the computational power'),
    Document(page_content='available at the time. In the past decade, however, advances in hardware and software have made it'),
    Document(page_content='possible to train LLMs on massive datasets, leading to significant improvements in'),
    Document(page_content='performance.\n\n\\subsection{Applications of LLMs}\nLLMs have many applications in industry, including'),
    Document(page_content='chatbots, content creation, and virtual assistants. They can also be used in academia for research'),
    Document(page_content='in linguistics, psychology, and computational linguistics.\n\n\\end{document}')]
```

Now when you choose which chunker to use for your data, extract embeddings for them and store them in Vector DB.

In this post, we’ve seen numerous examples of using chunking with LanceDB to store text chunks and their respective embeddings. LanceDB is an easy-to-setup, open source vector database that persists your data and vector index on disk, allowing you to scale without breaking the bank. It is also well-integrated with the Python data ecosystem so you can use it with your existing data tools like pandas, pyarrow, and more.

See [this notebook](https://colab.research.google.com/github/lancedb/vectordb-recipes/blob/main/tutorials/different-types-text-chunking-in-RAG/Text_Chunking_on_RAG_application_with_LanceDB.ipynb) for the code that performs these tasks.

## Conclusion

Text chunking is a relatively straightforward task, but it’s also important to study how it works, because it presents certain challenges and tradeoffs. There’s no single strategy that works universally, nor a chunk size that suits every scenario. What works for one type of data or solution might not be suitable for others.

Hopefully, this post reinforced the importance of text chunking and showed you some new approaches!

Learn more about LanceDB or applied GenAI applications from [vectordb-recipes](https://github.com/lancedb/vectordb-recipes). Don’t forget to drop us a 🌟!

![1453-https-www-lancedb-com-blog-a-primer-on-text-chun-2216b01b-fig-002](../images/1453-https-www-lancedb-com-blog-a-primer-on-text-chun-2216b01b/figure-002.jpg)

[Prashant Kumar](/author/prashant-kumar)

![1453-https-www-lancedb-com-blog-a-primer-on-text-chun-2216b01b-fig-003](../images/1453-https-www-lancedb-com-blog-a-primer-on-text-chun-2216b01b/figure-003.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1453-https-www-lancedb-com-blog-a-primer-on-text-chun-2216b01b-fig-004](../images/1453-https-www-lancedb-com-blog-a-primer-on-text-chun-2216b01b/figure-004.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1453-https-www-lancedb-com-blog-a-primer-on-text-chun-2216b01b-fig-005](../images/1453-https-www-lancedb-com-blog-a-primer-on-text-chun-2216b01b/figure-005.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb