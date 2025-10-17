#!/bin/bash
# 校验练习题文件格式 Bash 脚本
EXDIR="$1"
for f in description.md Test.txt metadata.json; do
    if [ ! -f "$EXDIR/$f" ]; then
        echo "缺少文件: $EXDIR/$f"
    else
        echo "文件存在: $EXDIR/$f"
    fi
done
