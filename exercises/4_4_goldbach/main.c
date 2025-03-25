#include <stdio.h>

// 判断一个数是否为素数
int isPrime(int n) {
    if (n <= 1) return 0;
    for (int i = 2; i * i <= n; i++) {
        if (n % i == 0) return 0;
    }
    return 1;
}

int main() {
    int n;
    printf("请输入一个大于2的偶数：");
    scanf("%d", &n);
    
    if (n <= 2 || n % 2 != 0) {
        printf("输入无效，请输入大于2的偶数\n");
        return 0;
    }
    
    printf("%d可以表示为以下素数之和：\n", n);
    for (int i = 2; i <= n/2; i++) {
        if (isPrime(i) && isPrime(n-i)) {
            printf("%d = %d + %d\n", n, i, n-i);
        }
    }
    
    return 0;
} 