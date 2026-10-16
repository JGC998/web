@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0.."
echo Publicando la web de CRM...
py _fuente\publicar.py
echo.
pause
