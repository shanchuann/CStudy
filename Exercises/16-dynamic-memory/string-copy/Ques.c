#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char word[128];
    char *copy = NULL;
    if (scanf("%127s", word) != 1) {
        return 0;
    }
    /* TODO: 用 malloc 申请 strlen(word) + 1 字节，复制字符串并输出，最后 free */
    (void)copy;
    return 0;
}

// Done
