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

# 检查并更新代码
if [ -d ".git" ]; then
    echo "[提示] 检查代码更新..."
    git fetch origin &> /dev/null
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse @{u} 2>/dev/null)
    
    if [ "$LOCAL" != "$REMOTE" ] && [ -n "$REMOTE" ]; then
        echo "[发现更新] 正在从GitHub拉取最新代码..."
        if git pull origin main; then
            echo "[成功] 代码已更新到最新版本！"
        else
            echo "[警告] 代码更新失败，可能有本地修改冲突"
            echo "[提示] 继续使用当前版本..."
        fi
    else
        echo "[成功] 已是最新版本"
    fi
    echo ""
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[1/4] 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "[2/4] 激活虚拟环境..."
source venv/bin/activate

# 检查并安装依赖
echo "[3/4] 检查依赖..."
if ! python -c "import duckdb" &> /dev/null; then
    echo "[提示] 检测到缺少依赖，正在自动安装（首次运行可能需要几分钟）..."
    pip install --upgrade pip --quiet
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败，请检查网络连接"
        exit 1
    fi
    echo "[成功] 依赖安装完成！"
else
    echo "[成功] 依赖已就绪"
fi

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
