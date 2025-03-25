#include <stdio.h>
#include <math.h>

// 复数结构体
typedef struct {
    double real;      // 实部
    double imag;      // 虚部
} Complex;

// 创建复数
Complex createComplex(double real, double imag) {
    Complex c = {real, imag};
    return c;
}

// 打印复数
void printComplex(Complex c) {
    if (c.imag >= 0) {
        printf("%.2f + %.2fi", c.real, c.imag);
    } else {
        printf("%.2f - %.2fi", c.real, -c.imag);
    }
}

// 复数加法
Complex addComplex(Complex a, Complex b) {
    Complex result = {
        a.real + b.real,
        a.imag + b.imag
    };
    return result;
}

// 复数减法
Complex subtractComplex(Complex a, Complex b) {
    Complex result = {
        a.real - b.real,
        a.imag - b.imag
    };
    return result;
}

// 复数乘法
Complex multiplyComplex(Complex a, Complex b) {
    Complex result = {
        a.real * b.real - a.imag * b.imag,
        a.real * b.imag + a.imag * b.real
    };
    return result;
}

// 复数除法
Complex divideComplex(Complex a, Complex b) {
    double denominator = b.real * b.real + b.imag * b.imag;
    if (denominator == 0) {
        printf("错误：除数不能为零！\n");
        return createComplex(0, 0);
    }
    
    Complex result = {
        (a.real * b.real + a.imag * b.imag) / denominator,
        (a.imag * b.real - a.real * b.imag) / denominator
    };
    return result;
}

// 计算复数的模
double magnitudeComplex(Complex c) {
    return sqrt(c.real * c.real + c.imag * c.imag);
}

// 计算复数的共轭
Complex conjugateComplex(Complex c) {
    Complex result = {c.real, -c.imag};
    return result;
}

// 显示菜单
void showMenu() {
    printf("\n复数运算系统\n");
    printf("1. 复数加法\n");
    printf("2. 复数减法\n");
    printf("3. 复数乘法\n");
    printf("4. 复数除法\n");
    printf("5. 计算模\n");
    printf("6. 计算共轭\n");
    printf("0. 退出系统\n");
    printf("请选择操作：");
}

// 输入复数
Complex inputComplex() {
    Complex c;
    printf("请输入实部：");
    scanf("%lf", &c.real);
    printf("请输入虚部：");
    scanf("%lf", &c.imag);
    return c;
}

int main() {
    int choice;
    Complex a, b, result;
    
    do {
        showMenu();
        scanf("%d", &choice);
        
        switch (choice) {
            case 1:
                printf("请输入第一个复数：\n");
                a = inputComplex();
                printf("请输入第二个复数：\n");
                b = inputComplex();
                
                printf("(");
                printComplex(a);
                printf(") + (");
                printComplex(b);
                printf(") = ");
                
                result = addComplex(a, b);
                printComplex(result);
                printf("\n");
                break;
                
            case 2:
                printf("请输入第一个复数：\n");
                a = inputComplex();
                printf("请输入第二个复数：\n");
                b = inputComplex();
                
                printf("(");
                printComplex(a);
                printf(") - (");
                printComplex(b);
                printf(") = ");
                
                result = subtractComplex(a, b);
                printComplex(result);
                printf("\n");
                break;
                
            case 3:
                printf("请输入第一个复数：\n");
                a = inputComplex();
                printf("请输入第二个复数：\n");
                b = inputComplex();
                
                printf("(");
                printComplex(a);
                printf(") * (");
                printComplex(b);
                printf(") = ");
                
                result = multiplyComplex(a, b);
                printComplex(result);
                printf("\n");
                break;
                
            case 4:
                printf("请输入第一个复数：\n");
                a = inputComplex();
                printf("请输入第二个复数：\n");
                b = inputComplex();
                
                printf("(");
                printComplex(a);
                printf(") / (");
                printComplex(b);
                printf(") = ");
                
                result = divideComplex(a, b);
                printComplex(result);
                printf("\n");
                break;
                
            case 5:
                printf("请输入复数：\n");
                a = inputComplex();
                
                printf("|");
                printComplex(a);
                printf("| = %.2f\n", magnitudeComplex(a));
                break;
                
            case 6:
                printf("请输入复数：\n");
                a = inputComplex();
                
                printf("共轭复数：");
                result = conjugateComplex(a);
                printComplex(result);
                printf("\n");
                break;
                
            case 0:
                printf("感谢使用！\n");
                break;
                
            default:
                printf("无效的选择，请重试！\n");
        }
    } while (choice != 0);
    
    return 0;
} 