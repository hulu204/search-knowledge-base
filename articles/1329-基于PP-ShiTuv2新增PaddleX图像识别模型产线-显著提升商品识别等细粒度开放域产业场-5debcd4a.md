---
title: '基于PP-ShiTuv2新增PaddleX图像识别模型产线，显著提升商品识别等细粒度开放域产业场景检索性能'
company: 百度
tag: 搜索
date: 2024-11-25
url: http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247602883&idx=1&sn=82f2944ccfc89eb9a8d7ef32af97b727&chksm=c03f62bff748eba983d5d256bf29b6b6cb9a0b03ceb4696351dfeebef2302e9493d2d4d1e7c3#rd
account: 百度Geek说
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_gif/5p8giadRibbOib5eKA9DvsnapbBokh883cWMjGKcouP64pz9gW7ayIktXwzlApWmhiawhw9RdHV0cHIv7ubnatc8lQ/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)点击蓝字，关注我们

![](https://mmbiz.qpic.cn/mmbiz_gif/5p8giadRibbOichNxgNgW2xyHYqnHnww2mnGT5PC84tpKOThGv2k88zXbdh8DTfA38RniadrhC3y4JagKaIEPTNPlQ/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

GEEK TALK

01

背景介绍

图像识别一直都是计算机视觉领域最基础的任务，也是生活中最为广泛应用的技术，从自动化身份核验中的人脸识别，到无人零售中的商品识别，其背后均有图像识别技术的应用，然而想要真正将技术落地应用却并不简单，虽然我们熟知的图像分类和目标检测一般认为属于图像识别范畴，但显然依赖单一技术难以解决实际应用中的问题：

* 当类别调整时，需要重新训练模型，对于类别需要频繁更新的场景，每次更新都重新训练模型显然是不切实际的；
* 很多场景要求细粒度识别，即不同类别特征差异较小，使用目标检测或是图像分类无法做到很好的区分，例如对于饮料商品，不同品牌的外观差异并不大；
* 深度模型训练依赖海量数据，数据集质量会严重影响模型性能，然而高质量数据集的制作成本不菲；
* 开放域目标检测技术依赖语义信息进行识别，因此类别的语言标注严重影响识别结果，例如商品识别中“尖叫”、“红牛”等标签，其语义信息和饮料图像特征并无明显关联；

针对上述问题，PaddleX 基于 PP-ShiTuV2**新增通用图像识别模型产线**，相较于单一的开放域目标检测模型展现出明显的效果优势。

GEEK TALK

02

算法解读

PP-ShiTuV2是一个实用的通用图像识别系统，主要由主体检测、图像特征和向量检索三个模块组成：

* **主体检测模块**：不同于一般的目标检测，主体检测只需将全部前景目标物体识别出来；
* **图像特征模块**：将主体检测模块识别得到的所有主体目标，通过深度学习模型提取得到对应的特征向量；
* **向量检索模块**：计算特征向量和特征底库的相似度，从而得到对应目标的预测类别；

![](https://mmbiz.qpic.cn/sz_mmbiz_png/TQX7ER5HdB234iaymwPia3eSQ4x4gQUBGREAgAVCer9B3TGL11t8XKejSyYSNCKbSxnickLcEg6dTBQV30FFd1wEg/640?wx_fmt=png&from=appmsg)

## ***△PP-ShiTu***

其中，图像特征模块的性能对于最终的识别效果至关重要，因为检索结果很大程度上依赖于特征向量的质量。通过深度学习方法，图像特征模块能够自动从图像数据中提取关键特征，这些特征以向量形式表示，能够高效捕捉图像的核心信息，从而为后续的检索任务提供有力支持。基于此，PaddleX 集成了两个服务端图像特征模型：**PP-ShiTuV2\_rec\_CLIP\_vit\_base 和 PP-ShiTuV2\_rec\_CLIP\_vit\_large**，两个模型均采用 CLIP\_vit 作为骨干网络，进一步提升了特征提取模块的性能：在 AliProducts 数据集上，其 recall@1指标最高可达**91.03%**，在内部私有开放域评测集上相较于 PP-ShiTuV2\_rec 模型**提升了超过20个百分点**。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/TQX7ER5HdB234iaymwPia3eSQ4x4gQUBGRuP8bVo1jibTCK4IjJ8y1L1OyKSliayk4sq3O32FRjOFFxdCar5eib0TQg/640?wx_fmt=png&from=appmsg)

**注**：以上精度指标为 AliProducts recall@1。所有模型 GPU 推理耗时基于 NVIDIA Tesla T4机器，精度类型为 FP32，CPU 推理速度基于 Intel(R) Xeon(R) Gold 5117 CPU @ 2.00GHz，线程数为8，精度类型为 FP32。

该系统从骨干网络选择和调整、损失函数的选择、数据增强、学习率变换策略、正则化参数选择、预训练模型使用以及模型裁剪量化多个方面，融合改进多种策略，对各个模块进行优化，最终在多个实际应用场景上的检索性能均有较好效果，且在处理商品等细粒度开放域场景时，PP-ShiTuV2相较于单一的开放域目标检测模型展现出明显优势。以下是 PP-ShiTuV2与 Grounding DINO 模型的识别效果对比。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/TQX7ER5HdB234iaymwPia3eSQ4x4gQUBGR5pGjcVGfUoz2Kib2fgictAPKlfmwHQzO5Kp9UkbQsdb5seqia9aVCmEQQ/640?wx_fmt=png&from=appmsg)

Grounding DINO 模型识别白酒品牌

![](https://mmbiz.qpic.cn/sz_mmbiz_png/TQX7ER5HdB234iaymwPia3eSQ4x4gQUBGRSZLgLOZt5g3skcryR8f6TMZ26RSEoV1VfqeciaYOSZ1qZsSCAVddmfg/640?wx_fmt=png&from=appmsg)

PP-ShiTuV2识别白酒品牌

滑动查看更多

![](https://mmbiz.qpic.cn/sz_mmbiz_png/TQX7ER5HdB234iaymwPia3eSQ4x4gQUBGR911liaVnmFpvmBO5DeGJz2ryOiaXScqP3xN8Yibic8fJsqOatUXvXQa33g/640?wx_fmt=png&from=appmsg)

Grounding DINO 模型识别饮料品牌

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/TQX7ER5HdB234iaymwPia3eSQ4x4gQUBGRt2czSiaMNBdvlulCNff4EmOeSE2iclibnXRUyWm3wX0SwSVUVC3pVwLhQ/640?wx_fmt=jpeg&from=appmsg)

PP-ShiTuV2识别饮料品牌

滑动查看更多

GEEK TALK

03

使用方法

下面就从零开始，使用 PaddleX 体验通用图像识别系统 PP-ShiTuV2：

**3.1 安装**

根据设备选择安装 PaddlePaddle

```
# cpupython -m pip install paddlepaddle==3.0.0b2 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/# gpu，该命令仅适用于 CUDA 版本为 11.8 的机器环境python -m pip install paddlepaddle-gpu==3.0.0b2 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/# gpu，该命令仅适用于 CUDA 版本为 12.3 的机器环境python -m pip install paddlepaddle-gpu==3.0.0b2 -i https://www.paddlepaddle.org.cn/packages/stable/cu123/
```

安装 PaddleX

```
pip install https://paddle-model-ecology.bj.bcebos.com/paddlex/whl/paddlex-3.0.0b2-py3-none-any.whl
```

**3.2 快速体验**

PaddleX 提供了简单易用的 Python API，只需几行代码即可体验端到端预测效果，在 PP-ShiTuV2的运行示例中需要预先构建索引库，您可以下载官方提供的饮料识别测试数据集，方便大家快速体验效果：

**饮料识别测试数据集：**

*https://paddle-model-ecology.bj.bcebos.com/paddlex/data/drink\_dataset\_v2.0.tar*

```
from paddlex import create_pipeline  
pipeline = create_pipeline(pipeline="PP-ShiTuV2")index_data = pipeline.build_index("drink_dataset_v2.0/", "drink_dataset_v2.0/gallery.txt")output = pipeline.predict("./drink_dataset_v2.0/test_images/", index=index_data)for res in output:    res.print()    res.save_to_img("./output/")
```

上述代码中：

* 首先使用产线名称调用 **create\_pipeline()**方法实例化产线对象；
* 然后调用 **build\_index()**方法构建特征向量库；
* 最后即可使用 **predict()**方法进行预测，对于预测结果支持 **print()**方法进行打印，以及 **save\_to\_img()**方法进行可视化并保存为图片。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/TQX7ER5HdB234iaymwPia3eSQ4x4gQUBGRrvIq1EL1F73v7SY90E2hIuU8yenoUDgTbac6bibJiafOBXhHBZkETBog/640?wx_fmt=png&from=appmsg)

## **△**PP-ShiTuV2预测可视化效果图

![](https://mmbiz.qpic.cn/sz_mmbiz_png/TQX7ER5HdB234iaymwPia3eSQ4x4gQUBGRG4iaIK6Cibr7ocExCkZEXMafbByFICwY2ClaUwCTVjaEtaIsfBibHUPUA/640?wx_fmt=png&from=appmsg)

## **△**PP-ShiTuV2预测可视化效果图

**3.3 二次开发**

如果对产线的预训练模型效果满意，可以直接对产线进行**高性能推理/服务化部署/端侧部署**，如果不满意，您也可以使用 PaddleX 进行便捷高效的**二次开发**，使用自己场景的数据对模型微调训练获得更优的精度。

基于 PaddleX 便捷的二次开发能力，使用统一命令即可完成数据校验、模型训练与评估推理，无需了解深度学习的底层原理，按要求准备好场景数据，简单运行命令即可完成模型迭代，此处以图像特征模块的模型训练为例：

```
python main.py -c paddlex/configs/general_recognition/PP-ShiTuV2_rec.yaml \    -o Global.mode=train \    -o Global.dataset_dir=./dataset/Inshop_examples
```

上述命令中，首先指定所用模型的配置文件（此处为 **PP-ShiTuV2\_rec.yaml**），然后选择模式为模型训练：**-o Global.mode=train**，再指定数据集路径：**-o Global.dataset\_dir** 即可。

更多参数也可以继续在命令中追加参数设置：如指定前2卡 gpu 训练：**-o Global.device=gpu:0,1**；设置训练轮次数为10：**-o Train.epochs\_iters=10**。此外，相关参数均可通过修改**.y****aml**配置文件中的 **Global**和 **Train**的具体字段来进行设置。

END

**推荐阅读**

[基于GPU的ANN检索](http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247602855&idx=1&sn=6d0f69509b036f181f299de13f0ea00e&chksm=c03f62dbf748ebcde68514c4674d7e288fe5f4e048baf0b4f7c46db497cdafc0c80931367053&scene=21#wechat_redirect)

[维度爆炸背景下uv计算在Feed业务的高效实践](http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247601927&idx=1&sn=c2303fb7cff50c4d1384fc7656a087cc&chksm=c03f7f7bf748f66da15fe82ccfc08f59f7b9779a9cf96abbf65fd208eed61affe7e3e20068b0&scene=21#wechat_redirect)

[数据湖系列之四  | 数据湖存储加速方案的发展和对比分析](http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247601872&idx=1&sn=73ec6487a1b0a4fa4f23f9faa5ffa25a&chksm=c03f7eacf748f7ba347d30fe38f24f22aade645250f19c1c2d16f800db3ea52097390afb1440&scene=21#wechat_redirect)

[大模型时代，云原生数据底座的创新和实践](http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247601863&idx=1&sn=aebae9a8e3371947f764612a564172d2&chksm=c03f7ebbf748f7ad716977f4f02bf1d8e3b2160be40d3046ac4355bbd6513eb4f9ebcf5d64b4&scene=21#wechat_redirect)

[百度沧海·存储统一技术底座架构演进](http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247601854&idx=1&sn=48b60faa00eae43492615d67c56a74f9&chksm=c03f7ec2f748f7d4cfb2e6fb9cd7b71e83760e82954af11ee38bd0ef64dd2e1ee49bd2d8d956&scene=21#wechat_redirect)

![](https://mmbiz.qpic.cn/mmbiz_png/5p8giadRibbO9x9T3iaxknhz6B4v4PPxvGEAlXibefUzgTftSnnT6QficHvz0w4T1CtHpDD8ZDU7NiaAjkHFssZN9IYA/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

一键三连，好运连连，bug不见👇