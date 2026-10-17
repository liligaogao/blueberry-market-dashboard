import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import t, get_lang

st.title(t("home_title"))

filtered_df = st.session_state.get("filtered_df")
if filtered_df is None or filtered_df.empty:
    st.warning(t("no_data"))
    st.stop()

lang = get_lang()

# ========== 关键指标 ==========
st.markdown(f"#### {t('key_metrics')}")
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

st.markdown("---")

# ========== 近7天数据洞察 ==========
st.markdown("#### " + ("📌 近7天数据洞察" if lang == "zh" else "📌 Last 7 Days Insights"))
latest_date = filtered_df["日期"].max()
week_start = latest_date - pd.Timedelta(days=7)
week_origin = filtered_df[(filtered_df["日期"] >= week_start) & (filtered_df["产地"] != "全国")]

if not week_origin.empty:
    lowest = week_origin.loc[week_origin["均价(元/kg)"].idxmin()]
    highest = week_origin.loc[week_origin["均价(元/kg)"].idxmax()]
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("近7天最低报价" if lang == "zh" else "Lowest (7d)", f"{lowest['均价(元/kg)']:.1f} {t('yuan_per_kg')}",
                  f"{lowest['产地']} · {lowest['品种规格']}")
    with col_b:
        st.metric("近7天最高报价" if lang == "zh" else "Highest (7d)",
                  f"{highest['均价(元/kg)']:.1f} {t('yuan_per_kg')}", f"{highest['产地']} · {highest['品种规格']}")
else:
    st.info("近7天暂无产地报价数据。" if lang == "zh" else "No origin data.")

st.markdown("---")

# ========== 全国均价走势 (带对比模式) ==========
st.markdown("#### " + ("📈 全国批发均价走势" if lang == "zh" else "📈 National Wholesale Price Trend"))

national_trend = filtered_df[filtered_df["产地"] == "全国"].sort_values("日期")
if not national_trend.empty:
    # 增加对比模式开关
    compare_mode = st.toggle("开启年份对比模式" if lang == "zh" else "Enable Yearly Comparison", value=False)

    if compare_mode:
        national_trend["Year"] = national_trend["日期"].dt.year
        national_trend["DayOfYear"] = national_trend["日期"].dt.dayofyear
        fig = px.line(national_trend, x="DayOfYear", y="均价(元/kg)", color="Year", markers=True,
                      labels={"DayOfYear": "一年中的第几天", "均价(元/kg)": "价格 (元/公斤)", "Year": "年份"})
        fig.update_layout(hovermode="x unified", height=500)
    else:
        fig = px.line(national_trend, x="日期", y="均价(元/kg)", markers=True)
        fig.update_traces(
            text=national_trend["均价(元/kg)"].apply(lambda x: f"{x:.1f}"),
            textposition="top center", textfont=dict(size=12), marker=dict(size=10)
        )
        fig.update_layout(hovermode="x unified", height=500)

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("暂无全国均价数据。" if lang == "zh" else "No national trend data.")