#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

// 定义文件统计结构体
typedef struct {
    long lineCount;    // 行数
    long wordCount;    // 字数
    long charCount;    // 字符数
} FileStats;

// 初始化统计结构体
FileStats initStats() {
    FileStats stats = {0, 0, 0};
    return stats;
}

// 统计文件内容
FileStats countFileStats(const char* filename) {
    FileStats stats = initStats();
    FILE* file = fopen(filename, "r");
    
    if (file == NULL) {
        printf("错误：无法打开文件 %s\n", filename);
        return stats;
    }
    
    char ch;
    int inWord = 0;  // 是否在单词内
    
    while ((ch = fgetc(file)) != EOF) {
        stats.charCount++;
        
        if (ch == '\n') {
            stats.lineCount++;
        }
        
        if (isspace(ch)) {
            if (inWord) {
                stats.wordCount++;
                inWord = 0;
            }
        } else {
            inWord = 1;
        }
    }
    
    // 处理最后一个单词
    if (inWord) {
        stats.wordCount++;
    }
    
    // 处理最后一行
    if (stats.charCount > 0 && ch != '\n') {
        stats.lineCount++;
    }
    
    fclose(file);
    return stats;
}

// 打印统计结果
void printStats(const char* filename, const FileStats* stats) {
    printf("\n文件统计结果:\n");
    printf("文件名: %s\n", filename);
    printf("行数: %ld\n", stats->lineCount);
    printf("字数: %ld\n", stats->wordCount);
    printf("字符数: %ld\n", stats->charCount);
    printf("------------------------\n");
}

int main(int argc, char* argv[]) {
    printf("文件内容统计程序\n");
    printf("===============\n\n");
    
    if (argc != 2) {
        printf("用法: %s <文件名>\n", argv[0]);
        return 1;
    }
    
    const char* filename = argv[1];
    FileStats stats = countFileStats(filename);
    printStats(filename, &stats);
    
    return 0;
} 