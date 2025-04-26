#include <stdio.h>
#include <string.h>
#include "../testwork/test_framework.h"

// 声明外部函数和变量
void process_request(int floor);
extern char current_output[100];
extern char current_input[100];

// 测试函数
void test_elevator() {
    // 直接使用测试用例的输入
    int floor;
    if (sscanf(current_input, "%d", &floor) != 1) {
        printf("Error: Invalid input format\n");
        return;
    }
    
    // 调用函数
    process_request(floor);
}

// 运行测试函数
void run_tests(TestCase* cases, int num_cases) {
    printf("\n========================================\n");
    printf("           Elevator System Tests         \n");
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
        test_elevator();
        
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
        "Move to same floor",
        "1",
        "Current floor: 1"
    },
    {
        "Move up one floor",
        "2",
        "Current floor: 2"
    },
    {
        "Move up multiple floors",
        "5",
        "Current floor: 5"
    },
    {
        "Move down one floor",
        "4",
        "Current floor: 4"
    },
    {
        "Move down multiple floors",
        "1",
        "Current floor: 1"
    },
    {
        "Invalid floor - below 1",
        "0",
        "Invalid floor"
    },
    {
        "Invalid floor - above 20",
        "21",
        "Invalid floor"
    }
};

int main() {
    int num_cases = sizeof(test_cases) / sizeof(TestCase);
    run_tests(test_cases, num_cases);
    return 0;
} 