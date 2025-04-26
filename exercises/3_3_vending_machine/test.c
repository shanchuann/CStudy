#include <stdio.h>
#include <string.h>
#include "../testwork/test_framework.h"

// 声明外部函数和变量
void vending_machine(int money, int choice);
extern char current_output[100];
extern char current_input[100];

// 测试函数
void test_vending_machine() {
    // 直接使用测试用例的输入
    int money, choice;
    if (sscanf(current_input, "%d %d", &money, &choice) != 2) {
        printf("Error: Invalid input format\n");
        return;
    }
    
    // 调用函数
    vending_machine(money, choice);
}

// 运行测试函数
void run_tests(TestCase* cases, int num_cases) {
    printf("\n========================================\n");
    printf("           Vending Machine Tests         \n");
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
        test_vending_machine();
        
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
        "Buy Cola - Enough Money",
        "10 1",
        "Buy Cola Success, Change: 7"
    },
    {
        "Buy Sprite - Enough Money",
        "10 2",
        "Buy Sprite Success, Change: 7"
    },
    {
        "Buy Water - Enough Money",
        "10 3",
        "Buy Water Success, Change: 8"
    },
    {
        "Buy Juice - Enough Money",
        "10 4",
        "Buy Juice Success, Change: 6"
    },
    {
        "Buy Coffee - Enough Money",
        "10 5",
        "Buy Coffee Success, Change: 5"
    },
    {
        "Buy Cola - Not Enough Money",
        "2 1",
        "Not Enough Money"
    },
    {
        "Buy Coffee - Not Enough Money",
        "4 5",
        "Not Enough Money"
    },
    {
        "Invalid Choice",
        "10 6",
        "Invalid Choice"
    },
    {
        "Buy Cola - Exact Money",
        "3 1",
        "Buy Cola Success, Change: 0"
    },
    {
        "Large Change Test",
        "200 1",
        "Buy Cola Success, Change: 197"
    }
};

int main() {
    int num_cases = sizeof(test_cases) / sizeof(TestCase);
    run_tests(test_cases, num_cases);
    return 0;
} 