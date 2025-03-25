#include <stdio.h>

// 定义联合体用于检测大小端
typedef union {
    int i;      // 4字节整数
    char c[4];  // 4个字节的字符数组
} EndianTest;

// 检测系统大小端
void checkEndian() {
    EndianTest test;
    test.i = 0x12345678;  // 设置一个测试值
    
    printf("测试值：0x12345678\n");
    printf("内存中的字节顺序：\n");
    for(int i = 0; i < 4; i++) {
        printf("字节 %d: 0x%02X\n", i, test.c[i]);
    }
    
    // 判断大小端
    if(test.c[0] == 0x78) {
        printf("\n系统是小端序（Little Endian）\n");
    } else if(test.c[0] == 0x12) {
        printf("\n系统是大端序（Big Endian）\n");
    } else {
        printf("\n无法确定系统字节序\n");
    }
}

// 显示字节序的详细信息
void showEndianDetails() {
    EndianTest test;
    test.i = 0x12345678;
    
    printf("\n字节序详细信息：\n");
    printf("----------------------------------------\n");
    printf("内存地址\t字节值\t含义\n");
    printf("----------------------------------------\n");
    
    for(int i = 0; i < 4; i++) {
        printf("%p\t0x%02X\t", (void*)&test.c[i], test.c[i]);
        switch(i) {
            case 0:
                printf("最低有效字节（LSB）");
                break;
            case 3:
                printf("最高有效字节（MSB）");
                break;
            default:
                printf("中间字节");
                break;
        }
        printf("\n");
    }
}

// 显示不同数据类型的字节序
void showDataTypeEndian() {
    printf("\n不同数据类型的字节序：\n");
    printf("----------------------------------------\n");
    
    // 测试short类型
    union {
        short s;
        char c[2];
    } shortTest;
    shortTest.s = 0x1234;
    printf("short (2字节): ");
    for(int i = 0; i < 2; i++) {
        printf("0x%02X ", shortTest.c[i]);
    }
    printf("\n");
    
    // 测试int类型
    EndianTest intTest;
    intTest.i = 0x12345678;
    printf("int (4字节): ");
    for(int i = 0; i < 4; i++) {
        printf("0x%02X ", intTest.c[i]);
    }
    printf("\n");
    
    // 测试long类型
    union {
        long l;
        char c[4];
    } longTest;
    longTest.l = 0x12345678;
    printf("long (4字节): ");
    for(int i = 0; i < 4; i++) {
        printf("0x%02X ", longTest.c[i]);
    }
    printf("\n");
}

int main() {
    printf("系统字节序检测程序\n");
    printf("==================\n\n");
    
    // 检测系统大小端
    checkEndian();
    
    // 显示详细信息
    showEndianDetails();
    
    // 显示不同数据类型的字节序
    showDataTypeEndian();
    
    return 0;
} 