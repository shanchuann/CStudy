#include <stdio.h>
#include <string.h>
#include "../testwork/test_framework.h"

// 声明外部函数和变量
void find_max_three(int a, int b, int c);
extern char current_output[100];
extern char current_input[100];

// 测试函数
void test_find_max_three() {
    // 直接使用测试用例的输入
    int a, b, c;
    if (sscanf(current_input, "%d %d %d", &a, &b, &c) != 3) {
        printf("Error: Invalid input format\n");
        return;
    }
    
    // 调用函数
    find_max_three(a, b, c);
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
        test_find_max_three();
        
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
        "All positive numbers",
        "5 3 8",
        "8"
    },
    {
        "All negative numbers",
        "-5 -3 -8",
        "-3"
    },
    {
        "Mixed positive and negative",
        "-5 3 -8",
        "3"
    },
    {
        "Equal numbers",
        "5 5 5",
        "5"
    },
    {
        "Two equal numbers",
        "5 3 5",
        "5"
    },
    {
        "First number is largest",
        "10 3 8",
        "10"
    },
    {
        "Second number is largest",
        "5 10 8",
        "10"
    },
    {
        "Third number is largest",
        "5 3 10",
        "10"
    }
};

int main() {
    int num_cases = sizeof(test_cases) / sizeof(TestCase);
    run_tests(test_cases, num_cases);
    return 0;
} 