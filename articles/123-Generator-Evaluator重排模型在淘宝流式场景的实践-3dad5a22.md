---
title: 'Generator-Evaluator重排模型在淘宝流式场景的实践'
company: 阿里淘系
tag: 重排
date: 2023-06-09
url: https://mp.weixin.qq.com/s/YoQNDdsRE6LZWJXrRKubLw
account: 大淘宝技术
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_gif/33P2FdAnju8wR6tAicOeT6zeXrYH5MAzz2tSeQeje01Wib7IrWTbaIDF3I7NiaH4wV9FNQqiaQTiawcriaQtZjF3pAbg/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

除了相关性，复杂信息流推荐场景还需要兼顾多样的业务需求，包括打散（多样性），流量调控，多展示形态/多路供给融合等。传统推荐系统采用pipeline的形式，分步处理上述需求，缺少统筹优化，这些模块之间常出现矛盾与覆盖，限制场景推荐效果。我们提出全新的基于Generator-Evaluator（GE）架构的重排模型，它不仅能够突破传统相关性贪心排序的范式，以序列整体效果为目标生成序列，还能突破pipeline的推荐范式，在一个模型中有机融合复杂业务规则，给出end2end联合最优解。我们在淘宝信息流场景验证了提案的有效性，并全量上线。

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9ktXcOebovS1SbeNE5Nc6ROCUABskFSIhpDnV6snAu0BaEwUuywlUnf5dkQLtKUpwOmg9WlYwOWw/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

引言

#### 

#### **▐**信息流场景面临的复杂挑战

﻿

复杂信息流可能包含不同类型、展示样式丰富的供给：文字、图片、视频、货架等，需要用一个统一的模型给不同类型的内容做排序。我们将业务需求总结为四大类：流量控制、多样性、组间排序以及定坑插入。纷繁复杂的业务需求可以拆解为这四个问题或者他们的组合。传统推荐系统往往需要构建pipeline，分步应对上述挑战。pipeline缺少统筹优化，时常会出现需求逻辑冲突与相互覆盖，无法获得联合最优解。

重排模型在淘宝不断发展，经历了3版迭代：V1版基于context特征增强的DNN-based判别式模型（贪心排序）[1]、V2版基于seq2seq结构的pointer-network生成式模型（贪心排序）[2]、V3版基于generator+evaluator架构的模型（生成式模型+判别式模型有机融合，考虑序列整体最优，非贪心排序）。这3版重排模型在淘宝不同的业务场景均拿到了明显的业务效果。今天我们聚焦于信息流场景，介绍如何利用V3版重排模型，突破pipeline的推荐范式，将四大类业务需求融入模型，给出end2end联合最优解。在淘宝信息流场景上，新模型实现了相关性与业务指标双增长，最终全量上线。

#### **▐**GE架构介绍

#### 

V3版模型由generator+evaluator两部分组成，在强化学习中generator也可以称为actor(agent)，evaluator也可以称为simulator。在我们的实现中，generator是基于pointer network的seq2seq生成式模型，它负责基于一个输入序，端到端地输出一个新的重排序。

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKdnLTVAgkTuxXxK1tj6OAVdNtuRNTia5EHGS0vPOkjEdFrML6icyDcWDg/640?wx_fmt=png)

EG架构的重排模型相比于监督学习的重排模型的一个优势是，generator不需要使用监督学习的方式训练，人为指定一个“最优序”作为label供模型学习，generator不需要学习生成我们人为给定的排序结果，因为人为给定的结果肯定是次优的。如果有一个evaluator模型能够近乎模拟线上用户的真实反馈，那么generator通过强化学习的方式，对着这个evaluator模型给出的反馈去训练是更合理的，不断尝试最大化获得的reward。如果数据中有一些非贪心排序范式的排序结果能够获得更好的线上指标，generator也会趋向生成这种模式的排序结果，从而突破贪心排序的范式，生成一些创造性的排序。

﻿

因此generator模型是通过探索/采样的方式，在训练初期，先尝试生成一些（不一定那么好的）序列，然后假设evaluator能够评估序列好坏，它能够给出用户对各种序列的反馈的估计，因此这个evaluator的打分就相当于对generator生成出的序列的reward。如果reward是正的，generator就调大生成这个序列的联合概率，相反，如果收到的reward是负的，generator就降低生成这个序列的联合概率。generator的训练目标是要使自己产生的序列能够最大化获得的evaluator给出的reward，所以是一个面向reward最终效果优化而不是面向模仿监督信号的模型，相当于一个强化学习框架。我们的generator就相当于agent，evaluator相当于真实环境的模拟器，generator通过不断探索试错，（基于模型参数）自主尝试各种action，并基于收到的reward不断调整自己的行为（调整模型参数），期望能够最大化获得evaluator反馈的reward。所以一开始generator可能都是生成一些随机的序列，随着训练的进行，generator会逐渐懂得生成一些能够最大化reward的序列，如果这个来自evaluator的reward与线上用户的真实反馈是相对保持一致的，那reward变大也就意味着线上效果会获得提升。

EG架构的重排模型，还有一个优势是能够方便地实现店铺打散、曝光宽度、曝光占比控制等业务目标，因为常用的贪心排序范式的模型，模型在打分的过程是不知道最终曝光的序列是怎样的，因此没办法端到端控制商家连续重复、某些类型曝光占比不足等问题，只能在按照模型分排序后做后处理。而EG架构这种生成式重排，generator模型在打分的过程中是直接生成最终排序的，因此在生成的过程中能够感知到生成的序列中商家是否重复、某些类型的曝光占比是否不足等问题。

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9ktXcOebovS1SbeNE5Nc6RVPNickIRicCdiaQ2bxameAK3wOHnQ93hVCqPO1FtrQiaBNSfhN2xp8tFoA/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

问题设定与符号定义

在全文中，一些表述比如：“商品/item”都可以理解为一个意思，表示推荐的一个独立载体；“序列/列表/排列”表示推荐系统中一页返回的多个商品构成的有序的推荐结果。

给定一个包含M个候选商品的集合![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKh8m9RIXbaMvH5iakbTJFgnWV7AfCVkliaeRXty0TWNfKjMqpF5lNJ9lQ/640?wx_fmt=png)，一个用户![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKkibxbTdun5U9OgPzL76kxlP7KbSFIMkSyKibhEibeZSXy2ic4n63tcVwLg/640?wx_fmt=png)，还有一个商品序列奖励函数![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKBC2OUcpwWVPdX3DpFh88kAPhwXEoNSLqNpDkF99NJwvBtlMzAWR6JQ/640?wx_fmt=png)，由偏好权重w加权求和而得，重排的目标是要找到最优的序列![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKB8s73nVic1QnNWYdibDics70PyJiakxjziclwf9VWs8evUSVqibANeDhJOcQ/640?wx_fmt=png)，使得生成的序列能够最大化获得的reward：

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKKQoaypP8xlvEtsz5LAA6Lo7ZHeHoWQKLYl7fT08hTOvsh7s2FEAicXQ/640?wx_fmt=png)

其中生成的每个序列长度为N，并且![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aK7W3DDD58E9Z7jJ7zsN83b2MROcQygtUbkHcSJxAYOQTauamiaVYs1pg/640?wx_fmt=png)。在本文中，我们假设奖励函数![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKDNLUdicItgDYFHMGGMy1xxZs5zG5v1O3lqc2eFqVoMPceKg29s2MxyQ/640?wx_fmt=png)为线性：

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKuq8dQVFjRqLJx8dWOOKOJIRyUicaFF0HMRGicuEaQ0AboicJ9gtIe7yUQ/640?wx_fmt=png)

其中U表示效用函数，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABafe4uOJfH52ZnnnoZccibq6ljB4jD9y5yp1DSicnIeupxxplbp6AKM2PGQ/640?wx_fmt=png)是我们关心的效用函数个数。因为w表示每个效用函数的相对重要性，它也被称为偏好权重。![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABafE4ZFWicfKJ0BC5icmianKXyDJicpvzVpkCbMY9MfWfgE0q6kHKdQ71xlJA/640?wx_fmt=png)通过一套人为设定的w计算而得，然后重排模型用参数表示，经过训练得到近似的指定w下的![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABaffxLbxiclM03MrW3ZaicHNmjjfxe6TtibUDNQ5iajwwb3OoKBNGL9wq8mIg/640?wx_fmt=png)到![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABaffQvKSjz9YYUuPibKqbvPQgp72ziaJrhAXs45ottMHRKn27zdHoM0AgXQ/640?wx_fmt=png)的映射。

我们表示每个用户u为一个embedding向量![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABaf7ze8zwB6bibibAIP4rKIib880hHCkabf5aPyhXfpbgjCgCGLibAM8YjeoA/640?wx_fmt=png)，同样地，一个候选商品被表示为一个特征向量![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABafh6J7GQicmFMh3Z1VUpuJtGpuHx4JsJQtPhwuRIfz4M01HPeRWDXUrrg/640?wx_fmt=png)。一个候选集合被表示为M个embedding的集合![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABafYFH9iajWFqCib5U8NawxJm6Q5icAouYRbVAic8odvL8O7LWfjOgSesFP9Q/640?wx_fmt=png)，重排模型选出的长度为N的商品序列可以被表示为一个矩阵![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABafrNjNRsJvyJb1Cibuvowic4NrlcPdKwiagnexOMRuSdYlx8iaydHrP0yVnQ/640?wx_fmt=png)，也就是N个商品embedding的堆叠![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABafspVb870Y2q2YS9hkOA2xfrlRLBpRphhU4PVzUVEfaM3h7yaricZWjibA/640?wx_fmt=png)

。

用户-商品的交互行为可以用向量![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABafDicm6f6GSdcGXaTcwDY3RicneKGyeGDsjFxd91ptErTtR5UIk7XYsKMQ/640?wx_fmt=png)表示，其中交互行为向量![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABaf2Up59zpA3ax3AauDO0T4eWx3QPUHs4lRGY4sve0jWlv17Tyc7ePLVg/640?wx_fmt=png)中的每一个元素可以是：曝光、点击、购买、视频观看时长等等，取决于特定的应用场景。而用户-商品序列的交互行为可以被表示为矩阵![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABaf43TDYfOA1TVHsvQNcZ1u8gxzcicDhmmLhvHyrEgRNKooaJksYk8OHbg/640?wx_fmt=png)。注意，我们没有所有M个候选商品的交互行为，因为只有其中的N个候选商品会在最终的推荐列表中，其余的商品用户不会看到。

每个用户-商品序列的交互行为会被记录成一条离线日志样本，一条样本也就是一个元组![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABafk6I9Nia9picNqGibmGX5KdU832ibGiaQSIF5DzgY7BpiavAYGzATmfKruACw/640?wx_fmt=png)。日志数据集![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABafOUc8YicVic6PYicY7VdYSEN1v9zAicicODmOrTFWpSZGwqFpNVic8zvyn6icg/640?wx_fmt=png)为![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABafVVT9KBD4Z445qkHuOovd6Su6W8gkUEGXHkoEBklRuAXIXOnFccx6sA/640?wx_fmt=png)，其中![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABafmJ9jT7qP040XAVbpv6pvkfItS6YibFB6nf0AHsiah5KgibgIyyCMbAic3g/640?wx_fmt=png)是记录下来的用户-商品序列的交互行为的数目。

一个效用函数是![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABafnYS5Yhgncg1B3DVicZS4BsPJO1jIpMzsx9053xiaBPiaBGBftiaa9phppw/640?wx_fmt=png)到一个实数的映射，即：![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABafy8nPWUg13IiayVsx4luOQPeXE5iaxjPQwkF5eyef4nticauibU7cf6t6Jw/640?wx_fmt=png)。其中实数![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABaf4IasvHbELKr7TULbO1Vce3rQhTn480n2sk9HstqpK403Kuhp7tpXXA/640?wx_fmt=png)分别表示对应的embedding维度。

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9ktXcOebovS1SbeNE5Nc6RIOKKwicFicPcOvvalDPb2yXHR6MlMfMjmcAeMbYsJuIUz6DsibHFeMsXg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

Generator

generator是一个encoder-decoder结构的模型，它的主要作用是从M个候选item中生成出长度为N的序列，其框架图如下所示。encoder负责对输入序进行编码，得到每个商品编码后的embedding，以及输入序整体的embedding，decoder会将输入序整体的embedding作为初始state，使用rnn一步一步地生成出最终的排序结果。

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKBYIlpmIQWMgZEq8BItaoaEibfff6KZRhtDR53f1c7l3BBVibnTfrR8HA/640?wx_fmt=png)

#### **▐**Encoder

在把候选商品集合输入给encoder之前，首先需要进行特征增强和embedding lookup的操作。一个商品的增强特征来源于候选集合，比如商品的历史点击率在整个候选集合中的排名。这是一个非常有效且简单的方式，告诉模型每个商品与它所在的候选集合之间的关系。然后ID特征会被转成实值embedding以方便数值计算。

﻿

Encoder是DeepSet的结构，因为它对输入商品的顺序不敏感，其结构图如下所示。DeepSet对于复杂的应用场景可能是更合适的encoder结构，因为要想找到一个好的混合了文本、图片、视频的初始输入序列是不容易的，差的初始输入序可能会伤害重排模型的效果。使用DeepSet不需要指定一个初始输入序，因为![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKn9uWbzkE5gfsjQF5DSbxdpackGWfPlEeosf4VAaBONn6d933CDxrLg/640?wx_fmt=png)已经包含了重排模型为了生成一个好的序列需要知道的所有信息。DeepSet定理描述了序不敏感函数，推导出了深度模型中排列不变性的充要条件，其模型结构入下图所示：

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKSDSypibd00pJUcwe4aDCezZvRvC8fR6zaHLkNFPu0SbW3ycOBMpHOPQ/640?wx_fmt=png)

#### **▐**Decoder

Decoder是基于Pointer Network的结构，其结构图如下所示。它每次会从候选集合中选择一个商品，然后立即更新上下文信息，然后选择下一个商品。

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKbyFxuoeItFxeEOYD407sOGLH4eVtrngVBUibF7exBQRgLpEY8ECF21A/640?wx_fmt=png)

对计算出的attention概率分布会采用Masking机制，主要有两点原因。首先，一个在前序步骤中已经被选出的商品不应该再被选择了，所以已被选出的商品的attention值需要被mask成0。其次，业务规则可能会要求模型在结果列表中的一些特定位置放一些特定的商品。因为一个顾客可能是通过点击一个trigger商品来到当前推荐场景的，所以需要把trigger商品强制放在推荐列表的最前面，以便提供更多关于trigger商品的信息给用户。在这种情况下，除了trigger的所有商品的attention值应该被mask成0。

﻿

同时，generator使用一个采样机制选择商品是至关重要的，因为这会让generator在相似的state尝试不同的action，最终能够帮助generator找到更优的序列生成策略。最简单的选择是Thompson Sampling，会依据每个商品mask后的attention值成比例地选择商品。一个更好的选择可能是Random Network Distillation，倾向于选择一个在之前相似的state下很少被选择的商品。

![](https://mmbiz.qpic.cn/mmbiz_jpg/33P2FdAnju9ktXcOebovS1SbeNE5Nc6RwrVnTnu2rZhKtELjZeKUKxKibY7z1s6AeeS0ZhOhTQFMBjoFh4RMiazQ/640?wx_fmt=jpeg&wxfrom=5&wx_lazy=1&wx_co=1)

Evaluator

**▐****模型介绍**

evaluator包含了一系列的效用函数，一个效用函数U是从一个商品序列![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABafn1fov6mkExeFxgZFIq05cvPPUIRkNggVAInDfAtRnr30SzTkI7RnJg/640?wx_fmt=png)到一个实数的映射，即![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuicH76Ox48icQKibFZibQOWABaf2gAGkVNzO2yM2ddYOoAwpysz5boZr5Cy1lQPqw0Vh2hdYgnuvaZp2g/640?wx_fmt=png)，表示在某种视角下这个序列的质量分数，在相关工作中这通常被描述为一个任务。

一些效用函数通常来自于业务规则以及好的排序结果应该满足的先验知识，比如商品多样性，这些效用函数有解析公式，能够被直接计算出来。其他的一些效用函数，比如用户对序列的交互概率，则不得不需要使用模型预测，模型会通过离线数据训练出来。模型一旦训练好后，会被用作为预先定义好的效用函数。

﻿

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKr7gIkcibLsLDJzg1ZsSv2ibP2orCE5lxovyGzAibibKQmTZuhWtIXXsiciag/640?wx_fmt=png)

evaluator的模型结构如上图所示。在经过与generator一样的特征处理后，会被5个聚焦于商品序列不同方面的模型channel处理，5个channel的输出结果会被concat起来，然后通过一个MLP转变成最终的预测分。

**▐****业务规则与模型的融合**

我们将现实业务中纷繁复杂的任务总结为四大类，包括：定坑插入、流量控制、多样性、分组排序，然后我们基于generator-evaluator框架的重排模型能够无缝地融合这些目标。

* ### 流量控制

﻿

流量控制确保来自特定群组的内容能够得到更多的曝光机会。可以从多个角度理解。比如：从公平性的角度，这些内容是受保护的少数内容；从平台生态视角来看，新创作的内容会被优先分发；从一个业务场景的功能定位的角度来看，推广上新内容的业务场景可能会更加强调新的内容而不是旧的内容。流量控制可以通过调整占比以及曝光位置两个因素实现：

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKOBe1Qla0CPAArwsqxQajn2Xoib4jdicUAMDoCnnXxiaZh9nXucg1y6gCQ/640?wx_fmt=png)

﻿

其中上标f表示流量控制，p表示一页的结果，b表示训练的一个batch，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKC7YSp97OYBiaMFHCZ2ibOWMqa7xl1dam1EpBNPT0SpribUe6ALG7CN4CA/640?wx_fmt=png)表示曝光占比的阈值。我们复用一些符号，i既表示位于位置i的商品，又表示一个商品在结果列表中的位置下标。![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKfBic9HJOK2icZ2zLOePW4qKhAmxiaOyVb5r2DBDe5XClhjdAJPH5I4CHQ/640?wx_fmt=png)是包含所有属于分组g的商品的集合，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKYeojOpLyfL18PZNTtge4jRzWvHL9rddmZhRTEibfVDkvrRicQCY0KV9A/640?wx_fmt=png)表示一页的大小，也就是一页的坑位数，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKWebXP61RTpR7S4b2kra2KwYt1CiaQLd7oVCwH7HQAlZlDb1gunfTwZQ/640?wx_fmt=png)是指示函数，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKqoaWLC4KGicjiaf2ibiclPbfXR97sfbUrdZhJckib6g1mqmraGoHWfp2hsw/640?wx_fmt=png)表示第i个商品的曝光位置，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKiczHDq4tfhCiaBI92I8uNITCTTmc5mELB0JJOmrzjulwQf4mLMMnpJtA/640?wx_fmt=png)表示曝光位置的阈值。

简单来说，这个算法是一个“抓大放小”的思想，如果整体没问题，没必要纠正其中个例的问题，如果整体有问题，那就需要对其中每一个不满足要求的个例都进行纠正与惩罚，才能逐渐达到整体满足要求的目的。

* ### 多样性

﻿

多样性意味着推荐结果列表中应该包含不同群组的商品。群组的概念可能包括：商家、类目、货源、商品展示类型（比如文本、图像、视频）。一个电子商务系统通常会考虑多个群组的多样性。多样性的reward可以写成：

﻿![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKa4q7cxs7PAoOicORkP8aXBX4fbM6PwrRdfmaDsHmGMEyXqE39DSUjgA/640?wx_fmt=png)

其中上标d表示多样性，g\_i表示位于位置i的商品所属的群组。![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKt6WFSO0SxMTmiahqicQvHnNyN280rx5GbDv6DdAziciasbF0Igl9fScVAw/640?wx_fmt=png)是在商品i前的一个滑动窗口中的多个商品所属的群组的集合，即：

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKm5xFk19ffBZ9UTQvvAfiaSDRC1E5ccVY7FqnL04s5Xk069GFKqled0Q/640?wx_fmt=png)

其中![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKgR8GGZoGrEALeAwUSL901D8Gwelcib5icdnEmz19fbouU3KvL32QicFsw/640?wx_fmt=png)是多样性的滑动窗口的长度。如果令![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKJZ7kbSxWFyE4Qcpnf2dfSMFdM9ibf9WyvtMYGsHXGD98hRSLn8pNs1Q/640?wx_fmt=png)则表示提升整个列表（而不仅是一个滑动窗口内）的多样性。

* ### 组间排序

﻿

组间排序意味着属于特定群组的商品应该以一个很大的概率被排在属于其他群组的商品的前面。在一个推广上新的场景，可能会倾向于优先展示3天内发布的新商品，然后才是展示发布超过3天的商品，以致于能够确保用户总能看到最新发布的内容。在另一些场景，被用户关注的商家的商品通常来说应该被排在用户未关注商家的商品的前面。组间排序能通过添加检查商品对的群组优先级的reward函数来实现。

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKhO4lhwS9JlQiaDNmV7nGhYGYdGia1Z8nIQvHlST8J2EA11YhFgPrwAhA/640?wx_fmt=png)

其中上标o表示组间排序，priority表示预定义好的群组的优先级函数。

* ### 定坑插入

﻿

定坑插入是一个非常严格的任务，意味着一个给定的商品必须被放在结果列表中的某个特定位置。比如用户可能会通过点击一个trigger商品来到一个推荐场景，需要强制把那个trigger商品放在推荐列表中非常靠前的位置，为了提供给用户更多关于trigger商品的信息。乍一看似乎很简单，因为我们总是可以在推荐结果列表生成以后再把trigger商品放在列表的顶部。然而，我们认为如果重排模型想要做好类似多样性和流量控制的任务，那让重排模型感知到trigger商品是很重要的。比如，在最后单独将trigger商品放在一个已经生成好的推荐结果列表的前面可能会导致头两个商品的商家重复，这会打破多样性的要求。对这种任务添加一个reward函数不会很有效，因为仅靠一个reward函数不能提供一个强保证。取而代之，正如在上文generator中介绍的，我们采用masking机制来实现定坑插入逻辑。

![](https://mmbiz.qpic.cn/mmbiz_jpg/33P2FdAnju9ktXcOebovS1SbeNE5Nc6R7qB42ptVQdf7nG7icqGaRbbJBicasGmia89rPiaeBWqFwsavuB1XC9oFgQ/640?wx_fmt=jpeg&wxfrom=5&wx_lazy=1&wx_co=1)

模型训练方法

在generator训练之前，会首先使用纯正的监督学习方式充分训练evaluator。目前对于evaluator，我们使用经典的交叉熵损失函数训练得到一个分类模型：

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKPeOLjWjqQQK3jUvEwE04FNRMLZHn3SibPrQQ7g4kDEvbBzEpjALHZ2A/640?wx_fmt=png)

其中![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKLVHcGKXIM8N1nwJM7HRpZDjqicAIXtBTHrpQGYOPVO92r4cQ8qA0Trw/640?wx_fmt=png)是一个类别的one-hot label，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKna4lXzwesKAtibBgvGOZ3LY2hpWGHicrlrXdf7wsN6rHic9C7EicItLMPw/640?wx_fmt=png)是对应类别的模型预测值。evaluator可能会预测生成的推荐结果列表是否会引导到某种特定的用户交互行为，比如点击以及各种交互的兴趣强度。

Evaluator-Generator架构中的generator，不会按照监督学习的方式，最大化某一个人为指定的输出序列的联合概率，而是像强化学习一样，generator通过一些带有随机性的探索机制，尝试让自己的生成结果能够最大化获得的reward。这个reward，既包含evaluator对生成序列点击率的模型预估分，又包含一些规则性的判断生成序列是否满足各项业务规则的评分，然后将这些分数通过加权求和的方式，融合到一个最终整体的reward上，这个reward是一个序列整体的reward，然后generator的训练目标就是不断最大化这个reward，手段是根据reward正负和大小调节生成具体序列的概率。

﻿

对于generator的训练，我们使用一个基于REINFORCE的方法。REINFORCE是一个经典的policy gradient算法。在强化学习中，policy是一个state到所有可能action的概率分布的一个映射，期望能够最大化total reward。简单来说，policy告诉我们在给定state下应该采取哪个action。在我们的模型中，公式(5)在policy中扮演了一个至关重要的角色，其中state就是![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKHOy1Xh5PW0fLduTRPENO4giaT6t1p8HfLOcv3gjwlkYFdRzcD7E0jnA/640?wx_fmt=png)，然后M个可选商品的概率分布就是![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKbVWqLETuiaiaQTf4rqwH7MkmZJVskfspI8uNZYic5vgONibo9iakt7l0xHw/640?wx_fmt=png)。假设对于一个用户u和一个候选商品集合![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKicqrb8fo5vAdcVKiatQGU9vWgnjrqk7iaKjl03mDhngCjNzb53d3KdfZw/640?wx_fmt=png)，generator生成了一个结果列表![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKtW76YKBcbYdJx92Lr84iaWnSicIcg7A9hibkneqMZ6ugrPcIckKCUTDdg/640?wx_fmt=png)记为![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKQtjIOPLlUKjcjnCxYwoZ7fficwic1x8vOE1IC8mmTuaVeYC7Hibx0eytQ/640?wx_fmt=png)。![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aK8mRCF8q4AMicIJE6ZL5ibMBuCqmYWHQqzl41MVYGGONfVBKEMQngmDBA/640?wx_fmt=png)是一个商品列表的指示器，比如![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKkTsPMhTKcfXKL4ZhFqfLhBQvEib55lKgKtlPKTIAj90iaTmichBIoTicaw/640?wx_fmt=png)表示候选集合中的第m个商品被放在了输出列表中的第n个位置。这里我们假设在候选集中进行任意排序得到![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aK1PaU78iaziaGB37xzgC4nk1VldRj766t9hogibBFECLvJK26nk8PkPEoQ/640?wx_fmt=png)。generator的损失函数![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKJgk19wxYZ9CKum0sB1uepQV4wuiaycZ99Y40D3Y3rgJdcsnviazkxf7w/640?wx_fmt=png)为：

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKBo9GM4JCtKxaej60GMy3sl1NibeymmU05lnTj2B0MYLYNibKOF97epRg/640?wx_fmt=png)

其中![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKKk4aFgdtq57Ft70OlQvykstMn5Ynv7iaZGgnrF0EOibxoJDUcacUKFsQ/640?wx_fmt=png)是generator生成的重排后的商品序列，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKBjKQApjJbdxtTBZzic2qme6859HJjoyHUWWLic5zJQBPDazscncyxuibA/640?wx_fmt=png)是线上日志记录下来的曝光序列，这两个序列的reward差值![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9stbb4l2sK7wgQJZxEt1aKUodic6Cx1qXS50SUAdiaKObUI4tdwnmWYxArTJo56JlEdMsIibmhSAe6A/640?wx_fmt=png)作为advantage函数。在这个loss中，我们假设每个动作对advantage值的贡献相等。

我们知道先进的训练方法比如PPO，尽管如此，基于REINFORCE的方法也表现得很好，所以我们把这个选项留待后续研究。我们观察到梯度裁剪对训练有很大好处。

﻿

总结一下这种强化学习训练方式的两个好处：

1. 不需要显式地指定label，在我们重排的场景下，就是不需要显式地指定模型应该输出怎样的重排序。因为我们根本不知道最优的重排序是什么，或者是有可能存在较多种优秀的重排序，没法知道哪个更好。这种情况下，我们就不需要去让模型模仿监督信号，而是要直接面向reward也就是最终效果进行优化，只要是能够获得更高reward的行为，就是更好的行为，有可能找到比贪心排序更好的组合更优的排序结果。正所谓“不管黑猫白猫，抓到老鼠就是好猫”，只面向最终结果，只要结果是好，不强求一定要模仿怎样的行为。
2. ﻿由于这个reward R是环境给予的反馈，在我们的实践中就是evaluator给予的反馈，它跟generator的模型参数是没关系的，因此我们调整generator的模型参数，去最大化这个最终获得的总reward R，是不需要对reward R算gradient的。也就意味着，如果假设reward是一个函数产生的，就算产生reward的这个函数是不可导的也没关系，因为我们不需要对产生reward的这个函数进行求导，就算它是一个黑盒，我们不知道它的计算式子也没关系，只要我们拿到它最终的值就可以了。因此这个reward函数可以任意复杂，既可以是模型预估分，也可以是根据业务规则计算出来的分数，方便融入各种业务要求，因此非常适用于我们这个业务规则约束较多的场景。

![](https://mmbiz.qpic.cn/mmbiz_jpg/33P2FdAnju9ktXcOebovS1SbeNE5Nc6R7tBInnyFh7Kcmh76NMu6xBg21dXd5QphTq68NrvpUic9KdIibwYwTgdQ/640?wx_fmt=jpeg&wxfrom=5&wx_lazy=1&wx_co=1)

实验结果

我们在淘宝信息流场景实践了EG架构的重排。generator模型的输入是混排后分数最高的20个候选item，这20个item中会包含不同类型的供给，它们会作为一个集合送进generator模型（也就是actor）打分，然后generator生成一个长度为10的重排后的序列。 训练结束后，我们只将训练好的序列生成器generator上线，evaluator不上线。

﻿

evaluator是判别式模型，给每个序列打一个分，希望用户反馈更多的序列的evaluator分数比用户反馈更少的序列的evaluator分数要高，因此evaluator离线评估看的是auc指标。在我们的实验中，evaluator的auc大概为0.75左右。

generator的离线评估指标是better percentage，含义是所有请求的样本中，generator生成的重排序获得的evaluator score，比线上真实曝光序的evaluator score更高的比例。在我们的实践中，generator的better percentage通常能达到70%+左右，也就是说如果evaluator的评判打分是靠谱的，那么大概有70%的请求，generator能够生成出比之前的线上曝光序更好的序列。

﻿

该重排模型成功上线并取得了显著的线上效果。

![](https://mmbiz.qpic.cn/mmbiz_jpg/33P2FdAnju9ktXcOebovS1SbeNE5Nc6RyKJlicbo13ZicNiaU9aG8C4mfvhVMMX7diaGQCmETM1mkIicAicz4hFey8OQ/640?wx_fmt=jpeg&wxfrom=5&wx_lazy=1&wx_co=1)

参考文档

[1] MiDNN:﻿Tao Zhuang, Wenwu Ou, and Zhirong Wang. Globally optimized mutual influence aware ranking in e-commerce search. In IJCAI, 2018.

[2] seq2slate: ﻿Irwan Bello, Sayali Kulkarni, Sagar Jain, et al. Seq2slate: Re-ranking and slate optimization with rnns, 2018

[3] PRM: Changhua Pei, Wenwu Ou, Dan Pei, Yi Zhang, Yongfeng Zhang, Fei Sun, Xiao Lin, Hanxiao Sun, Jian Wu, Peng Jiang, and Junfeng Ge. Personalized re-ranking for recommendation. In RecSys, 2019.

﻿[4] DLCM: ﻿Qingyao Ai, Keping Bi, Jiafeng Guo, and W. Croft. Learning a deep listwise context model for ranking refinement. In SIGIR, 2018.

﻿[5] GSF: ﻿Qingyao Ai, Xuanhui Wang, Sebastian Bruch, Nadav Golbandi, Michael Bendersky, and Marc Najork. Learning groupwise multivariate scoring func- tions using deep neural networks. In ICTIR, 2019

﻿[6] MiRNN:﻿Tao Zhuang, Wenwu Ou, and Zhirong Wang. Globally optimized mutual influence aware ranking in e-commerce search. In IJCAI, 2018.

﻿[7] Exact-k: Gong, Yu, et al. "Exact-k recommendation via maximal clique optimization." Proceedings of the 25th ACM SIGKDD international conference on knowledge discovery & data mining. 2019.

﻿[8] EGRerank: Guangda Huzhang, Zhenjia Pang, Yongqing Gao, et al. Aliexpress learning-to-rank: Maximizing online model performance without going online. TKDE, 2021

![](https://mmbiz.qpic.cn/mmbiz_jpg/33P2FdAnju99Up5tbCtZibX4V2wEiaQtESWtnRTODoVMPYMLwH7qYngkrJvWE2Fq8nUOUYm2TynRa2O3AGDsHibhg/640?wx_fmt=jpeg&wxfrom=5&wx_lazy=1&wx_co=1)

团队介绍

我们是大淘宝技术-私域用户算法团队，负责淘宝商家私域产品（店铺、详情、关注）相关的算法，我们通过对海量数据的分析和学习，帮助亿万用户在商家私域高效地逛和买，辅助数千万商家运营客户。同时我们也是一支注重技术创新，乐于分享的团队，不少成果已经整理发表在了AAAI、SIGIR、WWW、KDD等国际顶会上。这里有海量的数据、充足的计算资源、丰富的应用场景等着你来挑战！想进一步了解我们，可以通过邮件tieyi.lq@taobao.com联系我们！

**¤****拓展阅读****¤**

[3DXR技术](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAxNDEwNjk5OQ==&action=getalbum&album_id=2565944923443904512#wechat_redirect) | [终端技术](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAxNDEwNjk5OQ==&action=getalbum&album_id=1533906991218294785#wechat_redirect) | [音视频技术](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAxNDEwNjk5OQ==&action=getalbum&album_id=1592015847500414978#wechat_redirect)

[服务端技术](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAxNDEwNjk5OQ==&action=getalbum&album_id=1539610690070642689#wechat_redirect) | [技术质量](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAxNDEwNjk5OQ==&action=getalbum&album_id=2565883875634397185#wechat_redirect) | [数据算法](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzAxNDEwNjk5OQ==&action=getalbum&album_id=1522425612282494977#wechat_redirect)