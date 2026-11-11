---
title: '从理解 Phoenix 索引源码开始，构建全文索引'
company: DataFun
tag: 索引构建
date: 2019-06-28
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247491746&idx=1&sn=876c56ce231250f10d65a17dc0c92241&chksm=fbd752cecca0dbd8c7356f3f07728d793118563be496becde0eef86d5f0c0ec19906cb6e2bd6#rd
account: DataFunTalk
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXricQvEoSLTTPY9LltT5Kl4o3TibQticsoa92kjlvNpufKp9WBUTWFbLbqg/640?wx_fmt=jpeg)

图片来自网络

文章作者：吴少杰

编辑整理：Hoh Xil

内容来源：作者授权

出品社区：DataFun

注：欢迎转载，转载请注明出处

Phoenix 索引不支持全文检索，我们需要修改源码达到这一目的。添加全文检索的前提是我们需要了解当前索引创建、维护的机制。今天将带大家，逐步探索 Phoenix 原生索引的源码。

**第一章**

根据之前对 Phoenix 源码简略了解的经验来看，每一个 DDL/DML 等语句都会通过一个 XXXCompiler 类编译成一个 MutationPlan ，创建索引的逻辑在：

org.apache.phoenix.compile.CreateIndexCompiler

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXr9zGzrCCQojibgEVm17SBafSOCCgXiaHJsDjhA9TEiawZCJ1tGTRyUUjCA/640?wx_fmt=jpeg)

分析这段代码之后，有以下结论：

1. “create.getIndexType() == IndexType.LOCAL” 这段代码主要用来校验，可忽略，不再深入研究。
2. “for (int i = 0; i < splits.length; i++) ” 这段代码是有关 split 的逻辑，目前不用深入研究。
3. compile 函数最后返回了一个 **BaseMutationPlan**类，这是最终的可执行计划，创建索引的逻辑在这里。

BaseMutationPlan 是最终可执行的执行计划，execute 函数最终创建索引，源码如下：

```
@Overridepublic MutationState execute() throws SQLException {    return client.createIndex(create, splits);}
```

逻辑非常简单，就是调用 client 的 createIndex ，client 是根据当前连接创建的 MetaDataClient 类。createIndex 源码如下：

```
** * Create an index table by morphing the CreateIndexStatement into a CreateTableStatement and calling * MetaDataClient.createTable. In doing so, we perform the following translations: * 1) Change the type of any columns being indexed to types that support null if the column is nullable. *    For example, a BIGINT type would be coerced to a DECIMAL type, since a DECIMAL type supports null *    when it's in the row key while a BIGINT does not. * 2) Append any row key column from the data table that is not in the indexed column list. Our indexes *    rely on having a 1:1 correspondence between the index and data rows. * 3) Change the name of the columns to include the column family. For example, if you have a column *    named "B" in a column family named "A", the indexed column name will be "A:B". This makes it easy *    to translate the column references in a query to the correct column references in an index table *    regardless of whether the column reference is prefixed with the column family name or not. It also *    has the side benefit of allowing the same named column in different column families to both be *    listed as an index column. * @param statement * @param splits * @return MutationState from population of index table from data table * @throws SQLException */public MutationState createIndex(CreateIndexStatement statement, byte[][] splits) throws SQLException
```

通过这段注释我们知道，其实创建一个索引，就是通过 CreateTableStatement 来实现的，这期间有以下三个转换：

1. 把索引字段转换成支持 null 值的类型。比如会把 bigint 转换成 decimal 。
2. 把数据表的 row key 字段添加到索引字段列表。索引的数据与源表数据是1：1的关系
3. 修改索引字段名包含列簇名。索引名的格式就是：

   columnFamilyName:columnName

   比如列簇 A 里面有一个 B 字段，那么索引列的名称就是 “A:B” 。主要是为了引用方便和防止同名。

这个函数逻辑很复杂，我们先往下继续看，不过多涉及细节，先梳理其结构。不过这些忽略的代码，应该就是实现上面3点的。

我们来看 createIndex 的 return ，这里又调用了一个函数 : buildIndex 。

buildIndex 的代码也比较长，其中一个比较重要的代码逻辑如下：

```
MutationPlan mutationPlan = getMutationPlanForBuildingIndex(index, dataTableRef);
```

getMutationPlanForBuildingIndex 源码如下：

```
private MutationPlan getMutationPlanForBuildingIndex(PTable index, TableRef dataTableRef) throws SQLException {        MutationPlan mutationPlan;        if (index.getIndexType() == IndexType.LOCAL) {            PostLocalIndexDDLCompiler compiler =                    new PostLocalIndexDDLCompiler(connection, getFullTableName(dataTableRef));            mutationPlan = compiler.compile(index);        } else {            PostIndexDDLCompiler compiler = new PostIndexDDLCompiler(connection, dataTableRef);            mutationPlan = compiler.compile(index);        }        return mutationPlan;    }
```

为了简化分析流程，我们不分析 local 的索引。这段代码其实就是创建了一个 PostIndexDDLCompiler 类。

```
/** * Class that compiles plan to generate initial data values after a DDL command for * index table. */public class PostIndexDDLCompiler
```

官方注释也讲解的很清楚了，这个执行计划是为了给索引表生成初始化数据。其实创建索引分两步，第一步向系统表插入索引的元数据信息，第二步根据索引元数据生成索引数据。PostIndexDDLCompiler 就是用来生成初始化数据的。

```
StringBuilder updateStmtStr = new StringBuilder();updateStmtStr.append("UPSERT /*+ NO_INDEX */ INTO ").append(schemaName.length() == 0 ? "" : '"' + schemaName + "\".").append('"').append(tableName).append("\"(")   .append(indexColumns).append(") ");final StringBuilder selectQueryBuilder = new StringBuilder();selectQueryBuilder.append(" SELECT ").append(dataColumns).append(" FROM ").append(schemaName.length() == 0 ? "" : '"' + schemaName + "\".").append('"').append(dataTable.getTableName().getString()).append('"');this.selectQuery = selectQueryBuilder.toString();updateStmtStr.append(this.selectQuery);  
try (final PhoenixStatement statement = new PhoenixStatement(connection)) {    DelegateMutationPlan delegate = new DelegateMutationPlan(statement.compileMutation(updateStmtStr.toString())) {        @Override        public MutationState execute() throws SQLException {            connection.getMutationState().commitDDLFence(dataTable);            return super.execute();        }    };    return delegate;}
```

根据经验，我们还是只看 compile 函数，上面是 compile 函数的重点逻辑，其实就是生成了一个 upsert select 的 SQL ，然后执行。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrgqM1yfbgk7NbVUmViarjNknkO5ML7jtlLmnH5PLocMf306ztezV9o0A/640?wx_fmt=jpeg)

我们在回到 buildIndex 的主逻辑，简单来看就是执行完生成索引数据的 sql 之后，通过 alterIndex 命令修改索引的状态为 PIndexState.ACTIVE 。当然了，还有设置 Scan 的时间范围等其他逻辑，这里也先不深入研究了。

那我们就总结一下创建索引的过程，大概分两步：

1. 根据语句创建索引元数据信息，然后插入 Phoenix 系统表。
2. 根据元数据信息，生成初始化索引数据的逻辑。

如果要增加全文检索的类型，创建索引时需要哪些逻辑呢？

1. 扩展索引类型。这样“全文索引”类型就会插入到 Phoenix 系统表。
2. 将全文检索的参数保存到 Phoenix 系统表，如果 Phoenix 系统表不支持，则需要对其进行扩展。作者计划用 Solr 作为全文检索的引擎，那么 Solr 的连接信息就需要保存。
3. 增加初始化索引数据的逻辑。需要读取源表索引列的数据，将其插入到全文检索引擎中，比如 Solr 或 ElasticSearch 。

那么是不是增加全文检索的类型，到此就结束了呢？远不止。这里只是大概分析了创建索引的过程，创建之后该如何根据数据的增、删、改自动维护全文检索的数据也是难题。

另外，如何扩展当前的 DDL 语句也是问题，比如目前的创建索引的语法如下：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXr7jEeAMBaskaw37Hy4JNsIZCswzRv2qjqGicoGtTLEMbx3QKicYlK3a3w/640?wx_fmt=png)

简单来看有两种方案增加全文检索类型，第一个就是扩展 DDL 语法，使其在 local 的基础之上增加 solr ；第二个就是把索引的类型保存到 indexOptions 中。具体选择哪种方案就后面再深入研究了。

到此为止，我们就初步分析了索引创建的过程，后续会继续研究其他相关的逻辑。这里也只是抛砖引玉，如果大家有其他好的方案，欢迎留言讨论。

**第二章**

上一章我们简要分析了索引的创建流程，本章节分析全局索引写的时序和逻辑。

在引用的文章[《Phoenix重磅 | Phoenix(云HBase SQL)核心功能原理及应用场景介绍》](https://mp.weixin.qq.com/s?__biz=MzU5OTQ1MDEzMA==&mid=2247486436&idx=1&sn=e588c3909a22a49a39169992bf5c788c&scene=21#wechat_redirect)中有提到，全局索引的维护分为两类：Multable 表、Immutable 表。Mutable 表全局索引在 HBase 的 RegionServer 完成，其实就是通过 HBase 的 Coprocessor 实现，是异步的；Immutable 表是在客户端完成，也就是写数据的同时写入索引。

那我们寻找 Phoenix 索引维护的源码时，就要从 Coprocessor 入手，也就是继承并实现 Coprocessor 的类。根据包名和继承关系，我们找到了类：

org.apache.phoenix.hbase.index.Indexer

```
/** * Do all the work of managing index updates from a single coprocessor. All Puts/Delets are passed * to an {@link IndexBuilder} to determine the actual updates to make. * <p> * If the WAL is enabled, these updates are then added to the WALEdit and attempted to be written to * the WAL after the WALEdit has been saved. If any of the index updates fail, this server is * immediately terminated and we rely on WAL replay to attempt the index updates again (see * {@link #preWALRestore(ObserverContext, HRegionInfo, HLogKey, WALEdit)}). * <p> * If the WAL is disabled, the updates are attempted immediately. No consistency guarantees are made * if the WAL is disabled - some or none of the index updates may be successful. All updates in a * single batch must have the same durability level - either everything gets written to the WAL or * nothing does. Currently, we do not support mixed-durability updates within a single batch. If you * want to have different durability levels, you only need to split the updates into two different * batches. * <p> * We don't need to implement {@link #postPut(ObserverContext, Put, WALEdit, Durability)} and * {@link #postDelete(ObserverContext, Delete, WALEdit, Durability)} hooks because * Phoenix always does batch mutations. * <p> */public class Indexer extends BaseRegionObserver
```

简单分析这个类的注释，就得知 Indexer 拦截数据的写入和删除，然后将先关数据传值给 IndexBuilder 类来完成实际的索引更新；Indexer 只拦截了批量提交的数据更新操作。

```
@Overridepublic void start(CoprocessorEnvironment e) throws IOException   
@Overridepublic void stop(CoprocessorEnvironment e) throws IOException   
/** * We use an Increment to serialize the ON DUPLICATE KEY clause so that the HBase plumbing * sets up the necessary locks and mvcc to allow an atomic update. The Increment is not a * real increment, though, it's really more of a Put. We translate the Increment into a * list of mutations, at most a single Put and Delete that are the changes upon executing * the list of ON DUPLICATE KEY clauses for this row. */@Overridepublic Result preIncrementAfterRowLock(final ObserverContext<RegionCoprocessorEnvironment> e,        final Increment inc)        @Overridepublic void preBatchMutate(ObserverContext<RegionCoprocessorEnvironment> c,    MiniBatchOperationInProgress<Mutation> miniBatchOp)    @Overridepublic void postBatchMutateIndispensably(ObserverContext<RegionCoprocessorEnvironment> c,    MiniBatchOperationInProgress<Mutation> miniBatchOp, final boolean success)    @Overridepublic void postOpen(final ObserverContext<RegionCoprocessorEnvironment> c)  
@Overridepublic void preWALRestore(ObserverContext<RegionCoprocessorEnvironment> env, HRegionInfo info,    HLogKey logKey, WALEdit logEdit) throws IOException  
/** * Create a custom {@link InternalScanner} for a compaction that tracks the versions of rows that * are removed so we can clean then up from the the index table(s). * <p> * This is not yet implemented - its not clear if we should even mess around with the Index table * for these rows as those points still existed. TODO: v2 of indexing */@Overridepublic InternalScanner preCompactScannerOpen(final ObserverContext<RegionCoprocessorEnvironment> c,        final Store store, final List<? extends KeyValueScanner> scanners, final ScanType scanType,        final long earliestPutTs, final InternalScanner s) throws IOException
```

分析其实现的 Coprocessor 各个函数，排除掉不重要的函数，我们着重分析 preBatchMutate：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrnAXvTEAS4SIMVibiasKrjL8BqgiaFNLpPK5AQicOoGjHxRjzDBLdiaTVYxA/640?wx_fmt=png)

这段代码比较简单，重要的逻辑都在

preBatchMutateWithExceptions 函数中。

preBatchMutateWithExceptions 代码比较多，不再具体分析，但我们要特别关注代码中对 builder 对象的相关调用，因为这个类的类型是 IndexBuildManager ，所有索引维护的操作都由其完成。

```
/** * Manage the building of index updates from primary table updates. */public class IndexBuildManager implements Stoppableprivate final IndexBuilder delegate; 
```

这个类有一个很重要的变量：delegate 。所有索引维护的具体实现又转发给了 delegate 。

```
/** * Interface to build updates ({@link Mutation}s) to the index tables, based on the primary table * updates. * <p> * Either all the index updates will be applied to all tables or the primary table will kill itself * and will attempt to replay the index edits through the WAL replay mechanism. */public interface IndexBuilder extends Stoppable
```

根据其定义，getIndexUpdate 函数完成最终的索引维护

```
/**   * Your opportunity to update any/all index tables based on the update of the primary table row.   * Its up to your implementation to ensure that timestamps match between the primary and index   * tables.   * <p>   * The mutation is a generic mutation (not a {@link Put} or a {@link Delete}), as it actually   * corresponds to a batch update. Its important to note that {@link Put}s always go through the   * batch update code path, so a single {@link Put} will come through here and update the primary   * table as the only update in the mutation.   * <p>   * Implementers must ensure that this method is thread-safe - it could (and probably will) be   * called concurrently for different mutations, which may or may not be part of the same batch.   * @param mutation update to the primary table to be indexed.   * @param context index meta data for the mutation   * @return a Map of the mutations to make -> target index table name   * @throws IOException on failure   */  public Collection<Pair<Mutation, byte[]>> getIndexUpdate(Mutation mutation, IndexMetaData context) throws IOException;
```

我们在回到 preBatchMutateWithExceptions 这个函数，找到 getIndexUpdate 调用的地方。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrJ3xuGpE3Nax1ILW7Nzjfib3IkhbPWA3k8HKOLJw4kWPWMztNGVGU7wA/640?wx_fmt=jpeg)

“index update count” 这段英文消息，也更加证实了我们的分析，getIndexUpdate 函数维护了最终的索引数据。

delegate 最终由哪个类实现呢？

```
  private static IndexBuilder getIndexBuilder(RegionCoprocessorEnvironment e) throws IOException {    Configuration conf = e.getConfiguration();    Class<? extends IndexBuilder> builderClass =        conf.getClass(Indexer.INDEX_BUILDER_CONF_KEY, null, IndexBuilder.class);    try {      IndexBuilder builder = builderClass.newInstance();      builder.setup(e);      return builder;    } catch (InstantiationException e1) {      throw new IOException("Couldn't instantiate index builder:" + builderClass          + ", disabling indexing on table " + e.getRegion().getTableDesc().getNameAsString());    } catch (IllegalAccessException e1) {      throw new IOException("Couldn't instantiate index builder:" + builderClass          + ", disabling indexing on table " + e.getRegion().getTableDesc().getNameAsString());    }  }
```

这段代码由显示 “index.builder” 这个参数指定，我们看一下建表的参数：

|  |  |
| --- | --- |
|  | 'PHOENIX:CONTRACT\_GPS', {TABLE\_ATTRIBUTES => {coprocessor$1 => '|org.apache.phoenix.coprocessor.ScanRegionObserver|805306366|', coprocessor$2 => '|org.apache.phoenix.coprocessor.UngroupedAggregateRegionObserver|805306366|', coprocessor$3 => '|org.apache.phoenix.coprocessor.GroupedAggregateRegionObserver|805306366|', coprocessor$4 => '|org.apache.phoenix.coprocessor.ServerCachingEndpointImpl|805306366|', coprocessor$5 => '|org.apache.phoenix.hbase.index.Indexer|805306366|org.apache.hadoop.hbase.index.codec.class=org.apache.phoenix.index.PhoenixIndexCodec,index.builder=org.apache.phoenix.index.PhoenixIndexBuilder'}, {NAME => 'CF\_1', BLOOMFILTER => 'NONE', DATA\_BLOCK\_ENCODING => 'FAST\_DIFF'} |

很明显 delegate 的实际类型就是：

org.apache.phoenix.index.PhoenixIndexBuilder

其实分析到这里我们就不再深入研究，结合上一篇文章，我们简要总结一下索引创建和维护的过程：

1. 创建索引元数据，插入系统表
2. 根据索引元数据，构造当前数据的索引数据
3. 通过 Coprocessor 拦截源表的数据变更，维护索引表数据。

当然上面三个步骤是非常简化的，还要很多细节没有理清，但这并不妨碍我们实现基于 Solr 或 ElasticSearch 的全文索引。

最后贴一张引用的图，作为此次分析的结束。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXr8NnkfQSN35heCNAOc0StMyibjVNtzz6CCnKJIW9XXr2BQ9iaEoHHVF9g/640?wx_fmt=jpeg)

**第三章**

前两章我们分析了索引的创建和维护过程，后面我们会简要分析一下索引的使用，而在这之前需要先分析一下 PhoenixSQL 编译的过程。

与大部分的 SQL 引擎一样，Phoenix 也是用 ANTLR

https://www.antlr.org

实现 SQL 编译的，那我们就要简要分析一下 PhoenixSQL.g 这个文件。

```
grammar PhoenixSQL;tokens {}@parser::header {}@lexer::header {}@parser::members {}@rulecatch {}@lexer::members {}  
nextStatement returns [BindableStatement ret]......  
HINT_START: '/*+' ;....fragmentFIELDCHAR......
```

其中有几个地方需要注意：

1. tokens 。定义关键字。如果我们在 local 的基础上新增 full text 类型的索引，就需要在这里提前定义好。
2. @parser::header、@lexer::header。在生成对应的类中，自动带上这些包路径。其实就是定义最终生成的 java 文件的头
3. @parser::members、@lexer::members。其实就是扩展最终生成的parser类，简单来说就是在 java 文件中，插入一段代码
4. @rulecatch。定义语法解析异常时的规则，根据文件定义，Phoenix选择直接抛出异常。

剩余部分就是定义 DSL 语法和词法。

根据 antlr 语法，这个文件会生成：

PhoenixSQL.tokens/PhoenixSQLLexer/PhoenixSQLParser

我们需要知道这三个类在哪里被使用，才方便找到客户端提供的 SQL 在哪里编译。当然了，直接 debug 其他类 ( 比如 PhoenixStatement ) 也是可以跟踪到的。

```
<plugin>  <groupId>org.antlr</groupId>  <artifactId>antlr3-maven-plugin</artifactId>  <version>3.5.2</version>  <executions>    <execution>      <goals>        <goal>antlr</goal>      </goals>    </execution>  </executions>  <configuration>    <outputDirectory>${antlr-output.dir}/org/apache/phoenix/parse</outputDirectory>  </configuration></plugin>  
<antlr-output.dir>target/generated-sources/antlr3</antlr-output.dir>
```

根据 POM 文件的 plugin 可以得知，编译后的文件在 target

target/generated-sources/antlr3 目录。感兴趣的读者可以看一下这三个类的结构，我们就不再过多介绍。

经过全文检索，我们找到 PhoenixSQLParser 创建的地方：

org.apache.phoenix.parse.SQLParser

```
parser = new PhoenixSQLParser(cts);parser.setParseNodeFactory(factory);
```

SQLParser 构造函数中，这段代码还是比较重要的。这里设置了一个 factory 变量。下面是这个变量的类型和定义，

```
/** *  * Factory used by parser to construct object model while parsing a SQL statement *  *  * @since 0.1 */public class ParseNodeFactory
```

根据注释我们知道，它是把 SQL 语句转化为模型对象的。

```
// Parse a create index statement.create_index_node returns [CreateIndexStatement ret]    :   CREATE l=LOCAL? INDEX (IF NOT ex=EXISTS)? i=index_name ON t=from_table_name        (LPAREN ik=ik_constraint RPAREN)        (INCLUDE (LPAREN icrefs=column_names RPAREN))?        (async=ASYNC)?        (p=fam_properties)?        (SPLIT ON v=value_expression_list)?        {ret = factory.createIndex(i, factory.namedTable(null,t), ik, icrefs, v, p, ex!=null, l==null ? IndexType.getDefault() : IndexType.LOCAL, async != null, getBindCount(), new HashMap<String, UDFParseNode>(udfParseNodes)); }    ;
```

上面是 create\_index\_node的antlr 定义语句，简单来看就是解析完语法之后，调用 factory.createIndex 创建并返回一个 CreateIndexStatement 。这样我们的 create index 语句就被 ParseNodeFactory 转化成了 CreateIndexStatement 对象。

如果我们要增加全文索引，就需要修改这个定义语句的。比如在 LOCAL 的地方添加 FULL TEXT ，在 SPLIT 后面添加 Solr 或 ElasticSearch 的连接属性等参数。同时修改 factory.createIndex 方法，接收这些参数。

编译后的 create\_index\_node 函数代码还是很长的，我们只看最后的返回逻辑，可以发现，跟预期的一样。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrKnb2BWsia8qRL9nKibic5UabPpAoLoYRlQMsibvKQ8g6ibHoaesDR0or1Gw/640?wx_fmt=png)

下面是创建索引的语法树，大家可以提前熟悉一下，后面会修改这个语法。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrjUzyHTyvRHQkpCvxCmzH909M5A5Adq06Vp5Kqb9RicwWdO2A1CIg0cw/640?wx_fmt=jpeg)

SQL 解析编译的过程，相信大家已经有了简单的了解。下面就要研究 SQLParser 的初始化和创建的过程。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXr8hYfxRkibsIaXE3TibMOfibmibEBREWquOAJFWLgLcJNkJ0p7dO6HicEjEw/640?wx_fmt=png)

还是全文检索 SQLParser ，这样虽然比较笨，但还是非常直观的。细心的读者会发现，有很多地方会调用 SQLParser ，而且不同的场景会调用不同的方法。这就说明，Phoenix 在编译 SQL 时，会大概判断一下当前的 SQL 类型，DDL/DML 还是其他。

由于 SQLParser 使用的地方太多，如果一个个跟踪研究，过于繁琐。我们会转换一下思路，从源头开始，也就是编译 PreparedStatement 的地方，后面将会介绍。

**第四章**

上一章我们自底向上简要分析了 SQL 编译的过程，这一章从 Driver 分析。

用过 JDBC 进行数据库的 CRUD 的读者对：

* Driver
* Connection
* PreperedStatement/Statement
* ResultSet

一定不陌生，对应的 PhoenixSQL 中也有这些概念。我们会自顶向下逐一分析这些概念。

```
/** *  * JDBC Driver implementation of Phoenix for production. * To use this driver, specify the following URL: *     jdbc:phoenix:<zookeeper quorum server name>; * Only an embedded driver is currently supported (Phoenix client * runs in the same JVM as the driver). Connections are lightweight * and are not pooled. The last part of the URL, the hbase zookeeper * quorum server name, determines the hbase cluster to which queries * will be routed. *  *  * @since 0.1 */public final class PhoenixDriver extends PhoenixEmbeddedDriver  
/** *  * Abstract base class for JDBC Driver implementation of Phoenix *  *  * @since 0.1 */@Immutablepublic abstract class PhoenixEmbeddedDriver implements Driver, SQLCloseable
```

PhoenixDriver 就是 Driver 的一个子类，提供了相应的功能实现。不过目前只需要关注 connect 这个方法，它最终返回了一个 PhoenixConnection 。

PhoenixDriver 注释中提到了：

PhoenixConnection

非常轻量级，不需要池化，也就是说可以随便创建连接。关于这一点，不再过多介绍，感兴趣的读者可以自行谷歌。

```
/** *  * JDBC Connection implementation of Phoenix. Currently the following are * supported: - Statement - PreparedStatement The connection may only be used * with the following options: - ResultSet.TYPE_FORWARD_ONLY - * Connection.TRANSACTION_READ_COMMITTED *  *  * @since 0.1 */public class PhoenixConnection implements Connection, MetaDataMutated, SQLCloseable/** *  * Interface for applying schema mutations to our client-side schema cache * *  * @since 0.1 */public interface MetaDataMutated {    void addTable(PTable table, long resolvedTime) throws SQLException;    void updateResolvedTimestamp(PTable table, long resolvedTimestamp) throws SQLException;    void removeTable(PName tenantId, String tableName, String parentTableName, long tableTimeStamp) throws SQLException;    void removeColumn(PName tenantId, String tableName, List<PColumn> columnsToRemove, long tableTimeStamp, long tableSeqNum, long resolvedTime) throws SQLException;    void addFunction(PFunction function) throws SQLException;    void removeFunction(PName tenantId, String function, long functionTimeStamp) throws SQLException;    void addSchema(PSchema schema) throws SQLException;    void removeSchema(PSchema schema, long schemaTimeStamp);}
```

PhoenixConnection 只关注：

prepareStatement 和 createStatement

根据定义他们分表返回了：

* PhoenixPreparedStatement
* PhoenixStatement

分析到这里，还不涉及 SQL 的编译和执行，都是一些对象类型的转换和创建。为了简化分析，下面着重分析 PhoenixStatement 。

```
/** *  * JDBC Statement implementation of Phoenix. * Currently only the following methods are supported: * - {@link #executeQuery(String)} * - {@link #executeUpdate(String)} * - {@link #execute(String)} * - {@link #getResultSet()} * - {@link #getUpdateCount()} * - {@link #close()} * The Statement only supports the following options: * - ResultSet.FETCH_FORWARD * - ResultSet.TYPE_FORWARD_ONLY * - ResultSet.CLOSE_CURSORS_AT_COMMIT *  *  * @since 0.1 */public class PhoenixStatement implements Statement, SQLCloseable
```

注释讲的也很清楚，仅支持有限的方法，那么我们分析就有重点了。再加上此次分析的目的，executeQuery 方法就是我们的重中之重了。

```
@Overridepublic ResultSet executeQuery(String sql) throws SQLException {    if (logger.isDebugEnabled()) {        logger.debug(LogUtil.addCustomAnnotations("Execute query: " + sql, connection));    }        CompilableStatement stmt = parseStatement(sql);    if (stmt.getOperation().isMutation()) {        throw new ExecuteQueryNotApplicableException(sql);    }    return executeQuery(stmt,createQueryLogger(stmt,sql));}
```

executeQuery 逻辑比较简单，就是把SQL字符串编译成了 CompilableStatement ，然后交给另一个 executeQuery 执行。

```
protected CompilableStatement parseStatement(String sql) throws SQLException {        PhoenixStatementParser parser = null;        try {            parser = new PhoenixStatementParser(sql, new ExecutableNodeFactory());        } catch (IOException e) {            throw ServerUtil.parseServerException(e);        }        CompilableStatement statement = parser.parseStatement();        return statement;    }
```

parseStatement：

创建了：PhoenixStatementParser 

编译了：SQL 字符串

PhoenixStatementParser 其实是 SQLParser 的子类，其实就调用了 SQLParser 编译了 SQL 。

因为 PhoenixStatementParser 是在 executeQuery 中调用的，所以一定是一个 DML 语句。

```
/** * Parses the input as a SQL select or upsert statement. * @throws SQLException  */public BindableStatement parseStatement() throws SQLException {    try {        BindableStatement statement = parser.statement();        return statement;    } catch (RecognitionException e) {        throw PhoenixParserException.newException(e, parser.getTokenNames());    } catch (UnsupportedOperationException e) {        throw new SQLFeatureNotSupportedException(e);    } catch (RuntimeException e) {        if (e.getCause() instanceof SQLException) {            throw (SQLException) e.getCause();        }        throw PhoenixParserException.newException(e, parser.getTokenNames());    }}
```

根据其逻辑，可以知道 DML 语句由语法文件中的 statement 定义。至此，SQL 字符串就编译完成，但还没有执行。

```
private PhoenixResultSet executeQuery(final CompilableStatement stmt,        final boolean doRetryOnMetaNotFoundError, final QueryLogger queryLogger) throws SQLException
```

根据代码逻辑，我们找到了上面这个方法最终编译、执行了 CompilableStatement 。

继续分析，我们发现 CompilableStatement 被编译成了 QueryPlan ，QueryPlan 被

onnection.getQueryServices().getOptimizer().optimize

优化，根据 QueryPlan 创建了 PhoenixResultSet 。

细心的读者可能要问了，编译后的 SQL 在哪里转化成 HBase 的 Scan 呢？这就要知道 statement 是在哪里翻译的了。通过语法文件可以知道 statement 被 oneStatement 定义，oneStatement 语法图如下：

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrf49AMlicxIo3SWn8CN9xOoFcweT4qbkclLXZtqicPfibrBiaM46EEiciajkA/640?wx_fmt=jpeg)

很明显我们要去查看 select\_node 的语法树：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXryhIQrzsRlRgmy4FIs8U16FuTvpF4eVwYJ5PicdTdWQmVYgicypoU808w/640?wx_fmt=png)

从上图可得知，最终 sql 语法分析后通过 factory.select 进行了语义转换，生成了 SelectStatement 对象。

但这里需要特别注意，fatory 的具体类型。在 parseStatement 函数中，传给 PhoenixStatementParser 的第二个参数是 ExecutableNodeFactory ，这就是 factry 的具体类型，所以 select 的具体实现由 ExecutableNodeFactory 完成。下面是 select 的代码。

```
@Overridepublic ExecutableSelectStatement select(TableNode from, HintNode hint, boolean isDistinct, List<AliasedNode> select, ParseNode where,        List<ParseNode> groupBy, ParseNode having, List<OrderByNode> orderBy, LimitNode limit, OffsetNode offset, int bindCount, boolean isAggregate,        boolean hasSequence, List<SelectStatement> selects, Map<String, UDFParseNode> udfParseNodes) {    return new ExecutableSelectStatement(from, hint, isDistinct, select, where, groupBy == null ? Collections.<ParseNode>emptyList() : groupBy,            having, orderBy == null ? Collections.<OrderByNode>emptyList() : orderBy, limit, offset, bindCount, isAggregate, hasSequence, selects == null ? Collections.<SelectStatement>emptyList() : selects, udfParseNodes);}
```

也就说编译后 SelectStatement 实际的类型是 ExecutableSelectStatement 。

compilePlan 也是由 ExecutableSelectStatement 实现。

```
@SuppressWarnings("unchecked")@Overridepublic QueryPlan compilePlan(PhoenixStatement stmt, Sequence.ValueOp seqAction) throws SQLException {    if(!getUdfParseNodes().isEmpty()) {        stmt.throwIfUnallowedUserDefinedFunctions(getUdfParseNodes());    }    SelectStatement select = SubselectRewriter.flatten(this, stmt.getConnection());    ColumnResolver resolver = FromCompiler.getResolverForQuery(select, stmt.getConnection());    select = StatementNormalizer.normalize(select, resolver);    SelectStatement transformedSelect = SubqueryRewriter.transform(select, resolver, stmt.getConnection());    if (transformedSelect != select) {        resolver = FromCompiler.getResolverForQuery(transformedSelect, stmt.getConnection());        select = StatementNormalizer.normalize(transformedSelect, resolver);    }  
    QueryPlan plan = new QueryCompiler(stmt, select, resolver, Collections.<PDatum>emptyList(), stmt.getConnection().getIteratorFactory(), new SequenceManager(stmt), true, false, null).compile();    plan.getContext().getSequenceManager().validateSequences(seqAction);    return plan;}
```

这段代码非常重要，特别是其中的几个函数：

* SubselectRewriter.flatten；
* FromCompiler.getResolverForQuery；
* SubqueryRewriter.transform。

简单来说这段代码通过 connection 查询了表结构，将表、字段等信息设置到 ExecutableSelectStatement 中。

当然为了简化，也不再深入研究其中的逻辑，只关注下面三段代码：

```
QueryPlan plan = new QueryCompiler(stmt, select, resolver, Collections.<PDatum>emptyList(), stmt.getConnection().getIteratorFactory(), new SequenceManager(stmt), true, false, null).compile();plan.getContext().getSequenceManager().validateSequences(seqAction);return plan;
```

这段代码表明，最终的 plan 是 QueryCompiler ，且调用了 compile 函数。

通过分析 compile 函数，我们得知，对于简单的 select 查询，最终创建了一个 ScanPlan 。当然了，还有很多其他类型的 plan ，这里选择一个最简单的，感兴趣的读者可以根据自己的实际情况分析其他各种场景。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrkIGzGIgRPhoYJ908Qu2DRAz2FbdJvP3BIRYF2pbWHsbdUPLmRGtJng/640?wx_fmt=jpeg)

下面是 ScanPlan 的部分源码。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrTSRSQ1qjoYFiaYEqznfy3GlM484Pz6KvfO1Qz8wvw5clFXIUSgPS9Gw/640?wx_fmt=jpeg)

这里终于出现了我们最期待的 Scan 类型的对象。因为到这里，SQL 字符串就真正的变成了可实际执行的代码了。

这个类的 newIterator 函数要特别关注一下，因为最终由它返回了 ResultIterator ，其实就是对 Scan 的封装。Scan 具体是由 SerialIterators 或 ParallelIterators 生成的，细节也不再深入研究。

再回到 executeQuery 函数内部。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrKib5st9fI9gPicXznPk3hKXQxwNNu3OAvFqBsSCFQwF8R7uzSr93YAqA/640?wx_fmt=jpeg)

可以看到这里生成了具体可执行、可访问的 ResultIterator ，然后被 PhoenixResultSet 封装返回。

PhoenixResultSet 代码就比较简单了，就是调用 next、getXXX 处理返回的数据，不再深入分析。

到此为止，我们就大概了解了 SQL 编译的过程，这里只是以最简单的查询为例，其他各种场景没有具体深入，感兴趣的读者可以自行研究。虽然简单，但并不妨碍我们对整个过程的了解和窥探，对于扩展全文检索还是有一些帮助的，至少最终的 iterator 就不能翻译成 Scan 了。

**第五章**

上一章简要分析了 SQL 的编译、执行过程，Phoenix 具体是如何走索引的还不清楚，下面会做简要分析。

分析 Phoenix 如何使用索引表该从哪里入手呢？

使用过 Phoenix 索引的同学一定知道，在没有提示 ( hint ) 的情况下，Phoenix 默认是不会走索引的（除非只查询索引表包含的字段）。那么肯定要从解析 hint 来入手分析，至少这是个突破口。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrjqywd7XiaCmiavzhXZxMR99ZvznpGDoIKwrfcoS2iahdfZN9lPNB7sfibA/640?wx_fmt=jpeg)

通过上面的语法定义可以知道，hintClause 是 factory.select 的第二个参数。上一篇文章已经分析过这个 select ，此处就不再深入研究，但只需要找这里把 SQL 字符串中的 hint 编译成了 HintNode 类。

```
/** * Node representing optimizer hints in SQL */public class HintNode
```

在 HintNode 类中有一个 Hint 枚举类，其中定义了 INDEX 。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrnfQVYHVViaVqt75ZrVv9ZhhC7WVbkyE0kvPs2KEtEs7p35o1LsOpclw/640?wx_fmt=png)

关注这个枚举类，主要是为了加快源码分析的步骤。其实如果读者看过上一篇文章，就一定还记得，在编译 QueryPlan 之后，还有一个 QueryOptimizer 的逻辑，如果猜的没错，就是在哪里生成了走索引的逻辑。

还是老方法，全文检索 Hint.INDEX 的使用。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrfnNfaiabTB1iaM0cbXWoI5lo9icRnhicibNT81yU18vw9l3he5tKFt8bibvw/640?wx_fmt=png)

很明显就是在 QueryOptimizer 中处理的。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrsmrgDmHPeAbScu8n2WIGkNibhiabm4WyqqGLCc6GJVc6GhpsiahtCnXWA/640?wx_fmt=png)

QueryOptimizer.optimize 方法对 QueryPlan 进行了优化，那就要仔细分析一下了。通过阅读源码，来到了下面这个方法。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXr5XickbB9dlSX9qUdn9E1D5yEM6q7waA0InP7q5qNSuG8gkb5TL7VXsA/640?wx_fmt=jpeg)

简单起见，直接分析：

getApplicablePlansForSingleFlatQuery

这个方法中有一个很重要的代码调用：

IndexStatementRewriter.translate

```
/** * Rewrite the select statement by translating all data table column references to * references to the corresponding index column. * @param statement the select statement * @param dataResolver the column resolver * @return new select statement or the same one if nothing was rewritten. * @throws SQLException  */public static SelectStatement translate(SelectStatement statement, ColumnResolver dataResolver) throws SQLException {    return translate(statement, dataResolver, null);}
```

当然这里也只是提示这个函数的重要性，不对其逻辑做分析。因为还有一个非常重要的方法：

getHintedQueryPlan

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrJqJcjaPnNQKosmkj93Uh2V8UH8iawv6e8NbLRhtMZcdVZSic5FG2hnJw/640?wx_fmt=jpeg)

这个方法逻辑很长，但都是在解析处理 hint 字符串，个人感觉这个地方还是可以优化的，毕竟如果在语法文件里面定义好 hint 的解析规则，这里就不用那么麻烦了。下面是 hint 的语法定义，也是佐证了我们的猜想。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrksAQbJnEibBrzzC4iaIW5DADXmeRNkn2tGCQ2cxibByIviaUiaqF1C7SI7A/640?wx_fmt=jpeg)

上面代码最重要的就是调用了 addPlan 方法，这个方法还是比较复杂的。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrIzYyOPjntBkHXAcMiazx5WCtOEV4WIFvj2Hw4RpQHIBQY7BgfD5ibMyw/640?wx_fmt=jpeg)

简要分析其逻辑来看，就是根据索引和当前的 select 查询语句，重新构造了 SelectStatement 对象，调用

ParseNodeRewriter.rewrite

对其进行重写，最终调用 QueryCompiler 编译成了可执行的代码。

ParseNodeRewriter.rewrite 的第二个参数非常重要，具体的重写逻辑由其完成。如果我们新增全文检索，在重写时可能需要扩展这个类的功能。

```
/** * Used to replace parse nodes in a SelectStatement that match expressions that are present in an indexed with the * corresponding {@link ColumnParseNode} */public class IndexExpressionParseNodeRewriter extends ParseNodeRewriter
```

这个类就定义：

indexedParseNodeToColumnParseNodeMap

然后重写了 leaveCompoundNode

```
@Overrideprotected ParseNode leaveCompoundNode(CompoundParseNode node, List<ParseNode> children, CompoundNodeFactory factory) {    return indexedParseNodeToColumnParseNodeMap.containsKey(node) ? indexedParseNodeToColumnParseNodeMap.get(node)            : super.leaveCompoundNode(node, children, factory);}
```

简单来说就是重写了语法树，具体怎重写的，比较复杂，这里不再研究。

今天就先分析到这里，虽然很多地方都没有研究清楚，但并不妨碍我们了解 Phoenix 使用索引的过程，至少我们知道是通过重写了 QueryPlan 来实现的。后面我们会通过动态调试的形式，来追踪 Phoenix 究竟是如何重写 QueryPlan 的，这样我们在扩展全文索引的时候，就知道该从何处下手了。

——未完待续

**作者介绍**

吴少杰，大龄程序猿一枚，爱好大数据生态的技术和框架，对数仓架构和实时计算比较熟悉，目前主要从事大数据开发和架构的工作

**友情推荐：**

对作者感兴趣的小伙伴，可以关注作者个人公众号：

**![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjiccxfwnKPEWCWFsk7SDnXrRFwtrWNu4JVflZukltgbydIxicmnooJrHxyph9wAbGiaI2RWvkZxZtew/640?wx_fmt=png)**

******——END——******

******文章推荐：******

[万亿数据下 Hadoop 的核心竞争力](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247491163&idx=1&sn=f12d088e6f60c8d424eb17cfb8bec359&chksm=fbd4ac37cca32521d6dc69a263faede6020d61065d43f95030b697ba40827e14f8e65b9fd22d&scene=21#wechat_redirect)

[快手 Druid 精确去重的设计和实现](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247490269&idx=2&sn=902cd9ff47fbde254242d7865dcc0439&chksm=fbd4a8b1cca321a707c8f6f21a7f8055c6264e6a0ba0af1d9f5118db4a7976f1ba3c15241644&scene=21#wechat_redirect)

[基于Flink的严选实时数仓实践](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247487029&idx=1&sn=94d00c261cca0c42ca2c0f2564f32e50&chksm=fbd4bc59cca3354f0d3e313f5a770ec3c5b19a3505ea7da13ae5aa5b5a02c1bf965e9ed0dc25&scene=21#wechat_redirect)

**关于 DataFun：**

DataFun 定位于最实用的数据智能平台，主要形式为线下的深度沙龙、线上的内容整理。希望将工业界专家在各自场景下的实践经验，通过 DataFun 的平台传播和扩散，对即将或已经开始相关尝试的同学有启发和借鉴。

DataFun 的愿景是：为大数据、人工智能从业者和爱好者打造一个分享、交流、学习、成长的平台，让数据科学领域的知识和经验更好的传播和落地产生价值。

DataFun 成立至今，已经成功在全国范围内举办数十场线下技术沙龙，有超过三百位的业内专家参与分享，聚集了数万大数据、算法相关领域从业者。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhicE4hS5liayK0vWlwTanNgy003rMCMPvRlktwUjR2m8icG0MbH1ByNF7RuLdibwXKsA424lHOvaIHWw/640?wx_fmt=png)

**您的「在看」，我的动力！👇**