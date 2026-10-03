#include <stdio.h>

enum State
{
    NEW,
    RUNNING,
    DONE
};

int main(void) {
    int value;
    if (scanf("%d", &value) != 1) {
        return 0;
    }
    /* TODO: 用 switch 把 value 映射为对应的状态单词 */
    (void)value;
    return 0;
}

// Done
