"""Data Studio：数据整合工作台"""
import streamlit as st
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import get_client, db
from src.etl import DataExtractor
from src.panel import DailyPanelBuilder

st.set_page_config(page_title="Data Studio", page_icon="🔧", layout="wide")

st.title("🔧 Data Studio - 数据整合工作台")

st.info("""
**当前版本：步骤式流程（简化版）**

完整版将支持拖拽Canvas、节点连线、可视化流程设计（路线B）。
现在请按步骤手动运行各项任务。
""")

# Tab布局
tab1, tab2, tab3 = st.tabs(["📥 数据拉取", "🔨 面板构建", "📜 运行历史"])

with tab1:
    st.subheader("📥 数据拉取任务")
    
    # 基础数据初始化
    st.markdown("### 1️⃣ 基础数据（必须先运行）")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**交易日历**")
        st.write("提取交易日历（2010-至今）")
        
        if st.button("🚀 拉取交易日历", key="fetch_trade_cal"):
            with st.spinner("正在拉取..."):
                try:
                    extractor = DataExtractor()
                    df = extractor.extract_trade_calendar()
                    if df is not None and len(df) > 0:
                        st.success(f"✅ 成功拉取 {len(df)} 条交易日历")
                    else:
                        st.warning("未获取到数据")
                except Exception as e:
                    st.error(f"拉取失败: {e}")
    
    with col2:
        st.markdown("**股票列表**")
        st.write("提取A股全部股票基本信息")
        
        if st.button("🚀 拉取股票列表", key="fetch_stock_basic"):
            with st.spinner("正在拉取..."):
                try:
                    extractor = DataExtractor()
                    df = extractor.extract_stock_basic()
                    if df is not None and len(df) > 0:
                        st.success(f"✅ 成功拉取 {len(df)} 只股票")
                    else:
                        st.warning("未获取到数据")
                except Exception as e:
                    st.error(f"拉取失败: {e}")
    
    st.markdown("---")
    
    # 行情数据拉取
    st.markdown("### 2️⃣ 行情数据（日线）")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("按交易日拉取全市场行情（推荐模式：一天约5000股票，一次拉完）")
        
        fetch_date = st.date_input(
            "选择交易日",
            value=datetime.now() - timedelta(days=1),
            max_value=datetime.now()
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🚀 拉取单日行情", key="fetch_daily"):
            date_str = fetch_date.strftime("%Y%m%d")
            with st.spinner(f"正在拉取 {date_str} 的行情..."):
                try:
                    extractor = DataExtractor()
                    
                    # 同时拉取三张表
                    daily = extractor.extract_daily_by_date(date_str)
                    basic = extractor.extract_daily_basic_by_date(date_str)
                    adj = extractor.extract_adj_factor_by_date(date_str)
                    
                    st.success(f"✅ 成功拉取 {date_str} 的数据")
                    st.write(f"- 日线: {len(daily) if daily is not None else 0} 条")
                    st.write(f"- 指标: {len(basic) if basic is not None else 0} 条")
                    st.write(f"- 复权: {len(adj) if adj is not None else 0} 条")
                    
                except Exception as e:
                    st.error(f"拉取失败: {e}")
    
    # 批量拉取
    with st.expander("📅 批量拉取日期范围"):
        col1, col2 = st.columns(2)
        
        with col1:
            batch_start = st.date_input(
                "起始日期",
                value=datetime.now() - timedelta(days=30),
                key="batch_start"
            )
        
        with col2:
            batch_end = st.date_input(
                "结束日期",
                value=datetime.now(),
                key="batch_end"
            )
        
        if st.button("🚀 批量拉取", key="fetch_batch"):
            start_str = batch_start.strftime("%Y%m%d")
            end_str = batch_end.strftime("%Y%m%d")
            
            with st.spinner(f"正在批量拉取 {start_str}~{end_str}..."):
                try:
                    extractor = DataExtractor()
                    trade_dates = extractor.get_trading_dates(start_str, end_str)
                    
                    if not trade_dates:
                        st.warning("日期范围内无交易日")
                    else:
                        st.info(f"共 {len(trade_dates)} 个交易日，开始拉取...")
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i, date in enumerate(trade_dates):
                            status_text.text(f"正在拉取: {date}")
                            
                            try:
                                extractor.extract_daily_by_date(date)
                                extractor.extract_daily_basic_by_date(date)
                                extractor.extract_adj_factor_by_date(date)
                            except Exception as e:
                                st.warning(f"{date} 拉取失败: {e}")
                            
                            progress_bar.progress((i + 1) / len(trade_dates))
                        
                        status_text.text("✅ 批量拉取完成")
                        st.success(f"已完成 {len(trade_dates)} 个交易日的数据拉取")
                
                except Exception as e:
                    st.error(f"批量拉取失败: {e}")

with tab2:
    st.subheader("🔨 面板构建")
    
    st.info("面板构建：将Raw层数据合并、清洗、转换为 daily_panel / funda_panel")
    
    st.markdown("### 📊 交易日面板（daily_panel）")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("合并 daily + daily_basic + adj_factor，生成统一面板")
        
        panel_date = st.date_input(
            "选择构建日期",
            value=datetime.now() - timedelta(days=1),
            key="panel_date"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🔨 构建面板", key="build_panel"):
            date_str = panel_date.strftime("%Y%m%d")
            with st.spinner(f"正在构建 {date_str} 的面板..."):
                try:
                    # 初始化表结构
                    db.create_daily_panel_table()
                    
                    # 构建面板
                    builder = DailyPanelBuilder()
                    builder.build_for_date(date_str)
                    
                    st.success(f"✅ {date_str} 面板构建完成")
                    
                    # 查询结果预览
                    preview = db.query(f"""
                        SELECT COUNT(*) as cnt, 
                               MIN(trade_date) as min_date, 
                               MAX(trade_date) as max_date
                        FROM daily_panel
                        WHERE trade_date = '{date_str}'
                    """)
                    
                    if len(preview) > 0:
                        st.write(f"📊 面板记录数: {preview.iloc[0]['cnt']}")
                
                except Exception as e:
                    st.error(f"构建失败: {e}")
                    st.exception(e)
    
    # 批量构建
    with st.expander("📅 批量构建日期范围"):
        col1, col2 = st.columns(2)
        
        with col1:
            build_start = st.date_input(
                "起始日期",
                value=datetime.now() - timedelta(days=30),
                key="build_start"
            )
        
        with col2:
            build_end = st.date_input(
                "结束日期",
                value=datetime.now(),
                key="build_end"
            )
        
        if st.button("🔨 批量构建", key="build_batch"):
            start_str = build_start.strftime("%Y%m%d")
            end_str = build_end.strftime("%Y%m%d")
            
            with st.spinner(f"正在批量构建 {start_str}~{end_str}..."):
                try:
                    db.create_daily_panel_table()
                    
                    builder = DailyPanelBuilder()
                    builder.build_for_range(start_str, end_str)
                    
                    st.success(f"✅ 批量构建完成")
                    
                    # 统计
                    stats = db.query("""
                        SELECT COUNT(*) as total_rows,
                               COUNT(DISTINCT ts_code) as unique_stocks,
                               MIN(trade_date) as start_date,
                               MAX(trade_date) as end_date
                        FROM daily_panel
                    """)
                    
                    if len(stats) > 0:
                        st.write("### 📊 面板统计")
                        st.write(f"- 总记录数: {stats.iloc[0]['total_rows']}")
                        st.write(f"- 股票数: {stats.iloc[0]['unique_stocks']}")
                        st.write(f"- 日期范围: {stats.iloc[0]['start_date']} ~ {stats.iloc[0]['end_date']}")
                
                except Exception as e:
                    st.error(f"批量构建失败: {e}")

with tab3:
    st.subheader("📜 运行历史")
    
    try:
        # ETL状态
        etl_state = db.query("""
            SELECT api_name, watermark_value, last_success_at, last_row_count
            FROM etl_state
            ORDER BY last_success_at DESC
            LIMIT 20
        """)
        
        if len(etl_state) > 0:
            st.markdown("### 💾 增量水位（Watermark）")
            st.dataframe(etl_state, use_container_width=True)
        else:
            st.info("暂无运行记录")
    
    except Exception as e:
        st.warning(f"查询运行历史失败: {e}")

st.markdown("---")
st.caption("💡 路线B升级后，将支持可视化Flow Canvas（拖拽节点、连线、从任意节点运行）")
