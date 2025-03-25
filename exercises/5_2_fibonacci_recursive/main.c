#include <stdio.h>

// 递归计算斐波那契数列的第n项
int fibonacci(int n) {
    // 基本情况
    if (n <= 0) return 0;
    if (n == 1) return 1;
    
    // 递归情况
    return fibonacci(n-1) + fibonacci(n-2);
}

int main() {
    int n;
    printf("请输入要计算的斐波那契数列项数：");
    scanf("%d", &n);
    
    if (n < 0) {
        printf("请输入非负整数！\n");
        return 0;
    }
    
    printf("斐波那契数列的前%d项：\n", n);
    for (int i = 0; i < n; i++) {
        printf("%d ", fibonacci(i));
    }
    printf("\n");
    
    return 0;
} 