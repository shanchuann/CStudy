#include <stdio.h>

/* TODO: 把 value 改成 static 局部变量，让计数在多次调用之间保持 */
int next_value(void) {
    int value = 0;
    value++;
    return value;
}

int main(void) {
    int first = next_value();
    int second = next_value();
    int third = next_value();
    printf("%d %d %d\n", first, second, third);
    return 0;
}

// Done
