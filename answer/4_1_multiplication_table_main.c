#include <stdio.h>

int main() {
    // 打印乘法口诀表
    for (int i = 1; i <= 9; i++) {
        for (int j = 1; j <= i; j++) {
            printf("%d×%d=%-3d", j, i, i * j);
        }
        printf("\n");
    }
    return 0;
} 