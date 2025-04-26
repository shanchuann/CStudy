#include <stdio.h>
#include <string.h>
#include "../../testwork/test_framework.h"

// 声明练习中的函数
float calculate_circumference(float r);
float calculate_area(float r);

// 测试函数
int test_circle_calculator(void) {
    // 直接使用测试用例中的输入
    float r;
    if (sscanf(current_test_input, "%f", &r) != 1) {
        printf("输入格式错误！请输入一个浮点数。\n");
        return 1;
    }
    
    // 计算周长和面积
    float circumference = calculate_circumference(r);
    float area = calculate_area(r);
    
    // 将结果转换为字符串
    char actual[100];
    snprintf(actual, sizeof(actual), "Circumference: %.2f\nArea: %.2f", circumference, area);
    
    // 打印实际输出
    printf("实际输出：\n%s\n", actual);
    
    // 比较结果
    if (!compare_output(actual, current_test_expected)) {
        printf("结果错误！\n");
        printf("预期结果:\n%s\n", current_test_expected);
        printf("实际结果:\n%s\n", actual);
        return 1;
    }
    
    printf("结果正确！\n");
    return 0;  // 返回0表示测试通过
}

// 测试用例数组
TestCase test_cases[] = {
    {
        "计算半径为5的圆的周长和面积",
        "5",
        "Circumference: 31.42\nArea: 78.54",
        test_circle_calculator
    },
    {
        "计算半径为10的圆的周长和面积",
        "10",
        "Circumference: 62.83\nArea: 314.16",
        test_circle_calculator
    },
    {
        "计算半径为2.5的圆的周长和面积",
        "2.5",
        "Circumference: 15.71\nArea: 19.63",
        test_circle_calculator
    }
};

// 测试入口函数
int main() {
    printf("=== 圆形计算器测试 ===\n");
    run_tests(test_cases, sizeof(test_cases)/sizeof(TestCase));
    return 0;
} 