# 自定义 memset

## 题目描述

标准库的 memset 可以把一段内存的前若干个字节全部设置为同一个值。本题要求自己实现一个功能相同的函数：

```c
void *my_memset(void *dst, int value, size_t count);
```

它把 dst 指向的内存的前 count 个字节都设置为 value（只取 value 的低 8 位），并返回 dst。

主程序已经准备好一个字符数组，读入一个字符和一个计数后调用 my_memset，再把结果当作字符串输出。

## 输入格式

一行：一个可见 ASCII 字符 c 与一个整数 count，中间用空格分隔。

## 输出格式

输出一行：前 count 个字节全部为 c 的字符串。count 为 0 时输出一个空行。

## 数据范围

0 <= count <= 15。

## 示例

**示例 1**

输入：

```text
x 5
```

输出：

```text
xxxxx
```

**示例 2**

输入：

```text
- 0
```

输出：

```text

```

## 知识点

- void * 参数与按字节赋值
- size_t 计数类型与循环边界
- 内存操作函数返回目标地址的约定

## 提示

- 把 void * 转成 unsigned char * 之后逐字节赋值。
- count 为 0 时循环一次也不执行，直接输出一个换行。
