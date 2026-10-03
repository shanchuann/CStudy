# 宏的优先级保护

## 题目描述

宏是纯粹的文本替换，参数和整体都必须用括号保护，否则调用处的运算符优先级会把结果改掉。本练习要求定义

    #define SQUARE(x) ((x) * (x))

并用它算出两个结果。

## 输入格式

一行两个整数 a 和 b，用空格分隔。

## 输出格式

输出一行：sum_square=<(a+b) 的平方> double_square=<2 乘以 a 的平方>

## 示例

**示例 1**

输入：

```text
3 4
```

输出：

```text
sum_square=49 double_square=18
```

**示例 2**

输入：

```text
-2 1
```

输出：

```text
sum_square=1 double_square=8
```

## 知识点

- 宏是文本替换，不是函数调用
- 宏参数和整体都要加括号
- 宏参数的副作用风险（重复求值）

## 提示

- sum_square 用 SQUARE(a + b) 计算，检验参数有没有括号。
- double_square 用 2 * SQUARE(a) 计算，检验整体有没有括号。
