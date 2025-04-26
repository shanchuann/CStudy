#include <stdio.h>
#include <string.h>
#include "../testwork/test_framework.h"

// 声明外部函数和变量
void calculate_grade(double score);
extern char current_output[100];
extern char current_input[100];

// 测试函数
void test_calculate_grade() {
    // 直接使用测试用例的输入
    double score;
    if (sscanf(current_input, "%lf", &score) != 1) {
        printf("Error: Invalid input format\n");
        return;
    }
    
    // 调用函数
    calculate_grade(score);
}

// 运行测试函数
void run_tests(TestCase* cases, int num_cases) {
    printf("\n========================================\n");
    printf("           Grade Calculator Tests        \n");
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
        test_calculate_grade();
        
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
        "Perfect score",
        "100",
        "A,4.0"
    },
    {
        "A grade lower bound",
        "90",
        "A,4.0"
    },
    {
        "B grade upper bound",
        "89",
        "B,3.0"
    },
    {
        "B grade lower bound",
        "80",
        "B,3.0"
    },
    {
        "C grade upper bound",
        "79",
        "C,2.0"
    },
    {
        "C grade lower bound",
        "70",
        "C,2.0"
    },
    {
        "D grade upper bound",
        "69",
        "D,1.0"
    },
    {
        "D grade lower bound",
        "60",
        "D,1.0"
    },
    {
        "F grade upper bound",
        "59",
        "F,0.0"
    },
    {
        "F grade lower bound",
        "0",
        "F,0.0"
    },
    {
        "Invalid score - negative",
        "-1",
        "Invalid score"
    },
    {
        "Invalid score - above 100",
        "101",
        "Invalid score"
    }
};

int main() {
    int num_cases = sizeof(test_cases) / sizeof(TestCase);
    run_tests(test_cases, num_cases);
    return 0;
} 