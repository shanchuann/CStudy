# 练习4-2：计算阶乘和

## 题目描述
编写一个程序，计算1!+2!+...+n!的和，其中n由用户输入。

## 输入格式
- 输入一个正整数n

## 输出格式
- 按照"1!+2!+...+n! = 结果"的格式输出

## 示例
输入：
```
5
```
输出：
```
1!+2!+...+5! = 153
```

## 提示
1. 使用long long类型存储阶乘和结果，避免溢出
2. 使用一个变量factorial存储当前阶乘值
3. 使用一个变量sum存储阶乘和
4. 在循环中同时计算阶乘和累加
5. 注意n不要太大，避免结果溢出

## 学习要点
1. 大数处理
2. 循环结构
3. 数据类型选择
4. 溢出处理 