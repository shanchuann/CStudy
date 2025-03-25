#include <stdio.h>
#include <string.h>

// 去除字符串中的重复字符
void removeDuplicates(char* str) {
    if (str == NULL || str[0] == '\0') return;
    
    int len = strlen(str);
    int writeIndex = 0;  // 写入位置
    
    // 遍历字符串
    for (int i = 0; i < len; i++) {
        // 检查当前字符是否已经出现过
        int isDuplicate = 0;
        for (int j = 0; j < writeIndex; j++) {
            if (str[i] == str[j]) {
                isDuplicate = 1;
                break;
            }
        }
        
        // 如果不是重复字符，则保留
        if (!isDuplicate) {
            str[writeIndex++] = str[i];
        }
    }
    
    // 添加字符串结束符
    str[writeIndex] = '\0';
}

int main() {
    char str[1000];
    
    printf("请输入一个字符串: ");
    gets(str);
    
    // 去除重复字符
    removeDuplicates(str);
    
    printf("去除重复字符后的字符串: %s\n", str);
    
    return 0;
} 