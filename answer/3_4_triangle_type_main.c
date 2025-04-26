#include <stdio.h>
#include <math.h>

int main() {
    float a, b, c;
    
    // 获取用户输入
    printf("请输入三条边的长度，用空格分隔：");
    scanf("%f %f %f", &a, &b, &c);
    
    // 判断是否能构成三角形
    if (a + b <= c || b + c <= a || a + c <= b) {
        printf("这三条边不能构成三角形\n");
        return 0;
    }
    
    // 判断三角形类型
    if (a == b && b == c) {
        printf("这是一个等边三角形\n");
    } else if (a == b || b == c || a == c) {
        printf("这是一个等腰三角形\n");
    } else {
        // 判断是否为直角三角形
        float max = a;
        if (b > max) max = b;
        if (c > max) max = c;
        
        float sum = a * a + b * b + c * c - max * max;
        if (fabs(sum - max * max) < 0.0001) {
            printf("这是一个直角三角形\n");
        } else {
            printf("这是一个普通三角形\n");
        }
    }
    
    return 0;
} 