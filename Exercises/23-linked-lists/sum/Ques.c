#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int value;
    struct Node *next;
} Node;

int main(void) {
    int n = 0;
    if (scanf("%d", &n) != 1) {
        return 0;
    }

    Node *head = NULL;
    for (int i = 0; i < n; i++) {
        int value = 0;
        scanf("%d", &value);
        /* TODO: malloc 一个新节点，填入 value，尾插到 head 指向的链表 */
        (void)value;
    }

    int sum = 0;
    /* TODO: 从头遍历链表，累加到 sum，并在过程中 free 每个节点 */
    printf("%d\n", sum);
    (void)head;
    return 0;
}

// Done
