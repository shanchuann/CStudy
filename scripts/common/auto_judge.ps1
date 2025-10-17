# 自动判题与自动跳转 PowerShell 脚本（模仿 rustlings 的 //I'm Ok 机制）
param([string]$ExerciseDir)
# 以传入练习目录的父级作为 Exercises 根目录，避免路径定位到 scripts/Exercises
$ExercisesPath = Split-Path $ExerciseDir -Parent
function Show-Progress {
    $exercises = Get-ChildItem -Path $ExercisesPath -Directory
    $doneCount = 0
    $total = $exercises.Count
    foreach ($ex in $exercises) {
        $done = Test-Path (Join-Path $ex.FullName "done.flag")
        if ($done) { $doneCount++ }
    }
    $barLength = 30
    $doneBar = if ($total -eq 0) {0} else {[math]::Floor($doneCount/$total*$barLength)}
    $undoneBar = $barLength - $doneBar
    $progressBar = "=" * $doneBar + "*" * $undoneBar
    Write-Host "练习完成进度: [$progressBar]($doneCount/$total)"
}

$lastWrite = (Get-Item "$ExerciseDir\Ques.c").LastWriteTime
$lastPassed = $false
while ($true) {
    Start-Sleep -Seconds 2
    $currentWrite = (Get-Item "$ExerciseDir\Ques.c").LastWriteTime
    $inputCmd = $null
    Clear-Host
    Write-Host "CStudy (PowerShell) - Interactive C Programming Platform"
    Show-Progress
    $commands = "check, list, AI, help me, quit"
    Write-Host "命令: $commands"
    $exName = Split-Path $ExerciseDir -Leaf
    $cFile = Get-ChildItem -Path $ExerciseDir -Filter "*.c" | Select-Object -First 1
    if ($cFile) {
        Write-Host "练习: $exName 状态: 未完成 $($cFile.FullName)" -ForegroundColor Yellow
        $descPath = Join-Path $ExerciseDir "description.md"
        if (Test-Path $descPath) {
            Write-Host "`n题目描述" -ForegroundColor Magenta
            Get-Content $descPath | Write-Host
        }
    }
    if ($currentWrite -ne $lastWrite) {
        $cFile = Get-ChildItem -Path $ExerciseDir -Filter "*.c" | Select-Object -First 1
        if ($cFile) {
            # 检查第一行是否还有 //I'm Ok
            $firstLine = Get-Content $cFile.FullName -First 1
            $hasMarker = $firstLine -match "//I'm Ok"
            # 如果上次通过且现在删除了注释，则标记完成并跳转
            if ($lastPassed -and -not $hasMarker) {
                Set-Content "$ExerciseDir/done.flag" "done"
                Write-Host "已删除注释 //I'm Ok，练习标记为完成！" -ForegroundColor Green
                Write-Host "自动检查所有练习..." -ForegroundColor Cyan
                & "$PSScriptRoot/../cstudy.ps1"
                break
            }
            # 否则，执行判题
            Write-Host "检测到 Ques.c 已保存，自动判题..." -ForegroundColor Cyan
            & "$PSScriptRoot/judge.ps1" $cFile.FullName "$ExerciseDir/Test.txt"
            $passed = $LASTEXITCODE -eq 0
            if ($passed) {
                Write-Host "✓ 判题通过！请删除注释 //I'm Ok 以完成练习。" -ForegroundColor Green
                $lastPassed = $true
            } else {
                Write-Host "✗ 判题未通过，请继续修改代码。" -ForegroundColor Red
                $lastPassed = $false
            }
        }
        $lastWrite = $currentWrite
    }
    Write-Host "输入命令 (check, list, AI, help me, quit) 或直接回车继续监听..." -ForegroundColor Yellow
    $inputCmd = Read-Host
    if ($inputCmd) {
        $shouldQuit = $false
        switch ($inputCmd) {
            "check" {
                $cFile = Get-ChildItem -Path $ExerciseDir -Filter "*.c" | Select-Object -First 1
                if ($cFile) {
                    & "$PSScriptRoot/judge.ps1" $cFile.FullName "$ExerciseDir/Test.txt"
                } else {
                    Write-Host "未找到 C 文件" -ForegroundColor Red
                }
            }
            "list" {
                & "$PSScriptRoot/list_exercises.ps1"
            }
            "AI" {
                # 调用主入口进行模型管理（路径位于 scripts 层级）
                & "$PSScriptRoot/../cstudy.ps1"
            }
            "help me" {
                $desc = Join-Path $ExerciseDir "description.md"
                $test = Join-Path $ExerciseDir "Test.txt"
                $cFile = Get-ChildItem -Path $ExerciseDir -Filter "*.c" | Select-Object -First 1
                if ($cFile -and (Test-Path $desc) -and (Test-Path $test)) {
                    & "$PSScriptRoot/ai_helper.ps1" -Code $cFile.FullName -Desc $desc -Test $test
                } else {
                    Write-Host "练习目录缺少必要文件" -ForegroundColor Red
                }
            }
            "quit" {
                Write-Host "退出监听模式。" -ForegroundColor Green
                $shouldQuit = $true
            }
            default {
                if ($inputCmd -ne "") {
                    Write-Host "未知命令，继续监听..." -ForegroundColor Gray
                }
            }
        }
        Start-Sleep -Milliseconds 800
        if ($shouldQuit) { break }
        Clear-Host
    }
}