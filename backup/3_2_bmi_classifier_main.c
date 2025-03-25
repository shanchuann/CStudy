#include <stdio.h>
#include <string.h>

int main() {
    float height, weight;
    float bmi;
    char category[20];
    
    // 获取用户输入
    printf("请输入身高（米）：");
    scanf("%f", &height);
    printf("请输入体重（千克）：");
    scanf("%f", &weight);
    
    // 计算BMI
    bmi = weight / (height * height);
    
    // 判断肥胖等级
    if (bmi < 18.5) {
        strcpy(category, "体重过轻");
    } else if (bmi < 24) {
        strcpy(category, "体重正常");
    } else if (bmi < 28) {
        strcpy(category, "体重过重");
    } else {
        strcpy(category, "肥胖");
    }
    
    // 输出结果
    printf("您的BMI值为：%.1f，属于：%s\n", bmi, category);
    
    return 0;
} 