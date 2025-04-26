#include <stdio.h>

int main() {
    int year, month, day;
    int days = 0;
    int isLeapYear = 0;
    
    // 获取用户输入
    printf("请输入年 月 日（用空格分隔）：");
    scanf("%d %d %d", &year, &month, &day);
    
    // 判断是否为闰年
    if ((year % 4 == 0 && year % 100 != 0) || year % 400 == 0) {
        isLeapYear = 1;
    }
    
    // 计算天数
    switch (month) {
        case 12: days += 30;
        case 11: days += 31;
        case 10: days += 30;
        case 9: days += 31;
        case 8: days += 31;
        case 7: days += 30;
        case 6: days += 31;
        case 5: days += 30;
        case 4: days += 31;
        case 3: days += 28 + isLeapYear;
        case 2: days += 31;
        case 1: days += day;
    }
    
    // 输出结果
    printf("%d年%d月%d日是该年的第%d天\n", year, month, day, days);
    
    return 0;
} 