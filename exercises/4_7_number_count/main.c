#include <stdio.h>

int main() {
    int num;
    int positive = 0, negative = 0;
    
    printf("请输入一系列整数（输入0结束）：\n");
    
    while (1) {
        scanf("%d", &num);
        if (num == 0) {
            break;
        }
        if (num > 0) {
            positive++;
        } else {
            negative++;
        }
    }
    
    printf("正数个数：%d\n", positive);
    printf("负数个数：%d\n", negative);
    
    return 0;
} 