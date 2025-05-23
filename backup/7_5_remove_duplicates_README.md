# 练习7.5：去除字符串中的重复字符

## 题目描述
编写一个程序，去除字符串中的重复字符，只保留每个字符的第一次出现。例如，字符串"hello"去除重复字符后变成"helo"。要求不使用额外的数组空间，直接在原字符串上进行修改。

## 要求
1. 实现一个函数`removeDuplicates`，接收字符串作为参数
2. 不使用额外的数组空间
3. 保持字符的相对顺序
4. 处理空字符串和NULL的情况
5. 正确处理字符串结束符

## 输入格式
- 输入一行字符串

## 输出格式
- 输出去除重复字符后的字符串

## 示例
输入：
```
hello world
```
输出：
```
去除重复字符后的字符串: helo wrd
```

## 提示
1. 使用双指针技术
2. 使用writeIndex记录写入位置
3. 检查字符是否已经出现过
4. 注意字符串结束符的处理
5. 考虑使用更安全的输入函数 