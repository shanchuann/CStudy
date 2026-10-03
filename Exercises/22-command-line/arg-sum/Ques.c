#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

/* TODO: 严格解析一个参数：合法返回 1 并把结果写入 *out，否则返回 0。
   允许前导空白与正负号，不允许尾随非空白字符，溢出也算非法。 */
int parse_long(const char *text, long *out) {
    (void)text;
    (void)out;
    return 0;
}

int main(int argc, char *argv[]) {
    long long total = 0;

    (void)argc;
    (void)argv;
    (void)total;
    /* TODO: 遍历所有参数并用 parse_long 校验；任一非法输出 invalid，
       否则输出总和（没有参数时输出 0） */
    printf("invalid\n");
    return 0;
}

// Done
