#include <stdio.h>

/* TODO: 实现升序比较：a 应排在 b 前面时返回负数 */
int ascending(int a, int b) {
    (void)a;
    (void)b;
    return 0;
}

/* TODO: 实现降序比较 */
int descending(int a, int b) {
    (void)a;
    (void)b;
    return 0;
}

/* TODO: 实现冒泡排序，用 cmp 判断相邻元素是否要交换 */
void sort(int *values, int n, int (*cmp)(int, int)) {
    (void)values;
    (void)n;
    (void)cmp;
}

int main(void) {
    int n = 0, order = 0;
    int values[100];
    if (scanf("%d %d", &n, &order) != 2) {
        return 0;
    }
    for (int i = 0; i < n; i++) {
        if (scanf("%d", &values[i]) != 1) {
            return 0;
        }
    }
    /* TODO: 根据 order 选择比较函数并调用 sort，然后输出数组 */
    (void)order;
    return 0;
}

// Done
