#include <stdio.h>

int findSecondLargest(int arr[], int n) {
    if (n < 2) {
        printf("数组元素不足\n");
        return -1;
    }
    
    int largest = arr[0];
    int secondLargest = -1;
    
    for (int i = 1; i < n; i++) {
        if (arr[i] > largest) {
            secondLargest = largest;
            largest = arr[i];
        } else if (arr[i] > secondLargest && arr[i] != largest) {
            secondLargest = arr[i];
        }
    }
    
    return secondLargest;
}

int main() {
    int n;
    printf("请输入数组大小: ");
    scanf("%d", &n);
    
    int arr[100];
    printf("请输入%d个整数: ", n);
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    
    int result = findSecondLargest(arr, n);
    if (result != -1) {
        printf("第二大的元素是: %d\n", result);
    }
    
    return 0;
} 