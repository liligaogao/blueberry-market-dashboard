import streamlit as st
import plotly.express as px
import pandas as pd

st.title("📍 产区分析")

filtered_df = st.session_state.get("filtered_df")
if filtered_df is None or filtered_df.empty:
    st.warning("当前筛选条件下暂无数据。")
    st.stop()

origin_df = filtered_df[filtered_df["产地"] != "全国"].copy()
if origin_df.empty:
    st.info("暂无产地数据。")
    st.stop()

# ========== 核心：计算各产地的数据汇总 ==========
origin_summary = origin_df.groupby("产地").agg(
    均价=("均价(元/kg)", "mean"),
    最高价=("均价(元/kg)", "max"),
    最低价=("均价(元/kg)", "min"),
    样本数=("均价(元/kg)", "count")
).reset_index().sort_values("均价", ascending=True)

origin_summary_sorted = origin_summary.sort_values("均价", ascending=True)

# ========== 图1：各产区平均价格对比（只保留这一个清晰的图表） ==========
st.subheader("各产区平均价格对比")

fig1 = px.bar(
    origin_summary_sorted, x="均价", y="产地", orientation="h",
    text="均价", color="均价",
    color_continuous_scale="Blues",
    labels={"均价": "平均价格 (元/公斤)", "产地": ""},
    hover_data={"样本数": True, "最高价": ":.1f", "最低价": ":.1f"}
)
# 放大图1的字号
fig1.update_traces(
    texttemplate='%{text:.1f}',
    textposition='outside',
    textfont=dict(size=14)
)
fig1.update_layout(
    showlegend=False,
    coloraxis_showscale=False,
    height=600,
    font=dict(size=14),
    margin=dict(l=150, r=50, t=30, b=50)
)
st.plotly_chart(fig1, use_container_width=True)

# ========== 图2：各产区价格区间与均价（高级区间点图） ==========
st.subheader("各产区价格区间与均价")

# 使用 Plotly 的散点图来画区间和均值
import plotly.graph_objects as go

fig2 = go.Figure()

# 1. 绘制价格区间（浅蓝色细线）
for i, row in origin_summary_sorted.iterrows():
    fig2.add_trace(go.Scatter(
        x=[row["最低价"], row["最高价"]],
        y=[row["产地"], row["产地"]],
        mode="lines",
        line=dict(color="lightblue", width=4),
        showlegend=False,
        hoverinfo="skip"
    ))

# 2. 绘制均价（深蓝色圆点）
fig2.add_trace(go.Scatter(
    x=origin_summary_sorted["均价"],
    y=origin_summary_sorted["产地"],
    mode="markers",
    marker=dict(color="#1f77b4", size=12),
    name="均价",
    hovertemplate="产地: %{y}<br>均价: %{x:.1f} 元/公斤<extra></extra>"
))

# 3. 强制放大所有字体，并拉高图表
fig2.update_layout(
    height=800,  # 高度拉高
    font=dict(size=18),  # 全局字体放大到18
    xaxis=dict(
        title="价格 (元/公斤)",
        tickfont=dict(size=16),
        title_font=dict(size=18)
    ),
    yaxis=dict(
        tickfont=dict(size=16),
        automargin=True  # 自动留出左侧空间，防止产地名称被截断
    ),
    legend=dict(font=dict(size=16)),
    margin=dict(l=50, r=50, t=30, b=50)
)

st.plotly_chart(fig2, use_container_width=True)

# ========== 图3：自动采购建议 ==========
st.markdown("### 💡 采购建议")
if not origin_summary_sorted.empty:
    best = origin_summary_sorted.iloc[0]      # 均价最低的
    worst = origin_summary_sorted.iloc[-1]    # 均价最高的
    gap = worst["均价"] - best["均价"]
    st.success(
        f"在您当前筛选的 **{len(origin_summary_sorted)}** 个产地中，"
        f"**{best['产地']}** 平均价最低（**{best['均价']:.1f} 元/公斤**，样本数 {int(best['样本数'])}），"
        f"**{worst['产地']}** 最高（**{worst['均价']:.1f} 元/公斤**）。"
        f"两者价差 **{gap:.1f} 元/公斤**。"
        f"如果追求性价比，优先考虑 {best['产地']}；如果追求品质，可参考 {worst['产地']}。"
    )

# 数据明细表（可选折叠）
with st.expander("📋 查看完整原始数据"):
    st.dataframe(origin_summary_sorted, use_container_width=True)