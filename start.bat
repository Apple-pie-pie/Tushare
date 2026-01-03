@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
echo ========================================
echo    Tushare 鏁版嵁鍒嗘瀽绯荤粺 - 涓€閿惎鍔?br>echo ========================================
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

REM 检查并更新代码
if exist ".git\" (
    echo [鎻愮ず] 妫€鏌ヤ唬鐮佹洿鏂?..
    git fetch origin >nul 2>&1
    
    git rev-parse HEAD >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "delims=" %%i in ('git rev-parse HEAD 2^>nul') do set LOCAL=%%i
        for /f "delims=" %%i in ('git rev-parse @{u} 2^>nul') do set REMOTE=%%i
        
        if not "!LOCAL!"=="!REMOTE!" (
            if not "!REMOTE!"=="" (
                echo [鍙戠幇鏇存柊] 姝ｅ湪浠嶨itHub鎷夊彇鏈€鏂颁唬鐮?..
                git reset --hard origin/main >nul 2>&1
                git pull origin main
                if !errorlevel! neq 0 (
                    echo [璀﹀憡] 浠ｇ爜鏇存柊澶辫触
                    echo [鎻愮ず] 缁х画浣跨敤褰撳墠鐗堟湰...
                ) else (
                    echo [鎴愬姛] 浠ｇ爜宸叉洿鏂板埌鏈€鏂扮増鏈紒
                )
            ) else (
                echo [鎴愬姛] 宸叉槸鏈€鏂扮増鏈?br>            )
        ) else (
            echo [鎴愬姛] 宸叉槸鏈€鏂扮増鏈?br>        )
    )
    echo.
)

REM 检查虚拟环境
if not exist "venv\" (
    echo [1/4] 创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo [2/4] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查并安装依赖
echo [3/4] 妫€鏌ヤ緷璧?..
python -c "import loguru, duckdb, streamlit, retry" >nul 2>&1
if !errorlevel! neq 0 (
    echo [鎻愮ず] 妫€娴嬪埌缂哄皯渚濊禆锛屾鍦ㄨ嚜鍔ㄥ畨瑁?棣栨杩愯鍙兘闇€瑕佸嚑鍒嗛挓锛?..
    echo.
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt --no-cache-dir
    
    if !errorlevel! neq 0 (
        echo.
        echo [閿欒] 渚濊禆瀹夎澶辫触锛岃鎵嬪姩杩愯: install_dependencies.bat
        pause
        exit /b 1
    )
    echo.
    echo [鎴愬姛] 渚濊禆瀹夎瀹屾垚锛?br>) else (
    echo [鎴愬姛] 渚濊禆宸插氨缁?br>)

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
