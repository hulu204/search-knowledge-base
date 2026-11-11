---
title: 'https://eugeneyan.com//writing/mailbag-pdf-fields/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/mailbag-pdf-fields/
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

# Mailbag: Parsing Fields from PDFs—When to Use Machine Learning?

[
[machinelearning](/tag/machinelearning/)
[📬](/tag/📬/)
]
 · 4 min read

K writes:

> I am more a developer than a data science or ML person. I got a question to ask and I am not exactly asking for an answer to a close-ended question. More like I am asking for directions for a more open-ended quest.
>
> I have a situation where I have a script that reads a PDF to look for a particular . It then takes that quote number and assumes it's correctly inputted from the 3rd party and then looks up a database that I control to find the corresponding data row and its expected total value.
>
> Then performs a comparison: is the total value in the PDF the same as the total value expected in the database?
>
> That’s all the script does. And to look for the quote number in the PDF the script uses regex.
>
> Now this is all fine and dandy if the PDF is machine generated with a consistent formatting. However, I faced occasional issues (like around 1 in 100 cases) where there’s typo or misspelling.
>
> The misspelling causes the  not to be found even though it is actually there.
>
> The logic is `Quote: [The quote number is actually here]` but I get misspellings such as `Qoute:[The quote number is actually here]`. I have tried to patch this with increasing the regex but it will never be exhaustive.
>
> There are also typos in the quote number itself.
>
> They mean
> `Quote: Q20-100011`
>
> But they show
> `Quote: Q20-100101`
>
> And the unfortunate thing is sometimes, there are actual data rows that match the typo causing the wrong comparisons.
>
> I have never implemented any ML before and I also not sure whether it’s even worth it. Right now it’s more like human discovery of error after the fact to correct this kind of mistakes.
>
> So my question is: How do I evaluate if I should consider ML in a situation like the above and if so what kind should I be looking at? HOw do I consider the tradeoffs? Assume I am totally new to ML.

Hey K, thanks for reaching out! I think in this case, you have an excellent solution already—99% recall (i.e., error in 1 out of 100) is a great result.

Now, about those errors:

* For misspellings in the word “quote”, I think this can be resolved to some extent with [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance).
* I.e., for each word, how many characters do we have to change so that word becomes “quote”
* “qoute” would need two char changes while “route” would need one char change
* We can also combine this with a calculation of the proportion of characters that are exactly the same as “quote”.
* Thus, “qoute” would have a 100% match, while “route” would have a 80% match.
* Together, the two approaches should help with finding misspellings for “quote”.

About errors in the quote number itself: This is tricky.

* If we can find a quote in the database that is close enough tot he quote in the PDF (based on the two approaches above) and have identical value, we should flag that.
* Nonetheless, I think it’s best to flag these for a human to inspect and manually accept the error correction.
* What we don’t want is to erroneously find quotes that aren’t in the database.
* This would depend on how unique the quote values in your database are. If they’re are recurring quotes with identical values, we might have to match on date as well.

In both cases, I think using deterministic logic is far simpler, faster, and easier than machine learning. ML will have some error, and would be unlikely to improve on the 99% recall that you already have.

K’s reply:

> So from your working experience, it’s okay not to achieve 100% recall.
>
> So even with deep learning solutions, there’s an acceptance within your field not to hit 100% yes?

Yes, of course! IMO 99% recall is excellent.

---

Have a question for me? Happy to answer concise questions via email on topics I know about.
More details in [How I Can Help](/how-i-can-help/).

  
Share on: 

![](/assets/icon-twitter.svg)

![](/assets/icon-linkedin.svg)

![](/assets/bluesky.svg)

![](/assets/icon-facebook.svg)

![](/assets/icon-mail.svg)

  
Browse related tags: [
[machinelearning](/tag/machinelearning/)
[📬](/tag/📬/)
]

[« Datacast Podcast - Effective Data Science with Eugene Yan](/speaking/datacast-eugeneyan/)
[How to Test Machine Learning Code and Systems »](/writing/testing-ml/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---