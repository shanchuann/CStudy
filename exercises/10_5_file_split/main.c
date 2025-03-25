#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFFER_SIZE 8192
#define MAX_PARTS 100

// 生成分割文件名
void generatePartFileName(char* partName, const char* originalName, int partNum) {
    sprintf(partName, "%s.part%d", originalName, partNum);
}

// 分割文件内容
int splitFile(const char* inputFile, long partSize) {
    FILE* input = fopen(inputFile, "rb");
    if (input == NULL) {
        printf("错误：无法打开输入文件\n");
        return 0;
    }
    
    // 获取文件大小
    fseek(input, 0, SEEK_END);
    long totalSize = ftell(input);
    fseek(input, 0, SEEK_SET);
    
    if (totalSize == 0) {
        printf("错误：输入文件为空\n");
        fclose(input);
        return 0;
    }
    
    // 计算分割数量
    int partCount = (totalSize + partSize - 1) / partSize;
    if (partCount > MAX_PARTS) {
        printf("错误：分割数量超过最大限制(%d)\n", MAX_PARTS);
        fclose(input);
        return 0;
    }
    
    printf("开始分割文件...\n");
    printf("文件大小: %ld 字节\n", totalSize);
    printf("每部分大小: %ld 字节\n", partSize);
    printf("分割数量: %d\n\n", partCount);
    
    unsigned char buffer[BUFFER_SIZE];
    size_t bytesRead;
    long totalBytes = 0;
    char partName[256];
    
    // 依次创建每个分割文件
    for (int i = 0; i < partCount; i++) {
        generatePartFileName(partName, inputFile, i + 1);
        FILE* output = fopen(partName, "wb");
        if (output == NULL) {
            printf("错误：无法创建分割文件 %s\n", partName);
            fclose(input);
            return 0;
        }
        
        printf("正在创建分割文件 %d/%d: %s\n", i + 1, partCount, partName);
        
        // 计算当前部分的大小
        long currentPartSize = (i == partCount - 1) ? 
            (totalSize - i * partSize) : partSize;
        
        // 复制文件内容
        long bytesWritten = 0;
        while (bytesWritten < currentPartSize && 
               (bytesRead = fread(buffer, 1, 
                    (currentPartSize - bytesWritten < BUFFER_SIZE) ? 
                    (currentPartSize - bytesWritten) : BUFFER_SIZE, 
                    input)) > 0) {
            if (fwrite(buffer, 1, bytesRead, output) != bytesRead) {
                printf("错误：写入文件失败\n");
                fclose(output);
                fclose(input);
                return 0;
            }
            bytesWritten += bytesRead;
            totalBytes += bytesRead;
            
            // 显示进度
            int progress = (int)((bytesWritten * 100) / currentPartSize);
            printf("\r文件 %d 进度: %d%% (%ld/%ld 字节)", 
                   i + 1, progress, bytesWritten, currentPartSize);
        }
        
        printf("\n");
        fclose(output);
    }
    
    printf("\n文件分割完成！\n");
    printf("总字节数: %ld\n", totalBytes);
    printf("分割文件列表:\n");
    for (int i = 0; i < partCount; i++) {
        generatePartFileName(partName, inputFile, i + 1);
        printf("  %d. %s\n", i + 1, partName);
    }
    
    fclose(input);
    return 1;
}

int main(int argc, char* argv[]) {
    printf("文件分割程序\n");
    printf("============\n\n");
    
    if (argc != 3) {
        printf("用法: %s <输入文件> <每部分大小(字节)>\n", argv[0]);
        return 1;
    }
    
    const char* inputFile = argv[1];
    long partSize = atol(argv[2]);
    
    if (partSize <= 0) {
        printf("错误：每部分大小必须大于0\n");
        return 1;
    }
    
    if (splitFile(inputFile, partSize)) {
        printf("\n分割成功！\n");
    } else {
        printf("文件分割失败！\n");
    }
    
    return 0;
} 