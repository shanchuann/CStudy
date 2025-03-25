#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
    // 初始化随机数种子
    srand(time(NULL));
    
    // 生成1-100之间的随机数
    int target = rand() % 100 + 1;
    int guess;
    int attempts = 0;
    int max_attempts = 7;
    
    printf("欢迎来到猜数字游戏！\n");
    printf("我已经想好了一个1-100之间的数字，你有%d次机会猜对它。\n", max_attempts);
    
    while (attempts < max_attempts) {
        printf("\n请输入你的猜测（还剩%d次机会）：", max_attempts - attempts);
        scanf("%d", &guess);
        attempts++;
        
        if (guess == target) {
            printf("恭喜你猜对了！答案就是%d。\n", target);
            printf("你用了%d次就猜到了！\n", attempts);
            return 0;
        } else if (guess < target) {
            printf("太小了！再大一点。\n");
        } else {
            printf("太大了！再小一点。\n");
        }
    }
    
    printf("\n游戏结束！正确答案是%d。\n", target);
    return 0;
} 