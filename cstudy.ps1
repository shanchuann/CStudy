# Windows entry point for the portable CStudy CLI.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Get-Command py -ErrorAction SilentlyContinue
if ($python) {
    & $python.Source -3 (Join-Path $root 'cstudy.py') @args
    exit $LASTEXITCODE
}
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { throw 'CStudy requires Python 3.9+ (py or python) in PATH.' }
& $python.Source (Join-Path $root 'cstudy.py') @args
exit $LASTEXITCODE
