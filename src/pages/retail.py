import streamlit as st
import plotly.express as px

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

# 零售端规格价格对比
st.subheader("零售端不同规格价格对比")
fig = px.bar(
    retail_df, x="品种规格", y="均价(元/kg)",
    color="产地", barmode="group",
    text="均价(元/kg)",
    labels={"均价(元/kg)": "价格 (元/公斤)"}
)
fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig.update_layout(xaxis_tickangle=-45, height=450)
st.plotly_chart(fig, use_container_width=True)

# 果径 vs 价格分析
st.subheader("果径大小 vs 零售价格")
retail_analysis = retail_df[retail_df["品种规格"].str.contains("mm", na=False)].copy()
retail_analysis["果径"] = retail_analysis["品种规格"].str.extract(r'(\d+)mm').astype(float)
retail_analysis = retail_analysis.dropna(subset=["果径", "均价(元/kg)"])

if not retail_analysis.empty:
    fig_scatter = px.scatter(
        retail_analysis,
        x="果径", y="均价(元/kg)",
        color="产地", size="均价(元/kg)",
        hover_data=["品种规格"],
        labels={"果径": "果径 (mm)", "均价(元/kg)": "价格 (元/公斤)"}
    )
    fig_scatter.update_layout(height=450)
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("暂无包含果径规格(mm)的数据。")