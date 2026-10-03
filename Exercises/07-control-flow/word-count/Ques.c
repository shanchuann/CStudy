#include <stdio.h>

int main(void) {
    int ch;
    int in_word = 0;
    int words = 0;
    int chars = 0;
    while ((ch = getchar()) != EOF && ch != '\n') {
        chars++;
        /* TODO: 根据 ch 是否为空白更新 in_word，并在进入新单词时累加 words */
        (void)in_word;
    }
    printf("words=%d chars=%d\n", words, chars);
    return 0;
}

// Done
