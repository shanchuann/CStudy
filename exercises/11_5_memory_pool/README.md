# 练习11.5：内存池管理

## 题目描述
实现一个固定大小块的内存池管理器。内存池应该能够高效地分配和释放固定大小的内存块，避免频繁的系统内存分配。

## 要求
1. 实现内存池的初始化函数，指定块大小和块数量
2. 实现内存分配函数，从池中获取一个内存块
3. 实现内存释放函数，将内存块归还给池
4. 实现内存池销毁函数，释放所有资源
5. 添加错误处理机制

## 示例代码框架
```c
typedef struct {
    void* memory;        // 内存池起始地址
    size_t block_size;   // 每个块的大小
    size_t num_blocks;   // 块的数量
    void* free_list;     // 空闲块链表
} MemoryPool;

// 初始化内存池
MemoryPool* memory_pool_init(size_t block_size, size_t num_blocks);

// 分配一个内存块
void* memory_pool_alloc(MemoryPool* pool);

// 释放一个内存块
void memory_pool_free(MemoryPool* pool, void* ptr);

// 销毁内存池
void memory_pool_destroy(MemoryPool* pool);
```

## 提示
1. 使用链表管理空闲块
2. 考虑内存对齐
3. 实现线程安全（可选）
4. 添加内存泄漏检测（可选）

## 扩展要求
1. 实现可变大小块的内存池
2. 添加内存碎片整理功能
3. 实现内存使用统计
4. 添加内存池状态监控 