#include <stdio.h>

int main() {
    int n;
    printf("请输入菱形的高度（奇数）：");
    scanf("%d", &n);
    
    if (n % 2 == 0) {
        printf("请输入奇数！\n");
        return 0;
    }
    
    // 打印上半部分
    for (int i = 1; i <= n/2 + 1; i++) {
        // 打印空格
        for (int j = 1; j <= n/2 + 1 - i; j++) {
            printf(" ");
        }
        // 打印星号
        for (int j = 1; j <= 2*i - 1; j++) {
            if (j == 1 || j == 2*i - 1) {
                printf("*");
            } else {
                printf(" ");
            }
        }
        printf("\n");
    }
    
    // 打印下半部分
    for (int i = n/2; i >= 1; i--) {
        // 打印空格
        for (int j = 1; j <= n/2 + 1 - i; j++) {
            printf(" ");
        }
        // 打印星号
        for (int j = 1; j <= 2*i - 1; j++) {
            if (j == 1 || j == 2*i - 1) {
                printf("*");
            } else {
                printf(" ");
            }
        }
        printf("\n");
    }
    
    return 0;
} 