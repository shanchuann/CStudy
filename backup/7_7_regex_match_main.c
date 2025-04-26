#include <stdio.h>
#include <string.h>

// 简单的正则表达式匹配函数
int isMatch(const char* s, const char* p) {
    // 如果模式串为空
    if (*p == '\0') {
        return *s == '\0';
    }
    
    // 检查第一个字符是否匹配
    int firstMatch = (*s != '\0') && (*p == *s || *p == '.');
    
    // 如果下一个字符是*
    if (*(p + 1) == '*') {
        // 两种情况：1. 不使用*匹配 2. 使用*匹配
        return isMatch(s, p + 2) || (firstMatch && isMatch(s + 1, p));
    }
    
    // 如果下一个字符不是*，继续匹配下一个字符
    return firstMatch && isMatch(s + 1, p + 1);
}

int main() {
    char str[1000];
    char pattern[1000];
    
    printf("请输入要匹配的字符串: ");
    gets(str);
    
    printf("请输入模式串（支持.和*）: ");
    gets(pattern);
    
    // 执行匹配
    if (isMatch(str, pattern)) {
        printf("匹配成功\n");
    } else {
        printf("匹配失败\n");
    }
    
    return 0;
} 