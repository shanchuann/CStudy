#include <stdio.h>

int main(void) {
    int n;
    int a[100];
    scanf("%d", &n);
    for (int i = 0; i < n; i++) {
        scanf("%d", &a[i]);
    }

    /* TODO: 遍历数组求最大值，注意最大值要初始化为 a[0] */
    int best = 0;
    printf("%d\n", best);
    return 0;
}

// Done
