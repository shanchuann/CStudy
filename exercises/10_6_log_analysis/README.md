# 日志文件分析（统计错误类型）

## 问题描述
编写一个程序，分析日志文件并统计不同类型的错误信息。程序需要能够识别日志中的错误类型，统计每种错误的出现次数和最后出现时间，并提供基本的日志统计信息。

## 要求
1. 实现以下功能：
   - 读取日志文件
   - 解析日志行格式
   - 统计错误类型
   - 统计日志级别
   - 显示分析结果

2. 程序特点：
   - 支持标准日志格式
   - 统计错误类型和次数
   - 记录最后出现时间
   - 提供基本统计信息
   - 处理文件读取错误

## 日志格式
日志行格式如下：
```
[时间戳] [日志级别] [错误类型] 消息内容
```
例如：
```
[2024-03-20 10:30:15] [ERROR] [DATABASE_CONNECTION] 无法连接到数据库
[2024-03-20 10:30:16] [WARNING] [MEMORY_USAGE] 内存使用率超过80%
[2024-03-20 10:30:17] [INFO] [SYSTEM_START] 系统启动完成
```

## 输入输出格式
### 输入
- 通过命令行参数指定：
  - 日志文件名

### 输出
- 显示分析结果，包含：
  - 基本统计信息（总行数、错误数等）
  - 错误类型统计（类型、次数、最后时间）
  - 统计表格形式展示

## 示例
```
日志文件分析程序
===============

开始分析日志文件...

日志分析结果
============

基本统计：
总行数: 100
错误行数: 15
警告行数: 25
信息行数: 60

错误类型统计：
----------------------------------------
错误类型                         出现次数    最后出现时间
----------------------------------------
DATABASE_CONNECTION             5          2024-03-20 10:30:15
FILE_NOT_FOUND                 3          2024-03-20 10:30:10
PERMISSION_DENIED              7          2024-03-20 10:30:12
----------------------------------------
```

## 提示
1. 使用结构体存储统计信息
2. 使用字符串处理函数解析日志
3. 注意文件指针的正确关闭
4. 处理各种错误情况
5. 验证输入参数的有效性 