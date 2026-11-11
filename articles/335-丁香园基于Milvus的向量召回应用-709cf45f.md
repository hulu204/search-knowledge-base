---
title: '丁香园基于Milvus的向量召回应用'
company: 丁香园
tag: 召回
date: 2021-07-02
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247544207&idx=2&sn=4adac4d8c43122374905f236634e2b0e&chksm=fbd79fe3cca016f5f2896aa33cebd1442569f73aa8c807d4c0a0ac8753898e42fa736552bf1d&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
### 背景

随着BERT，GNN等模型在NLP领域的发展，DNN类模型的语义提取能力又得到进一步提升，我们对文本语义向量也有了更高的期待，期望语义向量或其他模型特征向量可以在召回段发挥更大作用；约2019年初，我们就尝试在推荐业务中引入基于Faiss的向量召回，随后很快意识到，作为一个基础库，Faiss固然可以快速部署，但缺乏分布式方案，数据持久管理等问题令其无法应付大数据场景；Milvus很好的弥补了Faiss的不足，具体来说：分布式解决方案、数据持久化管理、丰富的SDK这些优势都是其他ANN库无法比拟的，另外Milvus的社区很活跃，意味着用户遇到的问题能很快被解决；因此在2020年，丁香园算法组选择Milvus作为向量索引组件，并首先用于社区论坛搜索场景。

### 

### 召回流程

搜索召回通常基于Solr/ES这类组件，核心是基于概率检索模型，通常是BM25算法的分词召回；对丁香园的社区搜索场景而言，用于需求的内容不仅包含专业知识，还有考试求职和新闻热点等内容需求，因此query往往描述模糊，中心点不明确；利用BM25不得不接受分词的损失，还需要维护优质的业务相关词典，同时还需要识别关键词的算法辅助；简言之，BM25很难应对模糊和复杂语义表达，因此我们尝试通过不同的文本向量化模型改善对关键词和语义的召回结果

![](https://mmbiz.qpic.cn/mmbiz_png/ATU4OuicVx29juNibxSQ000b8OoyXrMlpjwcIrfB12jDk3VpRAgph3S1UB2pRiab7MvUalhaTLibiaWv4UJMmczW66A/640?wx_fmt=png)

### 

### 向量模型

#### Bi-Encoder[1]

BERT是典型的Cross-Encoder模型，通过12层Multi-Head Attention捕捉全局信息，单句BERT的Bi-Encoder结构会有不小性能损失，但向量召回模型只能选择Bi-Encoder类的结构，将候选文档提前向量化存储，线上服务只计算query的向量

![](https://mmbiz.qpic.cn/mmbiz_png/ATU4OuicVx29juNibxSQ000b8OoyXrMlpjcHFCnqVibeOibHRE6sYiaZsdX3pnys9CmDcZZP2rtTay7vibHCwxl6Cs4w/640?wx_fmt=png)

损失函数的选择和负采样策略显得尤为重要；这里我们也选择triplet loss，将负样本分为easy，middle，hard三部分，按2:2:1构造训练数据集

![](https://mmbiz.qpic.cn/mmbiz_png/ATU4OuicVx29juNibxSQ000b8OoyXrMlpjDCqwZOZicEgB5DyH5PG02IG8H97beicd0t8mIsTZvnGibPG4pJsialUP0g/640?wx_fmt=png)

#### 

#### Spherical Embedding[2]

论坛中话题的分布是很不均衡的，包含专业关键词的内容往往不如话题性内容多，所以很难只靠BERT捕捉到这些关键词的语义；我们首先想到word2vec类模型，这篇Spherical Text Embedding可以同时学习文档向量和词向量，实测中对关键词与文档的捕捉效果也不错

传统的word2vec只关注了中心词和周围词的语义关系，忽视了与整篇文章的关系，实际上文章中最先产生的往往中心词/主题词，然后才产生周围词，因此作者提出词向量的生成过程，基于doc向量，先生成中心词向量tgt，再产生周围词向量src；具体的，生成中心词tgt时可以将文档向量doc视作分布空间的均值向量，同理生成src时tgt就是均值向量

![](https://mmbiz.qpic.cn/mmbiz_png/ATU4OuicVx29juNibxSQ000b8OoyXrMlpjicFBXLTrUzXiaTS1CEFNCCQegbUvBV1GlmnGzNfmlTqCrzllIKAzxWCQ/640?wx_fmt=png)

需要指出，这里的三类向量doc，tgt，src都属于von Mises-Fisher(vMF)分布，所以概率密度函数的具体形式，用于计算基于doc的联合概率分布

![](https://mmbiz.qpic.cn/mmbiz_png/ATU4OuicVx29juNibxSQ000b8OoyXrMlpjtQuJtTPxZicw3mLGiaIjhGuk2gq9IrulJnS6zcONL2J2l0Heics81Zrow/640?wx_fmt=png)

具体的训练思路与word2vec类似，通过max-margin loss最大化正负样本的距离

![](https://mmbiz.qpic.cn/mmbiz_png/ATU4OuicVx29juNibxSQ000b8OoyXrMlpjGxgA2hmDVQwXz4DCjTicraoYkYOYPXusy8EHgwoQhnbzzrohjWwAxPw/640?wx_fmt=png)

#### Knowledge Embedding[3]

更直接的关键词向量化方法是利用现有的图谱结构，通过TranE这样的实体关系表示模型，或者node2vec这类邻接图表示模型直接得到关键词向量，这里以ProNE为例；在之前有关GNN的文章中也介绍过，ProNE整体可分为两部分，第一部分对无向图结构的邻接矩阵做稀疏矩阵分解。作者定义了如下损失函数最大化节点 r 和邻居 c 的共现频率p，同时最小化负采样邻居概率：

![](https://mmbiz.qpic.cn/mmbiz_png/ATU4OuicVx29juNibxSQ000b8OoyXrMlpjjo1jkunLvicibQiaTPChyLcfdMK5cL5xE89cYpTZfq8UhDfavThnFO84Q/640?wx_fmt=png)

最小化loss的充分条件是loss对 r*{i}{T} c*{j} 的偏导数为0，可得节点 r 和邻居 c 的的距离公式并构造距离矩阵

![](https://mmbiz.qpic.cn/mmbiz_png/ATU4OuicVx29juNibxSQ000b8OoyXrMlpjFDn5peRwdxwGJvTeBztjtGyWlBvRQoF34ibaInRmYxoVvoV8P3Rgflg/640?wx_fmt=png)

对距离矩阵 M 做tSVD(truncated Singular Value Decomposition)并取最后top-d的奇异值和对应向量作为这一部分的节点embedding表示，为了效率用randomized tSVD加速运算。第二部分借鉴GCN中spectrum方法的思路设计了传播策略(propagation strategy)，目的是获取图结构中的局部平滑(localized smoothing)信息和全局聚类(global clustering)信息；具体来说，根据图分割理论，子图的聚合度越高表明对图的划分越好，可以用常量值k表示，高阶Cheeger不等式将常量k与邻接图的特征值关联了起来

![](https://mmbiz.qpic.cn/mmbiz_png/ATU4OuicVx29juNibxSQ000b8OoyXrMlpjwcOG1mANkibjW9UEasU4EyhDh1lF48IjrPRVQ6upMGkm1WTOFic8nxLA/640?wx_fmt=png)

上式表明Cheeger 常量对应着特征值的上下界，更小的常量对应更小的特征值，也对应着更内聚(clustering)的子图，反之对应更大的特征值，此时图结构中的子图更为平滑(smoothing)；于是，作者设计了一个函数 g(\lambda) 用于控制特征值的取值范围，再参照GCN中利用切比雪夫多项式近似计算下面的 \widetilde{L} ，整个过程可以看作限制特征值范围的GCN，最后为保证正交性，还需要对Embedding结果做一次SVD。

![](https://mmbiz.qpic.cn/mmbiz_png/ATU4OuicVx29juNibxSQ000b8OoyXrMlpjmZctYHu0L4icd4mXB2RiaNITXhADXoLjpfzXyhVlDISpVbNSuKsHAGnQ/640?wx_fmt=png)

### 总结

本文简单梳理了丁香园在搜索场景中关于向量召回方向的思考和尝试，通过不同类型的向量表示模型逐步处理现实场景中复杂的语义表达，基于Milvus的向量召回引擎有良好的性能和成熟的落地方案，让我们可以把精力完全集中在表示模型的调试上；此外，我们在其他场景中也会灵活应用Milvus，例如将长文本转化为二值向量，通过汉明距离计算查询字面相近的内容，Milvus全面的SDK支持使得这些功能可以在不同团队不同业务线内快速部署上线。目前向量召回引擎在NLP和推荐领域的应用都已逐渐成为趋势，Milvus可靠的性能保证和丰富的落地技术支持极大的提高了我们的开发和部署效率，目前我们也积极在其他业务场景中引入向量表示模型，期待基于Milvus的应用能在更多业务线中发挥优势。

——本文转自丁香园大数据

#### 参考文献

1. https://arxiv.org/pdf/2006.11632.pdf
2. https://arxiv.org/pdf/1911.01196.pdf
3. https://www.ijcai.org/proceedings/2019/0594.pdf

**今天的分享就到这里，谢谢大家。**

---

在文末分享、点赞、在看，给个3连击呗~

---

**峰会推荐：**

想**了解更多语义表示与计算**落地案例吗？7月10日，DataFun将举办自然语言处理峰会，届时将邀请来自百度、阿里、腾讯、字节跳动、华为、美团、小米、MSRA、新浪微博等公司的资深专家进行会进行多场语义相关的深度分享，欢迎小伙伴们识别二维码，了解详情，并报名参与，本次峰会将全程直播！

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaG9NhwaIfZzml9g1jekkcr0w4M21n1ZcnoEpMoBa6ekjuicM7f9bDmkoTZeH9WVZS6dJYtqTCcpEg/640?wx_fmt=png)

**社群推荐：**

欢迎加入 **DataFunTalk NLP**交流群，跟同行零距离交流。**识别二维码**，添加小助手微信，**入群。**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPiaLYH3TP0Kib1vRrTlcSUTsbgFgr7MP646C7RoQGIz2Xk3euujTLm6UcGt4rHDJMaZaT7FxDm75ibQA/640?wx_fmt=jpeg)

**关于我们：**

**DataFunTalk**专注于大数据、人工智能技术应用的分享与交流。发起于2017年，在北京、上海、深圳、杭州等城市举办超过100+线下和100+线上沙龙、论坛及峰会，已邀请近1000位专家和学者参与分享。其公众号 DataFunTalk 累计生产原创文章400+，百万+阅读，10万+精准粉丝。

🧐**分享、点赞、在看**，给个**3连击**呗！**👇**