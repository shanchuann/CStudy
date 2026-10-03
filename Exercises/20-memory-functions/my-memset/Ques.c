#include <stdio.h>

/* TODO: 实现 my_memset：把 dst 的前 count 个字节设为 value，并返回 dst */
void *my_memset(void *dst, int value, size_t count) {
    (void)value;
    (void)count;
    return dst;
}

int main(void) {
    char c = 0;
    int count = 0;
    char buffer[16] = {0};

    if (scanf("%c %d", &c, &count) != 2) {
        return 0;
    }
    my_memset(buffer, c, (size_t)count);
    buffer[count] = '\0';
    printf("%s\n", buffer);
    return 0;
}

// Done
