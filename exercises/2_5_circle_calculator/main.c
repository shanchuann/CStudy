#include <stdio.h>
const float PI = 3.14159;

// 计算圆的周长
float calculate_circumference(float r) {
    return 2 * PI * r;
}

// 计算圆的面积
float calculate_area(float r) {
    return PI * r * r;
}