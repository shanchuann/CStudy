#include <stdio.h>
#include "../testwork/test_framework.h"

// 全局变量定义
char current_output[100];
char current_input[100];

// 判断是否为回文数
void is_palindrome(int num) {
    // TODO: 在这里实现你的代码
    // 输入：num - 要判断的数字
    // 输出：将结果存储在 current_output 中
    // 示例：sprintf(current_output, "Yes");
    // 示例：sprintf(current_output, "No");
    
    // 提示：
    // 1. A palindrome number reads the same backward as forward
    // 2. Examples: 121, 12321 are palindromes
    // 3. Examples: 123, 1234 are not palindromes
    // 处理负数
    if (num < 0) {
        sprintf(current_output, "No");
        return;
    }
    
    // 将数字转换为字符串
    char str[20];
    sprintf(str, "%d", num);
    
    // 判断是否为回文
    int len = strlen(str);
    int is_pal = 1;
    for (int i = 0; i < len/2; i++) {
        if (str[i] != str[len-1-i]) {
            is_pal = 0;
            break;
        }
    }
    
    sprintf(current_output, is_pal ? "Yes" : "No");
}