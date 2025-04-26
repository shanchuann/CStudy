#include <stdio.h>
#include <string.h>
#include "../testwork/test_framework.h"

// 声明外部函数和变量
void classify_bmi(double weight, double height);
extern char current_output[100];
extern char current_input[100];

// 测试函数
void test_classify_bmi() {
    // 直接使用测试用例的输入
    double weight, height;
    if (sscanf(current_input, "%lf %lf", &weight, &height) != 2) {
        printf("Error: Invalid input format\n");
        return;
    }
    
    // 调用函数
    classify_bmi(weight, height);
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
        test_classify_bmi();
        
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
        "Underweight",
        "50 1.75",
        "Underweight"
    },
    {
        "Normal weight",
        "70 1.75",
        "Normal weight"
    },
    {
        "Overweight",
        "80 1.75",
        "Overweight"
    },
    {
        "Obese",
        "100 1.75",
        "Obese"
    },
    {
        "Borderline underweight",
        "55 1.75",
        "Underweight"
    },
    {
        "Borderline normal",
        "75 1.75",
        "Normal weight"
    },
    {
        "Borderline overweight",
        "85 1.75",
        "Overweight"
    },
    {
        "Extreme obesity",
        "150 1.75",
        "Obese"
    }
};

int main() {
    int num_cases = sizeof(test_cases) / sizeof(TestCase);
    run_tests(test_cases, num_cases);
    return 0;
} 