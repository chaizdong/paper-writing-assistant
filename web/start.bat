@echo off
REM 论文写作辅助系统 - Web 版本启动脚本 (Windows)

echo ======================================
echo   论文写作辅助系统 - Web 版本
echo ======================================

cd /d "%~dp0\backend"

echo 正在安装依赖...
pip install -r requirements.txt

echo.
echo 启动后端服务器...
echo API 地址：http://localhost:8000
echo.
echo 按 Ctrl+C 停止服务器
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
