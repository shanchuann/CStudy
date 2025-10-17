#!/bin/bash
# AI助手 Bash 脚本
CODE="$1"
DESC="$2"
TEST="$3"
echo "AI分析中..."
# 实际应调用AIserver或ollama
echo "AI建议: 检查循环边界，变量初始化。"
echo -n "是否自动应用建议？(y/n): "
read apply
if [ "$apply" = "y" ]; then
    backup="/tmp/backup_$(date +%Y%m%d%H%M%S).c"
    cp "$CODE" "$backup"
    echo "已备份原代码到: $backup"
    # 示例：写入建议代码（实际应为AI返回内容）
    echo "// 建议代码示例
$CODE" > "$CODE"
fi

if ! command -v ollama &> /dev/null; then
    echo "未检测到ollama，请安装：https://ollama.com"
fi
