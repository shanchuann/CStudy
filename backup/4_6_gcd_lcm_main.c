#include <stdio.h>

// 计算最大公约数
int gcd(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

// 计算最小公倍数
int lcm(int a, int b) {
    return (a * b) / gcd(a, b);
}

int main() {
    int a, b;
    printf("请输入两个正整数：");
    scanf("%d %d", &a, &b);
    
    if (a <= 0 || b <= 0) {
        printf("请输入正整数！\n");
        return 0;
    }
    
    printf("最大公约数：%d\n", gcd(a, b));
    printf("最小公倍数：%d\n", lcm(a, b));
    
    return 0;
} 