#include <stdio.h>

enum Kind { K_INT, K_DOUBLE };
union Value { int i; double d; };
struct Tagged { enum Kind kind; union Value value; };

int main(void) {
    int kind = -1;
    struct Tagged t;
    if (scanf("%d", &kind) != 1) {
        return 0;
    }
    t.kind = (enum Kind)kind;
    /* TODO: 按 t.kind 读取联合体对应的成员并输出；kind 不是 0/1 时输出 invalid */
    (void)t;
    return 0;
}

// Done
