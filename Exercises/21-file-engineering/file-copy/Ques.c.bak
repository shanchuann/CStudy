#include <stdio.h>
#include <string.h>

int main(void) {
    char line[256] = {0};
    size_t length = 0;
    FILE *fp = NULL;

    if (fgets(line, (int)sizeof line, stdin) == NULL) {
        line[0] = '\0';
    }
    length = strlen(line);
    while (length > 0 && (line[length - 1] == '\n' || line[length - 1] == '\r')) {
        line[--length] = '\0';
    }

    (void)fp;
    /* TODO: 用 "wb" 打开 src.bin，把 line 的前 length 个字节写进去并关闭 */
    /* TODO: 用 "rb" 读出 src.bin 的全部字节，再用 "wb" 写入 dst.bin */
    /* TODO: 逐字节比较 src.bin 与 dst.bin，得到 equal */

    printf("bytes=%d equal=%s\n", (int)length, "no");
    return 0;
}

// Done
