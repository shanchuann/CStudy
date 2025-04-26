#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 指令类型
typedef enum {
    HALT,
    LOAD,
    STORE,
    ADD,
    SUB,
    MUL,
    DIV,
    JMP,
    JZ,
    CALL,
    RET
} OpCode;

// 指令结构
typedef struct {
    OpCode opcode;
    int operand1;
    int operand2;
} Instruction;

// 虚拟机状态
typedef struct {
    int registers[8];    // 通用寄存器
    int pc;             // 程序计数器
    int sp;             // 栈指针
    int* memory;        // 内存
    int memory_size;    // 内存大小
} VM;

// 初始化虚拟机
void vm_init(VM* vm, int memory_size) {
    vm->memory_size = memory_size;
    vm->memory = (int*)malloc(memory_size * sizeof(int));
    if (!vm->memory) {
        printf("内存分配失败\n");
        exit(1);
    }
    
    // 初始化寄存器和指针
    memset(vm->registers, 0, sizeof(vm->registers));
    vm->pc = 0;
    vm->sp = memory_size - 1;
}

// 加载程序
void vm_load_program(VM* vm, Instruction* program, int size) {
    for (int i = 0; i < size; i++) {
        vm->memory[i] = program[i].opcode;
        vm->memory[i + 1] = program[i].operand1;
        vm->memory[i + 2] = program[i].operand2;
    }
}

// 执行指令
void vm_execute(VM* vm) {
    while (1) {
        int opcode = vm->memory[vm->pc];
        int operand1 = vm->memory[vm->pc + 1];
        int operand2 = vm->memory[vm->pc + 2];
        
        switch (opcode) {
            case HALT:
                return;
                
            case LOAD:
                vm->registers[operand1] = vm->memory[operand2];
                vm->pc += 3;
                break;
                
            case STORE:
                vm->memory[operand2] = vm->registers[operand1];
                vm->pc += 3;
                break;
                
            case ADD:
                vm->registers[operand1] += vm->registers[operand2];
                vm->pc += 3;
                break;
                
            case SUB:
                vm->registers[operand1] -= vm->registers[operand2];
                vm->pc += 3;
                break;
                
            case MUL:
                vm->registers[operand1] *= vm->registers[operand2];
                vm->pc += 3;
                break;
                
            case DIV:
                if (vm->registers[operand2] == 0) {
                    printf("错误：除零\n");
                    return;
                }
                vm->registers[operand1] /= vm->registers[operand2];
                vm->pc += 3;
                break;
                
            case JMP:
                vm->pc = operand1;
                break;
                
            case JZ:
                if (vm->registers[operand1] == 0)
                    vm->pc = operand2;
                else
                    vm->pc += 3;
                break;
                
            case CALL:
                vm->memory[vm->sp] = vm->pc + 3;
                vm->sp--;
                vm->pc = operand1;
                break;
                
            case RET:
                vm->sp++;
                vm->pc = vm->memory[vm->sp];
                break;
                
            default:
                printf("错误：未知指令 %d\n", opcode);
                return;
        }
    }
}

// 打印虚拟机状态
void vm_debug(VM* vm) {
    printf("\n虚拟机状态:\n");
    printf("寄存器:\n");
    for (int i = 0; i < 8; i++)
        printf("R%d: %d\n", i, vm->registers[i]);
    printf("程序计数器: %d\n", vm->pc);
    printf("栈指针: %d\n", vm->sp);
}

// 测试程序
void test_vm() {
    VM vm;
    vm_init(&vm, 1000);
    
    // 测试程序：计算 1 + 2 * 3
    Instruction program[] = {
        {LOAD, 0, 1},    // R0 = 1
        {LOAD, 1, 2},    // R1 = 2
        {LOAD, 2, 3},    // R2 = 3
        {MUL, 1, 2},     // R1 = R1 * R2
        {ADD, 0, 1},     // R0 = R0 + R1
        {HALT, 0, 0}     // 停止
    };
    
    printf("开始执行虚拟机程序...\n");
    vm_load_program(&vm, program, sizeof(program)/sizeof(Instruction));
    vm_execute(&vm);
    vm_debug(&vm);
    
    free(vm.memory);
}

int main() {
    printf("开始测试虚拟机...\n");
    test_vm();
    printf("\n虚拟机测试完成！\n");
    return 0;
} 