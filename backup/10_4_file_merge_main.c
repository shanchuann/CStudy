#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFFER_SIZE 8192
#define MAX_FILES 10

// 合并文件内容
int mergeFiles(const char* outputFile, const char* inputFiles[], int fileCount) {
    FILE* output = fopen(outputFile, "wb");
    if (output == NULL) {
        printf("错误：无法创建输出文件\n");
        return 0;
    }
    
    unsigned char buffer[BUFFER_SIZE];
    size_t bytesRead;
    long totalBytes = 0;
    
    printf("开始合并文件...\n");
    
    // 依次处理每个输入文件
    for (int i = 0; i < fileCount; i++) {
        FILE* input = fopen(inputFiles[i], "rb");
        if (input == NULL) {
            printf("错误：无法打开文件 %s\n", inputFiles[i]);
            fclose(output);
            return 0;
        }
        
        // 获取当前文件大小
        fseek(input, 0, SEEK_END);
        long fileSize = ftell(input);
        fseek(input, 0, SEEK_SET);
        
        printf("正在处理文件 %d/%d: %s (大小: %ld 字节)\n", 
               i + 1, fileCount, inputFiles[i], fileSize);
        
        // 复制文件内容
        while ((bytesRead = fread(buffer, 1, BUFFER_SIZE, input)) > 0) {
            if (fwrite(buffer, 1, bytesRead, output) != bytesRead) {
                printf("错误：写入文件失败\n");
                fclose(input);
                fclose(output);
                return 0;
            }
            totalBytes += bytesRead;
            
            // 显示进度
            if (fileSize > 0) {
                int progress = (int)((totalBytes * 100) / fileSize);
                printf("\r文件 %d 进度: %d%% (%ld/%ld 字节)", 
                       i + 1, progress, totalBytes, fileSize);
            }
        }
        
        printf("\n");
        fclose(input);
    }
    
    printf("文件合并完成！\n");
    printf("总字节数: %ld\n", totalBytes);
    fclose(output);
    return 1;
}

int main(int argc, char* argv[]) {
    printf("文件合并程序\n");
    printf("============\n\n");
    
    if (argc < 4) {
        printf("用法: %s <输出文件> <输入文件1> <输入文件2> ...\n", argv[0]);
        printf("至少需要2个输入文件\n");
        return 1;
    }
    
    const char* outputFile = argv[1];
    const char* inputFiles[MAX_FILES];
    int fileCount = argc - 2;
    
    if (fileCount > MAX_FILES) {
        printf("错误：输入文件数量超过最大限制(%d)\n", MAX_FILES);
        return 1;
    }
    
    // 收集输入文件名
    for (int i = 0; i < fileCount; i++) {
        inputFiles[i] = argv[i + 2];
    }
    
    if (mergeFiles(outputFile, inputFiles, fileCount)) {
        printf("\n合并结果：\n");
        printf("输出文件: %s\n", outputFile);
        printf("输入文件数量: %d\n", fileCount);
        printf("输入文件列表:\n");
        for (int i = 0; i < fileCount; i++) {
            printf("  %d. %s\n", i + 1, inputFiles[i]);
        }
    } else {
        printf("文件合并失败！\n");
    }
    
    return 0;
} 