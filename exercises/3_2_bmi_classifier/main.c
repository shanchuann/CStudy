#include <stdio.h>
#include "../testwork/test_framework.h"

// 全局变量定义
char current_output[100];
char current_input[100];

// BMI分类函数
void classify_bmi(double weight, double height) {
    // 计算BMI
    double bmi = weight / (height * height);
    
    // 根据BMI值进行分类
    if (bmi < 18.5) {
        printf("Underweight");
    } else if (bmi < 25.0) {
        printf("Normal weight");
    } else if (bmi < 30.0) {
        printf("Overweight");
    } else {
        printf("Obese");
    }
}

// int main() {
//     float height, weight;
//     float bmi;
//     char category[20];
    
//     // 获取用户输入
//     printf("请输入身高（米）：");
//     scanf("%f", &height);
//     printf("请输入体重（千克）：");
//     scanf("%f", &weight);
    
//     // 计算BMI
//     bmi = weight / (height * height);
    
//     // 判断肥胖等级
//     if (bmi < 18.5) {
//         strcpy(category, "体重过轻");
//     } else if (bmi < 24) {
//         strcpy(category, "体重正常");
//     } else if (bmi < 28) {
//         strcpy(category, "体重过重");
//     } else {
//         strcpy(category, "肥胖");
//     }
    
//     // 输出结果
//     printf("您的BMI值为：%.1f，属于：%s\n", bmi, category);
    
//     return 0;
// } 