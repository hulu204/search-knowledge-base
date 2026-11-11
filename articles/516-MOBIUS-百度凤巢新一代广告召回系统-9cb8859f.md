---
title: 'MOBIUS：百度凤巢新一代广告召回系统'
company: 百度
tag: 召回
date: 2019-11-29
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247495618&idx=1&sn=42b06177dec45f33c29ab25d73b639a9&chksm=fbd75daecca0d4b8a6ae5c4854c40cc05bd6c7b67ac6ab45f74c05d425aafae9d54699a09c19&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPj1kmEQBolZz6jx1E9kkClS3mlXdRxj5NI5fiaDOhIp0TX04M5U8lVCmoOWuzu5o7dKrxGHhAU227g/640?wx_fmt=jpeg)

注：图片来自网络

文章作者：邱锡鹏 复旦大学 副教授

编辑整理：Hoh Xil

内容来源：知乎@邱锡鹏

出品社区：DataFun

注：欢迎转载，转载请注明出处

**导读：**近期，小编在知乎中关注到了一个有意思的话题 "NLP 任务中有哪些巧妙的idea？" ，目前已经有1188+关注，40000+浏览量，今天小编就为大家分享下获得最高点赞的答案，复旦大学邱锡鹏教授的回答：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPj1kmEQBolZz6jx1E9kkClSibkh3Uthk4ge8UT9mXboibmJDQeQcVNSalvVYqW6W7MSZU1gn5ib5qf5A/640?wx_fmt=png)

这个问题很有趣！看了下目前的回答都是深度学习之后的，我就回答几个深度学习之前的吧：

先从语义表示说起，个人觉得都是简单并且巧妙的想法 ( 但其背后的理论不一定简单 )。

**1. 分布式假设 ( Distributional Hypothesis )**

"Linguistic items with similar distributions have similar meanings." 

直白点就是，一个词的语义可以用它的上下文表示。

对 NLP 来说，个人觉得分布式假设是来自语言学的最有价值的 "理论" 之一。

**2. 词袋模型 ( Bag-of-Words )**

将一篇文档看作是一个词的集合，不考虑语法，甚至是词序信息也都抛弃了。

BoW 模型解决了用机器学习来做 NLP 的一个痛点问题：怎样把一个变成的文本序列转换为定长的向量。

相关扩展：N-gram，TF-IDF 等。

**3. 潜在语义分析 ( Latent Semantic Analysis )**

基于上面的分布式假设和词袋模型，我们可以构建一个词-文档矩阵 ( term-document matrix ) ![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPj1kmEQBolZz6jx1E9kkClSreWyOhHX0xRSpicBe3LLFOGj23IHUhnCR8QMiaJMic8RHCx4EvPHgj1iag/640?wx_fmt=png)。这个矩阵![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPj1kmEQBolZz6jx1E9kkClSreWyOhHX0xRSpicBe3LLFOGj23IHUhnCR8QMiaJMic8RHCx4EvPHgj1iag/640?wx_fmt=png)很有意思，每一列为一个文档的表示 ( BoW 向量 )，每一行为一个词的语义表示 ( 分布式假设，其中上下文是以文档为基本单位 )。这样我们就可以用 ![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPj1kmEQBolZz6jx1E9kkClSguT4uduz4rLK3MeRXwdk7PrwEiccdwanVavs0HEH1QPp658miaNey0cA/640?wx_fmt=png) 表示文档和文档之间的关系，用 ![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPj1kmEQBolZz6jx1E9kkClS8TyuQpBhTAGe2zzOtLQvXHIn4f4vQze9gxJZeOrVKnTTnPERQuKz0w/640?wx_fmt=png) 表示词与词之间的关系。这个矩阵还可以进行 SVD 分解，得到词和文档的稠密向量表示，可以发现潜在的语义信息 ( 比如主题等 )。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPj1kmEQBolZz6jx1E9kkClSprQhSxeZ7Ek6ZE7w2T89XM7ibibHPfbI57L7X8hKp38aZibCIcQWibmicsQ/640?wx_fmt=jpeg)

**4. 概率主题模型 ( Probabilistic Topic Models )**

概率主题模型比词袋模型多引入了一个 "主题 ( Topic )" 作为隐变量。词和文档的之间关联变成了：文档 -> 主题 -> 词。这个想法合情合理，听上去就更好。如果你觉得哪里不好，又可以魔改。概率主题模型的数学基础 ( 概率有向图模型 ) 十分漂亮，并且基于吉布斯采样的推断简单到不可思议，甚至不需要图模型的知识就可以理解。PTM 是前深度学习时代 NLP 领域的一个大宝矿 ( Shui Keng )！

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPj1kmEQBolZz6jx1E9kkClSFPicCM9YiaOheNkm1kLO7buacyJeqCibKQCCb1RiahmmwFDe4Pfbkjp70A/640?wx_fmt=jpeg)

**5. 基于 BMES 的中文分词或基于 BIO 的 NER/Chunking**

BMES 是 Begin/Middle/End/Single 的缩写，代表所标记的字符是一个词语的开始/中间/结尾/单字词。

BIO 是 Begin/Inside/Outside 的缩写，表示所标记的词是一个实体名的开始/内部/外部。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPj1kmEQBolZz6jx1E9kkClSYBV3DJN5HvBzX5CbOGOFu7TyL6HHNYlpMs4OdURSH3MibJiaDUKibmy1g/640?wx_fmt=jpeg)

这种标记将带有分割性质的 NLP 任务转换为序列标注任务，可以使用 HMM、CRF 等成熟的机器学习模型。

**6. 基于 PageRank 的 TextRank**

PageRank 本身非常巧妙了，TextRank 更是巧妙地将 PageRank 应用到 NLP 中的词排序或句子排序上面，比如关键词抽取、文本摘要等。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPj1kmEQBolZz6jx1E9kkClS1iciaE6EXpQqKHKTpdogMC7vUwH8loCQ3kwSK7eTVcvpBK7jEYfjpFicw/640?wx_fmt=jpeg)

**参考资料：**

1. "Linguistic items with similar distributions have similar meanings." 

https://en.wikipedia.org/wiki/Distributional\_semantics

2. term-document matrix

https://en.wikipedia.org/wiki/Term-document\_matrix

**原文链接：**

https://www.zhihu.com/question/356132676/answer/901244271

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhYUUTnAicmDgz064WIYEsbXHSGbTibHibFbx9W2nOrUDAFsNvia7o6XicyicpwY5w2Q2IrgTd2jstd5mPg/640?wx_fmt=png)

**分享嘉宾**

******▬******

邱锡鹏，复旦大学计算机科学技术学院 副教授，博士生导师，于复旦大学获得理学学士和博士学位。中国中文信息学会青年工作委员会执委、计算语言学专委会委员、中国人工智能学会青年工作委员会常务委员、自然语言理解专委会委员。主要研究领域包括人工智能、机器学习、深度学习、自然语言处理等，并且在上述领域的顶级期刊、会议（ACL/EMNLP/IJCAI/AAAI等）上发表过50余篇论文。自然语言处理开源工具FudanNLP作者，2015年入选首届中国科协青年人才托举工程，2017年ACL杰出论文奖。

**——END——**

**文章推荐：**

[自然语言处理中的多任务学习](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247486994&idx=1&sn=cc5868a3af3aba562463f74c2bcf8b3a&chksm=fbd4bc7ecca3356889bd45484f25f41c2dbaf2015eacb2cf12f0a684f94b2168b47c8928bd47&scene=21#wechat_redirect)

[阿里妈妈：品牌广告中的 NLP 算法实践](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247494094&idx=1&sn=4c32130746752039fba45a5ba6b7eedb&chksm=fbd75ba2cca0d2b45533b2464418873e366f1e733a5b92d8ad1a754d2390334e5443f8fa60b3&scene=21#wechat_redirect)

[深度学习在360搜索广告 NLP 任务中的应用](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247492151&idx=1&sn=e6e284f3dce6679eb5db088d05cef1d3&chksm=fbd7505bcca0d94d8d9db8743d4313c46d7cd3628db65b58daf3dfe90c6a467c5b8b86f998b8&scene=21#wechat_redirect)

********![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhOag2cOj19rzTkY9vMfpqr3icOsB3QwMMDMuEVibfcEovy0icyHuASlHbCicK9SJK1M9tsP1hZUmBBRA/640?wx_fmt=png)********

**DataFun：**

专注于大数据、人工智能领域的知识分享平台。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhicE4hS5liayK0vWlwTanNgy003rMCMPvRlktwUjR2m8icG0MbH1ByNF7RuLdibwXKsA424lHOvaIHWw/640?wx_fmt=png)

**一个「在看」，一段时光！****👇**