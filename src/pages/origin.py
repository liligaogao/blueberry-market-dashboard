import streamlit as st
import plotly.express as px
import pandas as pd
from utils import t, get_lang

st.title(t("origin_title"))

filtered_df = st.session_state.get("filtered_df")
start_date = st.session_state.get("start_date")
end_date = st.session_state.get("end_date")

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

# 图1
st.subheader(t("origin_avg_title"))
st.caption(t("origin_avg_note"))

origin_summary["颜色深度"] = origin_summary["样本数"].apply(lambda n: 1.0 if n >= 2 else 0.35)

fig1 = px.bar(
    origin_summary, x="均价", y="产地", orientation="h",
    text="均价", color="均价",
    color_continuous_scale="Purples",  # 换成紫色渐变，完美呼应蓝莓主题
    labels={"均价": t("avg_price_col"), "产地": ""},
    hover_data={"样本数": True, "最高价": ":.1f", "最低价": ":.1f", "数据日期范围": True}
)
fig1.update_traces(
    texttemplate='%{text:.1f}', textposition='outside', textfont=dict(size=14),
    marker=dict(opacity=origin_summary["颜色深度"].tolist(), line=dict(width=0))
)
fig1.update_layout(showlegend=False, coloraxis_showscale=False, height=600, font=dict(size=14), margin=dict(l=150, r=50, t=30, b=50))
st.plotly_chart(fig1, use_container_width=True)

# 图2 明细表
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

# 图3 采购建议
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
else:
    st.warning(t("no_data"))

single_points = origin_summary[origin_summary["样本数"] == 1]
if not single_points.empty:
    with st.expander(f"{t('single_point')} ({len(single_points)})"):
        st.dataframe(single_points[["产地", "均价", "数据日期范围", "参考性"]], use_container_width=True)