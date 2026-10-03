#include <stdio.h>
#include <string.h>

/* TODO: 实现 my_memcpy：把 src 的前 count 个字节复制到 dst，并返回 dst */
void *my_memcpy(void *dst, const void *src, size_t count) {
    (void)src;
    (void)count;
    return dst;
}

int main(void) {
    char src[64] = {0};
    char dst[64] = {0};

    if (scanf("%63s", src) != 1) {
        return 0;
    }
    /* 复制整个字符串，长度要包含结尾的 '\0' */
    my_memcpy(dst, src, strlen(src) + 1);
    printf("src=%s dst=%s equal=%s\n", src, dst,
           strcmp(src, dst) == 0 ? "yes" : "no");
    return 0;
}

// Done
