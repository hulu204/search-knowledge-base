---
title: 'RAG—Chunking策略实战｜得物技术'
company: 得物
tag: 问答/RAG
date: 2025-10-29
url: http://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247541482&idx=1&sn=8dab062bde592f5a33fd8469c924c97b&chksm=c16177b5f616fea37845f89c65cf8d54a13dffdfa448d9384db69a990eebce32ae1ee0b68a22#rd
account: 得物技术
origin: wechat-mp
---
![](http://mmbiz.qpic.cn/mmbiz_gif/AAQtmjCc74DZeqm2Rc4qc7ocVLZVd8FOASKicbMfKsaziasqIDXGPt8yR8anxPO3NCF4a4DkYCACam4oNAOBmSbA/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

**目录**

一、背景

二、什么是分块（Chunking）

三、为何要对内容做分块处理

四、分块策略详解

    1. 基础分块

    2. 结构感知分块

    3. 语义与主题分块

    4. 高级分块

    5. 混合分块

五、结论

**一**

**背 景**

在 RAG 系统中，即便采用性能卓越的 LLM 并反复打磨 Prompt，问答仍可能出现上下文缺失、事实性错误或拼接不连贯等问题。多数团队会频繁更换检索算法与 Embedding模型，但收益常常有限。真正的瓶颈，往往潜伏在数据入库之前的一个细节——文档分块（chunking）。不当的分块会破坏语义边界，拆散关键线索并与噪声纠缠，使被检索的片段呈现“顺序错乱、信息残缺”的面貌。在这样的输入下，再强大的模型也难以基于支离破碎的知识推理出完整、可靠的答案。某种意义上，分块质量几乎决定了RAG的性能上限——它决定知识是以连贯的上下文呈现，还是退化为无法拼合的碎片。

在实际场景中，最常见的错误是按固定长度生硬切割，忽略文档的结构与语义：定义与信息被切开、表头与数据分离、步骤说明被截断、代码与注释脱节，结果就是召回命中却无法支撑结论，甚至诱发幻觉与错误引用。相反，高质量的分块应尽量贴合自然边界（标题、段落、列表、表格、代码块等），以适度重叠保持上下文连续，并保留必要的来源与章节元数据，确保可追溯与重排可用。当分块尊重文档的叙事与结构时，检索的相关性与答案的事实一致性往往显著提升，远胜于一味更换向量模型或调参；换言之，想要真正改善 RAG 的稳健性与上限，首先要把“知识如何被切开并呈现给模型”这件事做好。

**PS：本文主要是针对中文文档类型的嵌入进行实战。**

**二**

**什么是分块（Chunking）**

分块是将大块文本分解成较小段落的过程，这使得文本数据更易于管理和处理。通过分块，我们能够更高效地进行内容嵌入（embedding），并显著提升从向量数据库中召回内容的相关性和准确性。

在实际操作中，分块的好处是多方面的。首先，它能够提高模型处理的效率，因为较小的文本段落更容易进行嵌入和检索。

其次，分块后的文本能够更精确地匹配用户查询，从而提供更相关的搜索结果。这对于需要高精度信息检索和内容生成的应用程序尤为重要。

通过优化内容的分块和嵌入策略，我们可以最大化LLM在各种应用场景中的性能。分块技术不仅提高了内容召回的准确性，还提升了整体系统的响应速度和用户体验。

因此，在构建和优化基于LLM的应用程序时，理解和应用分块技术是不可或缺的步骤。

分块过程中主要的两个概念：chunk\_size块的大小，chunk\_overlap重叠窗口。

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74C0H6bNibLYjiagVcVia8MfXtwtFTQ2KwWwyKcfUeEXwvj3JsLEkwdSgpPicH4xBNC6icSN5zXIyowR3aw/640?wx_fmt=png&from=appmsg)

**三**

**为何要对内容做分块处理**

* **模型上下文窗口限制**：LLM无法一次处理超长文本。分块的目的在于将长文档切成模型可稳定处理的中等粒度片段，并尽量对齐自然语义边界（如标题、段落、句子、代码块），避免硬切导致关键信息被截断或语义漂移。即便使用长上下文模型，过长输入也会推高成本并稀释信息密度，合理分块仍是必需的前置约束。
* **检索的信噪比**：块过大时无关内容会稀释信号、降低相似度判别力；块过小时语境不足、容易“只命中词不命中义”。合适的块粒度可在召回与精度间取得更好平衡，既覆盖用户意图，又不引入多余噪声。在一定程度上提升检索相关性的同时又能保证结果稳定性。
* **语义连续性**：跨段落或跨章节的语义关系常在边界处被切断。通过设置适度的 chunk\_overlap，可保留跨块线索、减少关键定义/条件被“切开”的风险。对于强结构文档，优先让边界贴合标题层级与句子断点；必要时在检索阶段做轻量邻近扩展，以提升答案的连贯性与可追溯性，同时避免重复内容挤占上下文预算。

总之理想的分块是在“上下文完整性”和“信息密度”之间取得动态平衡：chunk\_size决定信息承载量，chunk\_overlap 用于弥补边界断裂并维持语义连续。只要边界对齐语义、粒度贴合内容，检索与生成的质量就能提升。

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74C0H6bNibLYjiagVcVia8MfXtwDnSSHTvaxUFiaCaIfj0ibsiaurBZkB1lpSYG1oKUzQzOoLLmVXib9nHeLw/640?wx_fmt=png&from=appmsg)

**四**

**分块策略详解**

**基础分块**

**基于固定长度分块**

* **分块策略**：按预设字符数 chunk\_size 直接切分，不考虑文本结构。
* **优点**：实现最简单、速度快、对任意文本通用。
* **缺点**：容易破坏语义边界；块过大容易引入较多噪声，过小则会导致上下文不足。
* **适用场景**：结构性弱的纯文本，或数据预处理初期的基线方案。

```
from langchain_text_splitters import CharacterTextSplitter  
splitter = CharacterTextSplitter(    separator="",        # 纯按长度切    chunk_size=600,      # 依据实验与模型上限调整    chunk_overlap=90,    # 15% 重叠)chunks = splitter.split_text(text)
```

* **参数建议（仅限中文语料建议）**：

+ chunk\_size：300–800 字优先尝试；若嵌入模型最佳输入为 512/1024 tokens，可折算为约 350/700 中文字符起步。
+ chunk\_overlap：10%–20% 起步；超过 30% 通常导致索引体积与检索开销显著上升，对实际性能起负作用，最后的效果并不会得到明显提升。

**基于句子的分块**

* **分块策略**：先按句子切分，再将若干句子聚合成满足chunk\_size的块；保证最基本的语义完整性。
* **优点**：句子级完整性最好。对问句/答句映射友好。便于高质量引用。
* **缺点**：中文分句需特别处理。仅句子级切分可能导致块过短，需后续聚合。
* **适用场景**：法律法规、新闻、公告、FAQ 等以句子为主的文本。
* **中文分句注意事项**：

+ 不要直接用 NLTK 英文 Punkt：无法识别中文标点，分句会失败或异常。
+ 可以直接使用以下内容进行分句：

- 基于中文标点的正则：按“。！？；”等切分，保留引号与省略号等边界。
- 使用支持中文的 NLP 库进行更精细的分句：
- HanLP（推荐，工业级，支持繁多语言学特性）Stanza（清华/斯坦福合作，中文支持较好）spaCy + pkuseg 插件（或 zh-core-web-sm/med/lg 生态）

* 示例（适配常见中文标点，基于正则的分句）：

```
import re  
def split_sentences_zh(text: str):    # 在句末标点（。！？；）后面带可选引号的场景断句    pattern = re.compile(r'([^。！？；]*[。！？；]+|[^。！？；]+$)')    sentences = [m.group(0).strip() for m in pattern.finditer(text) if m.group(0).strip()]    return sentences  
def sentence_chunk(text: str, chunk_size=600, overlap=80):    sents = split_sentences_zh(text)    chunks, buf = [], ""    for s in sents:        if len(buf) + len(s) <= chunk_size:            buf += s        else:            if buf:                chunks.append(buf)            # 简单重叠：从当前块尾部截取 overlap 字符与下一句拼接            buf = (buf[-overlap:] if overlap > 0 and len(buf) > overlap else "") + s    if buf:        chunks.append(buf)    return chunks  
chunks = sentence_chunk(text, chunk_size=600, overlap=90)
```

HanLP 分句示例：

```
from hanlp_common.constant import ROOTimport hanlp  
tokenizer = hanlp.load('PKU_NAME_MERGED_SIX_MONTHS_CONVSEG')  # 或句法/句子级管线# HanLP 高层 API 通常通过句法/语料管线获得句子边界，具体以所用版本 API 为准# 将句子列表再做聚合为 chunk_size
```

**基于递归字符分块**

* **分块策略**：给定一组由“粗到细”的分隔符（如段落→换行→空格→字符），自上而下递归切分，在不超出 chunk\_size 的前提下尽量保留自然语义边界。
* **优点**：在“保持语义边界”和“控制块大小”之间取得稳健平衡，对大多数文本即插即用。
* **缺点**：分隔符配置不当会导致块粒度失衡，极度格式化文本（表格/代码）效果一般。
* **适用场景**：综合性语料、说明文档、报告、知识库条目。

```
import refrom langchain_text_splitters import RecursiveCharacterTextSplitter  
separators = [    r"\n#{1,6}\s",                 # 标题    r"\n\d+(?:\.\d+)*\s",          # 数字编号标题 1. / 2.3. 等    "\n\n",                        # 段落    "\n",                          # 行    " ",                           # 空格    "",                            # 兜底字符级]splitter = RecursiveCharacterTextSplitter(    separators=separators,    chunk_size=700,    chunk_overlap=100,    is_separator_regex=True,       # 告诉分割器上面包含正则)chunks = splitter.split_text(text)
```

* 参数与分隔符建议（仅中文文档建议）：

+ chunk\_size：400–800 字符；如果内容更技术化、长句多时可适当上调该数值。
+ chunk\_overlap：10%–20%。
+ separators（由粗到细，按需裁剪）：

- 章节/标题：正则 r"^#{1,6}\s"（Markdown 标题）、r"^\d+(.\d+)\*\s"（编号标题）
- 段落："\n\n"
- 换行："\n"
- 空格：" "
- 兜底：""

**总结**

* 调优流程：

+ 固定检索与重排，只动分块参数。
+ 用验证集计算 Recall@k、nDCG、MRR、来源命中文档覆盖率、答案事实性（faithfulness）。
+ 观察块长分布：若长尾太长，适当收紧chunk\_size 或增加粗粒度分隔符；若过短，放宽chunk\_size 或降低分隔符优先级。

* 重叠的成本与收益：

+ 收益：缓解边界断裂，提升答案连贯性与可追溯性。
+ 成本：索引尺寸增长、召回重复块增多、rerank 负载提升。通常不建议超过 20%–25%。

* 组合技巧：

+ 先递归分块，再对“异常长句”或“跨段引用”场景加一点点额外 overlap。
+ 对标题块注入父级标题上下文，提高定位能力与可解释性。

* 何时切换策略：

+ 若问答频繁丢上下文或引用断裂：增大overlap或改用句子/结构感知策略。
+ 若召回含噪过多：减小 chunk\_size 或引入更强的结构分隔符。

**结构感知分块**

利用文档固有结构（标题层级、列表、代码块、表格、对话轮次）作为分块边界，逻辑清晰、可追溯性强，能在保证上下文完整性的同时提升检索信噪比。

**结构化文本分块**

* 分块策略

  以标题层级（H1–H6、编号标题）或语义块（段落、列表、表格、代码块）为此类型文档的天然边界，对过长的结构块再做二次细分，对过短的进行相邻合并。

* 实施步骤

+ 解析结构：Markdown 用解析器remark/markdown-it-py或正则识别标题与语块；HTML用 DOMBeautifulSoup/Cheerio遍历 Hx、p、li、pre、table 等。
+ 生成章节：以标题为父节点，将其后的连续兄弟节点纳入该章节，直至遇到同级或更高层级标题。
+ 二次切分：章节超出 chunk\_size时，优先按子标题/段落切，再不足时按句子或递归字符切分。
+ 合并短块：低于 min\_chunk\_chars 的块与相邻块合并，优先与同一父标题下的前后块。
+ 上下文重叠：优先用“结构重叠”（父级标题路径、前一小节标题+摘要），再辅以小比例字符overlap（10%–15%）。
+ 写入 metadata。

* 示例代码

```
import refrom typing import List, Dict  
heading_pat = re.compile(r'^(#{1,6})\s+(.*)$')  # 标题fence_pat = re.compile(r'^```')                 # fenced code fence  
def split_markdown_structure(text: str, chunk_size=900, min_chunk=250, overlap_ratio=0.1) -> List[Dict]:    lines = text.splitlines()    sections = []    in_code = False    current = {"level": 0, "title": "", "content": [], "path": []}        path_stack = []  # [(level, title)]        for ln in lines:        if fence_pat.match(ln):            in_code = not in_code        m = heading_pat.match(ln) if not in_code else None        if m:            if current["content"]:                sections.append(current)            level = len(m.group(1))            title = m.group(2).strip()  
            while path_stack and path_stack[-1][0] >= level:                path_stack.pop()            path_stack.append((level, title))            breadcrumbs = [t for _, t in path_stack]            current = {"level": level, "title": title, "content": [], "path": breadcrumbs}        else:            current["content"].append(ln)        if current["content"]:        sections.append(current)        # 通过二次拆分/合并将部分平铺成块    chunks = []    def emit_chunk(text_block: str, path: List[str], level: int):        chunks.append({            "text": text_block.strip(),            "meta": {                "section_title": path[-1] if path else "",                "breadcrumbs": path,                "section_level": level,            }        })        for sec in sections:        raw = "\n".join(sec["content"]).strip()        if not raw:            continue        if len(raw) <= chunk_size:            emit_chunk(raw, sec["path"], sec["level"])        else:            paras = [p.strip() for p in raw.split("\n\n") if p.strip()]            buf = ""            for p in paras:                if len(buf) + len(p) + 2 <= chunk_size:                    buf += (("\n\n" + p) if buf else p)                else:                    if buf:                        emit_chunk(buf, sec["path"], sec["level"])                    buf = p            if buf:                emit_chunk(buf, sec["path"], sec["level"])        merged = []    for ch in chunks:        if not merged:            merged.append(ch)            continue        if len(ch["text"]) < min_chunk and merged[-1]["meta"]["breadcrumbs"] == ch["meta"]["breadcrumbs"]:            merged[-1]["text"] += "\n\n" + ch["text"]        else:            merged.append(ch)        overlap = int(chunk_size * overlap_ratio)    for ch in merged:        bc = " > ".join(ch["meta"]["breadcrumbs"][-3:])        prefix = f"[{bc}]\n" if bc else ""        if prefix and not ch["text"].startswith(prefix):            ch["text"] = prefix + ch["text"]        # optional character overlap can在检索阶段用邻接聚合替代，这里略        return merged
```

* 参数建议（中文文档）

+ chunk\_size：600–1000 字；技术文/长段落可取上限，继续适当增加。
+ min\_chunk\_chars：200–300 字（小于则合并）。
+ chunk\_overlap：10%–15%；若使用“父级标题路径 + 摘要”作为结构重叠，可降至 5%–10%。

**对话式分块**

* **分块策略**

  **以“轮次/说话人”为边界，优先按对话邻接对和小段话题窗口聚合。重叠采用“轮次重叠”而非单纯字符重叠，保证上下文流畅。**

* **适用场景**

  **客服对话、访谈、会议纪要、技术支持工单等多轮交流。**

* **检索期邻接聚合**

  **在检索阶段对对话块做“邻接扩展”：取被召回块前后各 1–2 轮上下文（或相邻块拼接）作为最终送审上下文，以提高回答连贯性与可追溯性。**

* **与重排协同**

  **可提升对“谁说的、在哪段说的”的判断力。**

* 示例代码：（按轮次滑动窗口分块）

```
from typing import List, Dict  
def chunk_dialogue(turns: List[Dict], max_turns=10, max_chars=900, overlap_turns=2):    """    turns: [{"speaker":"User","text":"..." , "ts_start":123, "ts_end":130}, ...]    """    chunks = []    i = 0    while i < len(turns):        j = i        char_count = 0        speakers = set()        while j < len(turns):            t = turns[j]            uttr_len = len(t["text"])            # 若单条超长，允许在句级二次切分（此处略），但不跨 speaker            if (j - i + 1) > max_turns or (char_count + uttr_len) > max_chars:                break            char_count += uttr_len            speakers.add(t["speaker"])            j += 1                if j > i:            window = turns[i:j]        elif i < len(turns):            window = [turns[i]]        else:            break        text = "\n".join([f'{t["speaker"]}: {t["text"]}' for t in window])        meta = {            "speakers": list(speakers),            "turns_range": (i, j - 1),            "ts_start": window[0].get("ts_start"),            "ts_end": window[-1].get("ts_end"),        }        chunks.append({"text": text, "meta": meta})                # 按轮次重叠回退        if j >= len(turns):            break        next_start = i + len(window) - overlap_turns        i = max(next_start, i + 1)  # 确保至少前进1步    return chunks
```

* **参数建议**

+ max\_turns\_per\_chunk：6–12 轮起步；语速快信息密度高可取 8–10。
+ max\_chars\_per\_chunk：600–1000 字；若存在长段独白，优先句级再切，不跨说话人。
+ overlap\_turns：1–2 轮；保证上一问下一答的连续性。
+ keep\_pairing：不要拆开明显的问答对；若 chunk 临界，宁可扩一轮或后移切分点。

**总结**

* 首选用结构边界做第一次切分，再用句级/递归策略做二次细分。
* 优先使用“结构重叠”（父标题路径、上段标题+摘要、相邻发言）替代大比例字符重叠。
* 为每个块写好 metadata，可显著提升检索质量与可解释性。
* 对 PDF/HTML 先去噪（页眉页脚、导航、广告等），避免把噪声索引进库。

**语义与主题分块**

该方法不依赖文档的物理结构，而是依据语义连续性与话题转移来决定切分点，尤其适合希望“块内高度内聚、块间清晰分界”的知识库与研究类文本。

**语义分块**

* **分块策略**

+ 对文本先做句级切分，计算句子或短段的向量表示；
+ 当相邻语义的相似度显著下降（发生“语义突变”）时设为切分点。

* **适用场景**

+ 专题化、论证结构明显的文档：
+ 白皮书、论文、技术手册、FAQ 聚合页；
+ 需要高内聚检索与高可追溯性。

* **使用流程**

+ 句级切分：先用中文分句（标点/中文分句模型）得到句子序列。
+ 向量化：对每个句子编码，开启归一化（normalize）以便用余弦相似度。
+ 突变检测：

- 简单粗暴的方法：sim(i, i-1) 低于阈值则切分。
- 稳健的方法：与“前后窗口的均值向量”比较，计算新颖度 novelty = 1 - cos(emb\_i, mean\_emb\_window)，新颖度高于阈值则切分。
- 平滑的方法：对相似度/新颖度做移动平均，降低抖动。

+ 约束与修正：设置最小/最大块长，避免过碎或过长，必要时进行相邻块合并。

* **与检索/重排的协同**

  **召回时可做“邻接扩展”（把被命中的块前后各追加一两句），再做重排序。语义分块的高内聚可让 重排序更精准地区分相近候选。**

* 代码示例

```
from typing import List, Dict, Tupleimport numpy as npfrom sentence_transformers import SentenceTransformerimport re  
def split_sentences_zh(text: str) -> List[str]:    # 简易中文分句，可替换为 HanLP/Stanza 更稳健的实现    pattern = re.compile(r'([^。！？；]*[。！？；]+|[^。！？；]+$)')    return [m.group(0).strip() for m in pattern.finditer(text) if m.group(0).strip()]  
def rolling_mean(vecs: np.ndarray, i: int, w: int) -> np.ndarray:    s = max(0, i - w)    e = min(len(vecs), i + w + 1)    return vecs[s:e].mean(axis=0)  
def semantic_chunk(    text: str,    model_name: str = "BAAI/bge-m3",    window_size: int = 2,    min_chars: int = 350,    max_chars: int = 1100,    lambda_std: float = 0.8,    overlap_chars: int = 80,) -> List[Dict]:    sents = split_sentences_zh(text)    if not sents:        return []        model = SentenceTransformer(model_name)    emb = model.encode(sents, normalize_embeddings=True, batch_size=64, show_progress_bar=False)    emb = np.asarray(emb)        # 基于窗口均值的“新颖度”分数    novelties = []    for i in range(len(sents)):        ref = rolling_mean(emb, i-1, window_size) if i > 0 else emb[0]        ref = ref / (np.linalg.norm(ref) + 1e-8)        novelty = 1.0 - float(np.dot(emb[i], ref))        novelties.append(novelty)    novelties = np.array(novelties)        # 相对阈值：μ + λσ    mu, sigma = float(novelties.mean()), float(novelties.std() + 1e-8)    threshold = mu + lambda_std * sigma        chunks, buf, start_idx = [], "", 0    def flush(end_idx: int):        nonlocal buf, start_idx        if buf.strip():            chunks.append({                "text": buf.strip(),                "meta": {"start_sent": start_idx, "end_sent": end_idx-1}            })        buf, start_idx = "", end_idx        for i, s in enumerate(sents):        # 若超长则先冲洗        if len(buf) + len(s) > max_chars and len(buf) >= min_chars:            flush(i)            # 结构化重叠：附加上一个块的尾部            if overlap_chars > 0 and len(s) < overlap_chars:                buf = s                continue                buf += s                # 达到最小长度后遇到突变则切分        if len(buf) >= min_chars and novelties[i] > threshold:            flush(i + 1)        if buf:        flush(len(sents))        return chunks
```

* 参数调优说明（仅作参考）

+ 阈值的含义：语义变化敏感度控制器，越低越容易切、越高越保守。
+ 设定方式：

- 绝对阈值：例如使用余弦相似度，若 sim < 0.75 则切分（需按语料校准）。
- 相对阈值：对全篇的相似度/新颖度分布估计均值μ与标准差σ，使用 μ ± λσ 作为阈值，更稳健。

+ 初始的配置建议（仅限于中文技术/说明文档）：

- 窗口大小 window\_size：2–4 句
- 最小/最大块长：min\_chunk\_chars=300–400，max\_chunk\_chars=1000–1200
- 阈值策略：novelty > μ + 0.8σ 或相似度 < μ - 0.8σ（先粗调后微调）
- overlap：10% 左右或按“附加上一句”做轻量轮次重叠

**主题的分块**

* 分块策略

  利用主题模型或聚类算法在“宏观话题”发生切换时进行切分，更多的关注章节级、段落级的主题边界。该类分块策略主要适合长篇、多主题材料。

* 适用场景

+ 报告、书籍、长调研文档、综合评审；
+ 当文档内部确有较稳定的“话题块”。

* 使用流程（最好用“句向量 + 聚类 + 序列平滑”而非纯 LDA）

+ 句级切分并编码：首先通过向量模型得到句向量，normalize。
+ 文档内或语料级聚类：

- 文档内小规模：MiniBatchKMeans（k=3–8 先验）或 SpectralClustering。
- 语料级统一主题：在大量文档上聚类（或用 HDBSCAN+UMAP），再将每篇文档的句子映射到最近主题中心。

+ 序列平滑与解码：

- 对句子的主题标签做滑窗多数投票或一阶马尔可夫平滑，避免频繁抖动。
- 当主题标签稳定变化并满足最小块长时，设为切分点。

+ 主题命名：

  用 KeyBERT/TF-IDF 在每个块内抽关键词，或用小模型生成一句话主题摘要，写入 metadata。
+ 约束：min/max\_chars，保留代码/表格等原子块，必要时与结构边界结合使用。

* 代码示例（KMeans 文档内聚类 + 序列平滑）

```
from typing import List, Dictimport numpy as npfrom sentence_transformers import SentenceTransformerfrom sklearn.cluster import KMeansimport re  
def split_sentences_zh(text: str) -> List[str]:    pattern = re.compile(r'([^。！？；]*[。！？；]+|[^。！？；]+$)')    return [m.group(0).strip() for m in pattern.finditer(text) if m.group(0).strip()]  
def topic_chunk(    text: str,    k_topics: int = 5,    min_chars: int = 500,    max_chars: int = 1400,    smooth_window: int = 2,    model_name: str = "BAAI/bge-m3") -> List[Dict]:    sents = split_sentences_zh(text)    if not sents:        return []        model = SentenceTransformer(model_name)    emb = model.encode(sents, normalize_embeddings=True, batch_size=64, show_progress_bar=False)    emb = np.asarray(emb)        km = KMeans(n_clusters=k_topics, n_init="auto", random_state=42)    labels = km.fit_predict(emb)        # 简单序列平滑：滑窗多数投票    smoothed = labels.copy()    for i in range(len(labels)):        s = max(0, i - smooth_window)        e = min(len(labels), i + smooth_window + 1)        window = labels[s:e]        vals, counts = np.unique(window, return_counts=True)        smoothed[i] = int(vals[np.argmax(counts)])        chunks, buf, start_idx, cur_label = [], "", 0, smoothed[0]    def flush(end_idx: int):        nonlocal buf, start_idx        if buf.strip():            chunks.append({                "text": buf.strip(),                "meta": {"start_sent": start_idx, "end_sent": end_idx-1, "topic": int(cur_label)}            })        buf, start_idx = "", end_idx        for i, s in enumerate(sents):        switched = smoothed[i] != cur_label        over_max = len(buf) + len(s) > max_chars        under_min = len(buf) < min_chars                # 尝试延后切分，保证最小块长        if switched and not under_min:            flush(i)            cur_label = smoothed[i]                if over_max and not under_min:            flush(i)                buf += s        if buf:        flush(len(sents))        return chunks
```

* 一些参数对结果的影响

+ k（主题数）：难以精准预设，可通过轮廓系数（silhouette）/肘部法初筛，再结合领域先验与人工校正。
+ HDBSCAN：min\_cluster\_size 影响较大，过小会碎片化，过大则合并不同话题。
+ min\_topic\_span\_sents：如 5–8 句，防止标签抖动导致过密切分。
+ 小文档不宜用：样本太少时主题不可分，优先用语义分块或结构分块。

**高级分块**

**小-大分块**

* 分块策略

  用“小粒度块”（如句子/短句）做高精度召回，定位到最相关的微片段；再将其“所在的大粒度块”（如段落/小节）作为上下文送入 LLM，以兼顾精确性与上下文完整性。

* 使用流程

+ 构建索引（离线）：

- Sentence/短句索引（索引A）：单位为句子或子句。
- 段落/小节存储（存储B）：保留原始大块文本与结构信息。

+ 检索（在线）：

- 用索引A召回 top\_k\_small 个小块（向量检索）。
- 将小块按 parent\_id 分组，计算组内分数（max/mean/加权），选出 top\_m\_big 个父块候选。
- 对“查询-父块文本”做交叉编码重排，提升相关性排序的稳定性。
- 上下文组装：在每个父块中高亮或优先保留命中小句附近的上下文（邻近N句或窗口字符 w），在整体 token 预算内拼接多块。

* 代码示例（伪代码）

```
# 离线：构建小块索引，并保存 parent_id -> 大块文本 的映射# 在线检索：small_hits = small_index.search(embed(query), top_k=30)groups = group_by_parent(small_hits)scored_parents = score_groups(groups, agg="max")candidates = top_m(scored_parents, m=3)  
# 交叉编码重排rerank_inputs = [(query, parent_text(pid)) for pid in candidates]reranked = cross_encoder_rerank(rerank_inputs)  
# 组装上下文：对每个父块，仅保留命中句及其邻近窗口，并加上标题路径contexts = []for pid, _ in reranked:    hits = groups[pid]    context = build_local_window(parent_text(pid), hits, window_sents=1)    contexts.append(prefix_with_breadcrumbs(pid) + context)  
final_context = pack_under_budget(contexts, token_budget=3000)    # 留出回答空间
```

**父子段分块**

* 分块策略

  将文档按章节/段落等结构单元切成“父块”（Parent），再在每个父块内切出“子块”（通常为句子/短段或者笃固定块）。然后为“子块”建向量索引以做高精度召回。当检索时先召回子块，再按 parent\_id 聚合并扩展到父块或父块中的局部窗口，兼顾最后召回内容的精准与上下文完整性。

* 适用场景

+ 结构清晰的说明文、手册、白皮书、法规、FAQ 聚合页；
+ 需要“句级证据准确 + 段/小节级上下文完整”的问答。

* 使用流程

+ 结构粗切（父块）

- 按标题层级/段落/代码块切出父块。
- 父块写入 breadcrumbs（H1/H2/...）、anchor、block\_type、start/end\_offset。

+ 精细切分（子块）

- 在父块内部以句子/子句/固定块为单位切分（可用递归分块兜底），小比例 overlap（或附加上一句内容）。
- 为每个子块记录child\_offset、sent\_index\_range、parent\_id。

+ 建索引与存储

- 子块向量索引A：先编码，normalize 后建索引。
- 父块存储B：保存原文与结构元信息，此处可以选建一个父块级向量索引用于粗排或回退。

+ 检索与组装

- 用索引A召回 top\_k\_child 子块。
- 按 parent\_id 分组并聚合打分（max/mean/命中密度），选出 top\_m\_parent 父块候选。
- 对 (query, parent\_text 或 parent\_window) 交叉编码重排。
- 上下文裁剪：对每个父块仅保留“命中子块±邻近窗口”（±1–2 句或 80–200 字），加上标题路径前缀，控制整体 token 预算。

* 打分与聚合策略

+ 组分数：score\_parent = α·max(child\_scores) + (1-α)·mean(child\_scores) + β·coverage（命中子块数/父块子块总数）。
+ 密度归一化：density = sum(exp(score\_i)) / length(parent\_text)，为避免长父块因命中多而“天然占优”。
+ 窗口合并：同一父块内相邻命中窗口若间距小于阈值则合并，减少重复与碎片。

* 与“小-大分块”的关系

+ 小-大分块是检索工作流（小粒度召回→大粒度上下文）；
+ 父子段分块是数据建模与索引设计（显式维护 parent–child 映射）。
+ 两者强相关、常配合使用：父子映射让小-大扩展更稳、更易去重与回链。

* 示例

```
from typing import List, Dict, Tupleimport numpy as npfrom sentence_transformers import SentenceTransformer  
  
embedder = SentenceTransformer("BAAI/bge-m3")  
def search_parent_child(query: str, top_k_child=40, top_m_parent=3, window_chars=180):    q = embedder.encode([query], normalize_embeddings=True)[0]    hits = small_index.search(q, top_k=top_k_child)  # 返回 [(child_id, score), ...]    # 分组    groups: Dict[str, List[Tuple[str, float]]] = {}    for cid, score in hits:        p = child_parent_id[cid]        groups.setdefault(p, []).append((cid, float(score)))        # 聚合打分（max + coverage）    scored = []    for pid, items in groups.items():        scores = np.array([s for _, s in items])        agg = 0.7 * scores.max() + 0.3 * (len(items) / (len(parents[pid]["sent_spans"]) + 1e-6))        scored.append((pid, float(agg)))    scored.sort(key=lambda x: x[1], reverse=True)    candidates = [pid for pid, _ in scored[:top_m_parent]]        # 为每个父块构造“命中窗口”    contexts = []    for pid in candidates:        ptext = parents[pid]["text"]        # 找到子块命中区间并合并窗口        spans = sorted([(children[cid]["start"], children[cid]["end"]) for cid, _ in groups[pid]])        merged = []        for s, e in spans:            s = max(0, s - window_chars)            e = min(len(ptext), e + window_chars)            if not merged or s > merged[-1][1] + 50:                merged.append([s, e])            else:                merged[-1][1] = max(merged[-1][1], e)        windows = [ptext[s:e] for s, e in merged]        prefix = " > ".join(parents[pid]["meta"].get("breadcrumbs", [])[-3:])        contexts.append((pid, f"[{prefix}]\n" + "\n...\n".join(windows)))        # 交叉编码重排（此处用占位函数）    reranked = cross_encoder_rerank(query, [c[1] for c in contexts])  # 返回 indices 顺序    ordered = [contexts[i] for i in reranked]    return ordered  # [(parent_id, context_text), ...]
```

* 调参建议（仅作参考，具体需要按照实际来）

  调参顺序：先定父/子块长度 → 标定 top\_k\_child 与聚合权重 → 调整窗口大小与合并阈值 → 最后接入交叉编码重排并控制 token 预算。

**代理式分块**

* 分块策略

  使用一个小温度、强约束的 LLM Agent 模拟“人类阅读与编排”，根据语义、结构与任务目标动态决定分块边界，并输出结构化边界信息与理由（rationale 可选，不用于检索）。

* 适用场景

+ 高度复杂、长篇、非结构化且混合格式（文本+代码+表格）的文档；
+ 结构/语义/主题策略单独使用难以取得理想边界时。

* 使用时的注意事项

+ 规则护栏：

- 禁止在代码块、表格单元、引用块中间切分，对图片/公式作为原子单元处理。
- 保持标题链路完整，强制最小/最大块长（min/max\_chars / min/max\_sents）。

+ 目标对齐：

  在系统提示中明确“为了检索问答/用于摘要/用于诊断”的目标，Agent 以任务优先级决定边界与上下文冗余度。
+ 结构化输出：

  要求输出 segments: [{start\_offset, end\_offset, title\_path, reason}]，不能接受自由文本。
+ 自检与回退：

  Agent 产出的边界先过一遍约束校验器（如长度、原子块、顺序等），不符合规则的内容则自动回退到递归/句级分块。
+ 成本控制：

- 长文分批阅读（分段滑动窗口）；
- 在每段末尾只输出边界草案，最终汇总并去重；
- 温度低（≤0.3）、max\_tokens 受控。

* 示例：Agent 输出模式（伪 Prompt 片段）

```
系统：你是分块器。目标：为RAG检索创建高内聚、可追溯的块。规则：1) 不得在代码/表格/公式中间切分；2) 每块400-1000字；3) 保持标题路径完整；4) 尽量让“定义+解释”在同一块；5) 输出JSON，含 start_offset/end_offset/title_path。  
用户：<文档片段文本>助手（示例输出）：{  "segments": [    {"start": 0, "end": 812, "title_path": ["指南","安装"], "reason": "完整步骤+注意事项"},    {"start": 813, "end": 1620, "title_path": ["指南","配置"], "reason": "参数表与示例紧密相关"}  ]}
```

* 集成的流程

+ 粗切：先用结构感知/递归策略获得初步块，降低 Agent 处理跨度。
+ Agent 精修：对“疑难块”（过长/多格式/主题混杂）调用 Agent 细化边界。
+ 质检：规则校验 + 语义稀疏度检测（块内相似度方差过大则再细分）。
+ 写入 metadata。

**混合分块**

单一策略难覆盖所有文档与场景。混合分块通过“先粗后细、按需细化”，在效率、可追溯性与答案质量之间取得稳健平衡。

* 分块策略

  先用宏观边界（结构感知）做粗粒度切分，再对“过大或主题跨度大的块”应用更精细的策略（递归、句子、语义/主题）。查询时配合“小-大分块”/“父子段分块”的检索组装，以小精召回、以大保上下文。

* 使用流程

+ 粗切（离线）：按标题/段落/代码块/表格等结构单元切分，清理噪声（页眉页脚/导航）。
+ 细化（离线）：对超长或密度不均的块，按规则选用递归/句子/语义分块二次细分。
+ 索引（离线）：同时为“小块索引（句/子句）”与“大块存储（段/小节）”生成数据与metadata。
+ 检索（在线）：小块高精度召回 → 按父块聚合与重排→ 在父块中抽取命中句邻域作为上下文，控制整体 token 预算。

* 策略选择规则

+ 若块类型为代码/表格/公式：保持原子，不在中间切分，直接与其解释文字打包。
+ 若为对话：按轮次/说话人做对话式分块，overlap 使用“轮次重叠”。
+ 若为普通说明文/Markdown章节：

- 长度 > max\_coarse或句长方差高/标点稀疏：优先语义分块（句向量+突变阈值）。
- 否则：递归字符分块（标题/段落/换行/空格/字符）保持语义边界。

+ 对过短块：与同一父标题相邻块合并，优先向后合并。

* 质量-成本档位（仅供参考）

+ fast：仅结构→递归。overlap 5%–10%，不跑语义分块和主题分块
+ balanced（推荐）：结构→递归，对异常块启用语义分块，小-大检索，overlap 10%左右
+ quality：在 balanced 基础上对疑难块启用 Agent 精修，更强的邻接扩展与rerank

* 简洁调度器示例， 将结构粗切与若干细分器组合为一个“混合分块”入口，关键是类型判断与长度阈值控制。可以把前文已实现的结构/句子/语义/对话分块函数挂入此调度器。

```
from typing import List, Dict  
def hybrid_chunk(    doc_text: str,    parse_structure,          # 函数：返回 [{'type': 'text|code|table|dialogue', 'text': str, 'breadcrumbs': [...], 'anchor': str}]    recursive_splitter,       # 函数：text -> [{'text': str}]    sentence_splitter,        # 函数：text -> [{'text': str}]    semantic_splitter,        # 函数：text -> [{'text': str}]    dialogue_splitter,        # 函数：turns(list) -> [{'text': str}]，若无对话则忽略    max_coarse_len: int = 1100,    min_chunk_len: int = 320,    target_len: int = 750,    overlap_ratio: float = 0.1,) -> List[Dict]:    """    返回格式: [{'text': str, 'meta': {...}}]    """    blocks = parse_structure(doc_text)  # 先拿到结构块    chunks: List[Dict] = []        def emit(t: str, meta_base: Dict):        t = t.strip()        if not t:            return        # 结构重叠前缀（标题路径）        bc = " > ".join(meta_base.get("breadcrumbs", [])[-3:])        prefix = f"[{bc}]\n" if bc else ""        chunks.append({            "text": (prefix + t) if not t.startswith(prefix) else t,            "meta": meta_base        })        for b in blocks:        t = b["text"]        btype = b.get("type", "text")                # 原子块：代码/表格        if btype in {"code", "table", "formula"}:            emit(t, {**b, "splitter": "atomic"})            continue                # 对话块        if btype == "dialogue":            for ck in dialogue_splitter(b.get("turns", [])):                emit(ck["text"], {**b, "splitter": "dialogue"})            continue                # 普通文本：依据长度与“可读性”启用不同细分器        if len(t) <= max_coarse_len:            # 中短文本：递归 or 句子            sub = recursive_splitter(t)            # 合并过短子块            buf = ""            for s in sub:                txt = s["text"]                if len(buf) + len(txt) < min_chunk_len:                    buf += txt                else:                    emit(buf or txt, {**b, "splitter": "recursive"})                    buf = "" if buf else ""            if buf:                emit(buf, {**b, "splitter": "recursive"})        else:            # 超长文本：语义分块优先            for ck in semantic_splitter(t):                emit(ck["text"], {**b, "splitter": "semantic"})        # 轻量字符重叠（可选）    if overlap_ratio > 0:        overlapped = []        for i, ch in enumerate(chunks):            overlapped.append(ch)            if i + 1 < len(chunks) and ch["meta"].get("breadcrumbs") == chunks[i+1]["meta"].get("breadcrumbs"):                # 在相邻同章节块间引入小比例重叠                ov = int(len(ch["text"]) * overlap_ratio)                if ov > 0:                    head = ch["text"][-ov:]                    chunks[i+1]["text"] = head + chunks[i+1]["text"]        chunks = overlapped        return chunks
```

**五**

**结论**

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74C0H6bNibLYjiagVcVia8MfXtwmL0g8AuQxYCibrKnys3JVqZbMCKk7JnIAHNNzjgazzlAwe1s0fByHvA/640?wx_fmt=png&from=appmsg)

**往期回顾**

1. [告别数据无序：得物数据研发与管理平台的破局之路](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247541473&idx=1&sn=f2b5457c7e5249ba06dd5fc5a8283d25&scene=21#wechat_redirect)

2. [从一次启动失败深入剖析：Spring循环依赖的真相｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247541352&idx=1&sn=5c1266becb499d69bd989f3ce5ef6ce8&scene=21#wechat_redirect)

3. [Apex AI辅助编码助手的设计和实践｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247541339&idx=1&sn=6d13fe7855ad4f350584f78e923a4a60&scene=21#wechat_redirect)

4. [从 JSON 字符串到 Java 对象：Fastjson 1.2.83 全程解析｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247541322&idx=1&sn=4fc8048deb13dccb6b6e85daaf93f701&scene=21#wechat_redirect)

5. [用好 TTL Agent 不踩雷：避开内存泄露与CPU 100%两大核心坑｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247541282&idx=1&sn=af1edf3514b35d807083282e0640b0bf&scene=21#wechat_redirect)

文 /昆岚

关注得物技术，每周一、三更新技术干货

要是觉得文章对你有帮助的话，欢迎评论转发点赞～

未经得物技术许可严禁转载，否则依法追究法律责任。

“

**扫码添加小助手微信**

如有任何疑问，或想要了解更多技术资讯，请添加小助手微信：

![](https://mmbiz.qpic.cn/mmbiz_jpg/AAQtmjCc74C0H6bNibLYjiagVcVia8MfXtwpga1EYuADZ8r2a81UAmv1sr8khWibiaDGphCEonLINg8CpFlEtMprdjw/640?wx_fmt=jpeg&from=appmsg)