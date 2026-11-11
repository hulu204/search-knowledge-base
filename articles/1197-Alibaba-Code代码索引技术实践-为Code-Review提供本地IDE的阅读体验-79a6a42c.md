---
title: 'Alibaba Code代码索引技术实践：为Code Review提供本地IDE的阅读体验'
company: 阿里
tag: 索引构建
date: 2022-06-14
url: http://mp.weixin.qq.com/s?__biz=Mzg4NTczNzg2OA==&mid=2247484885&idx=1&sn=1bf4d05edd4b09deeb983849780465f1&chksm=cfa51536f8d29c2070685f04176e6cbc3f862da420df0ee6c9240d83c2d23df0f290272ef55d#rd
account: 阿里技术
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hlia35Pshyp9oo1icQYDXaw16C573TLOhGDNiczuD57zrd0thxMibfZCJBPBY3ctoyKLiaV0vTs9r64yQ/640?wx_fmt=png)

这是阿里技术2022年的第19篇原创文章

（ 作者：李峥峰(曲径)   本文阅读时间：20分钟 ）

Code Review在研发流程中非常重要，但Web界面中Code Intelligence能力的缺失改变了原有的代码阅读习惯，又增加了阅读成本。本文将介绍阿里代码索引技术如何在提高阅读体验的同时兼顾精准性和性能。

Code Review是研发流程中非常重要的一个环节，无论是对于工程师成长还是对于工程质量的提升都是非常有益的。工程师之间通过Code Review对代码设计、实现、规范相关的讨论和交流，促进相互学习和成长。**坚持高标准的Code Review，也是追求卓越工程的有效手段。**

据统计，研发同学每天都会花大量时间从本地IDE转战到Web界面进行Code Review，但Web界面缺失了很多本地IDE的Code Intelligence能力，这从根本上改变了研发工程师的心理，既改变了原有的代码阅读习惯，又增加了阅读成本。为了提升研发工程师的阅读体验，我们打造了本地IDE般精准的Web-Based代码智能服务。

Alibaba Code是阿里巴巴内部的代码托管及价值衍生平台，旨在提供代码托管、浏览、历史追溯、Issues、Code Review、全局搜索、持续集成、Wiki、代码扫描、可视化报表、Code Compare等智能化的在线服务。本文以此为例，分享了阿里集团内部的代码智能化技术实践，我们还在持续优化，以此应对未来更大规模的研发挑战。

**01**

**实际效果**

下图中演示的是无容器版本的Web  IDE能力。传统容器版本的Web IDE存在**打开需等待、加载时间长**的缺点，而我们通过静态索引预热技术实现了实时计算提供服务、开箱即用，目前已经在集团内部提供百亿数量级的索引服务。

![](https://mmbiz.qpic.cn/mmbiz_gif/OmCbZ5JK30GtxBAR7EIGIqczTIHTtOFJNzekNDxENbzRmV7aye2qFiche2FL9HtQUTlCOb7Ak0bz77kxRt8UajA/640?wx_fmt=gif)

Code Review 中的代码智能服务演示

索引提供的语法服务能力

**1. 悬停提示（hover）：**鼠标悬浮在字符上即可提示该字符的相关定义信息（如悬浮在一个类名上可以提示该类的全限定类名以及相关注释）；Alt + 鼠标悬浮在字符上即可提示该字符的相关定义信息以及定义所在处的上下文。

**2. 转到定义（definition）：**Alt + 鼠标点击字符即可跳转到该字符的定义处（如点击一个类名可以跳转到该类所在文件中的类名处）。

**3. 查看引用（reference）：**Alt + 鼠标点击字符（该字符为定义时才能触发查看引用）即可弹出该字符在哪些地方被引用了（目前支持仓库维度），并且无需跳转到引用之处也能提前预览该引用的上下文。

**4. 跨文件（cross file）：**以上操作均支持文件之间的跨越。

**5. 跨仓库（cross repository）：**以上操作均支持仓库之间的跨越（即跨依赖）。

**02**

**面临的挑战**

大部分本地编译器的代码智能是在遵循了**LSP（language-server-protocol）**规范的容器中通过实时计算提供服务的，该传统方案达到了编译器级别的精准度，但是在大型代码库上的性能表现并不理想，服务的响应时间会随着代码库变大而明显变大（大型代码库开发者应该深有体会）。该领域做的出色的公司Sourcegraph *[ 04 ]*（GitLab的CEO Sid Sijbrandij曾评价Sourcegraph，“拥有这个世界上最好的查找定义、查找引用和智能代码导航能力。”）正是因为这个痛点从LSP转向使用**LSIF（language-server-index-format）**，很多本地编译器服务商也转向了这种方案。

LSIF通过预先计算静态索引的方式，显著降低了查询延迟的同时也没有牺牲准确性。但是该索引格式在增量的场景表现并不理想，而**集团内绝大部分场景是增量，面对集团如此庞大数量的活跃代码库，我们需要探寻适合增量构建特性的索引格式、高速的分布式构建能力、分钟级的索引预热能力、稳定的多版本控制能力、编译器级别的准确度、毫秒级的查询速度。**另外从代码索引的角度出发，源代码的命中率是远大于依赖的命中率的，所以实现依赖的按需索引势在必行，那么如何在提供跨库能力的同时又能节省对依赖的存储资源呢？

我们遇到了如下几个挑战：

* **如何保障编译器级别的准确度**
* **如何保障分钟级的构建速度**
* **如何保证多版本的稳定性**
* **如何保障毫秒级RT的服务**
* **如何实现依赖的按需索引**

如何保障编译器级别的准确度

准确度无疑是最先需要保障的，如果不能保持本地编译器的准确度，就一定会影响到工程师原有的阅读习惯，那么我们将如何提供Web -Based编译器级别的准确度呢？

✪ 语法分析

对编译原理有过了解的同学都知道，我们写的大部分都是高级语言（对人类友好但对机器不友好），想要让机器执行最终还需要编译成机器语言（二进制指令），而编译程序的工作过程一般也可以划分为五个阶段：词法分析、**语法分析**、语义分析与中间代码产生、优化、目标代码生成。在这里我们以Java为例，简单理解一下Java源代码编译成字节码的过程。为了降低读者的阅读成本我简化了下图的过程，其中图的左半部分是编程语言通用的。词法分析会将源代码的字符流按照预定规则转变为Token列表，Token是编译过程的最小元素，其中关键字、变量名、字面量、运算符等都可以成为Token，而语法分析则是根据Token流来构造树形表达式（AST）。

语法树的每一个节点都代表着程序代码中的一个语法结构，如类型、修饰符、运算符等。经过语法分析后，编译器就基本不会再对源码文件进行操作，后续的操作都建立在抽象语法树之上。简而言之，**只要基于抽象语法树来计算索引，该索引就可以保障如同本地编译器一样的准确度。**

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30GtxBAR7EIGIqczTIHTtOFJ9aap9bX7R6B5ic8bEA9O5zkfHtGNPwJ9bUGLNJibiahibcqbQ8s42TkBnw/640?wx_fmt=png)

✪ Abstract Syntax Tree

我们知道编程语言再怎么变，不变的是由「类型」「运算符」「流程语句」「函数」「对象」等组成的本质，这些本质概念表达了底层的运算与逻辑，对于这么多编程语言，要怎么抽离出这个逻辑本质呢？答案是统一的结构：AST（Abstract Syntax Tree）。

在这里同样用一个Java实例（User.java）来简化说明，将其转换成AST之后如下图所示，感兴趣的可以移步AST Explorer自行测试。截图信息有限，本章节中我们只需要关注一个信息，通过AST可以拿到代码中所有标志性信息（例如：包名、类名、成员变量、方法名、参数、符号关系、注释、位置等），从而计算静态索引。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30GtxBAR7EIGIqczTIHTtOFJ5oS8Zs4YwXUSiawJj9Mcyohzu4HKiaumENuJMM4ibKzELZiau0MWcyMFNg/640?wx_fmt=png)

如何保障分钟级的构建速度

对于绝大部分代码库而言，代码量的增长是平缓上升的（代码增量少于原代码总量）。所以**要想显著地提升构建速度，就应该基于原有代码来做增量构建，而非总是全量构建。**传统的语言服务器索引格式是类似图的数据结构，由于索引本身记录了太多的文件间关联关系，导致一个代码文件修改时，与其有关联的代码文件都要重新构建索引，导致索引预热速度慢且索引体积非常大不利于数据传输。因此，索引文件和代码文件如果能一一对应，且文件之间是相对独立的，尽可能地减少耦合，才能显著地提升构建速度。其次，如果遇到比较大的任务（大仓库的全量构建）时，单机构建很难满足需求，而采用分布式构建方案的话需要一个传输性能尽可能好的数据传输格式，以此提升大任务的整体构建速度。

✪ 主流方案LISF

LSIF（language-server-index-format）是一种用于描述程序信息且遵循LSP规范的语言服务器索引格式，同时它的查询和存储是支持HTTP协议的，目前主要用于Code Intelligence领域，并且是该领域非常主流的方案。通俗的讲，LSIF定义了一种可以响应LSP请求的存储索引格式，该格式将静态代码转换成了图的数据结构。它也是业界优秀的服务供应商Sourcegraph采用的索引格式方案，语法服务供应商会实现相应的解析器将静态代码转换成对应的索引格式。

有兴趣的同学可以移步What is the Language Server Index Format? *[ 02 ]*

LSIF 索引格式的设计是基于以下几点驱动：

* 该格式不应暗示使用某种持久化技术
* 定义的数据应该尽可能接近LSP的建模，便于通过LSP请求交互（生态好）
* 格式本身不定义任何符号语义，便于跨语言
* 输入输出格式基于JSON

以一个User.java实例来帮助读者理解LSIF是如何提供服务的，我们将鼠标悬停第14行第16个字符name上，触发textDocument/hover行为。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30GtxBAR7EIGIqczTIHTtOFJ7sy382Uibibq7w7Zlw80E7LaXUtQaWKlCDtN0Nl5RMGHql6ypLdlgyHQ/640?wx_fmt=png)

首先User.java的代码将会转换为如下索引（为了便于阅读，只展示与该行为相关的索引：悬停所在的symbol  range、hover result、method）

```
{   id: 1,             //表示this.name中name的range，即IDE中的坐标  type: "vertex",   label: "range",   start: { line: 14, character: 14},  end: { line: 14, character: 18} }{  id: 2,            //表示鼠标悬浮在name上的提示信息  type: "vertex",  label: "hoverResult",  result: {    contents: [      { language: "java", value: "String name \n 用户信息" }    ]  }}{  id: 3,            //表示一个鼠标悬浮提示行为  type: "edge",   label: "textDocument/hover",  outV: 2,   inV: 1            //输入为id=1的索引,输出为id=2的索引}
```

该次请求的流程如下图：

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30GtxBAR7EIGIqczTIHTtOFJB6CTcMOZFxfYahiaDOaTpJ959ToY7wBZGzTk3qswicJJLUThc3aOXS1Q/640?wx_fmt=png)

LSIF索引非常复杂，但不是本文关注的重点，通过分析这个简单的数据对象实例，只需关注以下几点，也是为什么我们没有采用这套索引格式方案的原因：

* 索引大、构建慢
* 关联复杂，不利于分布式构建
* 数据结构导致增量效率低

✪ 索引传输格式

首先我们也是遵循LSP规范而设计的语言服务索引格式，与LSIF采用JSON来做数据交换不同的是，我们选择了使用Protobuf。Protobuf是Google开发的一种数据交换的序列化协议，性能非常高，大部分IM通讯协议都是使用它来传输。性能之所以高是因为简化了很多其他数据格式之间的约定，省去了很多不必要的字符。延续这个思想，我们的索引格式也特别精简，只记录最本质的索引，关联性很强的部分都放在服务端计算。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30GtxBAR7EIGIqczTIHTtOFJibnWwJ3TJFPLoUB3P5Gd5GGQq5BMA1omFMa602QVNQmllz69AkHyJhw/640?wx_fmt=png)

从上图中，我们可以看到，一条数据用Protocol序列化后的大小是JSON的十分之一、是XML格式的二十分之一，但是性能却是它们的5~100倍。有兴趣的可以移步至protocol-buffers科普 *[ 03 ]* 。

✪ 代码索引格式

我们会将静态代码解析成下述格式的索引，和LSIF不同的是，我们只记录代码最原始、最本质的东西——代码本身以及必要的Symbol Relation，尽可能地将代码关联放在实时计算侧，以此降低预索引的时间以及存储压力，并且转换成下列索引格式。我们并不记录语法服务的执行路径（例如Hover、Definition、Reference等）。当一个LSP请求发来的时，执行路径将会在服务端基于索引实时计算得出。

```
syntax = "proto3";option java_package = "com.kite.protobuf";option java_outer_classname = "ReferenceProto";//基础字符message Reference {  uint64 hash_id = 1;              //以字面量+文件名+Range+关系类型取hash  uint64 symbol_string_id = 2;    //代码内容取hash  int32 reference_type = 3;        //参考类型  uint64 filename_string_id = 4;  //文件名取hash  int32 start_line = 5;            //起始行  int32 start_col = 6;            //起始字符  int32 end_line = 7;              //结束行  int32 end_col = 8;              //结束字符  int32 symbol_type = 9;          //字符类型  string module = 10;              //依赖信息（如java的jdk,js的react）,附加包管理器和版本等信息}//字符关系message SymbolRelation {  uint64 relation_type = 1;        //关系类型  uint64 start_id = 2;            //关系被动方的symbol_string_id  uint64 end_id = 3;              //关系主动方的symbol_string_id}
```

简单分析一下这套索引格式，显然可以从格式中看出，它在暗示我们使用关系型数据库来做持久化。代码被分割成了一个个Symbol条目，对应成数据库的一条记录，然后通过关系映射将代码之间的关联记录下来。与LSIF相比，极大地提升了增量效率。

* 每个Symbol的ID是通过代码字面量hash生成的，例如User.java文件中有一个String name =  "kite" ，不管有几处引用了这个name，都只会存储一份字面量在Protobuf文件中，因为他们字面量是相同的，以此尽可能地压缩索引文件的大小（分布式持久化时的数据载体），从而提升构建速度。
* hash\_id的设计类似于Java的 com.alibaba.indexer.schedule.engine.CodeIndexEngine，它实现了增量等于修改量的目标。我们解除了文件间的所有耦合，文件间的引用都采用全限定类名字面量的哈希值，这样当一个文件修改时也就只需要重新索引一个文件。并且每个索引文件只保存词法分析阶段产生的Symbol列表中与语法服务相关的Symbol，不存储不必要的语言服务器协议相关的信息，将与服务关联性较高的部分放在服务侧实时计算。
* 索引格式的核心就是字符表+关系表，而关系表只用了三个字段来维护，意味着增量构建时的影响面会特别小。

由于索引文件是二进制的，为方便阅读这里暂先转换为JSON格式，并以成员变量为实例讲述一下索引的原理。下图中sourcePath是成员变量，String是它的类型，/\*\* 源代码路径 \*/是它的注释。将符号表的Key和Symbol列表中的Value联系起来即可理解索引的运作原理。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hlia35Pshyp9oo1icQYDXaw1AyogOT7XBmhQm07pusMD8V2rEkTxAlyiaw5NmoDvd13gAtNRFctMZmA/640?wx_fmt=png)

该实例演示的是文件内索引原理，如果要进行文件跨越（或仓库跨越），例如sourcePath是来源于（引用）com.alibaba.code.indexer.Configuration中的成员变量。那么在关系表中则存储Configuration的全限定类名的字面量hash值即可。

✪ 调度系统的优化

就索引使用的场景而言，并非所有Push都应该触发索引构建任务。所以我们可以通过优化任务的过滤通道、支持任务的fast-failed、更高效的基线查询策略，以此来提升全局的构建性能。

⍟ 预处理 — Pre Schedule

用于在生成分布式任务之前，过滤推送事件与合并事件的消息，将删除分支、Release分支等不需要构建索引的场景排除，然后读取开关配置，最终装载相应数据生成任务。为什么我们要采用两套优先级不同的配置呢？因为数据库配置（页面或接口透出）是仓库级的，而文件级配置是版本级的。例如当你Checkout一个新分支时，你不希望这个分支构建索引（或者只希望这个分支构建索引），那么两套配置使用起来将会非常灵活，即同时支持仓库粒度和提交对象（Commit）粒度。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30GtxBAR7EIGIqczTIHTtOFJhN9fMTGrr1aj3dangIuqrsD3gHsg3TARPCxfV9iaKXWIEAIUsgSXMlw/640?wx_fmt=png)

⍟ 状态管理器 — State Machine

用于调度中间件自动重跑、API手动触发重跑、删除索引等操作时保持幂等性。当发起重跑时，任务只管跑，除了逻辑执行失败以外，状态机不会将任务置为失败，并且会清除脏数据。由于该任务可能会存在卡死、超时的情况，所以该模块可以提供 Fast-failed能力，另外也用于在Code Review中使用索引服务时能展示正确的索引状态。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30GtxBAR7EIGIqczTIHTtOFJ1bIiaE3XYTYfh4MpaT4CaotcmTicu4VonWKibK5wNCrWx8bCUiczRiaLmpQ/640?wx_fmt=png)

⍟ 基线选择器 — Baseline Selector

用于增量构建时选择合适的基线以及删除单个版本的索引时搜索它的影响面，以决定是否能删除或采用哪种策略删除。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30GtxBAR7EIGIqczTIHTtOFJic2aNqLes6RjUlIOC3dyNLqibzll7GlibQ5SUHiaJUl7KScIzsg9Y9XfQA/640?wx_fmt=png)

如何保证多版本的稳定性

代码仓库并非是随着一个方向的线性时间一直发展，经常会有例如reset（版本回退）、checkout（分支切换）等朝向多个方向发展的特征。那么如何保证稳定的多版本控制尤为重要，从某种意义而言，这一环节将会保障索引命中代码的准确度。这里举一个反例：在master分支中查看User类的定义，结果跳转到了feature/xxx分支中的User类。

✪ Git存储特性

目前集团中的绝大部分代码都是基于Git进行存储的，所以索引的存储设计和Git存储特性关联起来将会是非常好的选择。

在Git中有三大对象——数据对象、树对象和提交对象（即blob、tree和commit）。另外这里也会简单提到分支（branch）的概念，帮助我们进一步优化每次增量的大小。

⍟ Blob

在Git中，文件的内容将会存储在blob（二进制大对象）的对象中。blob与文件的不同在于，文件还会包含元数据（meta-data），例如创建时间等其他属性。而blob只存储内容——数据的二进制流，Git中的blob通过SHA-1哈希值 *[ 05 ]* 唯一标识。所以 blob的特性和我们的索引文件是高度一致**（即索引文件是blob的映射）**。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30GtxBAR7EIGIqczTIHTtOFJJcvxFwz6unDhUnQueLKlkUhdexE0T0GUN7WHVb9LqhoKk1EuhXcDrw/640?wx_fmt=png)

⍟ Tree

在Git中，树对象（tree） 相当于目录。一个树对象基本上就是一个目录列表，它引用着blob和其它的树对象。

树对象也用SHA-1哈希值唯一标识，它通过其它对象（blob或树对象）的SHA-1哈希值引用它们。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30GtxBAR7EIGIqczTIHTtOFJdyytOwGUlHkdK889xCANxfm9CWPic7SQUoTD04MsE9XpX7jhgUYMPww/640?wx_fmt=png)

⍟ Commit

在Git中，一个快照就是一个提交（commit）。一个提交对象包括一个指向主要树对象（根目录）的指针和一些像提交者、提交信息和提交时间这样的元数据。

在大多数情况下，一个提交还会有一个或多个父提交——之前的快照。当然，提交对象也通过它们的SHA-1哈希值唯一标识。这些哈希值就是我们使用git log命令时看到的那些哈希值。**（索引的快照文件同时包含了tree和commit的能力）**

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hlia35Pshyp9oo1icQYDXaw1ccOhGNaJA3sNC2fne4UWyAziayiabCF7IiabSUwUrHeiceR1ibJamwxLghQ/640?wx_fmt=png)

⍟ Branch

在Git中，分支（branch）只不过是提交对象的命名引用。我们可以一直用SHA-1哈希值引用一个提交，但是人们通常喜欢以其他形式命名对象。分支恰好是引用提交 的一种方式，实际上也只是这样。例如：在大多数仓库中，主线开发都是在一个叫做master的分支上完成的。分支对于索引的价值在于增量构建，我们认为通常一个分支中的多个commit的差异程度较小，即在分支内搜索基线的增量值会更小（增量表现更好）。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hlia35Pshyp9oo1icQYDXaw1f37ciaPJIbXibwMfCsbsJIbo0vxwVOqIVqOwKfJlqiazTO0pBiaFOQWL1w/640?wx_fmt=png)

✪ 索引版本管理器

当一个仓库push进来时，我们的Indexer总是会构建出一份版本快照。由于每个索引文件是独立的（快照中的uniqueId也是索引文件的名字即唯一标识，该标识保证仓库内文件进行变更时也唯一，例如：Parser.java文件经过四次修改，则会生成四个uniqueId不同的索引文件指向Parser.java）。因此该快照的作用类似于commit，或者说索引的索引。用于指向一个版本对应的所有索引文件。另外还可以保存文件间的依赖关联。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hlia35Pshyp9oo1icQYDXaw100YTmCrukFNgelmAic1pasunia4jsUIxSACgOJm7QFjfB5yN7PTKUTPg/640?wx_fmt=png)![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hlia35Pshyp9oo1icQYDXaw1vKTjazJKJOhFTsRGd9E4VzjnCG1zwpltprBiaunNeybozAFKegQ37dg/640?wx_fmt=png)

如何保障毫秒级RT的服务

我们已经对近十万个灰度仓库构建了百亿数量级的索引。随着灰度范围的扩大以及软件的生长，这个数字还会大幅度增加。当前我们的语法服务RT处于一个非常理想的水平，那么在数据总量持续上升的背景下如何保持这个水平呢？

✪ 数据分离

索引数据主要分为三类：二进制源文件、源代码索引和依赖索引。其中依赖的索引复用程度极高，例如多个仓库源代码中都使用了TDDL（淘宝分布式数据引擎），该部分属于共享数据，不需要做逻辑分离。并且出于未来可能用于代码搜索引擎的考虑，可以通过ElasticSearch的倒排索引机制，保障关键词搜索的速度，所以这部分索引被存储在ElasticSearch中。一般来说，开发人员在本地编译器中对源代码的开发习惯是仓库维度的，我们延续这个特性，把被高频率命中的源代码索引，以仓库作为分库分表的标志，存储在mysql数据库中。二进制源文件则存储在OSS中作为冷备机制，以及提供给大型仓库构建任务时做分布式持久化时使用。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hlia35Pshyp9oo1icQYDXaw1Kqicavpz62ssmlnDpU4aZLlxXiaQ531Xq8Z4pCpUl0SKHdPlicEEbrMtQ/640?wx_fmt=png)

✪ 冷热机制

哪怕将源码和依赖分离，还是无法平衡mysql每日新增数亿级的数据量带来的耗时增长。目前索引最常用的场景是代码评审，但并非所有的仓库都会做代码评审，所以代码评审的活跃度也被作为索引活跃度的一个重要参考指标。

我们通过仓库活跃度、仓库的代码评审活跃度等条件来判定该仓库的索引是否会活跃。如果被判定为不活跃，我们将构建链路缩短至索引的二进制源文件存储在OSS就结束任务，以此降低mysql的数据增长指数，同时也能提升索引的命中率。

当非活跃仓库想要使用索引服务怎么办呢？通过仓库活跃度监控，在冷库转变为热库的瞬间，调度系统就会在用户无感知的状态下调度机器将冷备份在OSS的索引文件快速持久化到mysql（生效快）。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hlia35Pshyp9oo1icQYDXaw1ticTFADwmdqKX42ibnDNwjkT9rodibSUojjgzMm7EyTZfokyjWUib097GQ/640?wx_fmt=png)

✪ 垃圾回收机制

随着软件的生长，索引数量也会相应增长。为了保障存储引擎的性能和命中率，我们应该建立相应的垃圾回收机制，之所以用垃圾回收这个词，是因为索引会随着时间线的推移而降低低活跃度（没有活跃度即没有使用价值，所以称为垃圾），因此通过该机制使整体的索引量保持在一个健康的水位线是非常必要的。

索引完整生命周期的数据模型如下图。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hlia35Pshyp9oo1icQYDXaw1G1l02Q3joEE2p3T6z3UU6bxT5lNF5oHlXva906dOCcjFibCp0aDrBTA/640?wx_fmt=png)

索引的生命周期被我们分为两类，一类是被作为基线的索引（被多版本共享，生命周期长），另一类是独立索引（未被共享，生命周期短）。每一份索引快照都类似于树上的一个节点，整个仓库的发展历程类似于一棵树的生长，而树枝的生长方向则类似于代码的发展方向（类似Git的分支约定），树上的节点越近则索引快照之间的相似度越高，而独立索引可以理解为是树最外层的叶子节点。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hlia35Pshyp9oo1icQYDXaw13RwzXlGA7ApoccY5RW5siad3dz3QqJFIdLDicibg0Cd1lsU59onvyCGVA/640?wx_fmt=png)

为了降低锁表风险，我们会在夜深人静的时候通过定时任务的方式进行垃圾回收。虽然会有多种判定条件来触发垃圾回收，但是索引特性导致回收策略只有两种：版本回收和仓库回收（如下图）。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hlia35Pshyp9oo1icQYDXaw1iat9cUeoibSnrxApQzPKaBPiaib9YPtoY6z3rrhIotY2HDjznhLjFMLWcA/640?wx_fmt=png)

版本回收：基于数据模型的分类，私有数据的清理是没有风险，而共享数据则会通过基线判定、引用计数器、 Commit 比对来决定是否能安全清理，以此在清理过程中保障仓库整体的索引稳定性。

仓库回收：整个数据模型的定时清理（无基线风险）。当仓库回归活跃时将会触发类似本地IDE的索引预热。

如何实现依赖的按需索引

通常的跨库能力都是将依赖仓库也进行索引，然后建立依赖仓库与源代码仓库的联系，从而实现跨库能力。源代码和依赖的索引本身没有区别，都是使用同一套代码索引格式，但是基于该格式之上，源代码的索引上层会封装仓库信息（如id、branch、commit，用于版本控制）；而依赖的索引上层会封装依赖包管理器信息、依赖包标识和版本信息。

从索引利用率的角度，源代码内部关键性极高（也可能会有少量无用代码在仓库中保存），而源代码和依赖的关联相比之下非常薄弱，例如在A仓库中使用一次 org.apache.commons.lang.StringUtils#isBlank方法，那么源代码和依赖只有这一条索引的联系，但是会存储整个org.apache.commons依赖包的索引（大概几百万条），也就是说索引命中率只有几百万分之一，而一般代码质量较高的源代码的索引命中率在99%以上。

基于上述背景，计算的策略维持现状，存储的策略将以最小原则按需存储。例如只引用了一个方法，那就只存储一条索引，以及与它的关联（索引标记），然后将依赖仓库的代码文件存储在OSS中，以此减少对mysql的压力。当需要跳转到这个文件的时候，服务会根据索引上的标记命中OSS（typescript语言通过unpkg方案）的相关文件，并装载文本内容进行响应。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hlia35Pshyp9oo1icQYDXaw1rh7vibmdeYcOkwWEz6baKtE8pqEAWtpwVTE0K1GDRnnFJJVsQINBBNQ/640?wx_fmt=png)

**03**

**总结与展望**

本文分享了阿里集团的代码索引技术实践，包括如何达到编译器级别的准确度和分钟级的构建速度、保障多版本的稳定性和毫秒级RT的服务等。目前已经在Code Review场景下为用户提供了本地IDE的阅读体验，有效地提升了工程师的研发效率，未来还将在阿里集团更多的云端代码阅读场景中落地。随着应用场景的不断增加，我们还将基于索引升级代码搜索引擎，帮助工程师准确定位错误和漏洞，以及在全局存储库中打补丁和升级。由于软件是不断生长的，所以我们会持续探索更好的存储架构，以此应对未来更大规模的研发挑战。

本文成果由研发基础设施团队、前端工程团队、Code Insight团队合作产出。 (排名不分前后)

参考文章

[01] 什么是语言服务器协议：What is the Language Server Protocol?

https://microsoft.github.io/language-server-protocol/overviews/lsp/overview/

[02] 简述语言服务器索引格式规范：Language Server Index Format Specification

https://microsoft.github.io/language-server-protocol/specifications/lsif/0.4.0/specification/

[03] Protocol Buffers的介绍：protocol-buffers

https://developers.google.com/protocol-buffers

[04] Sourcegraph 代码智能优化：Optimizing a code intelligence backend

https://about.sourcegraph.com/blog/optimizing-a-code-intel-backend/

[05] SHA1算法原理过程详解：SHA1密码散列函数

https://www.wosign.com/News/news\_2018121101.htm

[06] Git内部原理 - Git对象：Git对象

https://git-scm.com/book/zh/v2/Git-内部原理-Git-对象

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hlia35Pshyp9oo1icQYDXaw1PamMstfPdksnErUsUFcXNnQOhrV0Kyxkib7iaeNiaQXobPxYpst7HLW5Q/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30EMKQ9icwneSbNQzo1Y2ia3I0W9hCptKWotZ2XxAibQ8Zg0yrTBmkxPzEMjQWoJaCI5YQXZfbp7UPE5w/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_gif/OmCbZ5JK30GMpsz1kdxGBRiclB5yjhBh5iamZLYrF2BOK4YNhXbjibibx63B6o5ubgOvYGRyUa0DK6gpI9YibkKUUCQ/640?wx_fmt=gif)

欢迎留言一起参与讨论~