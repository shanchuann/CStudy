# 练习8.1：用指针实现数组逆序

## 题目描述
编写一个程序，使用指针实现数组的逆序操作。要求：
- 使用指针而不是数组下标来访问和修改数组元素
- 实现一个通用的逆序函数，可以处理任意大小的整型数组
- 保持原数组不变，返回逆序后的数组

## 要求
1. 实现一个函数`reverseArray`，接收数组指针和数组大小作为参数
2. 使用指针操作而不是数组下标来访问元素
3. 使用双指针技术实现逆序
4. 处理边界情况（空数组、单个元素等）
5. 提供数组打印功能用于验证结果

## 输入格式
- 第一行输入数组大小n（正整数）
- 第二行输入n个整数，用空格分隔

## 输出格式
- 第一行输出原始数组
- 第二行输出逆序后的数组

## 示例
输入：
```
5
1 2 3 4 5
```
输出：
```
原始数组: 1 2 3 4 5
逆序后的数组: 5 4 3 2 1
```

## 提示
1. 使用双指针技术（左右指针）
2. 注意指针的移动和边界条件
3. 考虑数组为空的情况
4. 注意指针运算的安全性
5. 可以扩展支持其他类型的数组 