# 自定义 memcpy

## 题目描述

memcpy 按字节复制一段内存：复制多少字节完全由调用者决定，它不关心源和目标是否重叠，也不会自动补上字符串结束符。

请实现：

```c
void *my_memcpy(void *dst, const void *src, size_t count);
```

把 src 指向的 count 个字节复制到 dst 并返回 dst。

主程序读入一个单词，用 my_memcpy 把它连同结尾的 '\0' 一起复制到另一个数组，然后输出原串、副本，并比较两者是否相同。

## 输入格式

一行一个不含空白的单词，长度 1..30。

## 输出格式

输出一行：src=<原串> dst=<副本> equal=<yes|no>

两个字符串相同时 equal 为 yes，否则为 no。

## 数据范围

单词长度 1..30。

## 示例

**示例 1**

输入：

```text
cstudy
```

输出：

```text
src=cstudy dst=cstudy equal=yes
```

**示例 2**

输入：

```text
a
```

输出：

```text
src=a dst=a equal=yes
```

## 知识点

- 按字节复制与 const void * 源参数
- 复制长度包含结尾的 '\0'
- memcpy 不处理重叠区域

## 提示

- 复制长度是 strlen(src) + 1，把结尾的 '\0' 也算进去。
- 把两个 void * 都转成 unsigned char * 再逐字节复制。
