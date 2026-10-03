#include <stdio.h>

int main(void) {
    int n;
    int k;
    int a[1000];
    scanf("%d", &n);
    scanf("%d", &k);
    for (int i = 0; i < n; i++) {
        scanf("%d", &a[i]);
    }

    /* TODO: 用三次翻转法把数组循环左移 k 位 */

    for (int i = 0; i < n; i++) {
        if (i > 0) {
            printf(" ");
        }
        printf("%d", a[i]);
    }
    printf("\n");
    return 0;
}

// Done
