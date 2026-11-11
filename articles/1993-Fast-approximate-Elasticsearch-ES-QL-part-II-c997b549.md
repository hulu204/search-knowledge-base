---
title: 'Fast approximate Elasticsearch ES|QL - part II'
company: Elastic
tag: 工程相关
date: 2026-04-17
url: https://www.elastic.co/search-labs/blog/fast-approximate-esql-part-2
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Fast approximate Elasticsearch ES|QL - part II

Explaining the approach we use to obtain fast approximate Elasticsearch ES|QL queries and the testing we did of error estimation.

April 17, 2026

[Thomas Veasey](/search-labs/author/thomas-veasey)[Jan Kuipers](/search-labs/author/jan-kuipers)

[ES|QL](/search-labs/blog/category/esql)

Part of the series:

[Fast Approximate ES|QL](/search-labs/blog/series/fast-approximate-es-or-ql)

In this series

Share

As we discussed in our [previous blog](https://www.elastic.co/search-labs/blog/fast-approximate-esql-part-1), we’re introducing fast approximate [ES|QL](https://www.elastic.co/docs/explore-analyze/query-filter/languages/esql) `STATS` queries, which will be available in version 9.4 of Elasticsearch and the Elastic Stack. This feature allows users to estimate an expensive analytics query, often orders of magnitude faster than running the full query, by relaxing the constraint that it returns the exact value. We believe this has many uses; for example, we’re planning to integrate it into Kibana to obtain fast chart previews where possible.

In order for you to be able to trust our estimates, we provide error estimates. Furthermore, since there are edge cases in error estimation, we certify when the estimated value and error are trustworthy. In this blog post, we’ll dive into the theory for approximating and estimating the error in such queries, as well as discuss the testing we’ve done.

### Background

In order to estimate ES|QL `STATS` queries efficiently, we make use of a property that’s shared by many statistics: Their estimates computed from a large number of independent samples from a dataset approach their true value. In the case of an index with some field X={xi},X=\{x\_i\},X={xi​}, we can think of the true value of a statistic as its value computed for a random variable with uniform discrete distribution on XXX. In the following we denote this quantity θ\thetaθ; it can be things like `AVG`, `MEDIAN`, and so on. If we make nnn independent draws from XXX, denoted SSS, such that each value is selected with probability 1∣X∣\frac{1}{|X|}∣X∣1​, we have nnn independent copies of this random variable. The property we rely on means that a sample statistic value θ^\hat{\theta}θ^ computed from SSS approaches θ\thetaθ as nnn becomes large. For example, if θ\thetaθ is the mean of some metric values then θ^=1∣S∣∑x∈Sx→1∣X∣∑x∈Xx=θ\hat{\theta} = \frac{1}{|S|}\sum\_{x\in S} x \rightarrow \frac{1}{|X|}\sum\_{x\in X} x=\thetaθ^=∣S∣1​∑x∈S​x→∣X∣1​∑x∈X​x=θ as ∣S∣=n|S|=n∣S∣=n becomes large. Indeed, for many statistics the limiting error distribution is known to be normal. Furthermore, it only depends on the distribution of XXX, the size of the sample nnn and the type of the aggregation θ\thetaθ. This means supported `STATS` queries can be approximated with fixed accuracy independent of the index size ∣X∣|X|∣X∣.

It is easy to pick values at random from a Lucene index: create a filter that takes exponentially distributed jumps through the dataset, where the expected jump size is controlled by the desired sample probability. The AND of this filter and any other Lucene query can be performed extremely efficiently, since AND’ing filter queries is one of the things for which it is well optimized. In our other post, we discussed some real-world query examples to give a sense of the speedup we obtain for different levels of accuracy.

So far, we've only discussed obtaining an estimate of a query. While such a point estimator can be useful, without knowing anything about its error those uses are limited. We found that ES|QL has existing capabilities that make it relatively easy to incorporate cheap, flexible, and accurate error estimation at the same time. We'll discuss this next.

### Error estimates

We view providing an accurate understanding of the uncertainty in our estimates as crucial for users to be able to trust the approximation. While having the option to quickly estimate an ES|QL query alone can be useful in certain situations, we wanted to provide a richer feature that allows clients to make intelligent choices. For example, if an approximate query is being used to preview a chart and the error is only a couple of pixels, there’s little point in running another expensive query to redraw it.

The way we've chosen to represent error is by a confidence interval: the α\alphaα-central confidence interval, to be precise. This can be expressed in terms of the [cumulative density](https://en.wikipedia.org/wiki/Cumulative_distribution_function), FFF, of the statistic being estimated. Specifically, it's the interval which contains the true value of the statistic with probability α\alphaα whose endpoints are F−1(1−α2)F^{-1}\left(\frac{1-\alpha}{2}\right)F−1(21−α​) and F−1(1+α2)F^{-1}\left(\frac{1+\alpha}{2}\right)F−1(21+α​). Confidence interval calculations are surprisingly subtle. There are also important constraints for our use case that make standard approaches undesirable. Next, we’ll take a look in more detail at the motivation and the design for the approach we’ve adopted.

A key requirement of the whole project is to dramatically accelerate expensive analytics queries. It’s therefore vital that the overhead of estimating uncertainty isn’t too large compared to estimating the query result itself. We also want the feature to be as general as possible, but “isolated” within the language. In other words, ES|QL is a flexible language, and we want estimation to work with as much of it as possible. At the same time, we don’t want to introduce a cross-cutting feature that incurs development costs on every new feature we ship.

With these considerations in mind, we chose to estimate confidence intervals by partitioning the sample set and computing the query output on each subsample. This is reminiscent of bootstrap; however, since we ensure that each partition receives a disjoint random subset of the sample data, we know that they comprise true estimates of the statistic distribution. To achieve the best possible estimate of the statistic itself, we still compute its value on the full sample. For example, to estimate the mean and its distribution the process can be expressed as follows:

```
FROM data | SAMPLE probability
          | EVAL bucketId = RANDOM(B) // B is the number of buckets
          | STATS avg     = AVG(x)
                  avg_0   = AVG(x) WHERE bucketId==0  
                  (...)
                  avg_B-1 = AVG(x) WHERE bucketId==B-1
            BY grouping
          | EVAL confidence_interval = CONFIDENCE_INTERVAL(avg, avg_0, ..., avg_B-1)
```

This introduces a complication to account for the discrepancy between the count of values used to estimate a query statistic and used to sample its distribution. This is a downside; however, there are some significant advantages.

Most of the work in analytic queries resides in computing the aggregate statistics: post-processing after a `STATS` reduction acts on a far smaller table, and the cost is often relatively small. In this scheme, every row in the input data to the `STATS` command is processed exactly twice compared to just estimating the statistic. Therefore, roughly speaking we pay a fixed overhead that's the same order of magnitude as the cost of estimating the query in order to estimate its uncertainty. Since we often achieve multiple orders of magnitude speedup on the exact query, this is acceptable.

Because this process uses a plain old table, with extra columns for the distribution samples, we can pass the whole table through any ES|QL pipeline and compute confidence intervals on the final results. For example, if we include `EVAL square_avg = avg * avg` in the pipeline above, we'd have exactly the same `square_avg`, `square_avg_0`, …, `square_avg_B-1` extra values. At the end of the pipeline, we have samples from the distribution of the original statistics and all quantities that are computed using them. Therefore, we can apply our standard confidence interval machinery to reduce the table and convert samples into confidence intervals for derived quantities as well. This whole process is essentially transparent to the rest of the ES|QL language, and as we showed above, can be achieved by query rewriting.

### The confidence interval calculation

We have independent samples of the statistic distribution {θ^i}\{\hat{\theta}\_i\}{θ^i​}. However, they're computed with fewer values than our estimate θˉ\bar{\theta}θˉ. We also have a relatively small number of distribution samples, to avoid the count discrepancy being too large, and so we don’t inflate the table too much. We therefore prefer a parametric approach for estimating confidence intervals.

The errors in the statistics for which we support estimation tend to normal distributions in the limit they're computed from many values. So a natural choice, the standard interval, is to estimate the mean and standard deviation from the samples and report the corresponding normal confidence intervals [m+σΦ−1(1−α2),m+σΦ−1(1+α2)]\left[ m+\sigma \Phi^{-1}\left(\frac{1-\alpha}{2}\right), m+\sigma \Phi^{-1}\left(\frac{1+\alpha}{2}\right) \right][m+σΦ−1(21−α​),m+σΦ−1(21+α​)]. Here, Φ\PhiΦ denotes the standard normal distribution function. For heavy-tailed data and statistical functions that are sensitive to outliers, such as `STD_DEV`, convergence to normality can be slow, resulting in poorly calibrated intervals.

Briefly, in order to assess the quality of the intervals, one can examine their calibration. Specifically, one computes a quantity called the [coverage](https://en.wikipedia.org/wiki/Coverage_probability). For a central confidence interval, it should contain the true statistic value roughly (1−α)n(1-\alpha)n(1−α)n times for nnn trials. In fact, since we seek the central confidence interval, we can make the stronger statement that the true value should be above, or below, the confidence interval endpoints in roughly 1−α2n\frac{1-\alpha}{2} n21−α​n out nnn trials. The empirical coverage is this fraction computed for a large number of trials. It allows us to compare alternative approaches by simulation. We return to this when we report our test results.

In order to obtain better confidence intervals, we tried a couple of different approaches: the [Cornish-Fisher](https://en.wikipedia.org/wiki/Cornish%E2%80%93Fisher_expansion) correction of quantiles and an adaptation of [bias-corrected accelerated](https://en.wikipedia.org/wiki/Bootstrapping_(statistics)#Deriving_confidence_intervals_from_the_bootstrap_distribution) (BCa) confidence intervals. Simulation showed BCa provided more robust calibration across a range of confidences, so this is the approach we selected. The basic idea, which was introduced by Efron, is to assume that there exists a monotonic transformation of the underlying statistic g=g(θ)g=g(\theta)g=g(θ) which, when applied to a distribution sample normalizes its distribution:

ϕ^=ϕ+(1+aϕ)(N(0,1)−z0)                                                          (1)\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\hat{\phi}=\phi+(1+a \phi) \left(N(0,1) - z\_0 \right)\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;\;(1)ϕ^​=ϕ+(1+aϕ)(N(0,1)−z0​)(1)

Here, ϕ^=g(θ^)\hat{\phi}=g(\hat{\theta})ϕ^​=g(θ^), ϕ=g(θ)\phi=g(\theta)ϕ=g(θ) and N(0,1)N(0,1)N(0,1) is the standard normal random variable. This is clearly a relaxation of the assumption that the statistic itself is normally distributed, which is used to derive the standard interval. In fact, this family includes many distributions, since ggg is only constrained to be monotonic. (You can think of 1+aϕ=1+ag(θ)1+a\phi=1+a g(\theta)1+aϕ=1+ag(θ) as a first-order Taylor expansion of the case that the variance is an arbitrary function of the true parameter value. This further relaxes the assumption that the normalizing transformation also stabilizes the variance.) The nice thing about this ansatz is that ggg never needs to be explicitly computed, and there exist standard approaches for estimating the parameters aaa and z0z\_0z0​ from the distribution samples.

To handle z0z\_0z0​ one simply arranges for the estimate to land at the median of transformed distribution. If we assume the cumulative distribution function in theta space is FθF\_{\theta}Fθ​ then z0=Φ−1(Fθ(θˉ))z\_0=\Phi^{-1}(F\_{\theta}(\bar{\theta}))z0​=Φ−1(Fθ​(θˉ)), where θˉ\bar{\theta}θˉ is the estimated statistic value, and as before Φ\PhiΦ is the standard normal distribution function. Typically, FθF\_{\theta}Fθ​ is approximated by the empirical distribution function, computed indirectly by bootstrap. However, somewhat surprisingly, extensive simulation showed that we obtained better calibrated intervals using a normal approximation to our sample values, i.e. Fθ(θˉ)=Φ(θˉ−θ^σ^)F\_{\theta}(\bar{\theta})=\Phi \left( \frac{\bar{\theta}-\hat{\theta}}{\hat{\sigma}}\right)Fθ​(θˉ)=Φ(σ^θˉ−θ^​) with θ^\hat{\theta}θ^ and σ^\hat{\sigma}σ^ their empirical mean and standard deviation, respectively.

To complete the procedure, one can rearrange (1) to derive αθ\alpha\_{\theta}αθ​ quantiles for θ\thetaθ as follows:

αθ=Φ(z0+z0+zα1−a(z0+zα))\alpha\_{\theta}=\Phi\left( z\_0 + \frac{z\_0+z\_{\alpha}}{1 - a (z\_0+z\_{\alpha})}\right)αθ​=Φ(z0​+1−a(z0​+zα​)z0​+zα​​)

where zαz\_{\alpha}zα​ is the standard normal z-score for quantile α\alphaα. Typically, one uses the inverse empirical cumulative density estimate of Fθ−1F\_{\theta}^{-1}Fθ−1​ to convert quantiles back to a confidence interval. However, because we have a mismatch between the count of values used to compute distribution samples and the query estimate, we need to do some sort of scaling. Exploring options by simulation, we again found it best to use a normal approximation, Fθ−1(αθ)=m^+σ^sΦ−1(αθ)=m^+σ^s(z0+z0+zα1−a(z0+zα))F\_{\theta}^{-1}(\alpha\_{\theta})=\hat{m}+\frac{\hat{\sigma}}{\sqrt{s}}\Phi^{-1}(\alpha\_{\theta})=\hat{m}+\frac{\hat{\sigma}}{\sqrt{s}}\left( z\_0 + \frac{z\_0+z\_{\alpha}}{1 - a (z\_0+z\_{\alpha})}\right)Fθ−1​(αθ​)=m^+s​σ^​Φ−1(αθ​)=m^+s​σ^​(z0​+1−a(z0​+zα​)z0​+zα​​), where sss is the number of distribution samples we use. This is just applying the usual scaling of variance by 1sample size\frac{1}{\sqrt{\text{sample size}}}sample size​1​.

Efron showed that in the case θ^\hat{\theta}θ^ is distributed as fθf\_{\theta}fθ​, i.e. that it depends only on the true value θ\thetaθ, then the acceleration aaa can be estimated without any knowledge of ggg. In particular, a=16SKEW(∂fθ∂θ)a=\frac{1}{6}\text{SKEW}\left(\frac{\partial f\_{\theta}}{\partial \theta}\right)a=61​SKEW(∂θ∂fθ​​). By assumption, our statistics tend to normal distributions with mean θ\thetaθ. Since skew is translation and scale invariant, this gives that a≈16SKEW({θ^})a \approx \frac{1}{6}\text{SKEW}(\{\hat{\theta}\})a≈61​SKEW({θ^}), i.e. one sixth of the skew of our distribution samples. One thing this glosses over is the dependence of skew, and therefore acceleration, on sample size. We know it tends to zero as the count increases. In fact, skew also asymptotes to zero as 1sample size\frac{1}{\sqrt{\text{sample size}}}sample size​1​ and so we also adjust acceleration to be 16sSKEW({θ^})\frac{1}{6\sqrt{s}}\text{SKEW}(\{\hat{\theta}\})6s​1​SKEW({θ^}) to account for the count mismatch between the samples {θ^}\{\hat{\theta}\}{θ^} and estimate θˉ\bar{\theta}θˉ.

Although we significantly improve the calibration of confidence intervals by using a better methodology, we still see issues in the case that the underlying distribution has very heavy tails for some of the supported `STATS` functions. Therefore, we introduce some additional guard rails we discuss next.

### Guard rails

To avoid the user having to understand too much about edge cases, we provide additional safeguards that surface when we've been unable to confirm that the distribution samples behave as we expect. This typically happens when the statistic isn’t computed from a sufficient number of values given the metric distribution. It's exacerbated by very skewed metric data and certain aggregation functions, such as the `STD_DEV`, which are sensitive to outliers.

We have some global constraints on the minimum count of values used to estimate a statistic for which we'll certify it. For example, if any bucket is empty, then we can’t rely on the distribution samples. This is because ES|QL allows mixing approximate statistics, which treat empty buckets differently. For example, consider the following query:

```
SET approximation=true;
FROM data | STATS avg = AVG(x), sum = SUM(y) | EVAL mix = avg + sum
```

There is no self-contained way of correctly assigning a value to `mix` for empty buckets, since summing requires that we treat them as zero, in which case we bias our estimate of `avg`. Alternatively, ignoring empty buckets introduces bias in the `sum`. There is also a global minimum count of values for which we’ve verified our certification method is sufficiently reliable; this is 10.

We explored a variety of additional tests to certify the results. These were based on both tests of the underlying data distribution, specifically [Hill’s estimator](https://en.wikipedia.org/wiki/Heavy-tailed_distribution#Hill.27s_tail-index_estimator), as well as the statistic’s distribution properties. If the true distribution of the statistic is sufficiently normal, then our estimate and confidence interval calculation behaves as we expect: The interval is well calibrated and the interval width is representative of the actual error. Therefore, in the end, we chose to use a test based on the p-value for distribution samples’ [skewness](https://en.wikipedia.org/wiki/Skewness) and [kurtosis](https://en.wikipedia.org/wiki/Kurtosis) versus a normal distribution null hypothesis. To certify a result, we require that the two tail p-values are greater than 0.05 for both tests. As we show below, we found this test was well aligned to our actual needs: to distinguish results for which the estimate and its confidence interval are more and less reliable.

There's a simple trick we can use to boost the accuracy of the accuracy of the test: Create multiple independent distribution samples and use a vote. Given a test to certify results with a failure rate fff, the distribution of the count of kkk failures for ttt tests is t!k!(t−k)!fk(1−f)t−k\frac{t!}{k!(t-k)!}f^k(1-f)^{t-k}k!(t−k)!t!​fk(1−f)t−k for the case the null hypothesis, that the estimate is trustworthy, is true. For example, for the majority vote assuming f=0.05f=0.05f=0.05 and t=3,t=3,t=3, then the significance of the test is 1−(3×0.952×0.05+0.953)=0.0071-(3\times 0.95^2\times 0.05+0.95^3)=0.0071−(3×0.952×0.05+0.953)=0.007, i.e. we fail to certify fewer than 1% of trustworthy results. Note that we can compute multiple trials relatively easily using different seeds for the `RANDOM` bucket identifier.

This additional check allows us to certify that we trust our estimates and their errors. We surface this information in the approximate query results. When we can’t certify results, they won’t necessarily be inaccurate, but they should be treated with more caution.

### Testing

The two main aims of the testing we discuss here were to understand the calibration of the confidence intervals and to see how well they characterize the statistics' estimation errors. The count function is particularly well behaved, its error distribution is binomial, so the majority of our testing focused on metric aggregations. We study smooth distributions but make sure we cover a range of tail behaviors. The presence of outliers is the key factor that reduces the accuracy of estimated statistics. For example, if an outlier isn’t sampled at all, it can significantly affect the value of some statistics.

We explored a range of light-tailed distributions, such as uniform and normal, and skewed and heavy-tailed distributions, such as exponential, log-normal, Cauchy, and Pareto. For each family of distribution, we used multiple parameterizations, focusing primarily on varying the scale parameter. In total, we had 24 distinct data distributions. Figure 1 shows some example sample distributions from this set. Note that we’ve truncated the charts to remove extreme outliers, which are present for both the Cauchy and log-normal distributions.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6e7b7df23a7e1faa/6a170ca0c1e8a505d7f88312/fb088c17f9755c0d1b3173fb917f0af2c0f83847-1712x950.png)

Figure 1 - Example metric sample distributions

For each data distribution, we evaluated 14 different sample sizes, ranging from 1000 to 500000. Then, for each sample set, we evaluated `AVG`, `COUNT`, `MEDIAN_ABSOLUTE_DEVIATION`, `MEDIAN`, `PERCENTILE([25, 75, 90, 95, 99])`, `SUM` and `STD_DEV` at two levels of confidence, 50% and 90%. In total, we have around 7500 distinct experiments. For each experiment, we assessed the interval calibration using 100 runs and counting the number of times the true statistic lands in the confidence interval. This gives us a binomially distributed estimate for the true confidence interval coverage. The variation we expect in the estimated coverage changes slightly with the level of confidence; for example, at 50% we expect to see values mainly between 0.44 and 0.56, and for 90% we expect to see values mainly between 0.86 and 0.94 using 100 trials.

Figure 2 shows [box plots](https://en.wikipedia.org/wiki/Box_plot) for the empirical coverage for the two confidence levels computed from all experiments. In all cases, the confidence intervals are reasonably well calibrated. Extreme percentiles are biased for small sample sizes, which leads to increased outlier counts for small sample sizes. As a rule of thumb, you’d want roughly 10p(1−p)\frac{10}{p(1-p)}p(1−p)10​ samples to ensure that you have enough samples in the appropriate tail.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte33fb7bc54844a83/6a170ca2839dfa7a19dcff38/02a5375025e811ba18c4e823e1d984261bbf6f42-631x763.png)

Figure 2 - Empirical coverage of the 50% and 90% confidence intervals for certified results

Next, we examine the degree to which the confidence intervals capture the typical size of the estimate error. To do this, we examine the distribution of the ratio of the estimated statistics' error and half the confidence interval width for all certified results. The higher the confidence, the wider the interval, so different confidence levels shift the mean of this distribution. Figure 3 shows this distribution computed for the 90% confidence interval. As expected, the distribution is roughly normal, albeit with a tail of some larger errors. We see in all cases the confidence interval width gives the order of magnitude of the estimated statistics' actual errors.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3d4bc25885b66945/6a170ca360084b472d3c45b4/2d4ab88a07910edac7e8406ae4942694751f0090-1000x600.png)

Figure 3 - Query error as a function of certified confidence interval width

We’ve shown that certified results are nearly always reliable; however, we’d also like some insight into the proportion of results which we fail to certify that are actually reliable, to confirm that the test aligns with our objective. We use *reliable* here in the fairly strong sense that the confidence interval is well calibrated. Specifically, for the 50% and 90% confidence intervals, we count the proportion of uncertified results for which the confidence interval empirical calibration has an acceptable margin of error, given the number of trials used to estimate it. Using this procedure, the false positive rate across all experiments is around 1%. This agrees well with the failure rate we expect by chance, given our test parameters, and confirms the assumption underlying the test.

Finally, to better understand the difference between certified and uncertified results, Figure 4 shows the error distribution of the ratio of the estimated statistics' errors and half the 90% confidence interval for the reliable and unreliable results separately. Note that we truncated the range for uncertified intervals.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0c4f729eb4c1127c/6a170ca5961e69c63cc4cf66/c0cd6d42f5d061aac15767539209a7c443ed1acd-1000x600.png)

Figure 4 - Query error as a function of certified and uncertified confidence intervals

### Wrapping up

In this post, we present the background behind our approach for quickly estimating ES|QL queries and providing an indication of their errors. To do this, we developed an effective confidence interval mechanism that allows us to provide error estimates. Our approach also allows us to estimate confidence intervals for quantities derived from sampled statistics via other pipeline operations. Quantifying the error comes with a relatively small overhead compared to just estimating the query. Finally, we developed a statistical test to certify results we return. Values that aren’t certified can still be accurate, but we’re less confident in them.

As well as testing the feature on a range of real-world use cases, which we discuss in [our companion post](https://www.elastic.co/search-labs/blog/fast-approximate-esql-part-1), we tested the error estimation by extensive simulation across a range of data characteristics, sample sizes, aggregation functions, and confidence levels. This showed confidence intervals are well calibrated, and the interval itself provides a good approximation of the actual error we observe in the estimates. Finally, we showed that we were able to certify intervals with a low false negative rate.

We’re planning to integrate this feature into other stack capabilities in the future, so stay tuned.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt4f83670092c8d0c2/6a170a560c4857412801aa59/21c42530fbbd95b10e09a1169afa4dbf379b4d92-3420x1814.png)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### A new era for Elastic Discover: ES|QL, context & multi-tabs

October 24, 2025|[Ninoslav Miskovic](/search-labs/author/ninoslav-miskovic)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltf76dd688c5b737e6/6a170cc9839dfa7fc7dcff40/21036e031070f14faccb2b53b22723de2750c391-1280x720.png)

[ES|QL](/search-labs/blog/category/esql)

### Faster ES|QL stats with Swiss-style hash tables

January 19, 2026|[Chris Hegarty](/search-labs/author/chris-hegarty)|[+2](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter