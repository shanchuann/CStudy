#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    const char *name = NULL;
    const char *age = NULL;

    (void)argc;
    (void)argv;
    (void)name;
    (void)age;
    /* TODO: 顺序任意地解析 -n NAME 与 -a AGE，两者都必须出现；
       缺少选项、选项后没有值、未知选项或多余参数时输出 invalid */
    printf("invalid\n");
    return 0;
}

// Done
