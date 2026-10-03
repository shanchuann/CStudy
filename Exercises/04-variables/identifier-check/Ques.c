#include <stdio.h>
#include <string.h>

int main(void) {
    char text[64];
    int valid = 0;

    if (scanf("%63s", text) != 1) {
        return 0;
    }

    /* TODO: 先检查字符集与首字符，再用关键字表逐个比较，设置 valid */
    (void)text;

    printf("%s\n", valid ? "valid" : "invalid");
    return 0;
}

// Done
