# CStudy 主入口 PowerShell 脚本
# UTF-8编码，自动检测平台，调用核心模块


[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "CStudy (PowerShell) - Interactive C Programming Platform"

$ExercisesPath = Join-Path $PSScriptRoot "..\Exercises"
$AIConfigPath = Join-Path $PSScriptRoot "..\AIserver\ai_enabled.txt"
$AIEnabled = $false

# 启动时询问是否启用AI服务（仅首次）
function InitAI {
    # 若已有配置文件，则按配置处理
    if (Test-Path $AIConfigPath) {
        $saved = (Get-Content $AIConfigPath -Raw).Trim().ToLower()
        if ($saved -ne 'enabled') { return $false }

        # 已启用时，确认 ollama 可用
        $ollamaOk = $false
        try {
            $ver = & ollama --version 2>&1
            if ($LASTEXITCODE -eq 0) { $ollamaOk = $true }
        } catch { $ollamaOk = $false }
        if (-not $ollamaOk) {
            Write-Host "未检测到 ollama，请先安装（https://ollama.com/download）。AI 服务将被禁用。" -ForegroundColor Yellow
            Set-Content $AIConfigPath 'disabled'
            return $false
        }

        # 确保模型目录与默认模型文件
        $modelDir = Join-Path $PSScriptRoot "..\AIserver\model"
        if (-not (Test-Path $modelDir)) { New-Item -ItemType Directory -Path $modelDir | Out-Null }
        $defaultFile = Join-Path $modelDir 'default-model.txt'
        if (-not (Test-Path $defaultFile)) {
            Write-Host "未检测到默认模型，进行一次性设置。" -ForegroundColor Cyan
            Write-Host "推荐模型（输入序号选择）：" -ForegroundColor Cyan
            Write-Host "  1. codegemma:2b         - 轻量，适合低内存环境（默认）" -ForegroundColor Gray
            Write-Host "  2. qwen2.5-coder:7b     - 中文友好，需更多内存" -ForegroundColor Gray
            Write-Host "  3. deepseek-coder-v2:16b - 性能强，显存/内存需求高" -ForegroundColor Gray
            Write-Host "  4. 自定义模型名称" -ForegroundColor Gray
            $sel = Read-Host "请选择"
            $model = switch ($sel) {
                '1' { 'codegemma:2b' }
                '2' { 'qwen2.5-coder:7b' }
                '3' { 'deepseek-coder-v2:16b' }
                '4' { Read-Host '请输入模型名称（如 codellama:13b）' }
                default { 'codegemma:2b' }
            }
            Set-Content $defaultFile $model
            Write-Host "默认模型已设置为：$model（首次使用将自动下载）" -ForegroundColor Green
        }

        # 读取默认模型，并给出存在性提示（不强制下载）
        $defaultModel = (Get-Content $defaultFile -Raw).Trim()
        try {
            $list = & ollama list 2>&1
            if ($LASTEXITCODE -eq 0) {
                $names = $list | ForEach-Object { if ($_ -match '^(\S+)\s') { $matches[1] } }
                if (-not ($names -contains $defaultModel)) {
                    Write-Host "提示：本地未发现模型 $defaultModel，首次调用时将自动下载。" -ForegroundColor Yellow
                }
            }
        } catch {}
        return $true
    }

    # 首次运行：是否启用 AI
    $ans = Read-Host "是否启用AI服务？(y/n)"
    if ($ans -ne 'y' -and $ans -ne 'Y') {
        Set-Content $AIConfigPath 'disabled'
        return $false
    }

    # 启用前检查 ollama
    Write-Host "正在检查 ollama 安装状态..." -ForegroundColor Cyan
    $ollamaOk2 = $false
    try {
        $ver2 = & ollama --version 2>&1
        if ($LASTEXITCODE -eq 0) { $ollamaOk2 = $true }
    } catch { $ollamaOk2 = $false }
    if (-not $ollamaOk2) {
        Write-Host "未检测到 ollama，请先安装（https://ollama.com/download）。AI 服务将被禁用。" -ForegroundColor Yellow
        Set-Content $AIConfigPath 'disabled'
        return $false
    }

    # 设置默认模型（不在此阶段下载）
    $modelDir2 = Join-Path $PSScriptRoot "..\AIserver\model"
    if (-not (Test-Path $modelDir2)) { New-Item -ItemType Directory -Path $modelDir2 | Out-Null }
    $defaultFile2 = Join-Path $modelDir2 'default-model.txt'
    Write-Host "推荐模型（输入序号选择）：" -ForegroundColor Cyan
    Write-Host "  1. codegemma:2b         - 轻量，适合低内存环境（默认）" -ForegroundColor Gray
    Write-Host "  2. qwen2.5-coder:7b     - 中文友好，需更多内存" -ForegroundColor Gray
    Write-Host "  3. deepseek-coder-v2:16b - 性能强，显存/内存需求高" -ForegroundColor Gray
    Write-Host "  4. 自定义模型名称" -ForegroundColor Gray
    $sel2 = Read-Host "请选择"
    $model2 = switch ($sel2) {
        '1' { 'codegemma:2b' }
        '2' { 'qwen2.5-coder:7b' }
        '3' { 'deepseek-coder-v2:16b' }
        '4' { Read-Host '请输入模型名称（如 codellama:13b）' }
        default { 'codegemma:2b' }
    }
    Set-Content $defaultFile2 $model2
    Set-Content $AIConfigPath 'enabled'
    Write-Host "AI 服务已启用，默认模型：$model2（首次使用将自动下载）" -ForegroundColor Green
    return $true
}

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

function Show-Header {
    Clear-Host
    Write-Host "CStudy (PowerShell) - Interactive C Programming Platform"
    Show-Progress
        Write-Host "命令列表：" -ForegroundColor Cyan
        $cmdTable = @(
            @{cmd='check'; desc='检测当前练习'},
            @{cmd='check all'; desc='检测所有练习'},
            @{cmd='list'; desc='题目列表'},
            @{cmd='AI'; desc='AI服务'},
            @{cmd='reset'; desc='重置系统'}
        )
        if ($AIEnabled) {
            $cmdTable += @{cmd='help me'; desc='询问AI'}
        }
        $cmdTable += @{cmd='quit'; desc='退出系统'}
        $maxCmdLen = ($cmdTable | ForEach-Object { $_.cmd.Length } | Measure-Object -Maximum).Maximum
        $pad = [Math]::Max($maxCmdLen, 8) + 2
        foreach ($row in $cmdTable) {
            $fmt = "  {0,-$pad} {1}"
            Write-Host ($fmt -f $row.cmd, $row.desc) -ForegroundColor Yellow
        }
    # 在进度条下方仅显示完成提示，不再显示题目描述，避免重复
    try {
        $exList = Get-ChildItem -Path $ExercisesPath -Directory
        $foundNext = $false
        foreach ($ex in $exList) {
            $done = Test-Path (Join-Path $ex.FullName "done.flag")
            if (-not $done) {
                $foundNext = $true
                break
            }
        }
        if (-not $foundNext) {
            Write-Host "`n恭喜完成所有练习！输入 quit 退出，输入 reset 重置。" -ForegroundColor Green
        }
    } catch {}
}

function Show-CurrentExerciseDetails {
    # 展示第一个未完成练习的详细信息与运行结果（包含文件路径），去除多余空行
    $exercises = Get-ChildItem -Path $ExercisesPath -Directory
    foreach ($ex in $exercises) {
        $doneFlag = Test-Path (Join-Path $ex.FullName "done.flag")
        if (-not $doneFlag) {
            $cFile = Get-ChildItem -Path $ex.FullName -Filter "*.c" | Select-Object -First 1
            if ($cFile) {
                Write-Host "练习: $($ex.Name) 状态: 未完成 $($cFile.FullName)" -ForegroundColor Yellow
                $descPath = Join-Path $ex.FullName "description.md"
                if (Test-Path $descPath) {
                    Write-Host "题目描述" -ForegroundColor Magenta
                    Get-Content $descPath | Write-Host
                }
                Write-Host "运行结果" -ForegroundColor Magenta
                $exe = "$($cFile.FullName).exe"
                gcc $cFile.FullName -o $exe 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    $testPath = Join-Path $ex.FullName "Test.txt"
                    if (Test-Path $testPath) {
                        $testLines = Get-Content $testPath
                        $inInputSection = $false
                        $inputLines = @()
                        foreach ($line in $testLines) {
                            if ($line.Trim() -eq "INPUT:") { $inInputSection = $true; continue }
                            if ($line.Trim() -eq "OUTPUT:" -or $line.Trim() -eq "---") { break }
                            if ($inInputSection) { $inputLines += $line }
                        }
                        $tmpInput = "$env:TEMP/tmp_input.txt"
                        $inputContent = ($inputLines -join "`n")
                        if ($inputContent) {
                            Set-Content -Path $tmpInput -Value $inputContent -Encoding UTF8
                            $output = Get-Content $tmpInput | & $exe
                            Remove-Item $tmpInput -ErrorAction SilentlyContinue
                        } else {
                            $output = & $exe
                        }
                        Write-Host ($output -join "`n")
                    } else {
                        $output = & $exe
                        Write-Host ($output -join "`n")
                    }
                    Remove-Item $exe -ErrorAction SilentlyContinue
                } else {
                    Write-Host "代码编译失败，请检查语法。" -ForegroundColor Red
                }
            } else {
                Write-Host "练习: $($ex.Name) 状态: 未完成 未找到C语言文件" -ForegroundColor Yellow
            }
            break
        }
    }
}

$AIEnabled = InitAI
Show-Header
Show-CurrentExerciseDetails

while ($true) {
    $cmd = Read-Host "`n请输入命令"
    Write-Host ""
    # 支持 check all 检测所有题
    if ($cmd -eq 'check all') {
        $exercises = Get-ChildItem "$ExercisesPath" -Directory
        foreach ($ex in $exercises) {
            Write-Host "判题: $($ex.Name)"
            $cFile = Get-ChildItem -Path $ex.FullName -Filter "*.c" | Select-Object -First 1
            if ($cFile) {
                & "$PSScriptRoot/common/judge.ps1" $cFile.FullName "$($ex.FullName)/Test.txt"
            }
        }
        Write-Host "`n按Enter键继续..." -ForegroundColor Yellow
        Read-Host
        Show-Header
        Show-CurrentExerciseDetails
        continue
    }
    # check 检测当前文件
    if ($cmd -eq 'check') {
        # 直接判第一个未完成练习的 C 文件
        $exercises = Get-ChildItem "$ExercisesPath" -Directory
        $checked = $false
        foreach ($ex in $exercises) {
            $doneFlag = Test-Path (Join-Path $ex.FullName "done.flag")
            if (-not $doneFlag) {
                $cFile = Get-ChildItem -Path $ex.FullName -Filter "*.c" | Select-Object -First 1
                $testFile = Join-Path $ex.FullName "Test.txt"
                if ($cFile -and (Test-Path $testFile)) {
                    Write-Host "判题: $($cFile.FullName)"
                    & "$PSScriptRoot/common/judge.ps1" $cFile.FullName $testFile
                    $checked = $true
                } else {
                    Write-Host "未找到 C 文件或测试用例" -ForegroundColor Red
                }
                break
            }
        }
        if (-not $checked) {
            Write-Host "没有未完成的练习可判题。" -ForegroundColor Yellow
        }
        Write-Host "`n按Enter键继续..." -ForegroundColor Yellow
        Read-Host
        Show-Header
        Show-CurrentExerciseDetails
        continue
    }
    switch ($cmd) {
        "list" { & "$PSScriptRoot/common/list_exercises.ps1" }
        "AI" {
            # 每次都进入模型配置界面（子循环），仅在输入 quit 时返回主界面
            $AIEnabled = InitAI
            while ($true) {
                Clear-Host
                Write-Host "CStudy (PowerShell) - AI 模型配置界面" -ForegroundColor Cyan
                $modelDir = "$PSScriptRoot/../AIserver/model"
                $defaultModelFile = Join-Path $modelDir "default-model.txt"
                $defaultModel = if (Test-Path $defaultModelFile) { (Get-Content $defaultModelFile -Raw).Trim() } else { "未设置" }
                Write-Host "当前默认模型: $defaultModel" -ForegroundColor Cyan
                Write-Host "AI模型管理: list, download, switch, remove, quit"
                $cmd2 = Read-Host "请输入模型管理命令（回车刷新本界面）"
                if ([string]::IsNullOrWhiteSpace($cmd2)) { continue }
                switch ($cmd2) {
                    "list" {
                        Write-Host "模型配置文件列表："
                        Get-ChildItem $modelDir | ForEach-Object {
                            $isDefault = ($_.Name -eq "default-model.txt")
                            $flag = if ($isDefault) { "(默认配置)" } else { "" }
                            Write-Host ("{0,-20} {1}" -f $_.Name, $flag)
                        }
                        Write-Host "\n本地 ollama 模型列表：" -ForegroundColor Yellow
                        try {
                            $ollamaModels = & ollama list 2>&1
                            if ($LASTEXITCODE -eq 0) {
                                $ollamaModels | ForEach-Object { Write-Host $_ }
                            } else {
                                Write-Host "无法获取 ollama 模型列表，请检查 ollama 安装。" -ForegroundColor Red
                            }
                        } catch {
                            Write-Host "无法获取 ollama 模型列表，请检查 ollama 安装。" -ForegroundColor Red
                        }
                        $null = Read-Host -Prompt '按 Enter 键继续...'
                    }
                    "download" {
                        $target = Read-Host "请输入要下载的模型名（如 deepseek-coder:6.7b）"
                        if ([string]::IsNullOrWhiteSpace($target)) {
                            Write-Host "已取消下载。" -ForegroundColor Yellow
                            $null = Read-Host -Prompt '按 Enter 键继续...'
                            break
                        }
                        Write-Host "开始下载模型：$target" -ForegroundColor Cyan
                        $exit = 1
                        try {
                            & ollama pull $target
                            $exit = $LASTEXITCODE
                        } catch {
                            $exit = 1
                        }
                        if ($exit -eq 0) {
                            Write-Host "✓ 模型已下载完成：$target" -ForegroundColor Green
                            Set-Content $defaultModelFile $target
                            Write-Host "默认模型已设置为：$target" -ForegroundColor Green
                        } else {
                            Write-Host "✗ 下载失败，请检查模型名或网络连接。" -ForegroundColor Red
                        }
                        $null = Read-Host -Prompt '按 Enter 键继续...'
                    }
                    "switch" {
                        while ($true) {
                            $newModel = Read-Host "请输入新模型名称（如 deepseek-coder:6.7b）"
                            if (-not $newModel -or $newModel.Trim() -eq "") {
                                Write-Host "未输入模型名称，未做更改。" -ForegroundColor Yellow
                                break
                            }
                            # 获取本地 ollama 模型列表
                            $ollamaModels = @()
                            try {
                                $ollamaList = & ollama list 2>&1
                                if ($LASTEXITCODE -eq 0) {
                                    $ollamaModels = $ollamaList | ForEach-Object {
                                        if ($_ -match '^(\S+)\s') { $matches[1] } else { $null }
                                    } | Where-Object { $_ }
                                }
                            } catch {}
                            if ($ollamaModels -and ($ollamaModels -contains $newModel.Trim())) {
                                Set-Content $defaultModelFile $newModel.Trim()
                                Write-Host "已切换默认模型为: $newModel" -ForegroundColor Green
                                $null = Read-Host -Prompt '按 Enter 键继续...'
                                break
                            } else {
                                Write-Host "未在本地模型列表中找到该模型：$newModel" -ForegroundColor Red
                                $retry = Read-Host "是否重新输入模型名称？(y/n)"
                                if ($retry -ne 'y' -and $retry -ne 'Y') {
                                    Write-Host "已取消切换，返回AI模型管理界面。" -ForegroundColor Yellow
                                    $null = Read-Host -Prompt '按 Enter 键继续...'
                                    break
                                }
                            }
                        }
                    }
                    "remove" {
                        $target = Read-Host "请输入要删除的模型名（如 deepseek-coder:6.7b）"
                        if ([string]::IsNullOrWhiteSpace($target)) {
                            Write-Host "已取消删除。" -ForegroundColor Yellow
                            $null = Read-Host -Prompt '按 Enter 键继续...'
                            break
                        }
                        $isDefault = ($defaultModel -ne "未设置" -and $target.Trim() -eq $defaultModel.Trim())
                        if ($isDefault) {
                            $confirm = Read-Host "该模型是当前默认模型，确认删除并清除默认设置？(y/n)"
                            if ($confirm -ne 'y' -and $confirm -ne 'Y') {
                                Write-Host "已取消删除。" -ForegroundColor Yellow
                                $null = Read-Host -Prompt '按 Enter 键继续...'
                                break
                            }
                        }
                        Write-Host "删除模型：$target" -ForegroundColor Cyan
                        $exit = 1
                        try {
                            & ollama rm $target
                            $exit = $LASTEXITCODE
                        } catch {
                            $exit = 1
                        }
                        if ($exit -eq 0) {
                            Write-Host "✓ 已删除模型：$target" -ForegroundColor Green
                            if ($isDefault) {
                                Remove-Item -ErrorAction SilentlyContinue $defaultModelFile
                                Write-Host "默认模型已清除。" -ForegroundColor Yellow
                                $setNew = Read-Host "是否设置一个新的默认模型？(y/n)"
                                if ($setNew -eq 'y' -or $setNew -eq 'Y') {
                                    try {
                                        $ollamaList = & ollama list 2>&1
                                        if ($LASTEXITCODE -eq 0) {
                                            Write-Host "本地可用模型：" -ForegroundColor Cyan
                                            $ollamaList | ForEach-Object { Write-Host $_ }
                                        }
                                    } catch {}
                                    $newModel = Read-Host "请输入一个已存在的本地模型名"
                                    if ($newModel -and $newModel.Trim() -ne "") {
                                        $valid = $false
                                        try {
                                            $ollamaList2 = & ollama list 2>&1
                                            if ($LASTEXITCODE -eq 0) {
                                                $names = $ollamaList2 | ForEach-Object { if ($_ -match '^(\S+)\s') { $matches[1] } }
                                                if ($names -contains $newModel.Trim()) { $valid = $true }
                                            }
                                        } catch {}
                                        if ($valid) {
                                            Set-Content $defaultModelFile $newModel.Trim()
                                            Write-Host "默认模型已设置为：$newModel" -ForegroundColor Green
                                        } else {
                                            Write-Host "未在本地找到该模型，未设置默认模型。" -ForegroundColor Yellow
                                        }
                                    }
                                }
                            }
                        } else {
                            Write-Host "✗ 删除失败，模型可能不存在或命令执行错误。" -ForegroundColor Red
                        }
                        $null = Read-Host -Prompt '按 Enter 键继续...'
                    }
                    "quit" { break }
                    default { Write-Host "未知模型管理命令"; $null = Read-Host -Prompt '按 Enter 键继续...' }
                }
                if ($cmd2 -eq 'quit') { break }
            }
            Show-Header
            Show-CurrentExerciseDetails
            continue
        }
        "help me" {
            if (-not $AIEnabled) {
                Write-Host "AI服务未启用，无法使用 help me 命令。" -ForegroundColor Yellow
                continue
            }
            $ex = Read-Host "输入练习名"; $exPath = Join-Path $ExercisesPath $ex
            $cFile = Get-ChildItem -Path $exPath -Filter "*.c" | Select-Object -First 1
            $desc = Join-Path $exPath "description.md"
            $test = Join-Path $exPath "Test.txt"
            if ($cFile -and (Test-Path $desc) -and (Test-Path $test)) {
                & "$PSScriptRoot/common/ai_helper.ps1" -Code $cFile.FullName -Desc $desc -Test $test
            } else {
                Write-Host "练习目录缺少必要文件" -ForegroundColor Red
            }
        }
        "quit" { 
            Write-Host "退出 CStudy，感谢使用！" -ForegroundColor Green
            break 
        }
        "reset" {
            & "$PSScriptRoot/reset.ps1"
        }
        default { Write-Host "未知命令" }
    }
    if ($cmd -eq "quit") { break }
    Write-Host "`n按Enter键继续..." -ForegroundColor Yellow
    Read-Host
    Show-Header
    Show-CurrentExerciseDetails
}
