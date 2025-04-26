#include <stdio.h>

#define MAX_SIZE 1000

// 栈结构
typedef struct {
    char data[MAX_SIZE];
    int top;
} Stack;

// 初始化栈
void initStack(Stack* s) {
    s->top = -1;
}

// 入栈
void push(Stack* s, char c) {
    s->data[++(s->top)] = c;
}

// 出栈
char pop(Stack* s) {
    if (s->top == -1) return '\0';
    return s->data[(s->top)--];
}

// 检查括号是否匹配
int checkBrackets(const char* str) {
    Stack s;
    initStack(&s);
    
    for (int i = 0; str[i] != '\0'; i++) {
        if (str[i] == '(' || str[i] == '[' || str[i] == '{') {
            push(&s, str[i]);
        } else if (str[i] == ')' || str[i] == ']' || str[i] == '}') {
            char top = pop(&s);
            if (top == '\0') return 0;  // 栈为空，右括号多余
            
            // 检查括号是否匹配
            if ((str[i] == ')' && top != '(') ||
                (str[i] == ']' && top != '[') ||
                (str[i] == '}' && top != '{')) {
                return 0;  // 括号不匹配
            }
        }
    }
    
    return s.top == -1;  // 栈为空表示匹配
}

int main() {
    char str[1000];
    
    printf("请输入包含括号的字符串: ");
    gets(str);
    
    // 检查括号匹配
    if (checkBrackets(str)) {
        printf("括号匹配正确\n");
    } else {
        printf("括号匹配错误\n");
    }
    
    return 0;
} 