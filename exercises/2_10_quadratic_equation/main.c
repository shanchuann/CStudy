#include <stdio.h>
#include <math.h>
#include "../testwork/test_framework.h"

// 全局变量定义
char current_output[100];
char current_input[100];

// 二次方程求解函数
void solve_quadratic(double a, double b, double c) {
    // 检查是否为二次方程
    if (a == 0) {
        sprintf(current_output, "Not a quadratic equation");
        return;
    }
    
    // 计算判别式
    double discriminant = b * b - 4 * a * c;
    
    // 根据判别式判断根的情况
    if (discriminant > 0) {
        // 两个不同的实根，确保x1 >= x2
        double x1 = (-b + sqrt(discriminant)) / (2 * a);
        double x2 = (-b - sqrt(discriminant)) / (2 * a);
        if (x1 < x2) {
            double temp = x1;
            x1 = x2;
            x2 = temp;
        }
        sprintf(current_output, "x1 = %.6f, x2 = %.6f", x1, x2);
    } else if (discriminant == 0) {
        // 两个相等的实根
        double x = -b / (2 * a);
        sprintf(current_output, "x1 = %.6f, x2 = %.6f", x, x);
    } else {
        // 无实根
        sprintf(current_output, "No real roots");
    }
} 