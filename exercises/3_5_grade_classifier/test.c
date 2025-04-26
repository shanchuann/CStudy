#include <stdio.h>
#include <string.h>
#include "../testwork/test_framework.h"

// 声明外部函数和变量
void classify_grade(int score);
extern char current_output[100];
extern char current_input[100];

// 测试函数
void test_classify_grade() {
    // 直接使用测试用例的输入
    int score;
    if (sscanf(current_input, "%d", &score) != 1) {
        printf("Error: Invalid input format\n");
        return;
    }
    
    // 调用函数
    classify_grade(score);
}

// 运行测试函数
void run_tests(TestCase* cases, int num_cases) {
    printf("\n========================================\n");
    printf("           Grade Classifier Tests        \n");
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
        test_classify_grade();
        
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
        "优秀 - 满分",
        "100",
        "优秀"
    },
    {
        "优秀 - 边界值",
        "90",
        "优秀"
    },
    {
        "良好 - 边界值",
        "89",
        "良好"
    },
    {
        "良好 - 中间值",
        "80",
        "良好"
    },
    {
        "中等 - 边界值",
        "79",
        "中等"
    },
    {
        "中等 - 中间值",
        "70",
        "中等"
    },
    {
        "及格 - 边界值",
        "69",
        "及格"
    },
    {
        "及格 - 中间值",
        "60",
        "及格"
    },
    {
        "不及格 - 边界值",
        "59",
        "不及格"
    },
    {
        "不及格 - 零分",
        "0",
        "不及格"
    },
    {
        "无效成绩 - 负数",
        "-1",
        "无效成绩"
    },
    {
        "无效成绩 - 超过满分",
        "101",
        "无效成绩"
    }
};

int main() {
    int num_cases = sizeof(test_cases) / sizeof(TestCase);
    run_tests(test_cases, num_cases);
    return 0;
} 