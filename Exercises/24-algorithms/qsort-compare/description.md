# qsort 与比较函数

## 题目描述

读入 n 个整数和一个排序方向 order，使用标准库函数 qsort 和自定义的比较函数完成排序。

比较函数的签名是 int compare(const void *left, const void *right)：先把它接收到的两个 const void * 转换成 const int * 再解引用取到整数，然后返回负数、零或正数来表示左操作数小于、等于或大于右操作数。不要直接返回 a - b，因为两个整数相减可能溢出。

order 为 1 时升序，order 为 -1 时降序。

## 输入格式

第一行两个整数 n 与 order，用空格分隔，其中 order 只会是 1 或 -1。

第二行 n 个整数，用空格分隔。

## 输出格式

输出一行，为按 order 排好序的 n 个整数，相邻两个数之间用一个空格分隔，行尾只有一个换行。

## 数据范围

1 ≤ n ≤ 100，每个整数的绝对值不超过 100000。

## 示例

**示例 1**

输入：

```text
5 1
3 1 4 1 5
```

输出：

```text
1 1 3 4 5
```

**示例 2**

输入：

```text
5 -1
3 1 4 1 5
```

输出：

```text
5 4 3 1 1
```

## 知识点

- qsort 的签名：void qsort(void *base, size_t count, size_t size, int (*compare)(const void *, const void *))
- 比较函数必须接收两个 const void * 参数
- 比较函数返回负数、零、正数分别表示小于、等于、大于
- 不要用 a - b 直接作为比较结果，整数相减可能溢出

## 提示

- 比较函数里先把 const void * 转成 const int * 再解引用。
- 降序可以复用升序的比较结果再取反。
