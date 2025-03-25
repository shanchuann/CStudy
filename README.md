# CStudy 🎯

欢迎使用 CStudy！这是一个帮助您学习 C 语言的项目，包含了一系列小练习，帮助您熟悉 C 语言的编程。这些练习包括阅读和编写 C 代码，以及理解和解决编译错误！

建议您在学习 C 语言的同时使用这个练习系统，配合阅读 C 语言教程或书籍 📚️

## 开始使用

### 安装要求

在开始使用 CStudy 之前，请确保您的系统已安装：

1. Windows 操作系统
2. PowerShell 7.0 或更高版本
3. GCC 编译器
   - 如果您还没有安装 GCC，请访问 [MinGW-w64](https://www.mingw-w64.org/) 下载并安装
   - 安装后请确保将 GCC 添加到系统环境变量中
4. Ollama（用于AI辅助功能，可选）
   - 从 [Ollama官网](https://ollama.ai) 下载并安装
   - 下载 deepseek-coder:6.7b 模型：`ollama pull deepseek-coder:6.7b`

### 安装 CStudy

1. 下载或克隆此仓库到本地
2. 将仓库目录添加到系统环境变量 PATH 中（可选）

### 初始化

1. 打开 PowerShell 或命令提示符
2. 进入 CStudy 目录
3. 运行以下命令开始练习：

```powershell
.\CStudy begin
```

## 工作环境

### 编辑器推荐

我们推荐使用支持 C 语言的编辑器，如：

- Visual Studio Code + C/C++ 扩展

- CLion

## 练习方式

### 练习列表

练习按主题分类，位于 `exercises/` 目录下。每个主题都有一个 `README.md` 文件，包含该主题的学习资源和说明。我们强烈建议您在开始练习前先阅读这些资源 📚️

### 练习内容

大多数练习都包含一些需要修复的错误，您需要：

1. 阅读练习说明
2. 修改代码
3. 编译并运行
4. 确保输出符合预期

### 交互模式

运行 `.\CStudy begin` 进入交互模式，系统会：

- 按预设顺序引导您完成练习
- 自动检测文件变化
- 提供实时反馈

### 可用命令

#### 系统外

- `.\CStudy begin` - 开始练习
- `.\CStudy reset` - 重置进度
- `.\CStudy list` - 显示列表
- `.\CStudy verify` - 验证所有练习
- `.\CStudy help` - 显示帮助信息

#### 系统内

- `t` - 测试当前练习
- `h` - 显示提示
- `a` - 使用AI辅助
- `n` - 跳转到下一个练习
- `q` - 退出练习

### AI辅助功能（可选）

CStudy 集成了基于 Ollama 的 AI 辅助功能，可以帮助您更好地理解和完成练习：

1. **使用方法**
   - 在练习界面按 `a` 进入AI辅助模式
   - 选择需要的帮助类型：
     1. 解题思路分析
     2. 代码实现指导
     3. 知识点讲解

2. **功能特点**
   - 智能分析题目要求
   - 提供针对性的解题思路
   - 讲解相关知识点
   - 给出代码实现指导（不直接提供完整答案）

3. **注意事项**
   - 首次使用时会自动启动 Ollama 服务
   - 确保 deepseek-coder:6.7b 模型已正确安装
   - AI 回答可能需要几秒钟的处理时间

## 目录结构

```txt
CStudy/
├── exercises/           # 练习目录
│   └── 01_hello_world/ # 第一个练习
│       ├── README.md   # 练习描述
│       ├── main.c      # 需要修改的代码
│       ├── hints.txt   # 练习提示
│       └── expected.txt # 期望输出
├── CStudy.bat          # 批处理启动脚本
├── CStudy.ps1          # PowerShell 主脚本
└── README.md           # 本文件
```

## 常见问题

### 如果遇到权限问题

请以管理员身份运行 PowerShell，或运行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 如果遇到编译错误

1. 确保 GCC 已正确安装
2. 检查环境变量是否正确设置
3. 尝试重新打开终端

### 如果AI功能无法使用

1. 确保 Ollama 已正确安装
2. 检查是否已下载 deepseek-coder:6.7b 模型
3. 确认 Ollama 服务是否正在运行
4. 检查 AI_Server 目录是否存在且包含必要文件

## 继续学习

完成 CStudy 的练习后，您可以：

1. 开始自己的 C 语言项目
2. 参与开源项目
3. 深入学习 C 语言的高级特性

## 卸载

如果您想删除 CStudy，只需删除整个目录即可。
