#include <stdio.h>

// 自定义strcpy函数
char* my_strcpy(char* dest, const char* src) {
    // 保存目标字符串的起始位置
    char* original_dest = dest;
    
    // 复制字符直到遇到字符串结束符
    while ((*dest++ = *src++) != '\0');
    
    return original_dest;
}

int main() {
    char src[100];
    char dest[100];
    
    printf("请输入源字符串: ");
    gets(src);
    
    // 调用自定义strcpy函数
    my_strcpy(dest, src);
    
    printf("复制后的字符串: %s\n", dest);
    
    return 0;
} 