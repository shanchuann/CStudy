# CStudy 系统初始化/重置脚本
# 用于重置所有练习状态，恢复到初始状态

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ExercisesPath = Join-Path $PSScriptRoot "..\Exercises"
$AIConfigPath = Join-Path $PSScriptRoot "..\AIserver\ai_enabled.txt"

Write-Host "=== CStudy 系统重置工具 ===" -ForegroundColor Cyan
Write-Host ""

# 1. 删除所有 done.flag 文件
Write-Host "正在删除所有 done.flag 文件..." -ForegroundColor Yellow
$exercises = Get-ChildItem -Path $ExercisesPath -Directory
$doneCount = 0
foreach ($ex in $exercises) {
    $doneFlag = Join-Path $ex.FullName "done.flag"
    if (Test-Path $doneFlag) {
        Remove-Item $doneFlag -Force
        $doneCount++
        Write-Host "  已删除: $($ex.Name)/done.flag" -ForegroundColor Gray
    }
}
Write-Host "✓ 已删除 $doneCount 个 done.flag 文件" -ForegroundColor Green

# 2. 恢复 Ques.c 为初始备份（Ques.c.bak）
Write-Host "`n正在恢复所有 Ques.c ..." -ForegroundColor Yellow
$restoreCount = 0
foreach ($ex in $exercises) {
    $cFile = Get-ChildItem -Path $ex.FullName -Filter "Ques.c" | Select-Object -First 1
    $bakFile = Get-ChildItem -Path $ex.FullName -Filter "Ques.c.bak" | Select-Object -First 1
    if ($cFile -and $bakFile) {
        Copy-Item -Path $bakFile.FullName -Destination $cFile.FullName -Force
        $restoreCount++
        Write-Host "  已恢复: $($ex.Name)/Ques.c" -ForegroundColor Gray
    } elseif ($cFile) {
        Write-Host "  未找到 Ques.c.bak，跳过: $($ex.Name)/Ques.c" -ForegroundColor DarkGray
    }
}
Write-Host "✓ 已恢复 $restoreCount 个 Ques.c 文件" -ForegroundColor Green

# 3. 清理编译生成的 .exe 文件
Write-Host "`n正在清理编译生成的 .exe 文件..." -ForegroundColor Yellow
$exeCount = 0
foreach ($ex in $exercises) {
    $exeFiles = Get-ChildItem -Path $ex.FullName -Filter "*.exe"
    foreach ($exe in $exeFiles) {
        Remove-Item $exe.FullName -Force
        $exeCount++
        Write-Host "  已删除: $($ex.Name)/$($exe.Name)" -ForegroundColor Gray
    }
}
Write-Host "✓ 已清理 $exeCount 个 .exe 文件" -ForegroundColor Green

# 4. 重置 AI 配置（可选）
Write-Host ""
$resetAI = Read-Host "是否重置 AI 配置？(y/n)"
if ($resetAI -eq "y" -or $resetAI -eq "Y") {
    if (Test-Path $AIConfigPath) {
        Remove-Item $AIConfigPath -Force
        Write-Host "✓ 已重置 AI 配置" -ForegroundColor Green
    } else {
        Write-Host "- AI 配置不存在，跳过" -ForegroundColor DarkGray
    }
} else {
    Write-Host "- 保留当前 AI 配置" -ForegroundColor DarkGray
}

Write-Host "`n=== 重置完成 ===" -ForegroundColor Cyan
Write-Host "所有练习已恢复到初始状态，可以开始学习了！" -ForegroundColor Green
Write-Host ""
Write-Host "运行 'scripts/cstudy.ps1' 开始学习" -ForegroundColor Yellow
