# 练习4-5：打印空心菱形

## 题目描述
编写一个程序，根据用户输入的高度（奇数），打印一个由星号组成的空心菱形图案。

## 输入格式
- 输入一个奇数n，表示菱形的高度

## 输出格式
- 如果输入无效（不是奇数），输出错误提示
- 如果输入有效，打印空心菱形图案
- 每行末尾不要有多余的空格

## 示例
输入：
```
5
```
输出：
```
  *
 * *
*   *
 * *
  *
```

## 提示
1. 输入验证：确保输入的是奇数
2. 将菱形分为上下两部分处理
3. 每行需要打印：
   - 前导空格
   - 星号和空格
4. 空格数量规律：
   - 前导空格：n/2 + 1 - i
   - 星号之间空格：2*i - 3
5. 星号位置：
   - 每行首尾是星号
   - 中间是空格

## 学习要点
1. 循环嵌套
2. 图案打印
3. 输入验证
4. 数学规律应用 