#!/bin/bash
# 自动检测并注册练习题 Bash 脚本
EXERCISES_PATH="../Exercises"
for ex in $(ls -d $EXERCISES_PATH/*/); do
    echo "检测到练习题: $(basename $ex)"
    # 可扩展：读取 description.md、Test.txt、metadata.json 校验
done
