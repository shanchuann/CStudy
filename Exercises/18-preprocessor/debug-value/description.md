# 条件编译切换输出

## 题目描述

用条件编译让同一份源码有两种行为：定义了宏 DEBUG 时输出 debug，否则输出 release。判题时不会定义 DEBUG，所以实际运行结果是 release。

## 输入格式

无输入。

## 输出格式

输出一行：release

## 示例

**示例 1**

输出：

```text
release
```

## 知识点

- #ifdef / #else / #endif 条件编译
- 宏是否定义决定哪一段代码参与编译
- 用条件编译隔离调试代码

## 提示

- 用 #ifdef DEBUG 判断，而不是 #if DEBUG。
- 没有定义 DEBUG 时编译 #else 分支。
