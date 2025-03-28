# 实现文件内容统计

## 问题描述
编写一个程序，统计文本文件的行数、字数和字符数。程序需要能够处理各种文本文件，并准确计算这些基本统计信息。

## 要求
1. 定义文件统计结构体，包含：
   - 行数
   - 字数
   - 字符数
2. 实现以下功能：
   - 打开并读取文件
   - 统计行数（以换行符为准）
   - 统计字数（以空白字符分隔）
   - 统计字符数（包括所有字符）
   - 显示统计结果

## 输入输出格式
### 输入
- 通过命令行参数指定要统计的文件名
- 程序需要处理文件不存在的情况

### 输出
- 显示统计结果，包含：
  - 文件名
  - 行数
  - 字数
  - 字符数
- 格式示例：
  ```
  文件统计结果:
  文件名: test.txt
  行数: 10
  字数: 50
  字符数: 200
  ```

## 示例
```
文件内容统计程序
===============

文件统计结果:
文件名: test.txt
行数: 5
字数: 20
字符数: 100
------------------------
```

## 提示
1. 使用结构体组织统计数据
2. 注意文件打开和关闭
3. 处理特殊字符和边界情况
4. 考虑大文件的处理
5. 使用适当的错误处理 