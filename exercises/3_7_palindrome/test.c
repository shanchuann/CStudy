#include <stdio.h>
#include <string.h>
#include "../testwork/test_framework.h"

// 声明外部函数和变量
void is_palindrome(int num);
extern char current_output[100];
extern char current_input[100];

// 测试函数
void test_is_palindrome() {
    // 直接使用测试用例的输入
    int num;
    if (sscanf(current_input, "%d", &num) != 1) {
        printf("Error: Invalid input format\n");
        return;
    }
    
    // 调用函数
    is_palindrome(num);
}

// 运行测试函数
void run_tests(TestCase* cases, int num_cases) {
    printf("\n========================================\n");
    printf("           Palindrome Tests              \n");
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
        test_is_palindrome();
        
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
        "Single digit",
        "1",
        "Yes"
    },
    {
        "Two digits palindrome",
        "11",
        "Yes"
    },
    {
        "Two digits non-palindrome",
        "12",
        "No"
    },
    {
        "Three digits palindrome",
        "121",
        "Yes"
    },
    {
        "Three digits non-palindrome",
        "123",
        "No"
    },
    {
        "Four digits palindrome",
        "1221",
        "Yes"
    },
    {
        "Four digits non-palindrome",
        "1234",
        "No"
    },
    {
        "Five digits palindrome",
        "12321",
        "Yes"
    },
    {
        "Five digits non-palindrome",
        "12345",
        "No"
    },
    {
        "Zero",
        "0",
        "Yes"
    },
    {
        "Negative number",
        "-121",
        "No"
    },
    {
        "Large palindrome",
        "123454321",
        "Yes"
    }
};

int main() {
    int num_cases = sizeof(test_cases) / sizeof(TestCase);
    run_tests(test_cases, num_cases);
    // 如果有任何测试失败，返回非零值
    for (int i = 0; i < num_cases; i++) {
        strcpy(current_input, test_cases[i].input);
        test_is_palindrome();
        if (strcmp(current_output, test_cases[i].expected) != 0) {
            return 1;
        }
    }
    return 0;
} 