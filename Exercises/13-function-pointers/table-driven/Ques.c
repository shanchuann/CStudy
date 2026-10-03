#include <stdio.h>
#include <string.h>

int add(int a, int b) {
    return a + b;
}

int sub(int a, int b) {
    return a - b;
}

int mul(int a, int b) {
    return a * b;
}

int divide(int a, int b) {
    return a / b;
}

int main(void) {
    char op = 0;
    int a = 0, b = 0;
    if (scanf(" %c %d %d", &op, &a, &b) != 3) {
        return 0;
    }
    /* TODO: 建立函数指针数组，按 op 找到对应函数并调用；运算符未知或除数为 0 时输出 error */
    (void)op;
    (void)a;
    (void)b;
    return 0;
}

// Done
