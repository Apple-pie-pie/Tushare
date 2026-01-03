"""Settings：系统设置"""
import streamlit as st
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

st.title("⚙️ Settings - 系统设置")

# Tab布局
tab1, tab2, tab3 = st.tabs(["🔑 Tushare配置", "💾 数据库", "📊 系统信息"])

with tab1:
    st.subheader("🔑 Tushare Token配置")
    
    st.info("""
    **如何获取Token？**
    
    1. 访问 [Tushare官网](https://tushare.pro) 注册账号
    2. 完成积分任务（邀请、贡献等）获得积分
    3. 在个人中心获取 Token
    4. 将Token填入下方并保存到 `.env` 文件
    """)
    
    # 读取现有配置
    env_path = Path(__file__).parent.parent.parent / ".env"
    current_token = ""
    current_points = "5000"
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith("TUSHARE_TOKEN="):
                    current_token = line.split("=", 1)[1].strip()
                elif line.startswith("TUSHARE_POINTS="):
                    current_points = line.split("=", 1)[1].strip()
    
    # Token输入
    col1, col2 = st.columns([3, 1])
    
    with col1:
        token_input = st.text_input(
            "Tushare Token",
            value=current_token if current_token else "",
            type="password",
            placeholder="请输入你的Tushare Token"
        )
    
    with col2:
        points_input = st.selectbox(
            "积分档位",
            options=["120", "2000", "5000", "10000", "15000"],
            index=["120", "2000", "5000", "10000", "15000"].index(current_points) if current_points in ["120", "2000", "5000", "10000", "15000"] else 2
        )
    
    # 保存配置
    if st.button("💾 保存配置", key="save_config"):
        if not token_input:
            st.error("Token不能为空")
        else:
            try:
                # 创建.env文件
                env_content = f"""# Tushare配置
TUSHARE_TOKEN={token_input}
TUSHARE_POINTS={points_input}

# 数据库配置
DATABASE_PATH=data/serve/tushare.duckdb

# 限频配置（{points_input}积分对应）
RATE_LIMIT_PER_MINUTE={{"120": "50", "2000": "200", "5000": "500", "10000": "1000", "15000": "1000"}[points_input]}
RATE_LIMIT_DAILY=999999

# 日志配置
LOG_LEVEL=INFO
"""
                
                with open(env_path, 'w') as f:
                    f.write(env_content)
                
                st.success("✅ 配置已保存到 .env 文件，请重启应用生效")
                
            except Exception as e:
                st.error(f"保存失败: {e}")
    
    # 测试连接
    st.markdown("---")
    st.subheader("🧪 测试连接")
    
    if st.button("🔍 测试Token & 查询积分", key="test_token"):
        if not token_input:
            st.warning("请先输入Token")
        else:
            with st.spinner("正在测试连接..."):
                try:
                    # 临时设置token（不保存）
                    os.environ["TUSHARE_TOKEN"] = token_input
                    
                    from src.core import TushareClient
                    client = TushareClient(token=token_input)
                    
                    # 获取用户信息
                    user_info = client.get_user_info()
                    
                    if user_info:
                        st.success("✅ Token有效，连接成功！")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("当前积分", user_info.get("score", "N/A"))
                        
                        with col2:
                            st.metric("到期日期", user_info.get("exp_date", "N/A"))
                        
                        with col3:
                            st.metric("用户组", user_info.get("user_type", "N/A"))
                        
                        # 显示详细信息
                        with st.expander("查看完整用户信息"):
                            st.json(user_info)
                    else:
                        st.error("无法获取用户信息，请检查Token")
                
                except Exception as e:
                    st.error(f"连接失败: {e}")
                    st.exception(e)

with tab2:
    st.subheader("💾 数据库管理")
    
    from config import DATABASE_PATH
    
    st.write(f"**数据库路径**: `{DATABASE_PATH}`")
    
    # 数据库统计
    try:
        from src.core import db
        
        # 初始化表（如果不存在）
        if st.button("🔧 初始化数据库表", key="init_db"):
            with st.spinner("正在初始化..."):
                try:
                    db.create_daily_panel_table()
                    db.create_funda_panel_table()
                    st.success("✅ 数据库表初始化完成")
                except Exception as e:
                    st.error(f"初始化失败: {e}")
        
        # 查询表统计
        st.markdown("---")
        st.subheader("📊 数据统计")
        
        tables = ["daily_panel", "funda_panel", "raw_daily", "raw_daily_basic", 
                  "raw_adj_factor", "stock_basic", "trade_cal"]
        
        stats_data = []
        
        for table in tables:
            try:
                result = db.query(f"SELECT COUNT(*) as cnt FROM {table}")
                count = result.iloc[0]['cnt'] if len(result) > 0 else 0
                stats_data.append({"表名": table, "记录数": count})
            except:
                stats_data.append({"表名": table, "记录数": "不存在"})
        
        import pandas as pd
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True)
    
    except Exception as e:
        st.warning(f"无法连接数据库: {e}")
        st.info("请先配置Token并运行初始化")

with tab3:
    st.subheader("📊 系统信息")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**环境信息**")
        st.write(f"- Python: {sys.version.split()[0]}")
        
        try:
            import tushare
            st.write(f"- Tushare: {tushare.__version__}")
        except:
            st.write("- Tushare: 未安装")
        
        try:
            import pandas
            st.write(f"- Pandas: {pandas.__version__}")
        except:
            pass
        
        try:
            import duckdb
            st.write(f"- DuckDB: {duckdb.__version__}")
        except:
            pass
    
    with col2:
        st.markdown("**项目信息**")
        st.write("- 版本: 1.0.0-alpha (路线A)")
        st.write("- 架构: Streamlit + DuckDB")
        st.write("- 数据源: Tushare Pro")
        st.write("- 开发状态: MVP阶段")
    
    st.markdown("---")
    st.subheader("🚀 升级路线")
    
    with st.expander("路线A → 路线B 升级计划"):
        st.markdown("""
        **当前路线A（快速原型）**：
        - ✅ Streamlit UI
        - ✅ 步骤式流程
        - ✅ DuckDB存储
        - ✅ 基础面板构建
        
        **路线B（专业版）升级**：
        - 🔲 React前端 + FastAPI后端
        - 🔲 可视化拖拽Canvas（React Flow）
        - 🔲 节点连线与流程设计
        - 🔲 多图布局与联动（TradingView风格）
        - 🔲 完整筛选器与策略回测
        - 🔲 Electron打包为桌面应用
        
        **升级时机**：
        - 路线A验证完成，业务逻辑稳定
        - 需要更复杂的交互体验
        - 需要分发给他人使用
        """)

st.markdown("---")
st.caption("💡 配置修改后，请重启Streamlit应用（Ctrl+C停止，重新运行 streamlit run ui/app.py）")
