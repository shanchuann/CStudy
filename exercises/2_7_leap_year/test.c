#include <stdio.h>
#include <string.h>
#include "../../testwork/test_framework.h"

// 声明练习中的函数
int is_leap_year(int year);

// 测试函数
int test_leap_year(void) {
    // 直接使用测试用例中的输入
    int year;
    if (sscanf(current_test_input, "%d", &year) != 1) {
        printf("输入格式错误！请输入一个整数。\n");
        return 1;
    }
    
    // 判断是否为闰年
    int result = is_leap_year(year);
    
    // 将结果转换为字符串
    char actual[100];
    if (result) {
        snprintf(actual, sizeof(actual), "%d is a leap year", year);
    } else {
        snprintf(actual, sizeof(actual), "%d is not a leap year", year);
    }
    
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
        "测试普通闰年",
        "2020",
        "2020 is a leap year",
        test_leap_year
    },
    {
        "测试世纪闰年",
        "2000",
        "2000 is a leap year",
        test_leap_year
    },
    {
        "测试非闰年",
        "2021",
        "2021 is not a leap year",
        test_leap_year
    },
    {
        "测试能被100整除但不是400整除的年份",
        "2100",
        "2100 is not a leap year",
        test_leap_year
    }
};

// 测试入口函数
int main() {
    printf("=== 闰年判断测试 ===\n");
    run_tests(test_cases, sizeof(test_cases)/sizeof(TestCase));
    return 0;
} 