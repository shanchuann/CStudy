#include <stdio.h>
#include <string.h>

int main(void) {
    int n = 0;
    if (scanf("%d", &n) != 1) {
        return 0;
    }
    if (n < 1 || n > 50) {
        return 0;
    }
    char words[50][33];
    for (int i = 0; i < n; i++) {
        if (scanf("%32s", words[i]) != 1) {
            return 0;
        }
    }
    /* TODO: 按 strcmp 字典序升序排序，然后每行输出一个单词 */
    for (int i = 0; i < n; i++) {
        printf("%s\n", words[i]);
    }
    return 0;
}

// Done
