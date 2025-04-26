#include <stdio.h>
#include <stdlib.h>

// 多项式项结构体
typedef struct Term {
    float coef;     // 系数
    int exp;        // 指数
    struct Term* next;  // 指向下一项的指针
} Term;

// 多项式结构体
typedef struct {
    Term* head;     // 头指针
    int size;       // 项数
} Polynomial;

// 创建新项
Term* createTerm(float coef, int exp) {
    Term* term = (Term*)malloc(sizeof(Term));
    if (term == NULL) {
        printf("内存分配失败！\n");
        exit(1);
    }
    term->coef = coef;
    term->exp = exp;
    term->next = NULL;
    return term;
}

// 初始化多项式
void initPolynomial(Polynomial* poly) {
    poly->head = NULL;
    poly->size = 0;
}

// 添加项到多项式
void addTerm(Polynomial* poly, float coef, int exp) {
    Term* newTerm = createTerm(coef, exp);
    
    // 如果多项式为空，直接添加为头项
    if (poly->head == NULL) {
        poly->head = newTerm;
        poly->size++;
        return;
    }
    
    // 如果新项的指数大于头项的指数，插入到头部
    if (exp > poly->head->exp) {
        newTerm->next = poly->head;
        poly->head = newTerm;
        poly->size++;
        return;
    }
    
    // 在适当位置插入新项
    Term* current = poly->head;
    while (current->next != NULL && current->next->exp >= exp) {
        current = current->next;
    }
    
    // 如果找到相同指数的项，合并系数
    if (current->exp == exp) {
        current->coef += coef;
        free(newTerm);
        return;
    }
    
    // 插入新项
    newTerm->next = current->next;
    current->next = newTerm;
    poly->size++;
}

// 多项式相加
Polynomial addPolynomials(const Polynomial* poly1, const Polynomial* poly2) {
    Polynomial result;
    initPolynomial(&result);
    
    // 复制第一个多项式
    Term* current = poly1->head;
    while (current != NULL) {
        addTerm(&result, current->coef, current->exp);
        current = current->next;
    }
    
    // 添加第二个多项式
    current = poly2->head;
    while (current != NULL) {
        addTerm(&result, current->coef, current->exp);
        current = current->next;
    }
    
    return result;
}

// 打印多项式
void printPolynomial(const Polynomial* poly) {
    if (poly->head == NULL) {
        printf("0\n");
        return;
    }
    
    Term* current = poly->head;
    int first = 1;
    
    while (current != NULL) {
        // 处理系数
        if (current->coef > 0 && !first) {
            printf(" + ");
        } else if (current->coef < 0) {
            printf(" - ");
        }
        
        // 打印系数
        if (current->coef != 1 && current->coef != -1 || current->exp == 0) {
            printf("%.2f", fabs(current->coef));
        }
        
        // 打印变量和指数
        if (current->exp > 0) {
            printf("x");
            if (current->exp > 1) {
                printf("^%d", current->exp);
            }
        }
        
        current = current->next;
        first = 0;
    }
    printf("\n");
}

// 释放多项式内存
void freePolynomial(Polynomial* poly) {
    Term* current = poly->head;
    while (current != NULL) {
        Term* next = current->next;
        free(current);
        current = next;
    }
    poly->head = NULL;
    poly->size = 0;
}

// 输入多项式
Polynomial inputPolynomial(const char* prompt) {
    Polynomial poly;
    initPolynomial(&poly);
    
    printf("%s\n", prompt);
    printf("请输入项数：");
    int n;
    scanf("%d", &n);
    
    for (int i = 0; i < n; i++) {
        float coef;
        int exp;
        printf("请输入第%d项的系数：", i + 1);
        scanf("%f", &coef);
        printf("请输入第%d项的指数：", i + 1);
        scanf("%d", &exp);
        addTerm(&poly, coef, exp);
    }
    
    return poly;
}

int main() {
    printf("多项式相加程序\n");
    printf("==============\n\n");
    
    // 输入第一个多项式
    Polynomial poly1 = inputPolynomial("请输入第一个多项式：");
    printf("第一个多项式：");
    printPolynomial(&poly1);
    
    // 输入第二个多项式
    Polynomial poly2 = inputPolynomial("请输入第二个多项式：");
    printf("第二个多项式：");
    printPolynomial(&poly2);
    
    // 计算并显示结果
    printf("\n计算结果：\n");
    printf("----------------------------------------\n");
    Polynomial result = addPolynomials(&poly1, &poly2);
    printPolynomial(&result);
    
    // 释放内存
    freePolynomial(&poly1);
    freePolynomial(&poly2);
    freePolynomial(&result);
    
    return 0;
} 