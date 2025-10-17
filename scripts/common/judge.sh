#!/bin/bash
# 判题引擎 Bash 脚本
CFILE="$1"
TESTFILE="$2"
EXE="${CFILE%.c}.out"
gcc "$CFILE" -o "$EXE"
if [ $? -ne 0 ]; then
    echo "编译失败: $CFILE"
    exit 1
fi

while read test; do
    timeout 10s ./$EXE $test
    if [ $? -eq 0 ]; then
        echo -e "\033[32m通过: $test\033[0m"
    elif [ $? -eq 124 ]; then
        echo -e "\033[33m超时: $test\033[0m"
    else
        echo -e "\033[31m失败: $test\033[0m"
    fi
done < "$TESTFILE"
