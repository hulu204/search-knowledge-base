---
title: '百度搜索exgraph图执行引擎设计与实践'
company: 百度
tag: 工程相关
date: 2024-01-09
url: https://juejin.cn/post/7321631687388430375
account: 
origin: harvest-202607
---
# 百度搜索exgraph图执行引擎设计与实践

[百度Geek说](/user/4186596000416094/posts)

2024-01-09
  
1,480
 
阅读11分钟

   

![公众号封面例图__2024-01-08+11_11_00.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/6a5197bbac7d422b896ec42f2c233efb~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=900&h=383&s=292705&e=png&b=e3e3e3)

作者 | 搜索Go研发组

> 导读
>
> 百度搜索exgraph图执行引擎设计重点分成三个部分：图描述语言、图执行引擎、对接扩展。
>
> 图描述语言是一种基于文本可读的图描述语言，用于描述任务中的算子以及算子之间的依赖关系，即让人可以理解，也可以被计算机理解并执行。
>
> 图执行引擎是exgraph的核心，负责根据图描述语言生成的图语法树进行高效执行。它支持如串行、并行、中断、选择等范式，以满足不同场景下的需求。
>
> 对接扩展则提供了与其他协议框架的接口，方便用户将exgraph集成到现有的系统中。
>
> 总之，exgraph图执行引擎设计的目标是实现高效、灵活的任务编排，以满足复杂逻辑处理需求。

> *全4430字，预计阅读时间12分钟。*

# **01 背景**

搜索展现架构承载模版选择、实时摘要补充、展现数据适配、结果渲染等职责，当前由PHP开发、HHVM执行，对接数十个产品线，数百个精细化的展现策略由100+RD共同开发。随着搜索业务产品日益复杂和生成式大模型产品开发需要，展现架构面临以下难题：

1、HHVM基础设施停止维护，且不支持异步并行支持，架构升级难度大；

2、历史累计的多个展现策略框架分布在各个阶段，且各自参数不同，研发难度大。

通过调研，了解到DAG有向无环图，将DAG图中顶点描述为业务拆分后的一个个算子，边及其方向作为执行顺序，一对一作为串行执行，一对多作为并发执行，即使是很复杂的业务也可以用这套逻辑进行表达。且代码实现较简单，还能用graphviz将DAG图生成图片，将整个逻辑可视化。

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8c653c9f9f23400e977d810723f3b249~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=1080&h=609&s=36327&e=png)

****△算子化后的逻辑执行视图****

好像很完美~~

但似乎还有些问题：

1、对于简单逻辑，DAG图不复杂，用graphviz构建图也很简单，但一旦顶点数量爆发，可阅读性急速下降。而不幸的是，搜索的PHP模块几百个策略，如果迁移进来，预计会有几百个顶点，构建这个图以及这个图的可读性，依然很差；

2、简单意味着功能弱。

* 比如搜索有多种版式：手百内、手百外、纯NA渲染等，下游顶点根据上游顶点的执行结果来选择不同的版式渲染。这种场景下只能呆呆的在每个版式顶点内自行判断是否执行，而不能由上游顶点直接选择一个版式分支执行。

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/1dc1c4d353dc4f93b1297269a46eb08b~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=1080&h=446&s=35663&e=png)

* 比如执行到某个顶点，发现后续不用执行了，逻辑执行没有好的退场机制。
* 各个算子间传递数据怎么处理。
* ...

# **02 图执行引擎**

DAG能满足大多数场景的需要，但依然不够。所以搜索设计了一套超集于DAG的图描述，并在这个描述上，添加逻辑执行的高级功能，与web框架进行融合，逐步诞生了exgraph图执行引擎。

exgraph图执行引擎设计重点分成两个三个部分：图描述语言、图执行引擎、对接扩展（用来对接协议框架）。

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/1cdb8951f4174263bcf0c3c3b647f885~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=905&h=767&s=32413&e=png)

## **2.1 图描述语言**

### **2.1.1 核心语法**

**算子**：业务执行的最小单位，通常一个单词就是一个算子（语法单独定义的关键词除外）。

**串行组**：即两个算子按照顺序执行，在图上表示为用箭头连接：

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/c35ea61ad68f41fd97a919bb808a1c2f~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=222&h=80&s=1109&e=png)

****△串行组****

**并发组**：即多个算子并发的执行，在图上用中括号﻿[]﻿包围：

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/7cac564e522b4a1daddde551323d9d50~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=314&h=110&s=1588&e=png)

**△并发组**

**属性**：图上所有用大括号﻿{}﻿包围的，都是属性。属性用于通过图描述传递参数给代码。

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/01cc98a6feb64fa5bc7ddca437dbd25e~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=764&h=96&s=5836&e=png)
**△属性**

**算子、串行组、并发组都是一个执行单元**，意味着，他们可以互相包含（算子是最小的执行单元，不能包含别的执行单元）。比如：

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/1cf0367fa16345a1960520e47cc63a11~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=1080&h=292&s=20304&e=png)

**△互相包含**

上面的这个描述，用人话说就是：

1、执行a算子

2、并发地：

* 执行b算子，
* 执行c算子，然后执行d算子，然后执行e算子
* 执行f算子，然后再并发地执行g算子和h算子

3、最后再执行i算子

**子图**：主图支持通过文件引入的方式，引入另一个图嵌入到主图

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/2b0a4ae02a9c407a977de75f13052dc0~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=1080&h=171&s=12261&e=png)

**△主图引入sub\_graph子图**

通过上面简单的介绍，你已经掌握几乎全部图描述语言语法了，可以开始思考，将自己所负责的业务如何用图进行描述了。

另外，为了更好的适配业务场景，exgraph还设计了几种指令来处理特殊场景。

#### **扩展指令**

**START指令**：图开始的标记，用做给图设置属性。

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/14c76cc38eec4befaac6ce848464fc27~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=724&h=290&s=9171&e=png)

****△START指令****

目前START指令用来指导创建HTTP的handler，直接让图引擎承接http处理、streaming rpc处理请求。

**MIDWARE指令**：包装含义。

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/1d58304ecea44dcfa6b989b91368a92a~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=538&h=94&s=3600&e=png)

**△MIDWARE指令**

可以在执行c算子前，先执行b算子，并控制是否执行c算子；也可以在执行c算子前后，执行一些通用的逻辑。

**SWITCH指令**：选择执行分支。

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/73eb80127f2d49bebb0ff00b0196089d~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=1080&h=250&s=25656&e=png)

**△SWITCH指令**

可以在﻿switch\_pc\_or\_wise﻿算子内，选择执行哪个分支。

基于图描述语言，用纯文本的方式就可以将业务整体描述，很好的解决了DAG图构图复杂性问题，并允许自定义一些高级用法。

## **2.2 图执行引擎**

上面介绍的图描述语言，让“人”可以更加简单的方式了解到程序的执行流程，但也仅仅只是个描述而已。

如何让其按照我们设定的描述将逻辑跑起来呢？

首先介绍一个重要的、执行单元必须实现的接口：

```
type Job interface{
    DoImpl(*engine.Context) error
}
```

其中\*Context负责传递所有信息到各个算子，提供：算子选项（算子{}附带的内容）内容获取、数据传递等功能。

在上面的章节中讲到**算子、串行组、并发组都是一个执行单元，其实就是说，它们都实现了Job接口**。

exgraph图执行引擎是：将图解析后的语法树作为入参，搭配全局算子注册，让算子按照预定的规则执行起来。

它的执行过程近似于：

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/5081d353663d4bc88405218b2c23b2f0~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=1080&h=164&s=14889&e=png)

em~~ 简单的有点像把大象放冰箱的过程，但实际远不止如此。

想一下，如果你执行到a算子，发现没有必要执行b算子了，怎么办？又或者a有数据要传递到b算子，怎么办？

### **2.2.1 对象容器**

exgraph中实现了一个并发安全的对象容器，用户可以通过\*engine.Context提供的接口，方便的设置和获取对象，就像这样：

```
type a struct {}

func (o *a) DoImpl(ctx *Context) error {
    // 算子a，设置对象
    var a int = 2023
    ctx.RegisterInstance(&a)
    return nil
}

type b struct {}

func (o *b) DoImpl(ctx *Context) error {
    var a int
     // 通过类型获取值
    ctx.MutableInstance(&a)
     // 打印2023
    fmt.Println(a)
    return nil
}
```

对象容器再存入时，将其类型作为标识符，取值时也通过相同类型的变量，通过反射赋值。

### **2.2.2 依赖注入和对象导出**

有了对象容器，exgraph设计了支持基于struct tag的对象依赖注入和导出功能，且采用脚本生成代码的方式实现：

```
type Operator struct {
    http.Request `inject:""`
    http.Response `inject:"canLost=true,canNil=true"`
    
    *Userinfo `extract:"canNil=true"`
}

type UserInfo struct {
    Name string
}

func (o *Operator) DoImpl(engine.Context) error {
    // 通过inject，算子内可以直接获取到Request对象
    if v, ok := o.Request.Header.Get("xx"); ok {
        // do something
    }
    
    return nil
}
```

利用struct tag和生成的代码，用户在使用算子时，实现了以下功能：

1、inject tag可以直接通过算子属性获取对象，省去了繁琐的取值过程，并支持：canLost=true表示允许对象不存在，canNil=true表示循序对象值为nil。

2、extract tag则允许用户直接赋值为算子属性，由生成的代码赋值将对象导出到对象容器中，且支持：canNil=true表示允许导出对象值为nil，repace=true表示允许替换对象。

### **2.2.3 中断和跳过**

为方便程序逻辑执行，exgraph内置了几种中断跳过逻辑：

**1、全局错误中断**

```
type a struct {}

func (o *a) DoImpl(ctx *Context) error {
    // 模拟业务执行遇到了不可兜底的错误
    err := errors.New("fatal error") 
     // 调用Abort函数即可中断整个图执行引擎
    ctx.Abort(err)
    return nil
}
```

**2、全局正常中断**

```
type a struct {}

func (o *a) DoImpl(ctx *Context) error {
    // 发现没必要走后面的逻辑
    // 直接中断整个图执行引擎
    ctx.Exit() 
    return nil
}
```

**3、跳过串行组**

```
type a struct {}

func (o *a) DoImpl (ctx *Context) error {
    // a算子执行跳过`a -> b`这个子集串行组
    // 即b算子不再执行，但c算子正常执行
    ctx.SkipSerialGroup() 
    return nil
}
```

**2.3 执行优化**

exgraph执行的一个声明周期内，大部分对象都允许池化。

### **2.3.1 对象池**

**对于算子**：exgraph内部对每个注册的算子，都是注册到一个sync.Pool中，算子对象在执行完成后，执行reset后返回到对象池内。

**对于放入对象容器的对象**：在exgraph执行引擎结束时，会循环对每个对象检测是否实现了Release接口，如果实现接口就会调用，用户就可以在Release时将对象reset后返回对象池内。

### **2.3.2 其他优化**

exgraph在执行每个算子时默认在当前goroutine执行，除非用户显示的给算子设置了超时时间a{timeout="1s"}。

依赖注入和对象导出，是基于脚本生成代码的，而非反射。

# **03 场景案例**

## **3.1 同路径不同逻辑**

**背景**：搜索PC和wise（移动端）同模块执行，检索路径都为/s

**方案**：可以用SWITCH选择模式，通过一个算子来判断使用哪个分支：

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/edcea59ad0f14a8881681f095863390f~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=1080&h=250&s=25656&e=png)

## **3.2 PHP策略迁移Go**

**背景**：搜索展现架构当前逐步由PHP迁移到Go。在过渡期，PHP代码迁移到Go之后，需要通过抽样验证Go代码逻辑无误，即：命中抽样，执行Go代码，否则执行PHP代码。而且需要迁移的PHP策略很多，如果没有统一的机制来支持，成本很高。

**方案**：用MIDWARE指令，用CommonDealPhpOrGoStrategy算子作为判断包装，判断命中抽样时，允许执行DemoStrategy1算子，并带标识到PHP，不执行PHP相应逻辑。

否则不执行DemoStrategy1而执行PHP相应逻辑。

关键的是，迁移后的Go算子都不需要做特殊处理，正常迁移代码加上MIDWARE就能支持以上功能。

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/16c884b96e1842aeb49328adacf696b7~tplv-k3u1fbpfcp-jj-mark:3024:0:0:0:q75.awebp#?w=1080&h=519&s=71626&e=png)

> 搜索技术平台研发部正在招募 AI 研发工程师，欢迎感兴趣的同学投递简历：
>
> [linzecheng@baidu.com](https://link.juejin.cn?target=mailto%3Alinzecheng%40baidu.com "mailto:linzecheng@baidu.com")

——END——

**推荐阅读**

[百度搜索&金融：构建高时效、高可用的分布式数据传输系统](https://link.juejin.cn?target=http%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247575843%26idx%3D1%26sn%3D52fc61ebc3de5d36c75061a6ca2f7dfe%26chksm%3Dc03f995ff74810492986bf919bbb764fee89153a04d5d6faa2a80aaa4a23a5d391403c01da6e%26scene%3D21%23wechat_redirect "http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247575843&idx=1&sn=52fc61ebc3de5d36c75061a6ca2f7dfe&chksm=c03f995ff74810492986bf919bbb764fee89153a04d5d6faa2a80aaa4a23a5d391403c01da6e&scene=21#wechat_redirect")

[“踩坑”经验分享：Swift语言落地实践](https://link.juejin.cn?target=http%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247575793%26idx%3D1%26sn%3Dfb9630ece7c3cd48bae3c29a49bdbc44%26chksm%3Dc03f988df748119b20f30ba8d64b35065949826ee823788530f97cb0b513bb80d0c4c9feb178%26scene%3D21%23wechat_redirect "http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247575793&idx=1&sn=fb9630ece7c3cd48bae3c29a49bdbc44&chksm=c03f988df748119b20f30ba8d64b35065949826ee823788530f97cb0b513bb80d0c4c9feb178&scene=21#wechat_redirect")

[移动端防截屏录屏技术在百度账户系统实践](https://link.juejin.cn?target=http%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247575653%26idx%3D1%26sn%3D07d5aa213569e00c8760165085ea814c%26chksm%3Dc03f9819f748110f2773accb08e9fd2fc92ad2cb0ce8c9c1e8bc3f15eee3d0d18ccf77eac129%26scene%3D21%23wechat_redirect "http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247575653&idx=1&sn=07d5aa213569e00c8760165085ea814c&chksm=c03f9819f748110f2773accb08e9fd2fc92ad2cb0ce8c9c1e8bc3f15eee3d0d18ccf77eac129&scene=21#wechat_redirect")

[AI Native工程化：百度App AI互动技术实践](https://link.juejin.cn?target=http%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247575380%26idx%3D1%26sn%3D4c1f508430f555a2527d7d89881a1c9c%26chksm%3Dc03f9728f7481e3ed3d7dab3713f3cd4856cd1021217e5236627c0b0f72f56ccc022ab1e960e%26scene%3D21%23wechat_redirect "http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247575380&idx=1&sn=4c1f508430f555a2527d7d89881a1c9c&chksm=c03f9728f7481e3ed3d7dab3713f3cd4856cd1021217e5236627c0b0f72f56ccc022ab1e960e&scene=21#wechat_redirect")

[揭开事件循环的神秘面纱](https://link.juejin.cn?target=http%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247575115%26idx%3D1%26sn%3D16ac22a935e00978af43e45ed75f1013%26chksm%3Dc03f9637f7481f213f18f38ed8eb4e727eb8fa65ae7a11665b42c3594f871fc314e18090894a%26scene%3D21%23wechat_redirect "http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247575115&idx=1&sn=16ac22a935e00978af43e45ed75f1013&chksm=c03f9637f7481f213f18f38ed8eb4e727eb8fa65ae7a11665b42c3594f871fc314e18090894a&scene=21#wechat_redirect")