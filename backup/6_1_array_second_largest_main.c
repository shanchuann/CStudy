#include <stdio.h>

int findSecondLargest(int arr[], int size) {
    // 处理特殊情况
    if (size < 2) {
        return -1;
    }
    
    // 找出最大元素
    int max = arr[0];
    for (int i = 1; i < size; i++) {
        if (arr[i] > max) {
            max = arr[i];
        }
    }
    
    // 找出第二大元素
    int secondMax = -1;
    for (int i = 0; i < size; i++) {
        if (arr[i] != max && arr[i] > secondMax) {
            secondMax = arr[i];
        }
    }
    
    return secondMax;
}

int main() {
    int size;
    printf("请输入数组大小：");
    scanf("%d", &size);
    
    if (size < 1 || size > 100) {
        printf("数组大小必须在1到100之间！\n");
        return 0;
    }
    
    int arr[100];
    printf("请输入%d个整数，以空格分隔：\n", size);
    for (int i = 0; i < size; i++) {
        scanf("%d", &arr[i]);
    }
    
    int result = findSecondLargest(arr, size);
    
    if (result == -1) {
        printf("不存在第二大的元素\n");
    } else {
        printf("第二大的元素是：%d\n", result);
    }
    
    return 0;
} 