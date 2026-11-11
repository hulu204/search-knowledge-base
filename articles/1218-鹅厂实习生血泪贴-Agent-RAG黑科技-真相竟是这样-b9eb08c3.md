---
title: '鹅厂实习生血泪贴：Agent/RAG黑科技，真相竟是这样！'
company: 腾讯
tag: 问答/RAG
date: 2025-06-16
url: http://mp.weixin.qq.com/s?__biz=MjM5ODYwMjI2MA==&mid=2649793971&idx=1&sn=2e346cdcff335433dfdbe308f0a1e290&chksm=becc36c889bbbfde80e0394f654f4550303b0dee4545ca0f55effee305ca898929f99e702daf#rd
account: 腾讯技术工程
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/sz_mmbiz_gif/j3gficicyOvasVeMDmWoZ2zyN8iaSc6XWYj79H3xfgvsqK9TDxOBlcUa6W0EE5KBdxacd2Ql6QBmuhBJKIUS4PSZQ/640?wx_fmt=gif&from=appmsg)

作者：33号实验室/knnwang

> 被Agent/RAG吊打？你缺的不是智商，是这篇文章！ 亲历鹅厂IEG/WXG项目实战，大三菜鸟用血泪debug记录， 撕开AI基石真面目 → 黑科技本质 = \_\_\_\_\_\_！ 连夜肝出 「人话说明书+通关路线图」 ， 即学即用！青铜连夜上分，帮助大家快速入门Agent/RAG （文章前半部分会介绍Agent，后半部分讨论RAG，最后还分享了优化RAG的一些tips，希望能帮助到大家！！）

### **1 AI的记忆管家与知识向导**

**当AI需要靠谱的知识而不是“胡说八道”时，就是我闪亮登场的时刻！**

#### **1.1 嗨，我是RAG！我决定不再让AI“凭空想象”**

你肯定遇到过那些场面：你的AI助手自信满满地告诉你“北京在长江以南”，或者信誓旦旦地说“牛顿发明了电灯泡”，是不是让人啼笑皆非？这些就是所谓的“幻觉”——就像你有一个知识渊博但偶尔会“异想天开”的朋友。唉，这就是我诞生之前的AI常态。

**我就是为解决这个问题而生的！**

我的全名是**检索增强生成（Retrieval Augmented Generation）**，你可以叫我RAG。简单说，我就是给AI装上的那个“事实核查器”！当AI需要回答问题时，我会先让它去查阅可靠的资料库，而不是坐在那里闭门造车、凭空编造。想象一下，一个认真的学生在考试前会先翻书复习，而不是瞎猜答案——我就是那个督促AI“翻书”的机制。今天，就让我亲自带你们了解一下我的工作原理、如何让我变得更强，以及我未来会变成什么样。虽然听起来有点技术含量，但我会用有趣的方式讲给你听！

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPvMtibFnEqQ5CeJy1PC3vg0VxTvMtnev27icN6WtCFoFJZ7hfEaqCt0Uw/640?wx_fmt=png&from=appmsg)

#### **1.2 我的基本功：强大的“查字典”技能**

##### **1.2.1 我是什么？**

想象一下，如果你是一位外科医生。大部分手术流程你都烂熟于心，但遇到一个罕见病例时，你会怎么办？没错，你会去查医学文献或者请教专家。**我的核心能力，就是赋予AI这种“查阅外部知识”的本事！**

本质上，我是一个技术框架，巧妙地把**检索系统**和**生成式AI模型（比如你们熟悉的大语言模型LLM）** 结合在一起。当用户提问时，我会先指挥检索系统去庞大的知识库里找到最相关的信息片段，然后把这些“证据”交给LLM，让它基于这些真实可靠的信息生成最终回答。这就相当于给AI配了一个**专属的“私人图书馆”** 和一个**超级高效的“图书管理员”（那就是我啦！）**——你需要什么，我立刻帮你找到、整理好！

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPn33bIru11oibGtbo89jwWhnq3IK2CaGHPH4hoPdRpckLicPBuvk5G8lw/640?wx_fmt=png&from=appmsg)

##### 1.2.2 我是怎么工作的？

我的工作流程就像一位高效的办公助理在处理你的请求，分三步走：

1.**检索（Retrieval - 我的搜索时间）：** 当你抛出问题，我立刻将它转化成一种我能理解的“查询向量”，然后一头扎进知识库的海洋，快速捞出最相关的文档或信息片段。这就像你的助理收到任务，立刻跑去档案柜精准查找文件。

2.**增强（Augmentation - 我的整理时间）：** 找到这些宝贝信息后，我可不会直接丢给LLM。我会精心地把它们和你的原始问题融合在一起，打包成一个信息更丰富、背景更清晰的“增强提示”。这就好比你的助理把找到的所有资料整理成一份重点突出、条理清晰的简报，准备呈报给老板。

3.**生成（Generation - LLM的表演时间）：** 最后，LLM这位“决策者”登场了！它基于我精心准备的“增强提示”，结合自身的理解能力，生成最终的、有据可依的回答。就像老板审阅了助理的简报后，给出了深思熟虑的解决方案。

##### **1.2.3 衡量我表现的关键指标**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPXibQmBPS8kaIC1dc9LKoZO4VaqlPFvBUkPfymRpPJSbe7XCE3dGOhZw/640?wx_fmt=png&from=appmsg)

想看看我这个“图书管理员”兼“助理”干得怎么样？主要看两个“成绩单”：

* **召回率（Recall - 我的找书能力）：** 这衡量我在知识库里能成功找到多少真正相关知识的比例。召回率高，说明我“找得全”，不会漏掉重要资料。就像图书管理员能帮你找到几乎所有相关书籍。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPJk62gAk8vYZnliaibM5CwlgLiaMVKibMgHjUVb4OvC5bEPdauYyrX8Yj9Q/640?wx_fmt=png&from=appmsg)

* **忠实度（Faithfulness - 我的诚实度）：** 这衡量我最终让LLM生成的内容，到底有多忠实于知识库里的原始信息。忠实度高，说明LLM“编造”得少，传达准确。就像你的助理在汇报时，能原原本本地传达文件内容，而不是添油加醋或者自己瞎发挥。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPlf8zP7ianQic0mPyxnYaAmXrWEyzbFsaL82sj9vKNnMUAwicV7PpAgwEw/640?wx_fmt=png&from=appmsg)

#### **1.3. 我的成长之路：从“菜鸟”到“高手”的优化之道**

坦白说，我刚“上岗”时表现可不咋地。就像文档里提到的，召回率才25.4%，忠实度才27.2%——活脱脱一个满腔热血但毛手毛脚的实习生！那我是怎么一步步变强的呢？

##### **1.3.1 优化我的“字典”——知识库**

如果给我的知识库一团糟——就像文档里说的“知识库混乱，评估规则口口相传，靠经验”——那就像给一个学生一本错误百出、章节乱序的教科书，我再聪明也使不上劲啊！

**我的优化秘籍：**

* **知识结构化（整理我的书架）：** 把那些杂乱无章的非结构化文本，变成整齐的结构化数据。就像把一堆散乱的笔记，分门别类整理成清晰明了的笔记本。
* **知识更新机制（让我的字典不过时）：** 文档里提到“构建定时器，加入裁判大模型构建自动化评估脚本”——这太关键了！我需要定期更新我的知识库，并用“裁判”模型自动检查内容质量，确保我掌握的都是最新、最准确的信息。
* **知识冗余消除（清理我的书库）：** 把那些重复的、过时的、或者互相矛盾的信息清理掉。就像图书馆定期下架旧书和处理复本一样。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPQeYKma61O3ocLDhN0V1n47efPKgUj9gIbjenZaiaUYcCrwA6n3OM3qw/640?wx_fmt=png&from=appmsg)![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPtg7WeRNHpWuezVicPRMmfFuibuVBJQic2okMMyxCSjwAhl7rnFlGvuw4g/640?wx_fmt=jpeg&from=appmsg)

##### **1.3.2 优化我的“查资料”技巧——检索策略**

召回率目标要从可怜的25.4%提升到90%！这意味着我要从“只能找到四分之一相关书”的菜鸟，变成“几乎能找全所有资料”的资深管理员。

**我的升级手段：**

* **混合检索策略（十八般武艺都用上）：** 我不再只用一种方法找资料。我会结合关键词检索（按书名/作者找）、语义检索（按意思找）、知识图谱检索（按知识关联找）等多种手段。就像同时用分类号、作者索引和主题词来帮你找书。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPggHHXebCvHhKibibhicWpGLbv4uqicfoWaY813z2gYP2JFhVBdYTs9liazw/640?wx_fmt=png&from=appmsg)

* **查询重写与扩展（理解你的言外之意）：** 我会对你的原始问题进行“深加工”——改写得更清晰，或者扩展出相关的主题。这样就能找到更多你可能真正需要的资料。就像图书管理员不仅给你找你要的那本书，还会推荐相关领域的其他好书。
* **上下文感知检索（记住我们的对话）：** 我会留意我们之前的聊天记录和你的背景信息。这样我就能更精准地理解你这次提问的意图。就像图书管理员记得你上次借了科幻小说，这次可能对科幻新书更感兴趣。
* **检索结果重排序（把最好的放前面）：** 初步找到一堆资料后，我会进行二次排序，把最相关、最有价值的信息排在最前面。就像图书管理员不仅找到了书，还按重要性给你排好了顺序。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPnEtjHjzcht3OfvSLr3jEdZgtDqbgWGdzaib7tRVZrar5zy1vKVphFeA/640?wx_fmt=png&from=appmsg)

##### **1.3.3 优化我的“表达方式”——生成策略**

另一个关键目标是大幅降低“幻觉率”（即瞎编乱造），目标降到10%以下！这意味着我要让LLM这个“演讲者”从“大部分内容靠编”进化到“90%以上都有真凭实据”。

**我的调教方法：**

* **引用增强（标明信息来源）：** 我会要求LLM在生成内容时，明确标注出哪些信息来自知识库的哪部分。就像写学术论文必须注明参考文献一样，清清楚楚。
* **不确定性表达（诚实比瞎猜强）：** 如果知识库里确实没有足够的信息来回答你的问题，我会让LLM坦率地说“这个我不太确定”或者“目前我掌握的信息不足以回答”，而不是硬着头皮编一个可能错误的答案。做个诚实的顾问很重要！
* **多样性采样控制（在框架内发挥）：** 我会调整LLM生成过程中的“随机性”程度，在允许它灵活表达的同时，牢牢控制它不偏离检索到的真实信息这个核心框架。就像即兴演讲可以精彩，但不能跑题胡说。
* **后处理验证（最后一道质量关）：** 生成答案后，我还会请其他专门的“验证模型”或者设定好的规则来检查一下内容的准确性。这就像出版前的最后一道事实核查工序。

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPdNrDy2z4Kzt7Sb04WjhOhtHx7pWAibOibVacQL9yKjGb5gickMSvj3cCA/640?wx_fmt=jpeg&from=appmsg)

##### **1.3.4 利用ragas评估自己的RAG**

RAGAS (Retrieval-Augmented Generation Assessment) 它是一个框架([ragas源码](https://gitcode.com/gh_mirrors/ra/ragas?utm_source=csdn_github_accelerator))，它可以帮助我们来快速评估RAG系统的性能，为了评估 RAG 系统。

**（1）环境配置**

```
pip install ragas  
pip install langchain  
pip install chromadb
```

接下来我们需要导入存放Openai的api\_key,这里我们会使用openai的gpt-3.5-turbo,对它的评估结果进行比对.

```
import os  
import google.generativeai as genai  
from dotenv import load_dotenv, find_dotenv  
   
#导入.env配置文件  
_ = load_dotenv(find_dotenv()) 
```

**（2）Embeddings模型配置**

```
from langchain.embeddings import HuggingFaceBgeEmbeddings  
   
#创建BAAI的embedding  
bge_embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5",  
                                          cache_folder="D:\\models")
```

**（3）加载文档**

```
from langchain.document_loaders import WebBaseLoader  
   
urls = "https://baike.baidu.com/item/恐龙/139019"  
loader = WebBaseLoader(urls)  
docs = loader.load()
```

**（4）创建父子文档检索器**可参考这篇文章学习，在实践过程中，父子文档检索是一种特别好用的技术 [父子文档技术](https://www.53ai.com/news/dify/2025010728651.html)

```
from langchain.text_splitter import RecursiveCharacterTextSplitter  
from langchain.retrievers import ParentDocumentRetriever  
from langchain.storage import InMemoryStore  
from langchain.vectorstores import Chroma  
  
#创建主文档分割器  
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)  
  
#创建子文档分割器  
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)  
  
# 创建向量数据库对象  
vectorstore = Chroma(  
    collection_name="split_parents", embedding_function = bge_embeddings  
)  
# 创建内存存储对象  
store = InMemoryStore()  
#创建父文档检索器  
retriever = ParentDocumentRetriever(  
    vectorstore=vectorstore,  
    docstore=store,  
    child_splitter=child_splitter,  
    parent_splitter=parent_splitter,  
#     verbose=True,  
    search_kwargs={"k": 2}  
)  
  
#添加文档集  
retriever.add_documents(docs)
```

**（5）创建Chain**

LangChain介绍：https://www.langchain.com/

```
from langchain.prompts import ChatPromptTemplate  
from langchain.schema.runnable import RunnableMap  
from langchain.schema.output_parser import StrOutputParser  
from langchain.chat_models import ChatOpenAI  
# from langchain_google_genai import ChatGoogleGenerativeAI  
  
# 创建模型实例  
# model = ChatGoogleGenerativeAI(model="gemini-pro")  # 使用Gemini模型  
  
# 创建OpenAI模型  
model = ChatOpenAI()  
  
# 创建提示模板  
template = """你是一个问答助手。  
请根据以下提供的上下文回答问题。  
如果你不知道答案，请直接说不知道。  
回答限制在两句话以内，并保持简洁。  
问题: {question}   
上下文: {context}   
答案:  
"""  
  
# 根据模板生成提示  
prompt = ChatPromptTemplate.from_template(template)  
  
# 创建链式流程  
chain = RunnableMap({  
    "context": lambda x: retriever.get_relevant_documents(x["question"]),  # 获取与问题相关的文档作为上下文  
    "question": lambda x: x["question"]  # 提取问题  
}) | prompt | model | StrOutputParser()  # 将流程串联：上下文+问题 -> 提示 -> 模型 -> 输出解析
```

**（6）创建文档集**

RAGAS需要以下信息:

question：用户输入的问题。 answer：从 RAG 系统生成的答案(由LLM给出)。 contexts：根据用户的问题从外部知识源检索的上下文即与问题相关的文档。 ground\_truths： 人类提供的基于问题的真实(正确)答案。 这是唯一的需要人类提供的信息。

```
from datasets import Dataset  
  
# 修改后的问题列表  
questions = [  
    "恐龙的名字是怎么来的？",  
    "恐龙的分类有哪些？",  
    "哪种恐龙的体型最大？",  
    "最长的恐龙是什么？它是在哪里发现的？",  
    "恐龙是如何繁殖后代的？",  
    "恐龙是冷血动物还是温血动物？",  
    "小行星撞击是恐龙灭绝的主要原因吗？",  
    "恐龙灭绝发生在什么时间？",  
    "鳄鱼和恐龙有亲缘关系吗？",  
    "恐龙在英文中如何称呼？"  
]  
  
# 修改后的参考答案列表  
ground_truths = [  
    ["1841年，英国科学家理查德·欧文在研究一些像蜥蜴骨头的化石时，认为它们属于一种史前生物，并将其命名为恐龙，意为‘令人恐惧的蜥蜴’。"],  
    ["恐龙可以分为两大类：鸟类恐龙和非鸟类恐龙。"],  
    ["恐龙总体来说体型庞大，其中蜥脚类恐龙是已知的最大种类。"],  
    ["目前已知最长的恐龙是梁龙，体长可达27米，它于1907年在美国怀俄明州被发现。"],  
    ["恐龙通过产卵并孵化的方式繁衍后代。"],  
    ["研究表明，恐龙既不是典型的冷血动物，也不是完全的温血动物，而是介于两者之间的一种状态。"],  
    ["最新研究显示，小行星撞击地球可能并非恐龙灭绝的唯一原因，当时脆弱的生态系统才是导致灭绝的关键因素。"],  
    ["恐龙灭绝的时间大约是6500万年前，地质年代属于白垩纪末期或第三纪初期。"],  
    ["鳄鱼是恐龙的现代近亲，但它们与非鸟类恐龙的关系比鸟类更远。"],  
    ["‘dinosaur’一词由英国古生物学家理查德·欧文于1842年提出，来源于希腊语中的‘deinos’（恐怖的）和‘sauros’（蜥蜴）。"]  
]  
  
answers = []  
contexts = []  
  
# 推理过程  
for query in questions:  
    answers.append(chain.invoke({"question": query}))  # 调用链式流程生成答案  
    contexts.append([docs.page_content for docs in retriever.get_relevant_documents(query)])  # 获取相关上下文  
  
# 构造数据字典  
data = {  
    "question": questions,  # 问题  
    "answer": answers,      # 模型生成的答案  
    "contexts": contexts,   # 相关上下文  
    "ground_truths": ground_truths  # 参考答案  
}  
  
# 将字典转换为数据集  
dataset = Dataset.from_dict(data)
```

**（7） 评估**

最后我们来让RAGAs对我们的问答集进行评估，我们选择了：context\_precision、context\_recall、faithfulness、answer\_relevancy这4个作为我们的评估指标：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPJTqiazSvBMRib3Sst3vxQnpOOFz693xQ63PKNKNqzZW3MW5AZShmqDfA/640?wx_fmt=png&from=appmsg)

```
#openai的结果  
from ragas import evaluate  
from ragas.metrics import (  
    faithfulness,  
    answer_relevancy,  
    context_recall,  
    context_precision,  
)  
  
result = evaluate(  
    dataset = dataset,   
    metrics=[  
        context_precision,  
        context_recall,  
        faithfulness,  
        answer_relevancy,  
    ],  
)  
  
df = result.to_pandas()  
df
```

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPkA9YKmyJcico3AjyZrRWE6iaBShK0OHcX5Mic2iawkKQZ6ic7LmEwMy8Euw/640?wx_fmt=png&from=appmsg)

优化RAG的小tips： 注：如果把前面说的优化方式都做的很好了，RAG的效果大多数都可以做的很不错，下面会介绍更底层的一些优化方式。

1.分词预处理优化

（1）常规方法 文本的分词直接通过`text.split()`处理，即会将空格，制表符\t、换行符\n等字符，作为分隔依据，这样操作太过简单。

（2）改进方式

```
1. 预处理：  
   - 将所有非单词字符（字母、数字、下划线以外的）替换为空格。  
   - 全角字符转半角。  
   - 转换为小写。  
   - 繁体中文转简体中文。  
2. 按语言切分：  
   - 将预处理后的文本按语言（中文/非中文）分割成多个片段。  
3. 分段处理：  
   - 对于非中文（通常是英文）片段：  
     - 使用 NLTK 的 `word_tokenize` 进行分词。  
     - 对分词结果进行词干提取 (PorterStemmer) 和词形还原 (WordNetLemmatizer)。  
   - 对于中文片段：  
     - 如果片段过短（长度<2）或为纯粹的英文/数字模式（如 "abc-def", "123.45"），则直接保留该片段。  
     - 否则，采用基于词典的混合分词策略：  
       a. 执行正向最大匹配 (FMM) 和逆向最大匹配 (BMM) 得到两组分词结果 (`tks` 和 `tks1`)。  
       b. 比较 FMM 和 BMM 的结果：  
          i.  找到两者从开头开始最长的相同分词序列，这部分通常是无歧义的，直接加入结果。  
          ii. 对于 FMM 和 BMM 结果不一致的歧义部分（即从第一个不同点开始的子串）：  
              - 提取出这段有歧义的原始文本。  
              - 调用 `self.dfs_` (深度优先搜索) 在这段文本上探索所有可能的分词组合。  
              - `self.dfs_` 会利用Trie词典，并由 `self.sortTks_` 对所有组合进行评分和排序。  
              - 选择得分最高的分词方案作为该歧义段落的结果。  
          iii.继续处理 FMM 和 BMM 结果中歧义段落之后的部分，重复步骤 i 和 ii，直到两个序列都处理完毕。  
       c. 如果在比较完所有对应部分后，FMM 或 BMM 仍有剩余（理论上如果实现正确且输入相同，剩余部分也应相同），  
          则对这部分剩余的原始文本同样使用 `self.dfs_` 进行最优分词。  
4. 后处理：  
   - 将所有处理过的片段（英文词元、中文词元）用空格连接起来。  
   - 调用 `self.merge_` 对连接后的结果进行进一步的合并操作，  
     尝试合并一些可能被错误分割但实际是一个完整词的片段（基于词典检查）。  
5. 返回最终分词结果字符串（词元间用空格分隔）。
```

专门配置一个词典，用来记录常见词汇，词频，词性等信息。为加速查询速度，构建一个Trie树的形式(huqie.txt.trie)。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPNdBrFTrpld4ZoTro1eyylmI1mkgquZicWJFYiaPsnvQ9wGEXXRicjG6DA/640?wx_fmt=png&from=appmsg)

#### 1.4.文档解析（PDF）

要用好rag的输出增强效果，文档解析是关键一环。如果文档解析块存在问题，那么后面检索到的内容，也会对模型造成错误干扰。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnP5IIPJ9e25rMy6EzibHqJcFplmUfLmDriadGV32tRxP0yN5pEs9VaOBCQ/640?wx_fmt=png&from=appmsg)

经调研，开源的文档解析产品主要有`MinerU`、`Marker`、`MarkItDown`、`Docling`四款主流产品。对于`Doc2X`，`TextIn`等未开源的收费产品，不在本文的考虑范围之内。

这四款开源产品及对应的开发公司如下表所示：

| 工具名称 | 开发团队/公司 |
| --- | --- |
| **MinerU** | 上海AI实验室(OpenDataLab) |
| **Marker** | VikParuchuri（个人开发者） |
| **MarkItDown** | 微软（Microsoft） |
| **Docling** | IBM |

考虑到本地部署，需要优先支持中文文档的解析，大致浏览了一下这四款产品的仓库，发现`MinerU`的生态非常完善，并且文档都有中文版本，对本土开发者非常友好，于是对其进行研究。MinerU 有在线试用网页，可让用户直接上传文件进行解析。地址如下：

<https://mineru.net/OpenSourceTools/Extractor>

我上传了中相同的论文，相同部分解析效果如下：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPB32icJFV95wcwSIODUAW0oZq4fu2QrtjJveIQfJSs3WOZibeaxicnqHTg/640?wx_fmt=png&from=appmsg)

### **2 智能体（Agent）的定义与历史**

#### 2.1 **OPENAI在AGI五级分类中对agent的定义**

**想象一下人工智能的进化阶梯，就像是从幼儿园到博士后的成长之路。OpenAI给我们画了一幅AI成长的"五年级"照片墙：**

**第1阶段：会聊天的AI（Conversational AI）** 这就像是刚学会说话的小朋友，能和你有来有往地聊天，比如我们熟悉的ChatGPT。它能回答你"今天天气怎么样"，但别指望它能帮你收拾房间——它只会说，不会做！

**第2阶段：会思考的AI（Reasoners）** 这是已经上了小学的AI，不仅会说，还会动脑筋。它能在学术领域大显身手，解决复杂问题，就像那个总是举手回答问题的班上小天才。"老师，我知道这道微积分题怎么解！"

**第3阶段：会自主行动的AI（Agents）** 这是已经能独立生活的青少年AI，可以自己做决定并付诸行动。它不需要你时刻盯着，能自己管理日程、回复邮件，就像你雇了一个永不疲倦的私人助理，而且不用发工资！

**第4阶段：会创新的AI（Innovators）** 这是已经成为创意总监的AI，不仅解决问题，还能提出新点子。它可能某天早上醒来说："嘿，我想到了一种全新的能源技术！"然后真的帮你设计出来。这时候，人类工程师可能要开始担心自己的饭碗了。

**第5阶段：会管理的AI（Organizers）** 这是已经坐上CEO宝座的AI，能管理整个组织，协调复杂流程，效率比人类还高。想象一下，你公司的老板是个AI，每天早上准时发布完美的工作安排，从不偏袒任何人（除了可能对打印机特别友好）。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPGvf2magSDPSTkROBl8yWX00Nicq8OdVADj2bjELfcm4W7TupcZsAxwg/640?wx_fmt=png&from=appmsg)

#### 2.2 智能体的核心定义

##### 2.2.1 智能体（Agent）是什么？

简单来说，智能体就是一个数字版的"全能选手"，它能看（感知）、想（决策）、做（执行）、学（学习）：

**感知**：就像你的眼睛和耳朵，智能体通过各种"传感器"获取信息。它的"眼睛"可能是摄像头，"耳朵"可能是麦克风。

**决策**：这是智能体的"大脑"，通过复杂算法做出判断。想象一个内置GPS的出租车司机，不断计算最佳路线。

**执行**：智能体的"手脚"，可能是机械臂，也可能是软件指令。就像你决定吃披萨后，手会自动拿起电话叫外卖。

**学习**：智能体的"成长能力"，它会从经验中学习。就像玩游戏，玩得越多，技术越好，不会一直犯同样的错误（理想情况下）。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPhdmHqOQ1lZrEWOBa4t4If8doeVEhncRyIz0mTPCm7przGYkrlCibpiaA/640?wx_fmt=png&from=appmsg)

##### 2.2.2 智能体的历史沿革

智能体的发展历程就像是从图书馆管理员到自学成才的天才的进化：

**1960～1980年代：规则驱动的智能体** 这是"图书馆管理员"阶段。所有知识都必须手动输入，就像是给AI准备了一本厚厚的"生活指南"。问题是，一旦遇到指南上没有的情况，它就傻眼了——"对不起，我的说明书上没写这个"。

**1990～2010年代：强化学习驱动的智能体** 这是"试错学习"阶段。AI开始通过不断尝试来学习，就像教宝宝走路——摔倒了再爬起来，慢慢就会了。"我上次这么做摔了一跤，这次我换个方法试试。"

**2020年代至今：大模型驱动的智能体** 这是"博览群书"阶段。大语言模型（LLM）让AI能理解和生成人类语言，不需要事无巨细的指导就能完成任务。就像那个不仅读过所有书，还能举一反三的学霸，"虽然我没做过这个具体任务，但根据我的知识，应该这样解决..."

#### 2.3 与其讨论 Agent，不如讨论 Agentic

讨论一个系统有多"Agentic"（具有智能体特性），就像讨论一个人有多"成人"——关键在于它能自己做多少决定：

**使用LLM将输入路由到特定下游工作流**： 这就像是个接线员，只负责把你的电话转给合适的部门。"您好，要查询账单请按1，要投诉请按2..."

**使用多个LLM进行多级路由决策**： 这是升级版接线员，不仅转接电话，还会根据你的问题做初步分析。"您说的问题涉及到账单和配送，我先帮您转到账单部门，然后..."

**如果某个步骤需要决定继续执行还是终止**： 这就像有了一定自主权的助理，能决定是否继续一项任务。"我看这个方案行不通，让我们尝试另一种方法..."

**当系统能自主构建工具、记忆工具并在后续步骤中使用**： 这是真正的"自主智能体"，就像一个全能助手，不仅执行任务，还能创造新工具来解决问题。"我发现这个问题需要特殊工具，我来设计一个，然后用它来解决..."

### 3 基于大模型的智能体的原理

**"LLM Agent：当你的AI助手突然有了上进心"**

这货可不是只会背课文的书呆子！作为大语言模型（LLM）驱动的"最强大脑"，它把简单聊天变成了"智力奥运会"——既能跟你唠嗑，又能干活跑腿，甚至偶尔露出"让我想想"的沉思者表情。

本质上是个披着对话框外衣的瑞士军刀： 🔧 **推理能力** - 堪比福尔摩斯，只是破案速度取决于服务器负载 🧠 **记忆功能** - 像金鱼，但属于那种会做笔记的金鱼 🤖 **自主性** - 约等于"知道主动问你要咖啡"的级别

**LLM Agent****的定义**

LLM Agent 是通过与自身之外的其他系统交互来服务于用户目标的生成式 AI 系统。换句话说，它不仅依赖于自身的计算能力，还需要与其他外部系统协同工作，从而完成更复杂的任务。

**LLM Agent****的核心组成**

• 大语言模型（Large Language Models） ：作为智能体的核心，负责理解和处理自然语言，提供推理和决策能力。

• 工具调用（Tool Invocation） ：智能体可以调用外部工具或 API 来完成特定任务，例如查询数据库、操作文件等。

• 规划（Planning） ：智能体需要根据任务目标制定计划，决定如何使用资源和工具。

• 记忆（Memory） ：智能体需要记住之前的操作和结果，以便在后续任务中参考和优化。

**LLM Agent****的工作流程**

1.感知环境 ：智能体通过与外部环境交互，获取任务需求和相关信息。

2.分析任务 ：利用大语言模型的强大推理能力，分析任务并制定解决方案。

3.执行任务 ：调用外部工具或 API 执行具体操作，逐步完成任务。

4.反馈与优化 ：根据执行结果进行学习和优化，提升未来的表现。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPbtMgNEs5oRPxpfSWNnIy3b5wMg4GYmDTRQBRusa4qvg0B0DktMmUCA/640?wx_fmt=png&from=appmsg)

#### 3.1 **规划（Planning）**

**子目标分解**

• **目的**：复杂任务通常包含多个步骤，智能体（Agent）需要了解这些步骤并提前规划。前面提到的 CoT（Chain of Thought，思维链）及其改进方法，本质上就是在进行任务分解。

• **任务分解实现**：

￮**给****LLM****提示词**：例如，“Steps for XYZ.\n1. What are the subgoals for achieving XYZ?”

￮ **使用具体任务指令**：例如，对于写小说的任务，先给出“Write a story outline.”的指令。

￮ **用户直接输入**：用户可以直接提供任务分解的步骤。

**关键点**

• **CoT****和****ToT****的本质**：无论是 CoT 还是 ToT（Thoughts on Thoughts），本质上都是通过精心设计的提示词（Prompt），激发模型原有的元认知能力（Metacognition）。也就是说，通过某种线索，能够更精准地调动模型中擅长规划的部分。

**LLM+P****方法**

•**整体规划**：LLM+P 是一种利用规划域定义语言（Planning Domain Definition Language, PDDL）来进行长序列任务规划的方法。

• **工作流程**：

a. **问题翻译**：LLM 将问题翻译成 PDDL 格式。

b. **请求经典****Planner**：接着，请求经典 Planner 根据现有的领域 PDDL 生成一个 PDDL Plan（计划）。

c. **翻译回自然语言**：最后，将 PDDL 计划翻译回自然语言（由 LLM 完成）。

• **前提条件**：这种方法需要特定领域的 PDDL 描述和合适的 Planner。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPWlmTTasSh6hyV17hgEQU3MFLDwWqAwruWz8RsTSWbYsAN8WAzY18KQ/640?wx_fmt=png&from=appmsg)

**反思与完善**

**Agent****的自我反思能力**非常重要。它能够对历史动作进行自我批评和反思，从错误中学习，并在后续步骤中不断优化，从而提升最终结果的质量。这种 **自我反思（Self-reflection）** 是 Agent 不断改进的关键环节。在现实世界中，犯错是不可避免的，而自我反思在其中发挥着至关重要的作用。

**ReAct****框架**

ReAct是一种结合了 **Reasoning（推理）** 和 **Action（行动）** 的方法。它的核心思想是通过扩展 Action Space，使其包含特定任务的离散动作和语言空间的组合。具体来说：

1. **Reasoning**：帮助 LLM 与环境进行交互。
2. **Action**：通过提示词，让 LLM 使用自然语言生成完整的推理过程。

ReAct 的提示词模板提供了一个明确的思考步骤，大致格式如下：

Thought: ... Action: ... Observation: ...

**ReAct****的优势**

在知识密集型任务和决策任务的实验中，ReAct 的表现优于传统的单一 **Act...** 方式。这是因为 ReAct 能够更好地结合推理和行动，使 Agent 更加灵活和高效。

**Reflexion****框架**

Reflexion 是一个让 Agent 具备动态记忆和自我反思能力的框架，旨在提高其推理能力。它采用标准的强化学习（RL）设置：

• **奖励模型**：提供简单的二进制奖励（成功或失败）。

• **Action Space**：在 ReAct 的基础上，进一步扩展为特定任务的行动空间，并加入语言支持，以实现更复杂的推理步骤。

在每个行动 a(t) 之后，Agent 会计算一个启发式函数 h(t)，并根据自我反思的结果决定是否重置环境，开始一个新的循环。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPgusoL01MoDia9O2IVia0Pic4hDlWlTwQBWdlvf1qtFubVIGgI0FNDc3iag/640?wx_fmt=png&from=appmsg)

#### 3.2 **记忆（Memory）**

**记忆的分类与实现**

**1.****短期记忆（短期学习）**

• **上下文学习**：这是模型的一种短期记忆能力，类似于人类的短期记忆，能够记住最近的信息或上下文。

**2.****长期记忆**

• **长期记忆功能**：为智能体提供保留和召回长期信息的能力。

• **实现方式**：通过外部向量存储和检索来实现。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPVdO2HSJFRMuMxKEaXiafugt7JGgNc8OD5ftKlhb6jhfvXTV2VVQTv1Q/640?wx_fmt=png&from=appmsg)

**人脑中的记忆类型**

记忆可以定义为用于获取、存储、保留和随后检索信息的过程。人脑中有多种类型的记忆：

1. **感官记忆**：

￮ 这是记忆的最早阶段，是在接受原始刺激后保留的感官信息（如视觉、听觉、触觉）的能力。

￮ 感官记忆通常只能持续几秒钟，主要包括以下几种：

▪ **图示记忆（Iconic memory,****视觉）**：对视觉信息的短暂记忆。

▪ **回声记忆（Echoic memory,****听觉）**：对听觉信息的短暂记忆。

▪ **触碰记忆（Haptic memory,****触觉）**：对触觉信息的短暂记忆。

1. **短时记忆（STM）或工作记忆**：

￮它存储了我们当前意识到的信息，以及执行复杂认知任务（如学习和推理）所需的信息。

￮ 短时记忆被认为有大约 7 个项目的容量，并能够持续 20-30 秒。

1. **长时记忆（LTM）**：

￮ 长时记忆可以将信息存储很长时间，从几天到几十年不等，存储容量基本上是无限的。

￮ 长时记忆分为两种：

▪ **显性/陈述性记忆**：对事实和事件的记忆，指那些可以有意识地回忆起的记忆，包括外显记忆（事件和经历）和语义记忆（事实和概念）。 ▪ **隐形/程序性记忆**：这种记忆是无意识的，涉及自动执行的技能和例行程序，如骑车、在键盘上打字。

**最大内部产品搜索（MIPS）**

为了缓解关注范围有限的限制，可以通过使用外部存储器来优化检索速度。常见的选择是 ANN（人工神经网络）算法，返回近似的 top k 个近邻，用少量精度损失换取速度的巨大提升。以下是几种常见的 ANN 算法选择进行快速 MIPS 的方法：

**LSH（****locality-sensitive hashing）**：

￮ 引入了一种哈希函数，能够最大限度地将相似的输入项映射到同一个桶中，其中桶的数量远小于输入内容的数量。

**ANNOY（Approximate Nearest Neighbors Oh Yeah）**：

￮ 核心数据结构是随机投影树，它是一个二叉树集合，每个非叶子节点表示将输入空间划分为两半的一个超平面，每个叶子节点存储一个数据点。

￮ 这些树是独立随机构建的，在某种程度上，它模拟了一个哈希函数的作用。

￮ ANNOY 的搜索发生在所有树中，迭代地搜索最接近查询的那一半，然后聚合结果。其思想与 KD 树非常相关，但可扩展性更强。

**HNSW（Hierarchical Navigable Small World）**

• **设计思想**：HNSW 的设计理念来源于“小世界网络”理论。在小世界网络中，每个节点只需要通过很少的步骤就可以连接到任何其他节点，就像社交网络中的“六度分隔”现象一样。

**结构特点**：

￮  HNSW 构建了多层的小世界网络结构，底层包含实际的数据点。

￮ 中间层添加了一些“快捷键”，用于加速搜索过程。

**搜索过程**：

￮  在进行搜索时，HNSW 从顶层的一个随机节点开始，逐步导航向目标节点移动。

￮  如果在某一层无法接近目标，它会下降到下一层，直到到达底层。

￮  在上层每一步导航都能潜在地跨越数据空间中的大距离，而在下层每一步导航可以提高搜索的质量。

**FAISS**

• **核心假设**：FAISS 基于一个假设，即在高维空间中，节点之间的距离遵循高斯分布，因此应该存在数据聚类。

• **实现方式**：

￮ FAISS 通过向量量化来实现。首先将向量空间划分为若干集群，然后在每个集群内进行更精细的量化。

￮ 在搜索时，首先使用粗粒度的量化查找可能的集群候选，然后在每个候选集群内使用更细致的量化进行进一步查找。

**ScaNN（Scalable Nearest Neighbor Search）**

•**主要创新**：ScaNN 算法的主要创新在于使用了各向异性向量量化。它对数据点进行向量化，使得内积 <q,> 尽可能与原始距离相似，而不是选择最接近的量化质心点。

#### 3.3 **工具使用（tool use）**

•对模型权重丢失的信息，agent学习调用外部API获取额外信息，包括当前信息、代码执行能力、专有信息源的访问等等。

**智能体与LLM的区别**

**LLM**

和LLM的对话就是：你输入一个提示，大模型生成一个回答。

Plain Text 用户输入：帮我写一篇科幻主题的文章 模型输出：文章xxxxxxxxxxxxxxxxxxxxx

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPXEI3bC4eS3Wd4xGSAnuM64OkpoFBAy4I9Btia8nrwfbot7wj0Dg7Kiag/640?wx_fmt=png&from=appmsg)

**Agent**

和Agent的对话就是：你有一个助手，你不是简单地直接写，先询问你是否需要进行一些网络研究，然后写下初稿，然后回顾初稿，并思考哪些部分需要修改，然后修改草稿，不断进行思考和迭代这个过程。这个流程是一个思考+迭代的过程。

Plain Text 用户输入：帮我写一篇科幻主题的文章 Step 1: 思考和规划 Step 2: 联网搜索 Step 3: 确定主体大纲 Step 4: 优化修改 模型输出：文章xxxxxxxxxxxxxxxxxxxxx

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPAkUJAG5GZBIBnUB5DuNnB1HV7ia28NceCjWTPgCZYpPicHHtHKtZOWMg/640?wx_fmt=png&from=appmsg)

**与强化学习智能体的区别**

• **强化学习智能体**：输入为预设好的向量化的环境状态（或者图像），策略通常由简单的神经网络结构进行初始化，输出动作多为底层控制（移动、攻击等）。

• **基于大模型的智能体**：输入为文字（多模态场景下也会有视觉、语音等信息），策略为预训练的具备世界知识的大语言模型，输出动作为文本，但可以通过结构化输出和提取实现 function\_call，进一步与现实环境进行交互。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPQaHdQXGPH8EGC0DN8cHbw7B9a8xvv0pOc4Y18ic27wU6j2716oYtFSw/640?wx_fmt=png&from=appmsg)

### 4 智能体的分类

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPKr760NqT8UgzmmGTsxz8qUfrtrBLzYGGazDebpvia7PMUzQVbwShh5A/640?wx_fmt=png&from=appmsg)

#### 4.1 **按照数量分类**

• **SingleAgent**：单个智能体进行任务规划与行动。

• **MultiAgent**：强调多样化的 agent profiles，agents 间交流相互作用和集体决策过程。更多动态和复杂的任务可以通过多个自主智能体的协作、辩论、讨论来完成，每个智能体都具有独特的策略和行为，并相互之间进行通信。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPf2bgpVNxNVz8jmWofJlOndJ44K6tS15EibSkeGoM2GJobxFG2yJNfug/640?wx_fmt=png&from=appmsg)

#### 4.2 **按照行为模式分类**

**Tool Use Agent**

•  **MRKL system**：Modular Reasoning, Knowledge, and Language（模块化推理、知识和语言）。一个 LLM 作为 router 提供对多种工具的访问，然后 router 可以多次调用工具获取诸如时间、天气等信息，然后结合这些信息给出回复。下面的相关工作都是类似的技术，大部分还包含了微调：Toolformer、Gorilla、Act-1、Hugging-gpt、ToolkenGPT。

• **CRITIC：Self-Correcting with Tool-Interactive Critiquing**利用工具交互评价来自我修正。首先根据 prompt 生成回答，然后同样的 LLM 对答案中可能出现的错位进行 criticize，最后使用相应的外部工具，如联网搜索、代码解释器对部分回答进行验证或修正。CRITIC 流程图：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnP0oP9pkJX56icsTvog9FicZ8GgPOVx7VqEibxxyfkjw8tC3kbxliciaia353w/640?wx_fmt=png&from=appmsg)

**Code Generation Agent**

代码编写和执行能力也是一项重要的 Agent 能力，也可以被划分为 Tool Use Agents（Tool 就是代码解释器等）。

**1. Program-aided LM**

将问题直接转换为 code，然后利用 Python 解释器生成答案。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPRSR4h45GfHmqGZvMhwfEDvOPHtSKJxQXddeIkoKicO2t1fClm3mYZDQ/640?wx_fmt=png&from=appmsg)

**2. Tool-Integrated Reasoning Agent**

类似 PAL，但是 code 和推理多步交叉直到解决问题。PAL 是单个 code-gen step。下图是 CoT、PAL 和本文的对比：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPrDicRSqlx95svwxtmSNsvn7wkAjOqWGahMXsEUG4bqPwFN6N9vXM4Sg/640?wx_fmt=png&from=appmsg)

**3. TaskWeaver**

也是类似 PAL，但是可以利用用户定义的插件。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPokPRL7RSMiamfUCISFyeUjkmljneKILg5ZCwxCpfgLIerM1H6InCCSg/640?wx_fmt=png&from=appmsg)

**Observation-based Agent**

一些 Agents 被设计为通过与（gym 之类的环境）交互来解决问题，这些基于 Obs 的 Agent 会将接收到的观测插入到 Prompt 中。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPUS2VdlcHhagIicLGlybBZia2RXnKDNnMNtic7CK2XAFlY7W0ldxkj7iakg/640?wx_fmt=png&from=appmsg)

**RAG Agent**

从外部来源（本地知识库等）检索信息并插入 prompt 的范式，可以提高知识密集型任务的性能。RAG 其实也是一种特殊的 Agent，一般都是调用外部数据库/向量库作为工具。

**4.智能体系统分类**

从架构上看，Agentic system 可以分为两大类系统：

• 工作流（Workflow） ：

￮ 通过预定义代码路径编排 LLM 和工具。

￮ 适用于任务明确、步骤可预定义的场景。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPDX64Jiax9x8QqJPP9M9Gfq3g8WsqujjcoFbMGB3ylpVX4ZR5tRPnQdQ/640?wx_fmt=png&from=appmsg)

• 自主智能体（Autonomous Agent） ：

￮ LLM 动态控制决策和工具使用。

￮ 自主规划任务。

￮ 适用于任务步骤难以预知、需长期自主规划的场景。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPNk9FWbYicqX5aYYnYYtACiaKD2YkeohgnS5hG6Nn3tKPyG2GBNp6qwAQ/640?wx_fmt=png&from=appmsg)

### **5 智能体评估框架**

**AgentBench**

AgentBench 的核心思想是，将LLM作为Agent进行评估。

其8种实际场景可以归为三类：

• 编码 ：让LLM生成代码，操作系统、数据库和知识图谱属于编码类型。

• 游戏 ：让LLM扮演游戏角色，数字卡牌游戏、横向思维谜题、持家游戏属于游戏类型。

• Web ：让LLM完成与网页相关的任务，网购和浏览网页属于Web类型。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPyzzWWbvlrbVnWQRR4sKianZ3IEUsicez0iciaeUpmDp6knxonOJhZGPQtA/640?wx_fmt=png&from=appmsg)

### **6 智能体实践**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPaZ5jcDo4AoIQcakCHZVzwKA1O0q34lkicwzhKlgYakFvRsl5YwiakpNg/640?wx_fmt=png&from=appmsg)

（1）基于openai接口实现简单的agent

```
from openai import OpenAI  
import json  
  
# 初始化 OpenAI 客户端  
client = OpenAI(api_key="sk-api_key")  
  
# 定义工具：查询股票价格  
tools = [  
    {  
        "type": "function",  
        "function": {  
            "name": "get_stock_price",  
            "description": "Get the current price of a given stock.",  
            "parameters": {  
                "type": "object",  
                "properties": {  
                    "symbol": {  
                        "type": "string",  
                        "description": "Stock symbol e.g. AAPL, GOOGL"  
                    }  
                },  
                "required": ["symbol"],  
                "additionalProperties": False  
            },  
            "strict": True  
        }  
    }  
]  
  
# 用户消息：询问某只股票的价格  
messages = [{"role": "user", "content": "What's the current price of Apple stock?"}]  
  
# 调用 OpenAI 的 chat completions API  
completion = client.chat.completions.create(  
    model="gpt-4",  
    messages=messages,  
    tools=tools,  
)  
  
# 打印模型的回复  
print(completion.choices[0].message.content)
```

**（2）基于Langchain实现一个简单的React Agent**

```
from langchain.chains import LLMMathChain, LLMChain  
from langchain.agents import Tool, initialize_agent, AgentType  
from langchain.prompts import PromptTemplate  
from langchain import OpenAI  
import os  
  
# 设置 OpenAI API 密钥  
os.environ["OPENAI_API_KEY"] = "your_api_key"  
  
# 初始化 LLM 模型  
llm = OpenAI(temperature=0)  
  
# 工具 1：翻译工具  
def translate_text(text, target_language):  
    """模拟翻译功能，将文本翻译为目标语言"""  
    # 这里可以替换为实际的翻译逻辑，例如调用翻译 API  
    returnf"Translated text: {text} (to {target_language})"  
  
translate_tool = Tool(  
    name='Translator',  
    func=lambda x: translate_text(x['text'], x['target_language']),  
    description='Useful for translating text from one language to another.'  
)  
  
# 工具 2：天气查询工具  
def get_weather(location):  
    """模拟天气查询功能，返回指定位置的天气信息"""  
    # 这里可以替换为实际的天气查询逻辑，例如调用天气 API  
    returnf"Weather in {location}: Sunny with a high of 75°F and low of 60°F."  
  
weather_tool = Tool(  
    name='WeatherChecker',  
    func=lambda x: get_weather(x['location']),  
    description='Useful for getting the current weather for a given location.'  
)  
  
# 将所有工具存进一个数组中  
tools = [translate_tool, weather_tool]  
  
# 初始化 ReAct Agent  
react_agent = initialize_agent(  
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  
    tools=tools,  
    llm=llm,  
    verbose=True  
)  
  
# 测试 ReAct Agent  
print(react_agent.run("What's the weather like in New York?"))  
print(react_agent.run("Translate 'Hello' to Spanish."))  
 
```

**（3）Manus分析****& OpenManus技术方案**

https://manus.im/share/OZB4PvsXY5N5FrvLXqqCl4?replay=1

注：这篇文章很多格式的处理就是通过manus帮我完成的

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavMzRbhL6GBjxAPTXPngtnPvwgxleCZiaadlpcibKjeIlMIfGBePnzYX7WopfbSI00gMFqv9icWtSjzQ/640?wx_fmt=png&from=appmsg)

**Manus****的工作原理**

Manus 是一个多智能体系统，它在完成任务时会按照以下步骤进行：

1.**任务拆分**：

￮ Manus 首先使用 PlanningTool 对任务进行规划，将复杂任务拆分成多个子任务。

￮ 这些子任务会被组织成一个线性的计划，每个任务都有明确的执行顺序。

2.**分配与执行**：

￮ 每个子任务会被分配给相应的智能体（Agent）。

￮ Agent 在执行任务的过程中，会以 ReAct 循环的形式调用工具来完成任务。ReAct 循环指的是“思考（Reason）+ 行动（Act）”，即 Agent 会先思考如何解决问题，然后通过调用工具来执行具体的操作。

3.**记录进度**：

￮ Manus 使用 TODO.md 文件来记录任务的完成情况，帮助跟踪进度。

**Manus****的核心能力**

•  **规划能力**：

￮ Manus 使用 PlanningTool 来规划任务，形成一个清晰的任务分解计划。

￮ 根据测试，这种规划能力在 SWEBench 上的表现非常出色，解决率从 49% 提升到了 70%，其中一部分提升来自于模型本身的优化，另一部分则来自于规划工具的效果。

• **工具使用能力**：

￮ Manus 结合了 Claude+ 和其他经过微调的模型，这些模型在工程上做了大量优化，增强了它们在不同场景下的工具使用能力。

**OpenManus****的特点**

OpenManus 是基于 Manus 的规划优势开发的，它继承了 Manus 的任务分解能力，并在此基础上进行了改进。以下是 OpenManus 的主要特点：

1.**极简可插拔框架**：

￮ OpenManus 的核心是一个简洁的 Agent 框架，强调模块化和扩展性。

￮ 开发者可以通过自由组合 Prompt（提示词）和 Tools（工具），快速定义 Agent 的行为逻辑和功能。

￮ 例如，Prompt 决定了 Agent 的思考方式，而 Tools 则提供了具体的行动能力（如代码执行、搜索、文件操作等）。

2.**工具驱动的****ReAct Agent**：

￮ OpenManus 基于 ReAct（Reason + Act）模式，以工具为核心驱动 Agent 的行动。

￮ Prompt 引导 Agent 的推理和逻辑，而 Tools 则赋予 Agent 行动能力。

￮ 这种设计让 Agent 不仅能“思考问题”，还能“执行任务”。

3.**规划能力处理复杂任务**：

￮ OpenManus 继承了 Manus 的多智能体规划优势，通过 PlanningTool 对用户需求进行高层次的规划。

￮ 它将复杂的任务分解为线性的子任务计划，显著提升了任务的成功率。

￮ 这种“先规划，后执行”的思路，在处理长链条任务时尤为有效。

1. **动态****Agent****分配与工具调度**：

￮ 当一个任务被拆解为多个子任务后，系统会根据任务类型，动态分配给预先定义或适配的 Agent。

￮ 这种“临时分配 + 工具协作”的机制，最大化利用了多模型、多工具的组合优势，提高了系统的灵活性和效率。

**结束语：**

“以上浅见，不过是我在鹅厂的一点实践心得。技术之路没有银弹，Agent与RAG的探索也远未到终局。文中的方案必然存在局限，恳请各位前辈同仁不吝指正。若这些血泪经验能为您节省几分钟调试时间，或带来一丝灵感火花，便已值得。AI浪潮奔涌，愿与诸君共同探索——毕竟，**真正的通关地图，永远由所有实践者共同绘制。**”

### 7.Reference

1.33号实验室安全左移优化

2.大模型知识学习笔记

3.[ragas官方](https://link.csdn.net/?from_id=135355723&target=https%3A%2F%2Fdocs.ragas.io%2Fen%2Flatest%2Fconcepts%2Fmetrics%2Findex.html)

4.RAGAS论文

5.[参考博客](https://blog.csdn.net/weixin_42608414/article/details/135355723)

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/j3gficicyOvasVeMDmWoZ2zyN8iaSc6XWYjZ7Hx6Udjjk2BGLzC9ahJq7ibxDd1RGA0c9NYZc1husEsvb3tY4FcWPQ/640?wx_fmt=gif&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvasVeMDmWoZ2zyN8iaSc6XWYj5q5PQEOc5ibURPb03vnRibrxC3UR8xzdyATfiawTYRV2vJvBnAIcE1FeQ/640?wx_fmt=png&from=appmsg)