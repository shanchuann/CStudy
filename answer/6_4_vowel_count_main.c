#include <stdio.h>
#include <string.h>
#include <ctype.h>

void countVowels(const char* str, int* counts) {
    // 初始化计数数组
    for (int i = 0; i < 5; i++) {
        counts[i] = 0;
    }
    
    // 统计元音字母
    for (int i = 0; str[i] != '\0'; i++) {
        char c = tolower(str[i]);
        switch (c) {
            case 'a': counts[0]++; break;
            case 'e': counts[1]++; break;
            case 'i': counts[2]++; break;
            case 'o': counts[3]++; break;
            case 'u': counts[4]++; break;
        }
    }
}

int main() {
    char str[1000];
    int counts[5] = {0};  // a, e, i, o, u
    
    printf("请输入一个字符串: ");
    fgets(str, sizeof(str), stdin);
    
    // 移除换行符
    str[strcspn(str, "\n")] = 0;
    
    countVowels(str, counts);
    
    // 输出结果
    printf("\n元音字母统计结果：\n");
    printf("a: %d\n", counts[0]);
    printf("e: %d\n", counts[1]);
    printf("i: %d\n", counts[2]);
    printf("o: %d\n", counts[3]);
    printf("u: %d\n", counts[4]);
    
    return 0;
} 