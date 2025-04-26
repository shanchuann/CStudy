#include <stdio.h>

// 反转三位数
int reverse_number(int num) {
    // 验证输入是否为三位数
    if (num < 0 || num > 999) {
        return -1;  // 返回-1表示输入无效
    }
    
    // 获取各位数字
    int ones = num % 10;        // 个位
    int tens = (num / 10) % 10; // 十位
    int hundreds = num / 100;   // 百位
    
    // 反转数字
    return ones * 100 + tens * 10 + hundreds;
}

// int main() {
//     int num;
    
//     printf("请输入一个三位数: ");
//     scanf("%d", &num);
    
//     int reversed = reverse_number(num);
//     if (reversed == -1) {
//         printf("输入无效，请输入一个三位数！\n");
//         return 1;
//     }
    
//     printf("反转后的数字: %03d\n", reversed);
//     return 0;
// } 