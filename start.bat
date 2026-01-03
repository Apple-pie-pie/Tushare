@echo off
chcp 65001 >nul
echo ========================================
echo    Tushare 数据分析系统 - 一键启动
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查.env文件是否存在
if not exist ".env" (
    echo [提示] 首次运行，正在创建配置文件...
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [重要] 请先编辑 .env 文件，填入你的Tushare token
        echo.
        echo 1. 用记事本打开 .env 文件
        echo 2. 修改 TUSHARE_TOKEN=your_token_here
        echo 3. 保存后重新运行此脚本
        pause
        exit /b 0
    )
)

REM 检查虚拟环境
if not exist "venv\" (
    echo [1/4] 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo [2/4] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo [3/4] 检查依赖...
pip install -r requirements.txt --quiet

REM 初始化数据库
if not exist "data\serve\tushare.duckdb" (
    echo [4/4] 初始化数据库...
    python scripts\init_db.py
) else (
    echo [4/4] 数据库已存在，跳过初始化
)

echo.
echo ========================================
echo    启动成功！浏览器即将打开...
echo    如未自动打开，请访问: http://localhost:8501
echo ========================================
echo.
echo 按 Ctrl+C 停止服务
echo.

REM 启动Streamlit
streamlit run ui\app.py
