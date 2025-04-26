#include <stdio.h>
#include <string.h>

// 通用冒泡排序函数
void bubbleSort(void* arr, int n, int size, int (*compare)(const void*, const void*)) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - 1 - i; j++) {
            void* current = (char*)arr + j * size;
            void* next = (char*)arr + (j + 1) * size;
            
            if (compare(current, next) > 0) {
                // 交换元素
                char temp[size];
                memcpy(temp, current, size);
                memcpy(current, next, size);
                memcpy(next, temp, size);
            }
        }
    }
}

// 整数比较函数
int compareInt(const void* a, const void* b) {
    return (*(int*)a - *(int*)b);
}

// 浮点数比较函数
int compareFloat(const void* a, const void* b) {
    float diff = (*(float*)a - *(float*)b);
    return (diff > 0) - (diff < 0);
}

int main() {
    // 测试整数数组
    int intArr[] = {64, 34, 25, 12, 22, 11, 90};
    int n1 = sizeof(intArr) / sizeof(intArr[0]);
    
    printf("排序前的整数数组：\n");
    for (int i = 0; i < n1; i++) {
        printf("%d ", intArr[i]);
    }
    printf("\n");
    
    bubbleSort(intArr, n1, sizeof(int), compareInt);
    
    printf("排序后的整数数组：\n");
    for (int i = 0; i < n1; i++) {
        printf("%d ", intArr[i]);
    }
    printf("\n\n");
    
    // 测试浮点数数组
    float floatArr[] = {3.14, 2.71, 1.41, 0.58, 1.73};
    int n2 = sizeof(floatArr) / sizeof(floatArr[0]);
    
    printf("排序前的浮点数数组：\n");
    for (int i = 0; i < n2; i++) {
        printf("%.2f ", floatArr[i]);
    }
    printf("\n");
    
    bubbleSort(floatArr, n2, sizeof(float), compareFloat);
    
    printf("排序后的浮点数数组：\n");
    for (int i = 0; i < n2; i++) {
        printf("%.2f ", floatArr[i]);
    }
    printf("\n");
    
    return 0;
} 