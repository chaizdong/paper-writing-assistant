#!/bin/bash
# 论文写作辅助系统 - Web 版本启动脚本

echo "======================================"
echo "  论文写作辅助系统 - Web 版本"
echo "======================================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误：需要 Python 3"
    exit 1
fi

# 进入后端目录
cd "$(dirname "$0")/backend"

# 安装依赖
echo "正在安装依赖..."
pip3 install -r requirements.txt

# 启动后端
echo ""
echo "启动后端服务器..."
echo "API 地址：http://localhost:8000"
echo "前端地址：http://localhost:8000/static (启动后在浏览器打开 frontend/index.html)"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 使用 uvicorn 启动
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
