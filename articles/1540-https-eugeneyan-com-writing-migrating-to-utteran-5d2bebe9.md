---
title: 'https://eugeneyan.com//writing/migrating-to-utterances/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/migrating-to-utterances/
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

# Migrating Site Comments to Utterances

[
[til](/tag/til/)
[python](/tag/python/)
]
 · 1 min read

Today I learnt how to migrate comments on this site to [Utterances](https://utteranc.es/). The comments functionality on this site has migrated from Discus to Commento and most recently, utterances. You can see the history in the comments [here](/writing/first-post/).

Here are the steps I took:

* Create a [repo](https://github.com/eugeneyan/eugeneyan-comments) just for comments.
* Set up [utteranc.es](https://utteranc.es) with the repo.
* Add the `html` below to my layout template.

```
<script src="https://utteranc.es/client.js"
        repo="eugeneyan/eugeneyan-comments"
        issue-term="url"
        theme="github-light"
        crossorigin="anonymous"
        async>
</script>
```

* Download site comments from Commento. The download is in `json` format.
* Figure out the [GitHub API for importing issues](https://gist.github.com/jonmagic/5282384165e0f86ef105); expected payload below.

```
{
  "issue": {
    "title": "Imported from some other system",
    "body": "..."
  },
  "comments": [
    {
      "body": "comment",
      "create_at": "timestamp"
    }
  ]
}
```

* Read the `json` comments, clean them up, and upload via the GitHub API ([code](https://github.com/eugeneyan/json-to-utterances/blob/master/json-to-utterances.ipynb)).

Now all comments are GitHub [issues](https://github.com/eugeneyan/eugeneyan-comments/issues). Here’s an example of how it looks like in a [post](/writing/end-to-end-data-science/). One downside is that readers will need to login via GitHub to be able to comment; hope this isn’t too big of a barrier.

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Sep 2020). Migrating Site Comments to Utterances. eugeneyan.com.
> https://eugeneyan.com/writing/migrating-to-utterances/.

or

```
@article{yan2020utterance,
  title   = {Migrating Site Comments to Utterances},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2020},
  month   = {Sep},
  url     = {https://eugeneyan.com/writing/migrating-to-utterances/}
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
[til](/tag/til/)
[python](/tag/python/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« How to Test Machine Learning Code and Systems](/writing/testing-ml/)
[How to Accomplish More with Less - Useful Tools & Routines »](/writing/how-to-accomplish-more-with-less/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---