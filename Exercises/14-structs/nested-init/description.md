# 嵌套结构体与指定初始化

## 题目描述

结构体的成员可以是另一个结构体，这样就能把相关的信息分层组织起来。C99 还提供了指定初始化器，用 .成员名 = 值 的形式只初始化关心的成员。

结构体定义如下：

    struct Date {
        int year;
        int month;
        int day;
    };

    struct Student {
        char name[32];
        struct Date birthday;
    };

读入姓名与出生年月日，输出姓名和格式化后的日期。

## 输入格式

一行：姓名（不含空白字符，长度不超过 31）与三个整数 year month day。

## 输出格式

输出一行：name (year-month-day)

## 示例

**示例 1**

输入：

```text
Lin 2000 1 2
```

输出：

```text
Lin (2000-1-2)
```

**示例 2**

输入：

```text
A 1999 12 31
```

输出：

```text
A (1999-12-31)
```

## 知识点

- 嵌套结构体：结构体成员本身是另一个结构体类型
- C99 指定初始化器 .member = value
- 成员链式访问 s.birthday.year
- 用 snprintf 把运行时字符串复制进字符数组

## 提示

- 先用指定初始化构造 struct Date，再把它作为 birthday 成员放进 struct Student。
- 输出格式是 name (year-month-day)，括号和连字符都要照写。
