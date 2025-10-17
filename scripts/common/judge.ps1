
# 判题引擎 PowerShell 脚本，支持标准化 INPUT/OUTPUT 块格式
param([string]$CFile, [string]$TestFile)

# 编译C代码
$exe = "$CFile.exe"
gcc $CFile -o $exe 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "编译失败: $CFile" -ForegroundColor Red
    Write-Host "请检查文件路径和代码语法" -ForegroundColor Yellow
    exit 1
}

# 解析标准化测试用例
$lines = Get-Content $TestFile
$testCases = @()
$currentInput = @()
$currentOutput = @()
$mode = "none"
foreach ($line in $lines) {
    if ($line.Trim() -eq "INPUT:") {
        $mode = "input"
        $currentInput = @()
        $currentOutput = @()
        continue
    }
    if ($line.Trim() -eq "OUTPUT:") {
        $mode = "output"
        continue
    }
    if ($line.Trim() -eq "---") {
        if ($currentInput.Count -gt 0 -or $currentOutput.Count -gt 0) {
            $testCases += [PSCustomObject]@{
                Input = ($currentInput -join "`n").Trim()
                Output = ($currentOutput -join "`n").Trim()
            }
        }
        $mode = "none"
        continue
    }
    if ($mode -eq "input") {
        $currentInput += $line
    } elseif ($mode -eq "output") {
        $currentOutput += $line
    }
}
# 处理最后一个测试块（无 --- 结尾时）
if ($mode -eq "output" -and ($currentInput.Count -gt 0 -or $currentOutput.Count -gt 0)) {
    $testCases += [PSCustomObject]@{
        Input = ($currentInput -join "`n").Trim()
        Output = ($currentOutput -join "`n").Trim()
    }
}

# 判题
$allPassed = $true
foreach ($case in $testCases) {
    $tmpInput = "$env:TEMP/tmp_input.txt"
    Set-Content -Path $tmpInput -Value $case.Input -Encoding UTF8
    $actual = Get-Content $tmpInput | & $exe
    $actual = ($actual -join "`n").Trim()
    $expected = $case.Output
    if ($actual -eq $expected) {
        Write-Host "✓ 通过: 期望[$expected] 实际[$actual]" -ForegroundColor Green
    } else {
        Write-Host "✗ 失败: 期望[$expected] 实际[$actual]" -ForegroundColor Red
        $allPassed = $false
    }
    Remove-Item $tmpInput -ErrorAction SilentlyContinue
}

# 返回退出码
if ($allPassed) {
    # 判题通过后，标记该练习为已完成
    try {
        $exerciseDir = Split-Path $CFile -Parent
        Set-Content -Path (Join-Path $exerciseDir 'done.flag') -Value 'done'
        Write-Host "已标记完成: $exerciseDir" -ForegroundColor Green
    } catch {}
    # 清理可执行文件
    Remove-Item $exe -ErrorAction SilentlyContinue
    exit 0
} else {
    # 清理可执行文件
    Remove-Item $exe -ErrorAction SilentlyContinue
    exit 1
}
