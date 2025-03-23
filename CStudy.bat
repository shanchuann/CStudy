@echo off
if "%OS%"=="Windows_NT" (
    powershell -ExecutionPolicy Bypass -File "%~dp0CStudy.ps1" %*
) else (
    echo 此脚本仅支持 Windows 系统
    pause
) 