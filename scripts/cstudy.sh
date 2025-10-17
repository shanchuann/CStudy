#!/bin/bash
# CStudy 主入口 Bash 脚本
# UTF-8编码，自动检测平台，调用核心模块

export LANG="en_US.UTF-8"
echo "CStudy (Bash) - Interactive C Programming Platform"
echo "可用命令: list, judge, progress, batch, aimodel"
read -p "请输入命令: " cmd
case $cmd in
    list)
        bash ./common/list_exercises.sh
        ;;
    judge)
        read -p "输入练习名: " ex
        bash ./common/judge.sh "../Exercises/$ex/$ex.c" "../Exercises/$ex/Test.txt"
        ;;
    progress)
        bash ./common/list_exercises.sh
        ;;
    batch)
        for ex in $(ls -d ../Exercises/*/); do
            echo "批量检测: $(basename $ex)"
            bash ./common/judge.sh "$ex/$(basename $ex).c" "$ex/Test.txt"
        done
        ;;
    goto)
        read -p "输入失败练习名: " ex
        xdg-open "../Exercises/$ex/$ex.c"
        ;;
    aihelp)
        read -p "输入练习名: " ex
        code=$(cat "../Exercises/$ex/$ex.c")
        desc=$(cat "../Exercises/$ex/description.md")
        test=$(cat "../Exercises/$ex/Test.txt")
        bash ./common/ai_helper.sh "$code" "$desc" "$test"
        ;;
    aimodel)
        echo "AI模型管理: list, download, switch, remove"
        read -p "请输入模型管理命令: " cmd
        case $cmd in
            list)
                ls ../AIserver/model
                ;;
            download)
                echo "下载模型（模拟）"
                ;;
            switch)
                echo "切换模型（模拟）"
                ;;
            remove)
                echo "删除模型（模拟）"
                ;;
            *)
                echo "未知模型管理命令"
                ;;
        esac
        ;;
    *)
        echo "未知命令"
        ;;
esac
# ...后续实现: 练习检测、判题、AI辅助等
