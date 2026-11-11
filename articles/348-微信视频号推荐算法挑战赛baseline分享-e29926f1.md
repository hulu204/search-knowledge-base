---
title: '微信视频号推荐算法挑战赛baseline分享'
company: 腾讯微信
tag: 推荐
date: 2021-05-23
url: http://mp.weixin.qq.com/s?__biz=MjM5MzY4NzE3MA==&mid=2247494303&idx=1&sn=b1d8d66bd590e66158b5ce745f2dc6ea&chksm=a691997291e610645cd6962a33c83945ddbc42a1630ac48bbef53bad9f22239a6db81a20a7cd&scene=27#wechat_redirect
account: 浅梦学习笔记
origin: readme
---
## 赛题描述-微信视频号推荐算法

本次比赛基于脱敏和采样后的数据信息，对于给定的一定数量到访过微信视频号“热门推荐”的用户， 根据这些用户在视频号内的历史n天的行为数据，通过算法在测试集上预测出这些用户对于不同视频内容的互动行为（包括点赞、点击头像、收藏、转发等）的发生概率。本次比赛以多个行为预测结果的加权uAUC值进行评分

比赛官网：2021中国高校计算机大赛 微信大数据挑战赛 (https://algo.weixin.qq.com/)

## 方案说明

本方案为基于DeepCTR(https://github.com/shenweichen/DeepCTR)实现的多任务学习模型MMOE(https://dl.acm.org/doi/10.1145/3219819.3220007)

完整代码地址(https://github.com/zanshuxun/WeChat\_Big\_Data\_Challenge\_DeepCTR\_baseline),点击文末阅读原文可直接访问。

* 特征：本方案关注于模型，仅使用以下6个较为基础的原始特征：['userid', 'feedid', 'authorid', 'bgm\_song\_id', 'bgm\_singer\_id', 'videoplayseconds']
* 线上结果：

  | 得分 | 查看评论 | 点赞 | 点击头像 | 转发 |
  | --- | --- | --- | --- | --- |
  | 0.633475 | 0.612465 | 0.613346 | 0.700479 | 0.643898 |

## 运行环境

python 3.6 deepctr==0.8.5
tensorflow-gpu(tensorflow)
pandas
scikit-learn

### deepctr安装说明

* CPU版本

  ```
  $ pip install deepctr==0.8.5
  ```
* GPU版本
  先确保已经在本地安装`tensorflow-gpu`,版本为 **「`tensorflow-gpu>=1.4.0,!=1.7.*,!=1.8.*`」**，然后运行命令

  ```
  $ pip install deepctr==0.8.5 --no-deps
  ```

## 运行说明

1. 新建data目录，下载比赛数据集，放在data目录下并解压，得到wechat\_algo\_data1目录
2. ```
   python run_mmoe.py
   ```

## 运行时间

在Tesla P40 24G GPU、E5-2650 v4 CPU机器上，训练时间为205s/epoch（6708846条样本）。

训练时显存占用为695MiB，内存占用为2.2G。

预测时间如下：

```
4个目标行为421985条样本预测耗时（毫秒）：352.331  
4个目标行为2000条样本平均预测耗时（毫秒）：1.670
```

## 关于DeepCTR

DeepCTR(https://github.com/shenweichen/DeepCTR)是一个易用、可扩展的深度学习点击率预测算法包，基于tensorflow深度学习框架。

添加**「特征」**时，仅添加feature\_columns即可，无需改动模型；

在**「模型」**方面，DeepCTR包含20多个CTR模型（如DeepFM、xDeepFM、DCN、AutoInt、DIN、FiBiNET等），可直接通过模型名调用。如需**「自定义模型」**，DeepCTR中也有很多高复用性的模型（例如DNN、FM、BiInteractionPooling、CIN、CrossNet等）。更多使用方法请参考DeepCTR文档(http://deepctr-doc.readthedocs.io/)。

DeepCTR也有pytorch版本：DeepCTR-Torch: https://github.com/shenweichen/DeepCTR-Torch

## 其他

楼主之前做比赛，从很多前辈的分享或开源中学到了很多，现在希望自己也能贡献一些。希望本文可以帮助大家降低深度学习CTR模型的门槛，普及这些算法技术。

预祝大家在本次大赛中取得好成绩！

## 推荐阅读

* [多任务学习在推荐算法中的应用](https://mp.weixin.qq.com/s?__biz=MjM5MzY4NzE3MA==&mid=2247492235&idx=1&sn=aed98d01c21ff7666c2fa4cee3779622&scene=21#wechat_redirect)
* [多目标推荐场景下的深度学习实践](https://mp.weixin.qq.com/s?__biz=MjM5MzY4NzE3MA==&mid=2247490966&idx=1&sn=79140d6160c6dcf77a3b42c936476af1&scene=21#wechat_redirect)
* [DCN-M：Google提出改进版DCN，用于大规模排序系统的特征交叉学习(附代码)](https://mp.weixin.qq.com/s?__biz=MjM5MzY4NzE3MA==&mid=2247487085&idx=1&sn=793c7b0a44d726ebc4e8258f1edf0efc&scene=21#wechat_redirect)
* [阿里定向广告智能投放技术体系](https://mp.weixin.qq.com/s?__biz=MjM5MzY4NzE3MA==&mid=2247494148&idx=1&sn=c1ed4c65e403b5a4a7663f4b94abd732&scene=21#wechat_redirect)

想了解更多关于**推荐系统**的内容，欢迎扫码关注公众号**浅梦的学习笔记**。回复**加群**可以加入我们的交流群一起学习！

****码字很辛苦，有收获的话就请********分享********、********点赞********、********在看********三连吧****👇****