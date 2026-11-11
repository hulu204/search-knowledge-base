---
title: 'https://eugeneyan.com//writing/raspberry-llm/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/raspberry-llm/
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

# Raspberry-LLM - Making My Raspberry Pico a Little Smarter

[
[llm](/tag/llm/)
[🛠](/tag/🛠/)
]
 · 2 min read

As I continue my exploration with large language models, I wondered how they might be used in a low-resource setting, such as a household appliance or a Raspberry Pico. I was also curious about how good they were with generating content in a particular style (e.g., Dr. Seuss), humour (e.g., fake WSJ quotes), and toxic (e.g., HackerNews troll comments).

To satisfy my curiosity, I hacked on `raspberry-llm` ([Github](https://github.com/eugeneyan/raspberry-llm)). It’s a simple Raspberry Pico with an e-ink screen that calls [WSJ](https://feeds.a.dj.com/rss/RSSWSJD.xml) and [HackerNews](https://hnrss.org/frontpage?points=100) RSS feeds, 3rd-party LLM APIs, and generates some content. It started with a rhyming clock, and then… well you’ll see.

• • •

While some use LLMs to disrupt industries and more,

Others build ChatGPT plugins, pushing boundaries galore.

Yet here I am with my Raspberry Pi loose,

Using LLMs to explain headlines via Dr. Seuss.

![Image](/assets/headline-seuss.webp "Image")

You'll find that it can be quite witty,

Making up fake quotes from celebrity.

![Image](/assets/headline-quote.webp "Image")

It can also pose as a hackernews troll,

Slinging mean comments, and being quite an a$$hole.

![Image](/assets/hackernews.webp "Image")

It all started with getting it to tell the time,

With a little quirk, with a little rhyme.

![Image](/assets/clock.webp "Image")

• • •

Overall, it was a fun experience learning how to work with only 8kb of memory(!) and [Micro Python](https://github.com/micropython/micropython). Given the memory constraints, common libraries (e.g., json, xmltodict) were unavailable on the Pico. And even if they were, I couldn’t load the entire RSS feed into memory before parsing it via `xmltodict.parse()`.

As a result, I had to [parse RSS feeds character by character](https://github.com/eugeneyan/raspberry-llm/blob/main/rss.py#L26), learn how much [memory was consumed](https://github.com/eugeneyan/raspberry-llm/blob/main/check_mem.py) at each step, and do lots of `gc.collect()`. It was also fun learning to draw on an e-ink screen (the helper functions made it easier than expected).

To try it, clone this [GitHub repo](https://github.com/eugeneyan/raspberry-llm/tree/main) and update your wifi and OpenAI credentials in [secrets.py](https://github.com/eugeneyan/raspberry-llm/blob/main/secrets.py).

OG image prompt on MidJourney: “An e-ink display connected to a raspberry pi displaying some text –ar 2:1”

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Apr 2023). Raspberry-LLM - Making My Raspberry Pico a Little Smarter. eugeneyan.com.
> https://eugeneyan.com/writing/raspberry-llm/.

or

```
@article{yan2023raspberry,
  title   = {Raspberry-LLM - Making My Raspberry Pico a Little Smarter},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2023},
  month   = {Apr},
  url     = {https://eugeneyan.com/writing/raspberry-llm/}
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
[llm](/tag/llm/)
[🛠](/tag/🛠/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Experimenting with LLMs to Research, Reflect, and Plan](/writing/llm-experiments/)
[More Design Patterns For Machine Learning Systems »](/writing/more-patterns/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---