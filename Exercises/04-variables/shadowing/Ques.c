#include <stdio.h>

/* TODO: 在这里定义文件作用域变量 value，初值为 10 */

int global_value(void) {
    /* TODO: 返回文件作用域的 value */
    return 0;
}

int main(void) {
    int value = 20;
    int inner = 0;
    {
        /* TODO: 在内层块中定义同名变量 value，初值为 30，并赋给 inner */
    }
    printf("global=%d local=%d inner=%d\n", global_value(), value, inner);
    return 0;
}

// Done
