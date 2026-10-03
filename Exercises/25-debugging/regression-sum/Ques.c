#include <stdio.h>

int sum_range(const int *values, int count) {
    int sum = 0;
    /* TODO: 用正确的边界条件遍历 count 个元素 */
    (void)values;
    (void)count;
    return sum;
}

int main(void) {
    int n = 0;
    int values[100];
    scanf("%d", &n);
    /* TODO: 读入 n 个整数 */
    (void)values;
    printf("sum=%d\n", sum_range(values, n));
    return 0;
}

// Done
