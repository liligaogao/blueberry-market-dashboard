import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 首页大盘概览")

filtered_df = st.session_state.get("filtered_df")

if filtered_df is None or filtered_df.empty:
    st.warning("当前筛选条件下暂无数据。")
    st.stop()

# ------------------ 核心指标卡片 ------------------
st.markdown("### 📈 关键指标")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("数据条数", len(filtered_df))

with col2:
    # 筛选出“全国”的数据，并按日期排序
    national_data = filtered_df[filtered_df["产地"] == "全国"].sort_values("日期")

    if not national_data.empty:
        # 取最新一天的全国均价
        latest_national = national_data.iloc[-1]
        latest_date_str = latest_national["日期"].strftime("%Y-%m-%d")
        latest_price = latest_national["均价(元/kg)"]
        st.metric(f"最新全国均价 ({latest_date_str})", f"{latest_price:.2f} 元/kg")
    else:
        # 如果没有“全国”数据，才退回到平均值（但改用中位数更抗干扰）
        median_price = filtered_df["均价(元/kg)"].median()
        st.metric("价格中位数 (元/kg)", f"{median_price:.2f}")

with col3:
    max_price = filtered_df["均价(元/kg)"].max()
    # 如果 max_price 不是空值，就显示，否则显示 N/A
    if max_price == max_price:  # NaN 不等于它自己，所以这行相当于判断非空
        st.metric("最高价格 (元/kg)", f"{max_price:.2f}")
    else:
        st.metric("最高价格 (元/kg)", "N/A")

# 自动洞察
st.markdown("### 🧠 今日洞察")
origin_only = filtered_df[filtered_df["产地"] != "全国"]
if not origin_only.empty:
    max_row = origin_only.loc[origin_only["均价(元/kg)"].idxmax()]
    min_row = origin_only.loc[origin_only["均价(元/kg)"].idxmin()]
    gap = max_row["均价(元/kg)"] - min_row["均价(元/kg)"]
    st.info(
        f"当前范围内，**{max_row['产地']}** 均价最高（**{max_row['均价(元/kg)']:.1f} 元/公斤**），"
        f"**{min_row['产地']}** 最低（**{min_row['均价(元/kg)']:.1f} 元/公斤**），"
        f"价差 **{gap:.1f} 元/公斤**。"
    )

national_trend = filtered_df[filtered_df["产地"] == "全国"].sort_values("日期")
if len(national_trend) >= 2:
    first_p = national_trend.iloc[0]["均价(元/kg)"]
    last_p = national_trend.iloc[-1]["均价(元/kg)"]
    change = (last_p - first_p) / first_p * 100
    direction = "下跌" if change < 0 else "上涨"
    st.warning(f"全国均价从 {first_p:.1f} 变化到 {last_p:.1f} 元/公斤，累计**{direction} {abs(change):.1f}%**。")

# 全国均价走势
st.markdown("### 📈 全国批发均价走势")
if not national_trend.empty:
    fig = px.line(
        national_trend, x="日期", y="均价(元/kg)",
        markers=True,
        labels={"均价(元/kg)": "价格 (元/公斤)"}
    )
    fig.update_traces(line_color="#1f77b4", line_width=3, marker_size=10)
    fig.update_layout(hovermode="x unified", xaxis_title="日期", yaxis_title="价格 (元/公斤)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("暂无全国批发均价数据。")