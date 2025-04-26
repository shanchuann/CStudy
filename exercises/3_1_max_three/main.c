#include <stdio.h>
#include "../testwork/test_framework.h"

// 全局变量定义
char current_output[100];
char current_input[100];

// 求三个数中的最大值
void find_max_three(int a, int b, int c) {
    int max = a;
    if (b > max) {
        max = b;
    }
    if (c > max) {
        max = c;
    }
    sprintf(current_output, "%d", max);
}

// int main() {
//     int a, b, c;
//     int max;
    
//     // 获取用户输入
//     printf("请输入三个整数，用空格分隔：");
//     scanf("%d %d %d", &a, &b, &c);
    
//     // 使用嵌套if语句找出最大值
//     if (a > b) {
//         if (a > c) {
//             max = a;
//         } else {
//             max = c;
//         }
//     } else {
//         if (b > c) {
//             max = b;
//         } else {
//             max = c;
//         }
//     }
    
//     // 输出结果
//     printf("最大值是：%d\n", max);
    
//     return 0;
// } 