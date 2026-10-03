#include <stdio.h>

int main(void) {
    int n = 0;
    int values[100];
    if (scanf("%d", &n) != 1) {
        return 0;
    }
    for (int i = 0; i < n; i++) {
        if (scanf("%d", &values[i]) != 1) {
            return 0;
        }
    }
    /* TODO: 用指针遍历数组求和，再用指针相减求 span，然后输出 */
    (void)n;
    return 0;
}

// Done
