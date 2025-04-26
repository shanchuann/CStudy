#include <stdio.h>
#include <string.h>
#include "../testwork/test_framework.h"

// 声明外部函数和变量
void solve_quadratic(double a, double b, double c);
extern char current_output[100];
extern char current_input[100];

// 测试函数
void test_solve_quadratic() {
    // 直接使用测试用例的输入
    double a, b, c;
    if (sscanf(current_input, "%lf %lf %lf", &a, &b, &c) != 3) {
        printf("Error: Invalid input format\n");
        return;
    }
    
    // 调用函数
    solve_quadratic(a, b, c);
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
        test_solve_quadratic();
        
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
        "Two different real roots",
        "1 -5 6",
        "x1 = 3.000000, x2 = 2.000000"
    },
    {
        "Two equal real roots",
        "1 -4 4",
        "x1 = 2.000000, x2 = 2.000000"
    },
    {
        "No real roots",
        "1 2 5",
        "No real roots"
    },
    {
        "Not a quadratic equation (a=0)",
        "0 2 3",
        "Not a quadratic equation"
    },
    {
        "Negative coefficients",
        "-1 -5 -6",
        "x1 = -2.000000, x2 = -3.000000"
    }
};

int main() {
    int num_cases = sizeof(test_cases) / sizeof(TestCase);
    run_tests(test_cases, num_cases);
    return 0;
} 