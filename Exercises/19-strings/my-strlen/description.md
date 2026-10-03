# 自定义 strlen 与 sizeof

## 题目描述

自己实现 size_t my_strlen(const char *text)：从头遍历，遇到 '\0' 就停下，返回经过的字符个数。再对比 sizeof(buf)，理解“字符串长度”和“数组占用的字节数”不是一回事。

## 输入格式

一行一个不含空白的单词，长度 1..100。

## 输出格式

输出一行：len=<my_strlen 的结果> size=<sizeof(buf)>

## 示例

**示例 1**

输入：

```text
hello
```

输出：

```text
len=5 size=101
```

**示例 2**

输入：

```text
a
```

输出：

```text
len=1 size=101
```

## 知识点

- strlen 遍历到 '\0' 为止，不含结尾的 '\0'
- sizeof 数组得到的是数组占用的总字节数
- sizeof 在编译期求值，strlen 在运行期求值

## 提示

- len 与 size 都先转换成 int，再用 %d 输出，避免 %zu。
- buf 要能装下 100 个字符再加一个结尾的 '\0'。
