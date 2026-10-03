#include <stdio.h>
#include <string.h>

/* TODO: 实现 my_memmove：正确处理 src 与 dst 重叠的按字节复制 */
void *my_memmove(void *dst, const void *src, size_t count) {
    (void)src;
    (void)count;
    return dst;
}

int main(void) {
    char buffer[64] = {0};
    size_t length = 0;
    char first = 0;

    if (scanf("%63s", buffer) != 1) {
        return 0;
    }
    length = strlen(buffer);
    first = buffer[0];
    /* 把第 2 个字符到结尾的内容整体左移到开头，源与目标重叠 */
    my_memmove(buffer, buffer + 1, length - 1);
    buffer[length - 1] = first;
    printf("%s\n", buffer);
    return 0;
}

// Done
