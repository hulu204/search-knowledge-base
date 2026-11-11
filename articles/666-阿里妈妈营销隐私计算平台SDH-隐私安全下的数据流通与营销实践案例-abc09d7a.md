---
title: '阿里妈妈营销隐私计算平台SDH：隐私安全下的数据流通与营销实践案例'
company: 阿里妈妈
tag: 广告
date: 2025-09-12
url: https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247496202&idx=1&sn=af7c6c74c3cc44028f2f25c650dd0917&chksm=c10c130573ce66684ac25f6329f5b4efb797eb63241ae9865ac0f062043446203cf1151574d7&scene=0&xtrack=1#rd
account: 阿里妈妈技术
origin: harvest-202607
---
以下文章来源于阿里妈妈数字营销，作者是守职，夜涧，翾逸

在数字广告的竞争洪流中，数据已成为驱动增长的核心燃料。然而，用户隐私保护不断升级，难题也接踵而至：

想充分使用数据，又担心泄露与权限治理风险；

想评估多平台投放的整体增量，但投放数据分散在多处，难以统一归因；

想控跨平台触达频次，但无法得知同一用户被触达了几次、在哪些场景被超频；

这些共性痛点反映了品牌在数据隐私与营销决策之间如何平衡的难题，而**阿里妈妈营销隐私计算平台Secure Data Hub（SDH）**指出了这种困境下的营销新解法。下面，我们将以四个典型场景展开——对应“**上翻追投、消费者洞察、效果衡量、全域频控**”的方法论与实践路径。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEd1dRcyLJvV98L4z7QE5dyI2vXjIT8A93kwSoceBeKALFPX89iaVibcSw/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

[查阅🔗隐私计算专题](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=Mzg5NTk4MDMwMA==&action=getalbum&album_id=3227116482966061058&subscene=0&scenenote=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5NTk4MDMwMA%3D%3D%26mid%3D2247496100%26idx%3D1%26sn%3D96e592db24b7d5df5d69ce3b1ecb1210%26chksm%3Dc1df25cf96ac2fbe59ca1134ff7453e3c930c2a728eb67df8608ce1186184758cab724020c47%26scene%3D0%26xtrack%3D1%26clicktime%3D1754987940%26ascene%3D1%26devicetype%3DiOS18.5%26version%3D18003d38%26nettype%3DWIFI%26abtest_cookie%3DAAACAA%253D%253D%26lang%3Dzh_CN%26session_us%3Dgh_bdfb0395a299%26countrycode%3DCN%26fontScale%3D100%26exportkey%3Dn_ChQIAhIQA1T54tMRc3kENjvEwjJO5hLuAQIE97dBBAEAAAAAAIfBMVvQHxcAAAAOpnltbLcz9gKNyK89dVj04xOVWSWqBFrul8VVlU3aasxiB6SJfprfbt04Dsl0lVszj2%252Ft94%252Bv7q727xxYx7G9JzLvZPc47JoTEadvtheL3p%252BTX6lOlcPCQaQT802pNKa7UELC0SjKYDLmf1mX1vy84mI5%252BFmXYlNa4PTXJItgnh2am6tw7ldisjpQRuUW9t%252F6s5eLbgACjglbgKGUA8H4cSammCHwr0%252F9LrMaxU23pgAgr8obg83OK3v9K4UlIzfGdOoA0MhkKzpusoAQviiRadlO98xUVaQ%253D%26pass_ticket%3DAXskJrCZGZ1Ae5qy3kA0COz6yobJDgxSOEdwTddEtuWo5Wk5hchtjiYJc5IAwz%252F6%26wx_header%3D3&nolastread=1&scene=21#wechat_redirect)

**背景：**随着全球主要市场陆续出台个人信息保护政策，互联网生态中的数据安全和用户隐私保护问题变得越发重要且日趋严格。在数字广告行业，采集和使用个人数据限制增多，广告生态数据割裂严重。如何解决广告精准营销和用户隐私的矛盾，实现数据“保密性”和“共享性”的平衡，成为当下广告生态中各企业急需攻克的难题。

**动机：**阿里妈妈营销隐私计算平台Secure Data Hub（SDH）应运而生。平台核心解决广告营销场景中的数据孤岛和跨域数据流通问题，实现广告行业下多方数据要素的高效流通。它为媒体、广告主和营销参与方提供及时、准确、安全的营销分析服务，用数据驱动消费升级。

**定位：**SDH是由阿里妈妈推出的一套面向广告营销行业的隐私计算PaaS产品，基于隐私安全环境，支持跨域数据互联互通、多方数据融合与联合建模。（目的）在保障各方隐私安全和数据合规的前提下，提供广告投放全流程的跨域安全一致的数据分析与决策能力，推动商家实现全域生意增长。

面向客户包括：媒体、广告主、DSP、DMP、CDP、三方监测公司、三方数据提供商等广告生态多元主体。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/RqLx3F3TPpnPlyiaRANo9O25mqjXc3lh6ic88W8blTIiasiaf3rzdiaiahiaj0Xt6oqWbHDatJVWR3hiboEiakorPkPjUAw/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

**核心能力：**SDH平台基于安全多方计算（MPC）、联邦学习（FL）、差分隐私（DP）等隐私增强技术，保障数据“可用不可见”。依托系统架构隔离、元数据管理、网络通信加密与计算流程加密，平台支持百亿级别的安全多方计算和联邦学习，计算准确性和时效性均达到行业SOTA水平。同时，平台提供异构混合云的多模式部署、营销分析套件、低代码SQL接口，极大降低了对接门槛，提升了营销安全分析效率。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/RqLx3F3TPpnPlyiaRANo9O25mqjXc3lh6GJBib22sz6G3zicoicTHUQodTNBRGAgKWIqakyib3MLS2v7b0b80hpSpxg/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

**平台优势：**

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/RqLx3F3TPpnPlyiaRANo9O25mqjXc3lh6zy9VKnicMjEfhHJoicpViaTMuXZVwmZD1dO87GJafKnia0C87uLR8pQfkg/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEibutbnB9Hh5dJwibNcE5DgI3N3XcJfcelU0TviboybyIB01leQicpH4CqQ/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YE4XnrOJq0MTV59A2FdkNYClGcEVqC2SC2JoqVs8PmSHyueGlxJ7XO2Q/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

通过阿里妈妈营销隐私计算平台SDH，德龙实现了将品牌一方人群和代理商（WPP Media）三方监测数据，以合规方式（PSI隐私集合求交）安全同步至平台DMP产品。再结合多维人群画像洞察和相似人群扩展，最终形成《超级品牌日》营销活动的人群策略，并同步到阿里妈妈品牌广告营销BP——百灵做定向程序化投放，实现了对高感未购用户与已购相似人群的跨域触达，保证了投放效果。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEVtdUC1mmjG5ia0zzRM2qslEbHYxeVjpVFAafAV9KSJ38hv9xQTUW5YA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=6)

**a.业务痛点**

品牌方德龙拥有一定规模的一方人群数据，但受制于数据合规要求，无法与阿里平台数据进行融合，导致这部分私域人群价值没有得到充分释放。

**b.参与数据**

**•**德龙：品牌一方人群/代理商（WPP Media）三方监测数据（百万级）

**•**阿里妈妈：设备ID映射数据（亿级）

**c.方案流程**

1.德龙（ISV：WPP Media）和阿里妈妈分别准备数据，完成元数据隐私保护配置；

2.调用SDH平台的人群上翻分析组件，提交PSI分析任务；

3.德龙的一方人群数据、代理商（WPP Media）三方监测数据与阿里妈妈设备ID粒度的用户映射数据，通过PSI技术在隐私保护下完成安全匹配，实现跨域用户识别；

4.将安全匹配撞库后的人群包同步至DMP品牌私域，再进行画像洞察和相似人群扩展，并最终同步至品牌广告营销BP进行定向投放。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/RqLx3F3TPpnPlyiaRANo9O25mqjXc3lh6CM8hOqePOcgoodYWibicN3W8KhnPicnW6kNB5rwDFvPPGGYaAb3EsE8sQ/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=7)

**d.方案价值**

SDH通过PSI技术实现了品牌一方人群和代理商（WPP Media）三方监测数据的安全上翻，支持多方数据安全合规上传，并应用于个性化广告投放，帮助品牌方德龙沉淀全域数据资产，释放人群价值。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEjF7EH93ib78yoibsqWKniah4bDfK13icuEYR2fn8ttj52Y86psrUcfLnuw/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=8)

通过SDH，德龙咖啡机实现了和商家的跨域数据共建与智能融合，打通了品牌CRM、公域广告投放互动人群、淘系相似行为人群等多维数据，构建了高精度人群包，实现了UD品牌广告投放全链路提效，全面提升了TA浓度、广告CTR及GMV。

**•**第一阶段：基于三方监测数据上翻，构建“增补人群包1.0”，精准锁定潜在高营销价值咖啡机用户。效果显示：人群包1.0对品牌TA贡献率超过10%，TA进店率超过70%，品牌关键词搜点率高于项目均值1.7倍，ROI高于项目均值1.2倍，有效提升了品牌认知与商品兴趣，显著促进了用户行动转化。

**•**第二阶段：基于一方人群上翻，结合lookalike相似人群扩展，构建“增补人群包2.0”，显著提升广告投放效能。人群包2.0的GMV贡献率排名第一，ROI较第一阶段大幅提升432%，为《超级品牌日》期间带来显著生意增长。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEzExQK6OL0CH6vSvW6vZrUml5wTdVlR1BULHqBsKPB7xAOvwvQbuE6g/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=9)

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEOThnsLRRg9d8sKKJibsjtbKM4VBh4Y5sQ0nN6oxg2nIibhNA1W26Vpvw/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=10)

某国际快消品牌在多平台投放广告并为淘内生意引流。但由于不同平台数据来源和算法模型存在差异，品牌难以打通、评估人群定向的准确性。借助阿里妈妈营销隐私计算平台SDH，品牌方实现了全域消费者画像的洞察，并将结果应用于多平台的人群定向优化，显著提升了淘内引流效果。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEVtdUC1mmjG5ia0zzRM2qslEbHYxeVjpVFAafAV9KSJ38hv9xQTUW5YA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=11)

**a.业务痛点**

某国际快消品牌在多个平台进行消费者运营并为淘内生意引流，但用户数据分散割裂，导致无法完整刻画全域用户资产，从而限制了个性化广告投放效果的提升。

**b.参与数据**

•阿里妈妈：设备ID转化映射数据、DMP“人-货-场”用户标签、店铺私域人群数据

•品牌方：品牌人群包数据

**c.方案流程**

1.品牌方和阿里妈妈分别准备数据，并完成元数据隐私保护配置；

2.调用SDH平台的画像洞察分析组件，提交MPC洞察分析任务；

3.将品牌方设备ID粒度的一方人群包和阿里妈妈店铺私域人群数据，通过隐私集合求并PSU进行安全聚合，得到全域人群包；

4.全域人群包再与DMP“人-货-场”用户标签数据进行PSI安全匹配，并基于不同标签对人群进行聚合分析，结合DP加噪，产出人群画像报告；

5.品牌方根据人群画像报告，优化多平台人群定向策略。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/RqLx3F3TPpnwcicsVJ2LJh9uywHbNX5ukdQTluPDZ0RenGEFTiaJQXxs5bRjQ211qH78iblbdEDnfor0pQ9Mbt0yw/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=12)

**d.方案价值**

SDH实现了多平台用户数据的隐私聚合和全域消费者资产洞察分析，帮助客户更全面、更清晰地理解全域消费者。在此基础上，进一步优化广告精准定向与多渠道预算分配策略，有效提升投放效果。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEmL3EdUuVicrKu4xuXcln1lvYiaHr5l8xkt0jh5vtrQO9cfZFUTrtDjeg/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=13)

自上线以来，SDH全域消费者洞察服务已覆盖美妆、个护、食品等多个行业的头部商家，帮助品牌更加精准地定位目标用户，并通过及时调整人群定向策略，实现广告投放效果的持续优化。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEEb3lLkrHF50ib4omhWXn4JkVS31sDb9ZEOb6SDia4dl0OJETOnjHQbxQ/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=14)

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEOThnsLRRg9d8sKKJibsjtbKM4VBh4Y5sQ0nN6oxg2nIibhNA1W26Vpvw/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=15)

玛氏在多平台进行广告投放，同时在多个生意场承接成交转化。但由于广告投放事件与用户转化数据分散在广告平台、媒体、电商平台、客户CDP等多处，导致投放与转化难以统一衡量。借助阿里妈妈营销隐私计算平台SDH，玛氏实现了多方数据的安全融合，并完成了跨渠道用户识别与转化效果的精准归因分析。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEmNR9OkVFgiaDMvmAiaKpGibic1TKIVxQiaDp64nYj2VZQZFgOJHI0Ro3b7w/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=16)

**a.业务痛点**

玛氏通过直投、代投等多种模式在多个广告平台投放广告，但曝光和点击数据分散在多个平台，投放数据和转化数据分散割裂，无法准确识别跨域用户，更难评估同一波投放对整体生意增长的贡献。

**b.参与数据**

•阿里妈妈：设备ID转化映射数据、平台投放广告曝光数据、电商转化数据

•玛氏：公域投放广告曝光数据

**c.方案流程**

1.玛氏（ISV：ReachMax）和阿里妈妈分别准备数据，并完成元数据隐私保护配置；

2.调用SDH平台的跨渠道归因分析组件，提交MPC归因分析任务；

3.将玛氏的公域广告曝光数据与平台广告曝光数据，通过PSU技术进行安全聚合；

4.利用PSI技术将总曝光事件和淘内电商转化数据进行安全匹配，完成跨渠道密态归因，再通过隐私集合四则运算PC技术进行安全加和，得到总用户转化数据；

5.归因结案分析报告经DP加噪处理，避免个体用户数据泄漏；

6.跨域归因结果返回品牌方，用于后续广告投放策略优化。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/RqLx3F3TPpnPlyiaRANo9O25mqjXc3lh60pb86D4PibAcKC8fR9icX0Qeb5TcXiaibEuOFRpJ2RmYZjicibHTS0UyOaew/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=17)

**d.方案价值**

SDH通过隐私增强技术PETs（PSU、PSI、PC）能力。有效解决了玛氏在多平台广告曝光和用户转化数据割裂、无法进行跨域用户识别和转化效果衡量的问题，提供了安全、科学、高效的跨域广告效果衡量数据分析报告。在数据安全性、计算准确性和产出时效性上都较传统方案有显著提升。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEjF7EH93ib78yoibsqWKniah4bDfK13icuEYR2fn8ttj52Y86psrUcfLnuw/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=18)

通过SDH的跨域效果衡量服务，玛氏打破了数据孤岛，实现了“多渠道广告曝光”到“全域转化”的效果衡量。目前，该服务已覆盖美妆、个护、食品、母婴、健康等多个行业的20+头部品牌，累计生成分析报告超过300份。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEhjVtaeX5otL9UUVWtWDIL26WVD2KJw7MOF6RnvnFQLQurtGNSamXiaw/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=19)

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEDZ5nu7OxgoxWXRXz0Iia7vO8N7rGcgjewgl1kZN2BICqoyGZHcSx1hw/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=20)

德芙通过ReachMax（加和科技）和阿里妈妈百灵平台开展跨平台广告投放。基于阿里妈妈营销隐私计算平台SDH，品牌初步实现了跨平台用户全局频次控制，有效避免超投，提升预算利用效率。在此基础上，再结合阿里妈妈的精准人群定向能力，进一步发力新客转化，最终取得了较好的投放效果。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEwmcpCUWAibzibSAgbBdlttNo79rCa0HjqB28aBMMzaB3unE1db3DP3QA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=21)

**a.业务痛点**

商家在跨平台广告投放过程中，由于广告投放事件数据分散，导致无法互联互通。同一用户或老客容易被广告超频触达，不仅浪费投放预算，还可能引发用户的疲劳和反感，从而影响整体投放效果。

**b.参与数据与方案**

•阿里妈妈：设备ID转化映射数据、平台广告曝光数据

•ReachMax：公域投放广告曝光数据

**c.方案流程**

1.德芙（ISV：ReachMax）和阿里妈妈分别准备数据，并完成元数据隐私保护配置；

2.调用SDH的全域频控组件，提交MPC计算分析任务；

3.通过PSI技术，将ReachMax的公域广告曝光数据和阿里妈妈的用户映射数据进行安全匹配，实现跨域用户识别，再通过PC技术和阿里妈妈的广告曝光数据进行安全加和，计算全域广告曝光数据；

4.生成全域曝光频次数据，并反馈至平台，用于后续人群投放范围和定向策略的制定。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/RqLx3F3TPpnPlyiaRANo9O25mqjXc3lh6MeJY10P4icKEiamZvDFmM3T9BbKQdu8wOQnptEzahS6a0pxpsXySxWAw/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=22)

**d.方案价值**

通过PETs能力（PC，PSI），SDH将德芙和阿里妈妈的广告曝光数据进行安全融合，跨域识别同一用户并精准计算整体曝光频次。这样既能平衡广告覆盖广度与用户记忆深度，又能有效避免重复曝光带来的用户疲劳，帮助商家实现更精细化的投放管理。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEmL3EdUuVicrKu4xuXcln1lvYiaHr5l8xkt0jh5vtrQO9cfZFUTrtDjeg/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=23)

**•**ROI表现领先行业：整体ROI水平突破2，显著超越同期行业大盘；

**•**增量效能显著：超过八成用户在三次及以下曝光就完成触达，投放效率突出。私域渠道带来近五百万级的新增人群，占比超过六成；在支付环节，私域人群贡献超过一半的新增支付人数，以及接近九成的支付金额；

**•人群价值优：约一成私域曝光贡献了约三成的支付金额，价值密度高。进一步分析发现，这部分人群与品牌的核心消费人群高度重合，尤其在年轻主力消费群体和高价值人群中渗透表现更为突出。**

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/RqLx3F3TPpnvxRia3OVgiaSEa8Pn56Y2YEjibbe3sVibZJarNoibHagrWqbYOW4eFrTvS2RgkUCe25yjQ3MPuvia8ICg/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=24)

阿里妈妈营销隐私计算平台SDH的系列应用案例，展示了隐私增强计算技术在广告营销领域的前沿探索。从人群上翻与跨域追投，到全域消费者洞察，再到跨渠道效果衡量与控频优化，SDH正在帮助品牌突破数据孤岛，实现“可用不可见”的数据流通方式，释放数据的全链路营销价值。这一系列实践不仅证明了隐私计算在广告场景中的可行性与商业价值，也为行业在数据合规与用户隐私保护日益严格的背景下，提供了安全、高效的解决思路。通过技术与生态的双重驱动，SDH正在逐步建立广告行业的数据要素流通新范式，推动营销方式从“经验驱动”走向“数据智能驱动”。

未来，SDH将持续迭代平台能力，进一步提升安全多方计算、联邦学习、差分隐私等核心技术的性能与适用性，探索更复杂场景下的联合建模与跨域分析。同时，SDH也将携手行业生态伙伴，拓展广告投放、洞察分析、效果归因、频控监测等更多环节的应用场景，帮助广告主实现更加科学的决策、更合理的预算分配和更高效的营销增长。

---

END

![图片](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc6nDBjJbezO2dMG543RhUibcELU7juTxCMBicyhVZFabfkasM6z5KADwjiar6FZz9icibn5FYdllnUENbQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&randomid=pugabtu8&tp=webp#imgIndex=12)

## 💡 关于我们

阿里妈妈SDS（Strategic Data Solutions）团队 致力于用数据让商家和平台的增长战略更加科学有效。我们为阿里妈妈全线广告客户提供营销洞察、营销策略、价值量化、效果归因、隐私计算的技术服务。我们将持续在营销场景下的数据隐私安全和解决方案方向进行探索和落地，欢迎各业务方关注与合作。

📮联系邮箱：alimama\_tech@service.alibaba.com

也许你还想看

[隐私信息检索（PIR）技术 | 查询者与数据库的隐形博弈](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247496138&idx=1&sn=0990c9cbd86dc5a423a82121efef3932&scene=21#wechat_redirect)

[隐私保护机器学习（PPML）技术｜为 AI 筑起隐私防火墙](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247496198&idx=1&sn=6bd832e0588ce82f6a135237bb3725dd&scene=21#wechat_redirect)

[隐私增强技术（PETs）综述 | 一文了解隐私计算技术发展脉络](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247496100&idx=1&sn=96e592db24b7d5df5d69ce3b1ecb1210&scene=21#wechat_redirect)

[阿里妈妈营销隐私计算平台SDH：公用云应用案例分享](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247491869&idx=1&sn=34ae632ca6952d5369c1c04800375236&scene=21#wechat_redirect)

[隐私集合运算（PSO）技术](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247496129&idx=1&sn=626841f56871b5ad295dca7b0728df38&scene=21#wechat_redirect)

**关注****[「阿里妈妈技术」](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490308&idx=1&sn=66643c1468bcec7a05449aedea9dc603&source=41&scene=21#wechat_redirect)，****了解更多****~**