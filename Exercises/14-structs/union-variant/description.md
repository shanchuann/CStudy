# 联合体与枚举

## 题目描述

联合体（union）的各个成员共用同一块存储，同一时刻只有最后写入的成员有意义。常见的用法是用一个枚举作为标签，说明联合体里当前存的是哪种类型。

定义如下：

    enum Kind { K_INT, K_DOUBLE };
    union Value { int i; double d; };
    struct Tagged { enum Kind kind; union Value value; };

读入 kind 与一个值，按 kind 选择读取联合体的对应成员并输出。

## 输入格式

一行：kind（整数）与 value，之间用空白分隔。kind 为 0 时 value 是整数，kind 为 1 时 value 是实数。

## 输出格式

kind 为 0 时输出一行：int=<值>

kind 为 1 时输出一行：double=<值，保留两位小数>

其他 kind 输出一行：invalid

## 示例

**示例 1**

输入：

```text
0 42
```

输出：

```text
int=42
```

**示例 2**

输入：

```text
1 3.5
```

输出：

```text
double=3.50
```

## 知识点

- 联合体 union 的成员共享同一块存储，大小等于最大成员
- 枚举 enum 作为标签记录当前有效的成员
- 同一时刻只读取最后写入的那个成员
- switch/if 按标签分派读取方式

## 提示

- kind=0 时用 %d 读入 value.i，kind=1 时用 %lf 读入 value.d。
- kind 既不是 0 也不是 1 时直接输出 invalid，不必读后面的值。
