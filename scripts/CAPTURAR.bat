@echo off
REM Executa o script de capturas dos exercicios 5 a 9 (pede permissao de administrador)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0capturar_windows.ps1"
