#include <stdio.h>
#include <string.h>
#include "../../testwork/test_framework.h"

// 声明练习中的函数
void convert_time(int hour, int minute, int *hour_12, int *minute_12, char *period);

// 测试函数
int test_time_conversion(void) {
    // 直接使用测试用例中的输入
    int hour, minute;
    if (sscanf(current_test_input, "%d:%d", &hour, &minute) != 2) {
        printf("输入格式错误！请输入时间（格式：HH:MM）。\n");
        return 1;
    }
    
    // 转换时间
    int hour_12, minute_12;
    char period;
    convert_time(hour, minute, &hour_12, &minute_12, &period);
    
    // 将结果转换为字符串
    char actual[100];
    snprintf(actual, sizeof(actual), "%02d:%02d %cM", hour_12, minute_12, period);
    
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
        "测试午夜时间",
        "00:00",
        "12:00 AM",
        test_time_conversion
    },
    {
        "测试上午时间",
        "09:30",
        "09:30 AM",
        test_time_conversion
    },
    {
        "测试中午时间",
        "12:00",
        "12:00 PM",
        test_time_conversion
    },
    {
        "测试下午时间",
        "15:45",
        "03:45 PM",
        test_time_conversion
    },
    {
        "测试晚上时间",
        "23:59",
        "11:59 PM",
        test_time_conversion
    }
};

// 测试入口函数
int main() {
    printf("=== 时间格式转换测试 ===\n");
    run_tests(test_cases, sizeof(test_cases)/sizeof(TestCase));
    return 0;
} 