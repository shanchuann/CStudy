# Compatibility adapter for the API-backed AI helper.
param([string]$Code, [string]$Desc, [string]$Test)
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$exercise = Split-Path -Leaf (Split-Path -Parent $Code)
& (Join-Path $root 'cstudy.ps1') ai $exercise
exit $LASTEXITCODE
