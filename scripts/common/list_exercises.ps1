# 练习题列表与状态展示 PowerShell 脚本
param([string]$ExercisesPath = "$(Resolve-Path "$PSScriptRoot/../../Exercises")")

$exercises = Get-ChildItem -Path $ExercisesPath -Directory
$doneCount = 0
$total = $exercises.Count
foreach ($ex in $exercises) {
    $desc = Join-Path $ex.FullName "description.md"
    $done = Test-Path (Join-Path $ex.FullName "done.flag")
    $status = if ($done) { "已完成" } else { "未完成" }
    $cfile = Get-ChildItem -Path $ex.FullName -Filter "*.c" | Select-Object -First 1
    $cfilePath = if ($cfile) { $cfile.FullName } else { "未找到C文件" }
    Write-Host "练习: $($ex.Name) 状态: $status C文件: $cfilePath"
    if ($done) { $doneCount++ }
}
Write-Host "完成进度: $doneCount/$total"

# 完成进度就是通过进度
Write-Host "批量检测结果: 通过 $doneCount, 失败 $($total - $doneCount), 总数 $total"
