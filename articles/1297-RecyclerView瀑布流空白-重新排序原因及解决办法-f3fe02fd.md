---
title: 'RecyclerView瀑布流空白、重新排序原因及解决办法'
company: 京东
tag: 排序
date: 2020-05-18
url: http://mp.weixin.qq.com/s?__biz=MzUyMDAxMjQ3Ng==&mid=2247492472&idx=1&sn=81c83d6c6eda100da94e3511db23c0e5&chksm=f9f274abce85fdbd1d0590ef30a1ebd981478f2d8005bb2512b0d832732cd0a51eec8fc3649b#rd
account: 京东零售技术
origin: wechat-mp
---
前言

在Android中RecyclerView配合LayoutManager可以实现多种列表效果，比如可以实现横滑、纵滑列表的的LinearLayoutManager，网格布局的GridLayoutManager， 如果想实现瀑布流的效果，那么使用StaggeredGridLayoutManager即可，但StaggeredGridLayoutManager也暴露出了一些问题，比如列表重排序、列表顶部出现空白,下面我们将会分析使用StaggeredGridLayoutManager实现瀑布流时，列表重排序以及顶部出现空白的原因及解决办法。

问题

01

列表重排序

列表重排序是列表在滚动过程中item的位置出现变化，这个问题解决相对容易一些。

```
layoutManager.setGapStrategy(StaggeredGridLayoutManager.GAP_HANDLING_NONE);  GAP_HANDLING_NONE表示不对任何空白间隙做处理。  
```

但也由此引发了下面的问题:

当列表出现空白间隙时，StaggeredGridLayoutManager其实是会对列表重排序来消除间隙，设置GAP\_HANDLING\_NONE后，屏蔽了这种机制，导致了顶部item空白的出现。

02

列表顶部空白

如下图所示：

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF9fDdkGJzcdwbklExa1KQAe3YglyCgiazFwnMyaq8tq7l1jNpsPFnXYoy37JJRe0BVhfpqXYJAfpLQ/640?wx_fmt=png)

查阅了一些资料找到一些解决办法:

```
layoutManager.setGapStrategy(StaggeredGridLayoutManager.GAP_HANDLING_NONE);//设置不对空白间隙处理  recyclerView.addOnScrollListener(new RecyclerView.OnScrollListener() {        @Override         public void onScrollStateChanged(RecyclerView recyclerView, int newState) {             super.onScrollStateChanged(recyclerView, newState);             staggeredGridLayoutManager.invalidateSpanAssignments();//重新布局         }         @Override        public void onScrolled(RecyclerView recyclerView, int dx, int dy) {               super.onScrolled(recyclerView, dx, dy);        });        public void invalidateSpanAssignments() {           // 将spanIndex数组清空，进行重绘,后面会讲解mLazySpanLookup的作用            mLazySpanLookup.clear();            requestLayout();        }  
```

这种方式确实是“解决了”空白的问题，但还是有一些问题：

* 造成图片闪烁;
* 调用invalidateSpanAssignments会重新测量、布局、重绘，由于是在滚动状态发生变化时调用，每次滚动都会造成至少2-3次的重绘，消耗性能;

在这里说一个更好的解决方案：使用notifyItemRangeChanged进行列表刷新，使用notifyItemRangeInser刷新分页数据，从而替代notifyDataSetChanged进行列表刷新。

下面我们将分析出现空白的原因。

造成空白的原因

01

现象分析

大家再看一下下面这张图，左右两张图中item的位置变化。

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF9fDdkGJzcdwbklExa1KQAevPo2Br6XoMlUuWJxyDFHfiatSeyjwu4zWVvfRwvwaNicrJagiaTVUcJJw/640?wx_fmt=png)

左侧图片是初始化时的展示，右侧图是加载了分页数据，列表刷新之后，重新回滚到顶部时的展示，显然右侧图的位置较之前出现了改变。

当我们有需求需要对列表整体进行刷新，或者在分页场景下，列表滚动并不在首屏，此时我们进行了分页数据的加载，如果使用notifyDataSetChanged进行了数据的更新，列表再回滚回去时，顶部就会出现空白。

我们从上图中大概也能猜到问题产生的原因，是由于索引变化导致的。下面我们将会对产生的原因进行具体分析。

02

RecyclerView的测量及布局流程

我们看下RecyclerView的测量布局的流程：

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF9fDdkGJzcdwbklExa1KQAeicSib3RFHTiawdBibiaPQC5KnW86AqNw1bict2EBavpEsWBRl2ANichOibIGfg/640?wx_fmt=png)

03

流程简化

在上面的流程图中忽略了一些判断条件，为了更直观分析，我们再简化一下:

* 瀑布流使用的是StaggeredGridLayoutManager，在StaggeredGridLayoutManager中isAutoMeasureEnabled的实现是设置为GAP\_HANDLING\_NONE时才为false,此处没有设置则为true。
* RecyclerView设置layout\_width和layout\_height都是match\_parent, 测量模式为EXACTLY,所以measureSpecModeIsExactly 为true。

那么简化流程图如下：

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF9fDdkGJzcdwbklExa1KQAeelVhugjPSuFqibmVkdWwbCTpxrLUc1R3fuzYO2cmqqzYVdyibic6VPNoQ/640?wx_fmt=png)

后面将以上面的流程分析，可以先有一个印象的流程，后续会具体分析。

StaggeredGridLayoutManager布局过程

LayoutManager负责的item的布局，因为是瀑布流，我们去看一下源码在StaggeredGridLayoutManager中是如何对处理item view的。

01

源码分析

LayoutManager对child 处理的入口为onLayoutChildren()。

```
 private void onLayoutChildren(RecyclerView.Recycler recycler,RecyclerView.State state, boolean shouldCheckForGaps) {          if (anchorInfo.mLayoutFromEnd) {                 // 省略部分代码...                fill(recycler, mLayoutState, state);//负责对RecycleView的item的填充与回收。                // 省略部分代码...           } else {               // 省略部分代码...               fill(recycler, mLayoutState, state);//负责对RecycleView的item的填充与回收。               // 省略部分代码...           }       }       private int fill(RecyclerView.Recycler recycler, LayoutState layoutState, RecyclerView.State state) {           while (layoutState.hasMore(state)                   && (mLayoutState.mInfinite || !mRemainingSpans.isEmpty())) {               //简单说这个while循环逻辑是指 列表中有内容同时适配器adapter中还有更多的数据时为true               View view = layoutState.next(recycler);               LayoutParams lp = ((LayoutParams) view.getLayoutParams());               final int position = lp.getViewLayoutPosition();                  //mLazySpanLookup 中存储adapter每一个item的 position与spanIndex之间的映射，               //通俗点就是可以通过item的position从mLazySpanLookup中获取到对应的spanIndex               final int spanIndex = mLazySpanLookup.getSpan(position);               Span currentSpan;               final boolean assignSpan = spanIndex == LayoutParams.INVALID_SPAN_ID;//判断spanIndex是否有效               if (assignSpan) {                   //spanIndex无效 重新计算                   //lp.mFullSpan是指当前view是否填充满所有跨度，假如我们瀑布流是竖向的具有两列，如果返回true,则该view将填充满屏幕宽度。                   //getNextSpan(layoutState) 生成一个span                   currentSpan = lp.mFullSpan ? mSpans[0] : getNextSpan(layoutState);                   mLazySpanLookup.setSpan(position, currentSpan);//存储span                   if (DEBUG) {                       Log.d(TAG, "assigned " + currentSpan.mIndex + " for " + position);                   }               } else {                   //spanIndex有效 ，不需要重新计算                   if (DEBUG) {                       Log.d(TAG, "using " + spanIndex + " for pos " + position);                   }                      //mSpans数组存储了代表每一列的sapn，列表是5列的数组，数组的长度就是5，在                   // StaggeredGridLayoutManager的构造方法中初始化                   currentSpan = mSpans[spanIndex];               }               // assign span before measuring so that item decorators can get updated span index               lp.mSpan = currentSpan;               if (layoutState.mLayoutDirection == LayoutState.LAYOUT_END) {                   //手指向上滚动时，在列表尾部addView                   addView(view);               } else {                   //手指向下滚动时，在列表头部，即列表的第一个位置，index=0的位置插入view                   addView(view, 0);               }               // 省略部分代码...           }       }  
```

在onLayoutChildren中调用了fill方法，该方法主要是负责View的填充。

从上面的源码中可以看到，在fill ()方法的处理中，首先获取了View的spanIndex（通过spanIndex找到View对应的span，从而可找到item是在第几列）并对spanIndex有效性做了判断。

上面有提到，出现空白的原因是spanIndex出现了变化导致item所处的列出现了变化，也就说很有可能是我们刷新列表之后，item的spanIndex无效了，即源码中 spanIndex ==  LayoutParams.INVALID\_SPAN\_ID时，重新生成了一个新的span，item的所在列的位置出现了变化，最终导致排序后的item无法刚好填充满屏幕，出现了空白。

02

布局流程图

我们看下onLayoutChildren过程的流程图如下：

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF9fDdkGJzcdwbklExa1KQAeUibrJQkkMvJ1p5W9YZGiasibUcuqDu4AhNdcic57qdrGK2bcQjoibeYPg9Q/640?wx_fmt=png)

notifyDataSetChanged刷新过程

我们推测使用notifyDataSetChanged时，会导致spanIndex无效，进而导致不能找到刷新之前标记其位置的span。接下来我们看看当调用notifyDataSetChanged时做了什么操作，会导致spanIndex无效。

01

源码分析

**1.1 notifyDataSetChanged过程**

notifyDataSetChanged源码如下：

```
 public final void notifyDataSetChanged() {           mObservable.notifyChanged();//此处的mObservable为AdapterDataObservable   }   static class AdapterDataObservable extends Observable<AdapterDataObserver> {            public boolean hasObservers() {                 return !mObservers.isEmpty();            }            public void notifyChanged() {                  for (int i = mObservers.size() - 1; i >= 0; i--) {                      mObservers.get(i).onChanged();//实际是调用RecyclerViewDataObserver的onChanged（）                  }              }   }   private class RecyclerViewDataObserver extends AdapterDataObserver {           @Override           public void onChanged() {               assertNotInLayoutOrScroll(null);               mState.mStructureChanged = true;               processDataSetCompletelyChanged(true);               if (!mAdapterHelper.hasPendingUpdates()) {                   requestLayout();//将会执行执行RecycleView的onMeasure、onLayout、onDraw               }           }   }     /**       * True after the data set has completely changed and          数据集发生了变化，并且这个变化已经完成       * {@link LayoutManager#onItemsChanged(RecyclerView)}should be called during the subsequent       * measure/layout.当为true时，onItemsChanged应该在measure/layout时被调用       * @see #processDataSetCompletelyChanged(boolean)       */    boolean mDispatchItemsChangedEvent = false;    void processDataSetCompletelyChanged(boolean dispatchItemsChanged) {          // 调用notifyDataSetChanged时，此处设置为true，代表数据集发生了变化，并且这个变化已经完成           mDispatchItemsChangedEvent |= dispatchItemsChanged;           mDataSetHasChangedAfterLayout = true;           markKnownViewsInvalid();    }  
```

从上述源码中可以看到，当调用notifyDataSetChanged之后最终是调用了RecyclerViewDataObserver的onChanged()，该方法会做一些视图无效化的操作，这里只关注我们需要的:

* 设置mDispatchItemsChangedEvent标记为true，即代表数据集发生了变化，并且这个变化已经完成，源码中针对该字段注释中可以看到，当为true时， onItemsChanged应该在measure/layout时被调用。
* 调用了requestLayout(),那么接下来将执行RecyclerView的onMeasure、onLayout、onDraw。

**1.2 onMeasure、onLayout过程**

这里先说下结论，在onItemsChanged()中做了使spanIndex无效的操作，而且注释中也提示我们它是在measure/layout时被调用，刚好这里调用了reqeustLayout下一步就是执行onMeasure了，先不管onItemsChanged做了什么，先按执行顺序走，我们看下onMeasure的源码：

```
           @Override       protected void onMeasure(int widthSpec, int heightSpec) {           //此处级调用的是StaggeredGridLayoutManager中的isAutoMeasureEnabled()，此处返回true           if (mLayout.isAutoMeasureEnabled()) {                //此处我们只针对一种情况分析，RecycleView 设置的layout_width和layout_height都match_parent,              //其他情况比如大同小异，该执行的方法都会执行               final int widthMode = MeasureSpec.getMode(widthSpec);//获取测量模式               final int heightMode = MeasureSpec.getMode(heightSpec);               mLayout.onMeasure(mRecycler, mState, widthSpec, heightSpec);   //RecycleView设置的match_parent那么它的测试模式就是MeasureSpec.EXACTLY，   //measureSpecModeIsExactly为true               final boolean measureSpecModeIsExactly =               widthMode == MeasureSpec.EXACTLY && heightMode == MeasureSpec.EXACTLY;               if (measureSpecModeIsExactly || mAdapter == null) {                   //此处measureSpecModeIsExactly为true,直接return，接下来将执行onLayout                   return;               }           }else{               //省略代码...           }             //省略代码...   }      @Override       public boolean isAutoMeasureEnabled() {//未设置GAP_HANDLING_NONE，返回true           return mGapStrategy != GAP_HANDLING_NONE;       }  
```

onMeasure执行完成，接下来就是onLayout，我们接着看：

```
  @Override       protected void onLayout(boolean changed, int l, int t, int r, int b) {           TraceCompat.beginSection(TRACE_ON_LAYOUT_TAG);           dispatchLayout();//这是重点圈起来           TraceCompat.endSection();           mFirstLayoutComplete = true;       }          void dispatchLayout() {            //代码被我精简了，这里主要就是执行布局的三步骤。我们只关注第一步dispatchLayoutStep1()           dispatchLayoutStep1();           dispatchLayoutStep2();           dispatchLayoutStep3();       }         private void dispatchLayoutStep1() {           processAdapterUpdatesAndSetAnimationFlags();      }   private void processAdapterUpdatesAndSetAnimationFlags() {             if (mDispatchItemsChangedEvent) {                //上面分析了调用notifyDataSetChanged会把mDispatchItemsChangedEvent置未true                //调用了StaggeredGridLayoutManager的onItemsChanged                mLayout.onItemsChanged(this);           }       }  
```

onLayout中执行了dispatchLayout()，dispatchLayout分三个步骤进行布局（这里我忽略了很多判断逻辑，不影响我们进行下去），在这里我们只关注第一步骤dispatchLayoutStep1()，从源码中可以看出在dispatchLayoutStep1()中调用了StaggeredGridLayoutManager的onItemsChanger()。

OK，到最后了，看下onItemsChanged的实现：

```
 @Override    public void onItemsChanged(RecyclerView recyclerView) {        mLazySpanLookup.clear();//调用LazySpanLookup.clear()        requestLayout();    }    static class LazySpanLookup {          void clear() {                if (mData != null) {                    //将mData的数据都置为LayoutParams.INVALID_SPAN_ID                    Arrays.fill(mData, LayoutParams.INVALID_SPAN_ID);                }                mFullSpanItems = null;          }        }  
```

onItemsChanged中的代码很少，主要就是为将mLazySpanLookup 做clear操作，将存储有spanIndex的mData数组中元素都置为了LayoutParams.INVALID\_SPAN\_ID无效，至此，当查找item的spanIndex时，因为无效了，所以重新生成了一个新span，由此导致item所处在的列出现了变化。

我们瀑布流item高度并不是一致的，item所在的列出现了变化，顺序乱了，重新排序之后，就不一定能够刚好把空间都占用，留出了顶部的空白。结合下面的刷新流程图会更好理解一些。

02

notifyDataSetChanged处理流程图

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF9fDdkGJzcdwbklExa1KQAecW9ykBTJyA2MPkwibU26QVuzj9KAGJRNjPqGn9gWHdI3iabtX2pTXCDA/640?wx_fmt=png)

notifyItemRangeChanged 刷新过程

notifyItemRangeChanged和notifyItemRangeInser关键流程一致，这里选择

notifyItemRangeChanged进行分析。

01

notifyItemRangeChanged分析

我们看下notifyItemRangeChanged的源码，为什么notifyItemRangeChanged不会导致空白问题：

```
 public final void notifyItemRangeChanged() {          mObservable.notifyItemRangeChanged();//此处的mObservable为AdapterDataObservable   }      static class AdapterDataObservable extends Observable<AdapterDataObserver> {          public void notifyItemRangeChanged(int positionStart, int itemCount) {                  notifyItemRangeChanged(positionStart, itemCount, null);       }           public void notifyItemRangeChanged(int positionStart, int itemCount, @Nullable Object payload) {               for (int i = mObservers.size() - 1; i >= 0; i--) {                   //实际是调用RecyclerViewDataObserver的onChanged（）                   mObservers.get(i).onItemRangeChanged(positionStart, itemCount, payload);               }        }   private class RecyclerViewDataObserver extends AdapterDataObserver {           @Override           public void onItemRangeChanged(int positionStart, int itemCount, Object payload) {               assertNotInLayoutOrScroll(null);               if (mAdapterHelper.onItemRangeChanged(positionStart, itemCount, payload)) {                   triggerUpdateProcessor();               }           }   }        void triggerUpdateProcessor() {               if (POST_UPDATES_ON_ANIMATION && mHasFixedSize && mIsAttached) {                   ViewCompat.postOnAnimation(RecyclerView.this, mUpdateChildViewsRunnable);               } else {                   //mHasFixedSize 为false,执行到这里                   //没有对mDispatchItemsChangedEvent进行 赋值true的操作                   //调用requestLayout 重绘时，不会clear spanIndex                   mAdapterUpdateDuringMeasure = true;                   requestLayout();               }      }  
```

在notifyItemRangeChanged中并没有对mDisoatchItemsChangedEvent赋值操作，所以不会清除spanIndex,刷新时依然复用之前的spanIndex，不会导致顺序的变化，故没有出现顶部空白问题。

02

notifyItemRangeChanged处理流程图

看下流程图，图中虚线部分是与执行notifyDataSetChanged的区别：

![](https://mmbiz.qpic.cn/mmbiz_png/MrFJyDNenF9fDdkGJzcdwbklExa1KQAeaoNTc3y5WrVJzjpFYpXicyd7UyQCFWpnQBViaeWOMcT9mClAOG8ibibMDg/640?wx_fmt=png)

总结

notifyDataSetChanged做列表刷新时，会导致item的spanIndex重新进行计算，item所在列的位置出现了变化，从而使列表重排，导致了顶部空白，而notifyItemRangeChanged和notifyItemRangeInsert依然是使用之前的spanIndex，所以没有出现该问题。