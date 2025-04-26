#include <stdio.h>
#include <string.h>
#include "../testwork/test_framework.h"

// 声明外部函数和变量
void calculate(double a, double b, char op);
extern char current_output[100];
extern char current_input[100];

// 测试函数
void test_calculator() {
    // 直接使用测试用例的输入
    double a, b;
    char op;
    if (sscanf(current_input, "%lf %c %lf", &a, &op, &b) != 3) {
        printf("Error: Invalid input format\n");
        return;
    }
    
    // 调用函数
    calculate(a, b, op);
}

// 运行测试函数
void run_tests(TestCase* cases, int num_cases) {
    printf("=== Starting Tests ===\n");
    int passed = 0;
    int failed = 0;
    
    for (int i = 0; i < num_cases; i++) {
        printf("\n[%d/%d] %s\n", i + 1, num_cases, cases[i].description);
        printf("Input: %s\n", cases[i].input);
        printf("Expected: %s\n", cases[i].expected);
        
        // 设置当前输入
        strcpy(current_input, cases[i].input);
        
        // 运行测试函数
        test_calculator();
        
        // 比较结果
        if (strcmp(current_output, cases[i].expected) == 0) {
            printf("Result: PASS\n");
            passed++;
        } else {
            printf("Result: FAIL\n");
            printf("Got: %s\n", current_output);
            failed++;
        }
    }
    
    printf("\n=== Summary ===\n");
    printf("Total: %d  Passed: %d  Failed: %d\n", num_cases, passed, failed);
}

// 测试用例数组
TestCase test_cases[] = {
    {
        "Addition",
        "5 + 3",
        "8.000000"
    },
    {
        "Subtraction",
        "10 - 4",
        "6.000000"
    },
    {
        "Multiplication",
        "6 * 7",
        "42.000000"
    },
    {
        "Division",
        "15 / 3",
        "5.000000"
    },
    {
        "Division by zero",
        "10 / 0",
        "Error: Division by zero"
    },
    {
        "Invalid operator",
        "5 % 3",
        "Error: Invalid operator"
    },
    {
        "Negative numbers",
        "-5 + -3",
        "-8.000000"
    },
    {
        "Decimal numbers",
        "3.5 * 2",
        "7.000000"
    }
};

int main() {
    int num_cases = sizeof(test_cases) / sizeof(TestCase);
    run_tests(test_cases, num_cases);
    return 0;
} 