# Compatibility entry point for the unified state reset.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
& (Join-Path $root 'cstudy.ps1') reset @args
exit $LASTEXITCODE
