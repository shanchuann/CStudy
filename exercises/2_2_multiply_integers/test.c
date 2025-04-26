#include <stdio.h>
#include <string.h>
#include "../../testwork/test_framework.h"

// 声明练习中的函数
int multiply(int a, int b);

// 测试函数
int test_multiply(void) {
    // 直接使用测试用例中的输入
    int a, b;
    if (sscanf(current_test_input, "%d %d", &a, &b) != 2) {
        printf("输入格式错误！请输入两个整数，用空格分隔。\n");
        return 1;
    }
    
    // 调用乘法函数
    int result = multiply(a, b);
    
    // 将结果转换为字符串
    char actual[20];
    snprintf(actual, sizeof(actual), "%d", result);
    
    // 打印实际输出
    printf("实际输出：%s\n", actual);
    
    // 比较结果
    if (!compare_output(actual, current_test_expected)) {
        printf("结果错误！\n");
        printf("预期结果: %s\n", current_test_expected);
        printf("实际结果: %s\n", actual);
        return 1;
    }
    
    printf("结果正确！\n");
    return 0;  // 返回0表示测试通过
}

// 测试用例数组
TestCase test_cases[] = {
    {
        "计算两个正整数的乘积",
        "5 3",
        "15",
        test_multiply
    },
    {
        "计算包含负数的乘积",
        "-4 6",
        "-24",
        test_multiply
    },
    {
        "计算两个负数的乘积",
        "-2 -3",
        "6",
        test_multiply
    }
};

// 测试入口函数
int main() {
    printf("=== 整数乘法计算器测试 ===\n");
    run_tests(test_cases, sizeof(test_cases)/sizeof(TestCase));
    return 0;
} 