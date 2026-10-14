import streamlit as st
import plotly.express as px
import pandas as pd

st.title("📊 首页大盘概览")

filtered_df = st.session_state.get("filtered_df")
if filtered_df is None or filtered_df.empty:
    st.warning("当前筛选条件下暂无数据。")
    st.stop()

# ========== 关键指标 ==========
st.markdown("### 📈 关键指标")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("数据条数", len(filtered_df))
with col2:
    national_data = filtered_df[filtered_df["产地"] == "全国"].sort_values("日期")
    if not national_data.empty:
        latest_national = national_data.iloc[-1]
        latest_date_str = latest_national["日期"].strftime("%Y-%m-%d")
        latest_price = latest_national["均价(元/kg)"]
        st.metric(f"最新全国均价 ({latest_date_str})", f"{latest_price:.2f} 元/kg")
    else:
        median_price = filtered_df["均价(元/kg)"].median()
        st.metric("价格中位数 (元/kg)", f"{median_price:.2f}")
with col3:
    max_price = filtered_df["均价(元/kg)"].max()
    st.metric("最高价格 (元/kg)", f"{max_price:.2f}" if pd.notna(max_price) else "N/A")

# ========== 自动洞察 ==========
st.markdown("### 🧠 今日洞察")
if not filtered_df.empty:
    origin_only = filtered_df[filtered_df["产地"] != "全国"]
    if not origin_only.empty:
        max_origin_row = origin_only.loc[origin_only["均价(元/kg)"].idxmax()]
        min_origin_row = origin_only.loc[origin_only["均价(元/kg)"].idxmin()]
        gap = max_origin_row["均价(元/kg)"] - min_origin_row["均价(元/kg)"]
        st.info(
            f"当前范围内，**{max_origin_row['产地']}** 均价最高（**{max_origin_row['均价(元/kg)']:.1f} 元/公斤**），"
            f"**{min_origin_row['产地']}** 最低（**{min_origin_row['均价(元/kg)']:.1f} 元/公斤**），"
            f"价差 **{gap:.1f} 元/公斤**。"
        )
    national_trend = filtered_df[filtered_df["产地"] == "全国"].sort_values("日期")
    if len(national_trend) >= 2:
        first_p = national_trend.iloc[0]["均价(元/kg)"]
        last_p = national_trend.iloc[-1]["均价(元/kg)"]
        change = (last_p - first_p) / first_p * 100
        direction = "下跌" if change < 0 else "上涨"
        st.warning(f"全国均价从 {first_p:.1f} 变化到 {last_p:.1f} 元/公斤，累计**{direction} {abs(change):.1f}%**。")

# ========== 全国均价走势 ==========
st.markdown("### 📈 全国批发均价走势")
national_trend = filtered_df[filtered_df["产地"] == "全国"].sort_values("日期")
if not national_trend.empty:
    # 画折线图+散点，看走势
    fig = px.line(
        national_trend, x="日期", y="均价(元/kg)",
        markers=True,  # 关键：加点
        labels={"均价(元/kg)": "价格 (元/公斤)"}
    )
    # 给每个点加上数值标签
    fig.update_traces(
        text=national_trend["均价(元/kg)"].apply(lambda x: f"{x:.1f}"),
        textposition="top center",
        textfont=dict(size=12, color="#1f77b4"),
        marker=dict(size=10, line=dict(width=2, color='white')),
        line=dict(width=3, color='#1f77b4')
    )
    fig.update_layout(
        hovermode="x unified",
        xaxis_title="日期",
        yaxis_title="价格 (元/公斤)",
        height=500,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 贴心提示，解释断档
    st.caption("📌 **提示**：5月至7月为国产蓝莓断档期，主要由进口蓝莓主导市场，故曲线在此处出现跳跃。")
else:
    st.info("暂无全国批发均价数据。")