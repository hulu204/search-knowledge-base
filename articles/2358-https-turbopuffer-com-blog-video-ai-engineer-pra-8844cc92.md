---
title: 'https://turbopuffer.com/blog/video-ai-engineer-pragmatic-engineer'
company: turbopuffer
tag: 搜索
date: 
url: https://turbopuffer.com/blog/video-ai-engineer-pragmatic-engineer
account: 
origin: en-rss
---
[NEW: Instant namespace branchingNEW: Branching for instant, copy-on-write namespaces](/docs/branching)

# Building turbopuffer

August 03, 2026•AI Engineer × The Pragmatic Engineer

## Transcript

**Gergely** [0:27]:  
I'm Gergely, author of The Pragmatic Engineer, and I'm excited to have a chat
with Simon Eskildsen, founding CEO of turbopuffer, a very technical CEO, and
we're going to have a pretty technical discussion. But before we jump into it,
Simon, I wanted to ask, where did you fall in love with computers?

**Simon** [0:50]:  
Through PowerPoint. PowerPoint. I don't know if any of you know this, but in
PowerPoint, well, you probably know this, but in PowerPoint, right, you can make
the diagrams and stuff when you click them go to another slide. That becomes
Turing complete real quick, right? You can sort of, you know, create very
complicated convoluted games. And then at some point...

**Gergely** [1:14]:  
You know, you make it through the Microsoft Office suite and you discover
FrontPage. Do you remember FrontPage?

**Simon** [1:19]:  
Yeah, I remember FrontPage. It was supposed to eliminate the need for any
front-end developers.

**Gergely** [1:25]:  
Exactly. And it only worked in Internet Explorer. I remember heartbreak I had
one day when someone opened a website I created in Firefox and it was just all
over the place. And then one day I accidentally clicked the HTML thing in
FrontPage and it just showed all of this stuff that I couldn't make sense of and
I just started looking at it and then going online and finding little snippets
that you could add in to make the cursor change and all of these different
things, and then it just sort of escalated from there. Then you upgrade to
Dreamweaver and now you're coding, and then you're like, well, how do you make
the pages dynamic? You learn PHP. And then for me, I exhausted the internet on
Danish language programming advice and I was around 11 or 12, and so I just, you
know, went and got addicted to World of Warcraft for four years, but that gets
you really, really good at English.

**Gergely** [2:20]:  
So you kind of started hacking, getting into deeper. Now the logical step would
have been to just, you know, go to university and learn properly about this
stuff, but that's not what you did, did you?

**Simon** [2:33]:  
I mean, I just started. I mean, you know, then I learned video games, then I
learned English, and then, you know, this massive arsenal of the web now would
be very interesting because the LLMs would just speak Danish to me and you could
just... You wouldn't have hit the wall like...

**Gergely** [2:51]:  
Yeah.

**Simon** [2:51]:  
I did. So that would have been very interesting. Maybe I would have been better
at programming. That would have been nice. And then I, yeah, then I just started
picking up jobs and things like that throughout high school. And when I was in
high school as well, I got exposed to this thing called the International
Olympiad in Informatics. Heard of this thing?

**Gergely** [3:08]:  
Yep.

**Simon** [3:10]:  
And I had an internet friend and she lived in Australia and she was on the
Australian team. And she told me, oh, there's probably something for the Danish
team as well, but I had never heard about it before. And so I found it on some
little mysterious website and then applied and then solved these programming
problems that looked very different from the HTML and PHP things that I'd solved
until then.

**Gergely** [3:31]:  
It's like the algorithmic-ish problems.

**Simon** [3:34]:  
Exactly. It's sort of like this is not actually the kind of problem you'd see
there, but I think it illustrates well the kind of problem that you might get,
right? You can imagine something like, okay, here's like N trucks, here's M
packages, the M packages have these dimensions, give me which trucks which
packages should be in, right?

**Gergely** [3:53]:  
Yep.

**Simon** [3:53]:  
And then do something optimal. Like that's an NP-complete problem you can't
solve that, but you could compete with everyone else in the competition of doing
the best thing. So it's these kinds of problems, right? And so I started doing
that in high school while working for a startup, and then Shopify found me while
I was still in high school.

**Gergely** [4:16]:  
And the whole Shopify family, was it through your open source contributions? Was
it something else?

**Simon** [4:22]:  
It was because I had written an article where I had dropped my iPhone and it
was, you know, the iPhones are a lot, like there used to be a time, right, where
you drop your iPhone and you just knew it was over for the screen.

**Gergely** [4:36]:  
Yep.

**Simon** [4:36]:  
It doesn't really happen as much anymore, like the screens have gotten a lot
better, but back then it was like, yeah, one drop and it was dead and you just
couldn't use it anymore. And so I went back to one of these old Nokia brick
phones, and this is back in 2013, and people hadn't really realized all the
pernicious effects of smartphones at the time.

**Gergely** [4:52]:  
So I wrote this article about how, oh my god, I'm like calling people and I have
my sense of direction back. And I wrote an article about it, and this article
went on Hacker News briefly, and the New York Times decided to feature it.

**Simon** [5:07]:  
No way.

**Gergely** [5:07]:  
And so a lot of traffic was driven to it, and then some astute Shopify
recruiter...

**Simon** [5:16]:  
Put it all together, and I had a call with them. And then I don't think they
realized that I was still in high school, but I had a great call with them. They
invited me on site to Ottawa, Canada. I had no idea what Ottawa, Canada is. I
think the email says something like, what's an Ottawa? I had no idea. And so I
went there, and it was just like walked into the building and it just felt
right. And so I interviewed with them and then said, well, I got to finish high
school first, and then I moved to Canada to work at Shopify in 2013.

**Gergely** [5:52]:  
Yeah, I think that's a legit excuse for like not even worrying about college and
university.

**Simon** [5:59]:  
But it really crossed your mind.

**Gergely** [5:59]:  
It did. I thought I was going. I thought I was doing a gap year. I thought I was
like, okay, I'm gonna go work at Shopify for a year and then I'll probably go
back and do... But I was just... I was very insecure at the time about the fact
that I hadn't studied computer science, and my only exposure had been all the
IOI competitions. It was a pretty good crash course in a lot of computer
science, and if nothing else, it had really taught me that you can just sit down
and read a paper and just figure it out if you spend enough time on it. So I did
that repeatedly. And in my first year at Shopify, every time I heard something
that I didn't know what it was, I noted it down on a piece of paper, and then I
went home, and then that evening I would just read about it because I felt
insecure that, like, well, if someone mentions TCP, surely they know exactly
what's in the three-way handshake and how TLS is layered on top and they've
looked at Wireshark and all of that. I don't think that's true, but that's what
I thought. And so I went and did that for everything that I encountered. So that
was a really good crash course, and then very quickly it became clear that,
well, I just want to continue doing this. I don't want to go somewhere else and
then come back to this because I felt like I'd already found what I wanted to
do.

**Gergely** [7:06]:  
So it sounds like it was a pretty good combination of like you just having this
very natural insecurity, like you're young, you know, you don't have the
education that everyone else has, and inside the company that's just doing
pretty cutting-edge stuff even at the time and even today, right? Like they're
leading. So you just kept self-teaching yourself, like just catching up and go
do I understand that you just went deep in every concept that you understand?
You didn't like just try to understand that surface level, but like go as deep
as you can, search on the internet, buy books, whatever that is.

**Simon** [7:35]:  
I think it was just that I just wanted to keep learning how computers work. And
I think that this is something that I now look for when we interview engineers,
is that you just can't help yourself but trying to peel back the layers. And for
me, that ended up with the infrastructure layer that was, you know, the people
closest to the metal at Shopify. And I would just always sit next to them at
lunch because I was working on the product side, but I just couldn't help
myself. I just wanted to learn what it was when they were talking about a
reverse proxy. I'm like, why is it reverse? I still can't answer that. I mean,
okay. You know, well, what's in reverse?

**Gergely** [8:22]:  
Because it's a proxy, right? I don't know. It's like an inverted index. Like
what's inverted? It's like it's a terrible name anyway.

**Simon** [8:32]:  
Yeah.

**Gergely** [8:32]:  
I mean, it's still better when you get the NAT tables to look up some of those
things. Like some of that, but yeah, I hear you. There's some weird names with
this. But at Shopify, what were some of the kind of hard engineering challenges
that you faced, engineering challenges, outages, like learnings that kind of
defined you that were really also fun at the time or interesting to learn, but
it would have been hard to get it elsewhere?

**Simon** [9:02]:  
Yeah, so I think it was, you know, in the 2010s, there were like a bunch of SaaS
companies that scaled really quickly, and I felt so fortunate to have a
front-row seat to that. And so I ended up on the infrastructure team, and this
was back in, you know, '13, '14, and Docker was coming out, and so we were
containerizing everything. And we were just... every single year we had to...
you know, the growth rates of SaaS sometimes seem quaint in comparison to the
growth rates of companies today, but it was a company that was growing at, you
know, 120, 140 percent year over year. And so every year we were just preparing
for a Black Friday that was going to be a lot worse than the last. And this is
back in the day of we're buying physical hardware, right? We have to like place
an order at a particular point in time and do some interpolation based on that,
and the software also had to scale. And when you're scaling most software, a lot
of the application layer problems end up back at the database layer.

**Gergely** [9:55]:  
Mm-hmm.

**Simon** [9:55]:  
So I just naturally found myself at this layer between Rails and the databases.
Shopify didn't at the time at least contribute many patches to the databases
themselves, but mostly just spent time orchestrating. So we were doing sharding
because, as my dear boss Camillo used to say, you can't cache writes. So there's
a fundamental point where you just have to move beyond a single shard. So I
joined around the time they did the sharding, and they did it, I think they did
the cutover a week before Black Friday, which is mind-blowing and very... but it
worked. And then the subsequent years we worked on things like going into
multiple data centers. We also had this big mysterious Redis server that was
like, you know, 128 gigabytes of RAM, which was a lot at the time. Today it's
not that much, and no one really knew what was in it. And then it went down one
day, and people were like, well, that's super terrifying because people had just
been treating it as this KV store. And so we started splitting it out. We did
all this stuff around making sure that if you visit a Shopify store and the
thing that stores your sessions is down, the right behavior is not just for the
entire of everything to be down, but that's kind of the default failure mode,
right?

**Gergely** [11:13]:  
Bye.

**Simon** [11:13]:  
You're not going to rescue all of that unless you're in a program that really
forces that decision. So we did things like build this matrix out of, okay,
well, this service when this component is down should act this way. And I find
myself writing the test suite for a bunch of that. And then I was like, okay,
well, we can't just mock all of this. And so I came up with this idea at the
time like, oh, what we're gonna do is we're just gonna shell out to GDB and then
into the process and then close the file descriptor to the database to simulate
deep through the entire layer that the database fails. That was a little crazy,
and we never shipped that on CI, but it did uncover a massive amount of issues
in Rails that be upstream and things like that around just like handling
failures at the connection layer. So then I moved on to create this proxy called
Toxiproxy.

**Gergely** [12:01]:  
That's a proxy.

**Simon** [12:01]:  
Have you heard of this before? Yeah, Toxiproxy is just like a Layer 7 proxy that
sits in between you and, well, Layer 4, but in between you and the databases. So
you basically have just like this proxy, and then MySQL, whatever doesn't speak
the protocol, then you can do an API call, say take the database down, make it
slow, and over time it also added Layer 7 things of like do a bunch of failures.
This way you're not mocking the low-level drivers, but you're testing the
drivers and their failure handling as well. So then this entire matrix could be
implemented in CI.

**Gergely** [12:36]:  
So basically the proxy was just like a really thin layer which like was passed
through, but you built the functionality to like simulate problems of database
or things like data corruption or whatever you wanted to do, so you could just
do it in there and then you can... anything that built on top of it.

**Simon** [12:57]:  
Exactly.

**Gergely** [12:57]:  
Okay.

**Simon** [12:58]:  
So you could do like MySQL, you know, proxy.mysqldown and then pass it a lambda
of what you wanted to do, like get this page, do a checkout, whatever with the
sessions table down. And this just uncovered tens of issues, right, in the MySQL
driver in Rails. Like it's just like no one in the ecosystem had been testing
for this, and it was very difficult to see it as in prod, right? Because they're
MySQL down, you're focused on just getting back up and not like what could the
application actually have done. Yeah, it's interesting.

**Gergely** [13:27]:  
Of course, we're going to talk a bit more about databases, obviously, but just
thinking about how a lot of the problems or some of the most gnarly problems in
large systems are always to do with state. And I never connected until now that,
I mean, state is usually there's a database. If there's no database, if you have
stateless services, you know, I mean, you still have problems. You have nodes
going down, you have, I don't know, corruption, whatever. But it's usually like
more isolated. But basically, like if we have state, we typically have
databases. If we have databases and if we can simulate these problems, suddenly
you can... I mean, you can like predict a lot of things. The problem with state
oftentimes is it's really hard to simulate problems happening ahead of time
unless when they happen. So it sounds like you have pretty good success with...

**Simon** [14:10]:  
Yeah, I think to my knowledge, it's still running in like the CI system of
Shopify today. I don't know if anyone in the crowd is from Shopify, but I'm
pretty sure that it still does. And so we wrote all these tests against it to
implement all of these different failure conditions, and it just... yeah, it
worked out great.

**Gergely** [14:29]:  
So you spent eight years in total at Shopify, so like started from like just a
gap year, it just went on a year, a year, and another year. At what point did
you think about leaving and why, and what was your kind of decision framework?
It sounds like you were like an epic running out. Even today, Shopify is doing
wonderful. It's probably doing even way better than you're like, you know, that
growth kind of kept on. So I'm sure there would have been an argument to stay
and, you know, stay on their rocket ship.

**Simon** [14:58]:  
Yeah, so I spent eight years there from '13 to '21. And I think there just came
a point where I wanted to see something different. Again, I've been inside
Shopify since I was 18 years old, right? I've been seeing one other startup in
high school. I was like, if I want to learn more about computers and learn
faster, it might be time to inject some novelty into dysfunction. And so I left
in '21, and I'd worked on so many different parts of the infrastructure, like
caching. Me and Justine, who's now my co-founder, we wrote the entire storefront
for Shopify, which powered almost 100% of traffic 18 months after we embarked on
it. We've worked on running Shopify in multiple data centers. We've worked on so
many database scaling projects, like caching, all of these different things,
right? A lot of the scalability came from the Kardashians launching lots of
products on Shopify, which would force a lot of traffic. But that's eventually
how I left. And so when I left, I didn't really know what I wanted to do. And so
one of the projects I had while I was at Shopify was this napkin math project.
Have you seen this?

**Gergely** [16:07]:  
Napkin math? No.

**Simon** [16:07]:  
No. So napkin math was essentially just this table that I maintain on GitHub of
how much bandwidth can you drive to DRAM? What is the round trip to S3 cost and
how long does it take? How much bandwidth can you drive to an NVMe SSD? How much
bandwidth can you drive to an EBS volume? Just the collection of probably...
there's probably like 50 of these numbers and then a REST script that generates
them all. What all these things cost, what do you like, what does a gigabyte of
memory cost? Two dollars. What does a gigabyte of S3 cost? Two cents. What does
a gigabyte of this cost? Ten cents, right? What does it cost on spot? What does
it cost on a three-year commit? Like I just have a massive table and then create
flashcards for almost every single cell so I know all these numbers. And this
was a project I started taking on at Shopify because I found myself in this role
a lot where I would go in and review a project, right? So some product team
would be like, okay, we got to build this thing. So we got to build this
infrastructure to support the feature. And a lot of the times they would say,
okay, well, we've gone and benchmarked it on database A, but the benchmarks are
not very good, so we're going to go with database B. And I hate benchmarks so
much because that's not a satisfying answer to me. To me, it's like, this does
not drive my intuition. Database A that you're saying takes 10 seconds to do
this should take 10 milliseconds if you do the napkin math, right? If it's a
search query, right? It's like, okay, you're searching for three terms. Each
term has this many documents that match it. That's this many megabytes. We
intersect these many lists. You have DRAM bandwidth on multiple cores of 100
gigabytes per second. This should take 10 milliseconds. You tell me the
benchmark takes 10 seconds. One of us is wrong. Either there's a gap in my
understanding, which is very likely, or you benchmarked the wrong thing. And in
some ways, some reasons, right? It's like, okay, you've done a benchmark. You
didn't realize that your benchmark is doing a distributed query across 100
different nodes, and so of course the p99 is going to be really, really high,
right? Unless you've cut that off or made some different set of trade-offs. So I
just found myself in these discussions repeatedly where people were making
infrastructure decisions based on poor benchmarks. And so I needed some animal
to go in and just be like, okay, we can just do the calculation right here. And
then because I was always doing these little demos or writing little prototype
scripts to demonstrate this. But it was just... I just... the argument of here's
how a B-tree works, this is how many pages we have to visit, this is what a
random SSD read takes, it takes one millisecond, and then present it back and
say this is the difference to your query. Well, like, is the query plan correct?
Like, is there a bug in MySQL? Do we have bad disks? Like, what's the
discrepancy here? And I just got caught with that bug. And so after I left
Shopify, I was just writing a lot of articles about this. I was just like, well,
how long should this query take? And then one hypothesis that I had at some
point is like, okay, well, how many writes per second can MySQL do? Well,
shouldn't the amount of writes per second that MySQL can do equal the amount of
fsyncs that you can do per second? That sort of makes sense, right? Every time
we do a write, you fsync to persist a disk. So how many fsyncs can you do per
second? Well, an fsync takes one millisecond, so you do a thousand writes per
second. That doesn't really match up. Like, I feel like a database can do more
than a thousand writes per second. Why can it do that? So that was one of those
things where I tested, and it's like, okay, well, MySQL on a little dinky box
could do 10,000 writes per second. Well, how is that possible?

**Gergely** [19:45]:  
Mm-hmm.

**Simon** [19:46]:  
And now you...

**Gergely** [19:47]:  
How?

**Simon** [19:47]:  
Just batch.

**Gergely** [19:48]:  
Is it possible?

**Simon** [19:48]:  
Because you batch. So an fsync happens on usually a 4k write, but it's like
that's not intuitive. Like it's actually... I got caught just like, you know,
probably some like 24-hour period where I just got obsessed with this question
where it's like you're writing like the BPF traces and all of that to do all of
this. This is like pre-LLM, so it took forever. And then I found out that, oh,
every fsync was like much larger than I would have inferred.

**Gergely** [20:14]:  
Yeah.

**Simon** [20:14]:  
Like, oh, it's batching. You go into the code and you read it, and then you
found some obscure article by... it's always someone in like a central German
town that's like written some article about like how some intricacy of MySQL
works and a patch that they did to... it's like the entire internet runs on
small towns in Bavaria, I'm convinced. Yeah, and then you decided to start
turbopuffer.

**Gergely** [20:43]:  
Yeah. How did you decide? Did you know what you wanted to build, or was it more
like I want to build something, something databases? Because you were clear,
very into databases. You'd done an awesome job benchmarking like what is the
theoretical limits you are very familiar with. This probably became like world
expert in this niche. And then how did you want to go into databases again?

**Simon** [21:05]:  
I think it was... there were three things that sort of came to a head. The last
project that I worked on at Shopify was Search, and I didn't have a good time.

**Gergely** [21:12]:  
What did you use back there?

**Simon** [21:21]:  
Um, I don't... we don't need to name names of other database companies, but it
was one of the traditional search companies that a lot of different companies
run. And it was just very difficult to get it to do what I did. And I was just
like, the projects that touch that database just... I couldn't get them to
perform at the napkin math. And there's no query planner, and I couldn't figure
out why it wasn't there. And sometimes it tracked, and then sometimes it really
didn't track at all. And so I tried to learn as much as I could to figure out
and like start reading the source code of it, and I was just... I couldn't get
it to track very often. It was very difficult to operate. And so I just... that
was sort of like in the back of my head. I never thought I would touch that
again. Then the second ingredient was the napkin math project because it sort of
just gave me a lot of facility with all of these napkin math numbers of what
might be achievable with the machine if you utilized it perfectly properly. And
then the third one was that doing this, you know, leaving Shopify in '21, having
spent eight years there and doing that time, I did this... I called it angel
engineering. So I was like joined my friend's companies and then I just vested
equity instead of just investing or something like that because I wanted to have
my fingers in... I wanted to like see what else was out there. That's why I
left. And this problem kept coming up again and again and again, right? Like
ChatGPT came out in 2022, and I was working with a company then, and they wanted
to connect a bunch of documents to AI, and that's when the context windows were
really small. So you have to reach for search very quickly, right?

**Gergely** [22:47]:  
It was like a few kilobytes.

**Simon** [22:49]:  
Yeah, it was eight kilobytes or four kilobytes depending on the model. It was
very, very small, so you have to reach for search very quickly, right?

**Gergely** [22:54]:  
Yeah.

**Simon** [22:54]:  
And so I worked with them, and I created a little recommendation engine, and the
recommendation engine was actually quite good. I found out that one of the
co-founders' wives was pregnant through the recommendations that I was getting
when I was running it on his feed. It was weird.

**Gergely** [23:14]:  
But...

**Simon** [23:14]:  
He was recommending... yeah, I mean, it was just like, you know, he was reading
about... like I didn't get permission. I just like... yeah, I don't think anyone
expected it to be good enough. And just like, okay, this thing is working. And
then I ran the back of the envelope math on what it would cost to do this for
everyone, like all the users. This is a company called Readwise, so it's like
articles that you save and then search later. And it was going to cost 30 grand
a month, and this was a company, it was a bootstrap Canadian company. They spent
about 5k a month on all the other infrastructure combined, so just it didn't...
these, you know, fundamentally in a company, if you're doing an investment, you
have to have to run some gross margin on top of whatever you're paying, right?
And it just didn't line up. And so we just didn't ship it. And I worked on...
I've, you know, tuned auto-vacuum on Postgres or something like that, which is a
good pastime. And then I just couldn't stop thinking about why it was so
expensive to store all of these vectors that we were using for the
recommendations. And I just sat and did the napkin math one day of like, can we
just use it all in S3 and do some clustering and then organize the files and
just... and like, maybe you could build that. And then one day I just kind of
said, fuck it, and did it and like sat down and started to write it out. And I
spent the summer of '23 just hammering my head against the wall trying to find
an approach where I can get the latency that I wanted. Because the problem with
S3 is it has really good durability, but latency, we're talking hundreds of
milliseconds, right? Yes, the p99 on a 256 or 512 kilobyte object on S3 is
around 200 milliseconds.

**Gergely** [24:55]:  
And you're saying p99 because like when you're talking large scale, you want to
care about the p99, right?

**Simon** [25:00]:  
Yeah, I think when you're designing a system, you want to optimize for the p99,
and especially because when you're designing a system on S3, generally in every
round trip, you're not doing one request. You're often doing lots of requests,
right? You're going to hit the p99 real quick. Exactly. So it's like if you're
navigating a tree on S3, right? It's like, okay, you get the upper layer of the
tree, 200 milliseconds. You get like another layer of the tree, 200
milliseconds. You get a bunch of leaves of the tree, it's 200 milliseconds. So
in aggregate, you want to look at the p99, probably even the p999 to design the
system properly because you will need to minimize the number of round trips that
you have to make. So I just sat and sketched that out and tried a bunch of
different approaches, and then finally in July of '23, I got something
end-to-end that seemed to work and then rewrote it probably twice and then
released it in October of '23 based on just that summer of working through it.

**Gergely** [25:56]:  
And then you kind of built it all on top of S3 because I guess durability and
all of it and just really good. How did you make it fast?

**Simon** [26:04]:  
We didn't in the beginning, or I didn't in the beginning. It was just me at the
time, and it was really like... it was a project. It was not a company. It was
not... it was to satisfy a curiosity. It was not... I did not set out to do this
like I'm going to go raise 10 million dollars and do it. I was like, I barely
knew what a VC was. I was like, I just had to do this thing, and I was so
focused on doing it, and it was so clear to me that if I wasn't going to do it,
someone else was going to do it. And I just became fully obsessed that summer
with it. And so the first version was the simplest possible thing. I think I'm a
very pragmatic person. I didn't get buried. I barely read any of the literature
on LSM. I sort of like, you know, read a bunch of it, just got the basic idea,
barely implemented that because that would have taken too much time. It was the
simplest possible version of what it could be. Like really what you have to
imagine is that the simplest way you could do this is you run some clustering
algorithm on the vectors, you get the clusters, and then you put the clusters in
files. The files are called cluster one, cluster two, cluster three. And then
you have another file called centroids of the clusters, and then you do the
search by downloading centroids, looking at the centroids, and then downloading
the N closest clusters. There's a few optimizations around merging some clusters
that were adjacent in files and so on just to like control some costs and some
performance, but that was basically it. And then getting that to scale, that was
the first version. And then how do we make it fast? Well, I didn't even
implement a caching layer. I just put the reverse proxy in front of S3 with
NGINX.

**Gergely** [27:42]:  
Do you know what a reverse proxy is?

**Simon** [27:43]:  
I do know what it is. I just still don't know what the reverse is about. But
anyway, the reverse proxy... reverse things. The performance in this case, maybe
that's what it's about by caching, right? All of the S3 objects again.

**Gergely** [28:03]:  
Yeah.

**Simon** [28:09]:  
I had written more NGINX Lua than a lot of NGINX Lua. Very good software. Just
had that cache in front. And then the way that I would do things like deleting
in the cache was just like shell out to XR and just remove things in the cache
and reverse engineer the directory structure on NGINX, and that's what we
shipped. And it was just running on a single server in a TMLUX instance. I was
like, okay, let's see if anyone gives a shit.

**Gergely** [28:36]:  
Yeah, so far, I mean, this is kind of like cool engineering and like a cool side
project and like a bunch of novel ideas and I, you know, like I think just some
hardcore engineering. How did Cursor come into play? Because like when I learned
about turbopuffer, I was talking with Cursor about like how they built their
backend, their database, how they scaled. And they're telling me all these
migrations, and they were telling me like, oh yeah, so we were on Postgres, but
it didn't... no, they did something else in Postgres. It didn't really work that
well. They went to AWS Aurora, which is AWS managed service for Postgres, and it
didn't work well, which is very surprising. And they're like, oh yeah, and then
we went to this thing called turbopuffer, and they worked well. Well, and I was
like, what's turbopuffer? And they're like, oh yeah, turbopuffer, I think they
said we were one of their first customers. And this never computed to me. Cursor
was already massive at that point.

**Simon** [29:19]:  
Yeah.

**Gergely** [29:19]:  
How did you meet the folks, and how did they become... were they the first
customer? One of the first?

**Simon** [29:25]:  
They were the first customer.

**Gergely** [29:26]:  
The first.

**Simon** [29:27]:  
The first. No.

**Gergely** [29:30]:  
They reached out after I just launched on Twitter. I was like, hey, I built this
thing, and frankly, it was like... I sat... it was like, hey, I launched this
thing, and to me, it was like, I am so sick of working on this. Like, I was
like, I've been working on this all summer. I don't know if anyone cares. I only
want to work on this if anyone cares. Let's put it on Twitter. Again, single
T-MUX instance on an eight-core node somewhere in GCP. I was like, if someone
goes to prod, I'll set it up properly on multiple, and like I'll just block on
that. But let's see if anyone cares. It was like the MVP of MVP. Anyone who's
actually worked in the internal on databases would never have had... like would
have had too much pride to ship anything like that. And I've just, you know,
I've worked on... I was just releasing it like a SaaS project. Why can't you
work on a database like it's SaaS? I don't... you know, it's like if anyone uses
it, we'll do it properly. I know how to run software with a lot of nines. But it
was not a proper LSM. It was very, very... it was the simplest version of what
it could be. And then I released it on Twitter. I was like, yeah, you can do a
million vectors for a dollar. And before that, I think the cheapest was maybe a
hundred dollars per million for something that actually worked.

**Gergely** [30:37]:  
Yeah.

**Simon** [30:38]:  
And I knew it was reliable, right? I knew like I had these invariants like if
you shut down all the VMs, like no data is lost, like all the writes are
committed directly to objects, like it has all the same invariants it had today.
And Cursor reached out. And knowing them now, I'm sure at the time, Cursor was
maybe eight people, and knowing the founders now, I am sure that they'd sat at
the dinner table one day and were like, the unit economics of what we have right
now, where all the vectors are in DRAM, are not working. Why hasn't anyone built
it where we can put it in S3? And the actual code bases that are actively being
used, we can put in memory and everything else to sit in object stores, and then
we just hard load it in and out.

**Gergely** [31:17]:  
Yeah.

**Simon** [31:17]:  
Of the cache makes so much sense, right? You open the code base a few seconds
and it's in RAM, and then the queries are as fast as...

**Gergely** [31:22]:  
Yeah.

**Simon** [31:22]:  
Anything else. It made so much sense. So, I mean, at the time, they were... if
you look at some of Aman, one of the co-founders' early tweets, he talks about
using S3 for KV caching and things like that, which barely anyone is still doing
even though the economics like it's...

**Gergely** [31:35]:  
Sorry.

**Simon** [31:35]:  
Yeah, it's very uncommon, and I think it will happen, right? But they were ahead
of their time, and I think they were... I don't know if they were thinking of
building it themselves. I think that's quite likely. And they found turbopuffer,
and it just perfectly pattern-matched into that. Again, I don't know if this
dinner conversation happened or if this was just inside...

**Gergely** [31:55]:  
Oh.

**Simon** [31:55]:  
Parviz's...

**Gergely** [31:56]:  
How fast they had known.

**Simon** [31:56]:  
But it pattern-matched something. And so we exchanged a bunch of emails, and
then something compelled... I didn't know anything about B2B sales. Now I love
B2B sales. I didn't know anything. I was just like, I just want to help them
because they were... they had some unit economics that didn't line up. So I just
went to San Francisco. I live in Canada. I went to San Francisco, and I showed
up at the office. And when I showed up at the office, they were having some
Postgres problem that they were discussing.

**Gergely** [32:23]:  
Yeah, the AWS server problems, yes.

**Simon** [32:25]:  
Yeah, early on. And I was like, oh, do you guys have PG Analyze? And they said,
oh, no, we don't. I was like, okay, let's get that going. All right, let's look
at it. And it was the same thing as it always is with Postgres, which is
auto-vacuum hadn't run enough, and so they had all of these going to heap when
they should be doing index scans and blah, blah, blah. So we were talking about
all of that. And so it's just helping them, right? It was like my, you know, my
database genius was like kicked in, and I think this built enough trust with
them that, okay, well, maybe if he knows how to help us with the database, maybe
he also would know how to build one. And at this time, I'd also approached who I
thought was the best engineer who ever worked at Shopify, my co-founder Justine,
and she'd come on. And the first thing that she did was remove the reverse proxy
NGINX cache with a file-based cache, just a direct cache, which again, great.
Like the S3 thing worked. And so she was online. She was starting to work on it,
and Cursor... Cursor... then that night was like, okay, well, we're going to
migrate. And so they migrated everything over the course of like a week or two
after that. But Cursor was a small company back then, right?

**Gergely** [34:04]:  
Yeah, and they were just in the beginning of their massive rapid growth.

**Simon** [34:06]:  
Exactly. And I told them that I was going to reduce their bill by 95%. And I
did. Like we did. Justine and I did. They came on, and their last bill with
their previous vendor and the first bill with us, it was 95% lower.

**Gergely** [34:20]:  
Yeah, and you're nice for not saying vendors, but I can say vendors. I've talked
to them, and it's in the deep dive about Cursor. It was Aurora specifically.

**Simon** [34:24]:  
So...

**Gergely** [34:24]:  
And...

**Simon** [34:25]:  
This was not... this was not Postgres.

**Gergely** [34:26]:  
No, this was a different one, but it's probably still in the write-up. We don't
need to name names. But yeah, this was... and then what Swala told me is he
said, like, look, there's a few things that we did. The issue never ever do, and
they said one of them you should never ever bet your business on a tiny startup
where you are their only or biggest customer except for turbopuffer. And he
said, I love those guys. So I guess it just comes to show that even in your
case, like to me, what the story shows is you can do things when you build
high-quality things and you're pushing for things, good things can happen. And
on the other side of the cursor, when you're a startup, it's okay to take
sometimes irrational risks when you have conviction. And it sounds to me that
you gave them conviction by showing up in person, by helping them, by showing
that you know your stuff. Like you suddenly brought in your 10-ish or 8 years of
Shopify experience and your curiosity, and they probably took a risk because of
that, not because you were some, you know, random vendor. They probably never
done that so fast. So fast forward today, turbopuffer is now a lot bigger.
You're working on some cool things, but you have this very interesting business
where for you, CPUs are important, right? You run on mostly CPUs. And you told
me a story over dinner yesterday that you met Jensen, and Jensen, he really
wanted to sell you on GPUs. Can you tell me how that meeting went?

**Simon** [35:46]:  
Um, yeah, Jensen Huang, right? Yeah, I just... I never met Jensen before. We
were at an event at NVIDIA, and we were just doing presentations.

**Gergely** [35:49]:  
He and big HQ, super impressive.

**Simon** [35:49]:  
Yeah, exactly. They invited a couple of companies to go and talk about our
businesses and how we can partner with NVIDIA and so on. And I don't know. I was
like, I think I was in a goofy mood that day. And so I went up on stage and I
said, hey, I'm Simon from turbopuffer. And yeah, if you're wondering about the
name, it's like if everything goes south, we can always pivot into vapes. I was
kind of nervous. And this is what I said. And then he said...

**Gergely** [36:26]:  
And...

**Simon** [36:26]:  
Back to...

**Gergely** [36:27]:  
Wait, who was in the room? Was it Jensen? Was it a direct report?

**Simon** [36:29]:  
It was Jensen and then a bunch of the NVIDIA leadership, right? Because you go
there and then you talk about that you find opportunities to partner and work
together, right? And so I said, yeah, you know, so plan B, it could be that we
could pivot into vapes. And then he said, I was already nervous. He said,
judging by your slide, maybe you should. No, he did not. And I didn't know what
to say back to that. So I said, well, Jensen, do you vape? He didn't answer the
question. Someone on the team wrote to the whole company, turbopuffer company,
Simon just asked Jensen if he vapes. And then, you know, this is a great start,
right? And then the team had sort of talked to me beforehand. It was like,
Simon, we got to make sure we don't say the C word. We can't say CPUs. And so I
just couldn't stop talking about CPUs. I was like, AVX-512 is so sick. Like we
love SIMD, and like there's so many CPUs, they're so easy to get. Like it's just
a riot in CPU land. Like, you know, I don't... I think I stopped short of saying
I'm so glad I don't need GPUs, but it was just... I just couldn't stop talking
about CPUs.

**Gergely** [37:43]:  
Yeah. And so, you know, Jensen took an interest in that.

**Simon** [37:46]:  
Yeah. So who knows? Like I'm sure you made a memorable person. Maybe he made his
mission now to like at some point get you guys onto GPUs. But speaking of CPUs,
can you tell me about what you're seeing inside of the hyperscale, the cloud
providers? You're now on AWS, you're in GCP, you're on Azure. What I would think
naively is there's a GPU shortage, and when I talk with inference companies,
they are... and AI labs, they're just getting whatever they can do. I would
think getting CPUs should be easy. Is it?

**Simon** [38:20]:  
No, it's not anymore.

**Gergely** [38:21]:  
Why? What was happening? Can you tell us about dynamics on the why and what
you've learned?

**Simon** [38:25]:  
Yeah, so I think that GPUs will probably continue to be scarce. Like, I don't
know, maybe there's going to be some surplus. I refuse to speculate too much
about the macro, but I think as RL is becoming a very, very large amount of the
workloads, that needs a lot of GPUs. So the labs are sucking up a lot of GPUs
because you need GPUs to be like, okay, we need to teach this model how to
search. We need to teach it how to use grep. We need to teach it how to boot up
bash. It needs to run real things and learn from that. It takes a lot of GPU.
And so I think as RL is consuming a lot of GPU, and then also... so just all of
the agents are running on CPUs, right? They need to do all kinds of very
general-purpose things on a CPU. And so as the demand curve is sort of shifting
to the right and it's becoming more and more applied, and that feeds back into
RL, by the way, right? Because as things become more applied, like, oh, the
models are not that good at CAD or chip building, I don't know. And then, you
know, you have to spin up even more RL environments to do that. I think that's
what we're seeing. And so we're on the other end of that needing these CPUs. We
need a lot of NVMe SSDs as well. And a lot of this right now is tied up in DRAM,
right? Of where like...

**Gergely** [39:38]:  
Yeah.

**Simon** [39:38]:  
You need a lot of that also for the GPU servers, but I would assume that it gets
a lot worse before it gets a lot better on the CPU side. And I think even the
big companies are fighting amongst each other, right, to get the allocations.
And even we, you know, we're selling to companies that we also fight for CPU
with and against, right? It's really difficult. And so you write things to try
to make sure you get these CPUs as fast as possible.

**Gergely** [40:05]:  
Yeah, and then yesterday I was at a dinner that you hosted with your team, where
you actually have a bunch of turbopuffer customers. A bunch of them are AI labs
or AI startups, but a lot of them, one of them, Reflection, had a huge massive
amount of footprint, and they were telling me that they're in a situation where
they cannot buy more. Like when it comes to GPUs or CPUs, they max out. They
have the longest contracts that possible, and I didn't realize how competitive
it is in the cloud when you go beyond a small fish to like a medium size or even
a large fish that now like...

**Simon** [40:38]:  
It's interesting.

**Gergely** [40:39]:  
So now you have this, and even you're having this kind of fight behind the
scenes that is maybe not as visible.

**Simon** [40:43]:  
Exactly. And I mean, you work with the clouds, right? You work with them to talk
about which regions have CPU, which regions are getting... it comes down to
power, right? Of like, okay, well, where is the power? Which is generally where
they're going to ship the new CPUs? And so we have to work with some of our
biggest customers on that. So these are real constraints, right, that are making
our way to us. We're just very fortunate that it's very easy for us to run lots
of turbopuffer clusters because all we need are like a few CPUs and NVMe SSDs
and an S3, and then we're in a good place. But there's lots of changes that we
can make even to the architecture to try to protect from a lot of this. Now, I'd
rather spend that engineering effort on other things, but...

**Gergely** [41:30]:  
Yep.

**Simon** [41:30]:  
We are very, very good at using a lot of very different SKUs, right? So we don't
need everything to be a particular CPU or instance type. We can run with many,
many different types of machine types on...

**Gergely** [41:42]:  
And then...

**Simon** [41:42]:  
Under CPU, meaning that's a fancy name for like the different machine types.

**Gergely** [41:44]:  
Yes, exactly, right? Like, you know, C4D or IAG or whatever they're called
under...

**Simon** [41:48]:  
What's your favorite one?

**Gergely** [41:49]:  
We really like right now the C4s on GCP.

**Simon** [41:51]:  
GCP, yeah. The Z4Ds are also performing really well now that we've done a bunch
of optimizations to them. Those are really, really great machine types. We
really like those. And then the ARM C4As as well on GCP. We like those. I think
that in general, like when you're... yeah, when you're small, it's very easy to
suck up a bunch of... but at Shopify, I was also part of, you know, deciding if
I had a BFCM, right, a few months out, you have to tell the cloud providers how
much you're intending to use, do commits on all of that, right? The clouds are
not infinite as they seem when you're small. And one way, of course, to get
infrastructure and also just credibility is venture capital. If you raise $100
million, $1 billion, some of your customers just raised $2 billion. Actually, I
talked with them yesterday. It gives you credibility, it gives you cash, you can
pay for this thing. Your specific turbopuffer's relationship to venture capital
seems very interesting. I never heard you announce a raise until maybe just very
recently. Can you tell me how you... and you told me that when you started this
thing, you didn't think too much outside of just building some cool stuff. How
did you think about venture capital? And how do you think about raising? Because
I feel you have a very fresh and different perspective than what is typical
inside of Silicon Valley.

**Simon** [43:05]:  
Yeah, so I think to understand how I think about capital, you have to go back to
the beginning of turbopuffer, right, where I promised Cursor that Justine and I
could get their bill to 4K a month. And this was based on some very rough napkin
math on, okay, if turbopuffer was a better implementation than it currently is,
then it should cost this much. And that's the pricing we ship with, and that's
what we guaranteed Cursor. But the software was not that good. Like it was very
reliable, but it was very simple, right? And that's like a core engineering
principle of me is simplicity above everything. You and I have talked before
about how software that ages well and some of the advantages of seeing... having
long tenures inside of companies. You had a long tenure at Uber, I had a long
tenure at Shopify, so you see simplicity just almost always wins. And at the
time, I was not convinced whether this was a venture-scale opportunity because I
understood that if you take venture capital, no matter how many smiles are in
the room, everyone's sort of expecting that you have to earn a big return on
that on some timeline that makes sense to everyone involved. And everyone
involved are, you know, pension funds in Canada. Like, it's like it is like a
whole stack, right, of people that need to... So at the time, I was like, I
don't know if this could be a billion-dollar company. I didn't know that in the
very, very beginning. It wasn't completely clear to me. It felt like a very
niche kind of product, right, to build this particular search engine. And that
was completely fine with me. So I, you know, it was fine. And so then I just
looked at the Cursor bill and I looked at my GCP bill, which is what we started
on. And, you know, it's like a, you know, dumb Danish person who's just like,
okay, like this number should just be lower than the other number. Yeah, that's
sort of like, you know, and it's just... I don't think I'd spent enough time in
San Francisco because I think the money over here works a little bit
differently. That's just... that's all I knew. You were doing business 101 as
long as you're making a profit, you're good, right?

**Gergely** [45:05]:  
Yeah.

**Simon** [45:05]:  
That was like... I'm not kidding in this exaggeration. That was just like that
just made sense to me that Justine and I were just going to go optimize this
until these numbers were roughly equal. And maybe if we could get some other
workloads, we could start paying ourselves. But that was like very much the
philosophy at the time because I didn't know if I could go raise a bunch of
money. I didn't know anyone who had the money. I didn't have any relationships.
I was an absolute outsider to the... I was an outsider. I was like an outsider
squared, right? I grew up in Aarhus, Denmark, and I then moved to Ottawa,
Canada. So it's like I'm an outsider to Canada, and in Canada, I'm an outsider
to San Francisco. So I was just thinking about this from first principles, like,
oh, you're a venture capital, you need this return, you need it on this
timeline. I don't know if I can deliver that yet. I would need more data to
decide that because I want to like... I kind of want to keep working on this.
And now I have to get to this point for it to not be a failure. In January then,
there was a person that I was at IOI with in 2012 and 2013, and his name is
Boyan, and he was on the North Macedonian team at IOI. And he was really good.
He was so good that the North Macedonian team called him God. I don't know why,
but that was what he went by. And he was, yeah, he was very good. He grew up,
and I really wanted to work with Boyan, but I couldn't afford to work with
Boyan. And he was very much like, this is what I could live off. Like, you know,
I just...

**Gergely** [46:43]:  
Yep.

**Simon** [46:43]:  
Like I want to build this thing. That would be like... this is what it can do.
But at this point, Justine and I hadn't taken a salary for like six months, and
we'd already spent like tens of thousands of dollars on like GCP bills and all
of that. And I was like, I don't think we can do it. And so I had met one
individual in Silicon Valley. His name is Lachy, and it just... I ended up just
calling him and saying, hey, I kind of want to learn a little bit faster here.
Can I... can we raise like 700k? That's like what I wanted to raise. So it's
just like I want to have like two engineers for the rest of the year, just you
and I still don't need to be paid, and then a little bit of buffer room. It's
like this is what I need, and if this doesn't have PMF and is a big opportunity
by the end of the year, I don't think we're going to bother, and we'll just shut
the whole thing down, and we won't have it taken down. We'll return everything
to you. I think that was the first time you heard anyone say it like that. And I
told some other VCs that at the time, and that was terrifying to them. I think
to someone on the West Coast, this sounds like you have low ambition or
something like that. And to me, it was just like, I don't know. It just came
from a... when I don't know how to play a game, I just play with open cards.
Like, this is how I see it. And so we were... it was very clear to us that we
wanted to do this, but also it became clear to us that we didn't want to just
like keep working on this unless it could become big. And we were starting to
develop conviction that it was actually going to become really, really big. And
so we did that and hired Boyan and then became profitable later that year and
then just continued to hire. And then it's like to raise more money, you need
sort of... there are six reasons to raise capital. The first reason to raise
capital is to fund R&D. That was the reason that we raised capital in January
because we funded R&D with a lot of our own, you know, opportunity costs and not
taking a salary and then paying the bills ourselves. But we wanted to learn a
little bit faster, and so we hired Boyan and Morgan as the first engineers. And
then the second reason to raise capital is to fund growth. You've built
something and you want to tell the world about it, and you want to spend more
capital to do that. The third reason to raise capital is for the founder's ego.
It's a very popular... it's...

**Gergely** [49:05]:  
I appreciate the honesty.

**Simon** [49:06]:  
...very popular, very, very popular, right? Big numbers, lots of press. And I
think this is a very, very dangerous reason to raise money, and I wish that it
was more talked about because you're diluting all of your employees when you do
it. You are setting a certain price for future employees and their upside. For
some people, it can become a status game, and that's not what it's about. We're
here to build a big business together, and this is not a reason to raise money.
But I do think that it happens. So the fourth reason to raise capital is to
reward your employees, right? You're on a very long journey, and you want to
work with the best people in the world. And by definition, there's not that many
best people in the world, so you want to reward them. That was the reason that
we took more capital in December, was to allow the employees to liquidate some
of their equity instead of waiting for some event like an IPO or something like
further out. The fifth reason to raise is for a strategic partnership. There are
strategic partnerships that have been made in this city that have made
companies. The sixth reason to raise would be doing M&A or something like that.
But it's like you have to be very honest about what reason you are raising in
those six. The first reason to raise was one, and the second reason we raised
was for...

**Gergely** [51:05]:  
Which was?

**Simon** [51:05]:  
The first reason to raise was R&D.

**Gergely** [51:06]:  
R&D.

**Simon** [51:06]:  
And the second reason was to provide liquidity to the employees.

**Gergely** [51:08]:  
Employees. Yep. I think it's a nice and healthy way. And I think, yeah, the ego
part, we don't talk about it. The identity, and especially the closer you are to
ecosystems where a lot of people are raising, it will be part of it. As closing,
I want to ask you about the way you have a remote culture. These days, I'm
seeing it, especially for companies that do anything with AI, may that be
building AI infra or just AI products. A lot of them prefer in-person, having an
HQ, oftentimes in SF or wherever your headquarters may be, London or somewhere
else, because you often... these companies often find that they have faster
iteration. It's just fewer layers cut in between, and of course, speed is very,
very important. You have started for remote, and you're still for remote. How is
it working, and what kind of quirks or like turbopuffer ways have you found to
make this work better?

**Simon** [52:05]:  
Yeah, I think the company started in '23, sort of like on the cusp of COVID,
where a lot of companies were just remote. The Shopify infrastructure was remote
since the very, very beginning because it's very difficult to get them all to
move to Ottawa. So it was natural to me. It's like, okay, I think there's kind
of maybe two cities where you can build a database company fast, and that's San
Francisco and maybe New York. There are maybe other cities, right? But that's
like kind of where it's been done. And so if you don't want to do that, I think
you have to go all in on some distributed model. And so we've tried to figure
out what does that distributed model mean for turbopuffer? It doesn't mean the
absence of in-person. We get everyone together twice a year in some location.
Earlier this year, we were in Banff, right? And then we were in Mexico City and
so on. So it's like that's not that uncommon. But one of the things that we've
been trying to do is we have this concept called campfires. And the concept of
the campfire is that when a couple of people just sort of randomly congregate in
a place, you call it a campfire, and you encourage as many people as you want to
come and join. So for example, this week is a turbopuffer campfire in San
Francisco because I'm here for this conference and a bunch of other things. And
so everyone is invited to come. Like we're going to go meet customers, right?
We're going to put on dinners for our customers and things like that, and we
just make a thing out of it and spend time together. And we encourage everyone
to come. We've also gone to the extent now of we won't encourage that, but not
everyone needs to go to the campfire all the time. Some people just want to, you
know, lock in and hack in the tent, and that's great. We have people that just
make it to the off-site twice a year, and otherwise they're home, they're with
their families, and they don't spend time on an airplane. Fantastic. Like that
is completely compatible with this model. And there are other people at the
company who are on a plane probably every two weeks. We had someone the other
day where they saw a campfire happening in New York, and everyone was dialing in
from a meeting room in New York, and she had so much FOMO that she took an Uber
straight to the airport in Ottawa and flew to New York to hang out with the
team, right? And I think that's fantastic. And we've also introduced these
things where if you do a conference talk or a blog post or something like that,
a turbopuffer, something a bit extracurricular, we give you a turbocredit. And a
turbocredit allows you to upgrade your next flight to business class, which
again encourages spending time together with the team. And now, I mean,
turbocredits are probably going to take on a life of their own. Someone was
talking about doing a central bank and doing interest rates on the turbocredits
and doing a betting market on the turbocredits. And so like this might take on
its life on its own. And you know, if you're at a conference like this, there's
some of our engineers here who just want to interact with customers and be on
like... and standing on an expo floor all day is quite taxing. And so if you do
that for two days because you want to do it well, you get a turbocredit, right?
And so it's just like these fun little things that we try to do to encourage
people to meet if they want to meet.

**Gergely** [55:05]:  
Thank you. Well, in this session, what I found very interesting is turbopuffer
is so many AI companies are using you as an infrastructure layer, but in this
conversation, we managed to talk very little about AI and a lot more about
engineering principles and the human connection, how important it is for people
to work together to trust each other. So just thank you very much for this. So
let's give a big round of applause for Simon. Thank you so much.

**Simon** [55:30]:  
That's great. Thank you.

![turbopuffer logo](/_next/static/media/lockup_transparent.6092c7ef.svg)

[Company](/about)[Pricing](/pricing)[Store](https://turbopuffer.supply)[Press & media](/press)[System status](https://status.turbopuffer.com)

Support

[Slack](https://join.slack.com/t/turbopuffer-community/shared_invite/zt-3v27t102a-3RynqZ5A9vuOuAo68X_wFQ)[Docs](/docs)[Email](/contact/support)[Sales](/contact/sales)

Follow

[Blog](/blog)[RSS](/blog/rss.xml)[Events](/events)

© 2026 turbopuffer Inc.

[Terms of service](/terms-of-service)[Data Processing Agreement](/dpa.pdf)[Privacy Policy](/privacy-policy)[Security & Compliance](/docs/security)

Docs search

esc

## Guides

[Quickstart

Get started with turbopuffer in minutes](/docs/quickstart)

[Vector Search

Perform approximate nearest neighbor searches](/docs/vector)

[Full-Text Search

Learn how to use BM25 full-text search](/docs/fts)

[Hybrid Search

Combine vector and full-text search strategies](/docs/hybrid)

## API Docs

[Write

Create, update, or delete documents](/docs/write)

[Query

Query documents with filters and ranking](/docs/query)

[Overview

Authentication, headers, and request encoding](/docs/api-overview)

[Namespace metadata

Get metadata about a namespace](/docs/metadata)

![](https://px.ads.linkedin.com/collect/?pid=8553810&fmt=gif)