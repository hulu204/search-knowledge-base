---
title: 'Table Formats in Depth: What is a Table Format?'
company: LanceDB
tag: 搜索
date: 2026-11-09
url: https://www.lancedb.com/blog/table-formats-in-depth-what-is-a-table-format
account: 
origin: en-rss
---
# Table Formats in Depth: What is a Table Format?

[Weston Pace](/author/weston-pace)

•

November 17, 2026

•

[Engineering](/category/engineering)

![2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337-fig-001](../images/2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337/figure-001.png)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

Table formats frighten data engineers.  I don't know why this is the case, but it's something I've observed time after time.  A well-meaning, mild-mannered developer stumbles across a table format, recoils in horror, clutches their file formats, and flees for the hills.  However, this is where it starts to get interesting.

Files are more or less immutable.  Data is not.  It has a pesky habit of changing.  Rows need to be corrected.  New observations are made and need to be recorded.  Our poor engineer, now safely away from the scary table formats, is confronted with this need for change and...promptly invents their own ad-hoc table format.

![2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337-fig-002](../images/2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337/figure-002.jpg)

A tale as old as time

If this sounds like you, then don't worry, I'm (probably) not (currently) stalking you and observing you from afar.  I'm speaking instead from experience, for I was once the fearful data engineer who unwittingly created a Frankenstein-like table concept.  I'm told it still lingers, haunting the lives of the poor engineers that followed in my wake.  Decisions that seemed so wise at the time are now rotting in the light of day.  This is not solely my opinion. Consider this quote from [an article about building data infrastructure for robotics](https://x.com/oh_its_me1/status/2118161174198092046?s=46).

> The single most expensive thing a robotics lab can do is let physical storage become the data model. File-first formats are great for getting started: a dataset is a directory, you can rsync it or list the files. But a directory can't be versioned, branched for an experiment, or queried. So those features get reinvented, badly and incrementally, one script at a time. Versions become suffixes like \_v2 and \_fixed\_res360. Syncing between clusters becomes a person or an agent. The dashboard, the QC tool and the data loader each grow their own partial index of what's on disk.

To help atone for my past sins, I'd like to start a new series of blog posts, shedding light on the mysteries of the table format.  This first post will describe what a table format is and what problem it's solving. Future posts will explore various table format features and implementation details, diving into topics like indexing, identity, conflicts, and the integration surface with related concepts like catalogs, query engines, and databases.

***Disclaimer: I work at LanceDB and spend my days working on the Lance table format.  While this series is intended to describe features in a neutral way, I will certainly have some bias.  I'll do my best to explain how various table formats do things in different ways, but I'll probably tend towards Lance terminology and focus on the use cases we experience at LanceDB.***

## What Is a Table Format and Why Do We Need One?

I alluded to this above, but the reason tables exist is that data changes.  Data files are, for all practical purposes, an immutable construct.  In cloud storage, we cannot modify an existing file; the operations do not exist (outside of some limited append support).  On local storage, we do have some options.  For example, Postgres' `fillfactor` allocates some extra space in each data page where we can write updated values.  If we're using compressed columnar storage, this problem can be even more difficult.  However, valiant efforts have been made; for example, Hugging Face's Content Defined Chunking will allow a Parquet file to change without reuploading the entire contents of the file.

![2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337-fig-003](../images/2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337/figure-003.png)

Data files are, generally speaking, immutable once written

In contrast to these attempts at supporting change, table formats embrace cheap cloud storage like S3, GCS, and Azure, where file modification is simply not allowed.  Instead, a table format typically expresses changes by creating new files.  For an operation like an append, where we add a new row, this is a fairly natural approach. The new row goes in a new file.  However, a table format can even describe deletions this way.  When we delete a row, since we can't change the file, we write out a special file marking the row as deleted.  We can go even further and create special index files that don't hold data at all, but provide summaries or lookups into our data files.

![2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337-fig-004](../images/2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337/figure-004.png)

Adding new rows?  Make new files.  Updating rows? New files. Compacting data? New files. Acquiring a table lock? Believe it or not, new files. Releasing a table lock? Also new files.  Deleting rows?  Believe it or not, new files.

This approach brings about certain fringe benefits, like time travel.  I'll probably describe this feature more later, but the summary is that we haven't modified or gotten rid of our data. It is still there, so we can easily view older snapshots of our data.  However, this approach also brings additional complexity.  We now have multiple files representing our data.  Some of these files, like deletion files, might not even be tabular data files. We need to come up with some set of rules for what files are active and what each file is doing.  This is where the table format comes into play.  Some example things a table format should do:

* Describe what each of the files in our table does
* Describe which files are active at any given point in time
* Describe how to record a change and what changes are valid

Today we have a whole variety of table formats. Iceberg, Hudi, and Delta Lake were some of the earliest.  Now we have new options like Lance, DuckLake, and more. These table formats were inspired by and tailored for different workflows.  They differ in a variety of small ways that can have large impacts.  Still, there are common components present in all table formats because all table formats must at least solve the same basic problems.

### The Manifest (snapshot, timeline, delta log, ...)

All table formats have some kind of metadata file(s) that describe what files are in our table and what each of those files is doing.  In Lance we call this a manifest, and in simple (most) cases it is a single file that lists out all the files in our table.  In Iceberg, this concept is called a snapshot, which is typically spread out across multiple files, though upcoming versions are consolidating this into fewer files.  In Delta Lake, this is the "delta log" which is written as a checkpoint file plus a number of delta files.  Hudi's approach is similar to Delta Lake, where we have a base archived timeline and a number of additional "instants" written on top, though the actual storage is somewhat more complex.  In DuckLake we write all of this down as rows in an external database (e.g. Postgres).

![2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337-fig-005](../images/2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337/figure-005.png)

The manifest tells us which files in object storage make up our data.  As changes occur, new files appear and old files become obsolete. As we can see, Hamlet definitely needs a storage layer that can adapt over time.

All of these approaches are surprisingly different, yet they are all solving the same basic problem.  We need some way to write down what each file in our table is and what it is doing.  For example, we can look at a Lance manifest. Data files are grouped into fragments.  Each fragment provides complete rows of data.  A fragment might have a deletion file associated with it.  A table could also have index files, which Lance describes by connecting a folder with one or more "covered" fragments (much more on that later).  The details are not important (for this post).  The only thing we need to know today is that this "manifest" (or whatever you want to call it) describes what files make up our data and tells us how we should interpret them.

### The Timeline (less line and more wibbly-wobbly, timey-wimey stuff)

It's not enough to simply describe our data; we also need a mechanism for describing how our data changes.  Imagine we want to add some new rows.  We can write a new data file with this new information.  We can also write out a new manifest. So far this is pretty easy to imagine.  The second manifest looks the same as our first manifest but also includes this new data file.  But how do we indicate that this second manifest is now the "active" manifest?  This problem is particularly difficult because we might have concurrent writers that both want their manifest to become the new manifest.

I'll loosely refer to this process as "the commit" and, unsurprisingly, every table format its own nuances to how they solve this problem.  Hudi, Lance, and Delta Lake all make use of a linear "timeline" or "log" of versions.  Versions have some kind of linear sequence (or timestamp), and newer ones are more recent.  Meanwhile, DuckLake and Iceberg punt this problem into another abstraction called "the catalog".  In fact, you could argue that the timeline / log approach is just one example of a catalog.  My retort would be (and in a future blog post, will be) that "catalog" is an overused term encompassing several concepts and the timeline is just one of them.

![2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337-fig-006](../images/2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337/figure-006.png)

In fact, "timeline" itself isn't a great term either because it implies a linear history.  As our friend The Doctor (whom I loosely quoted above) would point out, history isn't so linear.  We might want to support branching, and our "timeline" could actually be an entire graph of commits.  I feel I am spiraling here, but it is important.  Because all of these approaches, whether we call it a timeline or a catalog or anything in between, they all depend on some kernel of atomicity.  Some key mechanism that synchronizes concurrent writers.  This choice of mechanism has profound impacts on the resulting table format.

### The Atomic Kernel

At the heart of every table format change is some way to coordinate between multiple concurrent writers.  One of them must come first, and the other must come second.  It may feel like I am obsessing over some minute detail here, but the way this sequencing is handled has significant implications for the performance and complexity of the table format.  This is because the solutions to this problem fall into two distinct and important categories.

#### Zero Infrastructure Atomics

The simplest approach, which I have dubbed "zero infrastructure", is to rely on the filesystem.  In almost every cloud storage provider, we now have a "put if not exists" operation.  In addition, almost all traditional non-cloud filesystems have a rename if not exists concept (it is a standard, but not universal, POSIX extension).  We can use either of these to build our timeline.

![A sequence diagram demonstrating a commit conflict detected by a "put if not exists" operation](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/6af1d26b69503ac71b013b97_Untitled%20scene(1).png)

User 1 attempts to delete all the cat videos.  However, while they are figuring out which videos to delete, User 2 arrives and inserts some new rows.  User 1 loses the atomic commit race.  If you're curious to find out what happens next, you'll need to check out future posts in this series.

The zero infrastructure approach is great because, as the name implies, we don't have to have an extra long-running process.  For example, I can spin up 50 EC2 instances and have them all start publishing to the same table in S3 without any extra coordination service.  Regrettably, there are limitations.  The performance of "put if not exists" can be limiting in situations where you have a high rate of transactions.  [This article](https://cdouglas.github.io/posts/2026/01/conditional) describes it better, but as of the time I am writing this, you are essentially limited to at most ten or so commits per second.  Still, this is overkill for many situations, and the advantages of avoiding persistent infrastructure cannot easily be overstated.

#### Centralized Coordination

The alternative approach, which is probably obvious at this point, is to have some kind of persistent centralized coordination. For example, in DuckLake, you can utilize a Postgres instance as your commit coordinator.  Internally, this Postgres instance can utilize something like a mutex (or other CAS-based primitive) to handle the coordination.  This can potentially allow for a better transaction rate (although, as I may write about later, this is by no means guaranteed) and it has the advantage of working on all filesystems, even those that do not support "put if not exists" or a POSIX rename (though not mainstream, such filesystems do stubbornly continue to exist)

## Don't Go Alone

As I'm wrapping up this introductory article, I have already found myself talking about a fairly nuanced decision on a rather minor piece of the table format.  It's difficult to come up with the right solution here, and most table formats often end up providing the user with choices.  In Lance, we use zero infrastructure by default, but the commit handler could be extended to allow for centralized coordination.  In Iceberg, the "standard" approach is a REST based centralized coordination, but the boring catalog exists and provides a zero infrastructure alternative.

![2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337-fig-008](../images/2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337/figure-008.webp)

Some tables are read-heavy, others are write heavy.  Some ingest data with duplicate prevention while others do not require it.  Some need to ingest high rates of small writes while others receive large batched writes. There is no one-size-fits-all approach.

There are many ways a table can be used, and it is impossible to come up with a simple one-size-fits-all solution.  Table formats are faced with a myriad of minute technical decisions which favor one use case over another.  The best solution is often to implement several approaches and then develop heuristics that can pick the correct approach given the current situation so that users aren't faced with a configuration nightmare.  Creating this elegant and elaborate patchwork of compromises is no simple task.

This brings me back to my opening problem.  Table formats are complex.  Getting them correct is difficult.  I'm not here to tell people to stop reinventing the table format.  Instead, my hope is that by explaining table formats, I can remove some of the fear associated with the concept.  I also hope that by showing the cool ways table formats can solve real problems, I can spare you a few of the mistakes I've made.  If I do it right, and you stick with me, I might even be able to make them seem exciting or fun.  Ok, that's a stretch, but maybe we can at least shoot for "intriguing".

![2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337-fig-009](../images/2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337/figure-009.avif)

[Weston Pace](/author/weston-pace)

Data engineer from the open source space, working on LanceDB, Arrow, Substrait.

[GitHub](https://github.com/westonpace)[Linkedin](https://www.linkedin.com/in/weston-pace-cool-dude/)[Twitter](https://x.com/westonpace)

![2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337-fig-010](../images/2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337/figure-010.png)

### 🤖 LeRobot Trains on Lance, 🦾 Mining Robot Fleet Data Demo, 🔍 Vector Search at 10B Scale

ChanChan Mao

•

October 7, 2026

newsletter-september-2026

![2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337-fig-011](../images/2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337/figure-011.avif)

### Giving Back to the Open Source We Build On

Xuanwo

Taylor Smith

•

September 21, 2026

giving-back-to-open-source

![2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337-fig-012](../images/2536-Table-Formats-in-Depth-What-is-a-Table-Format-edbd4337/figure-012.png)

### How Jev Compares to Other Rerankers

Taylor Smith

Ayush Chaurasia

•

September 25, 2026

how-jev-compares-to-other-rerankers