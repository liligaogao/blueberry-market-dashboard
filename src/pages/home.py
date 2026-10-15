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

# ============================================================
# 第一层：三个关键指标
# ============================================================
st.markdown(f"#### {t('key_metrics')}")
st.markdown("")  # 空行，留呼吸空间

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

# 分隔线
st.markdown("---")

# ============================================================
# 第二层：近7天洞察
# ============================================================
title_7d = "📌 近7天数据洞察" if lang == "zh" else "📌 Last 7 Days Insights"
st.markdown(f"#### {title_7d}")
st.markdown("")  # 空行

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
            "近7天最低报价" if lang == "zh" else "Lowest (7d)",
            f"{lowest['均价(元/kg)']:.1f} {t('yuan_per_kg')}",
            f"{lowest['产地']} · {lowest['品种规格']}"
        )
    with col_b:
        st.metric(
            "近7天最高报价" if lang == "zh" else "Highest (7d)",
            f"{highest['均价(元/kg)']:.1f} {t('yuan_per_kg')}",
            f"{highest['产地']} · {highest['品种规格']}"
        )

    st.markdown("")  # 空行

    # 底部统计
    price_range = week_origin["均价(元/kg)"].max() - week_origin["均价(元/kg)"].min()
    origins_count = week_origin["产地"].nunique()

    if lang == "zh":
        st.caption(
            f"📅 近7天（{week_start.strftime('%m-%d')} 至 {latest_date.strftime('%m-%d')}）"
            f"共收录 {len(week_df)} 条数据 · 覆盖 {origins_count} 个产地/渠道 · "
            f"价格跨度 {price_range:.1f} 元/公斤"
        )
        st.caption("💡 以上数据仅为客观统计，不构成任何采购或投资建议。")
    else:
        st.caption(
            f"📅 Last 7 days ({week_start.strftime('%m-%d')} to {latest_date.strftime('%m-%d')}): "
            f"{len(week_df)} records · {origins_count} origins · range {price_range:.1f} yuan/kg"
        )
        st.caption("💡 For reference only. Not investment advice.")
else:
    st.info("近7天暂无产地报价数据。" if lang == "zh" else "No origin data in the last 7 days.")

# 分隔线
st.markdown("---")

# ============================================================
# 第三层：全国均价走势
# ============================================================
st.markdown(f"#### {t('national_trend_title')}")
st.markdown("")  # 空行

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
        height=500,
        margin=dict(l=20, r=20, t=30, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(t("no_data"))