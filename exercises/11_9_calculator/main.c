#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

// 词法单元类型
typedef enum {
    TOKEN_NUMBER,
    TOKEN_PLUS,
    TOKEN_MINUS,
    TOKEN_MULTIPLY,
    TOKEN_DIVIDE,
    TOKEN_LPAREN,
    TOKEN_RPAREN,
    TOKEN_END,
    TOKEN_ERROR
} TokenType;

// 词法单元结构
typedef struct {
    TokenType type;
    double value;
} Token;

// 全局变量
const char* input;
Token current_token;

// 错误处理
void error(const char* msg) {
    printf("错误: %s\n", msg);
    exit(1);
}

// 词法分析器
void get_next_token() {
    // 跳过空白字符
    while (*input && isspace(*input)) input++;
    
    if (*input == '\0') {
        current_token.type = TOKEN_END;
        return;
    }
    
    // 识别数字
    if (isdigit(*input)) {
        char* end;
        current_token.value = strtod(input, &end);
        input = end;
        current_token.type = TOKEN_NUMBER;
        return;
    }
    
    // 识别运算符和括号
    switch (*input) {
        case '+': current_token.type = TOKEN_PLUS; break;
        case '-': current_token.type = TOKEN_MINUS; break;
        case '*': current_token.type = TOKEN_MULTIPLY; break;
        case '/': current_token.type = TOKEN_DIVIDE; break;
        case '(': current_token.type = TOKEN_LPAREN; break;
        case ')': current_token.type = TOKEN_RPAREN; break;
        default: current_token.type = TOKEN_ERROR; error("无效字符");
    }
    input++;
}

// 语法分析函数
double expr();
double term();
double factor();
double number();

// 表达式: term ('+' term | '-' term)*
double expr() {
    double result = term();
    
    while (current_token.type == TOKEN_PLUS || current_token.type == TOKEN_MINUS) {
        TokenType op = current_token.type;
        get_next_token();
        
        if (op == TOKEN_PLUS)
            result += term();
        else
            result -= term();
    }
    
    return result;
}

// 项: factor ('*' factor | '/' factor)*
double term() {
    double result = factor();
    
    while (current_token.type == TOKEN_MULTIPLY || current_token.type == TOKEN_DIVIDE) {
        TokenType op = current_token.type;
        get_next_token();
        
        if (op == TOKEN_MULTIPLY)
            result *= factor();
        else {
            double divisor = factor();
            if (divisor == 0) error("除数不能为零");
            result /= divisor;
        }
    }
    
    return result;
}

// 因子: number | '(' expr ')'
double factor() {
    if (current_token.type == TOKEN_LPAREN) {
        get_next_token();
        double result = expr();
        if (current_token.type != TOKEN_RPAREN)
            error("缺少右括号");
        get_next_token();
        return result;
    }
    return number();
}

// 数字: number
double number() {
    if (current_token.type != TOKEN_NUMBER)
        error("期望数字");
    double result = current_token.value;
    get_next_token();
    return result;
}

// 测试函数
void test_calculator(const char* expression) {
    printf("计算表达式: %s\n", expression);
    input = expression;
    get_next_token();
    double result = expr();
    printf("结果: %.2f\n\n", result);
}

int main() {
    printf("开始测试计算器...\n\n");
    
    // 测试基本运算
    test_calculator("1 + 2");
    test_calculator("3 * 4");
    test_calculator("10 - 5");
    test_calculator("15 / 3");
    
    // 测试复杂表达式
    test_calculator("1 + 2 * 3");
    test_calculator("(1 + 2) * 3");
    test_calculator("10 / (2 + 3)");
    
    // 测试嵌套括号
    test_calculator("(1 + (2 + 3)) * 4");
    
    printf("计算器测试完成！\n");
    return 0;
} 