#include <stdio.h>

int main(void) {
    int score;
    if (scanf("%d", &score) != 1) {
        return 0;
    }
    /* TODO: 先处理 0..100 之外的分数，再用 switch (score / 10) 输出等级 */
    (void)score;
    return 0;
}

// Done
