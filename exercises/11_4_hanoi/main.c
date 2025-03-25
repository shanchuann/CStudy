#include <stdio.h>
#include <stdlib.h>

// 汉诺塔结构体
typedef struct {
    int* disks;     // 每个柱子上盘子的数组
    int size;       // 每个柱子上盘子的数量
    int capacity;   // 每个柱子的容量
} Tower;

// 初始化柱子
Tower* initTower(int capacity) {
    Tower* tower = (Tower*)malloc(sizeof(Tower));
    if (!tower) {
        printf("内存分配失败！\n");
        return NULL;
    }
    
    tower->disks = (int*)malloc(sizeof(int) * capacity);
    if (!tower->disks) {
        free(tower);
        printf("内存分配失败！\n");
        return NULL;
    }
    
    tower->size = 0;
    tower->capacity = capacity;
    return tower;
}

// 释放柱子内存
void freeTower(Tower* tower) {
    if (tower) {
        if (tower->disks) {
            free(tower->disks);
        }
        free(tower);
    }
}

// 添加盘子到柱子
int pushDisk(Tower* tower, int disk) {
    if (tower->size >= tower->capacity) {
        return 0;
    }
    tower->disks[tower->size++] = disk;
    return 1;
}

// 从柱子移除盘子
int popDisk(Tower* tower, int* disk) {
    if (tower->size <= 0) {
        return 0;
    }
    *disk = tower->disks[--tower->size];
    return 1;
}

// 获取柱子顶部的盘子
int peekDisk(Tower* tower, int* disk) {
    if (tower->size <= 0) {
        return 0;
    }
    *disk = tower->disks[tower->size - 1];
    return 1;
}

// 显示当前状态
void displayState(Tower* towers[], int numTowers, int numDisks) {
    printf("\n当前状态：\n");
    printf("----------------------------------------\n");
    
    // 从顶部开始显示
    for (int i = numDisks - 1; i >= 0; i--) {
        for (int j = 0; j < numTowers; j++) {
            if (i < towers[j]->size) {
                printf("%d\t", towers[j]->disks[i]);
            } else {
                printf("|\t");
            }
        }
        printf("\n");
    }
    
    // 显示柱子编号
    for (int j = 0; j < numTowers; j++) {
        printf("%c\t", 'A' + j);
    }
    printf("\n----------------------------------------\n");
}

// 移动盘子
void moveDisk(Tower* from, Tower* to, int* moves) {
    int disk;
    if (popDisk(from, &disk)) {
        pushDisk(to, disk);
        (*moves)++;
    }
}

// 递归解决汉诺塔
void solveHanoi(int n, Tower* towers[], int from, int aux, int to, int* moves) {
    if (n == 1) {
        moveDisk(towers[from], towers[to], moves);
        displayState(towers, 3, towers[0]->capacity);
        return;
    }
    
    solveHanoi(n - 1, towers, from, to, aux, moves);
    moveDisk(towers[from], towers[to], moves);
    displayState(towers, 3, towers[0]->capacity);
    solveHanoi(n - 1, towers, aux, from, to, moves);
}

int main() {
    int numDisks;
    printf("请输入盘子数量（1-8）：");
    scanf("%d", &numDisks);
    
    if (numDisks < 1 || numDisks > 8) {
        printf("无效的盘子数量！\n");
        return 1;
    }
    
    // 创建三个柱子
    Tower* towers[3];
    for (int i = 0; i < 3; i++) {
        towers[i] = initTower(numDisks);
        if (!towers[i]) {
            // 清理已分配的内存
            for (int j = 0; j < i; j++) {
                freeTower(towers[j]);
            }
            return 1;
        }
    }
    
    // 初始化第一个柱子
    for (int i = numDisks; i > 0; i--) {
        pushDisk(towers[0], i);
    }
    
    printf("\n初始状态：\n");
    displayState(towers, 3, numDisks);
    
    // 解决汉诺塔
    int moves = 0;
    solveHanoi(numDisks, towers, 0, 1, 2, &moves);
    
    printf("\n完成！总共移动 %d 步。\n", moves);
    
    // 释放内存
    for (int i = 0; i < 3; i++) {
        freeTower(towers[i]);
    }
    
    return 0;
} 