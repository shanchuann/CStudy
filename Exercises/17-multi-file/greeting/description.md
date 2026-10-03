# 多文件问候

## 题目描述

本练习演示把程序拆成多个源文件：Ques.c 负责 main 和函数声明，helper.c 负责函数实现，两个文件一起编译链接成一个程序。

helper.c 中实现

    const char *greeting(void);

它返回字符串 hello from helper；Ques.c 的 main 调用这个函数并把返回值打印出来。

## 输入格式

无输入。

## 输出格式

输出一行：hello from helper

## 示例

**示例 1**

输出：

```text
hello from helper
```

## 知识点

- 声明与定义分离：声明告诉编译器函数长什么样，定义提供函数体
- 跨文件函数调用与链接：多个 .c 一起交给编译器
- 函数声明放在使用它的源文件里，实现放在另一个源文件里

## 提示

- 在 Ques.c 中先写函数声明 const char *greeting(void);，再在 main 里调用它。
- helper.c 只负责实现 greeting，不要写 main。
