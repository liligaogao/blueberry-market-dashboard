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

# ========== 图1：各产区平均价格对比（彩色横向条） ==========
st.subheader("各产区平均价格对比")

fig1 = px.bar(
    origin_summary_sorted, x="均价", y="产地", orientation="h",
    text="均价", color="均价",
    color_continuous_scale="Turbo", # 换成鲜艳的彩虹色系
    labels={"均价": "平均价格 (元/公斤)", "产地": ""},
    hover_data={"样本数": True, "最高价": ":.1f", "最低价": ":.1f"}
)
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

# ========== 图2：各产区价格区间与均价（彩色区间点图） ==========
st.subheader("各产区价格区间与均价分布")

# 计算误差线（为了画出从最低价到最高价的水平线）
origin_summary_sorted["上限误差"] = origin_summary_sorted["最高价"] - origin_summary_sorted["均价"]
origin_summary_sorted["下限误差"] = origin_summary_sorted["均价"] - origin_summary_sorted["最低价"]

fig2 = px.scatter(
    origin_summary_sorted,
    x="均价",
    y="产地",
    color="均价",               # 用颜色映射价格
    color_continuous_scale="Plasma", # 鲜艳的渐变色板（紫-红-黄）
    error_x="上限误差",          # 向右画到最高价
    error_x_minus="下限误差",    # 向左画到最低价
    text="均价",
    labels={"均价": "价格 (元/公斤)", "产地": ""}
)

# 美化点和线
fig2.update_traces(
    marker=dict(size=18, line=dict(width=2, color='#2c3e50')), # 大圆点，带深色边框
    error_x=dict(thickness=3, width=6, color='#7f8c8d'),      # 加粗误差线（灰色）
    texttemplate='%{text:.1f}',
    textposition='top center',
    textfont=dict(size=15, color='black')
)

# 强制放大所有字体
fig2.update_layout(
    height=800,
    font=dict(size=16),
    coloraxis_showscale=False, # 隐藏颜色条，让画面更干净
    xaxis=dict(tickfont=dict(size=15), title_font=dict(size=18), title="价格 (元/公斤)"),
    yaxis=dict(tickfont=dict(size=15), automargin=True),
    margin=dict(l=50, r=50, t=50, b=50)
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