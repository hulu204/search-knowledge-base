---
title: 'https://eugeneyan.com//writing/netlify-back-to-github-pages/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/netlify-back-to-github-pages/
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

# Why I switched from Netlify back to GitHub Pages

[
[misc](/tag/misc/)
]
 · 3 min read

A week ago, I was looking for something to tinker with over the weekend. I ended up switching my site hosting from GitHub Pages to Netlify.

The [comparison was compelling](https://www.netlify.com/github-pages-vs-netlify/). I was appealed by the 1-click rollbacks, ability to use more Jekyll plug-ins, and A/B testing my site (fun!).

However, I switched back to GitHub Pages today. Why?

## My MX records weren’t migrated automatically

(MX records are DNS records for delivery email to your address.)

When I switched my DNS servers to Netlify, it was pretty painless: Update the DNS name servers, provision the cert, and we’re good to go.

However, I didn’t realize that my MX records weren’t automatically migrated as well. (When I previously moved to Cloudflare, this was taken care of).

As a result, emails to my domain bounced for a few days before I noticed. Thankfully, people reached out via other channels to inform me of it.

## Adding MX records on the DNS provider was a pain

Trying to add the MX records with the DNS provider, NS1, was a pain.

I had to create an account with NS1 and provide them with credit card details. (Update: Was charged $2 within a day; will enquire why).

Then, I had to set up a “Zone” to attach the MX records. However, when I tried setting up the zone for my domain, it was not allowed as the domain already exists. Probably from the Netlify integration.

I spent some time trying to figure this out. I also asked some Netlify folks. Turns out that while they use Netlify to host their site, they use other DNS providers (instead of NS1).

## Adding the custom certificate didn’t work

By now, I’ve switched my DNS provider back to Cloudflare, and added the Cloudflare Origin cert to my Netlify app. (I really wanted to continue using Netlify.)

However, I soon got complaints that people couldn’t access my site due to the error: “Peer’s Certificate issuer is not recognized.”. I faced the same issue too. I’m not sure where the issue lies (cert or host) but I had lost patience by now.

## Another gotcha: 300 build minutes monthly

While the [GitHub Pages vs Netlify comparison](https://www.netlify.com/github-pages-vs-netlify/) indicates that both are free, with Netlify being superior at 3 builds a minute, it leaves out one major gotcha: On the free tier, Netlify only provides 300 minutes of build time monthly. AFAIK, GitHub Pages has no limitations.

For someone who frequently adds and tweaks content, and mucks around with the CSS and whatnot, 300 minutes didn’t last long.

On its own, this limitation would have been bearable—I figured I would try to be more frugal. But the DNS issues broke the camel’s back.

## Back to GitHub Pages

Now, I’m back to hosting on GitHub Pages and merrily pushing updates as inspiration strikes. Previously, I was checking the build minutes remaining ever so often.

I guess I’ll have to do without the fancy Jekyll plug-ins, 3 builds/min, and A/B testing for now. In return, I get peace of mind.

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Oct 2020). Why I switched from Netlify back to GitHub Pages. eugeneyan.com.
> https://eugeneyan.com/writing/netlify-back-to-github-pages/.

or

```
@article{yan2020netlify,
  title   = {Why I switched from Netlify back to GitHub Pages},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2020},
  month   = {Oct},
  url     = {https://eugeneyan.com/writing/netlify-back-to-github-pages/}
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
[misc](/tag/misc/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Why Have a Data Science Portfolio and What It Shows](/writing/data-science-portfolio-how-why-what/)
[Data Discovery Platforms and Their Open Source Solutions »](/writing/data-discovery-platforms/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---