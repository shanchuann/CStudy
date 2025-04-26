#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_STUDENTS 100
#define MAX_NAME_LEN 50

// 学生结构体
typedef struct {
    int id;                     // 学号
    char name[MAX_NAME_LEN];    // 姓名
    float chinese;              // 语文成绩
    float math;                 // 数学成绩
    float english;              // 英语成绩
    float average;              // 平均分
} Student;

// 学生管理系统结构体
typedef struct {
    Student students[MAX_STUDENTS];  // 学生数组
    int count;                       // 当前学生数量
} StudentSystem;

// 初始化系统
void initSystem(StudentSystem* sys) {
    sys->count = 0;
}

// 添加学生
int addStudent(StudentSystem* sys) {
    if (sys->count >= MAX_STUDENTS) {
        printf("系统已满，无法添加更多学生！\n");
        return 0;
    }
    
    Student* student = &sys->students[sys->count];
    
    printf("请输入学号：");
    scanf("%d", &student->id);
    
    printf("请输入姓名：");
    scanf("%s", student->name);
    
    printf("请输入语文成绩：");
    scanf("%f", &student->chinese);
    
    printf("请输入数学成绩：");
    scanf("%f", &student->math);
    
    printf("请输入英语成绩：");
    scanf("%f", &student->english);
    
    // 计算平均分
    student->average = (student->chinese + student->math + student->english) / 3;
    
    sys->count++;
    printf("学生信息添加成功！\n");
    return 1;
}

// 查找学生
Student* findStudent(StudentSystem* sys, int id) {
    for (int i = 0; i < sys->count; i++) {
        if (sys->students[i].id == id) {
            return &sys->students[i];
        }
    }
    return NULL;
}

// 修改学生信息
void modifyStudent(StudentSystem* sys) {
    int id;
    printf("请输入要修改的学生学号：");
    scanf("%d", &id);
    
    Student* student = findStudent(sys, id);
    if (!student) {
        printf("未找到该学生！\n");
        return;
    }
    
    printf("请输入新的语文成绩：");
    scanf("%f", &student->chinese);
    
    printf("请输入新的数学成绩：");
    scanf("%f", &student->math);
    
    printf("请输入新的英语成绩：");
    scanf("%f", &student->english);
    
    // 更新平均分
    student->average = (student->chinese + student->math + student->english) / 3;
    
    printf("学生信息修改成功！\n");
}

// 删除学生
void deleteStudent(StudentSystem* sys) {
    int id;
    printf("请输入要删除的学生学号：");
    scanf("%d", &id);
    
    for (int i = 0; i < sys->count; i++) {
        if (sys->students[i].id == id) {
            // 将后面的学生前移
            for (int j = i; j < sys->count - 1; j++) {
                sys->students[j] = sys->students[j + 1];
            }
            sys->count--;
            printf("学生信息删除成功！\n");
            return;
        }
    }
    
    printf("未找到该学生！\n");
}

// 显示所有学生信息
void displayAllStudents(StudentSystem* sys) {
    if (sys->count == 0) {
        printf("暂无学生信息！\n");
        return;
    }
    
    printf("\n学生信息列表：\n");
    printf("学号\t姓名\t语文\t数学\t英语\t平均分\n");
    printf("----------------------------------------\n");
    
    for (int i = 0; i < sys->count; i++) {
        Student* student = &sys->students[i];
        printf("%d\t%s\t%.1f\t%.1f\t%.1f\t%.1f\n",
               student->id,
               student->name,
               student->chinese,
               student->math,
               student->english,
               student->average);
    }
}

// 按平均分排序
void sortByAverage(StudentSystem* sys) {
    // 使用冒泡排序
    for (int i = 0; i < sys->count - 1; i++) {
        for (int j = 0; j < sys->count - 1 - i; j++) {
            if (sys->students[j].average < sys->students[j + 1].average) {
                // 交换学生信息
                Student temp = sys->students[j];
                sys->students[j] = sys->students[j + 1];
                sys->students[j + 1] = temp;
            }
        }
    }
    
    printf("排序完成！\n");
    displayAllStudents(sys);
}

// 显示菜单
void showMenu() {
    printf("\n学生成绩管理系统\n");
    printf("1. 添加学生信息\n");
    printf("2. 修改学生信息\n");
    printf("3. 删除学生信息\n");
    printf("4. 显示所有学生\n");
    printf("5. 按平均分排序\n");
    printf("0. 退出系统\n");
    printf("请选择操作：");
}

int main() {
    StudentSystem sys;
    initSystem(&sys);
    
    int choice;
    do {
        showMenu();
        scanf("%d", &choice);
        
        switch (choice) {
            case 1:
                addStudent(&sys);
                break;
            case 2:
                modifyStudent(&sys);
                break;
            case 3:
                deleteStudent(&sys);
                break;
            case 4:
                displayAllStudents(&sys);
                break;
            case 5:
                sortByAverage(&sys);
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