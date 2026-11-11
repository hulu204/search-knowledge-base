---
title: 'Handling 300k requests per day: an adventure in scaling'
company: Firecrawl
tag: 工程相关
date: 2024-09-13
url: https://www.firecrawl.dev/blog/an-adventure-in-scaling
account: 
origin: harvest2-202607
---
[Blog](/blog)

# Handling 300k requests per day: an adventure in scaling

![placeholder](/_next/image?url=%2Fimages%2Fauthors%2Fmogery.webp&w=48&q=75&dpl=dpl_BonP4CzswHAdBhe4529NQAppYj1c)Gergő Móricz (mogery)Sep 13, 2024

![Handling 300k requests per day: an adventure in scaling image](/_next/image?url=%2Fimages%2Fblog%2Fan-adventure-in-scaling.jpg&w=3840&q=75&dpl=dpl_BonP4CzswHAdBhe4529NQAppYj1c)

When I joined the Firecrawl team in early July, we spent most of our time working on new features and minor bugfixes. Life was good — we could focus mostly on shipping shiny new stuff without worrying as much about architecture and server load. However, as we grew over time, we started experiencing the "hug of death" a lot more. People loved our product so much that our architecture couldn't take it anymore, and every day there was a brand new fire to put out. We knew that this was unsustainable, and ultimately it damages our DX more than any new feature we could put out could make up for. We knew we had to change things, stat.

## Our architecture, before the storm

We host our API service on [Fly.io](https://fly.io/), which allows us to easily deploy our code in a Docker container. It also manages load balancing, log collection, zero-downtime deployment strategies, VPC management, and a whole load of other stuff for us, which is very useful.

Our main API service has two kinds of "processes", as Fly calls it: `app` and `worker`.

`app` processes use Express to serve the main API, perform scrape requests (which take a relatively short time), and delegate crawls to `worker` processes using the [Bull](https://github.com/OptimalBits/bull) job queue.

`worker` processes register themselves as workers on the job queue, and perform crawls (which take a relatively long time).

Both processes use Supabase to handle authentication and store data in Postgres. Bull also runs on top of Redis, which we deployed on [Railway](https://railway.app), since it's super easy to use.

## Locks are hard

As more and more people started using us, more and more people started finding bugs. We started getting odd issues with crawls sometimes being stuck for hours without any progress. I charted the timing of these crawls, and I saw that it was happening every time we redeployed.

Due to some miscellaneous memory leak issues, we were redeploying our entire service every 2 hours via GitHub Actions, in order to essentially restart all our machines. This killed all our workers, which had acquired locks for these crawl jobs. I was not too familiar with the codebase at this point, and I thought that these locks got hard-stuck on the dead workers, so I to add some code to release all of the current worker's locks on termination.

This ended up being really complicated, due to multiple factors:

1. Other libraries we used also had cleanup code on `SIGTERM`. When you listen to `SIGTERM`, your app doesn't actually quit until the handler calls `process.exit()`. So, the other library's handler called `process.exit()` when its handler finished, which caused a race condition with our cleanup handler. (This was absolute hell to debug.)
2. Fly.io sometimes didn't respect our configuration, and hard-`SIGKILL`ed our application before the 30 second timeout we specified our config. This cut our cleanup code short.
3. There was no easy way to remove a lock via the Bull API. The only legitimate way it could be done was to:
   1. Get all in-progress jobs of this worker
   2. Set their status to failed
   3. Delete them from the queue
   4. Re-insert them to the queue
4. While the cleanup code was running, there was no easy way to disable the current worker, so sometimes jobs the cleanup code re-inserted were immediately picked up by the same worker that was about to be shut down.
5. Due to our rollover deployment strategy, during a deployment, the re-inserted jobs were picked up by workers that have not been updated yet. This caused all the jobs to be piled up on the last worker to be updated, which caused the cleanup code to run longer than Fly's maximum process shutdown timeout.

While I was going down a rabbithole that was spiraling out of control, Thomas (another Firecrawl engineer who mainly works on [Fire-Engine](https://www.firecrawl.dev/blog/introducing-fire-engine-for-firecrawl), which used a similar architecture) discovered that our queue lock options were grossly misconfigured:

```
webScraperQueue = new Queue("web-scraper", process.env.REDIS_URL, {
  settings: {
    lockDuration: 2 * 60 * 60 * 1000, // 2 hours in milliseconds
    lockRenewTime: 30 * 60 * 1000, // 30 minutes in milliseconds
  },
});
```

This was originally written with the understanding that `lockDuration` would be the maximum amount of time a job could take — which is not true. When a worker stops renewing the lock every `lockRenewTime` milliseconds, `lockDuration` specifies the amount of time to wait before declaring the job as `stalled` and giving it to another worker. This was causing the crawls to be locked up for 2 hours, similar to what our customers were reporting.

After I got rid of all my super-complex cleanup code, the fix ended up being this:

```
webScraperQueue = new Queue("web-scraper", process.env.REDIS_URL, {
  settings: {
    lockDuration: 2 * 60 * 1000, // 1 minute in milliseconds
    lockRenewTime: 15 * 1000, // 15 seconds in milliseconds
  },
});
```

Thank you Thomas for spotting that one and keeping me from going off the deep end!

## Scaling scrape requests, the easy way

As you might have noticed in the architecture description, we were running scrape requests on the `app` process, the same one that serves our API. We were just starting a scrape in the `/v0/scrape` endpoint handler, and returning the results. This is simple to build, but it isn't sustainable.

We had no idea how many scrape requests we were running and when, there was no way to retry failed scrape requests, we had no data source to scale the `app` process on (other than are we down or not), and we had to scrape Express along with it. We needed to move scraping to our `worker` process.

We ended up choosing to just add scrape jobs to the same queue as crawling jobs. This way the `app` submitted the job, the `worker` completed it, and the `app` waited for it to be done and returned the data. [We read the old advice about "never wait for jobs to finish"](https://blog.taskforce.sh/do-not-wait-for-your-jobs-to-complete/), but we decided to cautiously ignore it, since it would have ruined the amazing simplicity that the scrape endpoint has.

This ended up [being surprisingly simple](https://github.com/firecrawl/firecrawl/commit/6798695ee4daf1ce1b289db494d260d718b6752b#diff-6753e371514e1d188e797436080479e7c781d96183601ab8fa203e4df6ca0400), only slightly affected by Bull's odd API. We had to add a global event handler to check if the job had completed, since it lacked the [`Job.waitUntilFinished`](https://api.docs.bullmq.io/classes/v5.Job.html#waitUntilFinished) function that its successor [BullMQ](https://github.com/taskforcesh/bullmq) already had.

We saw a huge drop in weird behaviour on our `app` machines, and we were able to scale them down in exchange for more `worker` machines, making us way faster.

## Smaller is better

The redeploy crawl fiasco made us worried about handling big crawls. We could essentially 2x the time a big crawl ran if it was caught in the middle of a redeploy, which is sub-optimal. Some of our workers were also crashing with an OOM error when working on large crawls. We instead decided to break crawls down to individual scrape jobs that chain together and spawn new jobs when they find new URLs.

We decided to make every job in the queue have a scrape type. Scrape jobs that are associated with crawls have an extra bit of metadata tying them to the crawlId. This crawlId refers to some redis keys that coordinate the crawling process.

The crawl itself has some basic data including the origin URL, the team associated with the request, the robots.txt file, and others:

```
export type StoredCrawl = {
  originUrl: string;
  crawlerOptions: any;
  pageOptions: any;
  team_id: string;
  plan: string;
  robots?: string;
  cancelled?: boolean;
  createdAt: number;
};
 
export async function saveCrawl(id: string, crawl: StoredCrawl) {
  await redisConnection.set("crawl:" + id, JSON.stringify(crawl));
  await redisConnection.expire("crawl:" + id, 24 * 60 * 60, "NX");
}
 
export async function getCrawl(id: string): Promise<StoredCrawl | null> {
  const x = await redisConnection.get("crawl:" + id);
 
  if (x === null) {
    return null;
  }
 
  return JSON.parse(x);
}
```

We also make heavy use of Redis sets to determine which URLs have been already visited when discovering new pages. The Redis `SADD` command adds a new element to a set. Since sets can only store unique values, it returns 1 or 0 based on whether the element was added or not. (The element does not get added if it was already in the set before.) We use this as a lock mechanism, to make sure two workers don't discover the same URL at the same time and add two jobs for them.

```
async function lockURL(id: string, url: string): Promise<boolean> {
  // [...]
  const res = (await redisConnection.sadd("crawl:" + id + ":visited", url)) !== 0;
  // [...]
  return res;
}
 
async function onURLDiscovered(crawl: string, url: string) {
  if (await lockURL(crawl, url)) {
    // we are the first ones to discover this URL
    await addScrapeJob(/* ... */); // add new job for this URL
  }
}
```

You can take a look at the whole Redis logic around orchestrating crawls [here](https://github.com/firecrawl/firecrawl/blob/main/apps/api/src/lib/crawl-redis.ts).

With this change, we saw a huge performance improvement on crawls. This change also allowed us to perform multiple scrape requests of one crawl at the same time, while the old crawler had no scrape concurrency. We were able to stretch a crawl over all of our machines, maximizing the worth we get for each machine we pay for.

## Goodbye Bull, hello BullMQ

Every time we encountered Bull, we were slapped in the face by how much better BullMQ was. It had a better API, new features, and the most important thing of all: active maintenance. We decided to make the endeavour to switch over to it, first on Fire-Engine, and then on Firecrawl.

With this change, we were able to drop the horrible code for [waiting for a job to complete](https://github.com/firecrawl/firecrawl/blob/6798695ee4daf1ce1b289db494d260d718b6752b/apps/api/src/controllers/scrape.ts#L59-L89), and replace it all with `job.waitUntilFinished()`. We were also able to customize our workers to add Sentry instrumentation (more on that later), and to take on jobs based on CPU and RAM usage, instead of a useless max concurrency constant that we had to use with Bull.

BullMQ still has its API quirks (e.g. don't you dare call `Job.moveToCompleted` / `Job.moveToFailed` with the 3rd argument not set to `false`, otherwise you will check out and lock a job that will be returned to you that you're probably dropping)

## Our egress fee horror story

Our changes made us super scalable, but they also meant that a lot more traffic was going through Redis. We ended up racking up a 15000$ bill on Railway in August, mostly on Redis egress fees only. This wasn't sustainable, and we needed to switch quickly.

After being disappointed with Upstash, and having issues with Dragonfly, we found a way to deploy Redis to Fly.io natively. [We put our own spin on the config](https://github.com/firecrawl/firecrawl/blob/f7c4cee404e17b3ed201e005185a5041009d0e6f/apps/redis/fly.toml), and deployed it to our account. However, we were not able to reach the instance from the public IP using `redis-cli` (netcat worked though?!?!), which caused some confusion.

We decided to go another way and use Fly's [Private Networking](https://fly.io/docs/networking/private-networking/), which provides a direct connection to a Fly app/machine without any load balancer being in front. We crafted a connection string, SSH'd into one of our worker machines, installed `redis-cli`, tried to connect, and... it worked! We had a reachable, stable Redis instance in front of us.

So, we went to change the environment variable to the fancy new Fly.io Redis, we deployed the application, and... we crashed. After a quick revert, we noticed that [IORedis](https://github.com/redis/ioredis) wasn't able to connect to the Redis instance, but `redis-cli` stilled worked fine. So... what gives?

Turns out, `ioredis` only performs a lookup for an IPv4 address, unless you specify `?family=6`, in which case it only performs a lookup for an IPv6 address. This is not documented anywhere, except in a couple of GitHub issues which are hard to search for. I have been coding for almost 11 years now, and this is the worst configuration quirk I have ever seen. (And I use Nix daily!) In 2024, it would be saner to look for IPv6 by default instead of IPv4. Why not look for both? This is incomprehensible to me.

Anyways, after appending `?family=6` to the string, everything worked, except, sometimes not...

## Awaiting forever

We started having huge waves of scrape timeouts. After a bit of investigation, the `Job.waitUntilFinished()` Promise never returned, but after looking at our BullMQ dashboard, we saw that jobs were actually being completed.

BullMQ uses Redis streams for all of its event firing/handling code, including `waitUntilFinished`, which waits until the job's `finished` event fires. BullMQ enforces a maximum length for the event stream, in order to purge old events that have presumably already been handled, and it defaults to about 10000 maximum events. Under heavy load, our queue was firing so many events, that BullMQ was trimming events before they could be processed. This caused everything that depends on queue events to fail.

This maximum events parameter is configurable, however, it seems like a parameter that we'd have to babysit, and it's way too cryptic and too easy to forget about. Instead, we opted to rewrite the small amount of code that uses queue events to do polling instead, which is not affected by pub/sub issues like this.

Inexplicably, this never happened on the old Railway Redis instance, but it happened on every alternative we tried (including Upstash and Dragonfly). We're still not sure why we didn't run into this issue earlier, and BullMQ queue events still work happily on the Fire-Engine side under Dragonfly.

## Adding monitoring

We were growing tired of going through console logs to diagnose things. We were also worried about how many issues we could potentially be missing. So, we decided to integrate [Sentry](https://sentry.io) for error and performance monitoring, because I had some great experiences with it in the past.

The moment we added it, we found about 10 high-impact bugs that we had no idea about. I fixed them the day after. We also had an insight into what our services were actively doing — I was able to add custom instrumentation to BullMQ, and pass trace IDs over to Fire-Engine, so now we can view the entire process a scrape or crawl goes through until it finishes, all organized in one place.

![Sentry Trace view](/images/blog/scaling-sentry.png)

(The creation of this image for this post lead me to [decrease the time Firecrawl spends after Fire-Engine is already finished](https://github.com/firecrawl/firecrawl/commit/000a316cc362b935976ac47b73ec02923f4175c5). Thanks, Sentry!)

Sentry has been immensely useful in finding errors, debugging incidents, and improving performance. There is no longer a chance that we have an issue invisibly choking us. With Sentry we see everything that could be going wrong (super exciting to see AIOps tools like [Keep](https://www.keephq.dev/) popping up).

## The future

We are currently stable. I was on-call last weekend and I forgot about it. The phone never rang. It felt very weird after putting out fires for so long, but our investment absolutely paid off. It allowed us to do [our launch week](/blog/firecrawl-launch-week-1-recap), which would not have been possible if we were in panic mode 24/7. It has also allowed our customers to build with confidence, as the increased reliabilty adds another layer of greatness to Firecrawl.

However, there are still things we're unhappy with. Fly, while very useful early-stage, doesn't let us smoothly autoscale. We are currently setting up Kubernetes to give us more control over our scaling.

I love making Firecrawl better, be it with features or with added reliability. We're in a good place right now, but I'm sure there will be a lot more adventures with scaling in the future. I hope this post has been useful, since surprisingly few people talk about all this stuff. (We sure had trouble finding resources when we were trying to fix things.) I will likely be back with a part 2 when there's more exciting things to talk about.