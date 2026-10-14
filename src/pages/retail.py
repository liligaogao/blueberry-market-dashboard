import streamlit as st
import plotly.express as px
import pandas as pd
import re

st.title("🛒 零售市场")

filtered_df = st.session_state.get("filtered_df")
if filtered_df is None or filtered_df.empty:
    st.warning("当前筛选条件下暂无数据。")
    st.stop()

# 将你需要展示的所有零售渠道都加进来
retail_channels = ["济南大润发", "盒马鲜生", "上海市场", "北京新发地", "济南超市", "深圳盒马", "济南堤口", "全国超市"]
retail_df = filtered_df[filtered_df["产地"].isin(retail_channels)].copy()
if retail_df.empty:
    st.info("暂无零售端数据。")
    st.stop()

# ========== 关键优化：提取纯规格名称 ==========
# 比如把 "云南高山蓝莓14mm" 变成 "14mm"
def extract_spec(spec):
    match = re.search(r'(\d+mm\+?)', str(spec))
    return match.group(1) if match else spec

retail_df["规格简化"] = retail_df["品种规格"].apply(extract_spec)

# 提取果径用于散点图
retail_df["果径"] = retail_df["品种规格"].str.extract(r'(\d+)mm').astype(float)
retail_analysis = retail_df.dropna(subset=["果径", "均价(元/kg)"])

# ========== 图1：果径 vs 价格 ==========
st.subheader("果径大小 vs 零售价格")
if not retail_analysis.empty:
    fig_scatter = px.scatter(
        retail_analysis,
        x="果径", y="均价(元/kg)",
        color="产地", size="均价(元/kg)",
        hover_data=["品种规格"],
        labels={"果径": "果径 (mm)", "均价(元/kg)": "价格 (元/公斤)"},
        trendline="ols"
    )
    fig_scatter.update_layout(height=500, font=dict(size=14))
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("暂无包含果径规格的数据。")

# ========== 图2：各渠道同规格价格对比 ==========
st.subheader("各渠道同规格价格对比")
# 按简化后的规格排序
retail_df = retail_df.sort_values("规格简化")

fig2 = px.bar(
    retail_df, x="规格简化", y="均价(元/kg)",
    color="产地", barmode="group",
    text="均价(元/kg)",
    labels={"均价(元/kg)": "价格 (元/公斤)", "规格简化": "规格"}
)
fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside', textfont=dict(size=11))
fig2.update_layout(
    xaxis_tickangle=-45, # 倾斜45度
    height=600,          # 拉高图表
    font=dict(size=14),
    margin=dict(l=50, r=50, t=50, b=50)
)
st.plotly_chart(fig2, use_container_width=True)

# ========== 图3：性价比建议 ==========
st.markdown("### 💡 性价比建议")
if not retail_df.empty:
    best_value = retail_df.loc[retail_df.groupby("规格简化")["均价(元/kg)"].idxmin()]
    best_value = best_value.sort_values("规格简化")
    st.info(
        "以下是各规格下价格最低的渠道（性价比最高）：\n\n"
        + "\n".join([
            f"- **{row['规格简化']}**：{row['产地']}（{row['均价(元/kg)']:.1f} 元/公斤）"
            for _, row in best_value.iterrows()
        ])
    )