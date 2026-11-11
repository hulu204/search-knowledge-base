---
title: 'Brave Unveils New Privacy-Focused AI Answer Engine, Set to Handle Nearly 10 Billion Annual Queries'
company: Brave
tag: 搜索
date: 2024-04-17
url: https://brave.com/blog/answer-with-ai/
account: 
origin: harvest2-202607
---
# Brave Unveils New Privacy-Focused AI Answer Engine, Set to Handle Nearly 10 Billion Annual Queries

Published
Apr 17, 2024
(Last updated
Aug 23, 2024)

[Share on X (formerly Twitter)](https://twitter.com/intent/tweet?text=Answer%20with%20AI%20is%20the%20only%20large%20real-time%20answer%20engine%20that%20puts%20privacy%20first%20and%20does%20not%20rely%20on%20Big%20Tech%20search%20engines&via=brave&url=https://brave.com/blog/answer-with-ai/ "Share on X (formerly Twitter)")
[Share on Reddit](https://reddit.com/submit?url=https://brave.com/blog/answer-with-ai/&title=Answer%20with%20AI%20is%20the%20only%20large%20real-time%20answer%20engine%20that%20puts%20privacy%20first%20and%20does%20not%20rely%20on%20Big%20Tech%20search%20engines "Share on Reddit")
[Share on Telegram](https://t.me/share/url?url=https://brave.com/blog/answer-with-ai/&text=Answer%20with%20AI%20is%20the%20only%20large%20real-time%20answer%20engine%20that%20puts%20privacy%20first%20and%20does%20not%20rely%20on%20Big%20Tech%20search%20engines "Share on Telegram")
[Share on LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://brave.com/blog/answer-with-ai/ "Share on LinkedIn")

[AI news & features](/category/ai-news-features/)

*Update: As of August 23, 2024, [CodeLLM](/blog/codellm/) is now part of Answer with AI to offer a more consistent user experience when asking questions in Brave Search.*

*Answer with AI* is the only large real-time answer engine that puts privacy first and does not rely on Big Tech search engines

Today, Brave is announcing a major update to Brave Search and to how users find answers online. The new Brave Search answer engine synthesizes information from multiple sources into a single, intelligible answer to almost any query—a significant step forward from Brave’s [AI Summarizer released in 2023](/blog/ai-summarizer/).

Brave Search *Answer with AI* is unique in several respects:

* It is the first privacy-preserving answer engine available at scale, serving the almost 10 billion queries a year that Brave Search currently receives, making it, overnight, one of the largest AI solutions on the market.
* It produces near instant answers (with sources cited) with sources alongside traditional search results.
* The answers result from the only independent search index at scale outside of Big Tech, as the largest real-time answer engines rely on the Google or Bing search engines, directly or indirectly.

Brave Search’s *Answer with AI* feature is available for free to all users across platforms, on both desktop and mobile. No matter which browser users choose, it can be accessed on the Web at [search.brave.com](https://search.brave.com). The answer engine also supports multiple languages besides English. Brave Search’s 27 million queries a day makes it the fastest growing search engine since Bing.

![Clicking the Answer with AI button](/blog/answer-with-ai/images/image5.jpg)

Clicking the Answer with AI button

## The need for answer engines

Web-scale search engines have undergone many iterations: directory listings, ten blue links, query-dependent snippets, knowledge graphs and featured snippets. The Brave Search *Answer with AI* feature evolves this paradigm. An answer engine is a system that tries to *answer* a question, rather than point to websites *about* the question. Thanks to the proliferation and quality of [large language models](/ai/intro-to-large-language-models/) (LLMs), search-integrated answer engines are now a possibility at scale. In fact, several companies that operate search engines have released similar systems (including Bing Copilot and Google Gemini). Other answer engines rely on API access to existing search solutions to serve at least some portion of their real-time results.

[Brave Search released an AI tool for synthesized results](/blog/ai-summarizer/) known as the Summarizer in March 2023 to help users better navigate search results. With today’s release, we’re taking a big step forward in delivering a next-level search experience, whether an answer or links of page results.

*“With the new Brave Search and its integration of Answer with AI, users get the best of both worlds: one place to get generative answers as well as up-to-date links, providing instant and highly relevant results,” said Josep M. Pujol, Chief of Search at Brave. “Brave Search is uniquely positioned in this landscape, with the only independent search index besides Bing and Google. Unlike many search companies that are forced to rely on results from third parties, or others that solely offer answer engines, Brave now combines its index with AI to redefine the search experience and raise the bar on immediate pertinence in results, while preserving users’ privacy.”*

*Listen to the Brave Search team talk about building Answer with AI:*

[Transcript](#transcript-31510037)

## Introducing Answer with AI, Braveâs New AI Assistant

[00:00:00] **Luke:** From privacy concerns to limitless potential, AI is rapidly impacting our evolving society. In this new season of the Brave Technologist podcast, we’re demystifying artificial intelligence, challenging the status quo, and empowering everyday people to embrace the digital revolution. I’m your host Luke Mulks, VP of Business Operations at Brave Software.

Makers of the privacy respecting Brave browser and search engine, now powering AI with the Brave Search API. You’re listening to a new episode of The Brave Technologist, and this one features two guests from the Brave team, Josep, our lead at Brave Search, and Remi, the principal engineer at Brave. They joined us on the podcast this week to discuss our Answer with AI launch, which shipped a few weeks ago.

Today we dove into how Answer with AI is different from other chatbots, what this innovation means for traditional search, Our privacy policy with this engine, how we’re handling hallucinations. And what the main challenges have been in building this new system. These were the perfect guests to discuss this.

Joseph is the chief of search at Brave and has been working on an alternative search engine since 2014. Before being involved with search, he was a research scientist at multiple institutions, working on AI, distributed systems. And complex networks. He has authored over 30 papers and holds four patents.

He also holds a Ph. D. in A. I. from the Technical University of Catalonia. Remi has been working with A. I. since 2014 and currently as a Senior Software Engineer at BraveSearch, where he has been involved in scaling the ML infrastructure to serve continuously growing traffic and increasingly advanced needs, as well as in the development of BraveSearch’s latest feature, Answer with A.

I. We’re excited to share this update with you and why we’re so optimistic about it. Now for this week’s episode of the Brave Technologist. Remi and Joseph, welcome to the Brave Technologists podcast. How are you guys doing today? Good, good. Very well. Thank you. Awesome. Thanks for having us. Yeah, yeah, of course.

Excited to have you back, Joseph and Remi. Excited to have you here for the first time. I think a lot of what we’re talking about today is around this kind of new answer with AI summarizer feature that we just recently released. Remi, how is different from the typical chatbot like chatGPT or, Cloud?

[00:02:11] **Remi:** Yeah, great question. I think people sometimes kind of oppose them. I think, I mean, my opinion, our opinion is more complimentary. So if you take, you know, chat GPT or cloud, their goal is to build the best model for open ended conversation, you know, like, you know, having multiple rounds with a user on any, topic really.

One issue is that is often the lack of context, right? So like the only context they get is what the user gives them. And then they use the knowledge they have acquired during training to come up with answers, right? I like to think of them sometimes how they are called as foundational models. And I like this term because This is what we are doing.

We are building on top of this model. So they are kind of complimentary to what we do. And with answer with AI, basically what we do is like, we give access to this model, an entire independent search index, which is the brave search index, right? So they have quote unquote, perfect context in a way, right?

So for any user query, they are going to have access to the best information we can find on the web out of billions of pages. And we are going to synthesize this into, you know, the best answer we can, right? Okay. One, maybe like drawback with this approach is it’s off by design, a bit less interactive. So once you have your answer, you are a bit less free in the way that you can follow up.

You know, you cannot just start a conversation and it’s why, I mean, we’re going to talk, I think a bit later about that, but that’s why we’re working on integrating Leo so that we can offer, you know, both experiences, both like best answers, based on the web web, and then also following up in arbitrary ways and, you know, back and forth conversation ways of chatbots.

[00:03:45] **Luke:** No, it’s great. That’s awesome. And I think Joseph, when we had you here last, I think the summarizer, the first iteration of it had been out for a little bit. We’ve kind of addressed this question too, but I’m just kind of curious, like, as this new update rolls out and continue to see progress on the summarizer stuff, like, how’s your position changed?

Like, you think that, you know, answer engines are going to end up replacing traditional search or, Augmented or end of an era kind of thing, or what was your take on this?

[00:04:09] **Josep:** I get this question quite a lot. Well, I mean, first disclaimer, I mean, I’m better at predicting the past than the future.

It depends what you mean by replacement, right? Certainly answer engines are here to stay. They will constitute an evolution to search engines. That’s the fact. Are they going to replace them entirely? No, I don’t think so, right? For, like, for many reasons. some, right? First of all, I mean, not all the queries are amenable.

to be answered by an article type answer. We actually know from experience because of Summarizer v1, which was the toned down version of what we just released, the answers with AI, that was released more than a year ago. So we got a lot of data. And we estimate the queries that are amenable to be answered by answers with AI to be between a fourth and a third of the total queries.

So that means that you still have two thirds that are not, what are those two thirds, right? I mean, I don’t know, Bank of America login, NumPy download, Hotmail, the phone of a restaurant. I mean, can they be answered by an answer? Yes, but it’s not the most convenient way. To do it right, in a way, that’s why I don’t believe that answer engines are replacement and your answer engines are just like one extra thing that certain engines will have, right?

The same as feature the snippets or the same as knowledge graphs, right? I mean, and answer engines actually totally subsumed those two, right? But it will not subsume the 10 links and actually it shouldn’t, hopefully, right, because answers are very good, are very convenient, convenience have, have drawbacks, right?

Less choice, less sources of truth. So you don’t, you don’t want an article type answer. At least, that’s what I believe. And in any case, that’s what we experienced and, and that’s, I think that’s gonna be like this for a long time. Also in, and if you actually go more into the technical details, right? I mean, an answer engine needs a search engine nevertheless, right?

Because why are you going to pull the data from my knowledge on the LLMs? I mean, only has training data. So you need a lot of like context. To the rack generation, right? Who is the best search engine to get that context in, but you need to do things like grounding, provide citations. So you need to search engine, right?

Even if if everything was answers, you will just need a search engine. Or an a p to a search engine, right? Which is like the typical, the typical case. And then just lemme elaborate a little bit on, on those two. Yeah, please do. I mean, more like on the, on the strategy of what we want to do at Brave, right?

Just to have answers would not be actually on the best internet of the user in our opinion. Right? Because what we want to do is like an alternative to the big tech, right? So we need to do like a, to provide the same technology and the same specify the same user needs. It wouldn’t be optimal for the user to have, like, this dichotomy where they have to do certain type of queries.

It’s better one system, certain type of queries is better another system, right? People love convenience. When people search, they are not something that they do it for fun. Usually search is because you are doing a task. So you don’t want to do crazy experiments. Your need satisfied as soon as possible, right?

Regardless of the delivery methods, right? So we need to be like, we need to be one stop shop. Unless we are one stop shop, well, we cannot be the default, right? And we all know that the defaults are very important, right? I mean, there is a reason why Google pays 20 billion to Apple every year, just to be the default on Apple devices, right?

I mean, it’s like, so No, I’m not going anywhere.

[00:08:04] **Luke:** It is kind of a silly question too, right? Because I think one of the strengths of, of what we’ve been doing at Brave, that you guys have put a lot of care into, even with the first version of Summarizer, like making sure that things were, the citations were there and linkable and that, you know, and even with this new version, the blue links are there, right underneath, you guys are giving them for the full, like corpus of information they need.

From that summary. And I think that it’s really kind of a cool way that you guys are doing it, where you’ve mixed these two things together, where, when they serve, but I think even to unpack that a little bit, the fact that you all put so much care into just knowing what’s addressable by an answer versus what’s just a great thing to put us a search engine result page in front of, right?

Like, I think that’s even something that, you know, a level of thought that’s going into this that I think a lot of other companies probably wouldn’t apply because we’re thinking about the user like that.

[00:08:52] **Josep:** That’s a good point. I mean, we, one of the most challenging tasks is like the triggering, right? Like one, two, one, two, like do normal search and one to do like a answer type search, right?

And tell you, of course the user still is on control, but it’s always like a button. And then next to the query box where you can invoke the summarizer. But we try like to, you know, I try to double guess, well, to guess what is their real intent as much as possible again, like, because when I stop shop, satisfy, maximize this satisfaction, et cetera, et cetera.

So that’s kind of like, that’s one of the things and something I forgot to mention, which is like, it’s not only that, but for me, it would be better to talk about this, but I’ll do it anyway. I think the normal results on the bottom. We actually put a lot of emphasis on expanding beyond the wall of text.

People have noticed that we actually named entities and we add the structure of information into the generated answer just to understand. You know, like to be more like a friendly to the, not an eye candy, but actually like more like an informational value, right? I mean, that’s kind of like a important thing.

Like take for instance, like a phone number, right? When you don’t want to fish for a phone number on a wall of text, you want to know where it is. And just like, look there.

[00:10:10] **Luke:** I’ve got a great anecdote on that one too. I, it’s my go to in, business calls. I do now where, I have a feeling the person on the other end is a golfer because actually it was, look, I have these old golf clubs from like 2007.

And if anybody golfs, like when you’re putting a set together, you end up diving into these older sites where you’re like, I hope somebody put it in a HTML table of all of these, like, you know, different lofts and clubs. I actually like. Put it into the answer engine and just put everything in a beautiful table right there.

I knew all the lock degrees, all the club links, everything like that. So now it’s been kind of my go to because not only does it give me what I want, it cut probably three or four steps out of my journey of like digging up these specs and, and, and looking at it again. And I can just easily kind of share it with people.

So it’s super useful, like

[00:10:52] **Josep:** it’s very useful. And that’s why, like, it would be pretty short sighted not to provide answers. Right. Even with some of the drawbacks that they, they can cost, right? Like, minimize choice, narrow down, narrow down the ability for people to see other sites than, than the one that you’re providing.

I mean, those like things are, are important, but convenience. It’s like, you cannot fight the times.

[00:11:16] **Remi:** I love what you say about like, picking the right format of answer for any query, because in a way, like, if you forget about answer with AI, it’s what we’ve done since the beginning. You know, like, for some queries, you want a sport widget, sometimes you want a weather widget, sometimes you want, you know, something else, and answer with AI is just a continuation of that on more types of queries, where we can say, okay, for that particular query, it’s the best way to answer the user, right?

[00:11:41] **Luke:** It sounds like there’s probably opportunities too for, for some of these areas of concerns to kind of evolve and kind of upgrade with some of these things too, right? I mean, I’m sure that like people are concerned about, Oh, well, you know, it seems like nobody’s really monetizing the AI side other than doing premium and other things either, but it seems like a pretty greenfield there.

And when I see these things, I’m like, wow, there’s just like, this is a whole new level of interesting, useful things that users can benefit from that, you know, it’s just opening the doors to, which I think is super cool. Yeah. Joseph, you’re combining this AIML kind of SERP approach. You kind of touched on it, how giving the answer can be beneficial for users, but is there any other elaboration you want to break down on how like unique this is compared to what other competitors are doing, especially when it comes to like benefiting user?

[00:12:24] **Josep:** The main benefit is that, well, it’s like the one of Topshop, right? The ability that the user get the best answer or results, they get the best satisfaction of their query intent. If you want to go technical, you know, in a single place, right? That’s kind of like the main benefit, the integration. However, we must say that anyone can build an answering engine, right?

Actually, there’s plenty of YouTube videos that use Brave Search API, OpenAI. They combine quickly and they create like a complexity clone kind of thing. in, in a matter of a few hours, those things actually work fairly well. So that’s not the, there’s like the meat of the problem is not the, for me, we’ll talk more about that.

Right. But like the complicated thing of an answer engine is not the application in a way it’s like how you scale it and how you do the context creation and how you put the prompt and how you do the grounding, et cetera, et cetera. Right. And all those things. Basically, yeah, we have the same ingredients, right?

Because we do use Brave Search API. One of the things that we are important for people to remember is that Brave Search uses Brave Search API. So we, we, we try to do our own dog food so that we have the best API there is. Well, at least,

[00:13:43] **Luke:** It’s really interesting too. I mean, I think how does it feel for you guys when you see other people? I guess AI is one of these fields where it’s almost like if somebody can think it, they’re going to make a proof of concept for it, right? Like when you start seeing other people using, whether it’s the API, I saw somebody tweeting about this the other day where they were, you know, kind of leveraging the API, when you start to see people, experimenting with this.

Tech that you guys have built, how is that seeing that in the wild? Is it exciting? Is it something kind of like you hope to see, do you hope to see more people doing that type of thing? No, no, we, we hope to see it. I

[00:14:13] **Josep:** mean, look at the end of the day, innovation can happen anywhere, right?

There is no prototype that doesn’t have some value, right? And there is no company that doesn’t provide some value. The other thing. Which could be discussed is like why are those things are fundamental and can really affect the ecosystem on the long run to for the benefit of the users, which is one of the brave missions.

Or they’re just like, like, lemme quote, application layer things, right? , well, that can gather a lot of attention, can gather a lot of press, but at the end of the day, they are not, they’re not fundamental, but still, they provide value. We look, we copy, they copy from us. it is like cost evolution at the end on the benefit of the user.

[00:15:00] **Luke:** And digging into the fundamentals a bit too, Brave’s always big on privacy, right? What’s the privacy approach with the answer engine? How does that kind of compare to what’s out there? Should users be worried of, okay, I start to treat this more like a AI bot, right? Like, and I’m worried about what I’m inputting, you know, that kind of thing.

how, how’s Brave approaching this?

[00:15:18] **Josep:** For answer with AI, we treat it exactly as a query, which basically means that we do not keep a user history of the queries that the user does to break. So we have actually no technical ability to do a profile of someone. Even the data that we, that we get. We don’t have personal identifiable information, but even the IP gets dropped before it reaches to us, right?

Oh, wow. For, for privacy. So long story short, we have no concept of sessions, history, or anything like this. That’s actually a big departure, right? Because, having user sessions can be beneficial, especially for like, AI tasks, right? Because it’s good to have some context of prior answers, but we, we prefer not to do it because first, You can get almost the same value, if not the same, without the risk that that entails. User profiles are very dangerous, right? I mean, imagine, and companies may have the highest moral standards, no question, right? But if the government were to ask the data, you would be obliged to give it to them, like with a judge involved, right?

But anyway, that data, uh, it’s not to have it, right? So we do not have it. So we actually sleep very well at night, knowing that. If someone gained access to all our data, they would not be able to learn who are the queries of loop. Oh, like what? I love it. You have to, like, yeah. Yeah, I’m too late,

[00:16:52] **Luke:** asking too many weird things.

No, I think I, you know, but such a cool thing hearing you say that. I mean, you know, like had a search in, in what we’re doing here, because it’s literally the same thing that Brendan said too, from the beginning of the company, right? Like where it’s just, you know, they can’t take what they don’t have.

I think, you know, even more now than ever, people are seeing how their data is being impacted. Just, you know, even by good actors that are not even doing anything necessarily bad, but just the fact that, you know, software things happen and, and, people reach systems, right?

[00:17:20] **Josep:** Accidents can happen. And also like a good actor today can become a bad actor tomorrow.

this premise on privacy on why privacy is not something that needs to be sacrificed to build good tech. That’s like the DNA of Brave. And that’s actually one of the reasons why Remi and I joined Brave two years ago.

[00:17:38] **Luke:** Right. I mean, what a journey too. It’s been, I think, you know, just seeing like, I mean, in the past, you know, six months, it’s just been awesome from when we had you here, last time to now.

And, and, you know, hearing Remi talk about this stuff too, it’s, it’s been really cool to like, see just how fast the iterations have been and, how you guys are keeping that ethos alive with what you’re doing. I’m going to ask you guys now too, cause, we talk about this sometimes with, prospects and partners and things like that around how, you know, Brave’s really like the only other, you Independent option out there.

Like, and especially, I mean, for me, it was surprising coming from, you know, the advertising and monetization world before it came to brave, like, I thought that was a small circle of people, but then you start to look at the search world and it’s even smaller, right. We’re talking about using like the in house AML, AI ML and fine tuned LLMs and.

Open source LLMs, like how important is it that Brave is independent when looking at the landscape? And maybe, you guys can give the audience a sense because I have a feeling it’s really not well known just how small of a circle it is out there with indexes and a search out there.

[00:18:38] **Josep:** Yeah.

Independence is like a very odd quality, right? Everybody knows what it is, but it’s difficult to actually define. Brave’s mission is to, again, like build, Equal or better technology than big tech without compromising the privacy, right? And you cannot do that without building it period Because like if we’re if brave was using i don’t know google or being api There would be a dependency there where we could be a stronghold If only because companies can can go rogue, but also like terms of service can change So there’s like no real there is no real alternative, right?

So we need to build that is something that not everyone wants to do There are like many people who are, again, like working at the application layer, right? They want to actually build some cool feature or cool product that satisfy the user needs. And that’s totally legit, right? My only wish would be that they would be a little bit more transparent about it, right?

Right. But because in a way, why do you have to be transparent about it? Because basically, like, because users make a choice, right? And when people make a choice, they are giving with their boat, they are giving some value to the choices they make, right? I do believe that people would be actually, would do different choices if they actually knew the whole implications of the things they are doing, right?

Right. They always like, I use this analogy, which is kind of like the, the person like who drives An electric car, but doesn’t care where the electricity comes from. Sure. Yeah. You can drive a lot like your car because it’s nice looking. That’s awesome acceleration, but then don’t claim it’s beer. I mean, but don’t claim it.

That is good for the environment. If you do not care about where the electricity comes from. Right. So do you want choice? Then support brave. If you just want answers. Well, but it has answers too, but other people have answers. No, it’s not, they couldn’t be better or worse. We do believe it’s better. One important thing to build our own is that technology and our own search is that basically we changing the problem.

We can actually change the underlying architecture and the underlying system to provide different types of data that are more relevant to a new feature, right? So if you use an API at the end of the day, you know, like the set of ingredients is fixed. Right. We can make our own ingredients as we move along.

And that’s a fundamental reason why, you know, we can be one step ahead and of course be more sustainable, which is like what matters to us.

[00:21:20] **Luke:** Yeah. That’s awesome. That was a great way of putting it with the ingredients too. We’ve seen too, I mean, one of those interesting things that think people aren’t really aware of either is just, we have this whole verified creator system with Brave and we even introduced a premium right before we even had monetization on search.

But there’s a real, it seems like there’s a real appetite from people that do know to support solutions that are different and are breaking free. I mean, even the secondary effects of these things, when. Geopolitical things happen and then something, it might impact how results are presented, right?

Because, and it might not even be the impact of directly of the partner, but it’s just some, it’s how something’s working underneath. And we saw some of this too, like with Russia and Ukraine and Dukkako, for example, right? Where it was kind of controversial and they’re kind of, I mean, when you’re married to a partner, you’re married to a partner, so I think it’s a, it’s a really good point, right?

[00:22:07] **Josep:** It’s not only the, Potential censorship, so things like the terms of service might might change. I mean, the service does not allow to do AI integrations, perhaps some search engines that seem to be lacking on AI features is because of the terms of service. But nobody knows for a fact, right? Because it’s not being publicized in any case, like, but, but bottom line, what is important is like everyone provides some value, right?

Brief. It’s not just to build a product. It’s a product that doesn’t sacrifice privacy and that is from the, that is from the fundamental, right? That is provides an alternative. And right now, if you are in the US, most of the people listening probably are in the US. There’s only three search engines that have their own index, is Google, Microsoft, and Brave.

And the sizes of those three companies are pretty different, right?

[00:23:04] **Luke:** I mean, that’s something that people don’t realize, I don’t think, is that even when you’re going to other search engines, most of the time they’re just powered by, you know, one of these big companies, right? I think it’s, awesome that you’re putting light to that too.

I mean,

[00:23:16] **Josep:** some of them now, because we have a search API and some of the. Those search engines that they provide some value again. I mean, it’s not, I’m not trying to like talk them down or like think that we are better. No, no. It’s just like, we have a different value of position.

[00:23:30] **Luke:** Right. Totally. We came into market at a different time too, right.

Where we could, that’s one of the things that I see with ad tech too, where even if people aren’t necessarily malicious, right, like their intentions weren’t bad. It’s just that when tech exponentially. Scales and adoption, right? Sometimes important ethical questions get ignored, but we’ve had this great positions coming in later to where we can kind of, from first principles, really tackle these things that need tackling, which I think is fantastic that you guys are doing, but speaking of which, Remi, like how much traffic is a new answer with the AI system handling?

Are you guys seeing like a lot of use?

[00:24:05] **Remi:** I mean, what we’ve seen so far is that, you know, we are handling around a hundred requests per second. On this new system, right out of like more than 300 requests per second. So as Joseph said, it’s like around a third of the queries, you know, depending on the language and countries and stuff like that.

But then this hundred requests per second translates into more than 500 concurrent generation sessions because, you know, we get a hundred new requests every second, each of these requests takes a few seconds to generate the answer. Right. So overall the load on the system is much higher. Okay. And if I can maybe just like elaborate on how this is broken down is like, you know, if a user can trigger answer with AI by a press of a button, basically, right?

So like, you could, as a user have answered with AI on any query you make, right? But then what we’ve seen drives the load is basically this automatic triggering mechanism that Josette talked about. Describe where we actually decide we try to find the best, you know, queries for which answer with AI makes sense.

And then we’ve seen that tweaking these heuristics and this decision can increase or decrease the load. And as a matter of fact, because we are now extending this, this triggering mechanism to more queries, it’s increasing over time and we expect it to keep increasing in the coming weeks as we handle more types of queries automatically.

[00:25:22] **Luke:** And just for folks that are unaware, that might not know what we’re talking about when you’re talking about forcing it to answer with AI, there’s this like a little four diamond icon that’s next to where kind of the magnifying glasses. If you click on that, it’ll force it to answer with AI, right? Like, I’m just curious on that front.

Like, are you seeing people, like, are we measuring that? Are you able to see like how often that gets invoked or is it, are people like, Using it often or people kind of, I mean, I know with defaults, we tend to see people just kind of let the thing do what it’s supposed to do, but are you seeing users like invoking that a lot?

[00:25:55] **Remi:** Yeah, I think it’s, it’s fairly small, but as you said, defaults as are what matters in the end. Right. So like, even though. I mean, there needs to be a bit of time for people to kind of learn about the future. So we’ve tried to do some in, you know, in page education where we have this little purpose and you can click on this button, right?

When it makes sense. So we’ve seen that in the past with code LLM, so this like code assistant that we’ve built and integrated last year. And over time, the clicks rate increased as people realize, okay, I can do it. Right. And then in the future queries, they start doing it more and more. And I guess there is a bit of that, but

[00:26:33] **Josep:** it’s very low, as you said, but that’s in a way, that’s like the point, right?

Because that’s why we put so much emphasis on the automatic triggering. Right. I mean, if too much, but of course there’s a confounder there, right? I mean, we do not know if, but in principle, I think it’s like less, a little bit less than 1%. I’m pretty happy about it.

[00:26:54] **Luke:** And that’s one of those things, I think, too, that’s kind of not necessarily unique to us, but the fact that we have so many early adopters, you know, that try out brave stuff, the people that are more likely to kind of push all the knobs around, you know, like, in a lot of cases, at least from what I see, because it’s been interesting for my position, you know, being out there with the community a lot is that, you know, I see what I see often where it’s, anecdotally, some people want AI to answer everything, but then some people are really repulsed by the idea of AI answering everything.

Right. And when I see that, it usually means we’re doing something right. If I see things skewing too much one way or the other, when we release these things, it’s, but, but yeah, I think that you nailed it. Like the user shouldn’t need to know whether to answer it with AI or not. It should just give them a good answer, right?

Like whether it’s a search result query or,

[00:27:35] **Josep:** That’s our bet in a way, right? I mean that we don’t want to go either one way or the other. We believe that both options have values, have intrinsic values, and also like to always like have the choice of the user, right? Because at the day, the query intents are very complex.

Same query can have different intents depending on a context that we do not have. Perhaps you are like in the mood of reading a lot of text, or perhaps you just want to know like, what is the last album of Lady Gaga, right? I mean, the same, the same query last album of Lady Gaga can be anything. It could be like the actual answer.

you actually want to buy it or like, you want to know the ups and downs of the story behind it. Right. It’s not, it’s a no.

[00:28:24] **Luke:** Well, and it’s one of those things I really love about this too, is that it’s kind of like when I’m using it, it feels like a, for a lot of the zeitgeist is kind of looking at, at AI and thinking, okay, it’s a little staple, like a, what’s his name from Microsoft days.

I don’t know that that Clippy, yeah, yeah. Where, okay. It’s constrained into this little sidecar of a prompt. Right. But when I’m using this feature, it’s actually like, okay, wait a minute. Like, here’s something that. I don’t need to need some early adopter to use it. Everybody’s using search, right?

It’s one of those things where it’s actually useful AI application in something that you can get in front of millions of people and actually have them use it right away, which kind of rare, right? One thing I want to kind of ask about that though, is, you know, when you look at like these prompts, there’s a lot of concern around like hallucinations with results.

Like how are we handling that at Brave when we do things like this answer engine, where it’s kind of almost like a hybrid of, The serpent and what you see, like with these AI prompts.

[00:29:19] **Remi:** That’s a good point. I mean, it’s hallucinations are most likely the biggest issue with LLMs as we’ve seen, you know, in chat GPT and like the answer confidently and you’re like, is it true or not?

Right. So one thing to remember, I think is the answer with AI is like by design. grounded in the search result, right? So like, this means that for any user query, we already providing relevant information to the model. So already it’s kind of constrained to a scope, which is much more limited compared to like chat GPT, where it’s like, you know, you ask a question and then the model can pick up any knowledge it might have from its pre training, right?

So like the context matters. One caveat on that is that. Grounded doesn’t mean truth, right? Because what the answer reflects is the quality of the search results. And you might have multiple perspectives in there, and we try to make sure that the final answer reflects all of them if possible, right? So we try to make sure you get the best overview possible of the search results.

But this doesn’t mean, you know, This is truthful and you still need to check, you know, critical, critical facts, right? But at least you minimize the likelihood of the model just going completely astray and, you know, like inventing,

[00:30:33] **Josep:** making up something. I would like to like to congratulate the team, but especially Rene, because like those things are really like an art, right?

Like on how you actually like, because like all these LLMs. And systems that are actually fairly new, might sound stupid like what they’re going to say, but nobody actually understands fully how they actually work. So it’s kind of like, you know, like what happens with MLM is that you actually put them in an input, the output amazes you.

But then if you want to make them do something specific, it usually refuses to, right? And there is a lot of like, back and forth and trial and error and educated guesses that the team has been, that’s put on it just to make this kind of like thing that, well, I mean, the, the output of the answer should be based on the.

Content of the web and on the knowledge of the content of the web, rather than the knowledge of the model itself, all the things, I mean, congratulations to Remi and Tim, because it’s a

[00:31:36] **Luke:** good point. I was going to sing your praises a little more. I mean, it’s one of those things where when I was seeing, you know, having been at Brave for a long time, when we brought you guys on with the search engine, the comparisons we always used to hear from people were like, okay, how does this compare to DuckDuckGo?

But like, when I see what you guys are doing now. The comparisons I’m seeing from people are like, I can use this instead of Google, right? Like it’s getting to the point where I can like, it doesn’t happen unless you have a good product that you’re putting out there, which, I mean, all this thought and care and consideration, when, especially when you compare it to how, like I used to looking at a windows 11 install and seeing that I’ve got this.

Co-piloting everywhere that I didn’t ask for, right? Like and, and, and trying to force these things on me all over the place. Like it’s a balance, right? Like, and, and, I think that you guys are doing a, a lot of great work on focusing on where these things could be most useful and then really kind of attacking that and trying to give quality, you know, with that, that’s useful.

Which is not an easy thing to balance, right? I mean, like, you know, we’re still finding our. Product market fit as a, as a whole company and how you guys are in here kind of like with the scalpel, trying to kind of take on some giants, which is awesome, I think, how do you guys measure quality when you’re looking at these things?

I mean, cause it is, it’s almost like a higher bar that you guys have to aim for because it’s married with the search result page and people are using that for research and thing like, how do you guys measure quality when you’re looking at these AI answers?

[00:32:56] **Remi:** Yeah. Yeah. All right. So it’s a great question.

And quality in search is already hard. I think if you put LLMs in the mix, it becomes even harder because the output of this. Models are non deterministic by nature, right? So you have like a search index which is constantly being updated, refreshed, new pages, pages updated, new events. Then you have a model which whose output is non deterministic, you mix the two, then the output is Kind of hard to reason about in an automated way, right?

So what we’ve done is like, we have multiple, let’s say, layers of testing. the first one is automated testing. So we do manage to kind of, you know, replay hundreds of queries, real queries that we’ve seen for which we know what kind of things to expect in the answer, right? If you take, let’s say, height of Everest, well, no matter it’s phrased, you want to see 8, 800 meters somewhere.

Right. Like you can do it a bit fuzzy, of course, but like you kind of have this expectation. We can do some checks on the, you know, the entities that you expect in the answer on the format. So it’s not perfect, but it gives you kind of a good approximation of you didn’t break something fundamentally if you make a change, right?

So it’s like very helpful to iterate. You make a change, you run it again. It takes maybe a couple of minutes or three minutes. So it’s like very nice. And then in the end, you still need human assessment, kind of validate any meaningful change. So we do have a quality team whose job is to actually evaluate the search results, but now also sensor with AI.

And we’ve built like custom tooling for that. So the, I mean, one of the tools we’ve built is like some kind of chatbot arena internally, where you have a blind testing tool, you get a random query, you get a screenshot of two versions of the system. Randomized. And you need to say which one is better.

Right. And it’s used by the quality team. It’s used by, you know, anyone internally in the team. So we get like multiple opinions because as we’ve seen, you know, different people might prefer slightly different things. People prefer more verbose, less verbose, more concise, etc. Right. So it’s important to have a bit of a panel of different people assessing to get kind of a balanced view in the end.

Right. And then of course the last part is dog fooding. I mean, everyone that you know in the team uses Brave Search, every day at work, outside of work, and we get like great feedback from that. So it’s like super valuable.

[00:35:21] **Luke:** How’s the user feedback been so far? Are you seeing anything that’s kind of surprising?

I always see this when we throw stuff in market, you know, you see we few things or you’re like, whoa, I didn’t anticipate that. You know?

[00:35:30] **Remi:** Yeah. You have no idea what , what are people gonna do . I, I think one data point is, it ties back to what you said. A bit earlier, but some people saying, you know, there is AI.

How do I disable this thing? Right. And we’ve seen, you know, on communities like Reddit and Hacker News, people write, Oh, I didn’t like it, or I didn’t know I needed it, but now that I. See it in action. I cannot do without it. I think that’s the best feedback because people realize that this is valuable. It helps them, you know, find answers faster, or maybe it helps them do what they could not do at all without rates.

So that’s like pretty amazing to, to see this kind of feedback.

[00:36:08] **Luke:** What about you, Joseph? Anything surprising coming in?

[00:36:12] **Josep:** No, no, we have a lot of very good testimonials. We, of course, have a couple of testimonials that like this is factually incorrect. And then we actually checked and the web is wrong. Some other things are opinions.

There is a lot of like controversial topics where no good answer exists that doesn’t offend someone and answers just make that thing worse because someone is going to get offended in a way or another, but in general, the feedback is very good. And like Remi said, like the biggest positive feedback is that we have shown these answers to a lot of people, but like not everyone is like, on Hacker News all day long, but I know all the startups or they, or they did have, YouTube tutorials that they do X, Y, Z, right?

And we do serve about like 27 million queries per day. One third of those trigger the answers, right? So that’s almost like a, let’s say rounded up 10 million answers per day. That’s a lot of eyeballs, right? And it has raised awareness that that thing exists. For

[00:37:22] **Luke:** me too, looking at this space broadly, it’s like, you see when all the hype cycles happening and people are starting to use their buzzword bingo about stuff and you know, Oh, AI is ubiquitous.

It’s everywhere. What this has done for me is it’s kind of actually brought it home in a way where it’s like, look, like, sure, these things will be ubiquitous, but really like it. Putting this stuff in search, search is ubiquitous. Everyone’s using it, right? Like, like this, this is one of the best use cases for AI.

I think I’ve, I’ve, I’ve seen to date that as far as like utility and mass and, and actually like getting something that people could have help from right away that they’re not going to forget about, which is also something that I’m getting users to change their habits is really hard. And I think that, you know, by approaching this with this way and search, it’s really, really clever.

And. And with those ethos that you guys kind of were covering earlier aligned so well with what we’re doing here. I think it’s, it’s really kind of an under, underrated, undervalued thing in market right now, when you look at all of the kind of stuff that’s driving the hype out there. So I, I, my hat, tip my hat to you guys for cooking all this up.

This is amazing. and, I think this is really going to be impactful. I think one kind of out there question, like, you know, looking at the horizon for things, right. And I know Brendan talks about. There’s a lot in, in our ad platform too, kind of leverages some of the local data. Like when you guys look at things like answer engine long term, right?

Like beyond, I’m talking, you know, future, future, like do you see a a, a potential here for having it answers enhanced about, based on what’s locally in my browser by where I am in the world. Like all of these types of like, you know, next level types of results you could get. Do you see us going in that direction eventually?

[00:38:57] **Josep:** Yes, I mean, where you are in the world, I mean, already being used, but in any case, like, you mean, like, more like a personalized context? Yes, but that doesn’t have to be done in the context of, of Leo, right? Like the in browser. AI, right? That’s why Leo is like the in browser AI of, of reform and your audience shouldn’t be familiar with it right now.

There is no integration per se, but we are working heavily on, on how to integrate, right? Because like, you know, where they are complimentary, right? Like a search is more like a, a one off for a task. Of course it can be iterative, but that’s not meant to be where Leo is more like the user agent, where you can.

Like, you can expand and you can, like, really dig down into a particular topic. And of course, because it’s local, it could have like local information that is private to you, user sessions, and all the things that we do not want to keep. Again, for privacy considerations, they could be kept in the browser in a much safer way.

So we are like working on that. That’s kind of the big step forward. We haven’t done it so far. It’s mostly because the, you know, I just want to stop shop. I keep referring to right now because right now it’s actually difficult to transition from one system to another without the user, without the user.

Getting lost in the, in the way. Right. So there has to be like, once we have the integration worked out where like people understand clearly, like what’s going on, what’s going to get happened when you do something. Right. When we work out on this details, which hopefully is going to be very soon, then we will have like a clear winner, right?

Where like, you know, you start on search, then you transition to Leo and then you do like the, the heavy lifting. Or the other way around you’re liking or leo can actually have access to real time information using research

[00:40:47] **Luke:** Yeah, it’s really interesting because it’s kind of almost like we’re catering to two sides of a coin where you’ve got real like power AI users that might be using something like Leo and early adopters or people that are using it as part of their, you know, even a work function.

Right? And then you’ve got also like everybody else is doing like a search. Eventually these things kind of like a purging effort for both sides is really interesting and it’ll be cool to see them come together. I know we’re way over time. I really appreciate you guys making the time to come here and talk through this.

Is there anything we didn’t cover that you all want the audience to know about that they might find interesting whether it’s about the AI engine or about any of the broader stuff you guys are working on?

[00:41:29] **Remi:** And maybe we can touch briefly on some of the challenges that we faced while building it. Yeah, please do.

[00:41:34] **Josep:** I mean, to me, because that’s what I love, you know, building and solving problems, that’s one of the most interesting aspect of it. and we faced like quite a bunch of them.

I mean, there are two kind of categories of challenges. One is like performance because, you know, with the traffic that we mentioned, it’s actually not a trivial thing to serve, you know, these big LLMs at scale, although we did have a. Lot of experience because we’ve been, you know, using transformers for years now, but on, you know, smaller models, a stricter latency budget and everything, right?

[00:42:06] **Remi:** So like this new feature requires like a different kind of way of, of, of deploying this model. It is like streaming continuous matching all of these things. So we have had to do a lot of work to make sure we find the sweet spot in terms of costs, because we don’t want to, you know, spend mindlessly all the money on the GPUs and performance.

So that the users, you know, get a great, great experience that is fast and snappy, and they get the answer they need quickly. Right. Second aspect is quality. Of course, we’ve touched on it. Just want to maybe add like a few, few more elements on that, like to take a step back, like, you know, when you have a traditional search engine, like What you do is you take any user query with any intent, and you’re going to try to find the top 10 pages out of billions that you have in your index, right?

And that’s already extremely hard, as we know, because we built it, right? Built it. At this point, you kind of expect the user to go open a few pages and find the answer wherever it is. Maybe it’s in a paragraph, maybe it’s Whatever, right? But you know, like from the perspective of answer with AI, it’s not because the first page on the result set is there, but the whole content of the page is relevant, right?

Maybe it’s a subset of it, right? So with answer with AI, you kind of take on this job for the user and you need to go look. in a much more granular way to pick up the right information, right? And the right information might be, as I said, like paragraph, maybe it’s a single sentence, maybe it’s a table, maybe it’s a row in a table, maybe it’s like some structured data, you know, like JSON schemas, these kinds of things.

So we’ve had to kind of, Leverage a lot of technology we had, you know, like embeddings, models, Q, Q and A, question answering models, semantic understanding, which we already had built in house for like all the other search features we built over the years. But now we’re able to leverage that to go, you know, much finer grained.

And go pick up the right context and then have the model work on that and produce the final answer. So I think that’s kind of this mindset change is pretty interesting and also where the challenge lies, right? When you, when you build such feature. Maybe one last thing is on this, like, you know, entities we’ve mentioned before, I think Joseph touched on that earlier.

Some answers are texts, some answers are not text, right? You have like cards, maybe like a thumbnail. It’s kind of interesting because What we are doing here is you take a stream of tokens from a model and then on the fly, you’re transforming the stream of token into a different representation, right? So you’re like detecting, oh, this is about entities of type, let’s say albums, right?

And then you kind of fetch more information on the fly and then present it in the end with like all the metadata that makes sense, like some label. And title and stuff like that. And we’re going to expand on that in the future. So it’s going to be hopefully more and more useful for the user. But it’s kind of an interesting challenge to, to build this system.

[00:45:14] **Luke:** Yeah. I mean, I just remember even before any of this AI stuff or summarizer got worked in, like being on a call with a colleague, Jan and Aldo, and he’s pulling up, we were talking about a partner. He’s pulling them up and comparing them just on the basic search results and making sure that they’re fast enough.

And one thing that’s kind of stood out here is that, yeah, there is kind of a little bit of time, but if I compare that against answer outputs on like, you know, chat GPT or other things, it’s, it’s much faster than what I would typically get in a bot, right, or prompt. Whatever you guys are doing there, it sounds like you guys are having a chisel at some pretty interesting, you know, automation, custom stuff to make that performance side of it works, but it’s cool.

I mean, like, yeah, it is neat to see this kind of richer experience when it, when it’s necessary. But I really also kind of like what, what Joseph’s talking about too, where like, I think part of the wrench is that we don’t have to show you something every time, getting that part right is, is much harder than people think, I think, or appreciate, but there’s value in that too.

Yeah.

Just so people know, I mean, like some of this is, is probably obvious, but, but like, you know, if people see a result that they think is an accurate, or if they see something that could be improved, like I know there’s feed, there’s always in feedback loops and in search, like what’s the best way for people to get you actionable information?

Is it to use those feedback loops and like thumbs up, thumbs down, things are in the product or what would you guys recommend like specifically on quality?

[00:46:35] **Josep:** There is like a feedback button on every result on the page. A fair amount of people submit feedback, probably only a fraction of the feedback.

Sometimes actually like I’m surprised to see like how often the feedback is positive, which means that we have very nice users who actually report positive feedback, which is rare. But that’s one way. Then for things that are like really offensive or really like dangerous, Like community forums on the web or Twitter is also acceptable for like things are dangerous.

Last on the list, I mean, if we actually have some, because like the web could contain like personal information, you know, like a phone number, like names, things like we do respect the right to be forgotten that is mandatory in the U S on the EU, but we expand it also to the whole world. So if there is like some data that shouldn’t be indexed, There is like, an email where, like, privacy at brave.

com, where like, you can submit and actually it’s not privacy, don’t check the email later, but basically like people can submit like, read to be forgotten, which is also important. An important thing, right? Because the web, as Remi said, the web has everything for the good and for the bad.

[00:47:53] **Remi:** Everything and more.

[00:47:56] **Luke:** Great point too. I mean, about, about people, you find information in there too. And we just actually interviewed Pat Walsh recently too. And

[00:48:02] **Josep:** yeah, Pat is the one who’s reviewing those cases because those cases is not that you can send URLs, like, okay, I want those removed. No, no, I mean, that has to be, you have to prove that you actually are the person behind that, that thing.

And that’s like. Damaging for you, you have to demonstrate, certain aspects, but then we, we got, we get those as any search engine there is that has its own index. Those are problems that others do not have, but we do have that because, we need to clean up our own index.

[00:48:30] **Luke:** Joseph, Remi, I really appreciate you guys, coming on the show today.

I’d love to have you all back too, when we’ve got more new things to roll out. Thanks so much. Until next time, have a good one, you guys.

[00:48:43] **Josep:** Thank you for having us.

[00:48:47] **Luke:** Thanks for listening to the Brave Technologist podcast. To never miss an episode, make sure you hit follow in your podcast app. If you haven’t already made the switch to the Brave browser, you can download it for free today at brave.com and start using Brave Search, which enables you to search the web privately. Brave also shields you from the ads, trackers, and other creepy stuff following you across the web.

## What the Brave Search answer engine can do

The secret ingredient of an answer engine is not the LLM that powers it, but the combination of a model with up-to-date, reliable data. Such data can help supply the context from which the model derives the answers it presents to the user. Or, to put it another way: an effective answer engine requires *both* a model *and* access to a search engine. With API access to a search engine, even [individual contributors](https://www.youtube.com/watch?v=43ZCeBTcsS8) can generate a reasonable answer engine.

This is why Brave Search—with its index of 20 billion pages, curated and cleansed of the SEO spam and junk content that plagues other indexes—is uniquely positioned to provide such a powerful answer engine. It has the data needed to generate an accurate and timely answer, and the context.

![Answers enriched with text and other media](/blog/answer-with-ai/images/image6.jpg)

Answers enriched with text and other media

With the new answer engine, Brave Search aims to provide not just answers, but an integrated system to satisfy the multiple intents a user might have, and to do so at scale (currently Brave Search serves more than 27 million queries per day). Loosely speaking, these intents fall into one of a handful of categories:

* **Navigational**: Queries for specific sites, such as “Facebook” or “Twitter.”
* **Informational**: Question-based queries, or those seeking information, which generally fall into two subcategories:
  + **Specific lookups**: These are often served by rich user interfaces built around structured realtime information (e.g. currency conversion rates, weather, or sports results) or custom widgets with non-real time based, deterministic data (e.g. unit conversion or time and timezone conversions).
  + **Question-like queries**: Queries such as “How do I find north when hiking?”
* **Commercial**: Queries with the intent of finding or researching products and services.
* **Transactional**: Queries with the intent of completing an action (e.g. buying a product).

Given relevant context, most existing answer engines do well at informational, question-like queries. However, they tend not to perform as well on other kinds of queries. With this latest release, Brave Search will default to an answer engine experience for likely informational, question-like queries.

![Answers for informational queries](/blog/answer-with-ai/images/image3.jpg)

Answers for informational queries

For all other categories, users can trigger the answer engine on demand by simply clicking *Answer with AI.* This offers a best-in-class experience of both options: an answer engine that’s both predictive *and* optional.

Brave Search’s generative answers are not just text. The deep integration between the index and model makes it possible for us to combine online, contextual, named entities enrichments (a process that adds more context to a person, place, or thing) as the answer is generated. This means that answers combine generative text with other media types, including informational cards and images.

![Answer with AI results](/blog/answer-with-ai/images/image4.jpg)

![Answers enriched with text and other media](/blog/answer-with-ai/images/image7.jpg)

*Answer with AI results*

The Brave Search answer engine can even combine data from the index and geo local results to provide rich information on points of interest. To date, the Brave Search index has more than 1 billion location-based schemas, from which we can extract more than 100 million businesses and other points of interest. These listings—larger than any public dataset—mean the answer engine can provide rich, instant results for points of interest all over the world.

![Result for point of interest](/blog/answer-with-ai/images/image1.jpg)

Result for point of interest

![Summary of top stories related to a current event](/blog/answer-with-ai/images/image2.jpg)

Summary of top stories related to a current event

![Summary showing cited sources](/blog/answer-with-ai/images/image8.jpg)

Summary showing cited sources

## How to try Brave Search’s Answer with AI feature

Brave Search can be accessed by anyone on the Web at [search.brave.com](https://search.brave.com), and is also the default search engine in the Brave browser for multiple countries. *Answer with AI* is available for all Brave Search users for searches in English, French, German, Italian, and Spanish (the answer engine functionality is available in other languages as well, but some answers may appear in English). It’s available on all platforms, on desktop and mobile.

If Brave Search is already your default search engine, simply start a search in the address bar of your browser. For question-like queries, the answer engine should produce an answer by default, which will appear at the top of the search results page. Users also have the option to request answers on-demand by clicking / tapping the *Answer with AI* icon that appears beside the search bar on any search results page.

![Answer with AI](/blog/answer-with-ai/images/AnswerWithAI.gif)

The Brave Search answer engine is free to all users, and we hope to keep it this way, as we believe this is a natural evolution of search engines. In the future, we may also add a paid option, with premium experiences such as the ability to have an open ended chat, possibly in conjunction with [the premium options offered by Brave Leo](/leo/), the AI assistant in the Brave browser.

## The impact of answer engines on the Web

There is a clear demand from users for convenient methods of consuming content, and AI-augmented answers are a key example. On the other hand, delivering on this demand can contribute to the erosion of the incentives for publishers to put out content on the Web, ultimately changing its very nature.

This challenge is not unique to Brave Search, but present across most AI-powered answer engines and chatbots, premium or open. Brave, as both a browser and search engine, is aware of these challenges. Consequently, we will be monitoring and quantifying the impact of AI-generated content on site visits, and eventually will address the disruptions that could be caused by the drop in traffic. We hope others are working on this as well.

This is a Vimeo video. You'll need JavaScript enabled to view this.

[![YouTube logo](/static-assets/images/vimeo-logo.svg)](# "Play Video demonstration of 'Answer with AI' video")

*Note: This post was updated June, 2024 to include a link to the Brave Technologist Podcast interview with the Brave Search team.*

[Share on X (formerly Twitter)](https://twitter.com/intent/tweet?text=Answer%20with%20AI%20is%20the%20only%20large%20real-time%20answer%20engine%20that%20puts%20privacy%20first%20and%20does%20not%20rely%20on%20Big%20Tech%20search%20engines&via=brave&url=https://brave.com/blog/answer-with-ai/ "Share on X (formerly Twitter)")
[Share on Reddit](https://reddit.com/submit?url=https://brave.com/blog/answer-with-ai/&title=Answer%20with%20AI%20is%20the%20only%20large%20real-time%20answer%20engine%20that%20puts%20privacy%20first%20and%20does%20not%20rely%20on%20Big%20Tech%20search%20engines "Share on Reddit")
[Share on Telegram](https://t.me/share/url?url=https://brave.com/blog/answer-with-ai/&text=Answer%20with%20AI%20is%20the%20only%20large%20real-time%20answer%20engine%20that%20puts%20privacy%20first%20and%20does%20not%20rely%20on%20Big%20Tech%20search%20engines "Share on Telegram")
[Share on LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://brave.com/blog/answer-with-ai/ "Share on LinkedIn")