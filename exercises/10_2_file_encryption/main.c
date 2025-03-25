#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFFER_SIZE 1024

// 加密/解密文件内容
int encryptFile(const char* inputFile, const char* outputFile, unsigned char key) {
    FILE* inFile = fopen(inputFile, "rb");
    FILE* outFile = fopen(outputFile, "wb");
    
    if (inFile == NULL || outFile == NULL) {
        printf("错误：无法打开文件\n");
        if (inFile) fclose(inFile);
        if (outFile) fclose(outFile);
        return 0;
    }
    
    unsigned char buffer[BUFFER_SIZE];
    size_t bytesRead;
    
    while ((bytesRead = fread(buffer, 1, BUFFER_SIZE, inFile)) > 0) {
        // 对每个字节进行异或运算
        for (size_t i = 0; i < bytesRead; i++) {
            buffer[i] ^= key;
        }
        fwrite(buffer, 1, bytesRead, outFile);
    }
    
    fclose(inFile);
    fclose(outFile);
    return 1;
}

int main(int argc, char* argv[]) {
    printf("文件加密/解密程序\n");
    printf("===============\n\n");
    
    if (argc != 4) {
        printf("用法: %s <输入文件> <输出文件> <密钥(0-255)>\n", argv[0]);
        return 1;
    }
    
    const char* inputFile = argv[1];
    const char* outputFile = argv[2];
    unsigned char key = (unsigned char)atoi(argv[3]);
    
    if (key < 0 || key > 255) {
        printf("错误：密钥必须在0-255之间\n");
        return 1;
    }
    
    if (encryptFile(inputFile, outputFile, key)) {
        printf("文件加密/解密成功！\n");
        printf("输入文件: %s\n", inputFile);
        printf("输出文件: %s\n", outputFile);
        printf("使用密钥: %d\n", key);
    } else {
        printf("文件加密/解密失败！\n");
    }
    
    return 0;
} 