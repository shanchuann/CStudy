# 练习8.4：用指针操作实现strcat函数

## 题目描述
编写一个程序，使用指针操作实现字符串连接函数strcat。要求：
- 使用指针而不是数组下标来访问字符串
- 实现与标准库strcat相同的功能
- 处理各种边界情况
- 确保字符串正确终止

## 要求
1. 实现`my_strcat`函数
   - 接收目标字符串和源字符串作为参数
   - 使用指针操作访问字符串
   - 返回目标字符串的起始位置
   - 处理字符串结束符

2. 实现测试函数
   - 测试基本字符串连接
   - 测试空字符串
   - 测试长字符串
   - 测试边界情况

3. 使用const修饰只读参数
4. 添加参数有效性检查
5. 提供清晰的输出格式

## 输入格式
- 程序内部提供测试数据
- 使用预定义的字符串进行测试
- 包含多种情况的测试用例

## 输出格式
- 显示每个测试用例的输入字符串
- 显示连接后的结果
- 使用适当的格式化输出

## 示例
输出：
```
测试用例1：
str1: Hello, 
str2: World!
连接后: Hello, World!

测试用例2：
str3: 
str4: Empty string test
连接后: Empty string test

测试用例3：
str5: Non-empty string
str6: 
连接后: Non-empty string

测试用例4：
str7: This is a very long string that 
str8: will be concatenated with another long string.
连接后: This is a very long string that will be concatenated with another long string.
```

## 提示
1. 使用指针遍历字符串
2. 注意字符串结束符
3. 处理边界情况
4. 考虑缓冲区溢出
5. 可以添加安全检查 