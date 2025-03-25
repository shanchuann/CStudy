#include <stdio.h>

// 计算阶乘
long long factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// 计算阶乘和
long long factorialSum(int n) {
    long long sum = 0;
    for (int i = 1; i <= n; i++) {
        sum += factorial(i);
    }
    return sum;
}

int main() {
    int n;
    printf("请输入n的值：");
    scanf("%d", &n);
    
    if (n < 0) {
        printf("请输入非负整数！\n");
        return 0;
    }
    
    printf("1!+2!+...+%d! = %lld\n", n, factorialSum(n));
    
    return 0;
} 