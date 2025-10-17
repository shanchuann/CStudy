# 校验练习题文件格式 PowerShell 脚本
param([string]$ExerciseDir)
$desc = Join-Path $ExerciseDir "description.md"
$test = Join-Path $ExerciseDir "Test.txt"
$meta = Join-Path $ExerciseDir "metadata.json"
foreach ($f in @($desc, $test, $meta)) {
    if (-Not (Test-Path $f)) {
        Write-Host "缺少文件: $f"
    } else {
        Write-Host "文件存在: $f"
    }
}
