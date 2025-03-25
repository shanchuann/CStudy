#include <stdio.h>

int main() {
    printf("1000以内的完数有：\n");
    
    for (int num = 1; num <= 1000; num++) {
        int sum = 0;
        // 找出num的所有真因子并求和
        for (int i = 1; i < num; i++) {
            if (num % i == 0) {
                sum += i;
            }
        }
        // 如果和等于原数，则为完数
        if (sum == num) {
            printf("%d = ", num);
            // 输出完数的因子
            for (int i = 1; i < num; i++) {
                if (num % i == 0) {
                    printf("%d", i);
                    if (i < num/2) {
                        printf(" + ");
                    }
                }
            }
            printf("\n");
        }
    }
    
    return 0;
} 