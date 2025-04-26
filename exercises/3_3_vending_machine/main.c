#include <stdio.h>
#include "../testwork/test_framework.h"

// 全局变量定义
char current_output[100];
char current_input[100];

// 自动售货机函数
void vending_machine(int money, int choice) {
    // 商品信息
    struct {
        char name[20];
        int price;
    } products[] = {
        {"Cola", 3},
        {"Sprite", 3},
        {"Water", 2},
        {"Juice", 4},
        {"Coffee", 5}
    };
    
    // 检查选择是否有效
    if (choice < 1 || choice > 5) {
        sprintf(current_output, "Invalid Choice");
        return;
    }
    
    // 检查金额是否足够
    if (money < products[choice - 1].price) {
        sprintf(current_output, "Not Enough Money");
        return;
    }
    
    // 计算找零
    int change = money - products[choice - 1].price;
    sprintf(current_output, "Buy %s Success, Change: %d", products[choice - 1].name, change);
}

// int main() {
//     int money, choice;
    
//     // 显示菜单
//     printf("Welcome to Vending Machine!\n");
//     printf("1. Cola - 3\n");
//     printf("2. Sprite - 3\n");
//     printf("3. Water - 2\n");
//     printf("4. Juice - 4\n");
//     printf("5. Coffee - 5\n");
    
//     // 获取用户输入
//     printf("Please input money: ");
//     scanf("%d", &money);
//     printf("Please choose product (1-5): ");
//     scanf("%d", &choice);
    
//     // 调用自动售货机函数
//     vending_machine(money, choice);
    
//     return 0;
// } 