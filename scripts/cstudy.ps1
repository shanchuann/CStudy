# Compatibility entry point. The portable root CLI is canonical.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
& (Join-Path $root 'cstudy.ps1') @args
exit $LASTEXITCODE
