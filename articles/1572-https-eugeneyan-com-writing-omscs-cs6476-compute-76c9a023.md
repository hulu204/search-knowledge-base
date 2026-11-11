---
title: 'https://eugeneyan.com//writing/omscs-cs6476-computer-vision/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/omscs-cs6476-computer-vision/
account: 
origin: en-rss
---
# [eugeneyan](/)

* [Start Here](/start-here/ "Start Here")
* [Writing](/writing/ "Writing")
* [Speaking](/speaking/ "Speaking")
* [Prototyping](/prototyping/ "Prototyping")
* [About](/about/ "About")
* [![](/assets/icon-search.svg)](/search/ "Search")

# OMSCS CS6476 (Computer Vision) Review and Tips

[
[omscs](/tag/omscs/)
[learning](/tag/learning/)
[deeplearning](/tag/deeplearning/)
[python](/tag/python/)
]
 · 5 min read

> You might also be interested in this [OMSCS FAQ](/writing/georgia-tech-omscs-faq/) I wrote after graduation. Or view all OMSCS related writing here: [`omscs`](/tag/omscs).

I recently completed my first course for the [Georgia Tech OMSCS](/writing/im-going-back-to-school/)—[CS6476 Computer Vision](https://omscs.gatech.edu/cs-4495-computer-vision)—and wanted to share some thoughts I had on it.

## Why choose this course?

I recently built APIs for [image classification](/writing/image-categorization-is-now-live/) and [reverse image search](/writing/image-search-is-now-live/) using deep learning libraries. Through the process, I gained an understanding of how images work as a data structure, and how to apply machine learning on them to build useful data products.

Nonetheless, there was a yearning to get a more in-depth understanding of the fundamentals of working with images. In addition, there are plenty of other useful applications for image and video, and the course seemed to provide a broad overview.

## What specific CV applications were covered?

The class covered several CV algorithms, and how to apply them to solve simple problems, including:

* Detecting lines and circles, including counting the total value of currency (Hough)
* Measuring depth from multiple images (Window-based stereo matching)
* Detecting features to match images/stitch a panorama (Harris, SIFT, RANSAC)
* Detecting movements of objects across multiple images (Optical flow)
* Tracking movements of subjects in videos (Particle filters)
* Classifying motion in videos (Motion history images)

Here’s an example of detecting circles to count the total value of coins in an image. The algorithm is built solely on [Numpy](https://numpy.org/) while we used [OpenCV](https://opencv.org/) libraries to draw circles.

![Computer vision](/assets/computer-vision.webp "Computer vision")

Built solely with Numpy

## What’s the course like?

There were approximately [three hours of lectures weekly](https://docs.google.com/spreadsheets/d/176oY4XKTsvri0aRN7dDzExpFl_A5TMakXNTj8XgO7iQ/pubhtml), followed by an assignment every other week.

The lectures were relatively long and covered plenty of material. They contained a lot of mathematical proofs and derivations so it can feel a little dry at times. At times, the lectures felt packed with so much material that it can feel overwhelming. Thankfully, the professor did an excellent job in explaining the math and the concepts and intuition behind it. It also helped that he was humorous and that kept the lectures interesting.

Assignments were generally broken down into two parts: (i) Development to implement CV algorithms, and (ii) running experiments to tune parameters and document them in a report.

Development required you to apply what was learnt in the lectures to code low level CV algorithms from scratch (in Python). Most of the work was done in Numpy and involved working with matrices and writing efficient vectorized code. This is easier if you take time to get a solid understanding of the underlying math/linear algebra before translating it into efficient code.

For the report, a lot of time was spent running experiments and tuning parameters to get the desired results. While the results require time to achieve, they aren’t meant to be industrial grade. CV is difficult and the class teaches you about the real life difficulties and flaws of fundamental CV algorithms—the more you encounter such challenges, the better an understanding of CV you get.

Overall, the effort required can be quite intense at times and I found myself working approximately 15-20hrs a week for some problems sets. Though it was not necessary to understand fully the detailed math and equations for each topic, having an understanding of the intuition will help greatly.

## Online vs on-campus learning

I had imagined that learning online would be somewhat lacking as compared to learning on campus—I was completely wrong.

With the lectures being recorded, I had the luxury of attending them at a time of my convenience. In addition, there was excellent discussion and support via online forums (we used Piazza) and TAs held regular office hour sessions (that were also recorded). The recordings and forums meant I could revisit the material anytime—this was very helpful while preparing for the final exams. We also had our own course channel on slack for small talk and supporting each other through hair-pulling tough assignments.

With the support of education technology, I learnt a lot from my course mates, far more than my undergraduate days, making the course very fruitful.

## Other than CV specific skills, what else did I gain?

Technically, I gained greater proficiency with Numpy and writing efficient vectorized code. An autograder, with strict timeout settings, was used to test our code—inefficient code with loops had difficulty passing. Writing vectorized code—as opposed to using loops—took a bit more time and effort, though I believe it saved time while tuning parameters for the report.

I also learnt how to translate research, theory, and equations into working algorithms in code. Nonetheless, some research results in controlled lab environments did not translate so well to real life. This “translation” skill is immensely useful when applying cutting edge research into building useful applications.

Lastly, I gained a better understanding of working with images and video, and intuition of how CV related applications work. I recently attended a deep learning conference where there were demos of video tracking applications for emotions and action (e.g., alerts if someone falls down). The improved understanding and intuition helped me understand the technical development details of the application and its flaws before receiving an explanation from the presenter.

## So what’s next?

I aim to apply my newly gained knowledge and skills in working with images at Lazada. We have a lot of images that are sometimes dirty—image segmentation and preprocessing could help clean it up. There are also many applicable use cases such as de-duplication, classification, search, etc.

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (May 2017). OMSCS CS6476 (Computer Vision) Review and Tips. eugeneyan.com.
> https://eugeneyan.com/writing/omscs-cs6476-computer-vision/.

or

```
@article{yan2017vision,
  title   = {OMSCS CS6476 (Computer Vision) Review and Tips},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2017},
  month   = {May},
  url     = {https://eugeneyan.com/writing/omscs-cs6476-computer-vision/}
}
```

  
Share on: 

![](/assets/icon-twitter.svg)

![](/assets/icon-linkedin.svg)

![](/assets/bluesky.svg)

![](/assets/icon-facebook.svg)

![](/assets/icon-mail.svg)

---

  

Browse related tags: [
[omscs](/tag/omscs/)
[learning](/tag/learning/)
[deeplearning](/tag/deeplearning/)
[python](/tag/python/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« One way to help a data science team innovate successfully](/writing/one-way-to-help-a-data-science-team-succeed/)
[How to get started in Data Science »](/writing/how-to-get-started-in-data-science/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---