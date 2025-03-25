#include <stdio.h>

int main() {
    int price, payment;
    int change;
    
    // 获取用户输入
    printf("请输入商品价格（元）：");
    scanf("%d", &price);
    printf("请输入支付金额（元）：");
    scanf("%d", &payment);
    
    // 计算找零
    change = payment - price;
    
    // 输出找零金额
    printf("找零：%d元\n", change);
    
    // 计算并输出各种面额的数量
    printf("100元：%d张\n", change / 100);
    change %= 100;
    
    printf("50元：%d张\n", change / 50);
    change %= 50;
    
    printf("20元：%d张\n", change / 20);
    change %= 20;
    
    printf("10元：%d张\n", change / 10);
    change %= 10;
    
    printf("5元：%d张\n", change / 5);
    change %= 5;
    
    printf("2元：%d个\n", change / 2);
    change %= 2;
    
    printf("1元：%d个\n", change);
    
    return 0;
} 