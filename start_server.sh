#!/bin/bash

# 启动AI Agents后端服务

echo "🚀 启动AI Agents油烟机推荐系统后端..."

# 检查Python虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements.txt

# 启动服务
echo "🎯 启动FastAPI服务..."
echo "📡 服务地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo "💡 使用 Ctrl+C 停止服务"
echo ""

python api_server.py