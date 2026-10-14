import streamlit as st
import plotly.express as px
import pandas as pd

st.title("📍 产区分析")

filtered_df = st.session_state.get("filtered_df")
start_date = st.session_state.get("start_date")
end_date = st.session_state.get("end_date")

if filtered_df is None or filtered_df.empty:
    st.warning("当前筛选条件下暂无数据。")
    st.stop()

st.caption(f"📅 当前数据时间范围：**{start_date}** 至 **{end_date}**")

origin_df = filtered_df[filtered_df["产地"] != "全国"].copy()
if origin_df.empty:
    st.info("暂无产地数据。")
    st.stop()

# ========== 汇总数据 ==========
origin_summary = origin_df.groupby("产地").agg(
    均价=("均价(元/kg)", "mean"),
    最高价=("均价(元/kg)", "max"),
    最低价=("均价(元/kg)", "min"),
    样本数=("均价(元/kg)", "count"),
    最早日期=("日期", "min"),
    最晚日期=("日期", "max")
).reset_index()

origin_summary["数据日期范围"] = (
    origin_summary["最早日期"].dt.strftime("%Y-%m-%d") + " ~ " +
    origin_summary["最晚日期"].dt.strftime("%Y-%m-%d")
)
origin_summary = origin_summary.drop(columns=["最早日期", "最晚日期"])

# ========== 新增：根据样本数生成"参考性"标签 ==========
def reference_level(n):
    if n == 1:
        return "⚠️ 单点报价"
    elif n <= 3:
        return "一般"
    else:
        return "较高"

origin_summary["参考性"] = origin_summary["样本数"].apply(reference_level)
origin_summary = origin_summary.sort_values("均价", ascending=True)

# ========== 图1：各产区平均价格对比 ==========
st.subheader("各产区平均价格对比")
st.caption(
    f"⚠️ 均价是 **{start_date} 至 {end_date}** 期间所有数据的算术平均。"
    f"**样本数 n=1 的柱子用浅色绘制，仅代表单点报价，不具有统计意义**。"
)

# 根据样本数给柱子不同的透明度和颜色强度
origin_summary["颜色深度"] = origin_summary["样本数"].apply(
    lambda n: 1.0 if n >= 2 else 0.35  # 单点数据透明度 0.35
)

fig1 = px.bar(
    origin_summary, x="均价", y="产地", orientation="h",
    text="均价", color="均价",
    color_continuous_scale="Tealgrn",
    labels={"均价": "平均价格 (元/公斤)", "产地": ""},
    hover_data={"样本数": True, "最高价": ":.1f", "最低价": ":.1f", "数据日期范围": True}
)
# 用 marker 透明度区分单点数据和多样本数据
fig1.update_traces(
    texttemplate='%{text:.1f}',
    textposition='outside',
    textfont=dict(size=14),
    marker=dict(
        opacity=origin_summary["颜色深度"].tolist(),
        line=dict(width=0)  # 去掉边框
    )
)
fig1.update_layout(
    showlegend=False,
    coloraxis_showscale=False,
    height=600,
    font=dict(size=14),
    margin=dict(l=150, r=50, t=30, b=50)
)
st.plotly_chart(fig1, use_container_width=True)

# ========== 图2：明细表格 ==========
st.subheader("各产区价格与样本量明细")
st.dataframe(
    origin_summary[["产地", "均价", "最高价", "最低价", "样本数", "参考性", "数据日期范围"]],
    use_container_width=True,
    column_config={
        "产地": "产地",
        "均价": st.column_config.NumberColumn("均价 (元/kg)", format="%.1f"),
        "最高价": st.column_config.NumberColumn("最高价 (元/kg)", format="%.1f"),
        "最低价": st.column_config.NumberColumn("最低价 (元/kg)", format="%.1f"),
        "样本数": st.column_config.NumberColumn("样本数 (n)", format="%d"),
        "参考性": st.column_config.TextColumn("数据参考性", width="small"),
        "数据日期范围": st.column_config.TextColumn("数据日期范围", width="medium"),
    }
)

# ========== 图3：采购建议（只基于样本数>=2的产区） ==========
st.markdown("### 💡 采购建议")

# 只保留有统计意义的产区（样本数 >= 2）
reliable = origin_summary[origin_summary["样本数"] >= 2]

if not reliable.empty:
    best = reliable.iloc[0]
    worst = reliable.iloc[-1]
    gap = worst["均价"] - best["均价"]
    st.success(
        f"在您当前筛选的 **{len(reliable)}** 个有统计意义的产区中，"
        f"**{best['产地']}** 平均价最低（**{best['均价']:.1f} 元/公斤**，样本数 {int(best['样本数'])}），"
        f"**{worst['产地']}** 最高（**{worst['均价']:.1f} 元/公斤**）。"
        f"两者价差 **{gap:.1f} 元/公斤**。"
    )
else:
    st.warning("当前筛选范围内没有样本数 ≥ 2 的产区，无法生成采购建议。")

# 单点报价单独提示
single_points = origin_summary[origin_summary["样本数"] == 1]
if not single_points.empty:
    with st.expander(f"⚠️ 查看仅含单点报价的 {len(single_points)} 个产区（仅供参考）"):
        st.dataframe(
            single_points[["产地", "均价", "数据日期范围", "参考性"]],
            use_container_width=True,
            column_config={
                "均价": st.column_config.NumberColumn("报价 (元/kg)", format="%.1f"),
                "参考性": st.column_config.TextColumn("提示"),
            }
        )