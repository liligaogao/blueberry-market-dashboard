import streamlit as st
import plotly.express as px
import pandas as pd

st.title("🛒 零售市场")

filtered_df = st.session_state.get("filtered_df")
if filtered_df is None or filtered_df.empty:
    st.warning("当前筛选条件下暂无数据。")
    st.stop()

retail_channels = ["济南大润发", "盒马鲜生", "上海市场", "北京新发地"]
retail_df = filtered_df[filtered_df["产地"].isin(retail_channels)].copy()
if retail_df.empty:
    st.info("暂无零售端数据。")
    st.stop()

# 提取果径数值
retail_df["果径"] = retail_df["品种规格"].str.extract(r'(\d+)mm').astype(float)
retail_df = retail_df.dropna(subset=["果径", "均价(元/kg)"])

# ========== 图1：果径 vs 价格（带趋势线） ==========
st.subheader("果径大小 vs 零售价格")

fig = px.scatter(
    retail_df, x="果径", y="均价(元/kg)",
    color="产地", size="均价(元/kg)",
    hover_data=["品种规格"],
    labels={"果径": "果径 (mm)", "均价(元/kg)": "价格 (元/公斤)"},
    trendline="ols"  # 自动加一条趋势线
)
fig.update_layout(height=450)
st.plotly_chart(fig, use_container_width=True)

# ========== 图2：各渠道同规格价格对比（分组柱状图） ==========
st.subheader("各渠道同规格价格对比")

# 按规格排序
retail_df["规格排序"] = retail_df["果径"].fillna(0)
retail_df = retail_df.sort_values("规格排序")

fig2 = px.bar(
    retail_df, x="品种规格", y="均价(元/kg)",
    color="产地", barmode="group",
    text="均价(元/kg)",
    labels={"均价(元/kg)": "价格 (元/公斤)"}
)
fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig2.update_layout(xaxis_tickangle=-45, height=450)
st.plotly_chart(fig2, use_container_width=True)

# ========== 图3：自动性价比建议 ==========
st.markdown("### 💡 性价比建议")
if not retail_df.empty:
    # 找同一规格下最便宜的渠道
    best_value = retail_df.loc[retail_df.groupby("品种规格")["均价(元/kg)"].idxmin()]
    best_value = best_value.sort_values("品种规格")
    st.info(
        "以下是最新数据中，**同一规格下价格最低的渠道**（性价比较高）：\n\n"
        + "\n".join([
            f"- **{row['品种规格']}**：{row['产地']}（{row['均价(元/kg)']:.1f} 元/公斤）"
            for _, row in best_value.iterrows()
        ])
    )