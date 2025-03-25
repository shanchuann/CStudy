#include <stdio.h>
#include <string.h>

// 通用交换函数（使用void指针）
void swap(void* a, void* b, size_t size) {
    // 创建临时缓冲区
    char* temp = (char*)malloc(size);
    if (!temp) return;
    
    // 复制第一个元素到临时缓冲区
    memcpy(temp, a, size);
    // 复制第二个元素到第一个位置
    memcpy(a, b, size);
    // 复制临时缓冲区到第二个位置
    memcpy(b, temp, size);
    
    // 释放临时缓冲区
    free(temp);
}

// 测试整数交换
void testIntSwap() {
    int a = 5, b = 10;
    printf("交换前：a = %d, b = %d\n", a, b);
    swap(&a, &b, sizeof(int));
    printf("交换后：a = %d, b = %d\n", a, b);
}

// 测试浮点数交换
void testFloatSwap() {
    float a = 3.14f, b = 2.718f;
    printf("交换前：a = %.2f, b = %.2f\n", a, b);
    swap(&a, &b, sizeof(float));
    printf("交换后：a = %.2f, b = %.2f\n", a, b);
}

// 测试字符串交换
void testStringSwap() {
    char str1[] = "Hello";
    char str2[] = "World";
    printf("交换前：str1 = %s, str2 = %s\n", str1, str2);
    swap(str1, str2, strlen(str1) + 1);
    printf("交换后：str1 = %s, str2 = %s\n", str1, str2);
}

// 测试结构体交换
struct Point {
    int x;
    int y;
};

void testStructSwap() {
    struct Point p1 = {1, 2};
    struct Point p2 = {3, 4};
    printf("交换前：p1(%d,%d), p2(%d,%d)\n", p1.x, p1.y, p2.x, p2.y);
    swap(&p1, &p2, sizeof(struct Point));
    printf("交换后：p1(%d,%d), p2(%d,%d)\n", p1.x, p1.y, p2.x, p2.y);
}

int main() {
    printf("测试整数交换：\n");
    testIntSwap();
    printf("\n");
    
    printf("测试浮点数交换：\n");
    testFloatSwap();
    printf("\n");
    
    printf("测试字符串交换：\n");
    testStringSwap();
    printf("\n");
    
    printf("测试结构体交换：\n");
    testStructSwap();
    
    return 0;
} 