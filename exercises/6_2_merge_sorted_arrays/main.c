#include <stdio.h>

void mergeSortedArrays(int arr1[], int size1, int arr2[], int size2, int result[]) {
    int i = 0, j = 0, k = 0;
    
    // 合并两个数组
    while (i < size1 && j < size2) {
        if (arr1[i] <= arr2[j]) {
            result[k++] = arr1[i++];
        } else {
            result[k++] = arr2[j++];
        }
    }
    
    // 处理剩余元素
    while (i < size1) {
        result[k++] = arr1[i++];
    }
    while (j < size2) {
        result[k++] = arr2[j++];
    }
}

int main() {
    int size1, size2;
    int arr1[100], arr2[100], result[200];
    
    printf("请输入第一个数组的大小：");
    scanf("%d", &size1);
    printf("请输入第一个有序数组的元素：\n");
    for (int i = 0; i < size1; i++) {
        scanf("%d", &arr1[i]);
    }
    
    printf("请输入第二个数组的大小：");
    scanf("%d", &size2);
    printf("请输入第二个有序数组的元素：\n");
    for (int i = 0; i < size2; i++) {
        scanf("%d", &arr2[i]);
    }
    
    mergeSortedArrays(arr1, size1, arr2, size2, result);
    
    printf("合并后的数组：");
    for (int i = 0; i < size1 + size2; i++) {
        printf("%d ", result[i]);
    }
    printf("\n");
    
    return 0;
} 