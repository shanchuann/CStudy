#ifndef TEST_FRAMEWORK_H
#define TEST_FRAMEWORK_H

#include <stdio.h>
#include <string.h>

// 全局变量声明
extern char current_output[100];
extern char current_input[100];

// 测试用例结构
typedef struct {
    char description[64];  // 测试用例描述
    char input[32];        // 输入值
    char expected[128];    // 期望输出
} TestCase;

// 声明测试函数
void test_solve_quadratic();
void run_tests(TestCase* cases, int num_cases);

#endif // TEST_FRAMEWORK_H 