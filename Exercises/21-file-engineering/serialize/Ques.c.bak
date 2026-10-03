#include <stdio.h>

int main(void) {
    int id = 0;
    char name[32] = {0};
    double score = 0.0;
    int read_id = 0;
    char read_name[32] = {0};
    double read_score = 0.0;
    FILE *fp = NULL;

    if (scanf("%d %31s %lf", &id, name, &score) != 3) {
        return 0;
    }

    (void)fp;
    /* TODO: 用 "w" 打开 student.txt，fprintf 写入 id|name|score（score 用 %.1f）并关闭 */
    /* TODO: 用 "r" 重新打开，fscanf 按 "%d|%31[^|]|%lf" 读回 read_id / read_name / read_score */

    printf("id=%d name=%s score=%.1f\n", read_id, read_name, read_score);
    return 0;
}

// Done
