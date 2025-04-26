#include <stdio.h>

// 定义函数指针类型
typedef void (*CallbackFunc)(int);

// 定义事件类型
typedef enum {
    EVENT_START,
    EVENT_PROGRESS,
    EVENT_COMPLETE,
    EVENT_ERROR
} EventType;

// 定义事件处理函数
void onStart(int data) {
    printf("开始处理，数据：%d\n", data);
}

void onProgress(int data) {
    printf("处理进度：%d%%\n", data);
}

void onComplete(int data) {
    printf("处理完成，结果：%d\n", data);
}

void onError(int data) {
    printf("发生错误，错误码：%d\n", data);
}

// 定义事件处理器结构体
typedef struct {
    CallbackFunc start;
    CallbackFunc progress;
    CallbackFunc complete;
    CallbackFunc error;
} EventHandler;

// 模拟处理过程
void processData(int data, EventHandler* handler) {
    // 触发开始事件
    if (handler->start) {
        handler->start(data);
    }
    
    // 模拟进度更新
    for (int i = 0; i <= 100; i += 20) {
        if (handler->progress) {
            handler->progress(i);
        }
        // 模拟处理延迟
        for (int j = 0; j < 1000000; j++);
    }
    
    // 触发完成事件
    if (handler->complete) {
        handler->complete(data * 2);  // 模拟处理结果
    }
}

// 测试函数
void testCallback() {
    // 创建事件处理器
    EventHandler handler = {
        .start = onStart,
        .progress = onProgress,
        .complete = onComplete,
        .error = onError
    };
    
    printf("测试用例1：正常处理流程\n");
    processData(42, &handler);
    printf("\n");
    
    // 测试部分回调函数为空的情况
    printf("测试用例2：部分回调函数为空\n");
    EventHandler partialHandler = {
        .start = onStart,
        .progress = NULL,
        .complete = onComplete,
        .error = NULL
    };
    processData(100, &partialHandler);
}

int main() {
    testCallback();
    return 0;
} 