---
title: 'Giving Back to the Open Source We Build On'
company: LanceDB
tag: 搜索
date: 2026-09-21
url: https://www.lancedb.com/blog/giving-back-to-open-source
account: 
origin: en-rss
---
# Giving Back to the Open Source We Build On

[Xuanwo](/author/xuanwo)

[Taylor Smith](/author/taylor-smith)

•

September 29, 2026

•

[Community](/category/community)[Engineering](/category/engineering)

![2519-Giving-Back-to-the-Open-Source-We-Build-On-51bb128a-fig-001](../images/2519-Giving-Back-to-the-Open-Source-We-Build-On-51bb128a/figure-001.png)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

LanceDB depends on open source projects across our stack, from storage access to query execution. We benefit every day from the engineering, review, and maintenance behind those projects. That lets us spend more time on the problems that are specific to LanceDB.

When we run into a missing capability or find a useful optimization, we try to contribute it upstream rather than keep it inside LanceDB. Our engineers have contributed to [LeRobot](https://huggingface.co/lerobot), [Apache OpenDAL](https://opendal.apache.org/), [CocoIndex](https://cocoindex.io/), [ICU4X](https://icu4x.unicode.org/), and other projects we depend on. Nearly 90% of LanceDB's members on the Lance PMC also contribute to or help govern other major open-source projects.

A recent example is [adding ASOF join support to Apache DataFusion](https://github.com/apache/datafusion/pull/23738), the query engine behind SQL execution in LanceDB. We needed a better way to match records captured at different timestamps, a common pattern in robotics and other time-series workloads. Contributing the feature upstream makes it available to other DataFusion users too, with the benefit of review from the wider community.

## **Why DataFusion matters to LanceDB**

[Apache DataFusion](https://datafusion.apache.org/) is an extensible query engine written in Rust and built around Apache Arrow. It provides SQL and DataFrame APIs, query planning and optimization, and a columnar execution engine. Developers can extend it with their own data sources, functions, and operators.

For LanceDB, that means we do not have to build a SQL query engine from scratch. We can focus on storage, indexing, and the access patterns our users need, while DataFusion handles a large part of query planning and execution.

That also gives us a natural way to contribute back. When a capability we need could be useful beyond LanceDB, we would rather improve the shared engine than keep the solution private. ASOF joins are one example.

## **When timestamps do not line up**

Imagine a robotics dataset where camera frames and robot states are recorded at different frequencies. For each frame, you may want the most recent state recorded at or before the frame timestamp.

An equality join only works when the timestamps match exactly. Joining against every earlier state creates the opposite problem, leaving multiple candidates for each frame. What we actually want is the latest eligible state for the same robot and recording episode. Differently sampled sensor data is one area where DataFusion’s ASOF feature helps.

An ASOF join lets you write that relationship directly. A DataFusion query over the camera and state tables could look like this.

```
SELECT
    f.robot_id,
    f.episode_id,
    f.frame_id,
    f.ts AS frame_time,
    s.ts AS state_time,
    s.joint_positions
FROM camera_frames AS f
ASOF JOIN robot_states AS s
MATCH_CONDITION (f.ts >= s.ts)
ON f.robot_id = s.robot_id
   AND f.episode_id = s.episode_id;
```

For each frame, this finds the latest state at or before the frame timestamp for the same robot and episode. Frames with no matching state stay in the result with null state fields. Other comparison operators can be used to pick the next eligible record instead.

How an ASOF join works
Each camera frame is matched to the most recent IMU sample whose timestamp is at or before the frame, giving a per-frame robot state with a known staleness.

CAMERA FRAMES

IMU SAMPLES

TIME (MS)

30

70

110

10

40

60

100

120

30

10

70

60

110

100

RESULT

FRAME\_TS
MATCHED IMU\_TS
STALENESS

30
10
20 ms

70
60
10 ms

110
100
10 ms

This is useful beyond robotics too. In financial data, for example, an ASOF join can match a trade to the most recent quote. In both cases, records need to be matched by time even when their timestamps do not line up exactly.

## **Why we contribute upstream**

Contributing upstream means a feature built for one LanceDB use case can become useful to teams we may never meet. It also puts the implementation in front of maintainers and users with different workloads and assumptions.

That exchange improves our work, too. Review from the DataFusion community brings in perspectives we would not get from LanceDB’s requirements alone.

We depend on open source, so contributing back is part of how we want to build LanceDB. DataFusion is a good example of that relationship, and we are glad to contribute when the problems we solve can help the broader community.

You can read the [ASOF join contribution](https://github.com/apache/datafusion/pull/23738) or explore the [Apache DataFusion documentation](https://datafusion.apache.org/) for more detail.

![2519-Giving-Back-to-the-Open-Source-We-Build-On-51bb128a-fig-002](../images/2519-Giving-Back-to-the-Open-Source-We-Build-On-51bb128a/figure-002.avif)

[Xuanwo](/author/xuanwo)

ASF Member. Apache OpenDAL PMC Chair. VISION: Data Freedom. Working on RBIR with LanceDB.

[GitHub](https://github.com/Xuanwo)[Linkedin](https://www.linkedin.com/in/xuanwo/)[Twitter](https://x.com/xuanwo)

![2519-Giving-Back-to-the-Open-Source-We-Build-On-51bb128a-fig-003](../images/2519-Giving-Back-to-the-Open-Source-We-Build-On-51bb128a/figure-003.jpg)

[Taylor Smith](/author/taylor-smith)

Product Marketing

[GitHub](https://github.com/tsmithv11)[Linkedin](https://www.linkedin.com/in/taylorbsmith/)[Twitter](https://x.com/ifoundanifty)

![2519-Giving-Back-to-the-Open-Source-We-Build-On-51bb128a-fig-004](../images/2519-Giving-Back-to-the-Open-Source-We-Build-On-51bb128a/figure-004.webp)

### A Practical LLM Pretraining Pipeline with LanceDB

Ayush Chaurasia

•

September 14, 2026

practical-llm-pretraining

![2519-Giving-Back-to-the-Open-Source-We-Build-On-51bb128a-fig-005](../images/2519-Giving-Back-to-the-Open-Source-We-Build-On-51bb128a/figure-005.webp)

### Turning Fleet Data Into Better Models: The Data Mining Challenge in Physical AI

Lei Xu

•

September 1, 2026

data-mining-challenge-in-physical-ai

![2519-Giving-Back-to-the-Open-Source-We-Build-On-51bb128a-fig-006](../images/2519-Giving-Back-to-the-Open-Source-We-Build-On-51bb128a/figure-006.webp)

### 🎤 Reverie, Nov 5, ⚡ ML Data Loading Performance Guide, 🧠 CrewAI Cognitive Memory on LanceDB

ChanChan Mao

•

September 8, 2026

newsletter-august-2026