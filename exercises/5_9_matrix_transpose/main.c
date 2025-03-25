#include <stdio.h>

// 矩阵转置函数
void transpose(int matrix[][100], int rows, int cols) {
    // 创建临时矩阵
    int temp[100][100];
    
    // 复制原矩阵
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            temp[i][j] = matrix[i][j];
        }
    }
    
    // 转置
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            matrix[j][i] = temp[i][j];
        }
    }
}

int main() {
    int rows, cols;
    printf("请输入矩阵的行数和列数：");
    scanf("%d %d", &rows, &cols);
    
    if (rows <= 0 || cols <= 0 || rows > 100 || cols > 100) {
        printf("行数和列数必须在1到100之间！\n");
        return 0;
    }
    
    int matrix[100][100];
    printf("请输入矩阵元素：\n");
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            scanf("%d", &matrix[i][j]);
        }
    }
    
    printf("\n原始矩阵：\n");
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            printf("%d ", matrix[i][j]);
        }
        printf("\n");
    }
    
    transpose(matrix, rows, cols);
    
    printf("\n转置后的矩阵：\n");
    for (int i = 0; i < cols; i++) {
        for (int j = 0; j < rows; j++) {
            printf("%d ", matrix[i][j]);
        }
        printf("\n");
    }
    
    return 0;
} 