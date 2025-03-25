#include <stdio.h>

int josephus(int n, int k) {
    // 创建数组表示每个人
    int people[1000] = {0};
    int count = 0;  // 当前报数
    int alive = n;  // 存活人数
    int current = 0;  // 当前位置
    
    // 初始化数组
    for (int i = 0; i < n; i++) {
        people[i] = 1;  // 1表示存活
    }
    
    // 循环直到只剩一个人
    while (alive > 1) {
        // 如果当前位置的人还活着
        if (people[current] == 1) {
            count++;
            // 如果数到k，则淘汰该人
            if (count == k) {
                people[current] = 0;  // 0表示被淘汰
                alive--;
                count = 0;
            }
        }
        // 移动到下一个位置
        current = (current + 1) % n;
    }
    
    // 找到最后存活的人
    for (int i = 0; i < n; i++) {
        if (people[i] == 1) {
            return i + 1;  // 返回位置（从1开始计数）
        }
    }
    
    return -1;  // 不应该到达这里
}

int main() {
    int n, k;
    
    printf("请输入总人数n: ");
    scanf("%d", &n);
    printf("请输入报数k: ");
    scanf("%d", &k);
    
    if (n <= 0 || k <= 0) {
        printf("请输入正整数！\n");
        return 1;
    }
    
    int result = josephus(n, k);
    printf("最后存活的人的位置是: %d\n", result);
    
    return 0;
} 