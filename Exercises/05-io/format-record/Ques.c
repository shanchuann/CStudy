#include <stdio.h>

int main(void) {
    char name[64];
    int score = 0;
    if (scanf("%63s %d", name, &score) != 2) {
        return 0;
    }
    /* TODO: 按 name: score 的格式输出一行 */
    (void)name;
    (void)score;
    return 0;
}

// Done
