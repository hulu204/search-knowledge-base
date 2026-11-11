---
title: 'GraphRAG: Hierarchical Approach to Retrieval-Augmented Generation'
company: LanceDB
tag: RAG
date: 2024-03-25
url: https://www.lancedb.com/blog/graphrag-hierarchical-approach-to-retrieval-augmented-generation
account: 
origin: harvest3-202607
---
# GraphRAG: Hierarchical Approach to Retrieval-Augmented Generation

[Akash Desai](/author/akash-desai)

•

March 25, 2024

•

[Engineering](/category/engineering)

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69ca20f2e6680f810e8957f4_graphrag-hierarchical-approach-to-retrieval-augmented-generation.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

## What is RAG?

**Retrieval-Augmented Generation (RAG)** is an architecture that combines traditional information retrieval systems with large language models (LLMs). By integrating external knowledge sources, RAG enhances generative AI capabilities, allowing it to provide responses that are not only more accurate and relevant but also up to date.

## How Does Retrieval-Augmented Generation (RAG) Work?

RAG operates through a few key steps to enhance the performance of generative AI:

1. **Retrieval and Pre-processing:** RAG employs advanced search algorithms to access external data from sources such as websites, knowledge bases, and databases. The retrieved information is then pre-processed — cleaned, tokenized, and filtered — to ensure it’s ready for use.
2. **Generation:** The pre-processed data is integrated into the pre-trained LLM, enriching its context. This integration allows the LLM to generate responses that are more accurate, relevant, and informative.

These steps work together to make RAG a powerful tool for generating high-quality responses based on real-time information.

## Why Use RAG?

Retrieval-Augmented Generation (RAG) offers a range of compelling advantages over traditional text generation methods, making it particularly valuable in contexts where accuracy and relevance are paramount: are essential:

* **Access to Real-Time Data:** RAG ensures that responses are always up to date by seamlessly pulling in the latest information from diverse sources, allowing users to receive timely insights.
* **Guaranteed Accuracy:** It relies on verified sources to maintain factual correctness, building user trust.
* **Contextual Precision:** RAG customizes responses to align with the specific context of each query, enhancing relevance.
* **Consistency:** By grounding answers in accurate data, RAG minimizes contradictions and ensures reliability.
* **Efficient Retrieval:** Advanced vector databases allow RAG to quickly locate relevant documents, streamlining information access.
* **Enhanced Chatbots:** Integrating external knowledge elevates chatbot performance, providing more comprehensive and context-aware responses.

### Limitations of Baseline RAG

While RAG was designed to address various challenges in information retrieval and generation, its basic form has limitations in certain scenarios:

* **Difficulty in Connecting Information:** Baseline RAG often struggles with questions that require synthesizing disparate pieces of information into a cohesive answer, making it less effective for complex queries.
* **Challenges with Big Picture Understanding:** It has difficulty comprehensively understanding and summarizing large datasets or documents, which can hinder its ability to provide holistic insights.

This highlights the **need for advancements** in RAG to overcome these challenges and improve its overall effectiveness.

To overcome the limitations of baseline RAG, **Microsoft Research** introduced [**GraphRAG**](https://github.com/microsoft/graphrag). This method enhances the traditional RAG framework by constructing a dynamic knowledge graph from a given dataset. This graph serves as a structured representation of information, capturing not only the data itself but also the relationships and context between different pieces of information.

GraphRAG significantly enhances the ability to answer complex questions by effectively synthesizing and reasoning over diverse information, surpassing the performance of traditional methods.

## The GraphRAG Process 🤖

**GraphRAG** is an advanced iteration of RAG that leverages knowledge graphs to enhance both the retrieval and generation processes. By structuring data hierarchically, GraphRAG enables more effective reasoning over complex queries, which leads to improved accuracy and a deeper contextual understanding of responses. This structured approach allows the system to connect related information and deliver insights that are not only relevant but also nuanced.

### How GraphRAG Solves RAG Problems

GraphRAG effectively addresses the limitations of traditional RAG by introducing a structured approach to information retrieval. It constructs a dynamic knowledge graph from raw text, capturing essential entities, relationships, and key claims within the data. This structured representation allows GraphRAG to reason over multiple connections, enabling it to synthesize information more effectively. As a result, GraphRAG provides more accurate and comprehensive answers to complex queries, overcoming the challenges faced by baseline RAG in understanding intricate relationships among data points.

### How GraphRAG Works

**Indexing:** Raw text is divided into **TextUnits**, which are analyzed to extract entities and relationships. These **TextUnits** form the foundational elements for subsequent processing.

**Graph Construction:** Following indexing, a **knowledge graph** is created, organizing entities and relationships hierarchically. This graph is refined through hierarchical clustering using the **Leiden technique**, which groups related entities into communities. This approach aids in visualizing and understanding complex datasets holistically.

**Query Processing:** When a query is made, GraphRAG leverages the knowledge graph to retrieve relevant information through two primary modes:

* **Global Search:** This mode utilizes community summaries to provide answers to broad, holistic questions about the dataset, offering a comprehensive overview.
* **Local Search:** This mode concentrates on specific entities, exploring their neighbors and related concepts to facilitate detailed reasoning and more precise answers. It uses LanceDB as the default vector database for performing vector search to retrieve relevant entities.

We are going to see both in practice.

**LLM Integration:** After retrieving relevant data from the knowledge graph, it is fed into a large language model (LLM). The LLM generates coherent and contextually relevant responses by leveraging the structured knowledge, allowing it to address complex queries with precision.

**Prompt Tuning:** To achieve the best results with GraphRAG, it’s recommended to fine-tune your prompts according to the guidelines provided in the Prompt Tuning Guide. This step ensures that the model is optimally tailored to your specific data and query needs.

### When to Use GraphRAG

**Complex Queries:** Ideal for scenarios where answers require reasoning across multiple steps or connections within the data.

**If High Precision Needed:** Essential in situations where factual accuracy is critical, such as in legal or scientific contexts.

**Large-Scale Knowledge Bases:** Perfect for managing and querying extensive, interconnected datasets efficiently.

**Dynamic Information:** Best suited for environments where data is frequently updated or constantly evolving.

## Example

In this section, we will walk through the practical steps of implementing RAG

```
import bs4
from langchain import hub
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import LanceDB
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from lancedb.rerankers import LinearCombinationReranker

# Load the text document
loader = TextLoader("/content/HTE_gst_scheme.txt")
documents = loader.load()

# Split the loaded documents into manageable chunks using RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1100, chunk_overlap=100)
splits = text_splitter.split_documents(documents)

# Initialize the reranker and create a vector store with the document splits
reranker = LinearCombinationReranker(weight=0.3)
vectorstore = LanceDB.from_documents(documents=splits, embedding=OpenAIEmbeddings(), reranker=reranker)

# Set up the retriever to fetch relevant snippets from the vector store
retriever = vectorstore.as_retriever()
prompt = hub.pull("rlm/rag-prompt")

# Function to format the retrieved documents for output
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Initialize the language model for response generation
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Create the RAG chain to process the query with the context and question
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Invoke the RAG chain with a specific query and print the response
query = "tell me how to do export"
response = rag_chain.invoke(query)
print(response)
```

```
To export, one must first decide on the mode of shipping and choose an ocean freight forwarder. It is important to arrange for a customs clearance agent to ensure compliance with export processes. Quality control and meeting buyer's requirements are crucial steps in the export process.
```

## Implementing GraphRAG

To get started with GraphRAG, follow these steps:

### Step 1: Install GraphRAG

Begin by installing the GraphRAG package using the following command:

```
!pip install graphrag
```

### Step 2: Prepare Your Dataset

1. **Create and Organize Your Dataset** Start by creating your dataset and saving it in the following directory: **`/content/rag_exim/input/info.txt`**
2. **Supported File Types** Currently, GraphRAG supports only **`.txt`** and **`.csv`** file formats. If you need to add support for CSV files, you’ll need to modify the **`settings.yml`** file accordingly to include the necessary configurations.
3. **Download and Format Your Data** Ensure that your dataset is properly downloaded and formatted for seamless processing by GraphRAG.

### Step 3: Initialize the Dataset for Indexing

To set up the initial structure for indexing your dataset, use the following command:

```
!python3 -m graphrag.index --init --root /content/rag_exim
```

### Step 4: Index the Dataset

To index your dataset, use the following command:

```
!python3 -m graphrag.index --root /content/rag_exim
```

### Step 5: Execute the Query

As we said, we have two options for executing queries in GraphRAG: **global** and **local query execution**.

#### Global Query Execution

To perform a global query, use the following command:

```
!python3 -m graphrag.query --root /content/rag_exim --method global "tell me how to do export?"
```

Using the global query method allows you to gain comprehensive insights and overarching themes from your dataset. After executing this command, review the output to see the responses generated by GraphRAG.

**Output:**

```
SUCCESS: Global Search Response: To successfully engage in exporting goods from India, businesses must navigate a series of regulatory, financial, and logistical steps designed to ensure compliance with both national and international standards. The process is multifaceted, involving the acquisition of necessary codes, compliance with legal requirements, financial planning, and the strategic use of available schemes to enhance competitiveness.

### Obtaining Necessary Codes and Compliance

First and foremost, obtaining an Importer-Exporter Code (IEC) from the Directorate General of Foreign Trade (DGFT) is mandatory for all entities engaged in import or export in India. This code is a fundamental requirement and serves as a primary identifier for businesses in the international trade arena [Data: Reports (40, 43)].

### Regulatory Compliance and Customs Clearance

Ensuring compliance with regulatory requirements is crucial. This includes adherence to the Goods and Services Tax (GST) regulations, fumigation, phyto-sanitary measures, and the Foreign Trade Policy (FTP). The FTP outlines legal and procedural guidelines critical for exports and imports, making understanding these regulations essential for smooth operations [Data: Reports (32, 27)].

The export goods must meet all required safety and legal standards, which is verified through a mandatory Export Customs Clearance process. This involves inspection and approval by customs agents to ensure that shipments comply with all legal and safety requirements before leaving the country. Engaging a Customs Broker can significantly manage this process, acting as an intermediary between the business and customs authorities [Data: Reports (35)].

### Financial Planning and Support Mechanisms

Financial planning is another critical aspect of the export process. Leveraging financial support mechanisms such as Post Shipment Finance and Packing Credit from commercial banks can meet working capital requirements for fulfilling export transactions. Additionally, schemes like the Advance Authorisation Scheme allow for duty-free import of inputs used in export production, reducing costs and enhancing competitiveness [Data: Reports (27, 17)].

### Leveraging Schemes and Certifications

Businesses should also consider collaborating with Export Oriented Units (EOUs) and Special Economic Zones (SEZs) for benefits such as exemptions on GST and customs duties. Obtaining certifications from the Export Inspection Council of India (EIC) can enhance product competitiveness and consumer trust in international markets. Utilizing schemes like the Export Promotion Capital Goods (EPCG) scheme enables the import of capital goods at zero customs duty, further reducing the cost of acquiring new technology and equipment for export production [Data: Reports (31, 21, 26)].

### Conclusion

In summary, exporting from India requires meticulous planning and adherence to a range of regulatory, financial, and logistical requirements. By obtaining the necessary codes, ensuring regulatory compliance, engaging in financial planning, and leveraging available schemes and certifications, businesses can navigate the complexities of international trade more effectively. This comprehensive approach not only ensures compliance with national and international standards but also enhances the competitiveness of Indian exports in the global market [Data: Reports (40, 43, 35, 32, 27, 17, 31, 21, 26, +more)].
```

Onceyou are familiar with global queries, you can also explore local query execution for more specific inquiries.

#### Local Query Execution

To perform a local query, use the following command:

```
!python3 -m graphrag.query --root /content/rag_exim --method local "tell me how to do export?"
```

Using the local query method allows you to drill down into specific details and obtain precise answers based on the context of the entities involved. After executing this command, review the output to see the responses generated by GraphRAG for your local query.

**Output:**

```
SUCCESS: Local Search Response: Exporting goods from India involves a comprehensive process that includes understanding legal requirements, obtaining necessary documentation, and ensuring compliance with both Indian and international trade regulations. Here's a detailed guide on how to export from India, based on the information provided in the data tables:

### 1. Understand Export Regulations and Policies

Firstly, familiarize yourself with India's export regulations and policies. The Foreign Trade Policy (FTP) outlines the legal and procedural guidelines for exports and imports in India. It's crucial to understand the FTP's provisions, as it regulates the trade environment [Data: Entities (85)].

### 2. Obtain Necessary Documentation

Exporters must prepare and obtain several key documents to comply with both Indian and international regulations:

- **Bill of Lading/Airway Bill**: Acts as a contract and receipt between the shipper and the carrier [Data: Sources (11)].
- **Commercial Invoice cum Packing List**: Merges two essential documents into one, detailing the product and its destination [Data: Sources (11)].
- **Shipping Bill/Bill of Export**: Required for customs clearance, issued by Indian Customs Electronic Gateway (ICEGATE) [Data: Sources (11)].
- **Certificate of Origin**: Indicates the country where the goods were manufactured [Data: Sources (11)].
- **Export License/IEC (Import-Export Code)**: Necessary for all exporters; it's a unique code issued by the DGFT [Data: Sources (11)].

### 3. Packaging and Labeling

Proper packaging and labeling are critical to ensure that goods are protected during transit and comply with international standards. Packaging should protect against breakage, moisture, and other risks, while labeling should provide essential information like contents, destination, and handling instructions [Data: Sources (11)].

### 4. Financial and Banking Arrangements

Exporters need to secure financing for their export operations. This can include obtaining pre-shipment and post-shipment finance from commercial banks at concessional rates. It's also important to present the export documents to the bank within 21 days for payment processing [Data: Sources (11)].

### 5. Engage with Export Promotion Councils and Authorities

Export Promotion Councils (EPCs) and authorities like the Agricultural and Processed Food Products Export Development Authority (APEDA) play a significant role in supporting exporters. They offer workshops, advice, and financial guidance to enhance global market contributions [Data: Entities (87), Relationships (108, 112, 144)].

### 6. Compliance with Export Obligations

Certain schemes, like the Advance Authorisation Scheme, require exporters to fulfill specific export obligations within a stipulated period. Understanding and complying with these obligations is crucial for exporters to benefit from such schemes [Data: Relationships (294)].

### 7. Utilize E-Commerce Platforms

For exporters focusing on goods and services sold via the internet, it's essential to comply with the regulatory framework provided by the DGFT and RBI. This includes ensuring that payment channels are authorized and meet the guidelines specified by the RBI [Data: Relationships (69, 176)].

### Conclusion

Exporting from India requires careful planning and adherence to a range of regulatory requirements. By following the steps outlined above and leveraging the support available from government and trade bodies, exporters can successfully navigate the complexities of international trade.
```

You can explore all the source code in our shared Colab notebook, available [here](https://colab.research.google.com/drive/14xuJ9dbdCEILRSg74fOHJijS699JW-J1?usp=sharing).

## Conclusion

GraphRAG provides significant advantages in generating deeper insights by utilizing graph nodes for complex reasoning, an area where traditional retrieval-augmented generation (RAG) may face limitations. However, this added depth comes with higher computational costs, as GraphRAG requires multiple calls to large language models (LLMs), leading to increased token usage.

Both GraphRAG and traditional RAG possess distinct strengths and trade-offs, making them suitable for different scenarios. For instance, GraphRAG shines when tackling complex, multi-step queries that demand a thorough understanding of context and relationships, while traditional RAG tends to be more efficient for straightforward tasks that require quick and direct answers.

To optimize performance and mitigate costs, various strategies can be employed. For GraphRAG, leveraging a local LLaMA model can be a promising alternative, potentially reducing dependency on cloud-based services. Meanwhile, traditional RAG can be enhanced through a range of optimization techniques. Ultimately, the optimal approach will depend on your specific use case and the empirical results of your experiments

For more information on optimizing both methods, check out our [vector recipe](https://github.com/lancedb/vectordb-recipes) repository for detailed techniques.

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c2da55256db3a1ce1175fc_lancedb.jpeg)

[Akash Desai](/author/akash-desai)

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/6a567183dd1ae093c21b81d5_opt3.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/6a50fef0022a597f28313428_hero%20img.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/6a510da7aa738b84d6e9c040_preview-image.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb