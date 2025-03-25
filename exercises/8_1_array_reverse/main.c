#include <stdio.h>

// 使用指针实现数组逆序
void reverseArray(int* arr, int size) {
    int* left = arr;
    int* right = arr + size - 1;
    
    while (left < right) {
        // 交换左右指针指向的元素
        int temp = *left;
        *left = *right;
        *right = temp;
        
        // 移动指针
        left++;
        right--;
    }
}

// 打印数组
void printArray(const int* arr, int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

int main() {
    int size;
    printf("请输入数组大小: ");
    scanf("%d", &size);
    
    if (size <= 0) {
        printf("请输入正整数！\n");
        return 1;
    }
    
    int arr[1000];  // 假设最大输入1000个元素
    printf("请输入%d个整数: ", size);
    for (int i = 0; i < size; i++) {
        scanf("%d", &arr[i]);
    }
    
    printf("原始数组: ");
    printArray(arr, size);
    
    // 逆序数组
    reverseArray(arr, size);
    
    printf("逆序后的数组: ");
    printArray(arr, size);
    
    return 0;
} 