#include <stdio.h>

int main() {
    float price;
    float total = 0;
    int count = 0;
    
    printf("欢迎使用超市收银系统！\n");
    printf("请输入商品价格（输入0结束）：\n");
    
    while (1) {
        printf("商品%d价格：", count + 1);
        scanf("%f", &price);
        
        if (price <= 0) {
            break;
        }
        
        total += price;
        count++;
    }
    
    printf("\n=== 收银小票 ===\n");
    printf("商品数量：%d\n", count);
    printf("商品总额：%.2f\n", total);
    printf("==============\n");
    
    return 0;
} 