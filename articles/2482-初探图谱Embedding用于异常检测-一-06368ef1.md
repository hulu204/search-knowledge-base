---
title: '初探图谱Embedding用于异常检测（一）'
company: 百度Geek说
tag: 搜索/RAG
date: 2024-12-18
url: https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ%3D%3D&mid=2247603628&idx=1&sn=f75ddec65ee183dc0c3d48b7e1fdb1ea
account: 百度Geek说
origin: weread-history-2024
---
。![]()

点击蓝字，关注我们

![]()

作者 | StarKeeper

导读

introduction

本文探讨了图谱Embedding在业务安全与反作弊等关键业务场景中的应用，特别是在异常检测方面。传统的统计方法在面对复杂多变的攻击场景时显得力不从心，因此本文介绍了一种基于One-Hot编码的图谱Embedding算法GEE，通过标签传播实现结点特征的表达。作者还通过两篇论文的代码验证，发现稀疏矩阵改进版算法在测试数据集上性能不佳，并进一步优化了算法，使其在计算效率上有所提升。本文对于利用图谱数据进行异常检测的研究和实践具有一定的指导意义。

*全文11456字，预计阅读时间29分钟。*

在安全监控与反作弊等关键业务场景中，对流量数据和用户行为进行异常检测是不可或缺的基石。传统的方法涉及在各个业务层面上对流量和用户行为进行统计分析，提取关键指标特征，并在时间轴上对这些特征进行建模分析。借助相关算法，我们可以检测当前指标值是否偏离了其在历史数据中的正常分布模式。

然而，随着攻击手段的不断演变，单纯的统计方法在面对复杂多变的攻击场景时已显得力不从心。尤其对于规模较小、缺乏显著聚集特征的攻击行为，传统的统计方法往往难以奏效。在此情境下，我们常需借助多种辅助手段来聚合样本，并对聚合后的样本进行统计建模分析，以判断其是否异常。

在之前的文章:[Embedding空间中的时序异常检测](https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247592870&idx=1&sn=4356bf3d908eaf1a5457e2c05f06992c&scene=21#wechat_redirect)，我已详细介绍了一种利用特征Embedding聚类来建模用户行为并进行异常检测的方法。另一种常用的样本聚合手段则是借助图谱数据来识别团伙行为。由此，一个自然而然的思路是，若能恰当地对图谱数据进行Embedding处理，我们便能复用前述方法，对团伙行为进行异常检测。

然而，图谱数据的Embedding处理历来成本高昂，无论是计算成本还是存储成本都颇为可观。在业务实践中，我们所涉及的数据规模通常极为庞大，且异常检测对计算时效性有着一定的要求。因此，图谱Embedding的应用范围长期受到限制。  
不过，近期我偶然发现的两篇论文或许能为我们带来转机。以下是论文的原文链接：

* ﻿https://arxiv.org/abs/2109.13098﻿
* ﻿https://arxiv.org/abs/2406.03726

GEEK TALK

01

**GEE算法简介**

在第一篇论文中，作者提出了一种基于One-Hot编码的图谱Embedding算法——GEE(Graph Encoder Embedding)。

![]()

GEE算法的伪码如上，可以看到该算法的原理并不复杂，核心步骤如下：

1. 首先构造输入数据：

1. E: 图谱的边集，是一个三元组的列表，每个元组的三个元素分别代表两个顶点的索引值，以及边的权重。
2. Y: 图谱的顶点集，是一个整数列表，长度为N, 每个元素为相应顶点的标签，取值范围为[0, K], K为标签的类别数量。

2. 初始化Embedding矩阵与权重矩阵：

1. Z: 顶点Embedding矩阵，维度为[N,K]，其中N是顶点的数量，K是Embedding的维度，同时也是项点标签的类别数量。
2. W: 权重矩阵，维度同样为[N,K]，含义同上。

3. 计算权重矩阵：

1. 针对每一种标签K，计算其对应的权重：

   i. 查找该标签对应的顶点数量，记为n\_k。

   ii. 将该标签对应的项点与该标签的关系权重点设置为\frac{1}{n\_k}。

4. 计算Embedding矩阵：

1. 针对E中的每一条边：

   i: 将Z中源顶点与目标顶点标签对应的Embedding值，与权重矩阵中的目标顶点与目标项点标签对应的权重值与边的权重的乘积相加

   ii：将Z中目标顶点与源顶点标签对应的Embedding值，与权重矩阵中的源顶点与源项点标签对应的权重值与边的权重的乘积相加

从上面的过程不难看出，算法的核心思想其实是标签传播，通过在传播过程进行适当的加权，实现结点特征的表达。更多细节可以参考论文原文。从论文中的实验提供的数据来看，该算法在效果上略逊于随机游走算法，但在计算效率上有着数量级的提升。

在第二篇论文中，作者利用稀疏矩阵计算库`scipy.sparse`，对GEE算法进行了改进，进一步提高了计算效率。同时还提供了可以直接使用的实现代码。

GEEK TALK

02

**算法验证**

由于算法的原理实在太过简单，不免让人怀疑其在真实业务场景中是否真的有效，因此，需要利用真实数据来验证算法的有效性。

**2.1 数据准备**

从业务日志中抽取了用户ID、IP、设备ID、浏览器ID等字段做为顶点，建立了用户行为图谱，图谱中包含了约1000万条边。

针对IP、设备ID、浏览器ID等顶点，分别符加了地域（省份）、操作系统等标签，标签的维度为50。标签规则如下：

* 所有的用户ID顶点，标签统一为0
* IP顶点，标签为IP所属的省份的编号（1~34，未知为0） + 1
* 设备ID顶点，设备的操作系统编号（1~6，未知为0） + 36
* 浏览器ID顶点，浏览器的操作系统编号（1~6，未知为0） + 43

举例说明：

* 某个IP顶点，其所属省份的编号为10，其标签为11
* 某个设备顶点，其操作系统编号为3，其标签为39

**2.2 算法初步验证**

两篇论文均附带了参考实现的代码，然而，第一篇论文提供的代码需要经过修改才能顺利运行，相比之下，第二篇论文提供的代码则可直接执行。因此，在验证原始算法时，采用了第二篇论文中提供的Python实现代码（访问链接：https://github.com/xihan-qin/GEE\_sparse）。

在性能方面，我们对数据集进行了Embedding计算。结果显示，原始算法耗时约55秒，这一表现符合预期并具有实用价值。然而，令人惊讶的是，稀疏矩阵改进版的算法耗时高达约158秒，性能并未有所提升，反而有所下降。深入分析后发现，改进后的算法在计算过程中，需先将原始边集转换为稀疏矩阵，再借助`scipy.sparse`库进行计算，该转换过程便耗时约90秒。即便不计入这一转换时间，改进后的算法在我们的测试数据集上的表现仍不及原始算法。

在审阅参考实现代码的过程中，我们还发现了以下问题：

* 由于每个顶点仅有一个标签，因此同类顶点在权重矩阵W中的值相同。这意味着原始算法的权重矩阵W在计算和存储结构上均可进行简化。
* 原始算法的Embedding矩阵计算过程中，每次仅处理一条边，未能充分利用现代CPU的向量化计算能力。
* 稀疏矩阵改进版的算法在计算Embedding矩阵时，采用矩阵乘法一次性处理所有边，虽能利用CPU的向量化计算能力，但在数据量较大时，会严重依赖内存容量与带宽，导致计算效率降低。这可能是该算法在测试数据集上性能不佳的原因。

看到这里，做为一个资深码农，已经按耐不住要对算法再次进行改进了。

GEEK TALK

03

算法改进

**3.1 简化权重矩阵**

首先是简化了权重矩阵的版本，同时也作为后续改进的基准版本。

```
def graph_encode_embedding(X, Y, n_K, show_prog=False):    """    compute the edge embedding matrix Z and node weight matrix W    参考论文的原始实现  
    :param X: edge list, list of tuple, [(src, dst, weight), ...]    :param Y: node label, array of int, [node_label, ...]    :param n_K: number of classes    :return: Z, W    """    # 初始化权重矩阵W    W = np.zeros(n_K)    # 遍历每个类别    for k in range(n_K):        # 统计每个类别的节点数量        W[k] = (Y == k).sum()    # 计算每个类别的权重，即每个类别节点数量的倒数，为了避免除零错误，分母加1    W = 1 / (W + 1)    # 初始化节点嵌入矩阵Z，该矩阵的行数是节点的数量，列数是类别的数量，实际上是保存了每个节点与每个类别之间的相关性权重    Z = np.zeros((Y.shape[0], n_K))  
    # 初始化Jupyter进度条    if show_prog:        total = len(X)        steps = 0        prog_bar = ProgressBar(100)        prog_bar.display()  
    # 遍历每一条边，更新对应节点的嵌入向量    for src, dst, edg_w in X:        # 取出边的源节点和目标节点的标签        src = int(src)        dst = int(dst)        label_src = Y[src]        label_dst = Y[dst]        # 如果目标节点有标签（>=0），则更新源节点的嵌入向量        if label_dst >= 0:            # 更新源节点的嵌入向量，对源节点与目标节点对应的类别的权重进行累加            Z[src, label_dst] = Z[src, label_dst] + W[label_dst] * edg_w        # 如果源节点有标签（>=0）且不是自环，则更新目标节点的嵌入向量        if (label_src >= 0) and (src != dst):            # 更新目标节点的嵌入向量，对目标节点与源节点对应的类别的权重进行累加            Z[dst, label_src] = Z[dst, label_src] + W[label_src] * edg_w  
        # 更新进度条        if show_prog:            steps += 1            prog = int(steps / total * 100)            if prog > prog_bar.progress:                prog_bar.progress = prog  
    # 返回节点嵌入矩阵Z和节点权重矩阵W    return Z, W
```

由于每个顶点仅有一个标签，因此同类顶点在权重矩阵W中的值相同，也就是说其实只需要针对每个标签存储其对应的权重即可。这里将权重矩阵W简化为一个K维向量，其每个元素代表了对应标签的权重。

此外，在计算权重时，由于我们实际的数据中会存在某个分类标签下没有顶点的情况，因此，在计算权重时进行了容错处理。这会导致最终Embedding的计算结果与原始算法存在细微差异，但理论上应该不影响最终的Embedding效果。

为验证改进后的算法的结果与原始算法一致，重新构造随机生成的测试数据，在不添加容错处理的情况下，验证改进后的算法与原始算法的结果是否完全一致。之后再添加容错处理，并做为后续改进的基准版本。

该版本算法在业务数据测试集上的计算耗时约为35秒，已经比较原始算法有了明显的性能提升。

**3.2****支持mini-batch的向量化计算版本**

接下来是对Embedding计算过程的改进，主要思路是利用向量化计算，减少不必要的循环。同时利用mini-batch的方式，减少内存的占用。

```
def graph_encode_embedding_batched(X, Y, n_K, batch_size=1024, show_prog=False):    """    compute the edge embedding matrix Z and node weight matrix W    向量化版本，支持mini-batch，依赖numpy和pandas  
    :param X: edge list, array of float, [[src, dst, weight], ...]    :param Y: node label, array of int, [node_label, ...]    :param n_K: number of classes    :return: Z, W    """    # 初始化权重矩阵W    W = np.zeros(n_K)    # 遍历每个类别    for k in range(n_K):        # 统计每个类别的节点数量        W[k] = (Y == k).sum()    # 计算每个类别的权重，即每个类别节点数量的倒数，为了避免除零错误，分母加1    W = 1 / (W + 1)    # 初始化节点嵌入矩阵Z，该矩阵的行数是节点的数量，列数是类别的数量，实际上是保存了每个节点与每个类别之间的相关性权重    Z = np.zeros((Y.shape[0], n_K))    # 记录总的边数    total = len(X)  
    # 初始化Jupyter进度条    if show_prog:        prog_bar = ProgressBar(100)        prog_bar.display()  
    # 向量化方式处理所有的边，每次处理batch_size条边    for batch_id in range(0, total, batch_size):        # 获取当前batch的边信息        batch = slice(batch_id, batch_id + batch_size)        src = X[batch, 0].astype(int)        dst = X[batch, 1].astype(int)        edge_w = X[batch, 2]        # 提取源节点和目标节点的标签，注意，这里的src和dst中保存的都是节点的索引，不是节点的标签        # 得到的src_label和dst_label是节点的标签，与src和dst一样都是以边索引为索引的数组        src_label = Y[src]        dst_label = Y[dst]  
        # 首先处理目标节点，筛选有标签的目标节点，注意，dst_valid是边的索引，不是节点的索引        dst_valid = np.where(dst_label >= 0)[0]        # 筛选出有效目标节点的标签        dst_label = dst_label[dst_valid]        # 筛选出有效目标节点的边权重        dst_edge_w = edge_w[dst_valid]        # 筛选出有效目标节点的源节点        dst_valid_src = src[dst_valid]        # 将有效目标节点的信息转换为DataFrame，并按照源节点和标签进行分组，计算每个源节点与每个标签的权重和        df = pd.DataFrame({"src": dst_valid_src, "label": dst_label, "weight": dst_edge_w * W[dst_label]})        df = df.groupby(["src", "label"], as_index=False).sum()        # 将有效目标节点的信息更新到节点嵌入矩阵Z中        Z[df["src"], df["label"]] += df["weight"]  
        # 然后处理源节点，筛选有标签且不是自环的源节点，过程与目标节点类似        src_valid = np.where((src_label >= 0) & (src != dst))[0]        src_label = src_label[src_valid]        src_edge_w = edge_w[src_valid]        src_valid_dst = dst[src_valid]        # 将有效源节点的信息转换为DataFrame，并按照目标节点和标签进行分组，计算每个目标节点与每个标签的权重和，更新到节点嵌入矩阵Z中        df = pd.DataFrame({"dst": src_valid_dst, "label": src_label, "weight": src_edge_w * W[src_label]})        df = df.groupby(["dst", "label"], as_index=False).sum()        Z[df["dst"], df["label"]] += df["weight"]  
        # 更新进度条        if show_prog:            prog = min(int((batch_id + batch_size) / total * 100), 100)            if prog > prog_bar.progress:                prog_bar.progress = prog  
    # 返回节点嵌入矩阵Z和节点权重矩阵W    return Z, W
```

该版本算法在业务数据测试集上的计算耗时约为6.3秒，相比原始算法有了接近数量级的性能提升。

不过这版的算法实现中，同时使用了numpy和pandas两个库，做为一个“强迫症患者”，还是尽量只依赖一个库来实现比较好。

**3.3 Pandas版本**

由于算法中需要进行分组求知，而numpy中没有提供可以直接使用的groupby功能，因此先尝使用pandas来实现。

```
def graph_encode_embedding_batched_pd(X, Y, n_K, batch_size=10240, show_prog=False):    """    compute the edge embedding matrix Z and node weight matrix W    向量化版本2，支持mini-batch，只依赖pandas，用于性能测试  
    :param X: edge list, array of float, [[src, dst, weight], ...]    :param Y: node label, array of int, [node_label, ...]    :param n_K: number of classes    :return: Z, W    """    # 初始化权重矩阵W    W = np.zeros(n_K)    # 遍历每个类别    for k in range(n_K):        # 统计每个类别的节点数量        W[k] = (Y == k).sum()    # 计算每个类别的权重，即每个类别节点数量的倒数，为了避免除零错误，分母加1    W = 1 / (W + 1)    # 初始化节点嵌入矩阵Z，该矩阵的行数是节点的数量，列数是类别的数量，实际上是保存了每个节点与每个类别之间的相关性权重    Z = np.zeros((Y.shape[0], n_K))    # 记录总的边数    total = len(X)  
    # 初始化Jupyter进度条    if show_prog:        prog_bar = ProgressBar(100)        prog_bar.display()  
    # 向量化方式处理所有的边，每次处理batch_size条边    for batch_id in range(0, total, batch_size):        # 获取当前batch的边信息        batch = slice(batch_id, batch_id + batch_size)        # 将边信息转换为DataFrame        df = pd.DataFrame(X[batch], columns=["src", "dst", "edge_w"])        df.astype({"src": int, "dst": int}, copy=False)        # 添加源节点和目标节点的标签        df["src_label"] = Y[df["src"]]        df["dst_label"] = Y[df["dst"]]  
        # 筛选有标签的目标节点        df_dst_valid = df[df.dst_label >= 0]        # 计算每个目标节点的权重        df_dst_valid["weight"] = df_dst_valid["edge_w"] * W[df_dst_valid["dst_label"]]        # 按照源节点和标签进行分组，计算每个源节点与每个标签的权重和        df_dst_valid = df_dst_valid.groupby(["src", "dst_label"], as_index=False).sum()        # 将有效目标节点的信息更新到节点嵌入矩阵Z中        Z[df_dst_valid["src"], df_dst_valid["dst_label"]] += df_dst_valid["weight"]  
        # 筛选有标签且不是自环的源节点        df_src_valid = df[df.src_label >= 0]        # 计算每个源节点的权重        df_src_valid["weight"] = df_src_valid["edge_w"] * W[df_src_valid["src_label"]]        # 按照目标节点和标签进行分组，计算每个目标节点与每个标签的权重和        df_src_valid = df_src_valid.groupby(["dst", "src_label"], as_index=False).sum()        # 将有效源节点的信息更新到节点嵌入矩阵Z中        Z[df_src_valid["dst"], df_src_valid["src_label"]] += df_src_valid["weight"]  
        # 更新进度条        if show_prog:            prog = min(int((batch_id + batch_size) / total * 100), 100)            if prog > prog_bar.progress:                prog_bar.progress = prog  
    # 返回节点嵌入矩阵Z和节点权重矩阵W    return Z, W
```

该版本算法在业务数据测试集上的计算耗时约为7.4秒，仍然很快，但......

**3.4 Numpy版本**

由于numpy中没有提供可以直接使用的groupby功能，需要基于numpy现在函数来自己实现相似的功能，在查找了相关资料，反覆盖阅读了numpy的手册，并多次尝试后，终于找到了在numpy中使用groupby的方法。

```
def group_sum(indexes, values):    """    sum values by index    根据索引求和, 相当于: values.groupby(indexes).sum()  
    :param indexes: array of int, [[index1, index2, ...], ...]    :param values: array of float, [value1, value2, ...]    :return: grp_indexes, grp_sums    """    if indexes.ndim == 1:        # 若索引只有一列，可以直接使用        reindex = indexes    else:        # 若索引有多个列，需要进行合并，生成一个新的唯一索引，这里假定索引中都是整数。        reindex = np.zeros(indexes.shape[0], dtype=indexes.dtype)        for axis in reversed(range(indexes.shape[-1])):            reindex = indexes[:, axis] * (reindex.max() + 1) + reindex    # 对索引和数据进行排序    order = np.argsort(reindex)    sorted_reindex = reindex[order]    sorted_indexes = indexes[order]    sorted_values = values[order]    # 对索引进行分组，生成组别索引，索引中的每个元素表示该组的第一个元素在原数组中的位置    _, grp_idx = np.unique(sorted_reindex, return_index=True)    # 对每个组的数据求和，这里的reduceat是实现GroupBy的核心，它会根据grp_idx中的位置索引，对sorted_values进行分段的reduce操作。    grp_sums = np.add.reduceat(sorted_values, grp_idx, axis=0)    # 对索引进行还原    grp_indexes = sorted_indexes[grp_idx]    # 返回组别索引和组和    return grp_indexes, grp_sums
```

有了这个函数，就可以实现纯numpy版本的改进算法了。

```
def graph_encode_embedding_batched_np(X, Y, n_K, batch_size=1024, show_prog=False):    """    compute the edge embedding matrix Z and node weight matrix W    向量化版本，支持mini-batch，只依赖numpy  
    :param X: edge list, array of float, [[src, dst, weight], ...]    :param Y: node label, array of int, [node_label, ...]    :param n_K: number of classes    :return: Z, W    """    # 初始化权重矩阵W    W = np.zeros(n_K)    # 遍历每个类别    for k in range(n_K):        # 统计每个类别的节点数量        W[k] = (Y == k).sum()    # 计算每个类别的权重，即每个类别节点数量的倒数，为了避免除零错误，分母加1    W = 1 / (W + 1)    # 初始化节点嵌入矩阵Z，该矩阵的行数是节点的数量，列数是类别的数量，实际上是保存了每个节点与每个类别之间的相关性权重    Z = np.zeros((Y.shape[0], n_K))    # 记录总的边数    total = len(X)  
    # 初始化Jupyter进度条    if show_prog:        prog_bar = ProgressBar(100)        prog_bar.display()  
    # 向量化方式处理所有的边，每次处理batch_size条边    for batch_id in range(0, total, batch_size):        # 获取当前batch的边信息        batch = slice(batch_id, batch_id + batch_size)        src = X[batch, 0].astype(int)        dst = X[batch, 1].astype(int)        edge_w = X[batch, 2]        # 提取源节点和目标节点的标签，注意，这里的src和dst中保存的都是节点的索引，不是节点的标签        # 得到的src_label和dst_label是节点的标签，与src和dst一样都是以边索引为索引的数组        src_label = Y[src]        dst_label = Y[dst]  
        # 首先处理目标节点，筛选有标签的目标节点，注意，dst_valid是边的索引，不是节点的索引        dst_valid = np.where(dst_label >= 0)[0]        # 筛选出有效目标节点的标签        dst_label = dst_label[dst_valid]        # 筛选出有效目标节点的边权重        dst_edge_w = edge_w[dst_valid]        # 筛选出有效目标节点的源节点        dst_valid_src = src[dst_valid]        # 源节点和标签进行分组，计算每个源节点与每个标签的权重和        dst_indexes = np.array([dst_valid_src, dst_label]).T        dst_weights = dst_edge_w * W[dst_label]        dst_grp_indexes, dst_grp_weights = group_sum(dst_indexes, dst_weights)        # 将有效目标节点的信息更新到节点嵌入矩阵Z中        Z[dst_grp_indexes[:, 0], dst_grp_indexes[:, 1]] += dst_grp_weights  
        # 然后处理源节点，筛选有标签且不是自环的源节点，过程与目标节点类似        src_valid = np.where((src_label >= 0) & (src != dst))[0]        src_label = src_label[src_valid]        src_edge_w = edge_w[src_valid]        src_valid_dst = dst[src_valid]        # 按照目标节点和标签进行分组，计算每个目标节点与每个标签的权重和，更新到节点嵌入矩阵Z中        src_indexes = np.array([src_valid_dst, src_label]).T        src_weights = src_edge_w * W[src_label]        src_grp_indexes, src_grp_weights = group_sum(src_indexes, src_weights)        Z[src_grp_indexes[:, 0], src_grp_indexes[:, 1]] += src_grp_weights  
        # 更新进度条        if show_prog:            prog = min(int((batch_id + batch_size) / total * 100), 100)            if prog > prog_bar.progress:                prog_bar.progress = prog  
    # 返回节点嵌入矩阵Z和节点权重矩阵W    return Z, W
```

该版本算法在业务数据测试集上的计算耗时约为4.1秒。

**3.5 算法改进小结**

|  |  |
| --- | --- |
| 算法版本 | 计算耗时(s) |
| 原始版本 | 55 |
| 稀疏矩阵改进版本（含数据转换） | 158 |
| 稀疏矩阵改进版本（不含数据转换） | 66 |
| 改进版本（简化权重矩阵） | 35 |
| 向量化版本（numpy + pandas） | 6.3 |
| 向量化版本（pandas） | 7.4 |
| 向量化版本（numpy） | 4.1 |

**3.6 效果验证**

对Embedding的结果抽样并通过TSNE进行可视化，结果如下：

![]()

## ****△散点图******△HexBin图**

从图中可以看到顶点呈现出明显的聚类特征，说明Embedding的结果是有意义的。但是在用于异常检测时的效果的效果是否能真的能够达到我们的预期，且听下回分解。

END

**推荐阅读**

[AIAPI - 转向AI原生检索](https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247603616&idx=1&sn=6f18533697c0a083f9c58373ac6b1a85&scene=21#wechat_redirect)

[学校新来了一位AI作文老师：能看、会评、还教改写](https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247603585&idx=1&sn=1ea31a1565c49bc466ddb99b6d9e63d9&scene=21#wechat_redirect)

[搞定十万卡集群！贫穷限制了我的想象力…](https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247603457&idx=1&sn=b3a0dcf00cb7a38bf62729c279619824&scene=21#wechat_redirect)

[AI Agent重塑微服务治理](https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247603314&idx=1&sn=f4b05cb723de72ef1d3209082c998b28&scene=21#wechat_redirect)

[百度智能云千帆大模型平台引领企业创新增长](https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247602972&idx=1&sn=e6830233635d7425d4bd08737dbf3569&scene=21#wechat_redirect)

![]()

一键三连，好运连连，bug不见👇