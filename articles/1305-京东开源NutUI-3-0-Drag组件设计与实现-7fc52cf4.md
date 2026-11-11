---
title: '京东开源NutUI 3.0 Drag组件设计与实现'
company: 京东
tag: 搜索
date: 2021-03-25
url: http://mp.weixin.qq.com/s?__biz=MzUyMDAxMjQ3Ng==&mid=2247496054&idx=1&sn=e647cf6fc32b964e59754e114ed8a48b&chksm=f9f266a5ce85efb364a5424e19d069537204690e86e75419222705ca501a8af6724787506db1#rd
account: 京东零售技术
origin: wechat-mp
---
京东零售开源项目 NutUI 是一套京东风格的轻量级移动端 Vue 组件库，是开发和服务于移动 Web 界面的企业级产品。经过长时间的开发与打磨，NutUI 3.0 终于要和大家见面了！3.0 版本在技术和视觉方面都做出了较大改进，让组件看起来更绚丽，用起来更舒服。

 NutUI 3.0 源码抢先看：https://github.com/jdf2e/nutui

主题介绍

今天的主题是 NutUI Drag 组件的设计与实现，Drag组件是 NutUI 的一个拖拽组件，它用于在移动端手指触摸拖动元素到指定位置去触发一些特定的事件。让我们一起来看看在组件的开发过程中是如何一步步实现组件功能的。

我们为什么要去封装组件，去做组件化开发，组件化其实就是将一个功能化的模块作为一个单独的个体去看待，我们可以在每个页面去单独调用，它的功能和样式都是可以实现复用的。其实我们不难理解我们为什么要做组件化，组件化可以让我们的代码低耦合，我们不用像传统开发一样把所有的东西都揉在一起，从而极大的提高了我们的开发效率。同时我们避免了重复造轮子，提高了我们的代码质量，降低了维护的成本。

实现思路

移动端实现拖拽有两种主流的实现方案：

1. 将元素设置为固定定位，然后在拖拽的时候修改其定位，实现拖拽的效果；

1. 使用 transform 中的平移 translate 属性实现拖拽。

这里我画了一张图方便大家更好理解:

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF8Fb8iatGutRfuicNLr5rOP0XZCDibiaAW0pQibF18KRLSfEPJvUDVlXS0OqgDJDpeyJsuPFicicQ3msej8w/640?wx_fmt=png)

我们本次使用的是第一种方案，这种方案的核心就是给元素添加固定定位 position:fixed;

原理分析

01

拖拽原理

在我们想要做出拖拽这个效果的时候，我们需要分清这几个属性的区别，这几个属性都是计算鼠标点击的偏移值，我们需要对其进行了解才可以继续实现我们的拖拽效果：

 clientY 指的是距离可视页面左上角的距离；

 pageY 指的是距离可视页面左上角的距离(不受页面滚动影响)；

 screenY 指的是距离屏幕左上角的距离；

 layerY 指的是找到它或它父级元素中最近具有定位的左上角距离；

 offsetY 指的是距离它自己左上角的距离。

实现的原理是手指在拖动的过程中，实时去改变元素的位置即 top 和 left 值，使元素随着手指的移动而移动。

当我们开始拖动时：获取到接触点相对于整个视图区的坐标 clientX ，clientY ；元素初始化时候距离顶部和左侧的距离，以及获取手指点击元素初始的x轴和y轴的距离。

 拖动过程中：实时获取元素距离视图上侧和左侧的距离值，并赋值给元素，使元素跟着手指的移动而动起来。

 拖动结束，添加一些对元素额外的处理效果。

02

移动事件

我们首先需要知道一些关于拖拽的事件：

**1. touchstart 事件：**当手指触摸屏幕时候触发，即使已经有一个手指放在屏幕上也会触发。

**2. touchmove 事件：**当手指在屏幕上滑动的时候连续地触发。在这个事件发生期间，调用 preventDefault() 事件可以阻止滚动。

**3. touchend 事件：**当手指从屏幕上离开的时候触发。

下边有几张动图方便大家更好的理解。

![](https://mmbiz.qpic.cn/mmbiz_gif/MrFJyDNenF8Fb8iatGutRfuicNLr5rOP0XSGiaSpxqQnlch6W3GWADOlfoHNOjD3bxXshx298xuCniauVRXiajWA8xA/640?wx_fmt=gif)

![](https://mmbiz.qpic.cn/mmbiz_gif/MrFJyDNenF8Fb8iatGutRfuicNLr5rOP0XZPxXvzEnlZB55q64yD1GoLSewLWPWRYP0nLbDIBUiazNs9LBRCFzVyQ/640?wx_fmt=gif)

![](https://mmbiz.qpic.cn/mmbiz_gif/MrFJyDNenF8Fb8iatGutRfuicNLr5rOP0X79TzE5fQu2U3Opn5YuMvzNsrD7x1kScuzro2o9o4UJZeYUKjMRYeEA/640?wx_fmt=gif)

通过上面对事件的理解，我们其实想一想，只需要监听三个事件 touchstart 事件、touchmove 事件、touchend 事件。需要知道开始拖拽时的元素是谁，拖拽后去往的元素是哪个，以及最后拖拽的结束。因为每一个拖拽的项都是一个组件，所以这三个事件每次拖拽都会触发。

每个触摸事件被触发后，会生成一个 event 对象，event 对象里额外包括以下三个触摸列表：

touches :当前屏幕上所有触摸点的集合列表

targetTouches : 绑定事件的那个结点上的触摸点的集合列表

changedTouches : 触发事件时改变的触摸点的集合

下边这张图片就很好的展现了三者的不同：

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF8Fb8iatGutRfuicNLr5rOP0XemUyEIAZDHvCdD5EibbdVgZvHW7WEysUkoUmUJiacHF0dAhzQwPibZhog/640?wx_fmt=png)

举例来说，比如 div1, div2 只有 div2 绑定了 touchstart 事件，第一次放下一个手指在 div2 上，触发了 touchstart 事件，这个时候，三个集合的内容是一样的，都包含这个手指的 touch ，然后，再放下两个手指一个在 div1 上，一个在 div2 上，这个时候又会触发事件，但changedTouches 里面只包含第二个第三个手指的信息，因为第一个没有发生变化，而 targetTouches 包含的是在第一个手指和第三个在 div2 上的手指集合， touches 包含屏幕上所有手指的信息，也就是三个手指。

过程详解

01

初步实现

首先我们去获取手指拖动元素距离顶部的距离，距离左侧的距离，以及手指点击的 x 轴和 y 轴的距离：

```
 const state = reactive({      elWidth: 0, // 元素的宽度      elHeight: 0, // 元素的高度      screenWidth: 0, // 屏幕的宽度      screenHeight: 0, // 屏幕的高度      startTop: 0, // 拖拽元素距离顶部的距离      startLeft: 0, // 拖拽元素距离      direction: props.direction, //限定拖拽方向      position: { x: 0, y: 0 }, // 初始化位置      boundary: {  // 边界限定        top: 0,        left: 0,        right: 0,        bottom: 0      }     })   function touchStart(e: TouchEvent) {      const target = e.currentTarget as HTMLElement;      const touches = e.touches[0];      state.startTop = target.offsetTop; // 元素距离顶部的距离      state.startLeft = target.offsetLeft; // 元素距离左侧的距离      state.position.x = touches.clientX; // 手指点击的x轴的距离      state.position.y = touches.clientY; // 手指点击的y轴的距离    }
```

然后在移动的时候，计算每次移动的横向距离和纵向距离，并改变元素的 left 和 top 值，其中 direction 是用来限定在 x 轴还是 y 轴拖拽，默认为 all，各个方向都可以拖拽。

```
 function touchMove(e: TouchEvent) {      e.preventDefault();      const target = e.currentTarget as HTMLElement;      if (e.targetTouches.length === 1) {        const touch = e.targetTouches[0];        state.nx = touch.clientX - state.position.x;        state.ny = touch.clientY - state.position.y;        state.xPum = state.startLeft + state.nx;        state.yPum = state.startTop + state.ny;        target.style.left = state.xPum + 'px';        target.style.top = state.yPum + 'px';    }
```

02

边界判断

这样做就实现了拖拽啦，当然，单纯这样做是不行的，假如我们使劲往外拖动，那么它会滑出屏幕以外（可视区域之外），那样的话我们再使劲也是拖不回来啦，所以我们需要做一个边界限制。还得完善一下代码，去判断上下左右四个方向的边界，如果超过边界值就不能在拖动了，边界值实际上就是在屏幕上能拖动的最大距离。

```
 const rightLocation =          state.screenWidth - state.elWidth - state.boundary.right;    // 限制左右拖拽边界    if (Math.abs(state.xPum) > rightLocation) { //如果拖拽元素所在的位置大于左右边界，就让该拖拽元素的x轴位置为最大边界         state.xPum = rightLocation;       } else if (state.xPum <= state.boundary.left) {          state.xPum = state.boundary.left;       }       // 限制上下拖拽边界        if (state.yPum < state.boundary.top) {          state.yPum = state.boundary.top;        } else if (          state.yPum >          state.screenHeight - state.elHeight - state.boundary.bottom        ) {          state.yPum =            state.screenHeight - state.elHeight - state.boundary.bottom;        }
```

让我们来看一看效果吧。

![](https://mmbiz.qpic.cn/mmbiz_gif/MrFJyDNenF8Fb8iatGutRfuicNLr5rOP0XJJP2ia6WmZ2CicSW809Ht4yqqddwwggFr7WZFJZ0LF0QZnicjhy0T28jA/640?wx_fmt=gif)

我们还可以继续在上述代码中进行优化，可以增加限制拖动元素只能在 x 轴还是 y 轴进行拖动，如果是限定为 x 轴的话，就让y轴的距离不变，反之一样，限定为y轴的话，就让 x 轴的距离不变。

```
  if (props.direction != 'y') { // direction默认为all，所有方向都可以移动        target.style.left = state.xPum + 'px';      }     if (props.direction != 'x') {        target.style.top = state.yPum + 'px';      }
```

![](https://mmbiz.qpic.cn/mmbiz_gif/MrFJyDNenFibZgtuFMSQiacWvWC77ZqvnhVjYgZKWjpYs5UxLicmaN8zOMcyEIKPibLzY2JDhYI2ibibJqic55syKs0FA/640?wx_fmt=gif)

03

吸附效果

我们还可以为这个组件添加吸附功能，将页面从中间分开，去判断它的当前位置，假如它在左边的二分之一中的时候，当我们松开手指的时候，就让其自动吸附到左边边界，反之是一样的道理，当它在右边的二分之一的时候，当我们松开手指的时候，就让其自动吸附到右边边界。

我们需要 touchend 结束事件的时候去进行判断当前元素的位置是在哪里。

```
 function goLeft(target: HTMLElement) {      if (state.boundary.left) {        if (+target.style.left.split('px')[0] > state.boundary.left) {          target.style.left = +target.style.left.split('px')[0] - 10 + 'px';          requestAniFrame(() => {            goLeft(target);          });        } else {          target.style.left = `${state.boundary.left}px`;        }      } else {        if (+target.style.left.split('px')[0] > 10) {          target.style.left = +target.style.left.split('px')[0] - 10 + 'px';          requestAniFrame(() => {            goLeft(target);          });        } else {          target.style.left = '0px';        }      }    }    function goRight(target: HTMLElement, rightLocation: number) {      if (rightLocation - parseInt(target.style.left.split('px')[0]) > 10) {        target.style.left =          parseInt(target.style.left.split('px')[0]) + 10 + 'px';        requestAniFrame(() => {          goRight(target, rightLocation);        });      } else {        target.style.left = rightLocation + 'px';      }    }
```

效果就是这样啦。

![](https://mmbiz.qpic.cn/mmbiz_gif/MrFJyDNenF8Fb8iatGutRfuicNLr5rOP0X6Tap5OMWgRb9Pk0wn9pk55VOttsjvwHic1HnEyO8D5XgITPKzntm4SA/640?wx_fmt=gif)

结语

到这里我们就已经把拖拽效果用Vue组件的形式实现了，我们是用了定位的方式实现了拖拽，其实使用 transition 也是一样的，都是换汤不换药，我们需要弄清楚 pageY 、 screenY 、 clientY 、 layerY 、 offsetY 等区别。后续会加入一些对于拖动元素的操作，比如旋转，缩放等效果。本文介绍了 NutUI 中 drag 组件的实现方式，与大家共勉。最后再提一下我们的 NutUI 组件库，长期以来，团队的小伙伴都在尽心尽力地维护着 NutUI 2.0。在 3.0 版本发布后，我们依然会积极地维护与迭代，为有需要的同学提供技术支持，也会不定时地发布一些相关的文章帮助大家更好地理解与使用我们的组件库。

NutUI 3.0 预计发布的时间是 2021-03-31 。敬请期待！

NutUI 2.0：nutui@jd.com

来点个 Star 💚支持我们一下吧 ~