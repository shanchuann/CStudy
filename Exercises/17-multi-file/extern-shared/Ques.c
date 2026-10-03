#include <stdio.h>
#include "counter.h"

int main(void) {
    int n = 0;
    int sum = 0;
    if (scanf("%d", &n) != 1) {
        printf("calls=0 sum=0\n");
        return 0;
    }
    for (int i = 0; i < n; i++) {
        int value = 0;
        if (scanf("%d", &value) != 1) {
            break;
        }
        /* TODO: 调用 record(value)，并把 value 累加到 sum */
        (void)value;
    }
    printf("calls=%d sum=%d\n", g_calls, sum);
    return 0;
}

// Done
