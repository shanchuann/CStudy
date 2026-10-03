# 自定义 memcmp

## 题目描述

memcmp 按字节比较两段内存，返回值只表示大小关系：小于返回负数，相等返回 0，大于返回正数。

请实现：

```c
int my_memcmp(const void *lhs, const void *rhs, size_t count);
```

要求把字节当作 unsigned char 比较，返回 -1、0 或 1。

主程序读入两个单词，取 count = min(len1, len2) + 1（这样会把结尾的 '\0' 也比进去），调用 my_memcmp 并输出比较结果。

## 输入格式

两行，每行一个不含空白的单词，长度 1..30。

## 输出格式

输出一行：-1 表示 lhs < rhs，0 表示两者相同，1 表示 lhs > rhs。

## 数据范围

单词长度 1..30。

## 示例

**示例 1**

输入：

```text
abc
abc
```

输出：

```text
0
```

**示例 2**

输入：

```text
abc
abd
```

输出：

```text
-1
```

## 知识点

- 按字节比较与返回值符号约定
- 必须用 unsigned char 比较
- 比较长度包含结尾的 '\0'

## 提示

- 遇到第一个不同的字节就按 unsigned char 的大小返回 -1 或 1。
- count 取 min(len1, len2) + 1，短串的 '\0' 会参与比较。
