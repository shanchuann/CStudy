#include <stdio.h>
#include <string.h>

// 递归反转字符串
void reverseString(char* str, int start, int end) {
    if (start >= end) {
        return;
    }
    
    // 交换首尾字符
    char temp = str[start];
    str[start] = str[end];
    str[end] = temp;
    
    // 递归处理中间部分
    reverseString(str, start + 1, end - 1);
}

int main() {
    char str[100];
    printf("请输入一个字符串：");
    scanf("%s", str);
    
    int length = strlen(str);
    reverseString(str, 0, length - 1);
    
    printf("反转后的字符串：%s\n", str);
    
    return 0;
} 