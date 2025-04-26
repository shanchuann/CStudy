#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <math.h>

#define MAX_THREADS 4
#define MAX_NUMBER 1000000

// 线程参数结构
typedef struct {
    long start;          // 起始数字
    long end;           // 结束数字
    long* primes;       // 素数数组
    int* prime_count;   // 素数计数
    pthread_mutex_t* mutex;  // 互斥锁
} ThreadArgs;

// 判断一个数是否为素数
int is_prime(long n) {
    if (n <= 1) return 0;
    if (n <= 3) return 1;
    if (n % 2 == 0) return 0;
    
    long sqrt_n = (long)sqrt(n);
    for (long i = 3; i <= sqrt_n; i += 2) {
        if (n % i == 0) return 0;
    }
    return 1;
}

// 线程函数
void* prime_worker(void* arg) {
    ThreadArgs* args = (ThreadArgs*)arg;
    
    for (long i = args->start; i <= args->end; i++) {
        if (is_prime(i)) {
            pthread_mutex_lock(args->mutex);
            args->primes[*args->prime_count] = i;
            (*args->prime_count)++;
            pthread_mutex_unlock(args->mutex);
        }
    }
    
    return NULL;
}

// 主函数
void find_primes(long start, long end, int num_threads) {
    pthread_t threads[MAX_THREADS];
    ThreadArgs args[MAX_THREADS];
    long* primes = malloc((end - start + 1) * sizeof(long));
    int prime_count = 0;
    pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
    
    // 计算每个线程的工作范围
    long range = (end - start + 1) / num_threads;
    
    // 创建线程
    for (int i = 0; i < num_threads; i++) {
        args[i].start = start + i * range;
        args[i].end = (i == num_threads - 1) ? end : start + (i + 1) * range - 1;
        args[i].primes = primes;
        args[i].prime_count = &prime_count;
        args[i].mutex = &mutex;
        
        pthread_create(&threads[i], NULL, prime_worker, &args[i]);
    }
    
    // 等待所有线程完成
    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }
    
    // 打印结果
    printf("找到 %d 个素数:\n", prime_count);
    for (int i = 0; i < prime_count; i++) {
        printf("%ld ", primes[i]);
        if ((i + 1) % 10 == 0) printf("\n");
    }
    printf("\n");
    
    // 清理资源
    free(primes);
    pthread_mutex_destroy(&mutex);
}

int main() {
    clock_t start = clock();
    
    printf("开始多线程素数计算...\n");
    find_primes(1, MAX_NUMBER, MAX_THREADS);
    
    clock_t end = clock();
    double time_spent = (double)(end - start) / CLOCKS_PER_SEC;
    printf("\n计算用时: %.2f 秒\n", time_spent);
    
    return 0;
} 