#include <stdio.h>

// 判断一个数是否为素数
int isPrime(int n) {
    // 处理特殊情况
    if (n <= 1) return 0;
    if (n == 2) return 1;
    if (n % 2 == 0) return 0;
    
    // 只需要检查到平方根
    for (int i = 3; i * i <= n; i += 2) {
        if (n % i == 0) return 0;
    }
    return 1;
}

int main() {
    int n;
    printf("请输入一个正整数：");
    scanf("%d", &n);
    
    if (n <= 0) {
        printf("请输入正整数！\n");
        return 0;
    }
    
    if (isPrime(n)) {
        printf("%d是素数\n", n);
    } else {
        printf("%d不是素数\n", n);
    }
    
    return 0;
} 