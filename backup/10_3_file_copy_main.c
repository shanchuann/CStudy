#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFFER_SIZE 8192  // 使用较大的缓冲区以提高效率

// 复制文件内容
int copyFile(const char* sourceFile, const char* targetFile) {
    FILE* source = fopen(sourceFile, "rb");
    FILE* target = fopen(targetFile, "wb");
    
    if (source == NULL || target == NULL) {
        printf("错误：无法打开文件\n");
        if (source) fclose(source);
        if (target) fclose(target);
        return 0;
    }
    
    unsigned char buffer[BUFFER_SIZE];
    size_t bytesRead;
    long totalBytes = 0;
    
    // 获取源文件大小
    fseek(source, 0, SEEK_END);
    long fileSize = ftell(source);
    fseek(source, 0, SEEK_SET);
    
    printf("开始复制文件...\n");
    printf("源文件大小: %ld 字节\n", fileSize);
    
    while ((bytesRead = fread(buffer, 1, BUFFER_SIZE, source)) > 0) {
        if (fwrite(buffer, 1, bytesRead, target) != bytesRead) {
            printf("错误：写入文件失败\n");
            fclose(source);
            fclose(target);
            return 0;
        }
        totalBytes += bytesRead;
        
        // 显示进度
        if (fileSize > 0) {
            int progress = (int)((totalBytes * 100) / fileSize);
            printf("\r复制进度: %d%% (%ld/%ld 字节)", progress, totalBytes, fileSize);
        }
    }
    
    printf("\n文件复制完成！\n");
    fclose(source);
    fclose(target);
    return 1;
}

int main(int argc, char* argv[]) {
    printf("文件复制程序\n");
    printf("============\n\n");
    
    if (argc != 3) {
        printf("用法: %s <源文件> <目标文件>\n", argv[0]);
        return 1;
    }
    
    const char* sourceFile = argv[1];
    const char* targetFile = argv[2];
    
    if (strcmp(sourceFile, targetFile) == 0) {
        printf("错误：源文件和目标文件不能相同\n");
        return 1;
    }
    
    if (copyFile(sourceFile, targetFile)) {
        printf("源文件: %s\n", sourceFile);
        printf("目标文件: %s\n", targetFile);
    } else {
        printf("文件复制失败！\n");
    }
    
    return 0;
} 