---
title: 'Music Information Retrieval: the Intervals Matrix'
company: Sease
tag: 工程相关
date: 2020-08-25
url: https://sease.io/2020/08/music-information-retrieval-the-intervals-matrix.html
account: 
origin: harvest3-202607
---
In this post, we move a step up from the **[Intervals Table](https://sease.io/2020/02/music-information-retrieval-intervals-table.html)** and we describe what we call the **Interval Matrix**.

The **Intervals Matrix** has been described in our [London Information Retrieval meetup](https://www.meetup.com/it-IT/London-Information-Retrieval-Meetup-Group), in October 2019 ([here](https://www.slideshare.net/SeaseLtd/musical-information-retrieval-take-2-interval-hashing-based-ranking) are the slides): it is an intermediate data structure used in the **Cover Song Detection** approach we are investigating.

We already described in the previous post what an **interval** is and its central role in our approach; however, it’s worth briefly repeating: it allows us to think in terms of **“relativeness”** without caring about **absolute frequencies** or pitches.

## What is an Interval?

The music theory defines an interval as the **difference** in pitch between **two sounds**.

An interval can be **horizontal** (or **linear** or **melodic**), if it represents the distance between two **successively** sounding tones, and **vertical** or **harmonic** if it pertains to **simultaneously** sounding tones, such as in a chord.

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/02/intervals-1.png?fit=404%2C340&ssl=1)

In **Western music**, an interval represents the **distance** between **two notes** of a **diatonic scale**. The smallest of these intervals is a **semitone**.

The **diatonic scale** is a **musical scale** that has

* + **seven** pitches per octave
  + **five** double semitones (a.k.a. **tones**) intervals
  + **two** semitones intervals separated by **two** of **three** tones intervals

The **C-Major** scale is a perfect example of a diatonic scale (1/2 = semitone, 1 = Tone):

![The Diatonic Scale](https://i0.wp.com/sease.io/wp-content/uploads/2020/02/diatonic_scale.png?w=800&ssl=1)

## The Intervals Table

The **Intervals Table** is a **matrix** which defines the **possible intervals** between each note of the **chromatic scale**:

|  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | **C** | **C#** | **D** | **D#** | **E** | **F** | **F#** | **G** | **G#** | **A** | **A#** | **B** |
| **C** | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
| **C#** | 11 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| **D** | 10 | 11 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| **D#** | 9 | 10 | 11 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| **E** | 8 | 9 | 10 | 11 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| **F** | 7 | 8 | 9 | 10 | 11 | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| **F#** | 6 | 7 | 8 | 9 | 10 | 11 | 0 | 1 | 2 | 3 | 4 | 5 |
| **G** | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 0 | 1 | 2 | 3 | 4 |
| **G#** | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 0 | 1 | 2 | 3 |
| **A** | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 0 | 1 | 2 |
| **A#** | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 0 | 1 |
| **B** | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 0 |

Although in **Music Theory** each interval is denoted using a name (e.g. 0 semitones => unison) the table above uses the **number of semitones** as a measure for indicating the distance.

Using the **Intervals Table** above we can say that:

* + the distance between A and D# is 6 semitones
  + the distance between B and B is 0 semitones (unison)

## The Intervals Matrix

Before introducing the central concept of this post, it’s better to start from the input, the **chroma features/chroma matrix**, and then see the manipulation needed for getting an **interval matrix**.

##### Chroma Features

The **chroma features** is a **representation**, along an interval composed by subsequent instants {t0 – tn}, where for each instant the audio signal is decomposed using the **energy** associated with **12 classes** representing the **12 distinct semitones** (or **chroma**) of the musical octave used in Western music notation. Here’s a sample matrix:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/08/image.png?fit=1303%2C660&ssl=1)

where you can see **12 \* t** (t=6 in this case, t6 is partially hidden) matrix where each **vector represents** the **twelve pitches strengths** for a **given instant t**.

The following is another example: the bass riff of “Zombie”, by Cranberries. On the upper staff, you can see the symbolic notation of the riff, and then below there’s the corresponding chromagram; the coloured boxes highlight the compounding parts of the riff across the two different representations.

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/08/image-1.png?fit=1318%2C624&ssl=1)

##### From Chroma Matrix to Intervals Matrix

For **each Chroma Vector,** we keep the **top k** most intense pitch energies and we replace them with their corresponding **ordinal position**:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/08/image-2.png?fit=780%2C544&ssl=1)

We will end up having a **matrix of integers** with the **same columns** as the original matrix but only **k** rows. Each vector contains a ranked list of the k stronger pitch classes, sorted in descending order. Note the **underlying assumption** is that in order to **represent** and **summarise** a chroma vector, the **stronger** a class energy is, the **better**.

Almost done: the **Interval Matrix** is obtained by applying the **Intervals Table** as a function between cells (**ranks**) having the **same index** and belonging to **subsequent chroma vectors**.

In this way we compute a **distance between adjacent vectors** (x[n] – x[n-1]) and those measures compose an output matrix that has:

* + **the same number of rows** of the input matrix
  + **m-1 columns**: where **m** is the number of the columns of the input matrix.

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/08/image-3.png?fit=670%2C572&ssl=1)

## The implementation

As usual, let’s first define the behaviour we want to achieve:

The **Intervals Matrix**

* + should use the **IntervalsTable** in order to **compute the distance vectors**
  + should be a **zero/null matrix** if there’s **no distance** between the input vectors
  + should throw **an exception** in case the input **k parameter** is **greater than 12**
  + should throw **an exception** in case the input consists of an **empty chroma matrix**
  + should **filter** **out** all vectors having a cardinality **smaller** **than** the input **k parameter**
  + given in input an **m \* n** **chroma matrix** should have a dimension equal to **(m – 1) \* n**
  + should return an interval vector, whose size is k, for each subsequent pair of chroma vectors in the input matrix

We are going to use the same BDD approach for expressing those requirements as code [[1]](https://gist.github.com/agazzarini/d4a9cab15eb9a4795e1f34e818c11a4a):

```
				
					class IntervalsMatrixSpecs extends FlatSpec {

  "The Intervals Matrix" should "be a zero/null matrix if there's no distance between chroma vectors" in {
    val table = new IntervalsTable

    ...
  }

  it should "throw an exception in case the input k parameter is greater than 12" in {
    val table = new IntervalsTable
    val inputMatrix = chromaMatrix(31)

    assertThrows[IllegalArgumentException] {
      IntervalsMatrix(inputMatrix, 13, table)
    }

    assertThrows[IllegalArgumentException] {
      IntervalsMatrix(inputMatrix, 15, table)
    }
  }

  ...
}
				
			
```

And finally, the **IntervalsMatrix** is also available as a gist [[2]](https://gist.github.com/agazzarini/77b06db5bc1c6aeb245e5dc029bc4975). As you can read, it is a basic wrapper around a matrix of integers. The constructor takes a chroma matrix and creates the internal data structure which captures the ranked intervals.

Great! Our test suite is growing:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/08/intervals_matrix_and_table_test_suite.png?fit=1460%2C968&ssl=1)

## Need Help With This Topic?​​

If you’re struggling with music information retrieval, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with music information retrieval, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)