#include <stdio.h>
#include "../testwork/test_framework.h"

// 全局变量定义
char current_output[100];
char current_input[100];

// 电梯状态
typedef struct {
    int current_floor;  // 当前楼层
    int target_floor;   // 目标楼层
    int direction;      // 运行方向：1上行，-1下行，0停止
} Elevator;

// 初始化电梯
Elevator elevator = {1, 1, 0};

// 处理电梯请求
void process_request(int floor) {
    // 检查楼层是否有效
    if (floor < 1 || floor > 20) {
        sprintf(current_output, "Invalid floor");
        return;
    }
    
    // 设置目标楼层
    elevator.target_floor = floor;
    
    // 确定运行方向
    if (floor > elevator.current_floor) {
        elevator.direction = 1;  // 上行
    } else if (floor < elevator.current_floor) {
        elevator.direction = -1; // 下行
    } else {
        elevator.direction = 0;  // 停止
    }
    
    // 模拟电梯运行
    while (elevator.current_floor != elevator.target_floor) {
        elevator.current_floor += elevator.direction;
    }
    
    // 到达目标楼层后停止
    elevator.direction = 0;
    
    // 格式化输出
    sprintf(current_output, "Current floor: %d", elevator.current_floor);
}

// int main() {
//     int currentFloor, targetFloor;
    
//     // 获取用户输入
//     printf("请输入当前楼层（1-20）：");
//     scanf("%d", &currentFloor);
//     printf("请输入目标楼层（1-20）：");
//     scanf("%d", &targetFloor);
    
//     // 验证输入是否有效
//     if (currentFloor < 1 || currentFloor > 20 || targetFloor < 1 || targetFloor > 20) {
//         printf("楼层输入无效\n");
//         return 0;
//     }
    
//     // 输出当前状态
//     printf("当前楼层：%d\n", currentFloor);
//     printf("目标楼层：%d\n", targetFloor);
    
//     // 判断电梯运行状态
//     if (targetFloor > currentFloor) {
//         printf("电梯状态：向上运行\n");
//     } else if (targetFloor < currentFloor) {
//         printf("电梯状态：向下运行\n");
//     } else {
//         printf("电梯状态：停止\n");
//     }
    
//     return 0;
// } 