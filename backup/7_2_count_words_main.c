#include <stdio.h>
#include <ctype.h>

// 统计单词数量的函数
int countWords(const char* str) {
    int count = 0;
    int inWord = 0;  // 标记是否在单词内
    
    // 遍历字符串
    for (int i = 0; str[i] != '\0'; i++) {
        // 如果当前字符是字母或数字
        if (isalnum(str[i])) {
            if (!inWord) {  // 如果之前不在单词内
                count++;
                inWord = 1;
            }
        } else {
            inWord = 0;  // 遇到非字母数字字符，标记不在单词内
        }
    }
    
    return count;
}

int main() {
    char str[1000];
    
    printf("请输入一行文本: ");
    gets(str);
    
    // 统计单词数量
    int wordCount = countWords(str);
    
    printf("单词数量: %d\n", wordCount);
    
    return 0;
} 