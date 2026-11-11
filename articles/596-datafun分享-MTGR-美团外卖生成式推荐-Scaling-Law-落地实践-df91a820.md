---
title: '[datafun分享] MTGR：美团外卖生成式推荐 Scaling Law 落地实践'
company: 美团
tag: 生成式
date: 2025-09-11
url: https://mp.weixin.qq.com/s?__biz=MzkxMjM2MDIyNQ==&mid=2247656360&idx=1&sn=ec16a8bb0a67a5c822f9477815ec4fda&chksm=c09f3dc2e86e0ff9356f4275b4dc9704b9a173a1e2c885edba656e723a4a67fea29cc7a895db&mpshare=1&scene=1&srcid=1007PRgq1N8wrvg4JzthkTp0&sharer_shareinfo=6176f37960dc8a7115ffcd759387a833&sharer_shareinfo_first=6176f37960dc8a7115ffcd759387a833#rd
account: DataFunSummit
origin: xlsx
---
![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwhgibic8GHTAD5PoUDsIN504CdxeMHs3wprwygxxh2CkNl3Iw4R1CtSn6nNOFC2Y344VCKibias7JTmg/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgy05fLMBzU9P4NTq0YCqSe6kUDbX0XLEquF55SLnNHGsPRaShayurBNVn5Ktib9f54RdmrGT9pEjBg/640?wx_fmt=png&from=appmsg)

**导读** 本次分享题目为 MTGR：美团外卖下一代生成式推荐模型落地实践。

****主要介绍：****

1. 背景：为什么要做生成式推荐

2. MTGR ：美团生成式推荐落地实践

3. MTGRBoost ：训推引擎建设

4. 总结与展望：未来工作

5. Q&A

分享嘉宾｜韩瑞东 美团 算法专家

编辑整理｜Kathy

内容校对｜郭慧敏

出品社区｜DataFun

---

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfLqjLh41sB9ZsYp7d9FswzCj4Zp00SWo5aAick1GNlGun09ccJHJZzmg/640?wx_fmt=png&from=appmsg)

扫码入群参与讨论

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzR9NUfbmOybYiaT2MLAPjibTAVpHpSP1DG2exDpXd5Tk9UbuxmJrjtcyIibDibBzcxowLdxkBDqeVuCQ/640?wx_fmt=png&from=appmsg)

✅ 对分享有疑问？群里问！

✅ 老师在线解除疑惑！

✅ 有心得体会想分享？群里聊！

扫码入群参与讨论

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/e3dmuP1SaHcklzY3LGzN0I3DTOSaDsxw8VbAyGQgXF8EO7DLjujMIZ9xbRu8NPYs3dhfeBiaialzVKn5AWJBOSAQ/640?from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=3)

01

**背景：为什么要做生成式推荐**

推荐系统经过多年发展，已形成较为成熟的建模体系。然而，传统的优化方式（如通过增加交叉模块复杂度来提升效果）逐渐触及性能天花板。在美团外卖的排序模型演进过程中，我们曾尝试通过增加 MLP 层数、扩展 MoE 专家数量等方式提升模型表现，但离线和在线效果提升有限，表明传统建模范式已难以支撑进一步突破。

而大模型展现的扩展律（Scaling Law）特性为推荐领域带来新机会。大语言模型（如 LLaMA、DeepSeek-R1）的计算复杂度远超推荐模型，但其通过增加规模、数据量和算力持续提升性能的规律值得借鉴。

大模型（LLM）的出现，尤其是“Scaling Law”理念的提出，为推荐系统带来了新思路。随着 LLaMA、DeepSeek 等模型在参数量和计算复杂度上的飞跃，模型性能被证明可通过持续扩增资源实现提升。这一理念启发我们思考：是否可以将这种“以算力换效果”的建模方式引入推荐系统？

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0Ff1EdtXicruyf69qp43Pn6nZygZSt5kHrluibo5bgHuPVTCyhE4V48ZqSA/640?wx_fmt=png&from=appmsg)

我们发现，用户行为序列是推荐系统中最富含信息的部分。然而，当前主流做法多采用浅层的 Target Attention 结构对序列进行压缩，导致信息损失严重。2023 年起，我们开始尝试采用 Multi-Query Attention 和大规模 MoE 结构对用户模块进行原生扩展（Scaling User Module），以保留更完整的用户行为表征。

与之对比，传统的交叉模块扩展（Scaling Cross Module）虽然能更好建模 user X item 关系，但训练和推理成本高，扩展性差。因此，转向用户侧建模成为我们优化方向的重要转变。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfFVsVMpz5dAkUOrDTSRLbYfXtMLLCuq8GCR5dh0jnAey01qVBxkVgDQ/640?wx_fmt=png&from=appmsg)

**1. 推荐系统引入生成式建模面临挑战**

尽管生成式建模在自然语言处理领域已广泛应用，但在推荐系统中部署超深注意力机制仍面临诸多挑战：

* 基建历史包袱重：多数推荐系统仍基于 TensorFlow 1.x 等老旧架构，难以支持复杂 Attention 结构的高效实现；
* 算法认知螺旋上升：不同于 LLM 简洁的 decoder-only 架构，推荐模型往往包含多个模块，Scaling 哪一部分，怎么 Scaling 等核心问题在很长一段时间没有共识；
* 算法与工程协同不足：推荐模型结构复杂，缺乏算法与工程深度协同的 code design，限制了模型创新落地。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfHib9B2UZZ07bYcEjhE8KHiaQIlDhiccv8H3yO9lg5tZzOzB9f7aMoetMQ/640?wx_fmt=png&from=appmsg)

**2. 推荐系统中****Scaling Law****一一****HSTU**

Meta 提出的 GR 模型（基于 HSTU 架构）首次在真实业务场景中验证了生成式推荐模型的可行性。该模型将用户行为、点击、曝光等信息组织为一个完整序列，并采用生成式建模方式进行训练。其在任务定义、数据组织和模型结构上均区别于传统 DLRM 模型：

* 数据组织：将用户历史行为、点击信息、用户画像整合为统一序列；
* 任务定义：支持召回（自回归预测）与排序（多目标预估）一体化建模；
* 模型结构：采用简化版 Transformer，将长序列输入 Transformer 中进行信息交互。
* 扩展性表现：展现出良好的 Scaling Law 特性，模型效果随规模扩增持续提升。

GR 模型的落地为推荐系统提供了可持续发展的新路径，也促使我们深入思考如何在美团外卖场景中构建具备更强扩展性和表达能力的生成式排序模型。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfBrn0WUib2zb2SgMK430Fg0m1jxovaVqic2m4PfudicX4oPrKt8ia2Tg14Q/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfYjOLWbOibtEeSwtOCSggvSHAKictiaxSQAbcDeJibLyp5upJr5ibufC6Xxw/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0Ff989hz1lvhMvdvtYkD89B840QLictGh3tEuzoic0gmVJQURzpjDbeEn1A/640?wx_fmt=png&from=appmsg)

扫码入群参与讨论

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzR9NUfbmOybYiaT2MLAPjibTAVpHpSP1DG2exDpXd5Tk9UbuxmJrjtcyIibDibBzcxowLdxkBDqeVuCQ/640?wx_fmt=png&from=appmsg)

✅ 对分享有疑问？群里问！

✅ 老师在线解除疑惑！

✅ 有心得体会想分享？群里聊！

扫码入群参与讨论

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/e3dmuP1SaHcklzY3LGzN0I3DTOSaDsxw8VbAyGQgXF8EO7DLjujMIZ9xbRu8NPYs3dhfeBiaialzVKn5AWJBOSAQ/640?from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=3)

**02**

**MTGR****：美团生成式推荐落地实践**

基于上述背景与趋势，提出了 MTGR（MeiTuan Generative Ranking）模型，作为美团外卖下一代生成式推荐模型的实践方案。MTGR 旨在融合生成式建模思想与推荐系统特性，解决传统排序模型的扩展瓶颈，提升推荐效果与系统效率。

**1. MTGR-****核心问题**

* 通过严格的用户轨迹建模 next item：MetaGR 用 Causal Mask 建模沉浸式视频流，符合业务形态，用户一次只能看到一个 item；而外卖业务是单列 feed，一次曝光同时展示多个 item，强行引入“前一条导致后一条”的因果假设并不符合业务现状；此外，外卖 90% 以上的行为是低信息密度的曝光，若全部 token 化建模将带来十倍以上计算开销，训练与推理成本不可接受。
* 交叉特征缺失：MetaGR 为统一召回与排序，直接删掉全部交叉特征，靠模型 Scaling 弥补。在 LBS 场景下，“商家-用户距离”等交叉信号对转化起决定作用；我们的实验表明删掉交叉特征后，需要近百倍算力才能追回效果。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfIE3L8lt4JZT2Bh3OWbkIQ1sw67FgsLSJIJecSxOryADicprYvZg1WwQ/640?wx_fmt=png&from=appmsg)

**2. MTGR****的数据组织与处理策略**

我们在 MTGR 中采取了一系列措施以适应美团外卖的具体需求。首先，在数据组织上，我们取消了传统的负采样操作，因为单次曝光作为单独 token，数量上仅占用户行为 token 量级很的一小部分。此外，我们还取消了序列检索，采用端到端的长序列建模方式，这有助于提高长序列建模效果。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfV4QEt78MiczxU6Ybw61WFSUQMjNAmENXsCWf4HFIJ1ByZ68OqiaEs5BA/640?wx_fmt=png&from=appmsg)

在模型结构方面，模型结构整体上参考 HSTU 的实现，在序列构成和多目标预估上做了改动：

* 序列构成：序列由多种不同类别的 Token 构成  —— user\_profile（用户画像），lifelong\_seq（终生行为序列），rt\_seq（实时序列），pv\_items（曝光物品）。每种 Token 类别包含多个特征，同一类别具有相同的特征空间。
* HSTU 计算：输入序列经过 Embedding 层后，进入到 N 个 HSTU block 进行 Attention 计算。为了避免实时序列和曝光 items 出现特征穿越，需要根据时间戳自定义mask矩阵。
* 多目标预估：通过 MMoE 进行多任务学习。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfDGR4AXFJ8G8CE0VlRDO4icG2EfSrBXEA6yezmicrCaEy2EdYLWnR3Dlw/640?wx_fmt=png&from=appmsg)

为了更好地适配不同类型 token 的空间对齐，MTGR 提出了 Group LayerNorm，并针对静态特征采用了双向注意力编码，同时对实时侧特征实施动态演码以防止信息泄露。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfsRlxabSOUZkiccmlFxd14Z64xicbHGevXMATe300FJDuDG3UBrwGv4xQ/640?wx_fmt=png&from=appmsg)

**3. MTGR-****离在线效果**

我们发现，随着模型规模的扩展，收敛所需的数据量也在增加。尽管如此，MTGR 在不同尺寸下均展示了优异的表现，相比上一代模型，MTGR-large 复杂度提升了 65 倍并取得了最好的效果。更重要的是，保留交叉特征对于 LBS 业务至关重要，其影响远超模型规模增长带来的收益。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfMn2Xo0bQICyRWTBZD0AdBV8kibItx8a9jWdicUCJ8IgBQIArIGUyYAyA/640?wx_fmt=png&from=appmsg)

通过对不同尺寸模型（small, medium, large）进行长时间训练，MTGR 在离在线指标上取得了优异表现。在线上部署阶段，MTGR-large 模型不仅取得了近年来最大的迭代收益，还在推理成本上实现了 44% 的下降。这一成就主要得益于单分片一次性打分机制的应用，相比之前的多分片推理架构，更高效的复用用户侧计算结果，分摊计算成本，减少了计算资源消耗。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfKcJibb6mWW7FzSumSbGmICibEZhiadPUdRob6FdpPXMABnh5QAkmR5piaQ/640?wx_fmt=png&from=appmsg)

扫码入群参与讨论

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzR9NUfbmOybYiaT2MLAPjibTAVpHpSP1DG2exDpXd5Tk9UbuxmJrjtcyIibDibBzcxowLdxkBDqeVuCQ/640?wx_fmt=png&from=appmsg)

✅ 对分享有疑问？群里问！

✅ 老师在线解除疑惑！

✅ 有心得体会想分享？群里聊！

扫码入群参与讨论

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/e3dmuP1SaHcklzY3LGzN0I3DTOSaDsxw8VbAyGQgXF8EO7DLjujMIZ9xbRu8NPYs3dhfeBiaialzVKn5AWJBOSAQ/640?from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=3)

**03**

**MTGRBoost****：训推引擎建设**

随着生成式推荐模型 MTGR 的模型规模和计算复杂度显著提升，传统的推荐系统训练与推理框架已难以支撑其高效运行。为此，美团外卖构建了面向生成式推荐模型的高性能训练与推理引擎——MTGR Boost，以应对模型参数量、数据规模和推理时延等多方面的挑战。

按照 Scaling Law，MTGR 的效果提升直接依赖于训练数据量与参数量的同步放大。参考 LLM 训练动辄数百张卡、数十天的投入，推荐场景过去“单机单卡”的惯性思维被彻底打破：

* 训练侧：稀疏 Embedding 规模随特征维度线性膨胀，分布式存储与梯度通信成为新瓶颈；
* 推理侧：模型大小和计算量膨胀显著，需要更强算力、更大显存的 GPU 加速卡，或者考虑 CPU-GPU 联合推理的异构计算模式。

为此，我们构建了面向生成式推荐模型的高性能训练与推理引擎——MTGR Boost，整体分为两层：

* MTGR-Training：基于 TorchRec 深度定制，专注多机多卡高效训练；
* MTGR-Inference：以 TensorRT 为核心，面向毫秒级在线推理。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0Ff4ia0ynI6NSVg27ZqZnSPNFqsq4AwA4GXricrcKrVIEWPTvKuVW3RyGtg/640?wx_fmt=png&from=appmsg)

**1.****MTGR-Training****：基于****TorchRec****的深度定制与性能提升**

在训练侧，MTGR 模型的扩展带来了训练计算量的指数级增长。为满足模型对大规模数据和参数的处理需求，我们对训练引擎进行了全面重构，从 TensorFlow 1.x 迁移至 TorchRec 生态，并基于 TorchRec 框架进行深度定制，构建了支持大规模参数训练的 MTGR Training 系统。整个系统分为三层架构：

* 底层：采用 Meta 开源的 TorchRec 作为基础框架，并进行深度功能扩展；
* 中层：封装训练流程，包括数据读取、模型评估、断点续训、一致性校验等；
* 上层：提供算法模型接口，支持灵活定义模型结构。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfajWugiafjwwL8nd6icyibdUuNJUvdfZo23WX6TclxiagxA6ovOdAXia6BQw/640?wx_fmt=png&from=appmsg)

在训练优化方面，我们重点从功能扩展与性能优化两个方向进行突破。

* 功能扩展

  动态 HashTable 支持：工业场景中特征 ID 频繁更新，传统静态 Embedding 表难以应对。我们自研了高性能的动态哈希表（Hashtables），支持动态扩容、无需预设容量，显著提升训练灵活性。

  梯度累计：针对推荐系统中稀疏参数分布不均的问题，我们实现了高效的梯度聚合机制，提升多机训练效率。

* 性能优化

  ID 去重与通信优化（ID Unique）：通过去重输入稀疏 ID，减少冗余通信量，尤其在多机训练中效果显著，端到端吞吐提升近 45%。

  变长序列负载均衡：用户行为序列存在严重长尾现象，固定 Batch Size 训练易导致计算资源浪费。我们引入动态 Batch Size 机制，根据卡上序列长度动态调整数据读取量，保证各卡计算负载均衡，提升训练吞吐约30%。

  Kernel 优化：与 NVIDIA 合作，引入深度优化的 Cutlass-based 版本 HSTU Kernel，Attention 计算效率提升 2~3 倍。

  GAUC 计算优化：将部分 CPU 计算逻辑（用于训练效果监控）迁移至数据读取进程，减少训练主进程资源竞争，吞吐提升约 10%。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfnwqQyGQc8sfWdibCnAt36U5TNbvntj9CGA6zA1YeqY6yEfCh66YPicVQ/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0Ff1S7ce1ic8dJthGiav7kx9icVyQ8GDGnWthop8vuFibbsZKmqicoEWtjiczsg/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfR7ACVA5btb76F1icJyiaRjOUcN2dJaF3qvk6aQayEbngQKzPxCiaWGNUg/640?wx_fmt=png&from=appmsg)

**2. MTGR-Inference****：低时延、高吞吐的部署方案**

在推理侧，MTGR 模型的复杂度显著增加，为满足线上严格的延迟约束，我们构建了基于 TensorRT 的高性能推理系统，并引入多项优化策略。

* 框架选择：TensorRT + Triton Inference Server
* 针对推荐模型中大量特征需从 CPU 传入GPU的问题，优化 H2D 流程，减少传输延迟。
* 进一步优化 HashTable 通过裁剪写操作进行加速，额外引入 FP16 计算、算子融合等提升推理性能。
* 通过图优化技术提升模型推理效率。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfWO8DAOuzM2ia5ZNAyTaAQHOh6FCGj7G8ZzhaaRqHuUbVfEeMZCnUWKg/640?wx_fmt=png&from=appmsg)

扫码入群参与讨论

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzR9NUfbmOybYiaT2MLAPjibTAVpHpSP1DG2exDpXd5Tk9UbuxmJrjtcyIibDibBzcxowLdxkBDqeVuCQ/640?wx_fmt=png&from=appmsg)

✅ 对分享有疑问？群里问！

✅ 老师在线解除疑惑！

✅ 有心得体会想分享？群里聊！

扫码入群参与讨论

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/e3dmuP1SaHcklzY3LGzN0I3DTOSaDsxw8VbAyGQgXF8EO7DLjujMIZ9xbRu8NPYs3dhfeBiaialzVKn5AWJBOSAQ/640?from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=3)

**04**

**总结与展望：未来工作**

**1. MTGR****及其训推引擎的成功应用**

为了支持 GR 模型在美团实际业务中应用落地，我们提出了 MTGR 以及对应的模型训推引擎 MTGRBoost ，以较低的成本支持了对于 DLRM base 达65倍甚至更大规模计算量的 GR 模型的训练、推理，实际业务的线上 AB 实验也取得了一定的效果收益，为下一代搜推广模型的迭代打开了算力天花板。

**2.****未来主要工作**

展望未来，我们将围绕 MTGR 开展以下两个关键领域的探索：

* 改变多阶段上下游漏斗迭代范式

  MTGR 具备高效的推理性能，能够在较短延迟内处理数千个 token 量级的数据。这意味着它可以处理更复杂、更长的用户行为序列，从而可能改变现有的多阶段推荐流程。传统的推荐系统通常采用多阶段漏斗筛选机制，从召回、粗排到精排逐步缩小候选集。然而，MTGR 的强大能力使得我们可以考虑简化或重新设计这一流程，实现更加直接和精准的推荐路径。
* 跨业务的异构建模

  另一个重要特点是 MTGR 的所有输入均被 token 化，这使其天然适合于异构建模。基于此特性，我们将探索如何利用 MTGR 开发跨业务的通用模型。例如，在外卖、酒店预订等多个不同业务场景之间共享部分模型结构或参数，不仅可以提高模型的泛化能力和效率，还能促进各业务间的协同效应，进一步提升用户体验和服务质量。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfVibwVvqpNuTIS0NqtpBPtRlGHuSc29WO7Wur9JEokmL6rQ0tPeePrnQ/640?wx_fmt=png&from=appmsg)

**05**

**Q&A**

**Q1****：****MTGR****在训练和推理阶段的****MFU****（****Model Frequency Utilization****）表现如何？**  
A1：在训练阶段，MTGR 的 MFU 接近 30%。然而，在推理阶段，由于当前仅支持单分片推理，即每次请求处理一条样本，导致 GPU 性能未能完全发挥，MFU 较低，仅为个位数。尽管如此，相比上一代 DLRM，推理效率已提升了近一半，并有望进一步将推理成本降至原 DLRM 模型的 10%-20%。

**Q2****：****MTGR****是否是一个真正的生成式模型？**

A2：MTGR 本质上是一个判别式模型，叫生成式的原因，主要是其架构与 Meta GR 一致，采用了类似于 decoder-only 或 transformer-like 架构进行建模，但这并不意味着它是生成式的。生成式模型通常用于预测序列中的下一个元素，而 MTGR 专注于对用户行为序列进行高效编码以进行排序任务。

**Q3****：长序列建模对****MTGR****的效果有何影响？**

A3：实验显示，DLRM 直接对超长序列（如接近 3K 长度）进行建模时，效果反而不如使用较短序列（几百长度）。这可能是由于浅层网络难以从过长的序列中提取有用信息，反而容易受到噪声的影响。但是 MTGR 上则出现了序列长度增加效果增加的 scaling 曲线，表明 transformer 架构下超长序列 end2end 建模具有潜在的效果空间。

**Q4****：****MTGR****如何实现长度外推？**

A4： MTGR 通过随机截断的方式进行长度外推训练，能够在训练阶段实现超过 2 倍的加速比，并在推理时使用原始长度进行准确预测。有两个版本的序列长度被测试，一个较短版本（不到 1K 量级）未做长度外推，另一个超长版本（平均 2～3K 量级）则实现了良好的外推效果。

**Q5****：从****TensorFlow****迁移到****TorchRec****遇到了哪些挑战？**

A5：主要挑战包括评估逻辑的对齐以及不同框架间算子定义差异。特别需要注意的是某些函数维度默认值的不同可能导致长时间的调试工作。建议优先确保评估框架的一致性，并仔细检查 API 使用细节。

**Q6****：****MTGR****是否要工程同学参与优化？**

A6：工程优化对于 MTGR 项目的成功至关重要，特别是在编写高性能 CUDA 内核等方面的知识对于最大化利用 GPU 资源非常关键。虽然当前算法研究人员可能不熟悉这些底层技术，但随着相关工具和库的开源，未来的项目实施成本预计将大幅降低。

**以上就是本次分享的内容，谢谢大家。**

![图片](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUiaUMwM8I3NYH3SVrllWIPIMQXDtN5DqCLRhFwFhR9RictLsYYBpOwibjfw/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/EBaibcQicPxgwUz1D0owP8iavL9jp4gW0FfqgqTpOgoXf2tDhdmlUN9UQwf0iadBNa8anRChic141ZesdIGa8SA2t0Q/640?wx_fmt=jpeg&from=appmsg)

**分享嘉宾**

INTRODUCTION

![图片](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

****韩瑞东****

![图片](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

****美团****

![图片](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

**算法专家**

![图片](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

毕业于中国人民大学，主要负责美团外卖推荐系统的算法研发，专注于大模型与排序结合、LLM4Rec 等领域研究，主导美团生成式推荐项目 MTGR 落地。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzR9NUfbmOybYiaT2MLAPjibT2Gp7ytXgRhWdusMTyLqGvBR97NvxHiawQ6yia2icKxkXfjkqmlDy5vp3w/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzFIRJgR6icnsYggqY658ic35gBNk4iagR3AMo0anwXiadd2w6kNg8lbwCuibXX1ic9ZCAE2vibdbL63Zia9A/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyuwOorJVF9wBVsoGY433Re7t5qiaQdkKITdOPibK2lpiaKxCPvppsulq8wuRIHYNBZrTG1NmR073FOg/640?wx_fmt=png&from=appmsg)

往期推荐

[荣耀 Data+AI 最佳实践](https://mp.weixin.qq.com/s?__biz=MzkxMjM2MDIyNQ==&mid=2247656343&idx=1&sn=0e2aa69b8511c828a63b360e19567a5c&scene=21#wechat_redirect)

[1688 GenAI驱动的商业智能与多模态创新](https://mp.weixin.qq.com/s?__biz=MzkxMjM2MDIyNQ==&mid=2247656336&idx=1&sn=b00726ebd31abd682f9e3fb8ef50fa34&scene=21#wechat_redirect)

[滴滴 ChatBl 技术实践:智能数据分析的前沿探索与应用](https://mp.weixin.qq.com/s?__biz=MzkxMjM2MDIyNQ==&mid=2247656336&idx=4&sn=f0704f1afbb7401d32c9acc493877301&scene=21#wechat_redirect)

[GRAB：百度推荐广告生成排序模型技术实践](https://mp.weixin.qq.com/s?__biz=MzkxMjM2MDIyNQ==&mid=2247656315&idx=1&sn=a28d0bc49feab13a44a2253742cb74d2&scene=21#wechat_redirect)

[Data Agent：NL2SQL 应用新范式](https://mp.weixin.qq.com/s?__biz=MzkxMjM2MDIyNQ==&mid=2247656315&idx=2&sn=f3d95e759bba8b5d543ab35462dd2e14&scene=21#wechat_redirect)

[蚂蚁集团基于 Ray 构建的分布式 AI Agent 框架](https://mp.weixin.qq.com/s?__biz=MzkxMjM2MDIyNQ==&mid=2247656315&idx=4&sn=3b708e04b4c6d917a71b37be9b0c9533&scene=21#wechat_redirect)

[蚂蚁数科AIGD平台：高质量推理数据驱动AI推理模型训练革新实践探索](https://mp.weixin.qq.com/s?__biz=MzkxMjM2MDIyNQ==&mid=2247656297&idx=1&sn=d9b9bee75992c7d1f7b80be6976b4aef&scene=21#wechat_redirect)

[蚂蚁集团基于 Ray 构建的分布式 AI Agent 框架](https://mp.weixin.qq.com/s?__biz=MzkxMjM2MDIyNQ==&mid=2247656297&idx=4&sn=4edb3a6616dbee8b6f466d0bc4b06e41&scene=21#wechat_redirect)

[颠覆营销：京东、蚂蚁、联想、奇富科技实战派揭秘AI Agent如何助力增长！](https://mp.weixin.qq.com/s?__biz=MzkxMjM2MDIyNQ==&mid=2247655876&idx=2&sn=21516cd6c0d989574e4f22875834335f&scene=21#wechat_redirect)

[深圳站重磅！Agent安全×Infra基座×场景创新全解析](https://mp.weixin.qq.com/s?__biz=MzkxMjM2MDIyNQ==&mid=2247655874&idx=1&sn=7e8aefcd799057a2bb3e8c561c3cb85c&scene=21#wechat_redirect)

![](https://mmbiz.qpic.cn/mmbiz_png/vmBOIhnBRdvxZoWyBGhGa8aeRDHjjyDAaD4AK24kZXs0kUQMyQKQhBVI2lRf9QfjtUwVJcBZAZic9pdcJswicyzw/640)

点个在看你最好看

SPRING HAS ARRIVED

![](https://mmbiz.qpic.cn/sz_mmbiz_png/SQ45Y3ZsfmJKVcT1kXawmkZW9bwJAEymGTIkxekau03ntGSgJoQhqTFzWsFiaBmQWUiaUglT1tSW1cJxsJAEjZnQ/640)