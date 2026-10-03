# 多文件计算器

## 题目描述

把一个小计算器拆成三个文件：

- calc.h：用头文件保护（#ifndef / #define / #endif）声明 int calc_add(int, int)、int calc_mul(int, int)、int calc_div(int, int)；
- calc.c：给出三个函数的实现，其中 calc_div 在除数为 0 时返回 0；
- Ques.c：解析输入，调用 calc.c 里的函数并输出结果。

除数为 0 的判断由 main 负责：遇到除数为 0 或无法识别的运算符时输出 error。

## 输入格式

一行：运算符（+、* 或 /）与两个整数，用空格分隔。

## 输出格式

运算符可识别且除数不为 0 时输出运算结果（一个整数）；除数为 0 或运算符未知时输出 error。

## 示例

**示例 1**

输入：

```text
+ 3 4
```

输出：

```text
7
```

**示例 2**

输入：

```text
/ 1 0
```

输出：

```text
error
```

## 知识点

- 头文件保护 #ifndef / #define / #endif
- 声明放在头文件、实现放在源文件
- 多文件编译与链接：Ques.c、calc.c 一起编译
- 调用方负责检查前置条件（除数为 0）

## 提示

- calc.h 里只写函数声明，用头文件保护包起来，不要写函数体。
- main 里先判断 b == 0 并输出 error，再决定要不要调用 calc_div。
- 三个函数的实现都放在 calc.c 里。
