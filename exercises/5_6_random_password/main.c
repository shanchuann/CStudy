#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

// 生成随机密码
void generatePassword(char* password, int length) {
    const char lowercase[] = "abcdefghijklmnopqrstuvwxyz";
    const char uppercase[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const char digits[] = "0123456789";
    const char all[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    
    // 确保密码至少包含每种字符
    password[0] = lowercase[rand() % 26];
    password[1] = uppercase[rand() % 26];
    password[2] = digits[rand() % 10];
    
    // 填充剩余位置
    for (int i = 3; i < length; i++) {
        password[i] = all[rand() % 62];
    }
    
    // 打乱密码字符顺序
    for (int i = length - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        char temp = password[i];
        password[i] = password[j];
        password[j] = temp;
    }
    
    // 添加字符串结束符
    password[length] = '\0';
}

int main() {
    // 初始化随机数种子
    srand(time(NULL));
    
    int length;
    printf("请输入密码长度（至少8位）：");
    scanf("%d", &length);
    
    if (length < 8) {
        printf("密码长度至少为8位！\n");
        return 0;
    }
    
    char password[length + 1];
    generatePassword(password, length);
    
    printf("生成的密码：%s\n", password);
    
    return 0;
} 