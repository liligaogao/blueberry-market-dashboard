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

# 关键指标
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
    max_price = filtered_df["均价(元/kg)"].max()
    st.metric(t("max_price"), f"{max_price:.2f}" if pd.notna(max_price) else "N/A")

# 今日洞察
st.markdown(f"### {t('today_insight')}")
if not filtered_df.empty:
    origin_only = filtered_df[filtered_df["产地"] != "全国"]
    if not origin_only.empty:
        max_row = origin_only.loc[origin_only["均价(元/kg)"].idxmax()]
        min_row = origin_only.loc[origin_only["均价(元/kg)"].idxmin()]
        gap = max_row["均价(元/kg)"] - min_row["均价(元/kg)"]
        st.info(
            f"{t('highest')}: **{max_row['产地']}** ({max_row['均价(元/kg)']:.1f} {t('yuan_per_kg')}) | "
            f"{t('lowest')}: **{min_row['产地']}** ({min_row['均价(元/kg)']:.1f} {t('yuan_per_kg')}) | "
            f"{t('price_gap')}: **{gap:.1f} {t('yuan_per_kg')}**"
        )
    national_trend = filtered_df[filtered_df["产地"] == "全国"].sort_values("日期")
    if len(national_trend) >= 2:
        first_p = national_trend.iloc[0]["均价(元/kg)"]
        last_p = national_trend.iloc[-1]["均价(元/kg)"]
        change = (last_p - first_p) / first_p * 100
        direction = t("down") if change < 0 else t("up")
        st.warning(f"{first_p:.1f} → {last_p:.1f} {t('yuan_per_kg')}, {t('cumulative')} {direction} {abs(change):.1f}%")

# ========== 本周数据观察 ==========
st.markdown("### 📌 " + ("本周数据观察" if lang == "zh" else "Weekly Data Snapshot"))

latest_date = filtered_df["日期"].max()
week_start = latest_date - pd.Timedelta(days=7)
week_df = filtered_df[filtered_df["日期"] >= week_start].copy()
week_origin = week_df[week_df["产地"] != "全国"].copy()

if not week_origin.empty:
    lowest = week_origin.loc[week_origin["均价(元/kg)"].idxmin()]
    highest = week_origin.loc[week_origin["均价(元/kg)"].idxmax()]

    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(
            "本周最低报价" if lang == "zh" else "Lowest This Week",
            f"{lowest['均价(元/kg)']:.1f} {t('yuan_per_kg')}",
            f"{lowest['产地']} · {lowest['品种规格']}"
        )
    with col_b:
        st.metric(
            "本周最高报价" if lang == "zh" else "Highest This Week",
            f"{highest['均价(元/kg)']:.1f} {t('yuan_per_kg')}",
            f"{highest['产地']} · {highest['品种规格']}"
        )

    price_range = week_origin["均价(元/kg)"].max() - week_origin["均价(元/kg)"].min()
    origins_count = week_origin["产地"].nunique()

    if lang == "zh":
        st.markdown(
            f"- 📅 本周（{week_start.strftime('%m-%d')} 至 {latest_date.strftime('%m-%d')}）"
            f"共收录 **{len(week_df)}** 条数据\n"
            f"- 📍 覆盖 **{origins_count}** 个产地/渠道\n"
            f"- 📊 本周产地价格区间跨度：**{price_range:.1f} {t('yuan_per_kg')}**"
        )
        st.caption("💡 以上数据仅为客观统计，不构成任何采购或投资建议。")
    else:
        st.markdown(
            f"- 📅 This week ({week_start.strftime('%m-%d')} to {latest_date.strftime('%m-%d')}): "
            f"**{len(week_df)}** records\n"
            f"- 📍 Covers **{origins_count}** origins/channels\n"
            f"- 📊 Price range this week: **{price_range:.1f} {t('yuan_per_kg')}**"
        )
        st.caption("💡 The above data is for reference only and does not constitute any purchasing or investment advice.")
else:
    st.info("本周暂无产地报价数据。" if lang == "zh" else "No origin price data this week.")

# 全国均价走势
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
    fig.update_layout(hovermode="x unified", xaxis_title="Date" if lang == "en" else "日期", yaxis_title="Price (yuan/kg)" if lang == "en" else "价格 (元/公斤)", height=500)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(t("no_data"))