---
title: 'The first search engine with fully vectorized query execution'
company: turbopuffer
tag: 召回
date: 2026-10-26
url: https://turbopuffer.com/blog/fully-vectorized-search-engine
account: 
origin: en-rss
---
[tpuf v3 is coming: follow alongturbopuffer v3 is coming: follow our progress](/v3)

# The first search engine with fully vectorized query execution

October 26, 2026•Adrien Grand (Engineer)

When [turbopuffer v3](/v3) goes to production later this year, every turbopuffer
query will execute through an end-to-end vectorized pipeline. To our knowledge,
this will make turbopuffer the first and only search engine to adopt fully
vectorized execution, an
architecture more commonly associated with analytical databases.

Modern CPUs reward predictable, batch-oriented access patterns, and search
continues to evolve
[beyond narrow retrieval mechanisms](/blog/rip-vector-database). Vectorized
execution makes the best use of hardware so turbopuffer v3 can provide very
strong performance on many types of queries.

## How query engines have evolved

Historically, database query processing used the Volcano model, which organizes
execution as a pipeline of generic operators. Consider the query:

```
SELECT sum(price)
FROM product
WHERE price <= 32
```

A possible plan for this query includes three operators:

1. `SequentialScan` scans the `product` table to produce its rows
2. `Filter` drops rows that don't match `price <= 32`
3. `Aggregate` accumulates the sum on surviving rows

In the Volcano model, each operator implements a generic function to pull rows
one at a time from its children.

```
                sum  0
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

                sum  0
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │ 128
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
> ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

───
                sum  0
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │ drop 128
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
> ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

───────
                sum  0
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │ 32
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
> ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

──────────
                sum  0
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │ 32
                   ╵
                Filter
                   ▲
                   │
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
> ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

──────────────
                sum 32
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
> ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

─────────────────
                sum 32
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │ 16
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
> ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

─────────────────────
                sum 32
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │ 16
                   ╵
                Filter
                   ▲
                   │
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
> ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

────────────────────────
                sum 48
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
> ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

────────────────────────────
                sum 48
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │ 32
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
> ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

───────────────────────────────
                sum 48
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │ 32
                   ╵
                Filter
                   ▲
                   │
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
> ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

───────────────────────────────────
                sum 80
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

──────────────────────────────────────
                sum 80
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

──────────────────────────────────────
                sum  0
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

```
           sum  0
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

           sum  0
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │ 128
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
> ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

───
           sum  0
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │ drop 128
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
> ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

──────
           sum  0
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │ 32
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
> ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

─────────
           sum  0
              ▲
              │
              ╵
          Aggregate
              ▲
              │ 32
              ╵
           Filter
              ▲
              │
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
> ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

────────────
           sum 32
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
> ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

───────────────
           sum 32
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │ 16
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
> ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

──────────────────
           sum 32
              ▲
              │
              ╵
          Aggregate
              ▲
              │ 16
              ╵
           Filter
              ▲
              │
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
> ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

─────────────────────
           sum 48
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
> ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

────────────────────────
           sum 48
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │ 32
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
> ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

───────────────────────────
           sum 48
              ▲
              │
              ╵
          Aggregate
              ▲
              │ 32
              ╵
           Filter
              ▲
              │
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
> ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

──────────────────────────────
           sum 80
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

─────────────────────────────────
           sum 80
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

─────────────────────────────────
           sum  0
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░
```

The main weakness of this model is per-row overhead: every row, at every
operator, incurs the cost of a function call, dynamic dispatch, and
interpretation. The CPU spends more time figuring out what to do next than
actually doing it, which is a poor way of utilizing the CPU.

Two main approaches have emerged to address this inefficiency: **compiled query
engines** and **vectorized query engines**. Both have produced state-of-the-art
analytical databases, for example [Hyper](https://hyper-db.de/) (compiled) and
[DuckDB](https://duckdb.org/) (vectorized). You can learn more about this topic
in the excellent
[Everything You Always Wanted to Know About Compiled and Vectorized Queries But Were Afraid to Ask](https://drive.google.com/file/d/1LJeys01Ho9DREfRJhb9wHu3ssSC22Lll/view).

## What is a vectorized query engine?

Vectorized query engines process data in batches, rather than one row at a time.
Unlike compiled engines, which generate specialized code for each query,
vectorized query engines retain generic operators from the Volcano model. Unlike
the Volcano model, they process cache-friendly batches of rows, amortizing
dispatch overhead and enabling more efficient use of modern CPUs.

```
                sum  0
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

                sum  0
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │ [128, 32, 16, 32]
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
> ║ puffer jacket    cozy       128 ║░
> ║ tee puff         silly       32 ║░
> ║ cowpuff          moooo       16 ║░
> ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

─────────────
                sum  0
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │ [32, 16, 32]
                   ╵
                Filter
                   ▲
                   │
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
> ║ puffer jacket    cozy       128 ║░
> ║ tee puff         silly       32 ║░
> ║ cowpuff          moooo       16 ║░
> ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

─────────────────────────
                sum 80
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

──────────────────────────────────────
                sum 80
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

──────────────────────────────────────
                sum  0
                   ▲
                   │
                   ╵
               Aggregate
                   ▲
                   │
                   ╵
                Filter
                   ▲
                   │
                   ╵
            SequentialScan
                   ╷
                   │
  ╔═ product ══════╧════════════════╗
  ║ name             vibes    price ║░
  ╠═════════════════════════════════╣░
  ║ puffer jacket    cozy       128 ║░
  ║ tee puff         silly       32 ║░
  ║ cowpuff          moooo       16 ║░
  ║ lil block puff   nerdy       32 ║░
  ╚═════════════════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

```
           sum  0
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

           sum  0
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │ [128, 32, 16, 32]
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
> ║ puffer jacket     128 ║░
> ║ tee puff           32 ║░
> ║ cowpuff            16 ║░
> ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

───────────
           sum  0
              ▲
              │
              ╵
          Aggregate
              ▲
              │ [32, 16, 32]
              ╵
           Filter
              ▲
              │
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
> ║ puffer jacket     128 ║░
> ║ tee puff           32 ║░
> ║ cowpuff            16 ║░
> ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

──────────────────────
           sum 80
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

─────────────────────────────────
           sum 80
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░

─────────────────────────────────
           sum  0
              ▲
              │
              ╵
          Aggregate
              ▲
              │
              ╵
           Filter
              ▲
              │
              ╵
       SequentialScan
              ╷
              │
  ╔═ product ═╧═══════════╗
  ║ name            price ║░
  ╠═══════════════════════╣░
  ║ puffer jacket     128 ║░
  ║ tee puff           32 ║░
  ║ cowpuff            16 ║░
  ║ lil block puff     32 ║░
  ╚═══════════════════════╝░
   ░░░░░░░░░░░░░░░░░░░░░░░░░
```

## Why haven't search engines adopted vectorized evaluation?

Search engines have traditionally been optimized for narrow workloads: top-k
results by similarity with the query (whether full-text or vector). This query
shape is expressed as a single ranking algorithm, so it can be implemented as
one specialized loop rather than a pipeline of heterogeneous operators like
scan, filter, and aggregate.

```
┌─────────┐    ┌────────────┐    ┌───────┐
│  text   │───▶│ searchBM25 │───▶│ top-k │
└─────────┘    └────────────┘    └───────┘
```

```
   ┌──────┐
   │ text │
   └──────┘
      │
      ▼
┌────────────┐
│ searchBM25 │
└────────────┘
      │   
      ▼
  ┌───────┐
  │ top-k │
  └───────┘
```

As a result, search engines haven't had to pay the operator-dispatch overhead
that motivated vectorized engines for the analytical domain.

Furthermore, widely used search algorithms like
block-max WAND for text search
and HNSW for vector search are
less amenable to vectorization than typical database workloads. These algorithms
compute the similarity between the query and a document to decide which document
to look at next. While this lets them aggressively prune the index and thus
examine less data, it also creates a data dependency, so the CPU can't predict
the next branch or fetch the next document until the similarity is computed.

## Why turbopuffer v3 adopts vectorized execution

Two things motivate our adoption of a vectorized query engine: the increasing
complexity of our customers' queries, and the kind of work that modern hardware
rewards.

### Generic operators simplify query complexity

turbopuffer v1 had a single vector similarity operator, so there was no need for
dynamic dispatch among heterogeneous kinds of operators.

Today, however, turbopuffer customers incorporate many additional ranking
signals—like [filter evaluation](/blog/native-filtering),
[recency boosting](/blog/rank-by-attribute), and other
[custom scoring functions](/docs/query#fts-operators)—and operators beyond
ranking—like [aggregations](/docs/query#aggregations),
[group by](/docs/query#group-by), and
[order by](/docs/query#ordering-by-attributes).

For example, a BM25 query for "tpuf v3" filtered on permission scopes and
boosted by recency might have this plan:

```
                ┌────────────────┐
                │     Filter     │─────────────┐
                └────────────────┘             │
                                               │
                ┌────────────────┐   ┌─────────▼─────────┐
                │ BM25Term(tpuf) │──▶│                   │
                └────────────────┘   │                   │    ┌─────────┐
                                     │  TopKByTextScore  │───▶│ Project │
                ┌────────────────┐   │                   │    └─────────┘
                │  BM25Term(v3)  │──▶│                   │
                └────────────────┘   └─────────▲─────────┘
                                               │
┌───────────┐   ┌────────────────┐             │
│ Attribute │──▶│     Decay      │─────────────┘
└───────────┘   └────────────────┘
```

```
┌────────┐
│ Filter │──────────────┐
└────────┘              │
┌────────────────┐      │
│ BM25Term(tpuf) │──────┤
└────────────────┘      │
┌────────────────┐      │
│  BM25Term(v3)  │──────┤
└────────────────┘      │
┌─────────┐  ┌───────┐  │
│Attribute│─▶│ Decay │──┤
└─────────┘  └───────┘  │
                        │
                ┌───────▼───────┐
                │TopKByTextScore│
                └───────┴───────┘
                        │
                        ▼
                   ┌─────────┐
                   │ Project │
                   └─────────┘
```

turbopuffer now supports well over a dozen operators for vector, full-text, and
regex search, and our customers are asking for more. The average turbopuffer
text query today, for example, evaluates almost 17 operators (not all unique),
and we expect this number to keep growing.

Loading chart data...

Vectorization allows us to implement more heterogeneous operators through a
simple, generic interface while amortizing dispatch and interpretation overhead
across a large batch of rows.

### Modern hardware rewards predictable, batched work

turbopuffer has been moving toward hardware-friendly search algorithms for
several generations. Instead of traditional HNSW vector indexes, we use
[SPFresh](https://arxiv.org/abs/2410.14452), whose cluster-based design
organizes candidate vectors into partitions that can be scanned in batches.
Instead of the predominant block-max WAND algorithm for text search, we
implement a [vectorized variant of block-max MAXSCORE](/blog/fts-v2-maxscore)
that outperforms the alternatives we tested—especially on long, LLM-generated
queries.

Up until v3, however, vectorized execution was an optimization applied only to
select parts of some operators. With v3, batches are the default unit exchanged
between query-time abstractions, so new operators will naturally participate in
vectorized execution without a bespoke implementation.

In summary: "[Dumb and serial](/blog/zero-cost)" beats "smart and random" on
modern CPUs. To achieve peak search performance, we choose hardware-friendly
algorithms that prioritize serial workloads with predictable branches, even when
those algorithms examine more data. The bet behind turbopuffer v3 is simple:
doing more work, predictably, is faster than doing less work, unpredictably.
Vectorized execution lets the entire engine capitalize on that trade-off.

## turbopuffer

turbopuffer is a fast search engine that hosts 1T+ documents, handles 10M+ writes/s, and serves 100k+ queries/s. We are ready for far more. We hope you'll trust us with your queries.

[Get started](/join)

![turbopuffer logo](/_next/static/media/lockup_transparent.382403b6.svg)

[Company](/about)[Pricing](/pricing)[Merch](https://turbopuffer.supply)[Press & media](/press)[System status](https://status.turbopuffer.com)

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