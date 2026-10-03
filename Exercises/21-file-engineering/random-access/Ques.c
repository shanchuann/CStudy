#include <stdint.h>
#include <stdio.h>

int main(void) {
    int n = 0;
    int k = 0;
    int temp = 0;
    int32_t values[100] = {0};
    int32_t found = 0;
    long size = 0;
    FILE *fp = NULL;

    if (scanf("%d", &n) != 1 || n < 1 || n > 100) {
        return 0;
    }
    for (int i = 0; i < n; i++) {
        if (scanf("%d", &temp) != 1) {
            return 0;
        }
        values[i] = (int32_t)temp;
    }
    if (scanf("%d", &k) != 1 || k < 0 || k >= n) {
        return 0;
    }

    (void)fp;
    (void)values;
    /* TODO: 用 "wb" 把 values 的 n 条记录写入 data.bin 并关闭 */
    /* TODO: 用 "rb" 重新打开，用 fseek 定位到第 k 条记录并读入 found */
    /* TODO: 用 fseek 到 SEEK_END 加 ftell 求出文件总字节数 size */

    printf("value=%d size=%d\n", (int)found, (int)size);
    return 0;
}

// Done
