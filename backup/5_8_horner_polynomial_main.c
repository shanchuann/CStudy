#include <stdio.h>

// 使用霍纳法则计算多项式值
double horner(double x, double* coefficients, int n) {
    double result = coefficients[0];
    
    for (int i = 1; i < n; i++) {
        result = result * x + coefficients[i];
    }
    
    return result;
}

int main() {
    int n;
    printf("请输入多项式的项数：");
    scanf("%d", &n);
    
    if (n <= 0) {
        printf("项数必须大于0！\n");
        return 0;
    }
    
    double coefficients[n];
    printf("请从高次项到低次项依次输入系数：\n");
    for (int i = 0; i < n; i++) {
        printf("x^%d的系数：", n-1-i);
        scanf("%lf", &coefficients[i]);
    }
    
    double x;
    printf("请输入x的值：");
    scanf("%lf", &x);
    
    double result = horner(x, coefficients, n);
    printf("多项式在x=%.2f处的值为：%.4f\n", x, result);
    
    return 0;
} 