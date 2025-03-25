#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// 压缩字符串
char* compress(const char* s) {
    int len = strlen(s);
    if (len == 0) return strdup("");
    
    // 分配足够大的空间（最坏情况：每个字符都不同）
    char* result = (char*)malloc(len * 2 + 1);
    if (!result) return NULL;
    
    int writePos = 0;
    int count = 1;
    
    for (int i = 1; i <= len; i++) {
        if (i == len || s[i] != s[i-1]) {
            result[writePos++] = s[i-1];
            if (count > 1) {
                int numLen = sprintf(result + writePos, "%d", count);
                writePos += numLen;
            }
            count = 1;
        } else {
            count++;
        }
    }
    
    result[writePos] = '\0';
    return result;
}

// 解压缩字符串
char* decompress(const char* s) {
    int len = strlen(s);
    if (len == 0) return strdup("");
    
    // 计算解压后的最大长度
    int maxLen = 0;
    for (int i = 0; i < len; i++) {
        if (s[i] >= '0' && s[i] <= '9') {
            maxLen += (s[i] - '0') - 1;  // 减1是因为字符本身已经计算在内
        } else {
            maxLen++;
        }
    }
    
    // 分配空间
    char* result = (char*)malloc(maxLen + 1);
    if (!result) return NULL;
    
    int writePos = 0;
    for (int i = 0; i < len; i++) {
        if (s[i] >= '0' && s[i] <= '9') {
            int count = s[i] - '0';
            char prevChar = result[writePos - 1];
            for (int j = 1; j < count; j++) {
                result[writePos++] = prevChar;
            }
        } else {
            result[writePos++] = s[i];
        }
    }
    
    result[writePos] = '\0';
    return result;
}

int main() {
    char str[1000];
    
    printf("请输入一个字符串: ");
    gets(str);
    
    // 压缩
    char* compressed = compress(str);
    printf("压缩后的字符串: %s\n", compressed);
    
    // 解压缩
    char* decompressed = decompress(compressed);
    printf("解压缩后的字符串: %s\n", decompressed);
    
    // 释放内存
    free(compressed);
    free(decompressed);
    
    return 0;
} 