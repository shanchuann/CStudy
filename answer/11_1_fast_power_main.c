 #include <stdio.h>
#include <stdlib.h>

// 使用位运算实现快速幂算法
long long fastPower(long long base, int exponent) {
    long long result = 1;
    
    // 处理负指数的情况
    if (exponent < 0) {
        base = 1 / base;
        exponent = -exponent;
    }
    
    // 使用位运算进行快速幂计算
    while (exponent) {
        // 如果当前位为1，则乘以base
        if (exponent & 1) {
            result *= base;
        }
        // base平方
        base *= base;
        // 右移一位
        exponent >>= 1;
    }
    
    return result;
}

// 测试函数
void testFastPower() {
    // 测试用例1：正数指数
    printf("测试用例1：2^10 = %lld\n", fastPower(2, 10));
    
    // 测试用例2：零指数
    printf("测试用例2：5^0 = %lld\n", fastPower(5, 0));
    
    // 测试用例3：负数指数
    printf("测试用例3：2^-3 = %lld\n", fastPower(2, -3));
    
    // 测试用例4：大数
    printf("测试用例4：3^20 = %lld\n", fastPower(3, 20));
}

int main() {
    printf("快速幂算法演示\n");
    printf("==============\n\n");
    
    // 运行测试用例
    testFastPower();
    
    // 用户交互部分
    printf("\n请输入底数和指数（用空格分隔）：");
    long long base;
    int exponent;
    
    while (scanf("%lld %d", &base, &exponent) == 2) {
        long long result = fastPower(base, exponent);
        printf("%lld^%d = %lld\n", base, exponent, result);
        printf("\n请输入底数和指数（用空格分隔，输入非数字退出）：");
    }
    
    return 0;
}