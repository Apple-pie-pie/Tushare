@echo off
chcp 65001 >nul
echo ========================================
echo    安装所有依赖
echo ========================================
echo.

echo 正在升级pip...
python -m pip install --upgrade pip

echo.
echo 正在安装核心依赖...
pip install loguru>=0.7.0
pip install duckdb>=0.10.0
pip install streamlit>=1.30.0
pip install plotly>=5.18.0
pip install streamlit-aggrid>=0.3.4
pip install python-dotenv>=1.0.0
pip install pyyaml>=6.0
pip install tushare>=1.4.0
pip install pandas>=2.0.0
pip install numpy>=1.24.0
pip install requests>=2.31.0
pip install retry>=0.9.2
pip install python-dateutil>=2.8.2
pip install sqlalchemy>=2.0.0

echo.
echo ========================================
echo    安装完成！
echo ========================================
echo.
pause
