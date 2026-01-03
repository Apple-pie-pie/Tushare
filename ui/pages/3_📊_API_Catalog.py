"""API Catalog：接口目录与权限管理"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import load_endpoint_registry, get_available_endpoints, TUSHARE_POINTS
from src.core import get_client

st.set_page_config(page_title="API Catalog", page_icon="📊", layout="wide")

st.title("📊 API Catalog - 接口目录")

st.info(f"""
**你的当前积分档位：{TUSHARE_POINTS}+**（5000+积分对应：500次/分钟，约90%接口可用）

本页面展示所有Tushare接口的：
- 接口名 / 类别 / 权限模式 / 最低积分
- 主键字段（PK）/ 增量字段（Watermark）
- 当前状态（可用 / 无权限 / 需独立开通）
""")

# 加载接口注册表
registry = load_endpoint_registry()
endpoints = get_available_endpoints(TUSHARE_POINTS)

# 转为DataFrame
records = []
for api_name, config in endpoints.items():
    records.append({
        "接口名": api_name,
        "类别": config.get("category", ""),
        "权限模式": config.get("permission_mode", ""),
        "最低积分": config.get("min_points", "独立开通"),
        "主键字段": ", ".join(config.get("pk_fields", [])),
        "增量字段": config.get("watermark_field", "N/A"),
        "当前状态": "✅ 可用" if config.get("user_can_access") else "⚠️ 无权限",
        "描述": config.get("description", ""),
    })

df = pd.DataFrame(records)

# 筛选器
col1, col2, col3 = st.columns(3)

with col1:
    category_filter = st.multiselect(
        "按类别筛选",
        options=df["类别"].unique(),
        default=None
    )

with col2:
    permission_filter = st.selectbox(
        "按权限模式筛选",
        options=["全部", "积分接口", "独立权限接口"],
        index=0
    )

with col3:
    status_filter = st.selectbox(
        "按状态筛选",
        options=["全部", "可用", "无权限"],
        index=0
    )

# 应用筛选
filtered_df = df.copy()

if category_filter:
    filtered_df = filtered_df[filtered_df["类别"].isin(category_filter)]

if permission_filter == "积分接口":
    filtered_df = filtered_df[filtered_df["权限模式"] == "points"]
elif permission_filter == "独立权限接口":
    filtered_df = filtered_df[filtered_df["权限模式"] == "independent"]

if status_filter == "可用":
    filtered_df = filtered_df[filtered_df["当前状态"] == "✅ 可用"]
elif status_filter == "无权限":
    filtered_df = filtered_df[filtered_df["当前状态"] == "⚠️ 无权限"]

# 显示结果
st.markdown(f"### 📋 接口列表（共 {len(filtered_df)} 个）")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=600,
    column_config={
        "接口名": st.column_config.TextColumn("接口名", width="medium"),
        "类别": st.column_config.TextColumn("类别", width="small"),
        "当前状态": st.column_config.TextColumn("当前状态", width="small"),
        "描述": st.column_config.TextColumn("描述", width="large"),
    }
)

# 统计卡片
st.markdown("---")
st.subheader("📊 统计信息")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_count = len(df)
    st.metric("总接口数", total_count)

with col2:
    available_count = len(df[df["当前状态"] == "✅ 可用"])
    st.metric("可用接口", available_count)

with col3:
    no_permission_count = len(df[df["当前状态"] == "⚠️ 无权限"])
    st.metric("无权限接口", no_permission_count)

with col4:
    independent_count = len(df[df["权限模式"] == "independent"])
    st.metric("独立权限接口", independent_count)

# 探测接口能力
st.markdown("---")
st.subheader("🔍 接口能力探测")

st.write("探测接口实际可用性（发起最小请求，检查是否返回数据或权限错误）")

if st.button("🚀 探测所有接口", key="probe_all"):
    with st.spinner("正在探测接口能力..."):
        try:
            client = get_client()
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            
            for i, (api_name, config) in enumerate(endpoints.items()):
                status_text.text(f"探测: {api_name}")
                
                status, message = client.probe_endpoint(api_name)
                
                results.append({
                    "接口名": api_name,
                    "探测状态": status,
                    "消息": message,
                })
                
                progress_bar.progress((i + 1) / len(endpoints))
            
            status_text.text("✅ 探测完成")
            
            # 显示结果
            result_df = pd.DataFrame(results)
            st.dataframe(result_df, use_container_width=True)
            
            # 保存到数据库
            from src.core import db
            for result in results:
                db.execute("""
                    INSERT OR REPLACE INTO endpoint_capabilities 
                    (api_name, status, message, last_probe_at)
                    VALUES (?, ?, ?, datetime('now'))
                """, (result["接口名"], result["探测状态"], result["消息"]))
            
            st.success("探测结果已保存到数据库")
        
        except Exception as e:
            st.error(f"探测失败: {e}")

# 详细信息
st.markdown("---")
st.subheader("🔎 接口详情查询")

selected_api = st.selectbox(
    "选择接口查看详情",
    options=df["接口名"].tolist(),
    index=0
)

if selected_api:
    api_config = registry[selected_api]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**基本信息**")
        st.write(f"- **类别**: {api_config.get('category')}")
        st.write(f"- **权限模式**: {api_config.get('permission_mode')}")
        st.write(f"- **最低积分**: {api_config.get('min_points', '独立开通')}")
        st.write(f"- **描述**: {api_config.get('description')}")
    
    with col2:
        st.markdown("**技术信息**")
        st.write(f"- **主键字段**: {', '.join(api_config.get('pk_fields', []))}")
        st.write(f"- **增量字段**: {api_config.get('watermark_field', 'N/A')}")
        st.write(f"- **最大行数**: {api_config.get('max_rows', 'N/A')}")
        st.write(f"- **增量策略**: {api_config.get('increment_strategy', 'N/A')}")

st.markdown("---")
st.caption("💡 提示：独立权限接口需要联系Tushare官方单独开通（如分钟线、新闻公告等）")
