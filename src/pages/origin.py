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

# ========== 核心：计算各产地的数据汇总（图1和图2共用） ==========
origin_summary = origin_df.groupby("产地").agg(
    均价=("均价(元/kg)", "mean"),
    最高价=("均价(元/kg)", "max"),
    最低价=("均价(元/kg)", "min"),
    样本数=("均价(元/kg)", "count")
).reset_index().sort_values("均价", ascending=True)

# 按均价排序后，给图1和图2共用
origin_summary_sorted = origin_summary.sort_values("均价", ascending=True)

# ========== 图1：各产区平均价格对比 ==========
st.subheader("各产区平均价格对比")

fig1 = px.bar(
    origin_summary_sorted, x="均价", y="产地", orientation="h",
    text="均价", color="均价",
    color_continuous_scale="Blues",
    labels={"均价": "平均价格 (元/公斤)", "产地": ""},
    hover_data={"样本数": True, "最高价": ":.1f", "最低价": ":.1f"}
)
fig1.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig1.update_layout(showlegend=False, coloraxis_showscale=False, height=450)
st.plotly_chart(fig1, use_container_width=True)

# ========== 图2：各产区均价与价格区间对比（分组柱状图） ==========
st.subheader("各产区均价与价格区间对比")

# 1. 把数据“融化”成长表，方便分组画图
melted_df = origin_summary_sorted.melt(
    id_vars=["产地"],
    value_vars=["均价", "最高价", "最低价"],
    var_name="价格类型",
    value_name="价格"
)

# 2. 画分组柱状图
fig2 = px.bar(
    melted_df,
    x="价格",
    y="产地",
    color="价格类型",
    barmode="group",
    orientation="h",
    text="价格",
    labels={"价格": "价格 (元/公斤)", "产地": "", "价格类型": "指标"}
)

# 👇 修改2：增大全局字体（坐标轴、图例、标题），并拉高图表
fig2.update_layout(
    height=700,  # 高度从 500 提高到 700，避免三根柱子挤在一起
    font=dict(size=14),  # 全局字号统一调大
    xaxis_title="价格 (元/公斤)",
    yaxis_title="",
    legend_title=""
)
st.plotly_chart(fig2, use_container_width=True)

# 3. 画分组柱状图
fig2 = px.bar(
    melted_df,
    x="价格",
    y="产地",
    color="价格类型",
    barmode="group",  # 并排显示
    orientation="h",
    text="价格",
    labels={"价格": "价格 (元/公斤)", "产地": "", "价格类型": "指标"}
)
fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig2.update_layout(
    height=500,
    xaxis_title="价格 (元/公斤)",
    yaxis_title="",
    legend_title=""
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

# 数据明细表（可选）
with st.expander("📋 查看各产区详细数据"):
    st.dataframe(origin_summary_sorted, use_container_width=True)