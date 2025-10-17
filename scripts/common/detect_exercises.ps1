# 自动检测并注册练习题 PowerShell 脚本
param([string]$ExercisesPath = "../Exercises")

$exercises = Get-ChildItem -Path $ExercisesPath -Directory
foreach ($ex in $exercises) {
    Write-Host "检测到练习题: $($ex.Name)"
    # 可扩展：读取 description.md、Test.txt、metadata.json 校验
}
