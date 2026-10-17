import streamlit as st
import plotly.express as px
import pandas as pd
from utils import t, get_lang

st.title(t("origin_title"))

filtered_df = st.session_state.get("filtered_df")
start_date = st.session_state.get("start_date")
end_date = st.session_state.get("end_date")
lang = get_lang()

if filtered_df is None or filtered_df.empty:
    st.warning(t("no_data"))
    st.stop()

st.caption(f"{t('date_range_label')}: **{start_date}** ~ **{end_date}**")

origin_df = filtered_df[filtered_df["产地"] != "全国"].copy()
if origin_df.empty:
    st.info(t("no_data"))
    st.stop()

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


def reference_level(n):
    if n == 1:
        return t("single_point")
    elif n <= 3:
        return t("normal")
    else:
        return t("high")


origin_summary["参考性"] = origin_summary["样本数"].apply(reference_level)
origin_summary = origin_summary.sort_values("均价", ascending=True)

# ========== 图1：各产区平均价格对比 ==========
st.subheader(t("origin_avg_title"))
st.caption(t("origin_avg_note"))

origin_summary["颜色深度"] = origin_summary["样本数"].apply(lambda n: 1.0 if n >= 2 else 0.35)

fig1 = px.bar(
    origin_summary, x="均价", y="产地", orientation="h",
    text="均价", color="均价",
    color_continuous_scale="Purples",
    labels={"均价": t("avg_price_col"), "产地": ""},
    hover_data={"样本数": True, "最高价": ":.1f", "最低价": ":.1f", "数据日期范围": True}
)
fig1.update_traces(
    texttemplate='%{text:.1f}', textposition='outside',
    textfont=dict(size=13, color="#1A1A1A"),
    marker=dict(opacity=origin_summary["颜色深度"].tolist(), line=dict(width=0))
)
fig1.update_layout(
    showlegend=False, coloraxis_showscale=False, height=600,
    font=dict(size=13, color="#1A1A1A"),
    margin=dict(l=150, r=50, t=30, b=50)
)
st.plotly_chart(fig1, use_container_width=True)

# ========== 图2：明细表 ==========
st.subheader(t("origin_detail_title"))
st.dataframe(
    origin_summary[["产地", "均价", "最高价", "最低价", "样本数", "参考性", "数据日期范围"]],
    use_container_width=True,
    column_config={
        "产地": t("origin_col"),
        "均价": st.column_config.NumberColumn(t("avg_price_col"), format="%.1f"),
        "最高价": st.column_config.NumberColumn(t("max_price_col"), format="%.1f"),
        "最低价": st.column_config.NumberColumn(t("min_price_col"), format="%.1f"),
        "样本数": st.column_config.NumberColumn(t("sample_count"), format="%d"),
        "参考性": st.column_config.TextColumn(t("reference"), width="small"),
        "数据日期范围": st.column_config.TextColumn(t("date_range_col"), width="medium"),
    }
)

# ========== 图3：采购建议 ==========
st.markdown(f"### {t('purchase_advice')}")
reliable = origin_summary[origin_summary["样本数"] >= 2]
if not reliable.empty:
    best = reliable.iloc[0]
    worst = reliable.iloc[-1]
    gap = worst["均价"] - best["均价"]
    st.success(
        f"**{best['产地']}** ({best['均价']:.1f} {t('yuan_per_kg')}, n={int(best['样本数'])}) vs "
        f"**{worst['产地']}** ({worst['均价']:.1f} {t('yuan_per_kg')}) | "
        f"{t('price_gap')}: **{gap:.1f} {t('yuan_per_kg')}**"
    )

st.markdown("---")

# ========== 互动 1：进货成本模拟器 ==========
st.markdown("### 🛒 进货成本模拟器")
st.caption("假设您要进货，拖动下方滑块测算预估成本（基于近期均价）。")

col_calc_1, col_calc_2 = st.columns(2)
with col_calc_1:
    origins = sorted(origin_summary["产地"].unique().tolist())
    selected_origin = st.selectbox("选择意向产地", origins)
with col_calc_2:
    weight = st.number_input("输入进货重量 (公斤)", min_value=10, max_value=10000, value=100, step=50)

if selected_origin and weight:
    target_row = origin_summary[origin_summary["产地"] == selected_origin].iloc[0]
    avg_price = target_row["均价"]
    total_cost = avg_price * weight

    st.info(f"📊 **测算结果**：**{selected_origin}** 的近期均价约为 **{avg_price:.2f} 元/公斤**。\n\n"
            f"进货 **{weight} 公斤**，预计总成本为：**{total_cost:,.2f} 元**。")

    cheapest = origin_summary.iloc[0]
    if cheapest["产地"] != selected_origin:
        save_cost = (avg_price - cheapest["均价"]) * weight
        st.success(f"💡 **采购建议**：如果您选择全市场均价最低的 **{cheapest['产地']}**（{cheapest['均价']:.2f} 元/公斤），"
                   f"同样的重量可以省下 **{save_cost:,.2f} 元**！")

st.markdown("---")

# ========== 互动 2：自定义画图器 ==========
with st.expander("🛠️ 进阶探索：自定义图表生成器"):
    st.markdown("自己动手，探索数据中隐藏的关联关系。")

    col_x, col_y, col_c = st.columns(3)
    with col_x:
        x_axis = st.selectbox("X轴（横轴）", ["日期", "月份", "产地", "果径(mm)", "省份"])
    with col_y:
        y_axis = st.selectbox("Y轴（纵轴）", ["均价(元/kg)", "最高价(元/kg)", "最低价(元/kg)"])
    with col_c:
        color_by = st.selectbox("颜色分类", ["产地", "渠道类型", "等级", "省份", None])

    fig_custom = px.scatter(
        filtered_df, x=x_axis, y=y_axis, color=color_by,
        hover_data=["产地", "品种规格", "备注"],
        height=500,
        labels={"均价(元/kg)": "价格 (元/公斤)"}
    )
    fig_custom.update_layout(font=dict(color="#1A1A1A", size=13))
    st.plotly_chart(fig_custom, use_container_width=True)