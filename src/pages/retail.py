import streamlit as st
import plotly.express as px
import pandas as pd
import re
from utils import t, get_lang

st.title(t("retail_title"))
start_date = st.session_state.get("start_date")
end_date = st.session_state.get("end_date")
st.caption(f"{t('date_range_label')}: **{start_date}** ~ **{end_date}**")

filtered_df = st.session_state.get("filtered_df")
if filtered_df is None or filtered_df.empty:
    st.warning(t("no_data"))
    st.stop()

retail_channels = ["济南大润发", "盒马鲜生", "上海市场", "北京新发地", "济南超市", "深圳盒马", "济南堤口", "全国超市"]
retail_df = filtered_df[filtered_df["产地"].isin(retail_channels)].copy()
if retail_df.empty:
    st.info(t("no_data"))
    st.stop()

def extract_spec(spec):
    match = re.search(r'(\d+mm\+?)', str(spec))
    return match.group(1) if match else spec

retail_df["规格简化"] = retail_df["品种规格"].apply(extract_spec)
retail_df["果径"] = retail_df["品种规格"].str.extract(r'(\d+)mm').astype(float)
retail_analysis = retail_df.dropna(subset=["果径", "均价(元/kg)"])

# 图1
st.subheader(t("diameter_vs_price"))
if not retail_analysis.empty:
    fig_scatter = px.scatter(
        retail_analysis, x="果径", y="均价(元/kg)",
        color="产地", size="均价(元/kg)",
        hover_data=["品种规格", "日期"],
        labels={"果径": "Size (mm)" if get_lang() == "en" else "果径 (mm)", "均价(元/kg)": t("avg_price_col")},
        trendline="ols"
    )
    fig_scatter.update_layout(
        height=450,
        font=dict(size=13, color="#1A1A1A") # 加深
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info(t("no_data"))

# 图2
st.subheader(t("channel_compare"))
retail_df = retail_df.sort_values("规格简化")

fig2 = px.bar(
    retail_df, x="规格简化", y="均价(元/kg)",
    color="产地", barmode="group",
    text="均价(元/kg)",
    labels={"均价(元/kg)": t("avg_price_col"), "规格简化": t("spec"), "产地": t("origin_label")}
)
fig2.update_traces(
    texttemplate='%{text:.1f}', textposition='outside',
    textfont=dict(size=12, color="#1A1A1A")
)
fig2.update_layout(
    xaxis_tickangle=-45, height=500,
    font=dict(size=13, color="#1A1A1A") # 加深
)
st.plotly_chart(fig2, use_container_width=True)

# 图3
st.markdown(f"### {t('value_advice')}")
if not retail_df.empty:
    best_value = retail_df.loc[retail_df.groupby("规格简化")["均价(元/kg)"].idxmin()].sort_values("规格简化")
    st.info("\n".join([
        f"- **{row['规格简化']}**: {row['产地']} ({row['均价(元/kg)']:.1f} {t('yuan_per_kg')})"
        for _, row in best_value.iterrows()
    ]))