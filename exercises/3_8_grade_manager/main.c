#include <stdio.h>
#include "../testwork/test_framework.h"

// 全局变量定义
char current_output[100];
char current_input[100];

// 计算学生成绩等级和排名
void calculate_grade(double score) {
    // 检查成绩是否有效
    if (score < 0 || score > 100) {
        sprintf(current_output, "Invalid score");
        return;
    }
    
    // 确定成绩等级
    char grade;
    if (score >= 90) {
        grade = 'A';
    } else if (score >= 80) {
        grade = 'B';
    } else if (score >= 70) {
        grade = 'C';
    } else if (score >= 60) {
        grade = 'D';
    } else {
        grade = 'F';
    }
    
    // 计算绩点
    double gpa;
    if (grade == 'A') {
        gpa = 4.0;
    } else if (grade == 'B') {
        gpa = 3.0;
    } else if (grade == 'C') {
        gpa = 2.0;
    } else if (grade == 'D') {
        gpa = 1.0;
    } else {
        gpa = 0.0;
    }
    
    // 格式化输出
    sprintf(current_output, "%c,%.1f", grade, gpa);
} 