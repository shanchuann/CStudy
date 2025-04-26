#include <stdio.h>

void findDuplicates(int arr[], int n) {
    // 创建标记数组
    int marked[1000] = {0};
    int found = 0;
    
    // 遍历数组找出重复元素
    for (int i = 0; i < n; i++) {
        if (marked[arr[i]] == 0) {
            // 第一次出现，标记为1
            marked[arr[i]] = 1;
        } else if (marked[arr[i]] == 1) {
            // 第二次出现，标记为2并输出
            marked[arr[i]] = 2;
            if (!found) {
                printf("重复的元素是: ");
                found = 1;
            }
            printf("%d ", arr[i]);
        }
    }
    
    if (!found) {
        printf("没有找到重复的元素\n");
    } else {
        printf("\n");
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
    
    findDuplicates(arr, n);
    
    return 0;
} 