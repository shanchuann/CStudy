#!/bin/bash
# 判题沙箱 Bash 脚本
EXE="$1"
echo "沙箱运行: $EXE (模拟)"
# 示例：可扩展ulimit等资源限制
ulimit -t 5 -v 1048576 # 限制CPU时间与虚拟内存
