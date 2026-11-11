---
title: 'Chess Information Retrieval Insights'
company: Sease
tag: 工程相关
date: 2024-05-28
url: https://sease.io/2024/05/chess-information-retrieval-insights.html
account: 
origin: harvest3-202607
---
*A warm greeting to everyone,*  
*we are a group of 7 Computer Engineering students (Andrea Segala, Marco Martini, Mariafiore Tognon, [Leonardo Bellin](https://www.linkedin.com/in/leonardo-bellin/), [Maria Teresa Pepaj](https://www.linkedin.com/in/mariateresapj/), Matteo Salvalaio, Antonino Andrea Care) at the University of Padua. We recently gave birth to an idea for a possible project on a Chess Information Retrieval system. While the idea was born almost as a game we soon became passionate about its development and the game became a real challenge. We are so happy and excited about the evolution of the project that we decided to share the details with you. We hope you enjoy it!*

You probably guessed from the title that the article talks about chess, but we assure you don’t need any particular chess knowledge to understand its content. **A brief knowledge of the game and how it works is more than enough**. We cannot say the same about knowledge in the world of Information Retrieval. If you have no idea what an inverted index and a query are, this blog is probably not for you.

## The Context And Business Potential

Chess is one of the most popular games in the world. Millions of people play chess regularly and most of them use an online platform to play their games. Online chess is now a billionaire business, a striking example is *chess.com*. This online chess platform registers **hundreds of thousands of new users every day**. It is estimated that the company had a turnover of around 100 million in 2022 annual revenue.  
The main source of income for these platforms is achieved through paid user subscriptions. Generally, each chess site guarantees the possibility of being able to play their games completely free, but additional content such as puzzles, lessons, video lessons, game analysis, and other services are provided only to subscribed members.

## Chess information retrieval system

Our idea is to **increase the attractiveness of these services through a Chess Information Retrieval system** that provides the most relevant and effective additional content after each game.  
Going more in-depth, the idea is to transform the game just played into a query. It summarizes the main characteristics of the game (opening, errors, accuracy). Finally, based on the query, the user must receive the best content in order of relevance. **This way the player receives material closely related to the game he has just played!**

### The heart of our chess information retrieval system: query representation

What techniques can we use to convert a chess game into a textual query?  
An initial idea is to exploit chess language to convert the entire sequence of moves played into text.

![Chess Information Retrieval Insights](https://i0.wp.com/sease.io/wp-content/uploads/2023/05/image-2.png?fit=800%2C410&ssl=1)

The problem is that the sequence of played moves is not easily linked to mistakes, tactics, or other game characteristics.  
The idea is to **exploit a chess engine** to be able to analyze the string representing the sequence of moves and obtain significant information on the game.  
We are therefore assuming that we can use a chess engine, but this is not a problem. Every online chess platform always one or more engine licenses. So don’t worry, this is not a problem for our Chess Infomation Retrieval System and let’s go into the details of making our query.

##### Openings

In a game of chess, the opening is the initial stage. The opening includes a series of common moves that have specific names (e.g. Sicilian defense, Spanish game, etc.). Our idea is to **use a dictionary containing all the chess openings and their relative sequence of moves** to be able to identify the longest prefix of our string contained in the dictionary and convert it with the name of the relative opening.

![chess ir](https://i0.wp.com/sease.io/wp-content/uploads/2023/06/image-1.png?fit=751%2C529&ssl=1)

After the opening phase, the idea is to convert the sequence of remaining moves into a set of words that summarizes all the mistakes made.

##### Mistake acknowledgement

To recognize when a user’s move is a mistake, as mentioned above, we can rely on the chess engine. Each engine has evaluation algorithms capable of assigning a score to each move made. Thus from these scores, it is possible to recognize the various mistakes.

![chess engine](https://i0.wp.com/sease.io/wp-content/uploads/2023/06/image-4.png?fit=746%2C497&ssl=1)

###### Recognition of types of mistakes

**Many of the mistakes in chess are connected to key concepts** (fork, enfilade, discovery attack, etc.).

Our idea is to exploit the close connection between these key concepts and particular common structures of the position of the pieces on the board to identify common patterns for any type of mistake. The implementation of **this phase is undoubtedly one of the most complicated and lengthy parts of the project**, moreover, the nature of the problem is mostly a chess technicality, so we have avoided going into the details of the problem.

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/06/image-3.png?fit=756%2C345&ssl=1)

##### Player-level recognition

Another fundamental parameter to consider is the skill of the player. It would be of little use to offer advanced lessons to a user who has just started playing chess. The idea is therefore to **structure the query as a vector of two elements** where the first element is the body of the query (i.e. the keywords relative to the opening used and the errors made) and the second element is the **skill level of the player** which we assume could be classified as *0: Beginner*, *1: Intermediate* or *2: Advanced*.  
In this way, later in the searching phase, it will be possible to search only for content suitable for the player’s level.

### Structure of content

There are two possible types of content we can return to the user query:

* **Text content** (blogs, articles, match analysis);
* **Interactive content** (e.g. puzzles, lessons, workouts).
  + **Chess Puzzles**: A chess puzzle is a puzzle in which knowledge of the pieces and rules of chess is used to solve logically a chess-related problem. Usually, the goal is to find the best, ideally aesthetic, move or a series of best moves in a chess position created by a composer or taken from a real game.
  + **Chess lessons**: The lessons are a series of videos created by expert players, usually masters or grandmasters. These videos explain important concepts such as tactics and positioning, very often the video lessons are accompanied by interactive content, in which the user can try out the principles just learned on the chessboard through ad hoc puzzles.

While textual contents are easily associated with a textual source, the same cannot be said for interactive content, since they are activities that the platform offers to the user. Therefore, for this category, we must assume the creation of a key text, i.e. a textual representation of it.

##### Content fields

The idea is to transform each content into a Document object containing 2 fields:

* **ID**: identifies the various documents to each other.
* **BODY**: body of the textual representation of the document. It is the main field to evaluate the similarity between the query and the document.

### Collections organization and index creation

The documents described in the previous section must be **organized into 3 collections**. We divided them to organize the documents by level of difficulty. One collection for each skill level, i.e. collection 0 will contain all content suitable for a beginner, collection 1 will contain all intermediate, and finally collection 2 for the advanced level. The determination of the skill level of a document can be accomplished by the evaluation by a human operator or automatically through, for example, the frequency of some specific terms.

The system must take care of storing each collection in a dedicated inverted index to speed up the search.  
In particular, the search phase must take place only on one of the three indexes: the index relative to the collection based on the player’s level (i.e. the second element of the query).

## Body Analysis

During the indexing of the documents, we decided to elaborate the body field through an Analyzer composed of two filters.  
The **first filter is a tokenizer that transforms the text stream** contained in the body into a list of tokens. This filter has to take care of:

* The division into several words where a hyphen is present (de-hyphenation);
* Transformation of uppercase into lowercase;
* Elimination of punctuation.

Before introducing the next filter it is necessary to make some observations on the structure of a query body. Each **query consists of a sequence of key terms belonging to a finite set**.

Here are two possible examples:

* “sicilian defense variant dragon attack discovery fork pawn doubled mate corridor”
* “sicilian defense variant dragon accelerated fork trapped bishop trapped queen mate blackburne mate barbiere”

The idea is to take advantage of the fact that the set of key terms is finite, allowing us to use a **keyListFilter**. This filter eliminates every word in the body not contained in a *keyList.txt* file containing all accepted keywords. Roughly speaking, it is as if we were oppositely using a *stopFilter*, i.e. instead of removing all the words belonging to a specific list from the body, we remove all the terms from the body except those contained in the list. Note that with the use of this analyzer, the documents’ terms saved in the index will belong to the same domain where the queries’ terms belong.

In the following example, the proposed analyzer is applied to a piece of a possible document.

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/06/image-6.png?fit=727%2C591&ssl=1)

## Conclusions

In this blog, we have limited ourselves to outlining only a few key phases of this **Chess Information Retrieval project**. Our attention has focused on the characteristics and specific problems of this system. We decided to omit all those parts that can be tackled in a similar way to what would be done for a classic Information Retrieval system. We hope that one day we will have the opportunity to better develop this initial project idea. However, in life, you’ll never know how things will evolve. It’s similar to a game of chess, **you’ll never know what the opponent has in store for you**.

## Do You Want To Be Published?​

This blog post is part of our collaboration with the University of Padua. If you are a University student or professor and want to collaborate, contact us through e-mail.

[Click here](mailto:info@sease.io)

## Do You Want To Be Published?

This blog post is part of our collaboration with the University of Padua. If you are a University student or professor and want to collaborate, contact us through e-mail.

[Click Here](mailto:info@sease.io)