#!/bin/bash
# 练习题列表与状态展示 Bash 脚本
EXERCISES_PATH="../Exercises"
doneCount=0
total=0
for ex in $(ls -d $EXERCISES_PATH/*/); do
    total=$((total+1))
    if [ -f "$ex/done.flag" ]; then
        doneCount=$((doneCount+1))
    fi
done
echo "完成进度: $doneCount/$total"
for ex in $(ls -d $EXERCISES_PATH/*/); do
    if [ -f "$ex/done.flag" ]; then
        status="已完成"
    else
        status="未完成"
    fi
    echo "练习: $(basename $ex) 状态: $status"
done
pass=0
fail=0
total=0
for ex in $(ls -d $EXERCISES_PATH/*/); do
    total=$((total+1))
    if [ -f "$ex/pass.flag" ]; then
        pass=$((pass+1))
    else
        fail=$((fail+1))
    fi
done
echo "批量检测结果: 通过 $pass, 失败 $fail, 总数 $total"
