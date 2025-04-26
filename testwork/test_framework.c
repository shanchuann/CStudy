#include "test_framework.h"

// 全局变量定义
const char* current_test_input = NULL;
const char* current_test_expected = NULL;

// 获取用户输入
char* get_user_input(void) {
    char* input = (char*)malloc(1024);  // 分配足够大的缓冲区
    if (input == NULL) {
        printf("内存分配失败！\n");
        return NULL;
    }
    
    printf("请输入数据: ");
    if (fgets(input, 1024, stdin) == NULL) {
        printf("读取输入失败！\n");
        free(input);
        return NULL;
    }
    
    // 移除末尾的换行符
    size_t len = strlen(input);
    if (len > 0 && input[len-1] == '\n') {
        input[len-1] = '\0';
    }
    
    return input;
}

// 比较输出结果
int compare_output(const char* actual, const char* expected) {
    if (actual == NULL || expected == NULL) {
        return 0;
    }
    return strcmp(actual, expected) == 0;
}

// 运行单个测试用例
void run_single_test(TestCase* test_case, TestResult* result) {
    printf("\n测试用例：%s\n", test_case->description);
    printf("输入数据：%s\n", test_case->input);
    printf("期望输出：%s\n", test_case->expected);
    
    // 设置当前测试用例的输入和期望输出
    current_test_input = test_case->input;
    current_test_expected = test_case->expected;
    
    // 运行测试函数
    int test_result = test_case->test_func();
    if (test_result == 0) {  // 测试函数返回0表示通过
        printf("✅ 测试通过！\n");
        result->passed++;
    } else {
        printf("❌ 测试失败！\n");
        result->failed++;
    }
    
    result->total++;
}

// 运行所有测试用例
void run_tests(TestCase* test_cases, int num_tests) {
    TestResult result = {0, 0, 0};
    
    printf("\n=== 开始测试 ===\n");
    
    for (int i = 0; i < num_tests; i++) {
        run_single_test(&test_cases[i], &result);
    }
    
    printf("\n=== 测试结果 ===\n");
    printf("总测试数：%d\n", result.total);
    printf("通过数量：%d\n", result.passed);
    printf("失败数量：%d\n", result.failed);
    printf("通过率：%.1f%%\n", (float)result.passed / result.total * 100);
    
    if (result.failed == 0) {
        printf("\n🎉 所有测试通过！\n");
    } else {
        printf("\n�� 继续努力！\n");
    }
} 