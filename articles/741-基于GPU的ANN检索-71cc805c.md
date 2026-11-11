---
title: '基于GPU的ANN检索'
company: 百度
tag: 召回
date: 2024-11-21
url: https://juejin.cn/post/7439391408832004123
account: 
origin: harvest-202607
---
# 基于GPU的ANN检索

[百度Geek说](/user/4186596000416094/posts)

2024-11-21
  
582
 
阅读21分钟

   

## 导读

近似最近邻（ANN）向量检索的CPU方案已被广泛地应用于在线检索等多种场景中并取得了不错的效果。GPU相比CPU拥有更强大的并行计算能力，如何将GPU引入ANN检索获取更大收益，成为了业界重点研究的难题之一。百度与NVIDIA技术团队，基于 RAFT[1]开源代码库设计并实现了一种基于GPU的ANN在线检索方案，在一类高检索流量业务场景下获得了显著的成本收益。本文主要介绍整体方案并总结一些思考及展望。

## 01 ANN简介

随着自然语言处理和深度学习的高速发展，向量检索为提升搜索用户体验发挥出重要作用，近似最近邻（ANN）搜索是在有限时空条件下实现向量搜索的主要方式。ANN的核心思想是近似，所有ANN算法都致力于在低规模计算开销下保证最后选择的邻居是查询向量的最近邻概率很高，但不追求100%的准确性。根据近似思路的不同，ANN检索算法主要分为四类：基于树的ANN算法、基于LSH的ANN算法、基于量化的ANN算法和基于图的ANN算法。接下来对本文涉及的几种ANN算法原理进行简要介绍。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/ab2c5608c54e4a099dcc8eccbfa0f3a9~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785377577&x-signature=s%2BhWDXlGiFs%2BbwbrlmAwPlarg58%3D)

△IVF\_FLAT

**IVF\_FLAT**：如上图所示，基于量化[2]的方案是通过一组特定的点来表示全部的向量空间，每个特定点代表一个子空间，它常与倒排索引相结合[3]，首先对向量空间进行划分，每个数据点按照与其最近的子空间质心形成倒排拉链，这样每条倒排拉链对应一个子空间，拉链中元素为落在该子空间的向量id。检索时首先通过与质心的距离计算选取若干个子空间，然后只计算所选子空间内数据点与查询向量的距离，排序后得到最后结果，该思路被称作IVF\_FLAT方案。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/9266119275ab488096815e0df11c21c0~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785377577&x-signature=wfsa0p0QkUa7j24HTWpzEd6tJk8%3D)

△IVF\_PQ

**IVF\_PQ**：除了借助向量量化选取子空间减少计算以外，量化对于ANN检索的贡献还在于可以使用量化点计算量化距离从而代替精确距离的计算，这样减少了计算但会带来精度损失，这就要求量化的精度不能太低。乘积量化[3]（PQ）可以借助几组子向量器的质心，产生大量的质心，降低量化学习的复杂度。它与残差量化[4]相结合可以在有限的时空条件下提升整体量化的精度。基于乘积量化的IVF方案经典思路如上图所示，它是在构建时先对所有数据进行一次向量量化，根据这次向量量化的簇心形成倒排拉链，然后计算出所有数据与其质心的残差，然后再对残差进行乘积量化，记录对应其量化点的编码。检索时同样先与向量量化的质心计算决定候选拉链减少计算量，然后计算查询与质心的残差后对候选点进行距离计算，计算距离时是计算查询残差与候选点的量化距离，最后进行距离排序后返回检索结果，该思路被称作IVF\_PQ方案。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/3f7a5524d9134a2a8f0d2e025c60c047~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785377577&x-signature=28FWQawnh9dLLC9MuggK0GA2s%2Fo%3D)

△Cagra

**Cagra[6]**：基于图的ANN方案进行向量检索的过程都是通过图索引中点的邻接关系逼近到和查询向量点距离最近的若干个结果，图索引的构造和检索策略是基于图的ANN搜索方案研究的重点，需要考虑准召、搜索效率和空间开销等多方面因素。经过业界的不懈研究，以HNSW[5]为代表的诸多基于图的方案凭借优异性能都得到了广泛应用，但大部分的图算法在构建流程和检索路由过程中很难充分利用到GPU的并行能力，NVIDIA针对图算法这一挑战自研了名为Cagra[6]的基于GPU的ANN图算法，如上图所示。该算法以NN-descent[7]图为基础，然后借鉴NGT[8]的路径调整的思路对边进行剪枝，最后对剪枝后的正向图与对应的反向图各取一半的边进行合并，生成最终的Cagra图索引。检索过程维护一个top-M（M大于等于返回结果数目K）的列表和一个长度固定的候选列表，每轮迭代局部排序出距离最小的top-M并更新，然后将top-M的未被检索的邻居添加到候选列表中，直至top-M列表的节点都被遍历，然后选取top-K作为结果返回。Milvus[9]数据库就是借助Cagra算法实现了出色的性能加速。

## 02 我们选择了什么业务场景来使用ANN on GPU

在百度的某一类搜索业务场景下，对单次用户查询，会进行扩展检索以召回更多样化的相关结果。具体的业务场景需求：

* 约束：ms级低延迟、>90%的高召回率、亿级索引量
* 场景：超高检索吞吐
* 目标：更低的检索成本

在这样的超高检索吞吐场景下，基于 GPU 来做高并行度计算会比基于 CPU 的检索有更高的性价比。因此，我们选择在该场景下来做 ANN on GPU 的尝试。

## 03 我们是怎么做的

**3.1 索引算法选择**

RAFT[1]代码库是NVIDIA设计开发的一套开源代码库，包含了可广泛应用于机器学习和信息检索场景的基本算法和原语，这些算法经过CUDA加速优化并可以通过构建块使编程简易化。它提供了四种GPU-ANN算法：BruteForce、IVF\_FLAT、IVF\_PQ和Cagra，这些算法都通过相同名称的顶层接口来实现索引的构建（build）、存储（serialize）、加载（deserialize）、检索（search），为用户的使用提供了便利，以IVF\_FLAT为例：

```
//T为数据的类型，IdxT为数据id的类型
template <typename T, typename IdxT>
auto build(raft::resources const& handle,  //资源句柄
           const index_params& params,    //构建索引参数
           raft::device_matrix_view<const T, IdxT, row_major> dataset) //显存中存储的数据集
           -> index<T, IdxT>;

template <typename T, typename IdxT>         
void serialize(raft::resources const& handle,    //资源句柄
               const std::string& filename,    //存储文件名
               const index<T, IdxT>& index);    //索引对象

template <typename T, typename IdxT>              
index<T, IdxT> deserialize(raft::resources const& handle,     //资源句柄
                           const std::string& filename)；//加载文件名

template <typename T, typename IdxT>
void search(raft::resources const& handle,    //资源句柄
            const search_params& params,    //检索参数
            const index<T, IdxT>& index,    //索引对象
            const T* queries,    //查询指针
            uint32_t n_queries,    //查询数目
            uint32_t k,    //每条查询返回结果数
            IdxT* neighbors,    //返回结果id的指针
            float* distances,    //返回结果距离的指针
            rmm::mr::device_memory_resource* mr = nullptr) //可选的内存资源指针
```

我们对RAFT支持的四种算法进行了对比测试以找到适合我们场景最佳的算法选型，主要结论如下：

BruteForce：

* 暴力全量计算，召回率100%

单卡索引规模：目前仅支持float类型，A10单卡最多可支持2kw \* 256维数据

检索延时：约70ms（batch\_size<10）-> 无法满足我们场景下的延时要求Cagra：

单卡索引规模：在百万量级数据集上相比IVF系列有优势，但在千万规模数据集上效果下降较严重

检索成本：从成本考虑，单卡数据规模越大越好 -> 无法满足我们场景下的成本约束

* IVF\_PQ：

单卡索引规模：支持float和int8，会对任何输入类型都转成FP32，从而利用TF32的Tensor Core加速能力，所以不同数据类型下的检索性能都差不多；核心优势是显存占用小（索引不需保存原始向量，只需要保存编码）适合更大索引规模。

召回率：在我们的数据集上，PQ精度损失较大，量化距离排序不够准确，召回率损失较严重 -> 无法满足我们场景下的召回率要求

* IVF\_FLAT：

单卡索引规模：支持float和int8两种类型，float类型索引在大规模数据量下显存开销高，索引建库时间长；int8类型四分之一的压缩比可有效缓解显存受限问题

召回率：在合理选择int8量化方式后，IVF\_INT8精度损失很低，召回率不受限，加大检索倒排拉链数目后召回率提升很快

经过测试后，IVF\_INT8算法的查询延时和整体吞吐均表现优异

因此我们的场景下，最终选择采用 IVF\_INT8 索引算法。

**3.2 离线建库**

* 单分片索引容量提升
* 目标：成本考虑，需要在显存受限的情况下，尽可能提升单分片索引量
* 思路：量化+超显存
* 量化：int8量化
* 超显存：数据量达到一定规模后，有限的显存资源可能放得下索引，但却放不下输入数据无法构建出索引；为解决这种问题，我们在离线构建索引时使用了GPU的超显存技术（借助内存与显存的交换实现显存需求的超用），该技术可以在显存超用不严重的情况下依旧保持很高的计算性能，下方代码给出了使用示例：

```
std::shared_ptr<rmm::mr::device_memory_resource> resource_ptr = 
    std::make_shared<rmm::mr::managed_memory_resource>();
rmm::mr::set_current_device_resource(resource_ptr.get());
raft::device_resources  dev_resources(rmm::cuda_stream_per_thread, {nullptr}, resource_ptr);
```

* 索引调参
* 拉链长度控制：

IVF\_INT8在构建阶段需要训练簇心，训练数据从构建索引数据中按一定比例获取，由kmeans\_trainset\_fraction参数控制。而构建多少条倒排链由n\_lists参数决定，该建库参数影响着达到目标召回率时的检索计算量，因此需要调参以获得更佳的检索性能。

我们实践的经验规律是控制平均链长在一千到两千之间时，有较好的综合性能表现。

* 均衡性控制：

由于各条链与查询计算时有天然的并行度，为了避免计算长尾构建索引时应尽量使各链链长均匀，这一点可以借助raft代码库中的kmeans\_balanced组件实现：

```
//DataT为输入数据的类型，MathT为实际进行kmeans的类型，IndexT为数据id的类型，MappingOpT为数据类型映射的类型
template <typename DataT, typename MathT, typename IndexT, typename MappingOpT = raft::identity_op>
void fit(const raft::resources& handle, //资源句柄
         kmeans_balanced_params const& params, //kmeans平衡聚类所需的参数
         raft::device_matrix_view<const DataT, IndexT> X, //训练数据集
         raft::device_matrix_view<MathT, IndexT> centroids, //聚类中心
         MappingOpT mapping_op = raft::identity_op()) //输入数据类型到计算数据类型的映射
```

**3.3 在线检索**

下图展示了我们所设计的基于GPU的ANN在线检索方案，通过batch检索来达到充分发挥GPU并行计算能力的目的。在上游查询到达时，查询将会放入查询队列中，检索线程会按照batchsize取出对应数量的query组成BatchQuery，并将其作为输入进行基于GPU的ANN检索。在检索过程中需要先将BatchQuery拷贝到显存中，然后在GPU上进行IVF\_INT8算法检索，返回对应query顺序的BatchResult结果并将其从显存拷贝取出，检索服务模块对BatchResult按query拆分后进行算分、过滤等后置操作后返回结果到上游。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/ca032450cc6b43568ad675b1d07cfc56~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785377577&x-signature=kbOcuYw4tblUJGBn6M08RlSuK7k%3D)

△在线检索方案

* 向量距离计算并行化 & 显存数据复用

对选中的多条链与查询向量进行距离计算，是IVF\_INT8在检索时计算量最大的部分，RAFT代码库中使用interleaved\_scan\_kernel函数对这一阶段做高效并行计算，它是保障IVF\_INT8检索性能的关键。

由于各链和查询之间的距离计算并无依赖，该接口将每条链的数据用一个CUDA块进行扫描，并将容量不大的BatchQuery向量加载到共享显存中，这样可以使得同时读取索引数据和查询时节省全局显存带宽。

每个CUDA块都会将一条链的数据按照合理粒度分别承载给多个warp并行计算获取距离结果，最后调用matrix::detail::select\_k函数对多个不同块的结果merge后挑选最终top-K返回。

* 基于实时流量统计的动态 batchsize 控制

在合理的范围内增大batchsize可以增加实例的整体吞吐，但batchsize较大而流量较小时会出现为了组batch某些query等待延时过长的问题，从而导致查询超时；对应的，batchsize较小而流量较大时会有大量query入队却无法及时处理的情况，因此根据流量选择适合的batchsize至关重要。

我们采用训练数据拟合的方式得到流量相关的batchsize预估函数。满足一定时间阈值时，会使用预估函数预估当前流量下适合的batchsize，如果与之前设定的batchsize差距大于阈值，就会对batchsize进行调整。batchsize没有实时更新而是选择定时预估的方式是因为在GPU上进行检索时，会提前根据batchsize预先分配BatchQuery和BatchResult的显存，这部分耗时较长，更新不能过于频繁，因此时间阈值不能过短，否则会影响检索效率；但时间阈值也不能过长，否则无法根据最近时间段流量情况找到最适合的batchsize。

* GPU及CPU分数打平

我们对构建索引向量和查询向量的float数据进行INT8量化的思路是最通用的min-max量化，即通过训练统计最小值 min\_val 和最大值 max\_val 后进行量化。该方法会先计算两者差值为 diff\_val = max\_val - min\_val，然后借助量化公式 y = (x - min\_val) / diff\_val \* 255 - 128 将任何浮点数 x 量化为在int8数据表示范围的 y。而最后返回的量化距离可以借助量化公式的线性系数 255 / diff\_val 转化为原数据的真实距离，这样可以跟其他CPU方案ANN索引的检索距离直接进行比较，以便上游模块进行排序等操作。

整体上，通过借助RAFT代码中IVF\_INT8算法的高效实现、动态batchsize控制和显存数据复用逻辑充分发挥了GPU的并行计算优势，使得检索服务单实例可以达到更高的查询的吞吐能力，降低了高流量场景下副本数，大大降低了所需成本。

**3.4 达到的效果**

根据上述方案实现并测试后，对2500w256维数据集构建索引，索引所占显存<10G，建库时间<10分钟，检索服务单实例在返回结果top30的条件下可以承载约2w qps，平均查询延时在ms级。在我们的高检索流量落地场景中，总成本相比于CPU方案分别可以节省30%~50%资源。

## 04 思考和展望

**4.1 GPU在ANN检索场景的讨论**

* 什么场景下适合用GPU，什么场景下不适合用

GPU与CPU相比拥有更强大的并行处理能力，它可以借助成百上千个更小的、更高效的处理核心做到同时处理大量的数据，有益于提升计算吞吐。而是否选择GPU需要注意以下几点：

* 计算规模是否适合GPU发挥：

虽然CPU的计算能力相比GPU有不少差距，但是对于计算需求不大的场景CPU就足以胜任，这种情况下使用GPU无法充分发挥算力只会放大其价格昂贵的劣势。

ANN的核心思路是通过近似方式来减少算量，虽然近似的思路各有不同，但普遍趋势上算量越大，召回率越高，所以一般总体计算量大、召回率要求非常高的场景适合使用GPU；而对召回率要求较低、总计算任务不重的场景更适合CPU。

* 计算逻辑是否能够并行：

CPU拥有着可以支持复杂逻辑、更为强大的计算单元，而GPU虽然计算单元众多支持高并发，但控制逻辑相对简单，所以对于数据依赖严重、计算过程串行阶段较多的场景，可能很难设计并行算法发挥出GPU高带宽的计算能力，这类场景不适合GPU。

在ANN算法设计上，CPU方案可以进行步骤繁杂的流程，而GPU方案需要简化搜索逻辑，减少数据依赖和同步阶段，加强并行度以发挥GPU的高并发能力。所以对延时要求相对宽容、查询流量较高的场景更适合GPU方案。

* 是否受限于GPU显存容量：

由于GPU的计算任务需要将数据存放在显存中计算，而主存和显存之间的拷贝延时很长，所以基于GPU的ANN算法设计一般要避免过多的主存和显存的数据拷贝和交换，这就要求检索中需要用到的全部或关键数据需要提前存放在显存中。然而GPU显存又是有限的，因此GPU不仅身为计算单元有着其发挥计算能力的局限要求，还面临着类似“存储单元”的瓶颈——显存受限。

在GPU方案的ANN算法设计中需要想办法缓解这一问题，使显存中存放的数据更能发挥作用。所以单实例支持数据规模过大、数据冗余严重或需要数据备份等场景更适合CPU使用内存的方案；而单实例数据规模适度，数据不需频繁变动和过多冗余备份的场景更适合GPU。

* 我们的场景下，GPU比CPU节省成本的本质原因

对于大规模数据ANN在线检索场景，由于单实例资源有限，全部数据索引很难存放于同一个实例中，因此要对数据进行划分成若干个库层，查询会分发给每个库层进行检索得到局部结果后进行合并从而得到最终结果；另一方面，每个实例能够处理的流量也是有限的，因此根据上游下发的流量需要建立若干个副本共同承担查询流量。一个库种的检索成本与其库层数和每个库层的副本数高度相关。

对于低流量下的ANN在线检索场景，每个库层只需要少数副本，因为CPU资源足以承担计算，应用GPU只会浪费算力并放大GPU价格昂贵的缺点，导致总资源成本增加。而对于高流量下ANN在线检索场景，高流量所带来的巨额总计算量为GPU取代CPU创造了可能。因为CPU算力有限，基于CPU的ANN方案处理检索的能力也是有限的，因此需要对每个库层增添大量副本，这无疑会对成本造成极大的压力。虽然GPU的价格要比CPU昂贵，但如果能够有效发挥出GPU的并发处理计算能力，那么使用GPU替代CPU进行ANN检索势必能够实现高吞吐处理请求的效果，这样单副本可以承载更多的流量，从而减少每个库层的副本数节省资源。

假定一个库种承载的总流量为 x ，单个库层的总成本为 y，每个副本所使用的GPU总成本 p2 要高于使用CPU的总成本 p1，GPU方案和CPU方案下每个副本能承载的流量分别为 q2 和 q1，那么GPU方案单个库层的总成本为 y2 = ceil (x / q2) \* p2，CPU方案单个库层的总成本为y1 = ceil (x / q1) \* p1。下图展示了GPU和CPU方案在不同流量下的成本趋势，可以看出在低流量时，即使充分发挥GPU作用（即 q2 远大于 q1 时），CPU成本也比GPU要低；而在高流量场景下，GPU的成本要比CPU低得多，而且随着流量的增加所获得的成本收益也越高。所以高流量下的ANN在线检索场景成为了本文GPU方案的应用场景。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/e5d8642dbff34c64a3db16699c15fbd7~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785377577&x-signature=%2FicBR3jKTwHWh8MDjW1YusAfnKU%3D)

△不同吞吐下的检索成本对比示意

**4.2 未来展望**

本文以RAFT-LIB IVF\_INT8算法为核心算法，借助灵活batch检索充分发挥GPU的并行处理能力，完成了ANN on GPU在百度的一类实际业务场景的应用落地，在吞吐、延迟、召回效果等多个方面保证了很好的效果，并在成本方面取得了不小的收益。后续我们将会和NVIDIA技术团队一起，对RAFT代码库的IVF\_INT8算法做进一步优化，并对其它GPU相关ANN前沿算法进行深入探究，以期待GPU在ANN领域获得更多应用。

**参考文献：**

[1] [github.com/rapidsai/ra…](https://link.juejin.cn?target=https%3A%2F%2Fgithub.com%2Frapidsai%2Fraft "https://github.com/rapidsai/raft")

[2] *Robert M. Gray and David L. Neuhoff. Quantization. IEEE Trans. Inf. Theory, 1998, 44(6): 2325 ∼ 2383.*

[3] *Hervé Jégou, Matthijs Douze and Cordelia Schmid. Product Quantization for Nearest Neighbor Search. IEEE Trans. Pattern Anal. Mach. Intell. 2011, 33(1): 117 ∼ 128.*

[4] *Yongjian Chen, Tao Guan and Cheng Wang. Approximate Nearest Neighbor Search by Residual Vector Quantization. Sensors, 2010, 10(12): 11259 ∼ 11273.*

[5] *Yury A. Malkov and Dmitry A. Yashunin. Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs. CoRR, 2016, abs/1603.09320.*

[6] *H Ootomo, A Naruse, C Nolet, et al. 2023. CAGRA: Highly parallel graph construction and approximate nearest neighbor search for GPUs. arXiv preprint arXiv:2308.15136 (2023).*

[7] *Mengzhao Wang, Xiaoliang Xu, Qiang Yue, and Yuxiang Wang. A Comprehensive Survey and Experimental Comparison of Graph-Based Approximate Nearest Neighbor Search. arXiv:2101.12631 [cs], May 2021. arXiv: 2101.12631.*

[8] *Masajiro Iwasaki and Daisuke Miyazaki. Optimization of Indexing Based on k-Nearest Neighbor Graph for Proximity Search in Highdimensional Data, October 2018. arXiv:1810.07355 [cs].*

[9][github.com/milvus-io/m…](https://link.juejin.cn?target=https%3A%2F%2Fgithub.com%2Fmilvus-io%2Fmilvus "https://github.com/milvus-io/milvus")

———— END ————

**推荐阅读**

[维度爆炸背景下uv计算在Feed业务的高效实践](https://link.juejin.cn?target=http%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247601927%26idx%3D1%26sn%3Dc2303fb7cff50c4d1384fc7656a087cc%26chksm%3Dc03f7f7bf748f66da15fe82ccfc08f59f7b9779a9cf96abbf65fd208eed61affe7e3e20068b0%26scene%3D21%23wechat_redirect "http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247601927&idx=1&sn=c2303fb7cff50c4d1384fc7656a087cc&chksm=c03f7f7bf748f66da15fe82ccfc08f59f7b9779a9cf96abbf65fd208eed61affe7e3e20068b0&scene=21#wechat_redirect")

[数据湖系列之四  | 数据湖存储加速方案的发展和对比分析](https://link.juejin.cn?target=http%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247601872%26idx%3D1%26sn%3D73ec6487a1b0a4fa4f23f9faa5ffa25a%26chksm%3Dc03f7eacf748f7ba347d30fe38f24f22aade645250f19c1c2d16f800db3ea52097390afb1440%26scene%3D21%23wechat_redirect "http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247601872&idx=1&sn=73ec6487a1b0a4fa4f23f9faa5ffa25a&chksm=c03f7eacf748f7ba347d30fe38f24f22aade645250f19c1c2d16f800db3ea52097390afb1440&scene=21#wechat_redirect")

[大模型时代，云原生数据底座的创新和实践](https://link.juejin.cn?target=http%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247601863%26idx%3D1%26sn%3Daebae9a8e3371947f764612a564172d2%26chksm%3Dc03f7ebbf748f7ad716977f4f02bf1d8e3b2160be40d3046ac4355bbd6513eb4f9ebcf5d64b4%26scene%3D21%23wechat_redirect "http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247601863&idx=1&sn=aebae9a8e3371947f764612a564172d2&chksm=c03f7ebbf748f7ad716977f4f02bf1d8e3b2160be40d3046ac4355bbd6513eb4f9ebcf5d64b4&scene=21#wechat_redirect")

[百度沧海·存储统一技术底座架构演进](https://link.juejin.cn?target=http%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247601854%26idx%3D1%26sn%3D48b60faa00eae43492615d67c56a74f9%26chksm%3Dc03f7ec2f748f7d4cfb2e6fb9cd7b71e83760e82954af11ee38bd0ef64dd2e1ee49bd2d8d956%26scene%3D21%23wechat_redirect "http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247601854&idx=1&sn=48b60faa00eae43492615d67c56a74f9&chksm=c03f7ec2f748f7d4cfb2e6fb9cd7b71e83760e82954af11ee38bd0ef64dd2e1ee49bd2d8d956&scene=21#wechat_redirect")

[计算不停歇，百度沧海数据湖存储加速方案 2.0 设计和实践](https://link.juejin.cn?target=http%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247601780%26idx%3D1%26sn%3Dc981e3b008de14f90a46146468adcb57%26chksm%3Dc03f7e08f748f71e3e1d2d0a0de0574ca1a71879c6e3219d398668ad150c42994fe008f1171b%26scene%3D21%23wechat_redirect "http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247601780&idx=1&sn=c981e3b008de14f90a46146468adcb57&chksm=c03f7e08f748f71e3e1d2d0a0de0574ca1a71879c6e3219d398668ad150c42994fe008f1171b&scene=21#wechat_redirect")