"""Market Terminal：股票分析终端"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import db
from src.panel import DailyPanelBuilder

st.set_page_config(page_title="Market Terminal", page_icon="🏠", layout="wide")

st.title("🏠 Market Terminal - 股票分析终端")

# 侧边栏：自选股
st.sidebar.header("📋 自选股列表")

# 示例自选股（实际应从数据库加载）
default_watchlist = ["000001.SZ", "600000.SH", "000858.SZ", "600519.SH"]

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = default_watchlist

# 添加自选股
with st.sidebar.expander("➕ 添加股票"):
    new_stock = st.text_input("输入股票代码", placeholder="000001.SZ")
    if st.button("添加"):
        if new_stock and new_stock not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_stock)
            st.success(f"已添加 {new_stock}")
        st.rerun()

# 显示自选股
st.sidebar.markdown("---")
selected_stock = st.sidebar.radio(
    "选择查看股票",
    st.session_state.watchlist,
    index=0 if st.session_state.watchlist else None
)

# 主界面
if not selected_stock:
    st.warning("请先添加自选股")
    st.stop()

st.subheader(f"📊 {selected_stock} - 行情分析")

# 日期范围选择
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    start_date = st.date_input(
        "起始日期",
        value=datetime.now() - timedelta(days=180),
        max_value=datetime.now()
    )
with col2:
    end_date = st.date_input(
        "结束日期",
        value=datetime.now(),
        max_value=datetime.now()
    )
with col3:
    if st.button("🔄 刷新数据"):
        st.rerun()

# 查询数据
try:
    builder = DailyPanelBuilder()
    df = builder.query_panel(
        ts_codes=[selected_stock],
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        limit=500
    )
    
    if df is None or len(df) == 0:
        st.warning(f"暂无 {selected_stock} 的数据，请先在 Data Studio 拉取数据")
        st.stop()
    
    # 数据预处理
    df = df.sort_values('trade_date')
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    
    # Tab布局
    tab1, tab2, tab3, tab4 = st.tabs(["📈 K线图", "📊 指标", "💰 估值", "📋 数据表"])
    
    with tab1:
        st.subheader("K线与成交量")
        
        # K线图
        fig = go.Figure()
        
        # 添加K线
        fig.add_trace(go.Candlestick(
            x=df['trade_date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='K线'
        ))
        
        # 添加均线
        if len(df) >= 5:
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()
            
            fig.add_trace(go.Scatter(
                x=df['trade_date'],
                y=df['ma5'],
                mode='lines',
                name='MA5',
                line=dict(color='orange', width=1)
            ))
            
            fig.add_trace(go.Scatter(
                x=df['trade_date'],
                y=df['ma20'],
                mode='lines',
                name='MA20',
                line=dict(color='purple', width=1)
            ))
        
        fig.update_layout(
            height=500,
            xaxis_rangeslider_visible=False,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 成交量
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(
            x=df['trade_date'],
            y=df['vol'],
            name='成交量',
            marker_color='lightblue'
        ))
        fig_vol.update_layout(height=200, showlegend=False)
        st.plotly_chart(fig_vol, use_container_width=True)
    
    with tab2:
        st.subheader("每日指标")
        
        col1, col2, col3, col4 = st.columns(4)
        
        latest = df.iloc[-1]
        
        with col1:
            st.metric("最新价", f"{latest['close']:.2f}" if pd.notna(latest['close']) else "N/A")
        with col2:
            st.metric("涨跌幅", f"{latest['pct_chg']:.2f}%" if pd.notna(latest['pct_chg']) else "N/A")
        with col3:
            st.metric("换手率", f"{latest['turnover_rate']:.2f}%" if pd.notna(latest.get('turnover_rate')) else "N/A")
        with col4:
            st.metric("成交额(万)", f"{latest['amount']/10000:.0f}" if pd.notna(latest['amount']) else "N/A")
        
        # PE/PB走势
        if 'pe_ttm' in df.columns and 'pb' in df.columns:
            fig_pe = go.Figure()
            fig_pe.add_trace(go.Scatter(x=df['trade_date'], y=df['pe_ttm'], name='PE(TTM)', line=dict(color='blue')))
            fig_pe.add_trace(go.Scatter(x=df['trade_date'], y=df['pb'], name='PB', line=dict(color='green'), yaxis='y2'))
            
            fig_pe.update_layout(
                title="估值走势",
                yaxis=dict(title="PE(TTM)"),
                yaxis2=dict(title="PB", overlaying='y', side='right'),
                height=400
            )
            st.plotly_chart(fig_pe, use_container_width=True)
    
    with tab3:
        st.subheader("估值卡片")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pe_ttm = latest.get('pe_ttm')
            st.metric("PE(TTM)", f"{pe_ttm:.2f}" if pd.notna(pe_ttm) else "N/A")
            st.caption("市盈率（滚动）")
        
        with col2:
            pb = latest.get('pb')
            st.metric("PB", f"{pb:.2f}" if pd.notna(pb) else "N/A")
            st.caption("市净率")
        
        with col3:
            total_mv = latest.get('total_mv')
            st.metric("总市值", f"{total_mv/10000:.2f}亿" if pd.notna(total_mv) else "N/A")
            st.caption("总市值")
        
        st.info("💡 估值分位、ROE趋势等高级功能需先构建 funda_panel")
    
    with tab4:
        st.subheader("历史数据")
        
        # 选择显示列
        display_cols = ['trade_date', 'close', 'pct_chg', 'vol', 'amount', 
                        'turnover_rate', 'pe_ttm', 'pb', 'total_mv']
        available_cols = [col for col in display_cols if col in df.columns]
        
        display_df = df[available_cols].copy()
        display_df = display_df.sort_values('trade_date', ascending=False).head(100)
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # 导出
        csv = display_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 导出CSV",
            data=csv,
            file_name=f"{selected_stock}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv'
        )

except Exception as e:
    st.error(f"查询数据失败: {e}")
    st.exception(e)

# 底部信息
st.markdown("---")
st.caption("💡 提示：更多功能（筛选器、多图布局、财务趋势）持续开发中...")
