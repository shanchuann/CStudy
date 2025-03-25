$exercisesPath = Join-Path $PSScriptRoot 'exercises'
$backupPath = Join-Path $PSScriptRoot 'backup'

if (-not (Test-Path $backupPath)) {
    New-Item -ItemType Directory -Path $backupPath | Out-Null
}

Get-ChildItem -Path $exercisesPath -Directory | ForEach-Object {
    $prefix = $_.Name
    Get-ChildItem -Path $_.FullName -File | ForEach-Object {
        $newName = "${prefix}_$($_.Name)"
        $destPath = Join-Path $backupPath $newName
        Copy-Item -Path $_.FullName -Destination $destPath -Force
    }
}

Write-Host "备份完成！文件已保存到：$backupPath"