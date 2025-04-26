#include <stdio.h>
#include <string.h>

// 定义账户类型枚举
typedef enum {
    SAVINGS,    // 储蓄账户
    CHECKING,   // 支票账户
    CREDIT     // 信用卡账户
} AccountType;

// 定义交易类型枚举
typedef enum {
    DEPOSIT,    // 存款
    WITHDRAW,   // 取款
    TRANSFER,   // 转账
    INTEREST    // 利息
} TransactionType;

// 定义交易记录结构体
typedef struct {
    int id;                     // 交易ID
    TransactionType type;       // 交易类型
    double amount;              // 交易金额
    char date[11];             // 交易日期
    char description[50];      // 交易描述
} Transaction;

// 定义银行账户结构体
typedef struct {
    int accountNumber;          // 账号
    char accountName[50];       // 账户名
    AccountType type;           // 账户类型
    double balance;             // 余额
    double interestRate;        // 利率
    Transaction history[100];   // 交易历史
    int transactionCount;       // 交易数量
} BankAccount;

// 创建新账户
BankAccount createAccount(int number, const char* name, AccountType type, double initialBalance) {
    BankAccount account;
    account.accountNumber = number;
    strcpy(account.accountName, name);
    account.type = type;
    account.balance = initialBalance;
    account.transactionCount = 0;
    
    // 设置利率
    switch (type) {
        case SAVINGS:
            account.interestRate = 0.02;  // 2%年利率
            break;
        case CHECKING:
            account.interestRate = 0.01;  // 1%年利率
            break;
        case CREDIT:
            account.interestRate = 0.15;  // 15%年利率
            break;
    }
    
    return account;
}

// 添加交易记录
void addTransaction(BankAccount* account, TransactionType type, double amount, const char* description) {
    if (account->transactionCount >= 100) {
        printf("警告：交易历史已满！\n");
        return;
    }
    
    Transaction* trans = &account->history[account->transactionCount++];
    trans->id = account->transactionCount;
    trans->type = type;
    trans->amount = amount;
    strcpy(trans->date, "2024-03-20");  // 简化日期处理
    strcpy(trans->description, description);
    
    // 更新余额
    switch (type) {
        case DEPOSIT:
        case INTEREST:
            account->balance += amount;
            break;
        case WITHDRAW:
        case TRANSFER:
            account->balance -= amount;
            break;
    }
}

// 计算利息
void calculateInterest(BankAccount* account) {
    double interest = account->balance * account->interestRate;
    addTransaction(account, INTEREST, interest, "利息计算");
}

// 打印账户信息
void printAccount(const BankAccount* account) {
    printf("\n账户信息:\n");
    printf("账号: %d\n", account->accountNumber);
    printf("账户名: %s\n", account->accountName);
    printf("账户类型: ");
    switch (account->type) {
        case SAVINGS: printf("储蓄账户\n"); break;
        case CHECKING: printf("支票账户\n"); break;
        case CREDIT: printf("信用卡账户\n"); break;
    }
    printf("余额: %.2f\n", account->balance);
    printf("利率: %.2f%%\n", account->interestRate * 100);
    printf("交易数量: %d\n", account->transactionCount);
    printf("------------------------\n");
}

// 打印交易历史
void printTransactionHistory(const BankAccount* account) {
    printf("\n交易历史:\n");
    for (int i = 0; i < account->transactionCount; i++) {
        const Transaction* trans = &account->history[i];
        printf("交易ID: %d\n", trans->id);
        printf("类型: ");
        switch (trans->type) {
            case DEPOSIT: printf("存款\n"); break;
            case WITHDRAW: printf("取款\n"); break;
            case TRANSFER: printf("转账\n"); break;
            case INTEREST: printf("利息\n"); break;
        }
        printf("金额: %.2f\n", trans->amount);
        printf("日期: %s\n", trans->date);
        printf("描述: %s\n", trans->description);
        printf("------------------------\n");
    }
}

int main() {
    printf("银行账户操作程序\n");
    printf("==============\n\n");

    // 创建账户
    BankAccount account = createAccount(1001, "张三", SAVINGS, 1000.0);
    
    // 显示初始账户信息
    printf("初始账户信息:\n");
    printAccount(&account);
    
    // 进行一些交易
    addTransaction(&account, DEPOSIT, 500.0, "工资存入");
    addTransaction(&account, WITHDRAW, 200.0, "取款");
    addTransaction(&account, TRANSFER, 300.0, "转账给李四");
    
    // 计算利息
    calculateInterest(&account);
    
    // 显示交易后的账户信息
    printf("\n交易后的账户信息:\n");
    printAccount(&account);
    
    // 显示交易历史
    printTransactionHistory(&account);

    return 0;
} 