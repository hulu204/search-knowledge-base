---
title: 'Embedding空间中的时序异常检测'
company: 百度Geek说
tag: 搜索/RAG
date: 2024-08-07
url: https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ%3D%3D&mid=2247592870&idx=1&sn=4356bf3d908eaf1a5457e2c05f06992c
account: 百度Geek说
origin: weread-history-2024
---
。![]()

点击蓝字，关注我们

![]()

作者 | StarKeeper

导读

introduction

本文深入探讨了如何在Embedding空间中运用先进的时序异常检测技术，针对安全、反作弊等业务场景下的流量与用户行为进行精准监控。通过向量化处理和Embedding技术，将多维度的业务数据映射至高维空间，并基于此空间中的样本分布特征进行异常检测。实验验证了该方法在不同异常类型下的有效性，为快速定位和处理异常提供了有力支持。同时，文章还讨论了算法在实际应用中的调整与优化方向，展望了未来在异常检测领域的进一步应用与发展。

*全文5887字，预计阅读时间15分钟。*

GEEK TALK

01

背景

在安全、反作弊等业务场景下，对流量、用户行为进行异常检测是基本的刚需。通常的做法是，在各个业务维度上，对流量、用户行为进行统计分析，提取出相应的指标特征，然后在时间维度上，对这些指标特征进行建模分析。再利用相关的算法来检测当前的指标值是否背离了该指标在历史数据中的分布规律。

GEEK TALK

02

示例

假设某业务场景下，用户有100个来源渠道，用户使用产品时，有10种不同的操作方式，对于用户的行为，我们可以简单的撮取出PV、UV、失败率等指标。那么我们可以建立这样一个监控：

**监控的维度**：来源渠道 \* 操作方式 = 100 \* 10 = 1000个维度

**监控的指标**：PV、UV、失败率...

**统计周期**: 小时

然后针对每个维度、时刻、指标，收集过去30天的数据做为训练样本，训练异常检测模型（如EllipticEnvelope等），然后对当前时刻的指标值，进行异常检测。

上面的方法，通过合理的拆分监控维度，一方面可以有效的提高检测的灵敏度，避免较少的异常流量淹没在大盘监控在随机波动中；另一方面，也可以对异常流量进行快速的定位，便于及时处理。

GEEK TALK

03

问题

上面的方法也存在诸多的限制，比如：

* 监控维度必需是离散、可枚举的，否则无法建立历史数据的统计模型；
* 监控维度的粒度必须合适，否则或是灵敏度不足，或是噪声太多，无法有效检测异常。

显然，不是所有的业务场景都能满足上述的要求。即便是能满足上述要求的业务场景中，随着对攻击者的对抗不断深入，攻击者会尝试降低攻击的规模，并尽量将攻击行为分散到更多的维度中，从而躲避我们的检测手段。

GEEK TALK

04

解决思路

那么，能否不依赖业务维度拆分，直接对指标进行异常检测呢？

首先，我们需要把待检测的每一条日志、数据当做一个独立的样本。接下来，不难联想到，这些样本都可以映射到某个高维空间中，我们把这个空间叫做样本空间。可以通过向量化、Embedding等方法，得到样本在这个空间中的坐标。

样本在这个空间中的分布必然不是完全随机的，而是会存在一定的特点（分布特征）。若当前时刻样本在这个空间中的分布特征与历史数据中的分布特征不一致，则说明当前样本存在异常。而分布在差异最大的区域中的样本，则可以认为是异常样本。

接下来的问题就变成了如何对这种分布特征进行建模？

最先想到的是，我们可以通过聚类算法，来对样本进行划分，再对每个Cluster，提取出统计特征。但在具体实现时还需要考虑以下问题：

* 支持的样本数量要足够多；
* 支持的Cluster数量要足够多；
* 每个Cluster的样本数量要尽可能均匀；
* Cluster的划分要尽可能稳定，才能在时间维度上执行异常检测。

再进一步，其实我们不需要执行完整的聚类算法，我们只需要对样本空间设置足够多的采样点进行采样，计算出采样点附近的样本的统计特征做为采集采样点的分布特征，再对采样点的特征进行时间维度的异常检测，即可完成对整个样本空间的异常检测了。

![]()

GEEK TALK

05

算法实验

**5.1 数据准备**

取某业务场景下近30天的用户行为日志，约160万条，利用其中的UserAgent信息，对其进行向量化处理。每条日志的向量长度为128维。

向量化算法：

```
def to_vector(ua):    if isinstance(ua, (list, tuple)):        return [to_vector(c) for c in ua]    else:        vec = np.zeros(128)        for c in ua:            vec[ord(c) % 128] += 1  # UserAgent中的字符绝大多数都是Ascll字符，所以取余128        l2 = np.sqrt(np.sum(vec * vec))        if l2 != 0:            vec /= l2        return vec.tolist()
```

将清洗好的数据保存到向量DB中备用：

```
for day in days:    for hour in hours:        event_day = day.strftime("%Y%m%d")        event_hour = "{:02d}".format(hour)        collection = chroma_client.get_or_create_collection(            name="{}_{}_{}".format(name_prefix, event_day, event_hour)        )        sub_df = df_ua_pv[(df_ua_pv.event_day == event_day) & (df_ua_pv.event_hour == event_hour)]        ids = [hashlib.md5(bytes(str(row), "utf-8")).hexdigest() for _, row in sub_df.iterrows()]        docs = [row.ua for _, row in sub_df.iterrows()]        metadatas = [{"pv": row.pv} for _, row in sub_df.iterrows()]        embeddings = [to_vector(row.ua) for _, row in sub_df.iterrows()]        batch_size = 10000        for batch_id in range(0, len(docs), batch_size):            collection.upsert(                ids=ids[batch_id : batch_id + batch_size],                documents=docs[batch_id : batch_id + batch_size],                metadatas=metadatas[batch_id : batch_id + batch_size],                embeddings=embeddings[batch_id : batch_id + batch_size],            )            print("{:>8d} / {}".format(batch_id + batch_size, len(docs)))        collections[event_day + event_hour] = collection
```

为了更方便的验证算法的有效性，在数据集中，人工构造了一些异常样本，包括：

* 个别随机UA，PV增长：10%， 20%， 50%， 100%， 200%， 500%，1000%；数量：5；min\_pv=100。
* 部分相似UA，PV增长：5%，10%，20%， 50%， 100%；数量：10， 20， 50， 100；min\_pv=10。
* 生成相似UA，PV同比增长，数量：10， 20， 50， 100。
* 生成相似UA，整体PV不增长，数量：10， 20， 50， 100；min\_pv=1。

**5.2 算法实现**

随机生成采样点：

```
query_ua_list = (    df_ua_pv[(df_ua_pv.event_day == event_day) & (df_ua_pv.event_hour == event_hour)].sample(100)["ua"].to_list())
```

在样本空间进行邻近采样：

```
results = []query_ua_vec = to_vector(query_ua_list)for day in days:    for hour in hours:        res = get_collection(day, hour).query(query_embeddings=query_ua_vec, n_results=n_results)        for i in range(len(query_ua_list)):            for j in range(n_results):                row = [                    query_ua_list[i],                    res["metadatas"][i][j]["event_day"],                    res["metadatas"][i][j]["event_hour"],                    res["documents"][i][j],                    res["metadatas"][i][j]["pv"],                    res["distances"][i][j],                ]                if extra_fields:                    for field in extra_fields:                        row.append(res["metadatas"][i][j].get(field))                results.append(row)cols = ["ua", "day", "hour", "doc", "pv", "dist"]if extra_fields:    cols += extra_fieldsdf_results = pd.DataFrame(results, columns=cols)
```

定义要检测的字段：

```
AREA_EXP = [0, 2, 8]MODEL_FIELDS = ["pv", "dist"]MODEL_FIELDS += [f"dens_{i}" for i in AREA_EXP]MODEL_FIELDS += ["dens_s"]MODEL_AGGS = {}for col in MODEL_FIELDS:    MODEL_AGGS[f"{col}_mean"] = (col, "mean")    MODEL_AGGS[f"{col}_std"] = (col, "std")
```

进行天维度的异常检测：

```
df_query_results["dens_s"] = 1 / (df_query_results["dist"] ** 0.5 + 1)df_res_agg = df_query_results.groupby(["ua", "day"], as_index=False).agg(    pv=("pv", "sum"),    dist=("dist", "mean"),    dens_s=("dens_s", "mean"),)for i in AREA_EXP:    df_res_agg["area_{}".format(i)] = (df_res_agg["dist"] * 10) ** i    df_res_agg["dens_{}".format(i)] = df_res_agg["pv"] / df_res_agg["area_{}".format(i)]df_model = df_res_agg[df_res_agg.day <= last_event_day].groupby("ua").agg(**MODEL_AGGS)df_check = df_res_agg.join(df_model, on="ua")for col in MODEL_FIELDS:    df_check[f"{col}_sigma"] = (df_check[col] - df_check[f"{col}_mean"]) / df_check[f"{col}_std"]df_check["dens_avg_sigma"] = df_check[["dens_s_sigma"] + [f"dens_{i}_sigma" for i in AREA_EXP]].mean(axis=1)df_check["dens_max_sigma"] = df_check[["dens_s_sigma"] + [f"dens_{i}_sigma" for i in AREA_EXP]].max(axis=1)df_check["dens_min_sigma"] = df_check[["dens_s_sigma"] + [f"dens_{i}_sigma" for i in AREA_EXP]].min(axis=1)
```

GEEK TALK

06

### **实验效果**

**6.1 实验一**

个别随机UA，PV增长：10%， 20%， 50%， 100%， 200%， 500%，1000%；数量：5；min\_pv=100。

异常样本与原始样本的异常置信度分布对比如下图，由上到下分别为：

* 天级检测下异常样本的置信度分布；
* 天级检测下正常样本的置信度分布；
* 小时级检测下异常样本的置信度分布；
* 小时级检测下正常样本的置信度分布。

![]()

天级检测不同阈值下的准召情况：

![]()

小时级检测不同阈值下的准召情况：

![]()

**6.2 实验二**

部分相似UA，PV增长：5%，10%，20%， 50%， 100%；数量：5, 10, 20；  min\_pv=10。

异常样本与原始样本的异常置信度分布对比如下图，由上到下分别为：

* 天级检测下异常样本的置信度分布；
* 天级检测下正常样本的置信度分布；
* 小时级检测下异常样本的置信度分布；
* 小时级检测下正常样本的置信度分布。

![]()

天级检测不同阈值下的准召情况：

![]()

小时级检测不同阈值下的准召情况：

![]()

**6.3 实验三**

生成相似UA，PV同比增长，数量：5, 10， 20， 50， 100。

异常样本与原始样本的异常置信度分布对比如下图，由上到下分别为：

* 天级检测下异常样本的置信度分布；
* 天级检测下正常样本的置信度分布；
* 小时级检测下异常样本的置信度分布；
* 小时级检测下正常样本的置信度分布。

![]()

天级检测不同阈值下的准召情况：

![]()

小时级检测不同阈值下的准召情况：

![]()

**6.4 实验四**

生成相似UA，整体PV不增长，数量：10， 20， 50， 100；min\_pv=1。

异常样本与原始样本的异常置信度分布对比如下图，由上到下分别为：

* 天级检测下异常样本的置信度分布；
* 天级检测下正常样本的置信度分布；
* 小时级检测下异常样本的置信度分布；
* 小时级检测下正常样本的置信度分布。

![]()

天级检测不同阈值下的准召情况：

![]()

小时级检测不同阈值下的准召情况：

![]()

GEEK TALK

07

总结与展望

通过实验，验证了该算法的有效性，但在后续的工程化应用中，还需要结合具体的应用场景进行适当的调整。比如采样点的数量、采样点的选取方法、样本Embedding方法、距离计算方法等。

此外，在实践中，若要发挥出异常检测的真正价值，还需要考虑以下问题：

* 检测到异常后，如何快速定位到异常样本；
* 异常样本定位后，如何快速度评估分析，确定异常是否需要进一步处理；
* 若需要进一步处理，如何快速定位到异常样本来源特征，制定出相应的攻防策略等。

END

**推荐阅读**

[读友好的缓存淘汰算法](http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247592850&idx=1&sn=76f6451f3f149d210106dab1e036298c&chksm=c03f5beef748d2f8e47da9b2dec927af37b69d534958950e9bda1547645e2b9583acebd4335f&scene=21#wechat_redirect)

[如何定量分析 Llama 3，大模型系统工程师视角的 Transformer 架构](http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247592618&idx=1&sn=61740f39ea744e00280c70b638622b91&chksm=c03f5ad6f748d3c02b964f5f2d5c1b716c38c98c630d4741f4b687821c33d52f16b2cc8de612&scene=21#wechat_redirect)

[微服务架构革新：百度Jarvis2.0与云原生技术的力量](http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247592237&idx=1&sn=99dff8b8971f210c69ee50fa7383b9ee&chksm=c03f5951f748d0470163cdd13a5ce7d591a2054840fe8278ef7d5f4ba8ce7c374813ba823daf&scene=21#wechat_redirect)

[技术路线速通！用飞桨让京剧人物照片动起来](http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247591996&idx=1&sn=c5b5f19bf8f26d43b923c953273fe8cf&chksm=c03f5840f748d156881e820c037d719ae43b8c5387a89f44300692dc0de9ad6d93b04a108dd2&scene=21#wechat_redirect)

[无需业务改造，一套数据库满足 OLTP 和 OLAP，GaiaDB 发布并行查询能力](http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247591982&idx=1&sn=33db28d92148841f38b91779f2469101&chksm=c03f5852f748d1444e421bafb73dbe22f27614bf98131dd39091e53f9b7c3170dea0a39b1349&scene=21#wechat_redirect)

![]()

一键三连，好运连连，bug不见👇