---
title: 'The Future of Open Source Table Formats: Apache Iceberg and Lance'
company: LanceDB
tag: 工程相关
date: 2025-04-08
url: https://www.lancedb.com/blog/the-future-of-open-source-table-formats-iceberg-and-lance
account: 
origin: harvest3-202607
---
# The Future of Open Source Table Formats: Apache Iceberg and Lance

[Jack Ye](/author/jack-ye)

•

April 8, 2025

•

[Engineering](/category/engineering)

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c71f91174468e25f1841f0_the-future-of-open-source-table-formats-iceberg-and-lance.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

As the scale of data continues to grow, open-source table formats have become essential for efficient data lake management. Apache Iceberg has emerged as a leader in this space, while new formats like [Lance](https://github.com/lance-format/lance) are introducing optimizations for specific workloads. In this post, we’ll explore how Iceberg and Lance address different challenges and complement each other in the evolving landscape of data lake table formats.

## **The Rise of Open Source Table Formats**

Table formats like Apache Iceberg, Delta Lake, and Apache Hudi were designed to address the challenges of managing large-scale structured data in cloud storage. These formats brought capabilities like ACID transactions, schema evolution, and time travel, making data lakes more reliable and performant. Among them, Iceberg gained significant traction through widespread adoption in the open-source ecosystem and strong integration into commercial vendor products. Its architecture enables scalable and performant query execution while allowing flexible integration into existing data lake infrastructure.

## **Considerations for Apache Iceberg**

Iceberg is a major advancement over traditional approaches, but it has some challenges to consider:

1. **Metadata Overhead**: Iceberg’s metadata management relies on maintaining manifest lists and metadata trees, which can become a bottleneck as datasets grow. Querying data in Iceberg requires multiple hops before accessing the actual data: first, the catalog lookup, then fetching the metadata file (if you are not using REST catalog), followed by retrieving the manifest list, and finally loading the manifest file before reading the data itself. This multi-step process can introduce latency, especially for highly transactional workloads.
2. **Limited Multimodal Support**: Iceberg is built primarily for structured, tabular data and lacks native support for complex data types such as images, videos, audio, and vector embeddings. These types are becoming increasingly important in AI and ML workflows. While it’s possible to reference such data externally (e.g., via paths or object URIs) or store it as binary type, Iceberg does not natively handle or optimize storage and access for these data types, limiting its effectiveness in modern, multimodal machine learning pipelines.
3. **Lack of Efficient Random Access**: Iceberg is optimized for large-scale analytical SQL queries, where scan-based access patterns are common. However, it lacks native support for low-latency random access, which is critical for many machine learning scenarios. ML workflows often require retrieving a small number of records or specific features repeatedly—for example, during training, inference, or feature lookups—operations that are relatively inefficient with Iceberg’s current design. Although features like Parquet bloom filters can help reduce the scan range in some cases, they are not sufficient for true fine-grained, high-performance random access.
4. **Lack of Efficient Column Appends**: Iceberg with its currently supported file formats cannot append new column data to an existing table without rewriting the entire data file. Consider a common ML pipeline where one team produces a source dataset and multiple feature extraction teams append new feature columns to the dataset over time. Iceberg would result in significant inefficiencies when used in such a pipeline because a full table rewrite is required every time some new features are developed and need to be appended to the table as new columns.

## **How Lance Complements Iceberg**

Lance is an emerging open-source table format that focuses on optimizing for modern data applications, particularly AI and ML workloads. Rather than replacing Iceberg, Lance provides capabilities that are well-suited for specific use cases.

1. **Metadata Efficiency**: Instead of maintaining multiple metadata layers, Lance embeds efficient indexing structures within the table to reduce metadata overhead. This design minimizes lookup time and simplifies metadata synchronization, which is particularly beneficial in high-ingest or frequently updated environments. By storing metadata alongside the data in a unified format, Lance streamlines query planning and execution, resulting in lower latency and more predictable performance for ML and AI pipelines.
2. **Multimodal Data Support**: Unlike traditional table formats, Lance is built to efficiently store and query multimodal data, including text, images, audio, video, and vector embeddings. This capability is critical for AI-driven applications, where models often rely on a combination of structured and unstructured data. Lance supports native storage and access patterns for these data types, enabling seamless integration into machine learning workflows without requiring external storage systems or complex workarounds. For example, Lance can directly store image tensors and associate them with structured metadata or text captions in the same table. This simplifies the development of use cases like image classification, video analysis, recommendation systems, and semantic search, where multimodal data is core to the application logic. As a result, Lance empowers AI-driven applications to operate on fully integrated datasets—structured and unstructured alike—within a unified, high-performance framework that accelerates development and deployment of complex, multimodal models.
3. **Efficient Random Access**: Lance moves beyond Parquet by using a custom columnar format specifically designed for low-latency random access. On top of that, the Lance also supports a variety of secondary indexing techniques such as B-trees, bitmap indexes, n-gram indices, vector indexes, and full-text search, enabling highly efficient lookups and query acceleration. This makes Lance ideal for machine learning workloads that require fast retrieval of individual rows or columns—such as during training, inference, or feature lookups—without scanning large portions of the dataset. The format’s ability to support targeted access patterns makes it a strong fit for real-time and interactive AI and ML workflows.
4. **Efficient Column Appends**: Lance allows for appending new column data without rewriting the entire dataset, making schema evolution with backfill more efficient and reducing unnecessary I/O costs. It achieves this by expressing tables as a series of fragments, where each fragment contains multiple files that can contain data for a subset of columns. This architecture enables targeted updates and efficient storage of newly added columns, as backfilling data in a new column for existing fragments is as simple as adding new data files, avoiding the need to rewrite existing data files. This design makes Lance particularly well-suited for collaborative machine learning environments, where teams need to incrementally evolve feature sets without incurring the cost of full table rewrites.

## **The Future of Open Source Table Formats**

The future of data lake table formats will likely be shaped by the evolving needs of AI, real-time analytics, and efficient storage management. Iceberg is well-positioned as a **standard for data exchange**, given its broad adoption and integration into major query engines. We have already seen projects like Apache XTable and Delta Lake Uniform that enable users to use other open table formats while synchronizing to Apache Iceberg. Products like Amazon SageMaker Lakehouse has also proven the possibility of runtime metadata translation to present proprietary table formats like Amazon Redshift in the shape of Iceberg metadata through the Iceberg REST catalog interface. Overall, Apache Iceberg’s strong support for analytical workloads and enterprise data lake environments makes it a foundational format for interoperability.

Lance, on the other hand, is emerging as the **format for ML and AI**, where low-latency access, high-performance random access, and efficient column updates are critical. As organizations move toward hybrid analytics and machine learning-driven architectures, the demand for high-performance, scalable, and AI-native table formats will grow. We see a wave of AI-native data coming—multimodal, unstructured, constantly evolving—and bringing with it a new set of challenges that traditional data infrastructure is not built to handle. Current generation table formats like Iceberg, Delta Lake, and Apache Hudi have served the analytics ecosystem well, but they are not optimized for this new frontier. That’s why we believe this space is ripe for innovation. It’s an exciting opportunity to reimagine data infrastructure purpose-built for the future of AI, and we expect to see rapid evolution in how data is stored, queried, and shared in AI-centric environments.

Rather than competing, these formats can **coexist and serve complementary roles** in the modern data ecosystem, allowing organizations to optimize their data strategies based on workload-specific needs. We are excited to see collaborative developments such as Iceberg’s pluggable DataFile reader and writer API, which opens the door for querying Lance-formatted data through the Iceberg interface. This kind of interoperability reinforces the vision that table formats can work together to serve diverse workloads. We will also continue to evolve the Lance table format for ML and AI use cases, ensuring it meets the unique demands of these rapidly advancing domains.

What are your thoughts on the future of open-source table formats? Let’s [discuss](https://discord.gg/RRgWXFTSCs)!

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c2da56256db3a1ce117613_jack-ye.avif)

[Jack Ye](/author/jack-ye)

Data engineer and table format specialist, working on distributed systems and modern data lake architectures.

[GitHub](https://github.com/jackye1995)[Linkedin](https://www.linkedin.com/in/yezhaoqin/)

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