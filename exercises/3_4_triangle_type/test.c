#include <stdio.h>
#include <string.h>
#include "../testwork/test_framework.h"

// 声明外部函数和变量
void classify_triangle(int a, int b, int c);
extern char current_output[100];
extern char current_input[100];

// 测试函数
void test_classify_triangle() {
    // 直接使用测试用例的输入
    int a, b, c;
    if (sscanf(current_input, "%d %d %d", &a, &b, &c) != 3) {
        printf("Error: Invalid input format\n");
        return;
    }
    
    // 调用函数
    classify_triangle(a, b, c);
}

// 运行测试函数
void run_tests(TestCase* cases, int num_cases) {
    printf("\n========================================\n");
    printf("           Triangle Type Tests           \n");
    printf("========================================\n\n");
    
    int passed = 0;
    int failed = 0;
    
    for (int i = 0; i < num_cases; i++) {
        printf("Test Case %d/%d: %s\n", i + 1, num_cases, cases[i].description);
        printf("----------------------------------------\n");
        printf("Input:    %s\n", cases[i].input);
        printf("Expected: %s\n", cases[i].expected);
        
        // 设置当前输入
        strcpy(current_input, cases[i].input);
        
        // 运行测试函数
        test_classify_triangle();
        
        // 比较结果
        if (strcmp(current_output, cases[i].expected) == 0) {
            printf("Result:   \033[32mPASS\033[0m\n");
            passed++;
        } else {
            printf("Result:   \033[31mFAIL\033[0m\n");
            printf("Got:      %s\n", current_output);
            failed++;
        }
        printf("\n");
    }
    
    printf("========================================\n");
    printf("Test Summary:\n");
    printf("----------------------------------------\n");
    printf("Total Tests:  %d\n", num_cases);
    printf("Passed:       %d\n", passed);
    printf("Failed:       %d\n", failed);
    printf("Success Rate: %.1f%%\n", (float)passed / num_cases * 100);
    printf("========================================\n");
}

// 测试用例数组
TestCase test_cases[] = {
    {
        "等边三角形",
        "3 3 3",
        "等边三角形"
    },
    {
        "等腰三角形",
        "3 3 4",
        "等腰三角形"
    },
    {
        "普通三角形",
        "3 4 5",
        "普通三角形"
    },
    {
        "不能构成三角形 - 边长为0",
        "0 3 4",
        "不能构成三角形"
    },
    {
        "不能构成三角形 - 边长为负",
        "-1 3 4",
        "不能构成三角形"
    },
    {
        "不能构成三角形 - 两边之和等于第三边",
        "1 2 3",
        "不能构成三角形"
    },
    {
        "不能构成三角形 - 两边之和小于第三边",
        "1 2 4",
        "不能构成三角形"
    },
    {
        "等腰三角形 - 不同顺序",
        "4 3 3",
        "等腰三角形"
    },
    {
        "等腰三角形 - 不同顺序",
        "3 4 3",
        "等腰三角形"
    },
    {
        "大数测试",
        "100 100 100",
        "等边三角形"
    }
};

int main() {
    int num_cases = sizeof(test_cases) / sizeof(TestCase);
    run_tests(test_cases, num_cases);
    return 0;
} 