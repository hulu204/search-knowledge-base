---
title: 'From PDF tables to insights: An alternative approach for parsing PDFs in RAG'
company: Elastic
tag: RAG
date: 2024-10-18
url: https://www.elastic.co/search-labs/blog/alternative-approach-for-parsing-pdfs-in-rag
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# From PDF tables to insights: An alternative approach for parsing PDFs in RAG

An alternative approach to parsing PDF tables for RAG, overcoming the limitations of highly normalized formats like CSV and JSON.

October 18, 2024

[Sunile Manjee](/search-labs/author/sunile-manjee)

[AI](/search-labs/blog/category/ai)

Jump to

Share

When working with PDFs in a retrieval-augmented generation (RAG) pipeline, a key challenge is efficiently extracting and processing tables. Traditional methods often convert tables into highly normalized formats such as CSV or JSON, which fail to capture the contextual richness needed for effective search and retrieval. These representations break the data down into rows and columns, losing the broader relationships between elements. To address this, I developed a approach that leverages a large language model (LLM) to transform tables into readable text while retaining the context, enhancing the usability of the data in RAG workflows.

This article explains the reasoning behind this approach, the high-level benefits, and the key parts of the [notebook](https://github.com/elastic/elasticsearch-labs/blob/sunman/supporting-blog-content/alternative-approach-for-parsing-pdfs-in-rag/alternative-approach-for-parsing-pdfs-in-rag.ipynb).

## Why this table PDF parsing approach?

Standard table parsing techniques often fail in RAG because they produce highly normalized outputs. While CSV and JSON formats are useful for specific data analytics, they break down in scenarios where more context is needed. Retrieval-augmented generation models thrive on rich, content-heavy data, and having only single rows or minimal data points hinders effective search.

Instead of sticking with the traditional approach of exporting table data in structured formats, I opted to extract the tables, parse them using Azure OpenAI, and reformat the tables into human-readable text. This approach allows for better contextual embedding and enhances searchability without losing the richness of the data.

## Parsing challenges in PDF tables

In real-world applications, extracting structured information from PDFs often involves complex tables like the one below from Bank of America's SEC FORM 10-Q.

![Example of complex tables when extracting structured information from PDFs](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt07eb2716cae9a73c/6a17e406a2929966e3d02c0f/928434c694ec8a5f284066d600ed17739c9542c4-1384x376.jpg)

This table contains critical financial data, such as stock symbols, descriptions, and exchanges. However, parsing such tables presents multiple challenges:

### Complexity of table structure

The table includes merged cells, multi-line text, and varying formats for data types like numbers and text. This adds complexity to the parsing process as tools often struggle to identify the correct relationships between the data elements.

### Loss of context

When tables are converted to formats such as CSV or JSON, much of the relational context between the table's rows and columns is lost. For example, the relationship between the title of each class and its corresponding trading symbol may not be preserved, impacting the integrity of the extracted data.

### Handling special characters and formats

Stock symbols and series names, such as "BAC PrE" and "BAC PrL," may contain abbreviations or special characters that get misinterpreted by traditional parsing tools, leading to inaccurate data extraction.

## Addressing the challenges of parsing PDF tables in RAG

Using a large language model (LLM) approach, the tables can be transformed into readable text that retains the context of the relationships between rows and columns. This ensures that critical financial information is not lost during parsing and is fully searchable for retrieval-augmented generation (RAG) workflows.

For example, applying this method to the table above outputs the following text:

```
Table 1 (Page 1) Text Representation:
The following stocks are listed on the New York Stock Exchange:
Common Stock:
Par value: $0.01 per share
Symbol: BAC
Depositary Shares, each representing a 1/1,000th interest in a share of Floating Rate Non-Cumulative Preferred Stock, Series E:
Symbol: BAC PrE
Depositary Shares, each representing a 1/1,000th interest in a share of 6.000% Non-Cumulative Preferred Stock, Series GG:
Symbol: BAC PrB
Depositary Shares, each representing a 1/1,000th interest in a share of 5.875% Non-Cumulative Preferred Stock, Series HH:
Symbol: BAC PrK
7.25% Non-Cumulative Perpetual Convertible Preferred Stock, Series L:
Symbol: BAC PrL
Depositary Shares, each representing a 1/1,200th interest in a share of Bank of America Corporation Floating Rate Non-Cumulative Preferred Stock, Series 1:
Symbol: BML PrG
```

## The benefits

1. **Improved** **searchability**: Embedding text instead of highly structured table data ensures that RAG models can capture the relationships and broader context of the content, making it easier to retrieve accurate results.
2. **Preservation** **of** **context**: By converting tables into human-readable descriptions, we preserve the intent and structure of the original data, which is essential for RAG workflows where the document's meaning is crucial.
3. **Handling unstructured data**: This method handles the natural unstructured nature of PDFs better than simple table extraction, making it more versatile in real-world applications.
4. **Readable output**: Rather than dealing with abstract, normalized data, the final output is in a format that is easier for both humans and machines to interpret.

![PDF table architecture dectected](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd725fa15fd807b74/6a17e4077f6f1561b8c09aaa/2422b4542b7c19f2a801345a41c7cc1707027152-1440x892.png)

## Key code explanation

### 1. Extracting text and tables from PDFs

The first step in the process uses the `pdfplumber` library to extract both text and tables from each page of the PDF.

```
import pdfplumber

# Open the PDF and extract pages
with pdfplumber.open('path_to_pdf.pdf') as pdf:
    for page in pdf.pages:
        text = page.extract_text()  # Extract plain text
        tables = page.extract_tables()  # Extract tables
```

Here, `pdfplumber` is utilized to extract both plain text and tables from each page of the PDF. It provides a flexible way to handle PDFs and their internal structure.

### 2. Cleaning and sending tables to Azure OpenAI

After extracting the tables, the script sends a cleaned version of the table data to Azure OpenAI for transformation into readable text. This allows the LLM to create a natural language summary of the table.

```
def process_table_with_llm(table):
    # Clean the table for missing values and prepare the input
    cleaned_table = [row for row in table if row]

    # Sending to Azure OpenAI for text generation
    prompt = f"Convert the following table into a readable text:
{cleaned_table}"
    response = azure_openai.generate_text(prompt)
    return response['generated_text']
```

The tables are cleaned to handle missing or `None` values and are then passed to Azure OpenAI, which generates a textual description of the table's contents. This helps retain the table's context in the final output.

### 3. Writing the final output

Once the text has been generated from the tables and the non-table text has been extracted, everything is written into a single output file. This ensures that both text and table data are available for downstream tasks like search and retrieval.

```
with open('output_text_file.txt', 'w') as output_file:
    output_file.write(text)  # Write non-table text
    output_file.write('\n\n--- Table Summary ---\n')
    output_file.write(table_summary)  # Write table summary from Azure OpenAI
```

By embedding the table summaries alongside the rest of the text, we provide a comprehensive output that is ready for use in RAG applications, ensuring all information from the PDF is preserved in a human-readable format.

## Conclusion

By using an LLM to transform tables into readable text and embedding that text back into the original content, this approach significantly enhances the usability of PDF tables in retrieval-augmented generation workflows. It preserves context, improves searchability, and ensures that no valuable information is lost in the normalization process. This method offers a more comprehensive solution for those working with PDF-based data in RAG applications.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbca7a25e3c272aa8/6a17ffb1be60868d100049d2/6494d88d51edf6a5b31a92b8439792354eae7190-1536x1024.png)

[ES|QL](/search-labs/blog/category/esql)[AI](/search-labs/blog/category/ai)

### Using ES|QL COMPLETION + an LLM to write a Chuck Norris fact generator in 5 minutes

August 28, 2025|[Aurélien Foucret](/search-labs/author/aurelien-foucret)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blta9f7119562f10d5a/6a17f5507f6f151debc09ca3/f10a706b66a83e9df451ece25326cbcd10134e3c-721x420.jpg)

[AI](/search-labs/blog/category/ai)

### Generative AI using Elastic and Amazon SageMaker JumpStart

July 25, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5cd8853e995046c9/6a17e7872f4a5c03b6fa88f6/52748b9e2f082718804ed9c0d8f4272f4e4f893a-1024x1024.jpg)

[AI](/search-labs/blog/category/ai)

### Retrieval Augmented Generation (RAG) using Cohere Command model through Amazon Bedrock and domain data in Elasticsearch

November 23, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt576d87464937da1e/6a17f30e0b0bed0469dd36b1/7086754859ba2cbbaf673c843013462892738c30-720x420.jpg)

[AI](/search-labs/blog/category/ai)

### Transforming data interaction: Deploying Elastic’s MCP server on Amazon Bedrock AgentCore Runtime for crafting agentic AI applications

September 04, 2025|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter