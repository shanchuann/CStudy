#ifndef TEST_FRAMEWORK_H
#define TEST_FRAMEWORK_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 测试用例结构
typedef struct {
    const char* description;  // 测试用例描述
    const char* input;        // 输入数据
    const char* expected;     // 期望输出
    int (*test_func)(void);   // 测试函数
} TestCase;

// 测试结果结构
typedef struct {
    int total;      // 总测试数
    int passed;     // 通过的测试数
    int failed;     // 失败的测试数
} TestResult;

// 全局变量
extern const char* current_test_input;     // 当前测试用例的输入
extern const char* current_test_expected;  // 当前测试用例的期望输出

// 函数声明
char* get_user_input(void);
int compare_output(const char* actual, const char* expected);
void run_single_test(TestCase* test_case, TestResult* result);
void run_tests(TestCase* test_cases, int num_tests);

#endif // TEST_FRAMEWORK_H 