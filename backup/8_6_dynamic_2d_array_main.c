#include <stdio.h>
#include <stdlib.h>

// 创建二维数组
int** create2DArray(int rows, int cols) {
    // 分配行指针数组
    int** arr = (int**)malloc(rows * sizeof(int*));
    if (!arr) {
        printf("内存分配失败！\n");
        return NULL;
    }
    
    // 为每一行分配内存
    for (int i = 0; i < rows; i++) {
        arr[i] = (int*)malloc(cols * sizeof(int));
        if (!arr[i]) {
            printf("内存分配失败！\n");
            // 释放已分配的内存
            for (int j = 0; j < i; j++) {
                free(arr[j]);
            }
            free(arr);
            return NULL;
        }
    }
    
    return arr;
}

// 释放二维数组
void free2DArray(int** arr, int rows) {
    if (!arr) return;
    
    // 释放每一行的内存
    for (int i = 0; i < rows; i++) {
        free(arr[i]);
    }
    // 释放行指针数组
    free(arr);
}

// 初始化二维数组
void init2DArray(int** arr, int rows, int cols) {
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            arr[i][j] = i * cols + j;
        }
    }
}

// 打印二维数组
void print2DArray(int** arr, int rows, int cols) {
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            printf("%3d ", arr[i][j]);
        }
        printf("\n");
    }
}

// 测试函数
void testDynamic2DArray() {
    int rows = 3, cols = 4;
    
    printf("创建 %d x %d 的二维数组：\n", rows, cols);
    int** arr = create2DArray(rows, cols);
    if (!arr) {
        printf("创建数组失败！\n");
        return;
    }
    
    printf("\n初始化数组：\n");
    init2DArray(arr, rows, cols);
    print2DArray(arr, rows, cols);
    
    printf("\n释放内存...\n");
    free2DArray(arr, rows);
}

int main() {
    testDynamic2DArray();
    return 0;
} 