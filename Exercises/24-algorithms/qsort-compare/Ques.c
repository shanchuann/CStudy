#include <stdio.h>
#include <stdlib.h>

#define MAX_N 100

/* TODO: 实现比较函数 int compare(const void *left, const void *right) */

int main(void) {
    int n = 0;
    int order = 1;
    if (scanf("%d %d", &n, &order) != 2) {
        return 0;
    }
    if (n < 0) {
        n = 0;
    }
    if (n > MAX_N) {
        n = MAX_N;
    }

    int values[MAX_N];
    for (int i = 0; i < n; i++) {
        if (scanf("%d", &values[i]) != 1) {
            n = i;
            break;
        }
    }

    /* TODO: 用 qsort 和比较函数按 order 排序 values（order 为 1 升序，-1 降序） */
    (void)order;

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
