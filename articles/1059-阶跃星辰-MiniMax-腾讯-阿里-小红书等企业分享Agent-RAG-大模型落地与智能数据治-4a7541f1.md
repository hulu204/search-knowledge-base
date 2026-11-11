---
title: '阶跃星辰、MiniMax、腾讯、阿里、小红书等企业分享Agent、RAG、大模型落地与智能数据治理技术实践'
company: DataFun
tag: 问答/RAG
date: 2025-03-20
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247763204&idx=3&sn=967f81944a74807c427f058aed635a8b&chksm=fbdb7768ccacfe7ec815d8bef6ebc027de6414d7355116edddcf8fdb154837409226371c6924#rd
account: DataFunTalk
origin: wechat-mp
---
大模型从技术到实际应用之间仍存在一定的距离，这一距离正是通过RAG和Agent技术来弥合，这不仅解决了大模型落地的“最后一公里”问题，还为多Agent协同、智能数据治理、金融风控、运维自动化等领域提供了新的解决方案。

DataFun正在筹备**2025年4月25-26日DA数智技术大会（上海站）**，在会议筹备期，我们访谈了多位业界技术专家，请他们从技术和实践视角提供了自己的见解。本文整理了访谈内容，探讨这些技术的实践与应用，分析其在不同场景中的优势与挑战，并展望未来的发展方向。通过实际案例和技术解析，我们将揭示大模型如何在实际业务中发挥作用，以及如何通过智能数据治理和Agent协同来提升模型的准确性和可靠性。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjHZYkQ7McPsZ2Tntmic5xH0AfgA4lUXM4DzRaVPPHsw93liaaA6R8Lyup6qP7ZIHzHfGpR3YvO4j2w/640?wx_fmt=jpeg&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/ic71wVtGetfHDu1wydMskOKuoXicunjouOlWhIdKVhicUw0VEEUibaahW73bFBktvxRUb7w5A9GS4POh7uqoAm4I8w/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/Bd7jlAWL2kJb0ad17GyZNCYMgklIXicN3a4gtzIPibVdu0k3QMYmTqXZcJbzKN4BCUdoPTPfNvEyOenQmWShIKUw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/EeJSAMoAk9AaZBDONXq5mr1CnahhdFPRnN7Zk7c1R8mNJb1T2PCGUYiatym44rUOVbxzCHRByoeKaqz0Eh6o3ng/640?wx_fmt=png)

最新直播推荐

![](https://mmbiz.qpic.cn/mmbiz_png/cZBtichFtVOicw0ecmyjicxsyvdEtIDcDaN5EoEiaejwr3qhO8FFapczeI7LbibJlGTxgjQIm6Avy8ISPuEPI6yus7Q/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/3QTIKn9jFuMib8ic1Qldejuib3qXtTqDpDTRq0ciaZRBbE4WGzg7K2FvVhaIJ4HM6gs06qqYzoiaz22FEF38R0Ozr8A/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/3AJf6zpEXO8e3OMs0hVse7E8dySmiaRe5p5vExYnzKGdUV6pMv9VmicM0ib4QIUj08lGtiaQp2dXbSn2coO8mK4yBg/640?wx_fmt=png)

## 

🔥Manus 之后，Agent 将去往何处？

3月25日19:30-20:30，多位 Agent 领域知名技术专家在线深度探讨！

点击「预约」直播，一同解锁 Manus 之后的 Agent 技术格局和未来前景 ~

![](https://mmbiz.qpic.cn/mmbiz_png/ic71wVtGetfHDu1wydMskOKuoXicunjouOlWhIdKVhicUw0VEEUibaahW73bFBktvxRUb7w5A9GS4POh7uqoAm4I8w/640)

![](https://mmbiz.qpic.cn/mmbiz_png/Bd7jlAWL2kJb0ad17GyZNCYMgklIXicN3a4gtzIPibVdu0k3QMYmTqXZcJbzKN4BCUdoPTPfNvEyOenQmWShIKUw/640)

![](https://mmbiz.qpic.cn/mmbiz_png/EeJSAMoAk9AaZBDONXq5mr1CnahhdFPRnN7Zk7c1R8mNJb1T2PCGUYiatym44rUOVbxzCHRByoeKaqz0Eh6o3ng/640)

大模型落地的核心挑战与关键技术

![](https://mmbiz.qpic.cn/mmbiz_png/cZBtichFtVOicw0ecmyjicxsyvdEtIDcDaN5EoEiaejwr3qhO8FFapczeI7LbibJlGTxgjQIm6Avy8ISPuEPI6yus7Q/640)

![](https://mmbiz.qpic.cn/mmbiz_png/3QTIKn9jFuMib8ic1Qldejuib3qXtTqDpDTRq0ciaZRBbE4WGzg7K2FvVhaIJ4HM6gs06qqYzoiaz22FEF38R0Ozr8A/640)

![](https://mmbiz.qpic.cn/mmbiz_png/3AJf6zpEXO8e3OMs0hVse7E8dySmiaRe5p5vExYnzKGdUV6pMv9VmicM0ib4QIUj08lGtiaQp2dXbSn2coO8mK4yBg/640)

大模型从技术到应用的落地并非一蹴而就，RAG和Agent的结合成为解决这一问题的核心。RAG通过增强检索能力，弥补了大模型在直接解决应用问题时的不足，而Agent则通过模拟人类行为，完成从输入到输出的具体任务。例如，在运维领域，Agent可以根据告警输入生成相应的操作指令，而多Agent协同则进一步提升了任务的准确性和可靠性。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjHZYkQ7McPsZ2Tntmic5xH0V3SbkjPBHaeX0zLIJnicKIZJOkWxzWLPia2M7lxLHgia9wsEcDGoA5jUA/640?wx_fmt=png&from=appmsg)

Agent不仅仅是对话机器人，它还应具备知识库、行动能力等核心组件。在复杂场景中，多Agent协同成为趋势。例如，在运维领域，多个Agent可以从不同角度分析问题，并通过协同决策降低错误率。未来，多Agent协同将成为大模型落地的重要方向，尤其是在需要高精度和复杂逻辑的场景中。

![](https://mmbiz.qpic.cn/mmbiz_png/ic71wVtGetfHDu1wydMskOKuoXicunjouOlWhIdKVhicUw0VEEUibaahW73bFBktvxRUb7w5A9GS4POh7uqoAm4I8w/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/Bd7jlAWL2kJb0ad17GyZNCYMgklIXicN3a4gtzIPibVdu0k3QMYmTqXZcJbzKN4BCUdoPTPfNvEyOenQmWShIKUw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/EeJSAMoAk9AaZBDONXq5mr1CnahhdFPRnN7Zk7c1R8mNJb1T2PCGUYiatym44rUOVbxzCHRByoeKaqz0Eh6o3ng/640?wx_fmt=png)

大模型在运维领域的实践

![](https://mmbiz.qpic.cn/mmbiz_png/cZBtichFtVOicw0ecmyjicxsyvdEtIDcDaN5EoEiaejwr3qhO8FFapczeI7LbibJlGTxgjQIm6Avy8ISPuEPI6yus7Q/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/3QTIKn9jFuMib8ic1Qldejuib3qXtTqDpDTRq0ciaZRBbE4WGzg7K2FvVhaIJ4HM6gs06qqYzoiaz22FEF38R0Ozr8A/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/3AJf6zpEXO8e3OMs0hVse7E8dySmiaRe5p5vExYnzKGdUV6pMv9VmicM0ib4QIUj08lGtiaQp2dXbSn2coO8mK4yBg/640?wx_fmt=png)

运维领域是大模型落地的重要场景之一。大型企业通常需要维护数万台数据库或数据节点，运维复杂度极高。传统的运维方式依赖人工经验，容易出错且效率低下。大模型通过Agent实现自动化前后检查和回退操作，减少人工干预，降低操作风险。

例如，在变更操作中，Agent负责检查节点状态和备份，操作人员只需关注核心变更步骤。这种方式不仅提升了效率，还显著降低了人为错误的风险。此外，多Agent协同在运维中的应用也取得了显著成效。通过多个Agent从不同角度生成答案，并由总Agent进行分析，最终选择多数一致的答案作为正确输出。这种方式有效解决了大模型的幻觉问题，提升了模型的可靠性。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjHZYkQ7McPsZ2Tntmic5xH03Q0Eiamu8sYsFWLtQYYc1aEfopxyWjBaTUmIyQiavZfzfIRWFvtCdDXA/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/ic71wVtGetfHDu1wydMskOKuoXicunjouOlWhIdKVhicUw0VEEUibaahW73bFBktvxRUb7w5A9GS4POh7uqoAm4I8w/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/Bd7jlAWL2kJb0ad17GyZNCYMgklIXicN3a4gtzIPibVdu0k3QMYmTqXZcJbzKN4BCUdoPTPfNvEyOenQmWShIKUw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/EeJSAMoAk9AaZBDONXq5mr1CnahhdFPRnN7Zk7c1R8mNJb1T2PCGUYiatym44rUOVbxzCHRByoeKaqz0Eh6o3ng/640?wx_fmt=png)

大模型在金融领域的应用

![](https://mmbiz.qpic.cn/mmbiz_png/cZBtichFtVOicw0ecmyjicxsyvdEtIDcDaN5EoEiaejwr3qhO8FFapczeI7LbibJlGTxgjQIm6Avy8ISPuEPI6yus7Q/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/3QTIKn9jFuMib8ic1Qldejuib3qXtTqDpDTRq0ciaZRBbE4WGzg7K2FvVhaIJ4HM6gs06qqYzoiaz22FEF38R0Ozr8A/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/3AJf6zpEXO8e3OMs0hVse7E8dySmiaRe5p5vExYnzKGdUV6pMv9VmicM0ib4QIUj08lGtiaQp2dXbSn2coO8mK4yBg/640?wx_fmt=png)

金融领域是大模型落地的另一个重要方向。在运营方面，大模型主要用于智能客服等辅助场景，提升客户问答效率。这类应用不涉及核心业务流程，安全性较高。而在智能投顾领域，大模型则面临合规风险。例如，银行在提供智能投顾服务时，需要确保相关人员持牌并具备专业背景。大模型在推荐产品时，更多承担营销功能，实际购买环节仍需人工介入。

风控是大模型在金融领域的核心应用之一。尽管模型存在幻觉或不准确性，但其能够通过概率分析识别风险，辅助人工审核。风控大模型还解决了专业人才匮乏的问题，使更多企业能够开展金融业务。例如，一些缺乏金融基因的公司可以通过风控大模型快速建立专业的风控流程，降低运营成本。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjHZYkQ7McPsZ2Tntmic5xH0yM64vicIicUz7eHIUjcCeurHe3Rw4daKmZpbGLnbLfSgorgtl1IHvNDw/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/ic71wVtGetfHDu1wydMskOKuoXicunjouOlWhIdKVhicUw0VEEUibaahW73bFBktvxRUb7w5A9GS4POh7uqoAm4I8w/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/Bd7jlAWL2kJb0ad17GyZNCYMgklIXicN3a4gtzIPibVdu0k3QMYmTqXZcJbzKN4BCUdoPTPfNvEyOenQmWShIKUw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/EeJSAMoAk9AaZBDONXq5mr1CnahhdFPRnN7Zk7c1R8mNJb1T2PCGUYiatym44rUOVbxzCHRByoeKaqz0Eh6o3ng/640?wx_fmt=png)

智能数据治理与大模型

![](https://mmbiz.qpic.cn/mmbiz_png/cZBtichFtVOicw0ecmyjicxsyvdEtIDcDaN5EoEiaejwr3qhO8FFapczeI7LbibJlGTxgjQIm6Avy8ISPuEPI6yus7Q/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/3QTIKn9jFuMib8ic1Qldejuib3qXtTqDpDTRq0ciaZRBbE4WGzg7K2FvVhaIJ4HM6gs06qqYzoiaz22FEF38R0Ozr8A/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/3AJf6zpEXO8e3OMs0hVse7E8dySmiaRe5p5vExYnzKGdUV6pMv9VmicM0ib4QIUj08lGtiaQp2dXbSn2coO8mK4yBg/640?wx_fmt=png)

智能数据治理是大模型应用的另一个重要领域。数据治理的核心问题包括数据安全、合规性以及数据在不同场景中的应用。RAG技术在非结构化数据（如文档）检索中表现优异，但在结构化数据检索中仍需优化。

尽管预训练数据集建设需求减少，但微调和RAG仍需要高质量数据集。数据治理的自动化是大模型的重要应用方向。例如，在数据搬迁过程中，大模型可以自动化完成数据校验和鉴证，提升效率并降低人力成本。此外，数据伦理和安全合规也是智能数据治理需要重点关注的问题。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjHZYkQ7McPsZ2Tntmic5xH05AbmRpI45iatiatjoDrwuNNsOVpEJrISazdga22wDJyw7tBID9EoCynw/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/ic71wVtGetfHDu1wydMskOKuoXicunjouOlWhIdKVhicUw0VEEUibaahW73bFBktvxRUb7w5A9GS4POh7uqoAm4I8w/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/Bd7jlAWL2kJb0ad17GyZNCYMgklIXicN3a4gtzIPibVdu0k3QMYmTqXZcJbzKN4BCUdoPTPfNvEyOenQmWShIKUw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/EeJSAMoAk9AaZBDONXq5mr1CnahhdFPRnN7Zk7c1R8mNJb1T2PCGUYiatym44rUOVbxzCHRByoeKaqz0Eh6o3ng/640?wx_fmt=png)

大模型与数据库国产化

![](https://mmbiz.qpic.cn/mmbiz_png/cZBtichFtVOicw0ecmyjicxsyvdEtIDcDaN5EoEiaejwr3qhO8FFapczeI7LbibJlGTxgjQIm6Avy8ISPuEPI6yus7Q/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/3QTIKn9jFuMib8ic1Qldejuib3qXtTqDpDTRq0ciaZRBbE4WGzg7K2FvVhaIJ4HM6gs06qqYzoiaz22FEF38R0Ozr8A/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/3AJf6zpEXO8e3OMs0hVse7E8dySmiaRe5p5vExYnzKGdUV6pMv9VmicM0ib4QIUj08lGtiaQp2dXbSn2coO8mK4yBg/640?wx_fmt=png)

数据库国产化是当前的重要战略需求，涉及金融、互联网等多个领域。大模型技术在数据库国产化过程中发挥重要作用。例如，在数据搬迁和校验中，大模型可以实现自动化处理，显著降低人力成本。

数据安全是国产化过程中的核心问题。大模型通过自动化校验和鉴证，能够提升数据搬迁的安全性和效率，同时降低潜在风险。例如，传统的数据校验工作通常依赖人工完成，效率低下且容易出错，而大模型可以通过自动化流程显著提升效率和准确性。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjHZYkQ7McPsZ2Tntmic5xH0RnqTF0ico0cedTQwuwnOhYuDTDicicHtbeNvtAoficYDKMjFEwLjm8gibBg/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/ic71wVtGetfHDu1wydMskOKuoXicunjouOlWhIdKVhicUw0VEEUibaahW73bFBktvxRUb7w5A9GS4POh7uqoAm4I8w/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/Bd7jlAWL2kJb0ad17GyZNCYMgklIXicN3a4gtzIPibVdu0k3QMYmTqXZcJbzKN4BCUdoPTPfNvEyOenQmWShIKUw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/EeJSAMoAk9AaZBDONXq5mr1CnahhdFPRnN7Zk7c1R8mNJb1T2PCGUYiatym44rUOVbxzCHRByoeKaqz0Eh6o3ng/640?wx_fmt=png)

端侧模型与推理加速

![](https://mmbiz.qpic.cn/mmbiz_png/cZBtichFtVOicw0ecmyjicxsyvdEtIDcDaN5EoEiaejwr3qhO8FFapczeI7LbibJlGTxgjQIm6Avy8ISPuEPI6yus7Q/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/3QTIKn9jFuMib8ic1Qldejuib3qXtTqDpDTRq0ciaZRBbE4WGzg7K2FvVhaIJ4HM6gs06qqYzoiaz22FEF38R0Ozr8A/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/3AJf6zpEXO8e3OMs0hVse7E8dySmiaRe5p5vExYnzKGdUV6pMv9VmicM0ib4QIUj08lGtiaQp2dXbSn2coO8mK4yBg/640?wx_fmt=png)

端侧模型主要应用于手机、PC等客户端，模型规模较小，能够在本地完成推理任务，无需依赖外部网络。这种方式解决了网络延迟和设备资源占用问题，适合C端大规模应用。

然而，端侧模型并未直接解决大模型落地的挑战。云端推理加速则通过降低成本和提升效率，支持大规模应用场景。例如，在金融、运维等领域，云端推理加速能够显著降低计算资源成本，提升模型响应速度。端侧和云端的结合为大模型的广泛应用提供了更多可能性。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjHZYkQ7McPsZ2Tntmic5xH0wvSCJcN96fzgh9N8OMktBNOAic9M1BYkQQAppztMVyOkhJRhEMMou9g/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/ic71wVtGetfHDu1wydMskOKuoXicunjouOlWhIdKVhicUw0VEEUibaahW73bFBktvxRUb7w5A9GS4POh7uqoAm4I8w/640)

![](https://mmbiz.qpic.cn/mmbiz_png/Bd7jlAWL2kJb0ad17GyZNCYMgklIXicN3a4gtzIPibVdu0k3QMYmTqXZcJbzKN4BCUdoPTPfNvEyOenQmWShIKUw/640)

![](https://mmbiz.qpic.cn/mmbiz_png/EeJSAMoAk9AaZBDONXq5mr1CnahhdFPRnN7Zk7c1R8mNJb1T2PCGUYiatym44rUOVbxzCHRByoeKaqz0Eh6o3ng/640)

大模型的智能应用探索

![](https://mmbiz.qpic.cn/mmbiz_png/cZBtichFtVOicw0ecmyjicxsyvdEtIDcDaN5EoEiaejwr3qhO8FFapczeI7LbibJlGTxgjQIm6Avy8ISPuEPI6yus7Q/640)

![](https://mmbiz.qpic.cn/mmbiz_png/3QTIKn9jFuMib8ic1Qldejuib3qXtTqDpDTRq0ciaZRBbE4WGzg7K2FvVhaIJ4HM6gs06qqYzoiaz22FEF38R0Ozr8A/640)

![](https://mmbiz.qpic.cn/mmbiz_png/3AJf6zpEXO8e3OMs0hVse7E8dySmiaRe5p5vExYnzKGdUV6pMv9VmicM0ib4QIUj08lGtiaQp2dXbSn2coO8mK4yBg/640)

大模型在智能应用领域的探索也取得了显著进展。例如，在自动化办公场景中，大模型可以通过分析邮件和内部沟通记录，自动生成高质量周报，显著提升工作效率。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjHZYkQ7McPsZ2Tntmic5xH0GB03eSnRNDh0obOw9fj6mdaBLqFXBVnz9A7ibrX9v7HS3b6icGvdtr4Q/640?wx_fmt=png&from=appmsg)

在智能产品开发方面，大模型也展现出巨大潜力。例如，在旅行场景中，大模型能够根据目的地天气和用户偏好，提供出行穿着建议和酒店预订服务。这些应用虽然仍处于萌芽期，但为解决传统问题提供了新思路。未来，随着技术的不断优化，大模型将在更多领域发挥其价值。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjHZYkQ7McPsZ2Tntmic5xH017ialUUV4X89lMP82Ew5lwsPrlpib26Jy6nOib4vgibhvlbogjfFQ6KGdQ/640?wx_fmt=png&from=appmsg)

大模型技术在实际应用中的落地仍面临诸多挑战，但通过RAG、Agent、多Agent协同等技术的结合，其在运维、金融、数据治理等领域的应用已初见成效。未来，随着技术的不断优化和应用场景的拓展，大模型将在更多领域发挥其价值，推动智能化转型的深入发展。无论是提升运维效率、优化金融风控，还是实现数据治理的自动化，大模型都展现出了巨大的潜力。尽管目前仍处于探索阶段，但其未来的发展前景令人期待。

![](https://mmbiz.qpic.cn/mmbiz_png/ic71wVtGetfHDu1wydMskOKuoXicunjouOlWhIdKVhicUw0VEEUibaahW73bFBktvxRUb7w5A9GS4POh7uqoAm4I8w/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/Bd7jlAWL2kJb0ad17GyZNCYMgklIXicN3a4gtzIPibVdu0k3QMYmTqXZcJbzKN4BCUdoPTPfNvEyOenQmWShIKUw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/EeJSAMoAk9AaZBDONXq5mr1CnahhdFPRnN7Zk7c1R8mNJb1T2PCGUYiatym44rUOVbxzCHRByoeKaqz0Eh6o3ng/640?wx_fmt=png)

优惠购票

![](https://mmbiz.qpic.cn/mmbiz_png/cZBtichFtVOicw0ecmyjicxsyvdEtIDcDaN5EoEiaejwr3qhO8FFapczeI7LbibJlGTxgjQIm6Avy8ISPuEPI6yus7Q/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/3QTIKn9jFuMib8ic1Qldejuib3qXtTqDpDTRq0ciaZRBbE4WGzg7K2FvVhaIJ4HM6gs06qqYzoiaz22FEF38R0Ozr8A/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/3AJf6zpEXO8e3OMs0hVse7E8dySmiaRe5p5vExYnzKGdUV6pMv9VmicM0ib4QIUj08lGtiaQp2dXbSn2coO8mK4yBg/640?wx_fmt=png)

**9 折优惠购票，火热进行中。**

超值福利二选一，买就送 DA 数智大会2024·上海站视频回放或 DataFun 线上学习会员季卡 1 张/人，数量有限，先到先得！

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhgFCp3FPPPy0jt1BtY2VfqL4nRP3ndJEMtoM3y8abc3v3L3jkEZkOjJfHgsiaZjFEUwyjZw7t6v3A/640?wx_fmt=png&from=appmsg)

如有购票意向，可咨询DA大会福利官（电话/微信 13311343487）了解详情。

如对会议赞助方案、成为演讲嘉宾感兴趣，也可以微信添加 Alice（15650753618），了解详细内容。

点击**「阅读原文」**即可查看大会官网及最新议题信息。