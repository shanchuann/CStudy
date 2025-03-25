#include <stdio.h>

// 将整数转换为二进制形式并打印
void printBinary(int n) {
    // 处理负数
    if (n < 0) {
        printf("-");
        n = -n;
    }
    
    // 特殊情况处理
    if (n == 0) {
        printf("0");
        return;
    }
    
    // 递归打印二进制
    if (n > 0) {
        printBinary(n / 2);
        printf("%d", n % 2);
    }
}

int main() {
    int n;
    printf("请输入一个整数：");
    scanf("%d", &n);
    
    printf("%d的二进制形式是：", n);
    printBinary(n);
    printf("\n");
    
    return 0;
} 