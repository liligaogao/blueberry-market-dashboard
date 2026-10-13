import streamlit as st
import plotly.express as px

st.title("📍 产区分析")

filtered_df = st.session_state.get("filtered_df")

if filtered_df is None or filtered_df.empty:
    st.warning("当前筛选条件下暂无数据。")
    st.stop()

origin_df = filtered_df[filtered_df["产地"] != "全国"].copy()

if origin_df.empty:
    st.info("暂无产地数据。")
    st.stop()

latest_date = origin_df["日期"].max()
latest_origin = origin_df[origin_df["日期"] == latest_date]

# 产地价格对比
st.subheader(f"主产区价格对比（{latest_date.strftime('%Y-%m-%d')}）")
fig = px.bar(
    latest_origin, x="产地", y="均价(元/kg)",
    color="产地", text="均价(元/kg)",
    labels={"均价(元/kg)": "价格 (元/公斤)"}
)
fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig.update_layout(showlegend=False, xaxis_tickangle=-45, height=450)
st.plotly_chart(fig, use_container_width=True)

# 各产区价格分布
st.subheader("各产区价格分布")
fig_box = px.box(
    origin_df, x="产地", y="均价(元/kg)",
    color="产地",
    labels={"均价(元/kg)": "价格 (元/公斤)"}
)
fig_box.update_layout(showlegend=False, height=450)
st.plotly_chart(fig_box, use_container_width=True)