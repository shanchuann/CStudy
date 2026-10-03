#include <stdio.h>

#define MAX_N 1000

/* TODO: 实现 merge 与 merge_sort，用辅助数组完成递归归并排序 */

int main(void) {
    int n = 0;
    if (scanf("%d", &n) != 1) {
        return 0;
    }
    if (n < 0) {
        n = 0;
    }
    if (n > MAX_N) {
        n = MAX_N;
    }

    static int values[MAX_N];
    for (int i = 0; i < n; i++) {
        if (scanf("%d", &values[i]) != 1) {
            n = i;
            break;
        }
    }

    /* TODO: 调用归并排序把 values[0..n-1] 升序排列 */

    for (int i = 0; i < n; i++) {
        if (i > 0) {
            printf(" ");
        }
        printf("%d", values[i]);
    }
    printf("\n");
    return 0;
}

// Done
