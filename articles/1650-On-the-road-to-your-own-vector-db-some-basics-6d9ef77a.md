---
title: 'On the road to your own vector db - some basics'
company: softwaredoug
tag: 召回
date: 2025-05-03
url: https://softwaredoug.com/blog/2025/05/03/on-the-road-to-hnsw
account: 
origin: harvest3-202607
---
On Wednesday May 7th, I’ll stream myself [live-coding a vector database](https://maven.com/p/866f13/doug-live-codes-a-vector-database) with [John Berryman](https://arcturus-labs.com/). As part of that, I want to establish some baseline ideas / concepts before digging into the most popular vector search data structure - [Hierarchical Navigable Small Worlds](https://t.co/C4HkmUZeMA) (HNSW). HNSW sits at the core of systems like Weaviate, Elasticsearch, Vespa, OpenSearch, PGVector, and many others.

## What are vectors / vector search?

Vectors are just arrays of length N, where N might be 768, 1024, 1536, etc. We usually say “N dimensions”. We want to take a query vector (ie `[1,2,3,…]`) and find the K closest vectors in our system (ie maybe `[1.1, 1.9, 2.9,…]`).

These vectors correspond to [vector embeddings](https://cohere.com/blog/embeddings), a representation of a word, sentence, image, or, really anything. Embeddings come out of models that move similar items closer. Our model might know that “Mary had a little lamb” is very similar to “Little bo peep had a sheep” - yielding nearly identical embeddings - despite sharing no important words.

At scale, we need a way to enter an embedding for “Mary had a little lamb” `[1,2,3,...]` and pull back “Little bo peep had a sheep” `[1.1, 1.9, 2.9]` amongst the millions/billions of other vectors. That’s what vector search does.

We use a lot of two-dimensional analogies for high-dimensions (which [can be imperfect](https://softwaredoug.com/blog/2022/12/26/surpries-at-hi-dimensions-orthoginality)). But here, I think they’re apt. I’ll abuse Latitude / longitude on a map as one example of a 2D “vector”.

## Vector search that doesn’t work

Imagine if Lat / Long corresponds to property. Maybe you want to find the closest parcels a given location. Well that’s just 2D vector search.

Your first idea might be to chop up the space - such as on a grid. We find some “region” where `[1,2,3,..]` might exist. Then return all the parcels in that region. For our map analogy, this might be a grid like the US National Grid below (screenshot from [arggis](https://www.arcgis.com/home/item.html?id=d96095fb637846889fb0e46ce69e3967)). If you wanted to find nearest neighbors to lat / long 40.7128° N, 74.0060° W (New York City) you’d zoom in to grids 18T and then subgrid 18TWL like below:

![image.png](/assets/media/2025/hnsw-grid1.png)

![image.png](/assets/media/2025/hnsw-grid2.png)

Unfortunately, we know zooming into 18TWL will give us millions of parcels. Many of which are ***very similar*** to 40.7128° N, 74.0060° W but ***may not be nearest neighbors***.

That’s the first lesson of nearest neighbor search **nearest neighbors is NOT about finding ‘all the candidates within some nearby distance’** - its instead about ***nearest neighbors***. Depending where you live, your neighbor might be feet or miles away.

We all know New York is incredibly dense, finding nearest neighbors requires careful precision. Given that, could we just make a bigger grid? Well a super deep grid down to won’t serve a place like Wyoming - you’d have to gather many many granular squares until you got top K closest parcels. When you get away from 2D analogies, and have N dimensions the problem becomes tougher, creating more degrees of freedom where something can be near or far.

For any vector space - **accurate search requires sensitivity to the distribution of data points**. You have to understand the actual layout of people/property on your map.

## Clusters, graphs, quantization

**Quantization -** Some vector search systems *quantize vectors* to add sensitivity to the data distribution. Quantize usually means taking a very precise number like 40.7128 and shrinking to 40.7 to save space/time but sacrificing accuracy. But to be sensitive to the data, quantization, also means squishing or stretching lat/long to a different range to accomodate the actual population density, like the cartogram below (taken from [NHGIS](https://commons.wikimedia.org/wiki/File:CartogramPresidentialCounty1964Colorbrewer.gif)).

![image.png](/assets/media/2025/hnsw-cartogram.png)

Imagine we squished lat/long to an 8 bit integer. Some mathematical wizardry has helped put New York’s spaces into values 0-32 of each dimension. Los Angeles, gets 33-48 of that dimension. Wyoming just gets a few measly bits. You can dig into [product quantization](https://www.pinecone.io/learn/series/faiss/product-quantization/) and [better binary quantization (BBQ)](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch) for how this works.

**Clusters -** Another - very related - idea is to cluster data points with combinations. Such as the image below showing k-means population clustering (image below by [Michael Gastner](https://www.researchgate.net/figure/Facility-locations-determined-by-simulated-annealing-and-the-corresponding-Voronoi_fig1_6880647))

![image.png](/assets/media/2025/hnsw-voronoi.png)

K-means starts with some K points (like 500? 1000?) and nudges around them around the map until each minimizes its total distance to the actual data points (ie parcels of land).

Once trained, you can imagine having a list of centroids to lookup with a lat long - that points to the rough “neighborhood”. Then at least instead of a constant-zide grid, you’re working with a tiny zone that might be a slice of New York… or the entire state of Wyoming.

Clustering has long been part of vector search hacks [from the early days](https://www.youtube.com/watch?v=bWc4DOM-CHk), as they fit somewhat cleanly into traditional search indices inverted index data structure. Each cluster can point to a list of (vectors, people, parcels, etc) that live there. File formats like [IVF also map centroids to clusters](https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/understand-inverted-file-flat-vector-indexes.html) in an inverted index style format. Clusters drive Billion-scale vector indices like [SCANN/SPFresh](https://arxiv.org/pdf/2410.14452) - used by systems like [turbopuffer](http://turbopuffer.com).

**Graphs -** But we’re here to talk about graphs. That’s what HNSW uses.

If we connect all the neighbors together, and walk the graph until we get to the lat/long gets closest to our NYC coordinates, we’ll eventually gather that coordinates neighbors. Perhaps like the **roadmap:** below

![image.png](/assets/media/2025/hnsw-roadmap.png)

In this map we start somewhere, and head in the direction of our destination. If we encounter a fork in the road, we see where each fork heads, and choose the path that gets us closer to our destination. We track where we’ve visited, as to avoid loops.

This, indeed works!

## Let’s see it in code

Map based analogies only get us so far!

To fulfill the promise of building HNSW we need a graph. And every graph has a node:

```
class Node:
    def __init__(self, vector, id):
        self.vector = vector
        self.id = id
        self.neighbors = []
```

And a graph holding some nodes:

```
class VectorGraph:
    """Fully connected vector graph."""
    def __init__(self):
        self.nodes = []
```

We’ll write search first:

```
  def _search_graph(self, vector, k):
      visited = set()       # IDs of nodes visited thusfar
      last_num_visited = 0
      nearest_neighbors = []    # Nearest neighbors thusfar
      entry_point = self.nodes[0] if self.nodes else None     # Entry point
```

A lot of this is standard “walking a graph” stuff a Computer Science undergrad can do. We track where we’ve been to avoid double work. We always start with a consistent entry point (otherwise, when we use this search to build the graph, some roads won’t connect to each other!).

Any time we encounter a new Node in the graph we attempt to save it:

```
  def _save_neighbor(node):
      if node.id in visited:
          return
      distance = euclidean_distance(vector, node.vector)
      heapq.heappush(nearest_neighbors, (-distance, node))
      if len(nearest_neighbors) > k:
          heapq.heappop(nearest_neighbors)
      visited.add(node.id)
```

Using Python’s heapq library, we maintain a heap of the closest items, popping off anything past the top k. We also track the ids visited to not revisit anything.

Now we visit / add our current node’s neighbors, and move to the closest neighbor node we know about so far. Finally we stop our loop.

```
  while True:
      # Save all the current search nodes neighbors if close enough...
      for neighbor in curr.neighbors:
          _save_neighbor(neighbor)
      # Stop if nothing changed...
      if len(visited) == last_num_visited:
          break
      # Get the closest neighbor...
      curr = heapq.nlargest(1, nearest_neighbors)[0][1]
			last_num_visited = len(visited)
 return heapq.nlargest(k, nearest_neighbors)
```

Finally to add a node, we just search for the best insert location, and insert accordingly

```
  def add(self, vector, id):
      node = Node(vector, id)
      if not self.nodes:
          self.nodes.append(node)
          return
      nearest_node = self._search_graph(vector, 1)
      self.nodes.append(node)
      if nearest_node:
            dist, neighbor_node = nearest_neighbors[0]
            # Connect to the nearest neighbor
            neighbor_node.accept_neighbor(node)
            node.accept_neighbor(neighbor_node)
```

(All this obviously non-production ready code can be [found here](https://github.com/softwaredoug/hnsw/tree/main/hnsw))

### Real world considerations

This is a fairly straight-forward example of walking a graph to get closer to a destination. But we might consider a few things:

1. Limiting the number of neighbors any node can have. Right now that’s unbounded
2. Connecting our graph to more than just one node. Right now we connect to exactly 1 neighbor. This will make the search potentially less accurate
3. We only search exactly one neighbor node, what if the best route is some side route from the second closest neighbor from this node?

These relate to two [hyperparameters we’re not paying attention to yet](https://github.com/nmslib/hnswlib/blob/master/ALGO_PARAMS.md#hnsw-algorithm-parameters) - ef and M:

* ef - controls how many paths we go down our roadmap to find possible neighbors
* M - how connected our graph is

### And the big one - hierarchy

Even with a well-connected graph, we have a problem - very little hierarchy. If every road is a surface road in the US, finding directions can be a nightmare. If you’re driving, you hope to use the “higher level” constructs (boulevards / highways / interstates / etc) to efficiently navigate between two major cities. Otherwise navigating between LA to New York would involve 1000s of tiny turns, making the road-graph nearly useless. Highways let you quickly jump between regions, avoiding thousands of twists and turns. That’s where the *hierarchical* of HNSW comes from.

### See you Wednesday

But these finer points, and more (like adding hierarchy!), will need to wait till my embarrasing attempt to [live-code all of this on Wednesday](https://maven.com/p/866f13/doug-live-codes-a-vector-database). Hope to see you there!

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---