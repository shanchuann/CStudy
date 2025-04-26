#include <stdio.h>
#include <string.h>

// 计算最长回文子串长度
int longestPalindrome(const char* s) {
    int len = strlen(s);
    if (len == 0) return 0;
    
    int maxLen = 1;  // 最长回文子串的长度
    int start = 0;   // 最长回文子串的起始位置
    
    // 创建动态规划表
    int dp[1000][1000] = {0};
    
    // 初始化长度为1的回文串
    for (int i = 0; i < len; i++) {
        dp[i][i] = 1;
    }
    
    // 初始化长度为2的回文串
    for (int i = 0; i < len - 1; i++) {
        if (s[i] == s[i + 1]) {
            dp[i][i + 1] = 1;
            maxLen = 2;
            start = i;
        }
    }
    
    // 计算长度为3及以上的回文串
    for (int length = 3; length <= len; length++) {
        for (int i = 0; i < len - length + 1; i++) {
            int j = i + length - 1;
            if (s[i] == s[j] && dp[i + 1][j - 1]) {
                dp[i][j] = 1;
                if (length > maxLen) {
                    maxLen = length;
                    start = i;
                }
            }
        }
    }
    
    return maxLen;
}

int main() {
    char str[1000];
    
    printf("请输入一个字符串: ");
    gets(str);
    
    // 计算最长回文子串长度
    int length = longestPalindrome(str);
    
    printf("最长回文子串的长度: %d\n", length);
    
    return 0;
} 