#include <stdio.h>
#include <stdlib.h>

// 时间结构体
typedef struct {
    int year;   // 年
    int month;  // 月
    int day;    // 日
    int hour;   // 时
    int minute; // 分
    int second; // 秒
} Time;

// 检查日期是否有效
int isValidDate(const Time* t) {
    if (t->year < 1 || t->month < 1 || t->month > 12 || t->day < 1) {
        return 0;
    }
    
    // 计算每月的天数
    int daysInMonth[] = {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    
    // 处理闰年
    if (t->year % 4 == 0 && (t->year % 100 != 0 || t->year % 400 == 0)) {
        daysInMonth[2] = 29;
    }
    
    return t->day <= daysInMonth[t->month];
}

// 检查时间是否有效
int isValidTime(const Time* t) {
    return t->hour >= 0 && t->hour < 24 &&
           t->minute >= 0 && t->minute < 60 &&
           t->second >= 0 && t->second < 60;
}

// 时间加法
Time addTime(const Time* t1, const Time* t2) {
    Time result = *t1;
    
    // 添加秒
    result.second += t2->second;
    if (result.second >= 60) {
        result.minute += result.second / 60;
        result.second %= 60;
    }
    
    // 添加分
    result.minute += t2->minute;
    if (result.minute >= 60) {
        result.hour += result.minute / 60;
        result.minute %= 60;
    }
    
    // 添加时
    result.hour += t2->hour;
    if (result.hour >= 24) {
        result.day += result.hour / 24;
        result.hour %= 24;
    }
    
    // 添加日
    result.day += t2->day;
    
    // 添加月
    result.month += t2->month;
    
    // 添加年
    result.year += t2->year;
    
    // 处理月份进位
    while (result.month > 12) {
        result.year++;
        result.month -= 12;
    }
    
    // 处理日期进位
    while (!isValidDate(&result)) {
        result.day -= 1;
        result.month++;
        if (result.month > 12) {
            result.year++;
            result.month = 1;
        }
    }
    
    return result;
}

// 时间减法
Time subtractTime(const Time* t1, const Time* t2) {
    Time result = *t1;
    
    // 减去秒
    result.second -= t2->second;
    if (result.second < 0) {
        result.minute--;
        result.second += 60;
    }
    
    // 减去分
    result.minute -= t2->minute;
    if (result.minute < 0) {
        result.hour--;
        result.minute += 60;
    }
    
    // 减去时
    result.hour -= t2->hour;
    if (result.hour < 0) {
        result.day--;
        result.hour += 24;
    }
    
    // 减去日
    result.day -= t2->day;
    
    // 减去月
    result.month -= t2->month;
    
    // 减去年
    result.year -= t2->year;
    
    // 处理月份借位
    while (result.month < 1) {
        result.year--;
        result.month += 12;
    }
    
    // 处理日期借位
    while (!isValidDate(&result)) {
        result.month--;
        if (result.month < 1) {
            result.year--;
            result.month = 12;
        }
        result.day += 30; // 使用30天作为临时值
    }
    
    return result;
}

// 打印时间
void printTime(const Time* t) {
    printf("%04d-%02d-%02d %02d:%02d:%02d\n",
           t->year, t->month, t->day,
           t->hour, t->minute, t->second);
}

// 输入时间
Time inputTime(const char* prompt) {
    Time t;
    printf("%s\n", prompt);
    printf("请输入年：");
    scanf("%d", &t.year);
    printf("请输入月：");
    scanf("%d", &t.month);
    printf("请输入日：");
    scanf("%d", &t.day);
    printf("请输入时：");
    scanf("%d", &t.hour);
    printf("请输入分：");
    scanf("%d", &t.minute);
    printf("请输入秒：");
    scanf("%d", &t.second);
    return t;
}

int main() {
    printf("时间计算程序\n");
    printf("============\n\n");
    
    // 输入第一个时间
    Time t1 = inputTime("请输入第一个时间：");
    if (!isValidDate(&t1) || !isValidTime(&t1)) {
        printf("输入的时间无效！\n");
        return 1;
    }
    
    // 输入第二个时间
    Time t2 = inputTime("请输入第二个时间：");
    if (!isValidDate(&t2) || !isValidTime(&t2)) {
        printf("输入的时间无效！\n");
        return 1;
    }
    
    printf("\n计算结果：\n");
    printf("----------------------------------------\n");
    
    // 显示输入的时间
    printf("时间1：");
    printTime(&t1);
    printf("时间2：");
    printTime(&t2);
    
    // 计算并显示加法结果
    Time sum = addTime(&t1, &t2);
    printf("\n时间1 + 时间2 = ");
    printTime(&sum);
    
    // 计算并显示减法结果
    Time diff = subtractTime(&t1, &t2);
    printf("时间1 - 时间2 = ");
    printTime(&diff);
    
    return 0;
} 