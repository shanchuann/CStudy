#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_BOOKS 100
#define MAX_TITLE_LEN 50
#define MAX_AUTHOR_LEN 30

// 借阅状态枚举
typedef enum {
    AVAILABLE,    // 可借阅
    BORROWED,     // 已借出
    RESERVED      // 已预约
} BorrowStatus;

// 图书结构体
typedef struct {
    int id;                     // 图书编号
    char title[MAX_TITLE_LEN];  // 书名
    char author[MAX_AUTHOR_LEN];// 作者
    float price;                // 价格
    BorrowStatus status;        // 借阅状态
    char borrower[30];          // 借阅者姓名
    char borrowDate[20];        // 借阅日期
} Book;

// 图书管理系统结构体
typedef struct {
    Book books[MAX_BOOKS];      // 图书数组
    int count;                  // 当前图书数量
} LibrarySystem;

// 初始化系统
void initSystem(LibrarySystem* sys) {
    sys->count = 0;
}

// 添加图书
int addBook(LibrarySystem* sys) {
    if (sys->count >= MAX_BOOKS) {
        printf("系统已满，无法添加更多图书！\n");
        return 0;
    }
    
    Book* book = &sys->books[sys->count];
    
    printf("请输入图书编号：");
    scanf("%d", &book->id);
    
    printf("请输入书名：");
    scanf("%s", book->title);
    
    printf("请输入作者：");
    scanf("%s", book->author);
    
    printf("请输入价格：");
    scanf("%f", &book->price);
    
    book->status = AVAILABLE;
    strcpy(book->borrower, "");
    strcpy(book->borrowDate, "");
    
    sys->count++;
    printf("图书添加成功！\n");
    return 1;
}

// 查找图书
Book* findBook(LibrarySystem* sys, int id) {
    for (int i = 0; i < sys->count; i++) {
        if (sys->books[i].id == id) {
            return &sys->books[i];
        }
    }
    return NULL;
}

// 借阅图书
void borrowBook(LibrarySystem* sys) {
    int id;
    printf("请输入要借阅的图书编号：");
    scanf("%d", &id);
    
    Book* book = findBook(sys, id);
    if (!book) {
        printf("未找到该图书！\n");
        return;
    }
    
    if (book->status != AVAILABLE) {
        printf("该图书当前不可借阅！\n");
        return;
    }
    
    printf("请输入借阅者姓名：");
    scanf("%s", book->borrower);
    
    printf("请输入借阅日期：");
    scanf("%s", book->borrowDate);
    
    book->status = BORROWED;
    printf("图书借阅成功！\n");
}

// 归还图书
void returnBook(LibrarySystem* sys) {
    int id;
    printf("请输入要归还的图书编号：");
    scanf("%d", &id);
    
    Book* book = findBook(sys, id);
    if (!book) {
        printf("未找到该图书！\n");
        return;
    }
    
    if (book->status != BORROWED) {
        printf("该图书未被借出！\n");
        return;
    }
    
    book->status = AVAILABLE;
    strcpy(book->borrower, "");
    strcpy(book->borrowDate, "");
    printf("图书归还成功！\n");
}

// 预约图书
void reserveBook(LibrarySystem* sys) {
    int id;
    printf("请输入要预约的图书编号：");
    scanf("%d", &id);
    
    Book* book = findBook(sys, id);
    if (!book) {
        printf("未找到该图书！\n");
        return;
    }
    
    if (book->status != AVAILABLE) {
        printf("该图书当前不可预约！\n");
        return;
    }
    
    book->status = RESERVED;
    printf("图书预约成功！\n");
}

// 显示所有图书
void displayAllBooks(LibrarySystem* sys) {
    if (sys->count == 0) {
        printf("暂无图书信息！\n");
        return;
    }
    
    printf("\n图书信息列表：\n");
    printf("编号\t书名\t作者\t价格\t状态\t借阅者\t借阅日期\n");
    printf("--------------------------------------------------------\n");
    
    for (int i = 0; i < sys->count; i++) {
        Book* book = &sys->books[i];
        const char* statusStr;
        switch (book->status) {
            case AVAILABLE: statusStr = "可借阅"; break;
            case BORROWED: statusStr = "已借出"; break;
            case RESERVED: statusStr = "已预约"; break;
        }
        
        printf("%d\t%s\t%s\t%.2f\t%s\t%s\t%s\n",
               book->id,
               book->title,
               book->author,
               book->price,
               statusStr,
               book->borrower,
               book->borrowDate);
    }
}

// 显示菜单
void showMenu() {
    printf("\n图书管理系统\n");
    printf("1. 添加图书\n");
    printf("2. 借阅图书\n");
    printf("3. 归还图书\n");
    printf("4. 预约图书\n");
    printf("5. 显示所有图书\n");
    printf("0. 退出系统\n");
    printf("请选择操作：");
}

int main() {
    LibrarySystem sys;
    initSystem(&sys);
    
    int choice;
    do {
        showMenu();
        scanf("%d", &choice);
        
        switch (choice) {
            case 1:
                addBook(&sys);
                break;
            case 2:
                borrowBook(&sys);
                break;
            case 3:
                returnBook(&sys);
                break;
            case 4:
                reserveBook(&sys);
                break;
            case 5:
                displayAllBooks(&sys);
                break;
            case 0:
                printf("感谢使用！\n");
                break;
            default:
                printf("无效的选择，请重试！\n");
        }
    } while (choice != 0);
    
    return 0;
} 