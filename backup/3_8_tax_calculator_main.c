#include <stdio.h>

int main() {
    int income;
    float tax = 0;
    float afterTax;
    
    // 获取用户输入
    printf("请输入月收入（元）：");
    scanf("%d", &income);
    
    // 计算应纳税所得额
    int taxableIncome = income - 5000;
    
    // 根据税率表计算应缴税额
    if (taxableIncome <= 0) {
        tax = 0;
    } else if (taxableIncome <= 3000) {
        tax = taxableIncome * 0.03;
    } else if (taxableIncome <= 12000) {
        tax = taxableIncome * 0.1 - 210;
    } else if (taxableIncome <= 25000) {
        tax = taxableIncome * 0.2 - 1410;
    } else if (taxableIncome <= 35000) {
        tax = taxableIncome * 0.25 - 2660;
    } else if (taxableIncome <= 55000) {
        tax = taxableIncome * 0.3 - 4410;
    } else if (taxableIncome <= 80000) {
        tax = taxableIncome * 0.35 - 7160;
    } else {
        tax = taxableIncome * 0.45 - 15160;
    }
    
    // 计算税后收入
    afterTax = income - tax;
    
    // 输出结果
    printf("税前收入：%d元\n", income);
    printf("应纳税所得额：%d元\n", taxableIncome);
    printf("应缴税额：%.2f元\n", tax);
    printf("税后收入：%.2f元\n", afterTax);
    
    return 0;
} 