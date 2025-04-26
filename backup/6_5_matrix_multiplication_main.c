#include <stdio.h>

void inputMatrix(int matrix[][100], int rows, int cols) {
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            scanf("%d", &matrix[i][j]);
        }
    }
}

void multiplyMatrices(int matrix1[][100], int matrix2[][100], int result[][100],
                     int rows1, int cols1, int rows2, int cols2) {
    // 初始化结果矩阵为0
    for (int i = 0; i < rows1; i++) {
        for (int j = 0; j < cols2; j++) {
            result[i][j] = 0;
        }
    }
    
    // 矩阵乘法
    for (int i = 0; i < rows1; i++) {
        for (int j = 0; j < cols2; j++) {
            for (int k = 0; k < cols1; k++) {
                result[i][j] += matrix1[i][k] * matrix2[k][j];
            }
        }
    }
}

void printMatrix(int matrix[][100], int rows, int cols) {
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            printf("%d ", matrix[i][j]);
        }
        printf("\n");
    }
}

int main() {
    int rows1, cols1, rows2, cols2;
    
    // 输入第一个矩阵的维度
    printf("请输入第一个矩阵的行数和列数: ");
    scanf("%d %d", &rows1, &cols1);
    
    // 输入第二个矩阵的维度
    printf("请输入第二个矩阵的行数和列数: ");
    scanf("%d %d", &rows2, &cols2);
    
    // 检查矩阵是否可以相乘
    if (cols1 != rows2) {
        printf("错误：第一个矩阵的列数必须等于第二个矩阵的行数！\n");
        return 1;
    }
    
    // 声明矩阵
    int matrix1[100][100], matrix2[100][100], result[100][100];
    
    // 输入第一个矩阵
    printf("请输入第一个矩阵的元素：\n");
    inputMatrix(matrix1, rows1, cols1);
    
    // 输入第二个矩阵
    printf("请输入第二个矩阵的元素：\n");
    inputMatrix(matrix2, rows2, cols2);
    
    // 计算矩阵乘法
    multiplyMatrices(matrix1, matrix2, result, rows1, cols1, rows2, cols2);
    
    // 输出结果
    printf("\n矩阵乘法结果：\n");
    printMatrix(result, rows1, cols2);
    
    return 0;
} 