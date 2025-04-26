#include <stdio.h>

int main() {
    int num, original, reversed = 0;
    
    // 获取用户输入
    printf("请输入一个正整数：");
    scanf("%d", &num);
    
    // 保存原始数字
    original = num;
    
    // 反转数字
    while (num > 0) {
        reversed = reversed * 10 + num % 10;
        num /= 10;
    }
    
    // 判断是否为回文数
    if (original == reversed) {
        printf("%d是回文数\n", original);
    } else {
        printf("%d不是回文数\n", original);
    }
    
    return 0;
} 