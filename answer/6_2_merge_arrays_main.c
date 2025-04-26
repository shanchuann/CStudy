#include <stdio.h>

void mergeArrays(int arr1[], int n1, int arr2[], int n2, int result[]) {
    int i = 0, j = 0, k = 0;
    
    // 合并两个数组，保持有序
    while (i < n1 && j < n2) {
        if (arr1[i] <= arr2[j]) {
            result[k++] = arr1[i++];
        } else {
            result[k++] = arr2[j++];
        }
    }
    
    // 处理剩余元素
    while (i < n1) {
        result[k++] = arr1[i++];
    }
    while (j < n2) {
        result[k++] = arr2[j++];
    }
}

int main() {
    int n1, n2;
    
    // 输入第一个数组
    printf("请输入第一个数组的大小: ");
    scanf("%d", &n1);
    int arr1[100];
    printf("请输入%d个有序整数: ", n1);
    for (int i = 0; i < n1; i++) {
        scanf("%d", &arr1[i]);
    }
    
    // 输入第二个数组
    printf("请输入第二个数组的大小: ");
    scanf("%d", &n2);
    int arr2[100];
    printf("请输入%d个有序整数: ", n2);
    for (int i = 0; i < n2; i++) {
        scanf("%d", &arr2[i]);
    }
    
    // 合并数组
    int result[200];
    mergeArrays(arr1, n1, arr2, n2, result);
    
    // 输出结果
    printf("合并后的数组: ");
    for (int i = 0; i < n1 + n2; i++) {
        printf("%d ", result[i]);
    }
    printf("\n");
    
    return 0;
} 