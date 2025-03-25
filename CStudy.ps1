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
    AI = "Blue"
}

# 定义路径
$ExercisesDir = "exercises"
$BackupDir = "backup"
$ProgressFile = ".progress"
$OllamaPath = "AI_Server"  # 添加Ollama路径
$UseAI = $false  # 添加AI功能开关
$AIConfigFile = ".aiconfig"  # 添加AI配置文件

# 启动Ollama服务
function Start-OllamaService {
    try {
        # 检查是否已经有AI配置
        if (Test-Path $AIConfigFile) {
            $script:UseAI = (Get-Content $AIConfigFile) -eq "true"
            
            # 如果用户之前选择不使用AI，直接返回
            if (-not $script:UseAI) {
                Write-Host "已禁用AI功能。您可以随时通过重置系统来重新启用。" -ForegroundColor $Colors.Info
                return $true
            }
        }
        # 首次运行时询问是否使用AI功能
        elseif (-not (Test-Path $ProgressFile)) {
            Write-Host "`n是否启用AI辅助功能？这将需要下载约4GB的AI模型。(y/n): " -NoNewline -ForegroundColor $Colors.Prompt
            $useAIInput = Read-Host
            $script:UseAI = $useAIInput.ToLower() -eq 'y'
            
            # 保存AI配置
            $script:UseAI.ToString().ToLower() | Set-Content $AIConfigFile
            
            if (-not $script:UseAI) {
                Write-Host "已禁用AI功能。您可以随时通过重置系统来重新启用。" -ForegroundColor $Colors.Info
                return $true
            }
        }
        
        # 如果不使用AI功能，直接返回
        if (-not $script:UseAI) {
            return $true
        }
        
        # 检查Ollama服务是否已经运行
        $testConnection = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -ErrorAction SilentlyContinue
        if ($null -eq $testConnection) {
            Write-Host "正在启动Ollama服务..." -ForegroundColor $Colors.Info
            
            # 启动Ollama服务
            $ollamaExe = Join-Path $OllamaPath "ollama.exe"
            if (-not (Test-Path $ollamaExe)) {
                Write-Host "❌ 未找到Ollama可执行文件，尝试在系统路径中查找..." -ForegroundColor $Colors.Warning
                $ollamaExe = "ollama.exe"
            }
            
            try {
                # 尝试启动Ollama服务
                Start-Process -FilePath $ollamaExe -WindowStyle Hidden
                Write-Host "✅ Ollama服务启动命令已发送" -ForegroundColor $Colors.Success
                
                # 等待服务启动
                $retryCount = 0
                $maxRetries = 15  # 增加等待时间到30秒
                do {
                    Start-Sleep -Seconds 2
                    $retryCount++
                    try {
                        $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get
                        Write-Host "✅ Ollama服务已成功启动" -ForegroundColor $Colors.Success
                        
                        # 检查模型是否已下载
                        $models = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get
                        $modelExists = $models.models | Where-Object { $_.name -eq "deepseek-coder:6.7b" }
                        
                        if (-not $modelExists) {
                            Write-Host "正在下载 deepseek-coder:6.7b 模型..." -ForegroundColor $Colors.Info
                            Write-Host "下载可能需要几分钟时间，请耐心等待..." -ForegroundColor $Colors.Warning
                            $pullProcess = Start-Process -FilePath $ollamaExe -ArgumentList "pull deepseek-coder:6.7b" -NoNewWindow -Wait -PassThru
                            if ($pullProcess.ExitCode -eq 0) {
                                Write-Host "✅ 模型下载完成" -ForegroundColor $Colors.Success
                            } else {
                                Write-Host "❌ 模型下载失败" -ForegroundColor $Colors.Error
                                $script:UseAI = $false
                            }
                        }
                        
                        break
                    } catch {
                        if ($retryCount -eq $maxRetries) {
                            Write-Host "❌ Ollama服务启动失败" -ForegroundColor $Colors.Error
                            $script:UseAI = $false
                            return $false
                        }
                        Write-Host "等待服务启动中... ($retryCount/$maxRetries)" -ForegroundColor $Colors.Info
                    }
                } while ($retryCount -lt $maxRetries)
            } catch {
                Write-Host "❌ 无法启动Ollama服务：$($_.Exception.Message)" -ForegroundColor $Colors.Error
                $script:UseAI = $false
                return $false
            }
        } else {
            Write-Host "✅ Ollama服务已在运行" -ForegroundColor $Colors.Success
            
            # 检查模型是否存在
            $models = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get
            $modelExists = $models.models | Where-Object { $_.name -eq "deepseek-coder:6.7b" }
            
            if (-not $modelExists) {
                Write-Host "正在下载 deepseek-coder:6.7b 模型..." -ForegroundColor $Colors.Info
                Write-Host "下载可能需要几分钟时间，请耐心等待..." -ForegroundColor $Colors.Warning
                $ollamaExe = Join-Path $OllamaPath "ollama.exe"
                if (-not (Test-Path $ollamaExe)) {
                    $ollamaExe = "ollama.exe"
                }
                $pullProcess = Start-Process -FilePath $ollamaExe -ArgumentList "pull deepseek-coder:6.7b" -NoNewWindow -Wait -PassThru
                if ($pullProcess.ExitCode -eq 0) {
                    Write-Host "✅ 模型下载完成" -ForegroundColor $Colors.Success
                } else {
                    Write-Host "❌ 模型下载失败" -ForegroundColor $Colors.Error
                    $script:UseAI = $false
                }
            }
        }
        return $true
    } catch {
        Write-Host "❌ 无法启动Ollama服务：$($_.Exception.Message)" -ForegroundColor $Colors.Error
        $script:UseAI = $false
        return $false
    }
}

# 从 README.md 文件读取练习信息
function Get-Exercises {
    $exercises = @()
    Get-ChildItem -Path $ExercisesDir -Directory | ForEach-Object {
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
            
            # 解析章节和练习编号
            $nameParts = $_.Name -split '_'
            $chapter = [int]$nameParts[0]
            $exercise = [int]$nameParts[1]
            
            $exercises += @{
                Name = $_.Name
                Chapter = $chapter
                Exercise = $exercise
                title = $title
                description = $description.Trim()
                task = $task.Trim()
                points = $points.Trim()
            }
        }
    }
    
    # 按照章节和练习编号排序
    return $exercises | Sort-Object { $_.Chapter }, { $_.Exercise }
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
    $barLength = 30
    $filledLength = [math]::Round(($Current / $Total) * $barLength)
    $bar = "█" * $filledLength + "░" * ($barLength - $filledLength)
    
    # 根据完成百分比选择颜色
    $color = if ($percentage -eq 100) { $Colors.Success }
             elseif ($percentage -ge 80) { "Green" }
             elseif ($percentage -ge 60) { "Cyan" }
             elseif ($percentage -ge 40) { "Yellow" }
             elseif ($percentage -ge 20) { "DarkYellow" }
             else { "Red" }
    
    # 清除整个屏幕
    Clear-Host
    
    # 显示进度条
    Write-Host "进度: [$bar] $percentage% ($Current/$Total)`n" -ForegroundColor $color
}

# 清除进度条
function Clear-ProgressBar {
    # 清除整个屏幕
    Clear-Host
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

# 调用Ollama API获取AI回答
function Get-AIResponse {
    param (
        [string]$Prompt
    )
    
    $uri = "http://localhost:11434/api/generate"
    $body = @{
        model = "deepseek-coder:6.7b"
        prompt = $Prompt
        stream = $false
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/json"
        return $response.response
    }
    catch {
        Write-Host "❌ 无法连接到Ollama服务。请确保：" -ForegroundColor $Colors.Error
        Write-Host "1. Ollama已经安装并运行" -ForegroundColor $Colors.Warning
        Write-Host "2. deepseek-coder:6.7b模型已经下载" -ForegroundColor $Colors.Warning
        Write-Host "3. Ollama服务运行在默认端口(11434)" -ForegroundColor $Colors.Warning
        return $null
    }
}

# 显示AI辅助菜单
function Show-AIHelp {
    param (
        [hashtable]$Exercise
    )
    
    if (-not $script:UseAI) {
        Write-Host "`n❌ AI功能未启用。如需使用，请重置系统并在初始化时选择启用AI功能。" -ForegroundColor $Colors.Warning
        Write-Host "`n按任意键继续..." -ForegroundColor $Colors.Prompt
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        return
    }
    
    Clear-Host
    Write-Host "🤖 AI辅助模式" -ForegroundColor $Colors.AI
    Write-Host "===================" -ForegroundColor $Colors.AI
    Write-Host "`n当前题目：" -ForegroundColor $Colors.Title
    Write-Host $Exercise.title -ForegroundColor $Colors.Task
    
    Write-Host "`n任务描述：" -ForegroundColor $Colors.Title
    Write-Host $Exercise.task -ForegroundColor $Colors.Task
    
    Write-Host "`n请选择需要AI帮助的类型：" -ForegroundColor $Colors.Prompt
    Write-Host "[ 1:解题思路 | 2:代码指导 | 3:知识讲解 | 4:返回 ]" -ForegroundColor $Colors.Info
    
    $choice = Read-Host "`n请输入选择(1-4)"
    
    switch ($choice) {
        "1" {
            $prompt = "请分析以下C语言题目的解题思路：`n`n题目：$($Exercise.title)`n`n任务：$($Exercise.task)`n`n请给出详细的解题思路分析。"
            Write-Host "`n正在思考中..." -ForegroundColor $Colors.AI
            $response = Get-AIResponse -Prompt $prompt
            if ($response) {
                Write-Host "`n🤖 AI的解题思路分析：" -ForegroundColor $Colors.AI
                Write-Host $response -ForegroundColor $Colors.Info
            }
        }
        "2" {
            $prompt = "请针对以下C语言题目提供代码实现指导：`n`n题目：$($Exercise.title)`n`n任务：$($Exercise.task)`n`n请给出关键代码实现的指导，但不要直接给出完整代码。"
            Write-Host "`n正在思考中..." -ForegroundColor $Colors.AI
            $response = Get-AIResponse -Prompt $prompt
            if ($response) {
                Write-Host "`n🤖 AI的代码实现指导：" -ForegroundColor $Colors.AI
                Write-Host $response -ForegroundColor $Colors.Info
            }
        }
        "3" {
            $prompt = "请解释以下C语言题目涉及的重要知识点：`n`n题目：$($Exercise.title)`n`n知识点：$($Exercise.points)`n`n请详细讲解这些知识点。"
            Write-Host "`n正在思考中..." -ForegroundColor $Colors.AI
            $response = Get-AIResponse -Prompt $prompt
            if ($response) {
                Write-Host "`n🤖 AI的知识点讲解：" -ForegroundColor $Colors.AI
                Write-Host $response -ForegroundColor $Colors.Info
            }
        }
        "4" {
            return
        }
        default {
            Write-Host "❌ 无效的选择" -ForegroundColor $Colors.Error
        }
    }
    
    Write-Host "`n按任意键继续..." -ForegroundColor $Colors.Prompt
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Show-AIHelp -Exercise $Exercise
}

# 主函数
function Main {
    param (
        [string]$Command
    )
    
    # 在开始时自动启动Ollama服务
    Write-Host "正在初始化系统..." -ForegroundColor $Colors.Info
    if (-not (Start-OllamaService)) {
        Write-Host "❌ AI服务初始化失败。系统将以有限功能继续运行。" -ForegroundColor $Colors.Warning
        Write-Host "您可以继续使用系统，但AI辅助功能将不可用。" -ForegroundColor $Colors.Info
        $script:UseAI = $false
        Write-Host "按任意键继续..." -ForegroundColor $Colors.Prompt
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    
    $exercises = Get-Exercises
    if ($exercises.Count -eq 0) {
        Write-Host "❌ 错误：未找到任何练习。" -ForegroundColor $Colors.Error
        return
    }
    
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
                Clear-Host
                Write-Host "`n🎉 恭喜！您已完成所有练习！" -ForegroundColor $Colors.Success
                Write-Host "`n如果您想重新开始，请使用 'reset' 命令重置进度。" -ForegroundColor $Colors.Info
                Write-Host "`n按任意键返回主菜单..." -NoNewline
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
                return
            }
            
            Show-ProgressBar $progress.Completed.Count $exercises.Count
            
            while ($currentIndex -lt $exercises.Count) {
                # 清除控制台
                Clear-ProgressBar
                
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
                
                Write-Host "`n命令：" -ForegroundColor $Colors.Title
                Write-Host "[ t:测试 | h:提示 | a:AI助手 | n:下一题 | q:退出 ]" -ForegroundColor $Colors.Info

                Write-Host "`n请输入命令: " -NoNewline -ForegroundColor $Colors.Prompt
                $input = Read-Host
                
                switch ($input.ToLower()) {
                    "t" {
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
                            Clear-ProgressBar
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
                            Clear-ProgressBar
                        } else {
                            Write-Host "`n⚠️ 未找到提示文件。" -ForegroundColor $Colors.Warning
                            Write-Host "`n按任意键继续..." -NoNewline
                            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
                            Clear-ProgressBar
                        }
                    }
                    "a" {
                        Show-AIHelp -Exercise $exercise
                        Clear-ProgressBar
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
                # 重置AI功能选择
                $script:UseAI = $false
                
                # 删除AI配置文件
                if (Test-Path $AIConfigFile) {
                    Remove-Item $AIConfigFile -Force
                }
                
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
        
        "help" {
            Write-Host "欢迎使用 CStudy！🎯" -ForegroundColor $Colors.Info
            
            Write-Host "可用命令：" -ForegroundColor $Colors.Title
            Write-Host "  begin  - 开始练习" -ForegroundColor $Colors.Info
            Write-Host "  reset  - 重置所有练习" -ForegroundColor $Colors.Info
            Write-Host "  list   - 显示练习列表" -ForegroundColor $Colors.Info
            Write-Host "  verify - 验证所有练习" -ForegroundColor $Colors.Info
            Write-Host "  help   - 显示帮助信息" -ForegroundColor $Colors.Info
        }
        
        default {
            Write-Host "欢迎使用 CStudy！🎯" -ForegroundColor $Colors.Info
            
            Write-Host "可用命令：" -ForegroundColor $Colors.Title
            Write-Host "  begin  - 开始练习" -ForegroundColor $Colors.Info
            Write-Host "  reset  - 重置所有练习" -ForegroundColor $Colors.Info
            Write-Host "  list   - 显示练习列表" -ForegroundColor $Colors.Info
            Write-Host "  verify - 验证所有练习" -ForegroundColor $Colors.Info
            Write-Host "  help   - 显示帮助信息" -ForegroundColor $Colors.Info
        }
    }
}

# 执行主函数
Main $args[0]