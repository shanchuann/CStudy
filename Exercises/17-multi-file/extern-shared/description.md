# extern 共享状态

## 题目描述

counter.c 里定义全局变量 int g_calls = 0; 和函数 void record(int value)，每调用一次 record，g_calls 就加一；counter.h 用 extern 把这两个名字声明给别的源文件使用。

Ques.c 的 main 读入数据，对每个数调用 record，最后输出 g_calls 的值和所有数之和。

## 输入格式

第一行一个整数 n（0 ≤ n ≤ 100）；如果 n 大于 0，第二行是 n 个整数。

## 输出格式

输出一行：calls=<g_calls 的值> sum=<n 个整数之和>

## 示例

**示例 1**

输入：

```text
3
1 2 3
```

输出：

```text
calls=3 sum=6
```

**示例 2**

输入：

```text
0
```

输出：

```text
calls=0 sum=0
```

## 知识点

- extern 声明与定义的区别：声明不分配空间
- 全局变量在整个程序里只有一份，可以被多个源文件共享
- 跨文件访问全局变量时只在一个 .c 文件里定义并初始化

## 提示

- g_calls 的定义（带初始化）只能出现在 counter.c 里，counter.h 中写 extern int g_calls;。
- record 只负责让 g_calls 加一，求和由 main 自己完成。
