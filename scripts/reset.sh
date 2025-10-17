#!/bin/bash
# CStudy 系统初始化/重置脚本
# 用于重置所有练习状态，恢复到初始状态

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXERCISES_PATH="$SCRIPT_DIR/../Exercises"
AI_CONFIG_PATH="$SCRIPT_DIR/../AIserver/ai_enabled.txt"

echo "=== CStudy 系统重置工具 ==="
echo ""

# 1. 删除所有 done.flag 文件
echo "正在删除所有 done.flag 文件..."
done_count=0
for ex_dir in "$EXERCISES_PATH"/*/; do
    if [ -f "$ex_dir/done.flag" ]; then
        rm -f "$ex_dir/done.flag"
        done_count=$((done_count + 1))
        echo "  已删除: $(basename "$ex_dir")/done.flag"
    fi
done
echo "✓ 已删除 $done_count 个 done.flag 文件"

# 2. 确保所有 Ques.c 文件第一行有 //I'm Ok 注释
echo ""
echo "正在检查并添加 //I'm Ok 注释..."
added_count=0
for ex_dir in "$EXERCISES_PATH"/*/; do
    c_file=$(find "$ex_dir" -maxdepth 1 -name "*.c" | head -n 1)
    if [ -n "$c_file" ]; then
        first_line=$(head -n 1 "$c_file")
        if [[ "$first_line" != *"//I'm Ok"* ]]; then
            # 在文件开头添加 //I'm Ok
            echo "//I'm Ok" | cat - "$c_file" > temp && mv temp "$c_file"
            added_count=$((added_count + 1))
            echo "  已添加: $(basename "$ex_dir")/$(basename "$c_file")"
        else
            echo "  已存在: $(basename "$ex_dir")/$(basename "$c_file")"
        fi
    fi
done
echo "✓ 已添加 $added_count 个 //I'm Ok 注释"

# 3. 清理编译生成的 .exe 文件
echo ""
echo "正在清理编译生成的 .exe 和可执行文件..."
exe_count=0
for ex_dir in "$EXERCISES_PATH"/*/; do
    for exe_file in "$ex_dir"/*.exe "$ex_dir"/*.out; do
        if [ -f "$exe_file" ]; then
            rm -f "$exe_file"
            exe_count=$((exe_count + 1))
            echo "  已删除: $(basename "$ex_dir")/$(basename "$exe_file")"
        fi
    done
done
echo "✓ 已清理 $exe_count 个可执行文件"

# 4. 重置 AI 配置（可选）
echo ""
read -p "是否重置 AI 配置？(y/n) " reset_ai
if [[ "$reset_ai" == "y" || "$reset_ai" == "Y" ]]; then
    if [ -f "$AI_CONFIG_PATH" ]; then
        rm -f "$AI_CONFIG_PATH"
        echo "✓ 已重置 AI 配置"
    else
        echo "- AI 配置不存在，跳过"
    fi
else
    echo "- 保留当前 AI 配置"
fi

echo ""
echo "=== 重置完成 ==="
echo "所有练习已恢复到初始状态，可以开始学习了！"
echo ""
echo "运行 'scripts/cstudy.sh' 开始学习"
