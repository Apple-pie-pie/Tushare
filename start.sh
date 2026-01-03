#!/bin/bash
# 快速启动脚本

echo "=================================="
echo "📈 Tushare 数据面板系统"
echo "=================================="
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件"
    echo "正在复制 .env.example..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件"
    echo ""
    echo "请编辑 .env 文件，填入你的 Tushare Token，然后重新运行此脚本"
    echo "编辑命令: nano .env 或 vim .env"
    exit 1
fi

# 检查是否配置了 Token
if grep -q "your_token_here" .env; then
    echo "⚠️  Token 未配置"
    echo "请编辑 .env 文件，将 TUSHARE_TOKEN 替换为你的实际 Token"
    echo "编辑命令: nano .env 或 vim .env"
    exit 1
fi

echo "✅ 配置文件检查通过"
echo ""

# 检查数据库是否初始化
if [ ! -f data/serve/tushare.duckdb ]; then
    echo "🔧 首次运行，正在初始化数据库..."
    python scripts/init_db.py
    echo ""
fi

echo "🚀 启动 Streamlit UI..."
echo ""
echo "浏览器将打开 http://localhost:8501"
echo "按 Ctrl+C 停止服务"
echo ""

streamlit run ui/app.py
