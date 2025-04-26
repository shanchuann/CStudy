#include <stdio.h>
#include <string.h>
#include "../../testwork/test_framework.h"

// 声明练习中的函数
void swap(int *a, int *b);

// 测试函数
int test_swap(void) {
    // 直接使用测试用例中的输入
    int a, b;
    if (sscanf(current_test_input, "%d %d", &a, &b) != 2) {
        printf("输入格式错误！请输入两个整数，用空格分隔。\n");
        return 1;
    }
    
    // 保存原始值
    int original_a = a;
    int original_b = b;
    
    // 交换值
    swap(&a, &b);
    
    // 将结果转换为字符串
    char actual[100];
    snprintf(actual, sizeof(actual), "Before swap: %d %d\nAfter swap: %d %d", 
             original_a, original_b, a, b);
    
    // 打印实际输出
    printf("实际输出：\n%s\n", actual);
    
    // 比较结果
    if (!compare_output(actual, current_test_expected)) {
        printf("结果错误！\n");
        printf("预期结果:\n%s\n", current_test_expected);
        printf("实际结果:\n%s\n", actual);
        return 1;
    }
    
    printf("结果正确！\n");
    return 0;  // 返回0表示测试通过
}

// 测试用例数组
TestCase test_cases[] = {
    {
        "交换两个正整数",
        "5 3",
        "Before swap: 5 3\nAfter swap: 3 5",
        test_swap
    },
    {
        "交换包含负数的值",
        "-4 6",
        "Before swap: -4 6\nAfter swap: 6 -4",
        test_swap
    },
    {
        "交换两个负数",
        "-2 -3",
        "Before swap: -2 -3\nAfter swap: -3 -2",
        test_swap
    }
};

// 测试入口函数
int main() {
    printf("=== 变量交换测试 ===\n");
    run_tests(test_cases, sizeof(test_cases)/sizeof(TestCase));
    return 0;
} 