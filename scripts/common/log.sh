#!/bin/bash
# 日志与错误处理 Bash 脚本
log() {
    local level="$1"
    local msg="$2"
    local ts=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$ts][$level] $msg"
}
