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
        /* TODO: malloc 新节点并尾插到 head 指向的链表 */
        (void)value;
    }

    /* TODO: 用 previous / current / next 三个指针迭代反转链表，并更新 head */

    int first = 1;
    for (Node *current = head; current != NULL; current = current->next) {
        if (!first) {
            printf(" ");
        }
        printf("%d", current->value);
        first = 0;
    }
    printf("\n");
    return 0;
}

// Done
