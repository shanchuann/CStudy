#include <stdio.h>
#include <string.h>
#include "../../testwork/test_framework.h"

// 声明主程序中的函数
int reverse_number(int num);

// 全局变量，用于存储当前测试用例和结果
TestCase* current_test_case;
int current_test_passed;

// 测试函数
void test_reverse_number() {
    char actual[32];
    int num;
    
    // 将输入字符串转换为整数
    if (sscanf(current_test_case->input, "%d", &num) != 1) {
        strcpy(actual, "输入无效");
    } else {
        // 调用函数并获取结果
        int result = reverse_number(num);
        
        // 格式化实际输出
        if (result == -1) {
            strcpy(actual, "输入无效");
        } else {
            sprintf(actual, "%03d", result);
        }
    }
    
    // 比较结果
    current_test_passed = (strcmp(actual, current_test_case->expected) == 0);
    if (current_test_passed) {
        printf("✅ 测试通过\n");
    } else {
        printf("❌ 测试失败\n");
        printf("实际结果: %s\n", actual);
    }
}

// 测试用例
TestCase testCases[] = {
    {"123", "321", "123"},
    {"456", "654", "456"},
    {"789", "987", "789"},
    {"100", "001", "100"},
    {"999", "999", "999"},
    {"99", "输入无效", "输入无效"},
    {"1000", "输入无效", "输入无效"},
    {"-123", "输入无效", "输入无效"},
    {"abc", "输入无效", "输入无效"}
};

int main() {
    printf("开始运行测试...\n");
    printf("测试用例数量: %d\n", sizeof(testCases) / sizeof(TestCase));
    
    // 运行所有测试用例
    int passed = 0;
    int failed = 0;
    
    for (int i = 0; i < sizeof(testCases) / sizeof(TestCase); i++) {
        printf("\n测试用例 %d: %s\n", i + 1, testCases[i].description);
        printf("输入数字: %s\n", testCases[i].input);
        printf("期望结果: %s\n", testCases[i].expected);
        
        // 设置当前测试用例
        current_test_case = &testCases[i];
        
        // 运行测试
        test_reverse_number();
        
        // 统计结果
        if (current_test_passed) {
            passed++;
        } else {
            failed++;
        }
    }
    
    printf("\n=== 测试完成 ===\n");
    printf("通过: %d\n", passed);
    printf("失败: %d\n", failed);
    printf("总计: %d\n", sizeof(testCases) / sizeof(TestCase));
    
    return failed == 0 ? 0 : 1;  // 如果有测试失败，返回1
} 