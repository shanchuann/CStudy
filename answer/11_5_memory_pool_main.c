#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

// 内存块头部结构
typedef struct BlockHeader {
    struct BlockHeader* next;  // 指向下一个空闲块
    int is_free;              // 是否空闲
} BlockHeader;

// 内存池结构
typedef struct {
    void* memory;             // 内存池起始地址
    size_t block_size;        // 每个块的大小
    size_t num_blocks;        // 块的数量
    BlockHeader* free_list;   // 空闲块链表
} MemoryPool;

// 初始化内存池
MemoryPool* memory_pool_init(size_t block_size, size_t num_blocks) {
    // 计算总内存大小（包括头部）
    size_t total_size = (block_size + sizeof(BlockHeader)) * num_blocks;
    
    // 分配内存
    MemoryPool* pool = (MemoryPool*)malloc(sizeof(MemoryPool));
    if (!pool) return NULL;
    
    pool->memory = malloc(total_size);
    if (!pool->memory) {
        free(pool);
        return NULL;
    }
    
    pool->block_size = block_size;
    pool->num_blocks = num_blocks;
    
    // 初始化空闲块链表
    pool->free_list = (BlockHeader*)pool->memory;
    BlockHeader* current = pool->free_list;
    
    for (size_t i = 0; i < num_blocks; i++) {
        current->next = (BlockHeader*)((char*)current + block_size + sizeof(BlockHeader));
        current->is_free = 1;
        current = current->next;
    }
    current->next = NULL;
    
    return pool;
}

// 分配一个内存块
void* memory_pool_alloc(MemoryPool* pool) {
    if (!pool || !pool->free_list) return NULL;
    
    BlockHeader* block = pool->free_list;
    pool->free_list = block->next;
    block->is_free = 0;
    
    return (void*)((char*)block + sizeof(BlockHeader));
}

// 释放一个内存块
void memory_pool_free(MemoryPool* pool, void* ptr) {
    if (!pool || !ptr) return;
    
    BlockHeader* block = (BlockHeader*)((char*)ptr - sizeof(BlockHeader));
    if (!block->is_free) {
        block->is_free = 1;
        block->next = pool->free_list;
        pool->free_list = block;
    }
}

// 销毁内存池
void memory_pool_destroy(MemoryPool* pool) {
    if (pool) {
        free(pool->memory);
        free(pool);
    }
}

// 测试函数
void test_memory_pool() {
    // 创建内存池：块大小为32字节，共10个块
    MemoryPool* pool = memory_pool_init(32, 10);
    assert(pool != NULL);
    
    // 测试分配
    void* ptr1 = memory_pool_alloc(pool);
    void* ptr2 = memory_pool_alloc(pool);
    assert(ptr1 != NULL && ptr2 != NULL);
    
    // 使用内存
    strcpy(ptr1, "Hello");
    strcpy(ptr2, "World");
    
    // 测试释放
    memory_pool_free(pool, ptr1);
    memory_pool_free(pool, ptr2);
    
    // 测试重用
    void* ptr3 = memory_pool_alloc(pool);
    assert(ptr3 != NULL);
    
    // 清理
    memory_pool_destroy(pool);
}

int main() {
    printf("开始测试内存池...\n");
    test_memory_pool();
    printf("内存池测试完成！\n");
    return 0;
} 