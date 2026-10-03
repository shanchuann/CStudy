#include <stdio.h>

struct Student {
    int id;
    char name[32];
    double score;
};

int main(void) {
    int n = 0;
    struct Student students[100];
    scanf("%d", &n);
    /* TODO: 读入记录；写入 students.txt；关闭后重新打开读回；输出记录数与最高分学号 */
    (void)students;
    return 0;
}

// Done
