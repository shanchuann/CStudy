#include <stdio.h>
#include "../testwork/test_framework.h"

// 全局变量定义
char current_output[100];
char current_input[100];

// 计算函数
void calculate(double a, double b, char op) {
    double result;
    
    switch (op) {
        case '+':
            result = a + b;
            sprintf(current_output, "%.6f", result);
            break;
        case '-':
            result = a - b;
            sprintf(current_output, "%.6f", result);
            break;
        case '*':
            result = a * b;
            sprintf(current_output, "%.6f", result);
            break;
        case '/':
            if (b == 0) {
                sprintf(current_output, "Error: Division by zero");
                return;
            }
            result = a / b;
            sprintf(current_output, "%.6f", result);
            break;
        default:
            sprintf(current_output, "Error: Invalid operator");
            return;
    }
}