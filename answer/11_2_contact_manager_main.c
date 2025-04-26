#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_NAME_LEN 50
#define MAX_PHONE_LEN 20
#define INITIAL_CAPACITY 10

// 联系人结构体
typedef struct {
    char name[MAX_NAME_LEN];
    char phone[MAX_PHONE_LEN];
} Contact;

// 通讯录结构体
typedef struct {
    Contact* contacts;
    int size;
    int capacity;
} ContactBook;

// 初始化通讯录
ContactBook* initContactBook() {
    ContactBook* book = (ContactBook*)malloc(sizeof(ContactBook));
    if (!book) {
        printf("内存分配失败！\n");
        return NULL;
    }
    
    book->contacts = (Contact*)malloc(sizeof(Contact) * INITIAL_CAPACITY);
    if (!book->contacts) {
        free(book);
        printf("内存分配失败！\n");
        return NULL;
    }
    
    book->size = 0;
    book->capacity = INITIAL_CAPACITY;
    return book;
}

// 扩展通讯录容量
int expandCapacity(ContactBook* book) {
    int newCapacity = book->capacity * 2;
    Contact* newContacts = (Contact*)realloc(book->contacts, sizeof(Contact) * newCapacity);
    
    if (!newContacts) {
        printf("内存扩展失败！\n");
        return 0;
    }
    
    book->contacts = newContacts;
    book->capacity = newCapacity;
    return 1;
}

// 添加联系人
int addContact(ContactBook* book, const char* name, const char* phone) {
    if (book->size >= book->capacity && !expandCapacity(book)) {
        return 0;
    }
    
    strncpy(book->contacts[book->size].name, name, MAX_NAME_LEN - 1);
    strncpy(book->contacts[book->size].phone, phone, MAX_PHONE_LEN - 1);
    book->size++;
    return 1;
}

// 删除联系人
int deleteContact(ContactBook* book, const char* name) {
    for (int i = 0; i < book->size; i++) {
        if (strcmp(book->contacts[i].name, name) == 0) {
            // 将最后一个联系人移到当前位置
            if (i < book->size - 1) {
                book->contacts[i] = book->contacts[book->size - 1];
            }
            book->size--;
            return 1;
        }
    }
    return 0;
}

// 查找联系人
Contact* findContact(ContactBook* book, const char* name) {
    for (int i = 0; i < book->size; i++) {
        if (strcmp(book->contacts[i].name, name) == 0) {
            return &book->contacts[i];
        }
    }
    return NULL;
}

// 显示所有联系人
void displayContacts(ContactBook* book) {
    if (book->size == 0) {
        printf("通讯录为空！\n");
        return;
    }
    
    printf("\n通讯录内容：\n");
    printf("----------------------------------------\n");
    printf("序号\t姓名\t\t电话\n");
    printf("----------------------------------------\n");
    
    for (int i = 0; i < book->size; i++) {
        printf("%d\t%s\t%s\n", i + 1, book->contacts[i].name, book->contacts[i].phone);
    }
    printf("----------------------------------------\n");
}

// 释放通讯录内存
void freeContactBook(ContactBook* book) {
    if (book) {
        if (book->contacts) {
            free(book->contacts);
        }
        free(book);
    }
}

int main() {
    ContactBook* book = initContactBook();
    if (!book) {
        return 1;
    }
    
    int choice;
    char name[MAX_NAME_LEN];
    char phone[MAX_PHONE_LEN];
    
    while (1) {
        printf("\n通讯录管理系统\n");
        printf("==============\n");
        printf("1. 添加联系人\n");
        printf("2. 删除联系人\n");
        printf("3. 查找联系人\n");
        printf("4. 显示所有联系人\n");
        printf("5. 退出\n");
        printf("请选择操作（1-5）：");
        
        scanf("%d", &choice);
        getchar(); // 清除换行符
        
        switch (choice) {
            case 1:
                printf("请输入姓名：");
                fgets(name, MAX_NAME_LEN, stdin);
                name[strcspn(name, "\n")] = 0;
                
                printf("请输入电话：");
                fgets(phone, MAX_PHONE_LEN, stdin);
                phone[strcspn(phone, "\n")] = 0;
                
                if (addContact(book, name, phone)) {
                    printf("添加成功！\n");
                } else {
                    printf("添加失败！\n");
                }
                break;
                
            case 2:
                printf("请输入要删除的联系人姓名：");
                fgets(name, MAX_NAME_LEN, stdin);
                name[strcspn(name, "\n")] = 0;
                
                if (deleteContact(book, name)) {
                    printf("删除成功！\n");
                } else {
                    printf("未找到该联系人！\n");
                }
                break;
                
            case 3:
                printf("请输入要查找的联系人姓名：");
                fgets(name, MAX_NAME_LEN, stdin);
                name[strcspn(name, "\n")] = 0;
                
                Contact* contact = findContact(book, name);
                if (contact) {
                    printf("姓名：%s\n电话：%s\n", contact->name, contact->phone);
                } else {
                    printf("未找到该联系人！\n");
                }
                break;
                
            case 4:
                displayContacts(book);
                break;
                
            case 5:
                printf("感谢使用！\n");
                freeContactBook(book);
                return 0;
                
            default:
                printf("无效的选择！\n");
        }
    }
    
    return 0;
} 