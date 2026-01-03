"""Streamlit主应用：Tushare数据面板系统"""
import streamlit as st
from loguru import logger
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 页面配置
st.set_page_config(
    page_title="Tushare数据面板系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #1f77b4;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 主页面
st.markdown('<div class="main-header">📈 Tushare 数据面板系统</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">数据整合工作台 + 股票分析终端</div>', unsafe_allow_html=True)

# 欢迎信息
st.info("""
**欢迎使用 Tushare 数据面板系统！**

本系统模仿专业数据整合软件（Tableau Prep / Alteryx）与股票终端（TradingView / 同花顺），
提供：
- 🏠 **Market Terminal**：股票分析终端（自选股、K线、财务、筛选器）
- 🔧 **Data Studio**：数据整合工作台（ETL流程、面板构建）
- 📊 **API Catalog**：接口目录（权限透明、状态可见）
- ⚙️ **Settings**：系统设置（Token配置、积分查询）

👈 请从左侧导航栏选择工作台
""")

# 快速开始
st.markdown("---")
st.subheader("🚀 快速开始")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 1️⃣ 配置Token")
    st.write("进入 **Settings** 页面配置你的 Tushare Token")
    if st.button("前往设置", key="go_settings"):
        st.switch_page("pages/4_⚙️_Settings.py")

with col2:
    st.markdown("### 2️⃣ 初始化数据")
    st.write("进入 **Data Studio** 拉取基础数据（交易日历、股票列表）")
    if st.button("前往工作台", key="go_studio"):
        st.switch_page("pages/2_🔧_Data_Studio.py")

with col3:
    st.markdown("### 3️⃣ 开始分析")
    st.write("进入 **Market Terminal** 查看行情与财务")
    if st.button("前往终端", key="go_terminal"):
        st.switch_page("pages/1_🏠_Market_Terminal.py")

# 系统架构
st.markdown("---")
st.subheader("🏗️ 系统架构")

with st.expander("查看技术架构"):
    st.markdown("""
    **数据分层**：
    - **Raw层**：原始接口数据（可追溯）
    - **Clean层**：清洗后数据（规范化）
    - **Serve层**：面板数据（daily_panel + funda_panel）
    
    **核心设计**：
    - **绝对索引**：`(ts_code, trade_date)` 唯一主键
    - **权限透明**：所有接口显示积分门槛与状态
    - **增量可恢复**：按日期水位增量，支持断点续跑
    - **限频保护**：500次/分钟（5000+积分）
    
    **技术栈**：
    - UI：Streamlit + Plotly
    - 数据库：DuckDB + Parquet
    - 数据源：Tushare Pro API
    """)

# 底部信息
st.markdown("---")
st.caption("💡 提示：本系统为路线A（快速原型），后续可升级为路线B（React + FastAPI）")
