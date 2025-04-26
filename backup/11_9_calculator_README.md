# 练习11.9：递归下降法实现简单计算器

## 题目描述
使用递归下降法实现一个简单的计算器，支持基本的算术运算和括号表达式。

## 要求
1. 实现词法分析器
2. 实现语法分析器
3. 实现表达式求值
4. 支持基本运算符（+, -, *, /）
5. 支持括号表达式
6. 处理错误输入

## 示例代码框架
```c
// 词法单元类型
typedef enum {
    TOKEN_NUMBER,
    TOKEN_PLUS,
    TOKEN_MINUS,
    TOKEN_MULTIPLY,
    TOKEN_DIVIDE,
    TOKEN_LPAREN,
    TOKEN_RPAREN,
    TOKEN_END
} TokenType;

// 词法单元结构
typedef struct {
    TokenType type;
    double value;
} Token;

// 语法分析函数
double expr(void);
double term(void);
double factor(void);
double number(void);

// 词法分析函数
Token get_next_token(void);
```

## 提示
1. 实现递归下降解析器
2. 处理运算符优先级
3. 实现错误恢复
4. 添加调试信息

## 扩展要求
1. 支持更多运算符（^, %等）
2. 支持函数调用
3. 支持变量定义和使用
4. 添加语法树可视化
5. 实现代码生成 