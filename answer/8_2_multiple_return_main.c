#include <stdio.h>

// 计算数组的最大值、最小值和平均值
void calculateStats(const int* arr, int size, int* max, int* min, double* avg) {
    if (size <= 0) {
        *max = 0;
        *min = 0;
        *avg = 0.0;
        return;
    }
    
    // 初始化最大值和最小值为第一个元素
    *max = arr[0];
    *min = arr[0];
    int sum = 0;
    
    // 遍历数组计算统计值
    for (int i = 0; i < size; i++) {
        if (arr[i] > *max) *max = arr[i];
        if (arr[i] < *min) *min = arr[i];
        sum += arr[i];
    }
    
    // 计算平均值
    *avg = (double)sum / size;
}

// 计算二次方程的根
void solveQuadratic(double a, double b, double c, 
                   double* x1, double* x2, int* numRoots) {
    double discriminant = b * b - 4 * a * c;
    
    if (a == 0) {
        *numRoots = 0;  // 不是二次方程
        return;
    }
    
    if (discriminant > 0) {
        *numRoots = 2;
        *x1 = (-b + sqrt(discriminant)) / (2 * a);
        *x2 = (-b - sqrt(discriminant)) / (2 * a);
    } else if (discriminant == 0) {
        *numRoots = 1;
        *x1 = *x2 = -b / (2 * a);
    } else {
        *numRoots = 0;  // 无实根
    }
}

int main() {
    // 测试数组统计函数
    int arr[] = {1, 2, 3, 4, 5};
    int size = 5;
    int max, min;
    double avg;
    
    calculateStats(arr, size, &max, &min, &avg);
    printf("数组统计结果：\n");
    printf("最大值：%d\n", max);
    printf("最小值：%d\n", min);
    printf("平均值：%.2f\n", avg);
    
    // 测试二次方程求解函数
    double a = 1, b = -5, c = 6;
    double x1, x2;
    int numRoots;
    
    solveQuadratic(a, b, c, &x1, &x2, &numRoots);
    printf("\n二次方程 %.2fx² + %.2fx + %.2f = 0 的解：\n", a, b, c);
    if (numRoots == 2) {
        printf("x1 = %.2f, x2 = %.2f\n", x1, x2);
    } else if (numRoots == 1) {
        printf("x = %.2f（重根）\n", x1);
    } else {
        printf("无实根\n");
    }
    
    return 0;
} 