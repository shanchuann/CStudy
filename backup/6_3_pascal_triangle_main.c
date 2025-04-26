#include <stdio.h>

void printPascalTriangle(int n) {
    // 创建二维数组存储杨辉三角
    int triangle[100][100];
    
    // 初始化第一列和对角线为1
    for (int i = 0; i < n; i++) {
        triangle[i][0] = 1;
        triangle[i][i] = 1;
    }
    
    // 计算其他元素
    for (int i = 2; i < n; i++) {
        for (int j = 1; j < i; j++) {
            triangle[i][j] = triangle[i-1][j-1] + triangle[i-1][j];
        }
    }
    
    // 打印杨辉三角
    for (int i = 0; i < n; i++) {
        // 打印空格
        for (int j = 0; j < n - i - 1; j++) {
            printf("  ");
        }
        // 打印数字
        for (int j = 0; j <= i; j++) {
            printf("%-4d", triangle[i][j]);
        }
        printf("\n");
    }
}

int main() {
    int n;
    printf("请输入杨辉三角的行数: ");
    scanf("%d", &n);
    
    if (n <= 0 || n > 100) {
        printf("请输入1到100之间的正整数\n");
        return 1;
    }
    
    printPascalTriangle(n);
    return 0;
} 