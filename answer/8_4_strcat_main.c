#include <stdio.h>

// 使用指针实现strcat函数
char* my_strcat(char* dest, const char* src) {
    // 保存目标字符串的起始位置
    char* start = dest;
    
    // 移动到目标字符串的末尾
    while (*dest != '\0') {
        dest++;
    }
    
    // 复制源字符串到目标字符串末尾
    while (*src != '\0') {
        *dest = *src;
        dest++;
        src++;
    }
    
    // 添加字符串结束符
    *dest = '\0';
    
    return start;
}

// 测试函数
void test_strcat() {
    // 测试用例1：基本字符串连接
    char str1[50] = "Hello, ";
    const char* str2 = "World!";
    printf("测试用例1：\n");
    printf("str1: %s\n", str1);
    printf("str2: %s\n", str2);
    my_strcat(str1, str2);
    printf("连接后: %s\n\n", str1);
    
    // 测试用例2：空字符串
    char str3[50] = "";
    const char* str4 = "Empty string test";
    printf("测试用例2：\n");
    printf("str3: %s\n", str3);
    printf("str4: %s\n", str4);
    my_strcat(str3, str4);
    printf("连接后: %s\n\n", str3);
    
    // 测试用例3：连接空字符串
    char str5[50] = "Non-empty string";
    const char* str6 = "";
    printf("测试用例3：\n");
    printf("str5: %s\n", str5);
    printf("str6: %s\n", str6);
    my_strcat(str5, str6);
    printf("连接后: %s\n\n", str5);
    
    // 测试用例4：长字符串
    char str7[100] = "This is a very long string that ";
    const char* str8 = "will be concatenated with another long string.";
    printf("测试用例4：\n");
    printf("str7: %s\n", str7);
    printf("str8: %s\n", str8);
    my_strcat(str7, str8);
    printf("连接后: %s\n", str7);
}

int main() {
    test_strcat();
    return 0;
} 