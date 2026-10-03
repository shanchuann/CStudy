# 枚举状态

## 题目描述

用枚举定义一组状态：enum State { NEW, RUNNING, DONE }。读入一个整数，把它当作状态值，输出对应的英文状态名。

枚举成员默认从 0 开始依次递增，所以 NEW、RUNNING、DONE 分别是 0、1、2。不在这个范围内的输入视为未知状态。

## 输入格式

一行整数，可能是 0、1、2 或其他整数。

## 输出格式

输出一行小写单词：new、running、done 或 unknown。

## 示例

**示例 1**

输入：

```text
0
```

输出：

```text
new
```

**示例 2**

输入：

```text
1
```

输出：

```text
running
```

**示例 3**

输入：

```text
7
```

输出：

```text
unknown
```

## 知识点

- 枚举的定义与默认取值：enum State { NEW, RUNNING, DONE } 的成员依次为 0、1、2
- 枚举成员是整数常量，可以直接用作 switch 的 case 标签
- default 分支处理不在枚举范围内的输入

## 提示

- 枚举成员 NEW、RUNNING、DONE 分别等于 0、1、2。
- 其他输入落到 switch 的 default 分支，输出 unknown。
