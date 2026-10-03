# 标识符合法性

## 题目描述

判断一个字符串是不是合法的 C 标识符，需要同时满足三条规则：

1. 只由字母、数字和下划线组成；
2. 第一个字符不能是数字；
3. 不能是 C89 关键字。

关键字有：auto break case char const continue default do double else enum extern float for goto if int long register return short signed sizeof static struct switch typedef union unsigned void volatile while。

注意 C 语言区分大小写，`Int` 是合法标识符，`int` 不是。

## 输入格式

一行长度 1..32 的字符串，不含空白字符。

## 输出格式

合法输出 valid，否则输出 invalid。

## 示例

**示例 1**

输入：

```text
value
```

输出：

```text
valid
```

**示例 2**

输入：

```text
2fast
```

输出：

```text
invalid
```

## 知识点

- 标识符只能由字母、数字和下划线组成，且不能以数字开头
- 关键字是保留的，不能用作标识符
- C 语言区分大小写，Int 与 int 不同

## 提示

- 先逐个字符检查字符集，再检查首字符不能是数字。
- 关键字要用 strcmp 精确比较，注意大小写。
