#include <stdio.h>
#include <string.h>

// 字符串匹配函数（暴力匹配）
int stringMatch(const char* text, const char* pattern) {
    int textLen = strlen(text);
    int patternLen = strlen(pattern);
    
    // 如果模式串为空，返回0
    if (patternLen == 0) return 0;
    
    // 如果模式串长度大于文本串，返回-1
    if (patternLen > textLen) return -1;
    
    // 暴力匹配
    for (int i = 0; i <= textLen - patternLen; i++) {
        int j;
        for (j = 0; j < patternLen; j++) {
            if (text[i + j] != pattern[j]) {
                break;
            }
        }
        // 如果找到匹配，返回起始位置
        if (j == patternLen) {
            return i;
        }
    }
    
    // 未找到匹配，返回-1
    return -1;
}

int main() {
    char text[1000];
    char pattern[100];
    
    printf("请输入文本串：");
    scanf("%s", text);
    
    printf("请输入模式串：");
    scanf("%s", pattern);
    
    int position = stringMatch(text, pattern);
    
    if (position == -1) {
        printf("未找到匹配！\n");
    } else {
        printf("模式串在位置 %d 处匹配成功！\n", position);
    }
    
    return 0;
} 