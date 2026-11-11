---
title: '深度学习在花椒直播的应用——Tensorflow   原理篇'
company: 360
tag: 工程相关
date: 2019-08-28
url: http://mp.weixin.qq.com/s?__biz=MzkzNzI0MDMxNQ==&mid=2247487361&idx=2&sn=36cb82dd07dafa41ddd7b983f2c44649&chksm=c2933c15f5e4b503af0ac18437085f8928b09261e379e4d5a0628a386f2cefd4cbccb110ab60&mpshare=1&scene=1&srcid=0117dqnVg0mxFOFbynlpzCf9&sharer_sharetime=1673957459189&sharer_shareid=c032e8bde4d276951619cca1ff0debb1#rd
account: 360技术工程
origin: readme
---
**奇技指南**

本文作者：殷雅俊，2018年北京邮电大学硕士毕业，自2017年下半年来一直在花椒实习，随后进入花椒直播智能工程组担任算法工程师，主要负责花椒直播个性化推荐算法研发，花椒图像识别算法研发等工作。

本文来自**花椒技术**投稿。

***01***

**深度学习的应用**

**1**

**花椒直播的深度学习使用**

* 使用Spark进行数据清洗，构建用户画像和物品画像，挖掘数据特征，形成数据集存储在HDFS。
* 使用TensorFlow作为深度学习计算框架，通过Hbox调度深度学习作业，使用集群分布式训练。训练模型使用TF Serving部署，封装成TF-Web对内提供预测接口，线上使用Go Server提供推荐服务。

![](https://mmbiz.qpic.cn/mmbiz_png/cFX0EbKicKhQKloXoc3v2e2icpQbqpLiciaYmsutzE3mbDumpeGgsfTxr0DycSbJWw8ia2Ycxfe718qIT5Ok1bMr1RQ/640?wx_fmt=png)

**2**

**TensorFlow和TensorSlow**

TensorFlow是Google在2015年开源的深度学习框架，是目前最主流的深度学习计算框架。代码库本身有高达100万+的代码量，分为前端代码和后端代码。如此庞大的代码量造成了很多人不理解TensorFlow到底如何工作。

为此，Github上有个名为**TensorSlow**的项目，使用纯python的方式重构了TensorFlow底层。该项目旨在帮助理解TensorFlow的工作机制而不在意效率，所以取名TensorSlow。本文就以TensorSlow项目为基础，向大家梳理一下TensorFlow底层到底干了哪些事，对理解深度学习框架底层原理大有裨益。

***02***

**深度学习简介**

深度学习是机器学习的重要分支，是为了研究深层神经网络的结构和有效训练而演化来的一系列方法。

**1**

**神经网络**

**概念**：常见的深度模型使用的是前馈神经网络（多层感知机），它使用一个映射函数

![](https://mmbiz.qpic.cn/mmbiz_png/cFX0EbKicKhQKloXoc3v2e2icpQbqpLiciaYicXTpbosxBf6Tj77k1do48Vnn8k5Iicib4uxc2qeiadwalUEib7dCA9bq4A/640?wx_fmt=png)

来定义模型,其中为输入，θ为模型参数。由于模型函数可以和一个有向无环图（DAG）等价，所以被称为网络。

**隐藏层**：映射函数通常是多层的复合函数，例如

![](https://mmbiz.qpic.cn/mmbiz_png/cFX0EbKicKhQKloXoc3v2e2icpQbqpLiciaY4j2Y8EwMPptOPSoNOE5xAgYlMFcNiaTibIpSGRcVzwr0mxibF5cyJ1jMg/640?wx_fmt=png)

输入x是输入层，中间函数对应于隐藏层，输出y是输出层。

**代价函数**：衡量模型函数和数据集之间的距离的函数（最大似然）。它是模型参数θ的函数，记为J(θ)。

**梯度下降**：选择模型参数能使代价函数J(θ)最小化的优化方法。以梯度下降为代表的一系列优化方法，通过向参数θ的负梯度方向迭代，来寻找最优的参数θ。

**数量级**：参数的数量通常有几十万到数百亿不等。

![](https://mmbiz.qpic.cn/mmbiz_png/cFX0EbKicKhQKloXoc3v2e2icpQbqpLiciaYwjdulcR97JoyYiaj1BTcPBq0R1KRln2NKMJcic3bUzCWXTibZlBNgfxOQ/640?wx_fmt=png)

**2**

**前向传播**

当神经网络接收到输入层x后，经过网络不断向前流动，经过每一个隐藏层，最后传播到输出层y的过程，称为*前向传播*。在监督学习中，通常输出层y还会进一步得到代价函数J(θ)。

**3**

**反向传播**

从代价函数J(θ)出发，经过网络向后流动，传播到每一个参数上，计算出J(θ)对该参数θ的梯度的过程，称为*方向传播*。之后，可以通过梯度下降等优化方法，得到模型的最优参数。

***03***

**TensorFlow做了什么？**

**1**

**计算图（Computational Graph）**

深度学习模型的落地离不开**计算图**，**计算图**可以认为是深度模型的描述语言，是神经网络计算的函数描述。计算图被定义为有向图（DAG），其中的节点对应于变量。通过计算图，可以方便的表达复杂计算。

![](https://mmbiz.qpic.cn/mmbiz_png/cFX0EbKicKhQKloXoc3v2e2icpQbqpLiciaY8WurhXrsg8l66zES3OhhibS07HXXU2rS5zEttcU3ibpHqxEXk5gNws5A/640?wx_fmt=png)

上面的图例展示了一个简单的计算图，它对应于这么一个仿射变换:

![](https://mmbiz.qpic.cn/mmbiz_png/cFX0EbKicKhQKloXoc3v2e2icpQbqpLiciaYrg2Vpkx4MO4zVChwYOIuswxMVicia0cqicoByQKVgrI9kZZetsD02Sxuw/640?wx_fmt=png)

其中x是输入节点，A,b 是模型参数。

**2**

**节点（Vertex）**

在计算图中，节点用来表示一个变量。节点的输入和输出称为**Tensor**（它可以是标量，向量，矩阵或者更高维的）。根据输入输出的不同，节点可以分为以下三类：

Placeholder节点：整个计算图的输入节点。节点只有输出值，传递给它的子节点`consumers`。

```
class placeholder:        def __init__(self):                self.consumers = []                _default_graph.placeholders.append(self)
```

Variable节点：计算图中表示模型参数的节点。Variable节点拥有初始值`value`，将输出传递给它的子节点`consumers`。

```
class Variable:        def __init__(self, initial_value = None):                self.value = initial_value        self.consumers = []              _default_graph.variables.append(self)
```

Operation节点：使用Variable节点或Placeholder节点来组成简单的函数，可以通过复合Operation节点来建立复杂网络。它具有输入和输出，输入由父节点`input_nodes`传递，输出传递到子节点`consumers`中。而`compute`方法需要继承，用来表述Operation节点所表示的函数计算。

```
class Operation:        def __init__(self, input_nodes=[]):        self.input_nodes = input_nodes  
        self.consumers = []  
        for input_node in input_nodes:            input_node.consumers.append(self)  
        _default_graph.operations.append(self)  
    def compute(self):        pass
```

Addition Operation的具体写法

```
class add(Operation):        def __init__(self, x, y):        super().__init__([x, y])  
    def compute(self, x_value, y_value):        self.inputs = [x_value, y_value]        return x_value + y_value
```

**3**

**图（Graph）**

使用一个`Graph`类来绑定计算图中的所有节点（opeartions、placeholders和varaibles）。当创建新的graph的时候，可以调用`as_default`方法来设置为这张图的`_default_graph`，这样不用显式地将节点绑定到图中。

```
class Graph:        def __init__(self):        """Construct Graph"""        self.operations = []        self.placeholders = []        self.variables = []            def as_default(self):        global _default_graph        _default_graph = self
```

**4**

**会话（Session）**

完成了图定义，如何执行图？在TensorFlow中，通过定义Session实例，Client将计算图传递给后端，通过`Session.run`方法传递给master执行。

计算图的输出是特定的Operation节点。而输出节点的计算依赖其他中间节点，**必须保证operations是按拓扑顺序执行的，计算节点o**之前，节点o**的所有输入节点已经完成计算**。****比如，要计算z节点必须先计算出中间节点y。这里通过反向的后序遍历来完成拓扑排序。类似的，`Session`可以这么定义:

```
class Session:        def run(self, operation, feed_dict = {}):        """Computes the output of an operation        """        ...  
  
def traverse_postorder(operation):       nodes_postorder = []    def recurse(node):        if isinstance(node, Operation):            for input_node in node.input_nodes:                recurse(input_node)        nodes_postorder.append(node)  
    recurse(operation)    return nodes_postorder
```

`session.run`方法首先对节点进行拓扑排序，并根据排序结果依次计算节点输出，完成图的执行。

**5**

**前向传递算法**

再回顾这张计算图：

![](https://mmbiz.qpic.cn/mmbiz_png/cFX0EbKicKhQKloXoc3v2e2icpQbqpLiciaY8WurhXrsg8l66zES3OhhibS07HXXU2rS5zEttcU3ibpHqxEXk5gNws5A/640?wx_fmt=png)

它对应的放射变换可以用线性变换的方式写出，可以通过之前定义的代码完成前向传递的计算。

![](https://mmbiz.qpic.cn/mmbiz_png/cFX0EbKicKhQKloXoc3v2e2icpQbqpLiciaY7tMttRwNCOMRocgwkiayNpuPOgHxxSjJLIvvB4XRz0TCUvvKqEvxUibA/640?wx_fmt=png)

```
# Create a new graphGraph().as_default()  
# Create variablesA = Variable([[1, 0], [0, -1]])b = Variable([1, 1])  
# Create placeholderx = placeholder()  
# Create hidden node yy = matmul(A, x)  
# Create output node zz = add(y, b)  
session = Session()output = session.run(z, {x: [1, 2]})print(output)
```

可以得到结果：

```
[ 2 -1]
```

**6**

**构建损失函数**

深度学习中，分类任务通常使用交叉熵作为损失函数，它的公式如下：

![](https://mmbiz.qpic.cn/mmbiz_png/cFX0EbKicKhQKloXoc3v2e2icpQbqpLiciaYaC4GA6ORP58vRAlk9UqiaiajJjrlG0cEc5yqZcZibxobc4EFnL8Ww5PSw/640?wx_fmt=png)

其中c是数据集中的真实分类标签。损失函数的Operation节点J由许多基础`Operation`来构建。将输入和参数向量化，并添加节点J，改写后的计算图如下：

![](https://mmbiz.qpic.cn/mmbiz_png/cFX0EbKicKhQKloXoc3v2e2icpQbqpLiciaYLjN4vL6lbTvqas6kg1ejAa7rh4qyposRjC9rlCzpNhsRajxmNQQBRA/640?wx_fmt=png)

```
# Create a new graph  
Graph().as_default()  
  
X = placeholder()  
c = placeholder()  
  
W = Variable([[1, -1],  
              [1, -1]])  
b = Variable([0, 0])  
p = softmax( add(matmul(X, W), b) )  
  
# Cross-entropy loss  
J = negative(reduce_sum(reduce_sum(multiply(c, log(p)), axis=1)))  
  
session = Session()  
print(session.run(J, {  
    X: np.concatenate((blue_points, red_points)),  
    c:  
        [[1, 0]] * len(blue_points)  
        + [[0, 1]] * len(red_points)}))
```

**7**

**梯度下降优化算法**

通过使用梯度下降方法来最小化代价函数，流程如下：

1. 模型参数W和b设置随机初始值。
2. 计算代价函数J对W和b的梯度。
3. 分别在其负梯度的方向上下降一小步(使用`learning_rate`控制步长大小)。
4. 回到步骤2，继续执行。

```
class GradientDescentOptimizer:        def __init__(self, learning_rate):        self.learning_rate = learning_rate            def minimize(self, loss):        learning_rate = self.learning_rate                class MinimizationOperation(Operation):            def compute(self):                # Compute gradients                grad_table = compute_gradients(loss)                                for node in grad_table:                    if type(node) == Variable:                        grad = grad_table[node]                        node.value -= learning_rate * grad                             return MinimizationOperation()
```

`compute_gradients`函数通过反向传递算法计算梯度，`grad_table`字典存放了代价函数J节点对计算图中所有variable节点的当前梯度。

**8**

**反向传递算法**

链式法则是计算梯度的基本法则。下图和公式显示了e对a的梯度计算：

![](https://mmbiz.qpic.cn/mmbiz_png/cFX0EbKicKhQKloXoc3v2e2icpQbqpLiciaY7QMoVYzN3b53osEvUmJ16bunVs9smzofMtSkyUx2N9rGJKotulxffA/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/cFX0EbKicKhQKloXoc3v2e2icpQbqpLiciaYpXicFrfkRWolictd3FzVwZicTXPGCOvCL0kFahodzp0OdZdsy7bENq3bg/640?wx_fmt=png)

反向传递的算法用链式法则来计算节点n的梯度：

    1. J节点自身的梯度为1。

    2. 对任意节点z的所有子节点`consumer`，计算子节点的梯度。

    3. 将子节点的梯度乘以节点z本身的梯度得到J节点对任意节点z的梯度。

按照这种方式，直到反向传递到节点n。如果节点J经过多个路径方向传递到该节点，那么对该节点来自不同路径的梯度求和。

`compute_gradients`方法从J节点开始，使用**BFS**的方式执行上面的流程。它会先计算所有子节点的梯度，然后计算当前节点的梯度，直到传递到输出节点。

```
from queue import Queue  
def compute_gradients(loss):  
    # grad_table[node] will contain the gradient of the loss w.r.t. the node's output        ...    return grad_table
```

**9**

**节点自身的梯度**

`Operation`的自身梯度通过预先定义，使用`RegisterGradient`注册到全局变量`_gradient_registry`中。以`sigmoid`函数为例：

```
@RegisterGradient("sigmoid")def _sigmoid_gradient(op, grad):        sigmoid = op.output  
    return grad * sigmoid * (1-sigmoid)
```

***04***

**实践：搭建MLP**

**MLP**是经典的神经网络，在深度学习中广泛使用。MLP由多个节点层组成，每一层全连接到下一层。除了输入节点，每个节点都是一个带有非线性激活函数的神经元。下面构建了一个含有3个隐层的MLP来进行分类任务：

![](https://mmbiz.qpic.cn/mmbiz_png/cFX0EbKicKhQKloXoc3v2e2icpQbqpLiciaYGlhE28zouGoqhdVDc1yQq9ASyK8e5T8c0kiaTv3CYUZLd7lLvP6IkBw/640?wx_fmt=png)

```
# Create a new graphts.Graph().as_default()  
# Create training input placeholderX = ts.placeholder()  
# Create placeholder for the training classesc = ts.placeholder()  
# Build a hidden layerW_hidden1 = ts.Variable(np.random.randn(2, 4))b_hidden1 = ts.Variable(np.random.randn(4))p_hidden1 = ts.sigmoid(ts.add(ts.matmul(X, W_hidden1), b_hidden1))  
# Build a hidden layerW_hidden2 = ts.Variable(np.random.randn(4, 8))b_hidden2 = ts.Variable(np.random.randn(8))p_hidden2 = ts.sigmoid(ts.add(ts.matmul(p_hidden1, W_hidden2), b_hidden2))  
# Build a hidden layerW_hidden3 = ts.Variable(np.random.randn(8, 2))b_hidden3 = ts.Variable(np.random.randn(2))p_hidden3 = ts.sigmoid(ts.add(ts.matmul(p_hidden2, W_hidden3), b_hidden3))  
# Build the output layerW_output = ts.Variable(np.random.randn(2, 2))b_output = ts.Variable(np.random.randn(2))p_output = ts.softmax(ts.add(ts.matmul(p_hidden3, W_output), b_output))  
# Build cross-entropy lossJ = ts.negative(ts.reduce_sum(ts.reduce_sum(ts.multiply(c, ts.log(p_output)), axis=1)))  
# Build minimization opminimization_op = ts.train.GradientDescentOptimizer(learning_rate=0.03).minimize(J)  
# Build placeholder inputsfeed_dict = {    X: np.concatenate((blue_points, red_points)),    c:        [[1, 0]] * len(blue_points)        + [[0, 1]] * len(red_points)  
}  
# Create sessionsession = ts.Session()  
# Perform 100 gradient descent stepsfor step in range(2000):    J_value = session.run(J, feed_dict)    if step % 100 == 0:        print("Step:", step, " Loss:", J_value)    session.run(minimization_op, feed_dict)
```

通过可视化决策边界，可以发现模型学习到了比较复杂的非线性关系。

![](https://mmbiz.qpic.cn/mmbiz_png/cFX0EbKicKhQKloXoc3v2e2icpQbqpLiciaYnribqloChW7K7QpPPcszKvicjbTyjNQWyHXJN0XmKS5tk0kCU3zPwz1Q/640?wx_fmt=png)

***05***

**联系TensorFlow**

1. TensorSlow简单深刻的展示了深度学习框架底层的一般原理，加深理解生产使用的TensorFlow。
2. TensorFlow后端使用C++高效实现。
3. TensroFlow优化了算法过程，比如公共表达式消除，常量折叠。
4. TensorFlow支持分布式，支持GPU等硬件设备。
5. TensorFlow提供生产化的一系列工具。

***06***

**主要参考资料**

1. https://colah.github.io/posts/2015-08-Backprop/
2. www.cs.columbia.edu/~mcollins/ff2.pdf
3. http://www.cs.cornell.edu/courses/cs5740/2017sp/lectures/04-nn-compgraph.pdf
4. 《TensorFlow 内核剖析》刘光聪
5. 《深度学习》Ian Goodfellow, Yoshua Bengio

界世的你当不

只做你的肩膀

无

![](https://mmbiz.qpic.cn/mmbiz_jpg/IwabbYzTYkarkIl1KopUUxZS4ZCmea0XFRGRxLLb6Y17bFVmUyI8KWWgU57WuRwUPv2ha3hECsLD5uFtKWI2Ew/640?wx_fmt=jpeg)

![](https://mmbiz.qpic.cn/mmbiz_jpg/IwabbYzTYkarkIl1KopUUxZS4ZCmea0X2N0597gT9OTfiaPltXHFp6cVFzuT5vnfblud74V4vc55ibNJmoJtaCgw/640?wx_fmt=jpeg)

360官方技术公众号

技术干货|一手资讯|精彩活动

空·

![](https://mmbiz.qpic.cn/mmbiz_gif/IwabbYzTYkarkIl1KopUUxZS4ZCmea0Xu9HqPkqXdqgm6yKvicYSBcvGUPbycd3F0dDlneayX58JnDzq64g8I3A/640?wx_fmt=gif)

**更多精彩内容“阅读原文”**

**右边给我一朵小花花**

![](https://mmbiz.qpic.cn/mmbiz_gif/IwabbYzTYkarkIl1KopUUxZS4ZCmea0Xu9HqPkqXdqgm6yKvicYSBcvGUPbycd3F0dDlneayX58JnDzq64g8I3A/640?wx_fmt=gif)