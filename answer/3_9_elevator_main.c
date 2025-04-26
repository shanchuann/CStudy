#include <stdio.h>

int main() {
    int currentFloor, targetFloor;
    
    // 获取用户输入
    printf("请输入当前楼层（1-20）：");
    scanf("%d", &currentFloor);
    printf("请输入目标楼层（1-20）：");
    scanf("%d", &targetFloor);
    
    // 验证输入是否有效
    if (currentFloor < 1 || currentFloor > 20 || targetFloor < 1 || targetFloor > 20) {
        printf("楼层输入无效\n");
        return 0;
    }
    
    // 输出当前状态
    printf("当前楼层：%d\n", currentFloor);
    printf("目标楼层：%d\n", targetFloor);
    
    // 判断电梯运行状态
    if (targetFloor > currentFloor) {
        printf("电梯状态：向上运行\n");
    } else if (targetFloor < currentFloor) {
        printf("电梯状态：向下运行\n");
    } else {
        printf("电梯状态：停止\n");
    }
    
    return 0;
} 