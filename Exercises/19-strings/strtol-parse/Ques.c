#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <limits.h>
#include <ctype.h>
#include <string.h>

int main(void) {
    char line[64];
    if (fgets(line, (int)sizeof(line), stdin) == NULL) {
        printf("invalid\n");
        return 0;
    }
    /* TODO: 用 strtol 解析 line；检查 end 指针、尾随空白与 int 范围，
       成功输出 int=<值>，否则输出 invalid */
    printf("invalid\n");
    return 0;
}

// Done
