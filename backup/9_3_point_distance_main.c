#include <stdio.h>
#include <math.h>

// 点结构体
typedef struct {
    double x;    // x坐标
    double y;    // y坐标
} Point;

// 创建点
Point createPoint(double x, double y) {
    Point p = {x, y};
    return p;
}

// 打印点
void printPoint(Point p) {
    printf("(%.2f, %.2f)", p.x, p.y);
}

// 计算两点间距离
double calculateDistance(Point p1, Point p2) {
    double dx = p2.x - p1.x;
    double dy = p2.y - p1.y;
    return sqrt(dx * dx + dy * dy);
}

// 计算点到原点距离
double calculateDistanceToOrigin(Point p) {
    return sqrt(p.x * p.x + p.y * p.y);
}

// 计算两点间中点
Point calculateMidpoint(Point p1, Point p2) {
    Point mid = {
        (p1.x + p2.x) / 2,
        (p1.y + p2.y) / 2
    };
    return mid;
}

// 判断三点是否共线
int areCollinear(Point p1, Point p2, Point p3) {
    // 使用斜率判断
    double slope1 = (p2.y - p1.y) / (p2.x - p1.x);
    double slope2 = (p3.y - p2.y) / (p3.x - p2.x);
    
    // 考虑浮点数精度误差
    return fabs(slope1 - slope2) < 1e-10;
}

// 显示菜单
void showMenu() {
    printf("\n点坐标计算系统\n");
    printf("1. 计算两点间距离\n");
    printf("2. 计算点到原点距离\n");
    printf("3. 计算两点间中点\n");
    printf("4. 判断三点是否共线\n");
    printf("0. 退出系统\n");
    printf("请选择操作：");
}

// 输入点坐标
Point inputPoint() {
    Point p;
    printf("请输入x坐标：");
    scanf("%lf", &p.x);
    printf("请输入y坐标：");
    scanf("%lf", &p.y);
    return p;
}

int main() {
    int choice;
    Point p1, p2, p3;
    
    do {
        showMenu();
        scanf("%d", &choice);
        
        switch (choice) {
            case 1:
                printf("请输入第一个点：\n");
                p1 = inputPoint();
                printf("请输入第二个点：\n");
                p2 = inputPoint();
                
                printf("点");
                printPoint(p1);
                printf("和点");
                printPoint(p2);
                printf("之间的距离为：%.2f\n", calculateDistance(p1, p2));
                break;
                
            case 2:
                printf("请输入点：\n");
                p1 = inputPoint();
                
                printf("点");
                printPoint(p1);
                printf("到原点的距离为：%.2f\n", calculateDistanceToOrigin(p1));
                break;
                
            case 3:
                printf("请输入第一个点：\n");
                p1 = inputPoint();
                printf("请输入第二个点：\n");
                p2 = inputPoint();
                
                Point mid = calculateMidpoint(p1, p2);
                printf("点");
                printPoint(p1);
                printf("和点");
                printPoint(p2);
                printf("的中点为：");
                printPoint(mid);
                printf("\n");
                break;
                
            case 4:
                printf("请输入第一个点：\n");
                p1 = inputPoint();
                printf("请输入第二个点：\n");
                p2 = inputPoint();
                printf("请输入第三个点：\n");
                p3 = inputPoint();
                
                if (areCollinear(p1, p2, p3)) {
                    printf("这三个点共线！\n");
                } else {
                    printf("这三个点不共线！\n");
                }
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