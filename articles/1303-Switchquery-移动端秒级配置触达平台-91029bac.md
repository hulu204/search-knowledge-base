---
title: 'Switchquery：移动端秒级配置触达平台'
company: 京东
tag: 时效性
date: 2022-11-16
url: http://mp.weixin.qq.com/s?__biz=MzUyMDAxMjQ3Ng==&mid=2247500101&idx=1&sn=22f37f697144abc0c46f855650e0bd14&chksm=f9f25696ce85df8022f66975523f312f2aad321915ef4c8b3e38cf9783c2b791d64b14829776#rd
account: 京东零售技术
origin: wechat-mp
---
**一、背景**

随着移动互联网的快速发展，为满足各类用户及人群的体验需求，移动端的开发者们开发了丰富多彩的体验与功能。同时对于快速控制各类功能的切换、灰度，降级等能力的要求也越来越高，例如通过配置快速打开某个灰度功能，通过配置信息的实时触达关闭某个引起App崩溃的功能等等。因此需要一套具有实时触达配置信息到移动端的能力，低沉本的配置平台来解决。我们研发了Switchquery配置平台，它是一套具有秒级变更能力，助力业务快速变更，让配置信息在App运行中秒级生效，同时提升配置信息触达率，统一管理的配置平台。

**二、技术原理**

**1**

**触达技术选型**

在Switchquery配置平台核心能力中，实时触达的能力尤为重要，目前业界主流的触达技术方案主要有以下几种方式：

**1) 推送push 消息：**push消息当前已经成为实时推送营销信息、重要通知的最主要手段之一，push消息拥有较强的实时性，而实际的移动端的应用场景中，push消息多用于营销方案或重要信息的通知，很少使用此通道来作为研发配置信息的触达通道，其会产生UI交互的变化。另外push消息依赖于用户打开通知权限开关，而业内普遍打开通知开关权限的比例低于50%，因此大部分用户无法触达。

**2) tcp或websocket长连接：**通过建立一条客户端到服务端之间的长连接通道，此方案可以在发生配置信息变更后实时的将信息传递至客户端，但是需要耗费较大的服务器资源，来维护一条长连接通道。

**3) 轮询：**客户端以一定的时间间隔向服务端发出请求，通过频繁请求的方式来保持客户端和服务器端的信息同步，这种同步方案的最大问题是当客户端以固定频率向服务器发起请求的时候，服务器端的数据可能并没有更新，这样会带来很多无效的网络传输。

**2**

**实现原理**

**2.1**

**实时触达方案**

由于推送push消息方案存在触达比例低的问题，长链接存在耗费服务器资源的缺点，同时轮询的方案也存在很多无效的网络传输等弊端，因此以上三种方案都不是Switchquery 配置平台的触达方案的最佳技术选型。通过调研，我们采取了一种配置信息从服务端实时触达到客户端的新方案，方案的具体描述为：先搭建一个信息配置管理CMS平台，同时构建一个客户端获取配置信息的客户端组件，由用户在CMS配置信息，然后由CMS后台将配置信息的版本号信息同步至统一网关，所有客户端请求到达统一网关，并在返回的接口数据的header内都会携带最新的版本号至客户端，客户端对比发现新的版本号比缓存的版本大则请求配置信息拉取Switchquery配置接口，这样只要App打开就会存在接口携带变化标志返回，这样就会触发客户端主动发起请求更新配置信息，提高了实时性，不受push开关权限控制和影响，不需要额外打造长连接通道，具有低成本，实时性高等优点。以下是Switchquery配置平台的时序图：

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF8Iib3icV1vRIzdV1icdGM2iamHbmib3exMnIQYd15KXKq0LyGlWeCricCTru37xAqTYTEdr47ssJAv9wibg/640?wx_fmt=png)

1) 用户在Switchquery CMS 后台配置相关信息，目前平台上支持配置布尔类型、整型、字符串等类型的配置信息，可以配置App版本生效区间，按设备号灰度比例，iOS或者安卓平台的设定，生效白名单等相关信息。

2) Switchquery CMS后台配置信息并提交和保存完成后，由CMS配置后台将新的版本号写入到统一网关后台（所有客户端到服务端的http请求都会经过统一网关，所有服务端返回到客户的http请求响应都会经过统一网关），统一网关记录下数据版本号，客户端的所有接口请求的响应header增加一个字段x-switch-config，此字段会携带回配置信息的版本号至客户端。

3) Switchquery CMS配置后台完成信息配置后，后台会基于当前时间戳，生成一个新的配置信息版本号，同时将这些配置的静态数据写入到服务端内存缓存内，同步刷新配置开关接口。

4) Switchquery CMS配置后台将配置信息数据写入和保存一份静态数据json到CDN，防止接口降级或者失败以后可以降级从CDN拉取配置信息数据。

5) 网关会将版本号下发至客户端网络组件，网络组件在接受到网络请求返回后，首先会解析网络请求的响应header，如果解析到关键字将其对应的value一起解析封装后发起一个全局通知。

6) 配置客户端组件在监听到通知后，与本地已经缓存的配置信息数据版本号进行比对，相同则不处理，大于本地版本号则发起配置信息拉取请求，这样即可获取到最新的开关配置信息并缓存在磁盘。

7) 客户端在接口降级或者失败后会从CDN拉取配置数据信息。

此种触达方式只要客户端打开即会触发请求至统一网关，随即就可以根据变化情况来决定是否更新最新的配置接口数据，无需push通知，无需建立长连接通道，成本低，实时性高。

**2.2**

**流程架构设计**

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF8Iib3icV1vRIzdV1icdGM2iamHTBlDC7I6S7rY9ic0A0twdQEG5iaMjyCCzm7pWDicMAEtdNMB4rEf1evuA/640?wx_fmt=png)

1) 用户在CMS配置平台进行信息配置后，配置后台接口对配置信息进行对比，包括配置信息中的开关的状态，开关值等关键信息，如果没发生变化，则结束；发生变化则判断此次变更距离上一次变更是否到了n秒，距离n秒内则不会触发配置信息变更同步，距离n秒外则触发配置信息同步，触发网关和后台接口数据发生变化。

2）CMS触发变化将新的版本号传递至统一网关，统一网关会做数据版本号的存储，同时会将统一网关的所有机器内存里都存储一份最新的版本号。也会将数据变更信息同步到配置后台接口，同步写入一份json静态数据到CDN，这个是为了防止配置信息接口服务端挂了后可以走CDN兜底。

3）客户端任意接口请求都会经过统一网关，所有请求的返回也会通过统一网关返回，在返回的响应header内新增一个x-switch-config字段，其value是一段字符串，由下划线隔开，格式如：switch\_version\_randomtime\_reserved,第一个字段switch=0/1，其中0表示此能力统一降级关闭，1表示此能力打开；第二个字段version就是配置信息的数据版本号，目前是按时间戳的形式标识版本号；第三个字段randomtime表示客户端获取到版本号变化差异后并非立刻请求，会延迟[0,randomtime]之间的一个随机时间后才发起请求，这个是为了降低瞬间尖峰流量的产生；第四个字段是留作未来使用。

4）客户端网络框架在客户端会不间断随机广播全局通知， 开关客户端组件收到通知后，获取到统一网关的返回数据，解析网络接口返回的header部分，获取x-switch-config字段，解析字段中的value，如果是降级，则结束，如果版本号没有发生变化,则结束，如果非限流同时 switch=1，并且本地的缓存的开关version小于解析后的version，则根据randomtime随机数发起客户端请求；如果服务端返回了特定的限流码则客户端直接从CDN拉取配置信息数据并更新本地缓存数据，如果服务端正常返回则获取开关数据并更新本地缓存。

**3**

**技术优化**

在Switchquery 配置平台的设计开发中，从实时性，性能，成本，稳健等多维度进行了优化，具体的优化措施如下：

1）考虑到实时性与机器成本的平衡，我们在CMS配置端做了聚合n秒后才将配置变更同步至统一网关，主要为了防止多个用户在很近的时间内做了多个修改，会导致统一网关侧频繁的接收到不同的版本号，进而引起客户端频繁的发起请求，导致配置信息服务端的流量陡增，目前的经验值是n=5秒。

2）考虑性能与机器成本的平衡，客户端会根据randomtime来随机发起请求，是为了打散请求发起时机，实际经验我们发现5s会增日常2倍左右的QPS，10s会增加日常1.5倍左右，实际各个场景可以根据自身的服务器机器数量与成本来动态决定选择设置多长时间。

3）为了保障在大促或者特殊促销场景下的稳定性和健壮性，我们在配置信息产生后，首先写入数据到服务器的内存里，这样每次客户端的请求就直接读取内存性能很高，另外也会写入一份json数据到CDN，当服务端出问题后或在大促主动降级后可以通过CDN来兜底。

4）实时触达方案在App原生端来实现此功能，同时对于App内嵌的小程序、H5、RN都提供了桥接组件，尤其webview也可以读取此配置信息来实现配置信息的实时获取。

**三、接入流程**

**1**

**客户端**

**1.1**

**Android 平台接入**

```
//获取bool开关值,switchName:开关名称，拉取失败或未取到配置返回defValue默认值SwitchQueryFetcher.getSwitchBooleanValue(String switchName, boolean defValue)//获取int开关值，拉取失败或未拉取到配置返回defValue默认值SwitchQueryFetcher.getSwitchIntValue(String switchName, int defValue)//获取String开关值，拉取失败或未拉取到配置返回defValue默认值SwitchQueryFetcher.getSwitchStringValue(String switchName, String defValue)
```

**1.2**

**Apple 平台接入**

```
//自定义bool开关，获取不到返回NOBOOL JDSwitchBoolValue(NSString *key); //自定义整型开关，获取不到返回0NSInteger JDSwitchIntValue(NSString *key); //自定义字符开关，获取不到返回nilNSString* JDSwitchStringValue(NSString *key); //取intvalue  NSNumber *n1 = [JDRouter openURL:@"router://JDBSHServerConfigModule/intValue?key=test"                   arg:nil                 error:nil            completion:nil]; //取boolvalue   NSNumber *n2 = [JDRouter openURL:@"router://JDBSHServerConfigModule/boolValue?key=test"                arg:nil                error:nil        completion:nil];//取stringValue NSString *n3 = [JDRouter openURL:@"router://JDBSHServerConfigModule/stringValue?key=test"                arg:nil                error:nil        completion:nil];
```

**2**

**CMS 创建**

为了让研发测试阶段和线上的数据安全隔离，预发和线上的数据是隔离的，在预发环境测试验证OK后，配置数据再同步到线上。

**2.1**

**业务模块创建**

进入CMS界面，选择左侧的模块管理菜单，进入模块管理界面，新增业务模块，弹出弹窗如下图：

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF8Iib3icV1vRIzdV1icdGM2iamHVgYBUvJc36qVdVwWTzic1utopHVL53a1hS71EeSAQ46KaPDgSbRtKNw/640?wx_fmt=png)

1）名称：对应业务模块名称；

2）关键字：设置对应业务模块的关键字；

3）管理员：模块分配的管理员，一般默认为模块的创建者；

4）成员：该模块分配的管理成员，成员有新增，删除，修改该模块下的配置权限，但没有修改，删除当前模块的权限；

5）说明：对当前模块的描述；

**2.2**

**配置创建**

创建好业务模块后，在该业务模块下新建或者编辑配置，编辑界面如下图：

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF8Iib3icV1vRIzdV1icdGM2iamHria5IGb2vQ8tIM7J7zGicpViaCjkNpwcZ3OraW56J5ft7u2JFibsSO9CSg/640?wx_fmt=png)

1）开关编号：为当前开关配置分配的唯一标识编号;

2）平台版本：目前支持android，apple，ipad三种平台，可支持开关生效App的版本的区间范围设置，按照左闭右开的原则，默认不设置，全版本生效；

3）系统版本：设置系统版本的区间，默认不设置，全系统版本生效；

4）开关类型：目前支持布尔开关，整形开关，字符串开关以及敏感数据开关(10.4.4版本以上)4种类型开关配置信息；

5)  开关名称：设置的开关配置名称；

6)  开关打开比例：命中规则为：android 平台根据uuid，apple平台根据openudid，通过hash算法算出来的值和100取余加1，如果最终值小于或者等于设置的值即为命中，反之不命中；

7)  白名单：该开关配置对应的白名单，可以通过手动的方式将pin以逗号分隔拷贝到编辑框，未来可接入尝鲜系统通过扫码的方式添加白名单；

8)  开关配置值：布尔开关默认不展示，整形或者字符串类型的配置类型需设置开关值；

9)  开关描述：通过描述知道开关配置的用途；

**四、收益**

  

**1**

**护航X项目**

在2022年春晚X项目中每次口播的时候面临着流量大，启动接口多的问题，这样会造成网关压力巨大，业务瘫痪的问题，会导致整个X项目的失败，不容有失。因此通过销峰降频，减少接口请求等方式进行App启动降级。通过Switchquery配置平台，在客户端下发降级信息配置，以及修正时间戳等数据，成功的保障X项目中App启动接口的成功降级。

**1.1**

**启动接口降级**

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF8Iib3icV1vRIzdV1icdGM2iamHec2f7mMS09sLDh5eMZwB43FAnRQ4ApPbvFh0xiaJ6rRdVqkImaesqyQ/640?wx_fmt=png)

降级成功率为100%，线上0事故，启动接口数从110个降级到8个。

**1.2**

**流量降级**

单个接口的峰值QPS比日常QPS降幅达88.7%左右,网关整体峰值QPS比日常QPS降幅达30%左右，均在2分钟之内完成降级。

**2**

**护航双十一**

2022年双十一期间Switchquery 保障了大促活动的稳定运营，具体情况如下：

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF8Iib3icV1vRIzdV1icdGM2iamHGIibAunicJibNm2ZqpEmuj551p3Niabpf2fhXooRQ8jgKHD48YeibEGRia2w/640?wx_fmt=png)

2022 年双十一期间，Switchquery 配置平台服务业务模块数为38个，在线开关总数为392个，整体开关配置的触达率为98.3%左右,服务开关配置秒级变更次数为61次，Switchquery配置接口峰值QPS环比去年下降58.8%有效的保障了大促活动的顺利进行。

**五、结语**

未来Switchquery配置平台会为更多的业务模块提供配置服务，同时我们会赋能更多的App，支持一整套从配置客户端组件控制到后台CMS支持多App切换以及网关实时秒级触达的一整套秒级触达的高性能移动配置技术方案。同时支持更完备的功能体验例如操作日志查看能力，支持机型过滤能力，黑白名单通过接入尝鲜平台通过扫码的方式动态添加等功能，打造一套具有秒级配置变更能力，助力业务快速变更的配置平台。