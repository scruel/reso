#!/bin/bash -e

echo "🚀 开始导入商品数据到 PGVector..."
echo

source /home/scruel/reso/.venv/bin/activate

# 检查 Python 环境
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到 Python，请先安装 Python"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -f "import_goods_to_pgvector.py" ]; then
    echo "❌ 错误: 请在 tools 目录下运行此脚本"
    exit 1
fi

# 检查商品数据目录
GOODS_DIR="../resource/good"
if [ ! -d "$GOODS_DIR" ]; then
    echo "❌ 错误: 未找到商品数据目录 $GOODS_DIR"
    exit 1
fi

# 统计商品数量
GOODS_COUNT=$(find "$GOODS_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l)
echo "📦 发现 $GOODS_COUNT 个商品文件夹"

# 检查依赖
echo "🔍 检查 Python 依赖..."
if [ -f "requirements.txt" ]; then
    python -c "import psycopg2, torch, transformers, numpy" 2>/dev/null || {
        echo "⚠️  警告: 部分依赖未安装，正在安装..."
        pip3 install -r requirements.txt
    }
else
    echo "⚠️  警告: 未找到 requirements.txt 文件"
fi

# 检查环境变量或提示用户
if [ -z "$DB_HOST" ] && [ -z "$DB_NAME" ] && [ -z "$DB_USER" ]; then
    echo
    echo "💡 提示: 请确保已配置数据库连接参数"
    echo "   方法1: 设置环境变量 (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)"
    echo "   方法2: 修改脚本中的 db_params 字典"
    echo "   方法3: 复制 .env.example 为 .env 并修改配置"
    echo
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 用户取消操作"
        exit 1
    fi
fi

# 运行导入脚本
echo "🔄 开始导入商品数据..."
echo "📝 日志文件: import_goods.log"
echo

python import_goods_to_pgvector.py

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo
    echo "✅ 商品数据导入完成！"
    echo
    echo "🔍 测试语义搜索:"
    echo "   python test_semantic_search.py \"充电宝\""
    echo "   python test_semantic_search.py \"小米手机配件\""
    echo
    echo "📊 查看日志:"
    echo "   tail -f import_goods.log"
else
    echo
    echo "❌ 导入失败，请检查日志文件: import_goods.log"
    echo "📋 常见问题:"
    echo "   1. 检查数据库连接参数"
    echo "   2. 确认 PostgreSQL 服务正在运行"
    echo "   3. 验证 pgvector 扩展已安装"
    echo "   4. 检查网络连接（模型下载）"
fi

exit $EXIT_CODE
