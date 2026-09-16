# DRHL 候选元素与语义验证规则

本文档对应论文 4.3.1–4.3.3，描述当前源码分析实现的有效契约。PHP、Java/JSP、Python 和 Go 只在 CST 适配层不同；候选验证与片段生成共用 `drhl/cst_semantic_analysis.py`。

## 4.3.1 候选提取

1. 递归扫描目标源码目录，每个文件独立转换为 Tree-sitter CST：
   - PHP：`tree-sitter-php`
   - Java/JSP：`tree-sitter-java`；JSP scriptlet 先包装成保持源码块映射的 Java 解析单元
   - Python：`tree-sitter-python`
   - Go：`tree-sitter-go`
2. 只有直接出现在条件谓词中的变量、字段、下标表达式或用户定义调用表达式进入候选参数集。`isset`、`len`、`defined` 等语言或运行库谓词本身不是数据参数，但其操作数仍会保留。
3. 赋值 CST 用于建立文件内别名闭包。直接赋值、类型转换和仅含一个数据依赖的简单变换都会保留来源关系。
4. 若候选参数或别名出现在 SQL/JDBC/ORM 查询谓词中，记录其 `database_relations`，但此时尚不判定它一定具有访问控制语义。
5. 所有函数、方法和构造器定义进入候选函数集，保留名称、形式参数和完整函数体。函数名不参与语义验证。

## 4.3.2 语义验证

### 特权参数

每个候选参数严格使用以下析取规则：

```text
DBMatch(CP)  := CP 或其别名引用了配置集合 D_AC 中的数据库字段
TermMatch(CP):= CP 所在条件的直接控制分支包含 E_T 中的访问拒绝终止
P_AC         := { CP | DBMatch(CP) or TermMatch(CP) }
```

`analysis.source_analysis.access_control_database_fields` 是应用级的 `D_AC`。支持 `table.field`、`*.field` 和不带表名的 `field`。

默认 `E_T` 只包含具有明确访问拒绝语义的构造：HTTP 401/403、权限/认证拒绝异常、登录或拒绝页重定向、以及包含拒绝文本的终止或输出。普通业务返回、普通异常、成功页重定向和数据库错误退出不属于默认 `E_T`。

`analysis.source_analysis.termination_patterns` 用于补充应用自己的拒绝机制，例如 `error_no_permission()`。每个值是正则表达式，可匹配单条语句，也可匹配“条件 + 分支”的完整上下文；上下文匹配只会提升该分支中的返回、抛出、退出、重定向等控制转移语句。

终止语句采用“最近条件归属”：内层条件的拒绝不会自动使外层业务路由参数通过 `TermMatch`。

### 验证函数

候选函数只有在函数体内存在同一个条件，同时满足以下两点时才进入 `F_AC`：

1. 条件引用已经验证的 `P_AC` 或其别名；
2. 该条件的直接控制分支包含 `E_T`。

实现不使用 `auth`、`admin`、`permission` 等函数名启发式。旧配置中的 `validated_function_name_patterns` 和 `validated_function_code_patterns` 为兼容旧配置而仍可被读取，但当前四语言分析器会忽略它们。

## 4.3.3 片段生成

输出片段只包含两类：

- 已验证参数对应的条件框架，以及该条件直接控制的访问拒绝终止语句；
- 已验证函数的完整定义。

条件片段保持目标语言语法：Python 使用冒号和缩进，Go 使用无括号条件，PHP/Java 使用括号与花括号。赋值上下文和验证函数调用点不会作为独立片段加入。

## 配置与评测

应用差异应只通过 `access_control_database_fields` 和 `termination_patterns` 表达，不应写入四语言通用分析代码。字段和终止模式应结合应用数据库模式、源码与人工 ground truth 审核。

隔离评测入口是 `test_extract/evaluate.py`。它复用正式 CLI 的源码分析入口，并评测 `configs` 中全部具有 ground truth 的应用。
