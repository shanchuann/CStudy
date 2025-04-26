#include <stdio.h>
#include <string.h>
#include <ctype.h>

// 将字符串转换为驼峰命名法
void toCamelCase(char* str) {
    if (str == NULL || str[0] == '\0') return;
    
    int len = strlen(str);
    int writeIndex = 0;
    int capitalizeNext = 0;  // 标记下一个字符是否需要大写
    
    // 遍历字符串
    for (int i = 0; i < len; i++) {
        // 跳过空格和特殊字符
        if (isspace(str[i]) || ispunct(str[i])) {
            capitalizeNext = 1;
            continue;
        }
        
        // 根据标记决定是否大写
        if (capitalizeNext) {
            str[writeIndex++] = toupper(str[i]);
        } else {
            str[writeIndex++] = tolower(str[i]);
        }
        
        capitalizeNext = 0;
    }
    
    // 添加字符串结束符
    str[writeIndex] = '\0';
}

int main() {
    char str[1000];
    
    printf("请输入一个字符串: ");
    gets(str);
    
    // 转换为驼峰命名法
    toCamelCase(str);
    
    printf("驼峰命名法: %s\n", str);
    
    return 0;
} 