# 练习11.7：多线程素数计算

## 题目描述
使用pthread库实现多线程计算指定范围内的素数，提高计算效率。

## 要求
1. 使用pthread创建多个工作线程
2. 实现任务分配机制
3. 实现线程同步
4. 统计计算时间和结果
5. 处理线程安全的数据访问

## 示例代码框架
```c
#include <pthread.h>

typedef struct {
    long start;          // 起始数字
    long end;           // 结束数字
    long* primes;       // 素数数组
    int* prime_count;   // 素数计数
    pthread_mutex_t* mutex;  // 互斥锁
} ThreadArgs;

// 判断一个数是否为素数
int is_prime(long n);

// 线程函数
void* prime_worker(void* arg);

// 主函数
void find_primes(long start, long end, int num_threads);
```

## 提示
1. 使用互斥锁保护共享资源
2. 实现负载均衡
3. 考虑线程创建开销
4. 处理大数计算

## 扩展要求
1. 实现动态任务分配
2. 添加进度显示
3. 实现结果排序
4. 添加性能分析
5. 实现线程池 