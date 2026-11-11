---
title: 'Efficient bitwise matching in Elasticsearch'
company: Elastic
tag: 召回
date: 2024-10-21
url: https://www.elastic.co/search-labs/blog/efficient-bitwise-matching-in-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Efficient bitwise matching in Elasticsearch

Explore six approaches to encoding and matching binary data in Elasticsearch, including terms encoding (my preferred approach), boolean encoding, sparse bit position encoding, integer encoding with exact matching, integer encoding with scripted bitwise matching, and integer encoding with ESQL for bitwise matching, with practical examples and use cases.

October 21, 2024

[Alexander Marquardt](/search-labs/author/alexander-marquardt)

[Basics](/search-labs/blog/category/basics)

Jump to

Share

## Introduction to binary encoding andbitwise matching

Binary encoding is an important technique in modern applications, especially in areas like IoT device monitoring, where vast amounts of binary sensor data or operational flags are continuously processed. Efficiently managing and searching through such data is essential for real-time analytics and decision-making. To achieve this, bitwise matching is a powerful tool for filtering based on binary values, allowing for precise data extraction. With the right data modeling, Elasticsearch not only supports bitwise matching but can do so with high performance.

At the time of writing this article, Elasticsearch [doesn’t have a native operator for bitwise matching](https://github.com/elastic/elasticsearch/issues/975), and [Lucene doesn’t directly support bitwise matching](https://issues.apache.org/jira/browse/LUCENE-2460). To overcome this limitation, this article presents six approaches for binary encoding and bitwise matching in Elasticsearch: terms encoding (my preferred approach), boolean encoding, sparse bit position encoding, integer encoding with exact matching, integer encoding with scripted bitwise matching, and integer encoding with ESQL for bitwise matching.

## Terms encoding

Using terms for binary representation leverages Elasticsearch’s optimized term-based queries. This method involves representing each bit as a term which is stored in a keyword field.

### Advantages of terms encoding

The terms-based approach allows for Elasticsearch to make use of optimized data structures, resulting in efficient querying even for large datasets. Additionally, this method scales well in situations where different combinations of bits need to be queried frequently, as each bit is treated as an independent entity that can be indexed and searched.

### Disadvantages of terms encoding

This method requires that data is pre-processed to get it into the terms encoding format before storing it in Elasticsearch. Additionally bitwise queries would have to be constructed as a series of terms matches as demonstrated below. Furthermore, because each binary sequence is represented by multiple terms, this will likely occupy more storage than an integer representation would require.

### Setting up the environment for terms encoding

Define the mapping for keyword representation:

```
PUT test_terms_encoding
{
 "mappings": {
   "properties": {
     "terms_encoded_bits": {
       "type": "keyword"
     }
   }
 }
}
```

### Indexing documents with terms encoding

Index documents with their binary bit representations:

```
POST test_terms_encoding/_doc/1
{
 "terms_encoded_bits": ["b3=0", "b2=1", "b1=1", "b0=0"] // binary 0110
}
```

```
POST test_terms_encoding/_doc/2
{
 "terms_encoded_bits": ["b3=1", "b2=0", "b1=1", "b0=0"] // binary 1010
}
```

### Querying using terms encoding

To query documents where b3 is true, and b0 is false (i.e the doc where \_id=2 above)

```
GET test_terms_encoding/_search
{
  "query": {
    "bool": {
      "filter": [
        {
          "term": {
            "terms_encoded_bits": "b3=1"
          }
        },
        {
          "term": {
            "terms_encoded_bits": "b0=0"
          }
        }
      ]
    }
  }
}
```

## Boolean Encoding

This method uses separate boolean fields for each bit, providing clear and direct access to specific bits.

### Advantages of boolean encoding

The Boolean Encoding method has all of the advantages of the “Terms Encoding” method and some may find this method to be more intuitive. It may also require slightly less storage for some data sets, as just a single boolean value is stored for each field rather than a string.

### Disadvantages of boolean encoding

This has all of the disadvantages listed for the “Terms Encoding” approach. An additional disadvantage of this approach is that because we create a new field for each bit, this will contribute to [mapping explosion](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-explosion.html).

### Setting up the environment for boolean encoding

Define the mapping with boolean fields:

```
PUT test_boolean_encoding
{
  "mappings": {
    "properties": {
      "b3": { "type": "boolean" },
      "b2": { "type": "boolean" },
      "b1": { "type": "boolean" },
      "b0": { "type": "boolean" }
    }
  }
}
```

### Indexing documents with boolean encoding

Index documents with boolean values for each bit:

```
POST test_boolean_encoding/_doc/1
{
 "b3": false, 
 "b2": true,
 "b1": true,
 "b0": false
} // binary 0110 – integer 6
```

```
POST test_boolean_encoding/_doc/2
{
 "b3": true,
 "b2": false,
 "b1": true,
 "b0": false
} // binary 1010 – integer 10
```

### Querying using boolean encoding

To query documents where b3 is true, and b0 is false (i.e the doc where \_id=2 above):

```
GET test_boolean_encoding/_search
{
 "query": {
   "bool": {
     "filter": [
       {
         "term": {
           "b3": true
         }
       },
       {
         "term": {
           "b0": false
         }
       }
     ]
   }
 }
}
```

## Sparse bit position encoding

This approach encodes only the positions of bits that are set to true in an array.

### Advantages of sparse bit position encoding

If the vast majority of documents generally do not have any bits set to true, this could be more efficient in terms of storage versus the previous approaches. For example, you could imagine data sets where the bits represent warning flags should rarely be true, which would result in the bit position encoding arrays being empty (and therefore space-efficient) for a large percentage of documents.

### Disadvantages of sparse bit position encoding

One drawback of this approach is that querying for bits that are not true would require using the [must\_not operator](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html). However, using must\_not for queries can lead to performance overhead since Elasticsearch needs to scan documents to verify the absence of certain values, which is less efficient than directly querying for the presence of specific terms. In large datasets, this could slow down processing. Another drawback is that if the data consistently has many bits set to true, then this would require a long series of integers for representation, which would increase the storage requirements. And finally, like the other approaches, this approach requires pre-processing your data to convert it to the sparse bit position encoding, prior storing it in Elasticsearch.

### Setting up the environment for sparse bit position encoding

Define the mapping for arrays of integers:

```
PUT test_sparse_encoding
{
  "mappings": {
    "properties": {
      "sparse_bit_positions": {
        "type": "integer"
      }
    }
  }
}
```

### Indexing documents with sparse bit position encoding

Index documents with the positions of the bits encoded as integers:

```
POST test_sparse_encoding/_doc/1
{
  "sparse_bit_positions": [2, 1] // binary 0110
}
```

```
POST test_sparse_encoding/_doc/2
{
  "sparse_bit_positions": [3, 1] // binary 1010
}
```

### Querying using sparse bit position encoding

To query documents where b3 is true, and b0 is false (i.e the doc where \_id=2 above):

```
GET test_sparse_encoding/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "term": {
            "sparse_bit_positions": 3
          }
        }
      ],
      "must_not": [
        {
          "term": {
            "sparse_bit_positions": 0
          }
        }
      ]
    }
  }
}
```

## Integer encoding with exact matching

In this approach, binary values are encoded into integers. This is an intuitive approach, especially when you need to store and query complete binary sequences (i.e. integers) efficiently.

### Advantages of integer encoding with exact matching

Of the approaches discussed so far, this is the approach that is most likely to directly map to the way that data is stored in the source systems, which often represent binary sequences as integers. Therefore, storing documents with this approach may require less preprocessing than the other approaches.

### Disadvantages of integer encoding with exact matching

This approach only discusses exact matching of integer values which represent binary sequences. It does not address bitwise matching within the integers. It also requires that you convert your binary values to integers before storing them in Elasticsearch.

### Setting up the environment for integer encoding with exact matching

Define the mapping for integer encoding:

```
PUT test_integer_encoding
{
 "mappings": {
   "properties": {
     "integer_representation": {
       "type": "integer"
     }
   }
 }
}
```

### Indexing documents with integer encoding with exact matching

Index documents by converting binary sequences into integers:

```
POST test_integer_encoding/_doc/1
{
 "integer_representation": 6  // binary 0110
}
```

```
POST test_integer_encoding/_doc/2
{
 "integer_representation": 10 // binary 1010
}
```

### Querying using integer encoding with exact matching

The following query retrieves documents where the binary representation equals a specific value – in this example, the doc which contains an integer representation of 0110 with \_id=1:

```
GET test_integer_encoding/_search
{
 "query": {
   "term": {
     "integer_representation": 6 // binary 0110
   }
 }
}
```

## Integer encoding with scripted bitwise matching

In this approach, we extend the concept of encoding binary values into integers and make use of [scripted query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-script-query.html) functionality to query individual bits that are set within an integer value. This approach is discussed in this article for completeness, but keep in mind that extensive use of scripted queries will generate additional workload on the cluster, and may be slower and less efficient than alternative approaches.

### Advantages of nteger encoding with scripted bitwise matching

This approach has the advantages of the “Integer Encoding with Exact Matching” approach. An additional advantage is that individual bits can be matched.

### Disadvantages of integer encoding with scripted bitwise matching

This approach to bitwise matching does not leverage the data structures that Elasticsearch builds to ensure fast and efficient queries. Therefore this approach is likely to result in slower queries that require more resources than the previously mentioned approaches. For this reason, I would generally recommend the previously discussed approaches.

### Setting up and indexing documents

In this section we will use the same index that was populated in the second called “Integer Encoding with Exact Matching”.

### Querying

To query documents where b3 is true, and b0 is false (i.e the doc where \_id=2 above) we can use a scripted query. The following query satisfies these requirements, and is commented to explain the logic:

```
GET test_integer_encoding/_search
{
  "query": {
    "bool": {
      "filter": {
        "script": {
          "script": {
            "source": """
            // b3 is true 
            // i.e. "integer_representation" AND 1000 == 1000
            // Keep in mind that 1000 binary == 8 in integer
            ((doc['integer_representation'].value & 8) == 8) && 
            
            // b0 false 
            // i.e. "integer_representation" AND 0001 == 0
            ((doc['integer_representation'].value & 1) == 0)"""   
          }
        }
      }
    }
  }
}
```

## Integer encoding with ES|QL for bitwise matching

Like the “Integer Encoding with Scripted Bitwise Matching” approach, this approach can also match individual bits, but it leverages [ES|QL](https://www.elastic.co/guide/en/elasticsearch/reference/current/esql.html) rather than scripted queries. This approach is discussed in this article for completeness, but extensive use of this approach may generate additional workload on the cluster, and may be slower and less efficient than alternative approaches.

### Advantages of integer encoding with ES|QL for bitwise matching

This approach has the same advantages as “Integer encoding with scripted bitwise matching”. An additional advantage it that it leverages ES|QL which is designed with performance in mind.

### Disadvantages of integer encoding with ES|QL for bitwise matching

Even though this approach leverages ES|QL, it is unable to directly use pre-built data structures for bitwise matching. Therefore this approach is likely to result in slower queries that require more resources than many of the other approaches.

### Setting up and indexing documents

In this section we will use the same index that was populated in the second called “Integer Encoding with Exact Matching”.

### Querying

To query documents where b3 is true, and b0 is false (i.e the doc where \_id=2 above) we can use ES|QL. The following query satisfies these requirements, and is commented to explain the logic:

```
POST /_query?format=txt
{
  "query": """
  FROM test_integer_encoding METADATA _index, _id
  // The following uses division to shift the bit we are interested 
  // in, to the right. ie. dividing by 8 (or b1000 - corresponding to b3) 
  // shifts b3 to the least significant bit position, or b0. 
  // Additionally, the rightmost bits are dropped.
  // Then the modulus by 2 checks if the new (post shift) 
  // value of b0 (formerly b3)is odd or even (1 or 0)
  | WHERE (integer_representation / 8 % 2 == 1)  // b3 is true
  | WHERE (integer_representation / 1 % 2 == 0)  // b0 is false
  | KEEP _id, integer_representation
  """
}
```

## Conclusion

In this article, we explored six approaches for bitwise matching — terms encoding (my preferred approach), boolean encoding, sparse bit position encoding, integer encoding with exact matching, integer encoding with scripted bitwise matching, and integer encoding with ES|QL for bitwise matching. This demonstrated how different methods can be applied to efficiently handle bitwise matching in Elasticsearch. Each method has its advantages and trade-offs depending on the specific requirements of your application.

For scenarios requiring individual bit matching, the term-based and boolean field approaches work well and should be efficient. Representing true bit positions in arrays of integers provides a compact and flexible solution for sparse bit sequences. Encoding binary sequences as integers might be suitable for whole sequence operations but at the cost of losing the ability to *efficiently* query individual bits. We can also query individual bits within integers with scripted queries or with ES|QL, but these approaches are likely to be less efficient than the other approaches.

## Acknowledgements

Thanks to Honza Kral for the idea of using terms and integers to encode individual bits, to Alexis Charveriat for suggesting the bitwise matching approach using ES|QL, and to Carly Richmod for making valuable suggestions during the technical review process.

### Frequently Asked Questions

#### What is bitwise matching?

Bitwise matching is a powerful tool for filtering based on binary values, allowing for precise data extraction.

#### What is boolean encoding?

Boolean encoding is a method that uses separate boolean fields for each bit, providing clear and direct access to specific bits. This method is used for encoding and matching binary data.

#### What is integer encoding with exact matching?

Integer encoding with exact matching is used to encode and match binary data. Here, binary values are encoded into integers.

#### What is terms encoding?

Terms encoding is a method used to encode and match binary data. It involves representing each bit as a term which is stored in a keyword field.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt6d8bd040a15da207/6a17e422414c640e67945116/ef9edded97edd7c919e617e648e62016155cde56-720x420.jpg)

[Basics](/search-labs/blog/category/basics)

### Parsing JSON fields in Elasticsearch

October 17, 2025|[Valentin Crettaz](/search-labs/author/valentin-crettaz)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt373f9290a1371dd7/6a17122e0c48579b2001abba/fd87bff40e296ebce871d631c86fd0245f11c796-1440x960.jpg)

[Javascript](/search-labs/blog/category/javascript-programming)[Basics](/search-labs/blog/category/basics)

### Automatically updating your Elasticsearch index using Node.js and an Azure Function App

June 04, 2024|[Jessica Garson](/search-labs/author/jessica-garson)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1a0bf009f00b1c80/6a1711fa4a531b3db636aa9f/c7c174d6408b23fca482664c608f9e8849243d96-1440x720.jpg)

[Basics](/search-labs/blog/category/basics)

### Adding document level security (DLS) to your internal knowledge search

January 22, 2024|[Sean Story](/search-labs/author/sean-story)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d7e4a5bbd9427c2/6a170e4d0e2e4905b641a1b7/04f1738a38cead88c9a67b0f863171b4b43010ab-1600x913.png)

[Basics](/search-labs/blog/category/basics)

### Elasticsearch plugin for UBI: Analyze user data in Kibana

September 26, 2025|[Eduard Martin](/search-labs/author/eduard-martin)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltc31c3bf0d453d846/6a170e12cdacbfdf6a7d2a7e/3ae41b1f2876d2ad11c8e2b79bbf79955d6902aa-1440x840.png)

[Java](/search-labs/blog/category/java-programming)[Basics](/search-labs/blog/category/basics)

### Testing Elasticsearch. It just got simpler.

March 19, 2026|[Piotr Przybyl](/search-labs/author/piotr-przybyl)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter