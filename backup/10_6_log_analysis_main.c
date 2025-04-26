#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_LINE_LENGTH 1024
#define MAX_ERROR_TYPES 100

// 错误类型结构
typedef struct {
    char type[50];
    int count;
    char last_occurrence[50];
} ErrorType;

// 日志统计结构
typedef struct {
    int total_lines;
    int error_lines;
    int warning_lines;
    int info_lines;
    ErrorType error_types[MAX_ERROR_TYPES];
    int error_type_count;
} LogStats;

// 初始化统计结构
void initLogStats(LogStats* stats) {
    stats->total_lines = 0;
    stats->error_lines = 0;
    stats->warning_lines = 0;
    stats->info_lines = 0;
    stats->error_type_count = 0;
}

// 更新错误类型统计
void updateErrorType(LogStats* stats, const char* error_type, const char* timestamp) {
    // 查找是否已存在该错误类型
    for (int i = 0; i < stats->error_type_count; i++) {
        if (strcmp(stats->error_types[i].type, error_type) == 0) {
            stats->error_types[i].count++;
            strcpy(stats->error_types[i].last_occurrence, timestamp);
            return;
        }
    }
    
    // 添加新的错误类型
    if (stats->error_type_count < MAX_ERROR_TYPES) {
        strcpy(stats->error_types[stats->error_type_count].type, error_type);
        stats->error_types[stats->error_type_count].count = 1;
        strcpy(stats->error_types[stats->error_type_count].last_occurrence, timestamp);
        stats->error_type_count++;
    }
}

// 分析日志行
void analyzeLogLine(LogStats* stats, const char* line) {
    char timestamp[50];
    char level[10];
    char error_type[50];
    char message[MAX_LINE_LENGTH];
    
    // 解析日志行
    if (sscanf(line, "[%[^]]] [%[^]]] [%[^]]] %[^\n]", 
                timestamp, level, error_type, message) == 4) {
        stats->total_lines++;
        
        // 统计日志级别
        if (strcmp(level, "ERROR") == 0) {
            stats->error_lines++;
            updateErrorType(stats, error_type, timestamp);
        } else if (strcmp(level, "WARNING") == 0) {
            stats->warning_lines++;
        } else if (strcmp(level, "INFO") == 0) {
            stats->info_lines++;
        }
    }
}

// 分析日志文件
int analyzeLogFile(const char* filename, LogStats* stats) {
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        printf("错误：无法打开日志文件\n");
        return 0;
    }
    
    char line[MAX_LINE_LENGTH];
    printf("开始分析日志文件...\n");
    
    while (fgets(line, sizeof(line), file)) {
        analyzeLogLine(stats, line);
    }
    
    fclose(file);
    return 1;
}

// 显示统计结果
void displayStats(const LogStats* stats) {
    printf("\n日志分析结果\n");
    printf("============\n\n");
    
    printf("基本统计：\n");
    printf("总行数: %d\n", stats->total_lines);
    printf("错误行数: %d\n", stats->error_lines);
    printf("警告行数: %d\n", stats->warning_lines);
    printf("信息行数: %d\n", stats->info_lines);
    
    printf("\n错误类型统计：\n");
    printf("----------------------------------------\n");
    printf("%-30s %-10s %-20s\n", "错误类型", "出现次数", "最后出现时间");
    printf("----------------------------------------\n");
    
    for (int i = 0; i < stats->error_type_count; i++) {
        printf("%-30s %-10d %-20s\n",
               stats->error_types[i].type,
               stats->error_types[i].count,
               stats->error_types[i].last_occurrence);
    }
    
    printf("----------------------------------------\n");
}

int main(int argc, char* argv[]) {
    printf("日志文件分析程序\n");
    printf("===============\n\n");
    
    if (argc != 2) {
        printf("用法: %s <日志文件>\n", argv[0]);
        return 1;
    }
    
    LogStats stats;
    initLogStats(&stats);
    
    if (analyzeLogFile(argv[1], &stats)) {
        displayStats(&stats);
    } else {
        printf("日志分析失败！\n");
    }
    
    return 0;
} 