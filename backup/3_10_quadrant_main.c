#include <stdio.h>

int main() {
    float x, y;
    
    // 获取用户输入
    printf("请输入x坐标：");
    scanf("%f", &x);
    printf("请输入y坐标：");
    scanf("%f", &y);
    
    // 判断坐标点位置
    if (x == 0 || y == 0) {
        printf("该点位于坐标轴上\n");
    } else if (x > 0 && y > 0) {
        printf("该点位于第一象限\n");
    } else if (x < 0 && y > 0) {
        printf("该点位于第二象限\n");
    } else if (x < 0 && y < 0) {
        printf("该点位于第三象限\n");
    } else {
        printf("该点位于第四象限\n");
    }
    
    return 0;
} 