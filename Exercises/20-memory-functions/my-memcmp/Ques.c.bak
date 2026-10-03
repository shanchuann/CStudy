#include <stdio.h>
#include <string.h>

/* TODO: 实现 my_memcmp：按 unsigned char 逐字节比较，返回 -1 / 0 / 1 */
int my_memcmp(const void *lhs, const void *rhs, size_t count) {
    (void)lhs;
    (void)rhs;
    (void)count;
    return 0;
}

int main(void) {
    char lhs[64] = {0};
    char rhs[64] = {0};
    size_t len1 = 0;
    size_t len2 = 0;
    size_t count = 0;

    if (scanf("%63s %63s", lhs, rhs) != 2) {
        return 0;
    }
    len1 = strlen(lhs);
    len2 = strlen(rhs);
    count = (len1 < len2 ? len1 : len2) + 1;
    printf("%d\n", my_memcmp(lhs, rhs, count));
    return 0;
}

// Done
