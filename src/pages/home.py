import streamlit as st
import plotly.express as px
import pandas as pd
from utils import t, get_lang

st.title(t("home_title"))

filtered_df = st.session_state.get("filtered_df")
if filtered_df is None or filtered_df.empty:
    st.warning(t("no_data"))
    st.stop()

lang = get_lang()

# ========== 关键指标 ==========
st.markdown(f"### {t('key_metrics')}")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(t("data_count"), len(filtered_df))

with col2:
    national_data = filtered_df[
        (filtered_df["产地"] == "全国") &
        (filtered_df["品种规格"].isin(["批发均价", "蓝莓"]))
    ].sort_values("日期")
    if not national_data.empty:
        latest = national_data.iloc[-1]
        st.metric(
            f"{t('latest_price')} ({latest['日期'].strftime('%Y-%m-%d')})",
            f"{latest['均价(元/kg)']:.2f} {t('yuan_per_kg')}"
        )
    else:
        st.metric(t("avg_price_col"), f"{filtered_df['均价(元/kg)'].median():.2f}")

with col3:
    latest_year = filtered_df["日期"].max().year
    this_year_df = filtered_df[filtered_df["日期"].dt.year == latest_year]
    if not this_year_df.empty:
        max_price_this_year = this_year_df["均价(元/kg)"].max()
        label = f"{latest_year}年最高价" if lang == "zh" else f"{latest_year} Max Price"
        st.metric(label, f"{max_price_this_year:.2f}" if pd.notna(max_price_this_year) else "N/A")
    else:
        st.metric(t("max_price"), "N/A")

# ========== 一行洞察文字 ==========
latest_date = filtered_df["日期"].max()
week_start = latest_date - pd.Timedelta(days=7)
week_origin = filtered_df[
    (filtered_df["日期"] >= week_start) & (filtered_df["产地"] != "全国")
]

if not week_origin.empty:
    lowest = week_origin.loc[week_origin["均价(元/kg)"].idxmin()]
    highest = week_origin.loc[week_origin["均价(元/kg)"].idxmax()]

    if lang == "zh":
        st.caption(
            f"📌 近7天：最低 **{lowest['均价(元/kg)']:.1f} 元/公斤**（{lowest['产地']}）"
            f"　·　最高 **{highest['均价(元/kg)']:.1f} 元/公斤**（{highest['产地']}）"
        )
    else:
        st.caption(
            f"📌 Last 7 days: Low **{lowest['均价(元/kg)']:.1f} yuan/kg** ({lowest['产地']})"
            f"　·　High **{highest['均价(元/kg)']:.1f} yuan/kg** ({highest['产地']})"
        )

# ========== 全国均价走势 ==========
st.markdown(f"### {t('national_trend_title')}")
national_trend = filtered_df[filtered_df["产地"] == "全国"].sort_values("日期")
if not national_trend.empty:
    fig = px.line(national_trend, x="日期", y="均价(元/kg)", markers=True)
    fig.update_traces(
        text=national_trend["均价(元/kg)"].apply(lambda x: f"{x:.1f}"),
        textposition="top center",
        textfont=dict(size=12, color="#1f77b4"),
        marker=dict(size=10, line=dict(width=2, color='white')),
        line=dict(width=3, color='#1f77b4')
    )
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="Date" if lang == "en" else "日期",
        yaxis_title="Price (yuan/kg)" if lang == "en" else "价格 (元/公斤)",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(t("no_data"))