#include <stdio.h>

int main() {
    int n;
    printf("请输入n的值：");
    scanf("%d", &n);
    
    long long sum = 0;
    long long factorial = 1;
    
    for (int i = 1; i <= n; i++) {
        factorial *= i;
        sum += factorial;
    }
    
    printf("1!+2!+...+%d! = %lld\n", n, sum);
    return 0;
} 