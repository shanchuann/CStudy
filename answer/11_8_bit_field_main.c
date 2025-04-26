#include <stdio.h>
#include <string.h>

// 紧凑的数据结构示例
struct CompactData {
    unsigned int flag1 : 1;    // 1位标志
    unsigned int flag2 : 1;    // 1位标志
    unsigned int value : 4;    // 4位值
    unsigned int type : 2;     // 2位类型
    unsigned int reserved : 24; // 保留位
};

// 数据操作函数
void set_flag1(struct CompactData* data, int value) {
    data->flag1 = value ? 1 : 0;
}

int get_flag1(const struct CompactData* data) {
    return data->flag1;
}

void set_flag2(struct CompactData* data, int value) {
    data->flag2 = value ? 1 : 0;
}

int get_flag2(const struct CompactData* data) {
    return data->flag2;
}

void set_value(struct CompactData* data, int value) {
    data->value = value & 0x0F; // 确保值不超过4位
}

int get_value(const struct CompactData* data) {
    return data->value;
}

void set_type(struct CompactData* data, int type) {
    data->type = type & 0x03; // 确保类型不超过2位
}

int get_type(const struct CompactData* data) {
    return data->type;
}

// 打印数据结构内容
void print_data(const struct CompactData* data) {
    printf("数据结构内容:\n");
    printf("flag1: %d\n", get_flag1(data));
    printf("flag2: %d\n", get_flag2(data));
    printf("value: %d\n", get_value(data));
    printf("type: %d\n", get_type(data));
    printf("结构体大小: %zu 字节\n", sizeof(struct CompactData));
}

// 测试函数
void test_bit_field() {
    struct CompactData data = {0}; // 初始化所有位为0
    
    printf("初始状态:\n");
    print_data(&data);
    
    // 测试设置和获取标志位
    set_flag1(&data, 1);
    set_flag2(&data, 0);
    printf("\n设置标志位后:\n");
    print_data(&data);
    
    // 测试设置和获取值
    set_value(&data, 12); // 设置4位值
    printf("\n设置值后:\n");
    print_data(&data);
    
    // 测试设置和获取类型
    set_type(&data, 3); // 设置2位类型
    printf("\n设置类型后:\n");
    print_data(&data);
    
    // 测试边界值
    set_value(&data, 16); // 尝试设置超出4位的值
    printf("\n尝试设置超出范围的值后:\n");
    print_data(&data);
}

int main() {
    printf("开始测试位域数据结构...\n");
    test_bit_field();
    printf("\n位域数据结构测试完成！\n");
    return 0;
} 