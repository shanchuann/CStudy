#include <stdio.h>
#include "../testwork/test_framework.h"

// 全局变量定义
char current_output[100];
char current_input[100];

// 判断是否为闰年
int is_leap_year(int year) {
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

// 获取月份的天数
int get_days_in_month(int year, int month) {
    if (month == 2) {
        return is_leap_year(year) ? 29 : 28;
    } else if (month == 4 || month == 6 || month == 9 || month == 11) {
        return 30;
    } else {
        return 31;
    }
}

// 计算一年中的第几天
void day_of_year(int year, int month, int day) {
    // 检查日期是否有效
    if (month < 1 || month > 12 || day < 1 || day > get_days_in_month(year, month)) {
        sprintf(current_output, "无效日期");
        return;
    }
    
    int days = 0;
    for (int m = 1; m < month; m++) {
        days += get_days_in_month(year, m);
    }
    days += day;
    sprintf(current_output, "%d", days);
    return;
}

int main() {
    // 测试框架会自动调用day_of_year函数
    return 0;
} 