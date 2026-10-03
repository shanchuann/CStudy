# _Generic 泛型接口

## 题目描述

C11 的 _Generic 根据控制表达式的类型挑选一个结果表达式，常用来写类型安全的“泛型”宏。请定义

    #define type_name(x) _Generic((x), int: "int", double: "double", char *: "string", default: "other")

然后分别对一个 int 变量、一个 double 变量和一个 char * 变量调用它。

## 输入格式

无输入。

## 输出格式

输出一行三个词，用空格分隔：int double string

## 示例

**示例 1**

输出：

```text
int double string
```

## 知识点

- _Generic 按表达式的类型选择结果表达式
- C11 泛型接口的写法
- char * 与字符串字面量的类型区别

## 提示

- _Generic 的控制表达式不会被求值，编译器只看它的类型。
- 三个分支分别是 int、double 和 char *。
