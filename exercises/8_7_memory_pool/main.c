#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BLOCK_SIZE 1024
#define MAX_BLOCKS 10

// 内存块结构
typedef struct {
    void* data;          // 数据区域
    size_t size;         // 块大小
    int is_used;         // 使用状态
} MemoryBlock;

// 内存池结构
typedef struct {
    MemoryBlock blocks[MAX_BLOCKS];  // 内存块数组
    size_t total_size;               // 总大小
    size_t used_size;                // 已使用大小
} MemoryPool;

// 初始化内存池
MemoryPool* createMemoryPool(size_t total_size) {
    MemoryPool* pool = (MemoryPool*)malloc(sizeof(MemoryPool));
    if (!pool) {
        printf("内存池创建失败！\n");
        return NULL;
    }
    
    // 初始化内存池
    pool->total_size = total_size;
    pool->used_size = 0;
    
    // 分配内存块
    for (int i = 0; i < MAX_BLOCKS; i++) {
        pool->blocks[i].data = malloc(BLOCK_SIZE);
        if (!pool->blocks[i].data) {
            printf("内存块 %d 分配失败！\n", i);
            // 释放已分配的内存
            for (int j = 0; j < i; j++) {
                free(pool->blocks[j].data);
            }
            free(pool);
            return NULL;
        }
        pool->blocks[i].size = BLOCK_SIZE;
        pool->blocks[i].is_used = 0;
    }
    
    return pool;
}

// 从内存池分配内存
void* poolAlloc(MemoryPool* pool, size_t size) {
    if (!pool || size == 0) return NULL;
    
    // 查找可用内存块
    for (int i = 0; i < MAX_BLOCKS; i++) {
        if (!pool->blocks[i].is_used && pool->blocks[i].size >= size) {
            pool->blocks[i].is_used = 1;
            pool->used_size += size;
            return pool->blocks[i].data;
        }
    }
    
    printf("没有足够的内存块！\n");
    return NULL;
}

// 释放内存到内存池
void poolFree(MemoryPool* pool, void* ptr) {
    if (!pool || !ptr) return;
    
    // 查找对应的内存块
    for (int i = 0; i < MAX_BLOCKS; i++) {
        if (pool->blocks[i].data == ptr) {
            pool->blocks[i].is_used = 0;
            pool->used_size -= pool->blocks[i].size;
            memset(pool->blocks[i].data, 0, pool->blocks[i].size);
            return;
        }
    }
    
    printf("无效的内存指针！\n");
}

// 释放内存池
void destroyMemoryPool(MemoryPool* pool) {
    if (!pool) return;
    
    // 释放所有内存块
    for (int i = 0; i < MAX_BLOCKS; i++) {
        free(pool->blocks[i].data);
    }
    free(pool);
}

// 打印内存池状态
void printPoolStatus(MemoryPool* pool) {
    if (!pool) return;
    
    printf("\n内存池状态：\n");
    printf("总大小：%zu 字节\n", pool->total_size);
    printf("已使用：%zu 字节\n", pool->used_size);
    printf("使用率：%.2f%%\n", (float)pool->used_size / pool->total_size * 100);
    
    printf("\n内存块状态：\n");
    for (int i = 0; i < MAX_BLOCKS; i++) {
        printf("块 %d: %s (大小: %zu 字节)\n", 
               i, 
               pool->blocks[i].is_used ? "已使用" : "空闲",
               pool->blocks[i].size);
    }
}

// 测试函数
void testMemoryPool() {
    printf("创建内存池...\n");
    MemoryPool* pool = createMemoryPool(MAX_BLOCKS * BLOCK_SIZE);
    if (!pool) {
        printf("内存池创建失败！\n");
        return;
    }
    
    printPoolStatus(pool);
    
    printf("\n分配内存...\n");
    char* str1 = (char*)poolAlloc(pool, 100);
    if (str1) {
        strcpy(str1, "Hello, Memory Pool!");
        printf("分配的内存内容：%s\n", str1);
    }
    
    printPoolStatus(pool);
    
    printf("\n再次分配内存...\n");
    char* str2 = (char*)poolAlloc(pool, 200);
    if (str2) {
        strcpy(str2, "This is another allocation.");
        printf("分配的内存内容：%s\n", str2);
    }
    
    printPoolStatus(pool);
    
    printf("\n释放第一个内存块...\n");
    poolFree(pool, str1);
    
    printPoolStatus(pool);
    
    printf("\n释放内存池...\n");
    destroyMemoryPool(pool);
}

int main() {
    testMemoryPool();
    return 0;
} 