#include <stdio.h>

// 二分查找函数
int binarySearch(int arr[], int left, int right, int target) {
    while (left <= right) {
        int mid = left + (right - left) / 2;
        
        // 找到目标值
        if (arr[mid] == target) {
            return mid;
        }
        
        // 目标值在右半部分
        if (arr[mid] < target) {
            left = mid + 1;
        }
        // 目标值在左半部分
        else {
            right = mid - 1;
        }
    }
    
    // 未找到目标值
    return -1;
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
    printf("请输入%d个已排序的整数: ", n);
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    
    int target;
    printf("请输入要查找的目标值: ");
    scanf("%d", &target);
    
    // 执行二分查找
    int result = binarySearch(arr, 0, n - 1, target);
    
    // 输出结果
    if (result != -1) {
        printf("目标值%d在数组中的位置是: %d\n", target, result);
    } else {
        printf("未找到目标值%d\n", target);
    }
    
    return 0;
} 