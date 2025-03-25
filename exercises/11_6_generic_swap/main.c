#include <stdio.h>
#include <string.h>

// 基本SWAP宏实现
#define SWAP(x, y) do { \
    typeof(x) temp = x; \
    x = y;             \
    y = temp;          \
} while(0)

// 无临时变量的SWAP宏实现（仅适用于整数）
#define SWAP_XOR(x, y) do { \
    x = x ^ y;             \
    y = x ^ y;             \
    x = x ^ y;             \
} while(0)

// 结构体定义
struct Point {
    int x;
    int y;
};

// 测试函数
void test_swap() {
    // 测试整数交换
    int a = 10, b = 20;
    printf("交换前: a = %d, b = %d\n", a, b);
    SWAP(a, b);
    printf("交换后: a = %d, b = %d\n", a, b);
    
    // 测试浮点数交换
    float f1 = 1.5f, f2 = 2.5f;
    printf("\n交换前: f1 = %.1f, f2 = %.1f\n", f1, f2);
    SWAP(f1, f2);
    printf("交换后: f1 = %.1f, f2 = %.1f\n", f1, f2);
    
    // 测试字符交换
    char c1 = 'A', c2 = 'B';
    printf("\n交换前: c1 = %c, c2 = %c\n", c1, c2);
    SWAP(c1, c2);
    printf("交换后: c1 = %c, c2 = %c\n", c1, c2);
    
    // 测试结构体交换
    struct Point p1 = {1, 2}, p2 = {3, 4};
    printf("\n交换前: p1 = (%d,%d), p2 = (%d,%d)\n", 
           p1.x, p1.y, p2.x, p2.y);
    SWAP(p1, p2);
    printf("交换后: p1 = (%d,%d), p2 = (%d,%d)\n", 
           p1.x, p1.y, p2.x, p2.y);
    
    // 测试无临时变量的整数交换
    int x = 5, y = 10;
    printf("\nXOR交换前: x = %d, y = %d\n", x, y);
    SWAP_XOR(x, y);
    printf("XOR交换后: x = %d, y = %d\n", x, y);
}

int main() {
    printf("开始测试泛型交换函数...\n");
    test_swap();
    printf("\n泛型交换函数测试完成！\n");
    return 0;
} 