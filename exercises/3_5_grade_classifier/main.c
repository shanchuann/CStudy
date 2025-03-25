#include <stdio.h>

int main() {
    int score;
    char grade;
    
    // 获取用户输入
    printf("请输入分数（0-100）：");
    scanf("%d", &score);
    
    // 判断分数是否有效
    if (score < 0 || score > 100) {
        printf("输入分数无效\n");
        return 0;
    }
    
    // 根据分数判断等级
    if (score >= 90) {
        grade = 'A';
    } else if (score >= 80) {
        grade = 'B';
    } else if (score >= 70) {
        grade = 'C';
    } else if (score >= 60) {
        grade = 'D';
    } else {
        grade = 'E';
    }
    
    // 输出结果
    printf("您的分数是%d分，等级为：%c\n", score, grade);
    
    return 0;
} 