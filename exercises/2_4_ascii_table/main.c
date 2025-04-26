#include <stdio.h>

int main() {
    // 在这里编写代码
    // 提示：使用for循环遍历ASCII码值
    int col = 0;
    for (int i = 33; i < 127; i++) {
        printf("%c:%d", i, i);
        col++;
        if (col == 4) {
            printf("\n");
            col = 0;
        } else {
            printf(" ");
        }
    }
    printf("\n");
    return 0;
} 