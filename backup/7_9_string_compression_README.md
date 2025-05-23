# 练习7.9：字符串压缩和解压缩

## 题目描述
编写一个程序，实现字符串的压缩和解压缩功能。压缩规则如下：
- 如果连续字符相同，则用字符加上重复次数表示
- 如果字符只出现一次，则直接输出该字符
- 压缩后的字符串应该比原字符串短

例如：
- "aabcccccaaa" 压缩后为 "a2b1c5a3"
- "abcd" 压缩后为 "abcd"（因为压缩后反而变长，所以保持原样）

## 要求
1. 实现一个函数`compress`，接收一个字符串作为参数，返回压缩后的字符串
2. 实现一个函数`decompress`，接收压缩后的字符串作为参数，返回解压缩后的字符串
3. 使用动态内存分配
4. 处理空字符串的情况
5. 考虑内存泄漏问题

## 输入格式
- 输入一个字符串

## 输出格式
- 输出压缩后的字符串
- 输出解压缩后的字符串

## 示例
输入：
```
aabcccccaaa
```
输出：
```
压缩后的字符串: a2b1c5a3
解压缩后的字符串: aabcccccaaa
```

## 提示
1. 压缩时需要考虑字符重复次数
2. 解压缩时需要正确解析数字
3. 注意内存管理
4. 考虑边界情况
5. 可以添加压缩率检查 