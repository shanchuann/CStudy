#include <stdio.h>
#include <ctype.h>

// 凯撒密码加密函数
void caesarCipher(char* str, int shift) {
    for (int i = 0; str[i] != '\0'; i++) {
        if (isalpha(str[i])) {
            // 确定基准值（大写字母为'A'，小写字母为'a'）
            char base = isupper(str[i]) ? 'A' : 'a';
            // 计算移位后的字符
            str[i] = base + ((str[i] - base + shift + 26) % 26);
        }
    }
}

int main() {
    char str[1000];
    int shift;
    
    printf("请输入要加密的文本: ");
    gets(str);
    
    printf("请输入移位值（1-25）: ");
    scanf("%d", &shift);
    
    // 确保移位值在有效范围内
    shift = ((shift % 26) + 26) % 26;
    
    // 执行加密
    caesarCipher(str, shift);
    
    printf("加密后的文本: %s\n", str);
    
    return 0;
} 