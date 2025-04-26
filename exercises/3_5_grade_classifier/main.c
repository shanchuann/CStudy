#include <stdio.h>
#include "../testwork/test_framework.h"

// 全局变量定义
char current_output[100];
char current_input[100];

// 成绩分类函数
void classify_grade(int score) {
    // 检查成绩是否有效
    if (score < 0 || score > 100) {
        sprintf(current_output, "无效成绩");
        return;
    }
    
    // 判断成绩等级
    if (score >= 90) {
        sprintf(current_output, "优秀");
    } else if (score >= 80) {
        sprintf(current_output, "良好");
    } else if (score >= 70) {
        sprintf(current_output, "中等");
    } else if (score >= 60) {
        sprintf(current_output, "及格");
    } else {
        sprintf(current_output, "不及格");
    }
}

// int main() {
//     int score;
    
//     // 获取用户输入
//     printf("请输入成绩：");
//     scanf("%d", &score);
    
//     // 调用成绩分类函数
//     classify_grade(score);
    
//     return 0;
// } 