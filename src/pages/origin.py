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

# ========== 图1：各产区平均价格对比（横向条形图） ==========
st.subheader("各产区平均价格对比")

# 计算每个产地的平均价、最高价、最低价、样本量
origin_summary = origin_df.groupby("产地").agg(
    均价=("均价(元/kg)", "mean"),
    最高价=("均价(元/kg)", "max"),
    最低价=("均价(元/kg)", "min"),
    样本数=("均价(元/kg)", "count")
).reset_index().sort_values("均价", ascending=True)

fig1 = px.bar(
    origin_summary, x="均价", y="产地", orientation="h",
    text="均价", color="均价",
    color_continuous_scale="Blues",
    labels={"均价": "平均价格 (元/公斤)", "产地": ""},
    hover_data={"样本数": True, "最高价": ":.1f", "最低价": ":.1f"}
)
fig1.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig1.update_layout(showlegend=False, coloraxis_showscale=False, height=450)
st.plotly_chart(fig1, use_container_width=True)

# ========== 图2：各产区价格区间（带样本量标注） ==========
st.subheader("各产区价格区间（最高-最低）")

# 按均价排序，让图更直观
origin_summary_sorted = origin_summary.sort_values("均价", ascending=True)

fig2 = px.bar(
    origin_summary_sorted, x="均价", y="产地", orientation="h",
    error_x=None,
    text="样本数",
    labels={"均价": "价格 (元/公斤)", "产地": ""},
    hover_data={"最高价": ":.1f", "最低价": ":.1f", "样本数": True}
)
# 手动添加价格区间线段
for i, row in origin_summary_sorted.iterrows():
    fig2.add_shape(
        type="line",
        x0=row["最低价"], x1=row["最高价"],
        y0=row["产地"], y1=row["产地"],
        line=dict(color="red", width=2)
    )
fig2.update_traces(texttemplate='n=%{text}', textposition='outside')
fig2.update_layout(showlegend=False, height=450)
st.plotly_chart(fig2, use_container_width=True)

# ========== 图3：自动采购建议 ==========
st.markdown("### 💡 采购建议")
if not origin_summary.empty:
    best = origin_summary.iloc[0]      # 均价最低的
    worst = origin_summary.iloc[-1]    # 均价最高的
    gap = worst["均价"] - best["均价"]
    st.success(
        f"在您当前筛选的 **{len(origin_summary)}** 个产地中，"
        f"**{best['产地']}** 平均价最低（**{best['均价']:.1f} 元/公斤**，样本数 {int(best['样本数'])}），"
        f"**{worst['产地']}** 最高（**{worst['均价']:.1f} 元/公斤**）。"
        f"两者价差 **{gap:.1f} 元/公斤**。"
        f"如果追求性价比，优先考虑 {best['产地']}；如果追求品质，可参考 {worst['产地']}。"
    )

# 数据明细表（可选）
with st.expander("📋 查看各产区详细数据"):
    st.dataframe(origin_summary, use_container_width=True)