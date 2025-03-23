# 定义颜色
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Prompt = "Magenta"
    Title = "White"
    Task = "White"
    Points = "White"
}

# 定义路径
$ExercisesDir = "exercises"
$BackupDir = "backup"
$ProgressFile = ".progress"

# 从 README.md 文件读取练习信息
function Get-Exercises {
    $exercises = @()
    Get-ChildItem -Path $ExercisesDir -Directory | Sort-Object Name | ForEach-Object {
        $readmeFile = Join-Path $_.FullName "README.md"
        if (Test-Path $readmeFile) {
            $content = Get-Content $readmeFile -Raw
            $lines = $content -split "`n"
            
            # 解析标题
            $title = $lines[0].Trim()
            
            # 解析描述
            $description = ""
            $i = 1
            while ($i -lt $lines.Count -and $lines[$i].Trim() -ne "任务") {
                if ($lines[$i].Trim() -ne "") {
                    $description += $lines[$i] + "`n"
                }
                $i++
            }
            
            # 解析任务
            $task = ""
            $i++
            while ($i -lt $lines.Count -and $lines[$i].Trim() -ne "学习要点") {
                if ($lines[$i].Trim() -ne "") {
                    $task += $lines[$i] + "`n"
                }
                $i++
            }
            
            # 解析学习要点
            $points = ""
            $i++
            while ($i -lt $lines.Count) {
                if ($lines[$i].Trim() -ne "") {
                    $points += $lines[$i] + "`n"
                }
                $i++
            }
            
            $exercises += @{
                Name = $_.Name
                title = $title
                description = $description.Trim()
                task = $task.Trim()
                points = $points.Trim()
            }
        }
    }
    return $exercises
}

# 获取进度
function Get-Progress {
    if (Test-Path $ProgressFile) {
        $content = Get-Content $ProgressFile
        if ($content.Count -ge 2) {
            return @{
                CurrentIndex = [int]$content[0]
                Completed = $content[1..($content.Count-1)]
            }
        }
    }
    return @{
        CurrentIndex = 0
        Completed = @()
    }
}

# 保存进度
function Save-Progress {
    param (
        [int]$CurrentIndex,
        [string[]]$Completed
    )
    $content = @($CurrentIndex) + $Completed
    $content | Set-Content $ProgressFile
}

# 显示进度条
function Show-ProgressBar {
    param (
        [int]$Current,
        [int]$Total,
        [bool]$IsNewLine = $true
    )
    $percentage = [math]::Round(($Current / $Total) * 100)
    $barLength = 20
    $filledLength = [math]::Round(($Current / $Total) * $barLength)
    $bar = "=" * $filledLength + "×" * ($barLength - $filledLength)
    
    if ($IsNewLine) {
        Write-Host "`n进度: [$bar] $percentage% ($Current/$Total)`n" -ForegroundColor $Colors.Info
    } else {
        Write-Host "`r进度: [$bar] $percentage% ($Current/$Total)" -NoNewline -ForegroundColor $Colors.Info
    }
}

# 测试练习
function Test-Exercise {
    param (
        [string]$ExerciseDir
    )
    
    $mainFile = Join-Path $ExerciseDir "main.c"
    $expectedFile = Join-Path $ExerciseDir "expected.txt"
    
    if (-not (Test-Path $mainFile)) {
        Write-Host "❌ 错误：未找到 $mainFile" -ForegroundColor $Colors.Error
        Write-Host "请确保您已经创建了 main.c 文件。" -ForegroundColor $Colors.Warning
        return $false
    }
    
    if (-not (Test-Path $expectedFile)) {
        Write-Host "❌ 错误：未找到 $expectedFile" -ForegroundColor $Colors.Error
        Write-Host "请联系管理员，因为这是系统文件缺失的问题。" -ForegroundColor $Colors.Warning
        return $false
    }
    
    # 编译代码
    $outputFile = Join-Path $ExerciseDir "output.exe"
    $compileOutput = & gcc -o $outputFile $mainFile 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 编译错误：" -ForegroundColor $Colors.Error
        Write-Host $compileOutput
        Write-Host "`n💡 提示：请检查您的代码是否有语法错误。" -ForegroundColor $Colors.Warning
        return $false
    }
    
    # 运行程序
    $actualOutput = & $outputFile 2>&1
    $expectedOutput = Get-Content $expectedFile -Raw
    
    # 清理输出文件
    Remove-Item $outputFile -Force
    
    # 比较输出
    $actualLines = $actualOutput.TrimEnd() -split "`n"
    $expectedLines = $expectedOutput.TrimEnd() -split "`n"
    
    if ($actualLines.Count -ne $expectedLines.Count) {
        Write-Host "❌ 输出行数不匹配：" -ForegroundColor $Colors.Error
        Write-Host "期望：$($expectedLines.Count) 行"
        Write-Host "实际：$($actualLines.Count) 行"
        Write-Host "`n💡 提示：请检查您的输出是否包含了所有必要的行。" -ForegroundColor $Colors.Warning
        return $false
    }
    
    for ($i = 0; $i -lt $actualLines.Count; $i++) {
        if ($actualLines[$i].TrimEnd() -ne $expectedLines[$i].TrimEnd()) {
            Write-Host "❌ 第 $($i + 1) 行不匹配：" -ForegroundColor $Colors.Error
            Write-Host "期望：'$($expectedLines[$i].TrimEnd())'"
            Write-Host "实际：'$($actualLines[$i].TrimEnd())'"
            Write-Host "`n💡 提示：请仔细检查第 $($i + 1) 行的内容，确保与期望输出完全一致。" -ForegroundColor $Colors.Warning
            return $false
        }
    }
    
    return $true
}

# 备份初始代码
function Backup-InitialCode {
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir | Out-Null
    }
    
    foreach ($exercise in $exercises) {
        $exerciseDir = Join-Path $ExercisesDir $exercise.Name
        if (Test-Path $exerciseDir) {
            $files = @("main.c", "README.md", "expected.txt", "hints.txt")
            foreach ($file in $files) {
                $sourceFile = Join-Path $exerciseDir $file
                if (Test-Path $sourceFile) {
                    $backupFile = Join-Path $BackupDir "$($exercise.Name)_$file"
                    Copy-Item $sourceFile $backupFile -Force
                }
            }
        }
    }
}

# 恢复初始代码
function Restore-InitialCode {
    foreach ($exercise in $exercises) {
        Write-Host "`n恢复练习：$($exercise.Name)"
        $exerciseDir = Join-Path $ExercisesDir $exercise.Name
        if (Test-Path $exerciseDir) {
            $files = @("main.c", "README.md", "expected.txt", "hints.txt")
            foreach ($file in $files) {
                $backupFile = Join-Path $BackupDir "$($exercise.Name)_$file"
                $targetFile = Join-Path $exerciseDir $file
                if (Test-Path $backupFile) {
                    Copy-Item $backupFile $targetFile -Force
                    Write-Host "  ✅ 已恢复 $file"
                } else {
                    Write-Host "  ⚠️ 未找到 $file 的备份"
                }
            }
        }
    }
}

# 主函数
function Main {
    param (
        [string]$Command
    )
    
    # 获取练习列表
    $exercises = Get-Exercises
    
    switch ($Command) {
        "begin" {
            Write-Host "欢迎使用 CStudy！🎯" -ForegroundColor $Colors.Info            
            # 首次运行时备份初始代码
            if (-not (Test-Path $BackupDir)) {
                Backup-InitialCode
            }
            
            $progress = Get-Progress
            $currentIndex = $progress.CurrentIndex
            
            # 检查是否已完成所有练习
            if ($progress.Completed.Count -eq $exercises.Count) {
                Write-Host "`n🎉 恭喜！您已完成所有练习！" -ForegroundColor $Colors.Success
                Write-Host "如果您想重新开始，请使用 'reset' 命令重置进度。" -ForegroundColor $Colors.Info
                return
            }
            
            Show-ProgressBar $progress.Completed.Count $exercises.Count
            
            while ($currentIndex -lt $exercises.Count) {
                # 清除控制台
                Clear-Host
                
                $exercise = $exercises[$currentIndex]
                $exerciseDir = Join-Path $ExercisesDir $exercise.Name
                
                Write-Host "`n练习：$($exercise.Name)" -ForegroundColor $Colors.Points
                Write-Host "`n当前练习路径："
                Write-Host "练习目录："
                Write-Host $exerciseDir
                Write-Host "主文件："
                Write-Host (Join-Path $exerciseDir "main.c")
                Write-Host "`n$($exercise.description)" -ForegroundColor $Colors.Info
                Write-Host "`n任务" -ForegroundColor $Colors.Info
                Write-Host $exercise.task -ForegroundColor $Colors.Task
                Write-Host "`n学习要点" -ForegroundColor $Colors.Info
                Write-Host $exercise.points -ForegroundColor $Colors.Points
                
                Write-Host "`n输入 'v' 验证，'h' 获取提示，'n' 进入下一个练习，'q' 退出: " -NoNewline -ForegroundColor $Colors.Prompt
                
                $input = Read-Host
                switch ($input) {
                    "v" {
                        if (Test-Exercise $exerciseDir) {
                            Write-Host "`n✅ 恭喜！练习完成！" -ForegroundColor $Colors.Success
                            if (-not $progress.Completed.Contains($exercise.Name)) {
                                $progress.Completed += $exercise.Name
                                Show-ProgressBar $progress.Completed.Count $exercises.Count
                                Write-Host "✅ 进度已更新！" -ForegroundColor $Colors.Success
                            }
                            Write-Host "`n输入 'n' 进入下一个练习，'q' 退出: " -NoNewline -ForegroundColor $Colors.Prompt
                            $nextInput = Read-Host
                            switch ($nextInput) {
                                "n" {
                                    $currentIndex++
                                }
                                "q" {
                                    Save-Progress $currentIndex $progress.Completed
                                    Write-Host "`n已保存当前进度，下次继续时将从这里开始。" -ForegroundColor $Colors.Info
                                    return
                                }
                                default {
                                    Write-Host "`n无效的命令。请重试。" -ForegroundColor $Colors.Error
                                }
                            }
                        } else {
                            Write-Host "`n❌ 练习未通过，继续努力！" -ForegroundColor $Colors.Error
                            Write-Host "💡 提示：请仔细检查您的代码，确保输出与期望完全一致。如果遇到困难，可以输入 'h' 获取提示。" -ForegroundColor $Colors.Warning
                            Write-Host "`n按任意键继续..." -NoNewline
                            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
                            Clear-Host
                        }
                    }
                    "h" {
                        $hintsFile = Join-Path $exerciseDir "hints.txt"
                        if (Test-Path $hintsFile) {
                            Write-Host "`n💡 提示：" -ForegroundColor $Colors.Info
                            Get-Content $hintsFile | ForEach-Object {
                                Write-Host $_ -ForegroundColor $Colors.Info
                            }
                            Write-Host "`n按任意键继续..." -NoNewline
                            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
                            Clear-Host
                        } else {
                            Write-Host "`n⚠️ 未找到提示文件。" -ForegroundColor $Colors.Warning
                            Write-Host "`n按任意键继续..." -NoNewline
                            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
                            Clear-Host
                        }
                    }
                    "n" {
                        if (-not $progress.Completed.Contains($exercise.Name)) {
                            Write-Host "`n⚠️ 注意：未完成验证，进度未更新" -ForegroundColor $Colors.Warning
                        }
                        $currentIndex++
                        Show-ProgressBar $progress.Completed.Count $exercises.Count
                    }
                    "q" {
                        Save-Progress $currentIndex $progress.Completed
                        Write-Host "`n已保存当前进度，下次继续时将从这里开始。" -ForegroundColor $Colors.Info
                        return
                    }
                    default {
                        Write-Host "`n无效的命令。请重试。" -ForegroundColor $Colors.Error
                    }
                }
            }
            
            if ($progress.Completed.Count -eq $exercises.Count) {
                Write-Host "`n🎉 恭喜！您已完成所有练习！" -ForegroundColor $Colors.Success
            }
        }
        
        "reset" {
            Write-Host "欢迎使用 CStudy！🎯" -ForegroundColor $Colors.Info
            
            Write-Host "确定要重置所有练习进度吗？这将删除所有进度记录和编译文件。(y/n): " -NoNewline
            $confirm = Read-Host
            if ($confirm -eq "y") {
                Write-Host "`n开始恢复初始代码..." -ForegroundColor $Colors.Info
                Restore-InitialCode
                
                # 删除进度记录和编译文件
                if (Test-Path $ProgressFile) {
                    Remove-Item $ProgressFile -Force
                }
                
                # 删除所有练习目录中的编译文件
                Get-ChildItem -Path $ExercisesDir -Directory | ForEach-Object {
                    $exeFile = Join-Path $_.FullName "output.exe"
                    if (Test-Path $exeFile) {
                        Remove-Item $exeFile -Force
                    }
                }
                
                Write-Host "`n✅ 初始代码恢复完成" -ForegroundColor $Colors.Success
                Write-Host "✅ 已重置练习系统：" -ForegroundColor $Colors.Success
                Write-Host "  - 删除了进度记录" -ForegroundColor $Colors.Info
                Write-Host "  - 删除了所有编译文件" -ForegroundColor $Colors.Info
            }
        }
        
        "list" {
            Write-Host "欢迎使用 CStudy！🎯" -ForegroundColor $Colors.Info
            
            $progress = Get-Progress
            Write-Host "练习列表：`n" -ForegroundColor $Colors.Title
            
            for ($i = 0; $i -lt $exercises.Count; $i++) {
                $exercise = $exercises[$i]
                $status = if ($progress.Completed.Contains($exercise.Name)) { "✅" } else { "  " }
                Write-Host "$status $($i + 1). $($exercise.title)" -ForegroundColor $Colors.Info
            }
            
            Write-Host "`n输入练习编号继续，或输入 'q' 退出: " -NoNewline -ForegroundColor $Colors.Prompt
            $input = Read-Host
            
            if ($input -eq "q") {
                Write-Host "`n已退出练习列表。" -ForegroundColor $Colors.Info
                return
            }
            
            $index = [int]$input - 1
            if ($index -ge 0 -and $index -lt $exercises.Count) {
                $exercise = $exercises[$index]
                $progress.CurrentIndex = $index
                if (-not $progress.Completed.Contains($exercise.Name)) {
                    $progress.Completed = $progress.Completed | Where-Object { $_ -ne $exercise.Name }
                }
                Save-Progress $progress.CurrentIndex $progress.Completed
                Main "begin"
            } else {
                Write-Host "`n无效的练习编号。" -ForegroundColor $Colors.Error
            }
        }
        
        "verify" {
            Write-Host "欢迎使用 CStudy！🎯" -ForegroundColor $Colors.Info
            Write-Host "这是一个帮助您学习 C 语言的练习系统。`n" -ForegroundColor $Colors.Info
            
            $progress = Get-Progress
            $totalExercises = $exercises.Count
            $completedExercises = 0
            
            Write-Host "开始验证所有练习...`n" -ForegroundColor $Colors.Info
            
            foreach ($exercise in $exercises) {
                $exerciseDir = Join-Path $ExercisesDir $exercise.Name
                Write-Host "验证练习：$($exercise.title)" -ForegroundColor $Colors.Info
                
                if (Test-Exercise $exerciseDir) {
                    Write-Host "✅ 通过" -ForegroundColor $Colors.Success
                    if (-not $progress.Completed.Contains($exercise.Name)) {
                        $progress.Completed += $exercise.Name
                        $completedExercises++
                    }
                } else {
                    Write-Host "❌ 未通过" -ForegroundColor $Colors.Error
                }
            }
            
            if ($completedExercises -gt 0) {
                $progress.CurrentIndex = $progress.Completed.Count
                Save-Progress $progress.CurrentIndex $progress.Completed
                Write-Host "`n✅ 已更新进度！" -ForegroundColor $Colors.Success
            }
            
            $percentage = [math]::Round(($progress.Completed.Count / $totalExercises) * 100)
            Write-Host "`n完成情况：$($progress.Completed.Count)/$totalExercises ($percentage%)" -ForegroundColor $Colors.Info
            
            if ($progress.Completed.Count -eq $totalExercises) {
                Write-Host "`n🎉 恭喜！您已完成所有练习！" -ForegroundColor $Colors.Success
            } else {
                Write-Host "`n💪 继续加油！" -ForegroundColor $Colors.Info
            }
        }
        
        default {
            Write-Host "欢迎使用 CStudy！🎯" -ForegroundColor $Colors.Info
            Write-Host "这是一个帮助您学习 C 语言的练习系统。`n" -ForegroundColor $Colors.Info
            
            Write-Host "可用命令：" -ForegroundColor $Colors.Title
            Write-Host "  begin  - 开始练习" -ForegroundColor $Colors.Info
            Write-Host "  reset  - 重置所有练习" -ForegroundColor $Colors.Info
            Write-Host "  list   - 显示练习列表" -ForegroundColor $Colors.Info
            Write-Host "  verify - 验证所有练习" -ForegroundColor $Colors.Info
        }
    }
}

# 执行主函数
Main $args[0]