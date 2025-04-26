#include <stdio.h>
#include "../testwork/test_framework.h"

// 全局变量定义
char current_output[100];
char current_input[100];

// 三角形类型判断函数
void classify_triangle(int a, int b, int c) {
    // 检查边长是否有效
    if (a <= 0 || b <= 0 || c <= 0) {
        sprintf(current_output, "不能构成三角形");
        return;
    }
    
    // 检查是否满足三角形两边之和大于第三边的条件
    if (a + b <= c || a + c <= b || b + c <= a) {
        sprintf(current_output, "不能构成三角形");
        return;
    }
    
    // 判断三角形类型
    if (a == b && b == c) {
        sprintf(current_output, "等边三角形");
    } else if (a == b || b == c || a == c) {
        sprintf(current_output, "等腰三角形");
    } else {
        sprintf(current_output, "普通三角形");
    }
}

// int main() {
//     int a, b, c;
    
//     // 获取用户输入
//     printf("请输入三角形的三条边长：");
//     scanf("%d %d %d", &a, &b, &c);
    
//     // 调用三角形类型判断函数
//     classify_triangle(a, b, c);
    
//     return 0;
// } 