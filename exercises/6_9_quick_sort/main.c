#include <stdio.h>

// 交换两个元素
void swap(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

// 选择基准值并分区
int partition(int arr[], int low, int high) {
    // 选择最后一个元素作为基准值
    int pivot = arr[high];
    int i = low - 1;  // 小于基准值的元素的最后位置
    
    // 将小于基准值的元素移到左边
    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    
    // 将基准值放到正确的位置
    swap(&arr[i + 1], &arr[high]);
    return i + 1;
}

// 快速排序的递归实现
void quickSort(int arr[], int low, int high) {
    if (low < high) {
        // 获取分区点
        int pi = partition(arr, low, high);
        
        // 递归排序左半部分
        quickSort(arr, low, pi - 1);
        // 递归排序右半部分
        quickSort(arr, pi + 1, high);
    }
}

int main() {
    int n;
    printf("请输入数组大小: ");
    scanf("%d", &n);
    
    if (n <= 0) {
        printf("请输入正整数！\n");
        return 1;
    }
    
    int arr[1000];
    printf("请输入%d个整数: ", n);
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    
    // 执行快速排序
    quickSort(arr, 0, n - 1);
    
    // 输出排序后的数组
    printf("排序后的数组: ");
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    
    return 0;
} 