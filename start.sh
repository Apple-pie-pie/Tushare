#!/bin/bash

echo "========================================"
echo "   Tushare 数据分析系统 - 一键启动"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python 3.8+"
    echo "Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

# 检查.env文件是否存在
if [ ! -f ".env" ]; then
    echo "[提示] 首次运行，正在创建配置文件..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "[重要] 请先编辑 .env 文件，填入你的Tushare token"
        echo ""
        echo "运行命令: nano .env"
        echo "修改 TUSHARE_TOKEN=your_token_here"
        echo "保存后重新运行此脚本"
        exit 0
    fi
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[1/4] 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "[2/4] 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "[3/4] 检查依赖..."
pip install -r requirements.txt --quiet

# 初始化数据库
if [ ! -f "data/serve/tushare.duckdb" ]; then
    echo "[4/4] 初始化数据库..."
    python scripts/init_db.py
else
    echo "[4/4] 数据库已存在，跳过初始化"
fi

echo ""
echo "========================================"
echo "   启动成功！浏览器即将打开..."
echo "   如未自动打开，请访问: http://localhost:8501"
echo "========================================"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动Streamlit
streamlit run ui/app.py
