#include <stdio.h>
#include <string.h>

// 定义信号灯状态枚举
typedef enum {
    RED,
    GREEN,
    YELLOW
} LightState;

// 定义信号灯结构体
typedef struct {
    LightState state;    // 当前状态
    int duration;        // 当前状态持续时间（秒）
    int redDuration;     // 红灯持续时间
    int greenDuration;   // 绿灯持续时间
    int yellowDuration;  // 黄灯持续时间
} TrafficLight;

// 初始化交通信号灯
void initTrafficLight(TrafficLight* light, int red, int green, int yellow) {
    light->state = RED;
    light->duration = 0;
    light->redDuration = red;
    light->greenDuration = green;
    light->yellowDuration = yellow;
}

// 获取当前状态名称
const char* getStateName(LightState state) {
    switch (state) {
        case RED: return "红灯";
        case GREEN: return "绿灯";
        case YELLOW: return "黄灯";
        default: return "未知";
    }
}

// 更新信号灯状态
void updateTrafficLight(TrafficLight* light) {
    light->duration++;
    
    switch (light->state) {
        case RED:
            if (light->duration >= light->redDuration) {
                light->state = GREEN;
                light->duration = 0;
            }
            break;
        case GREEN:
            if (light->duration >= light->greenDuration) {
                light->state = YELLOW;
                light->duration = 0;
            }
            break;
        case YELLOW:
            if (light->duration >= light->yellowDuration) {
                light->state = RED;
                light->duration = 0;
            }
            break;
    }
}

// 打印信号灯状态
void printTrafficLight(const TrafficLight* light) {
    printf("当前状态: %s\n", getStateName(light->state));
    printf("持续时间: %d秒\n", light->duration);
    printf("红灯时长: %d秒\n", light->redDuration);
    printf("绿灯时长: %d秒\n", light->greenDuration);
    printf("黄灯时长: %d秒\n", light->yellowDuration);
    printf("------------------------\n");
}

int main() {
    printf("交通信号灯状态机程序\n");
    printf("==================\n\n");

    // 创建交通信号灯实例
    TrafficLight light;
    initTrafficLight(&light, 30, 25, 5);  // 红灯30秒，绿灯25秒，黄灯5秒

    // 模拟信号灯运行
    printf("初始状态:\n");
    printTrafficLight(&light);
    printf("\n");

    // 模拟10次状态更新
    for (int i = 0; i < 10; i++) {
        printf("第%d次更新:\n", i + 1);
        updateTrafficLight(&light);
        printTrafficLight(&light);
        printf("\n");
    }

    return 0;
} 