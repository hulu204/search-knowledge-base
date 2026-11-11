---
title: '10亿月活用户下，快手基于CNCF Dragonfly的超大规模镜像分发实践'
company: 快手
tag: 搜索
date: 2023-01-17
url: http://mp.weixin.qq.com/s?__biz=Mzg2NzU4MDM0MQ==&mid=2247485076&idx=1&sn=ffcaba975dc3c4b92057b77bd3f03d97&chksm=ceb8264ef9cfaf58d27b93346752f3e673cf6aab78068cb41aef29309a0561d763c3dd8bf55c#rd
account: 快手技术
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/ZxDY5TMPs0EtMUQLZicoiaf5Kvjng1m5ZSLEqpQY7jicQHrzepf19Uxic8o4VSjtYuSdYCODcuxRR6jYLKVqVHI0XA/640?wx_fmt=jpeg)

挑战

快手容器云平台旨在为快手不断增长、不断变化和多样化的业务，提供基于容器化部署的超大规模基础设施服务。为了实现这一目标，快手工程师需要解决弹性、稳定性、效率和无服务器架构等挑战，在这些挑战中，镜像分发的稳定性和效率也是最棘手的问题之一。

解决方案

为了让快手容器云平台的镜像分发更加稳定和高效，快手容器云技术团队携手阿里云、蚂蚁集团在龙蜥社区适配，优化落地解决方案。事实证明，Dragonfly 及其子项目 Nydus 是最合适的解决方案，该方案能够与现有系统很好地兼容，在现有能力基础上平滑过渡，同时也为服务交付带来了大幅的效率提升。

效果

Dragonfly 上线后，整个集群通过 P2P 组建分发网，所有节点帮助中心化 Harbor 缓解网络带宽压力。Harbor 的网络带宽压力平均缓解 70% 以上，峰值压力缓解 80% 以上，镜像分发系统变得更加稳定、可靠、高效，系统能够同时支持更多数量的镜像并发拉取请求，尤其是在应对 Daemonset 部署和关键、大批量实例业务服务更新的场景中，高并发镜像拉取仓库不再是瓶颈。

使用项目

* Dragonfly https://github.com/dragonflyoss/Dragonfly2
* Nydus https://github.com/dragonflyoss/image-service
* containerd https://github.com/containerd/containerd
* Harbor https://github.com/goharbor/harbor

相关数据

|  |  |  |
| --- | --- | --- |
| 峰值缓解80%以上 | 镜像拉取时间节省90%以上 | POD实例服务耗时节省50% |

为每月10 亿用户提供稳定性和性能支持

> 在快手，Dragonfly 有效解决了海量文件分发问题。
>
>                                                                          ——吴宏斌，快手综合运营平台负责人

对于快手的镜像分发系统升级改造来说，最大的挑战不仅仅是镜像仓库峰值压力的缓解和镜像拉取加速，如何让服务分发无缝衔接平滑过渡，尽可能让业务无感、不受系统变化影响同样重要。快手容器云平台工程师通过调研发现，Nydus 与 Dragonfly 系统深度集成，同时也支持传统 OCI 镜像，能够以兼容友好的方式提供快速、稳定、安全、便捷的容器镜像访问，非常容易地就能适配容器云平台已有工作，实现业务从已有镜像使用方式平滑过渡到新镜像格式。平台唯一要做的就是将容器运行引擎从 Docker 切换到 containerd，因为 containerd 与 Dragonlfly 的集成体验更好。在快手工程师的努力下，大规模节点的容器引擎平稳切换轻而易举，containerd 和 Dragonfly 均已被快速全面采用。

稳定高效的镜像分发

对于稳定、高效的镜像分发，Dragonfly 给出了完美的答案。在快手，有许多重要的服务需要在短短几分钟内扩容到成千上万个实例，例如快手的818 购物节或双 11 活动的业务扩容需求。这种缩放需要数千 GB 带宽才能直接从镜像仓库下载。在另外一些场景中，预测模型和搜索业务需要定期更新模型参数文件和索引文件来保证推荐效果和检索效果，这在技术上意味着必须立即将数百 GB 的文件分发到每个相关实例。

快手工程师在所有容器云主机部署了 Dragonfly 组件：Dfdaemon 和 Dfget，通过 P2P 算法拉取文件。同时，在每个 AZ 部署了独立的超级节点集群，为 Dfget 设计了 Schedule Server，选择合适的超级节点来避免跨 AZ 或者跨 Region 的流量。更重要的是，工程师基于 Dragonfly 独特的片管理 P2P 算法实现了数据流 P2P 传输，降低了磁盘负载。得益于 Dragonfly，数以万计的实例可以同时拉取镜像或下载文件，而不会增加时间成本和磁盘负载。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0EtMUQLZicoiaf5Kvjng1m5ZS1OJKRgD75U4GCeYCXdzkLJLVSLxRMDopNC0NpeW86TbsicPgYOTRccA/640?wx_fmt=png)

> 先进的技术就是第一生产力，快手容器云平台拥抱 Dragonfly 和 Nydus 后，应用交付效率大幅提升，给业务创新带来了更多可能。
>
>                                                                                             ——孙寅，快手容器云负责人

由于拉取镜像是容器生命周期中比较耗时的步骤之一，为了进一步加速镜像分发和服务启动，工程师们又继续启用了 Nydus 镜像懒加载项目。快手有许多服务有数千个 Pod 实例，其中一些有超过 20G 或更大的镜像，当这些服务升级或扩容时，巨大的镜像和启动时间会严重减慢服务启动。快手需要一种能够显著提高服务启动速度的解决方案，特别是因为某些服务将其训练模型放入镜像中，这对于服务启动来说可能是灾难性的。

由于快手在 Dragonfly 项目上的应用和实施，工程师们很早就了解到 Nydus 项目。Nydus 是一个强大的开源文件系统解决方案，可以为云原生工作负载，例如容器镜像，构建高效的镜像分发系统。

得益于 Nydus 全新的镜像设计，每个 Pod 可以在几秒钟内完成启动，这样可以大量节省服务部署实例的启动时间，让应用尽快为用户提供服务。对于每个集群节点，支持Nydus的工作并不复杂，通过容器引擎无损切换（指无需 POD 驱逐）、配置变更即可顺利完成。

在实践中，Harbor 作为快手容器云平台的全局镜像仓库中心，仍然扮演着非常重要的角色，具体来说，我们做了以下事情：

1. 容器引擎从 Docker 无损切换到 containerd；
2. 在镜像构建阶段支持使用 Nydus 标准构建镜像；
3. 在集群节点间，使用 Dragonfly 的 P2P 技术支持镜像分发；
4. containerd通过配置Dragonfly 的 P2P 代理拉取镜像，并使用 Nydus 镜像启动容器。

当然，以上所有的变动，都继续兼容当前已有的 OCI 镜像格式以及系统已有功能。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0EtMUQLZicoiaf5Kvjng1m5ZSwF3Fl13CriaBHicB48bwxV8SzgbhYGOIeEYRwDC7M1UNiagGxK8eVjiblg/640?wx_fmt=png)

综上所述，Dragonfly 和 Nydus 一起为快手容器云平台提供了处理镜像分发问题的最佳解决方案。数以万计的快手服务大大减少了部署时间，业务线研发工程师在更新服务时也更加轻松容易。

Dragonfly 和 Nydus 都是来自 CNCF 的优秀开源项目，更进一步说，快手也将继续对该项目进行更多投入，并与社区展开深入合作，使它变得更加强大和可持续。云原生技术是基础设施领域的一场革命，尤其是在弹性和无服务器方面，我们相信 Dragonfly 一定会在云原生生态中扮演重要角色。

参考资料

1. https://www.cncf.io/case-studies/kuaishou-technology/
2. [https://mp.weixin.qq.com/s/YuNeVRHXxOFKE4vb8ODWnQ](https://mp.weixin.qq.com/s?__biz=MzI5ODk5ODI4Nw==&mid=2247529577&idx=1&sn=6763a27263e9ed6e692d6e94becdfe95&scene=21#wechat_redirect)
3. https://github.com/containerd/containerd
4. https://github.com/dragonflyoss/Dragonfly2
5. https://d7y.io/
6. https://github.com/dragonflyoss/image-service
7. https://nydus.dev/
8. https://github.com/goharbor/harbor