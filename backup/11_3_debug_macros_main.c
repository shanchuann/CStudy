#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// 调试级别定义
#define DEBUG_LEVEL_NONE    0
#define DEBUG_LEVEL_ERROR   1
#define DEBUG_LEVEL_WARN    2
#define DEBUG_LEVEL_INFO    3
#define DEBUG_LEVEL_DEBUG   4

// 当前调试级别
#ifndef DEBUG_LEVEL
#define DEBUG_LEVEL DEBUG_LEVEL_INFO
#endif

// 获取当前时间字符串
#define GET_TIME_STR() \
    do { \
        time_t now; \
        time(&now); \
        strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", localtime(&now)); \
    } while(0)

// 调试宏定义
#define DEBUG_PRINT(level, fmt, ...) \
    do { \
        if (level <= DEBUG_LEVEL) { \
            char timeStr[26]; \
            GET_TIME_STR(); \
            fprintf(stderr, "[%s][%s:%d] " fmt "\n", \
                    timeStr, __FILE__, __LINE__, ##__VA_ARGS__); \
        } \
    } while(0)

// 不同级别的调试宏
#define DEBUG_ERROR(fmt, ...) DEBUG_PRINT(DEBUG_LEVEL_ERROR, "ERROR: " fmt, ##__VA_ARGS__)
#define DEBUG_WARN(fmt, ...)  DEBUG_PRINT(DEBUG_LEVEL_WARN,  "WARN:  " fmt, ##__VA_ARGS__)
#define DEBUG_INFO(fmt, ...)  DEBUG_PRINT(DEBUG_LEVEL_INFO,  "INFO:  " fmt, ##__VA_ARGS__)
#define DEBUG_DEBUG(fmt, ...) DEBUG_PRINT(DEBUG_LEVEL_DEBUG, "DEBUG: " fmt, ##__VA_ARGS__)

// 断言宏
#define ASSERT(condition) \
    do { \
        if (!(condition)) { \
            DEBUG_ERROR("Assertion failed: %s", #condition); \
            abort(); \
        } \
    } while(0)

// 内存分配检查宏
#define SAFE_MALLOC(ptr, size) \
    do { \
        ptr = malloc(size); \
        if (!ptr) { \
            DEBUG_ERROR("Memory allocation failed: %s", #ptr); \
            exit(1); \
        } \
        DEBUG_DEBUG("Memory allocated: %s = %p", #ptr, (void*)ptr); \
    } while(0)

// 函数入口和出口宏
#define FUNCTION_ENTRY() DEBUG_DEBUG("Entering function: %s", __FUNCTION__)
#define FUNCTION_EXIT()  DEBUG_DEBUG("Exiting function: %s", __FUNCTION__)

// 示例函数
void exampleFunction(int value) {
    FUNCTION_ENTRY();
    
    DEBUG_INFO("Processing value: %d", value);
    
    if (value < 0) {
        DEBUG_WARN("Negative value received: %d", value);
    }
    
    int* ptr;
    SAFE_MALLOC(ptr, sizeof(int));
    *ptr = value;
    
    DEBUG_DEBUG("Value stored at %p: %d", (void*)ptr, *ptr);
    
    free(ptr);
    DEBUG_DEBUG("Memory freed: %p", (void*)ptr);
    
    FUNCTION_EXIT();
}

int main() {
    printf("调试宏演示程序\n");
    printf("==============\n\n");
    
    // 测试不同级别的调试信息
    DEBUG_ERROR("这是一条错误信息");
    DEBUG_WARN("这是一条警告信息");
    DEBUG_INFO("这是一条信息");
    DEBUG_DEBUG("这是一条调试信息");
    
    printf("\n测试函数调用：\n");
    exampleFunction(42);
    
    printf("\n测试断言：\n");
    int x = 10;
    ASSERT(x > 0);  // 这个断言会通过
    printf("断言测试通过！\n");
    
    printf("\n测试内存分配：\n");
    int* ptr;
    SAFE_MALLOC(ptr, sizeof(int));
    *ptr = 100;
    printf("分配的内存值：%d\n", *ptr);
    free(ptr);
    
    return 0;
} 