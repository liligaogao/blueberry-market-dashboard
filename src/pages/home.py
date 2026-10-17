# ========== 全国均价走势 (带对比模式) ==========
st.markdown("#### " + ("📈 全国批发均价走势" if lang == "zh" else "📈 National Wholesale Price Trend"))

national_trend = filtered_df[filtered_df["产地"] == "全国"].sort_values("日期")
if not national_trend.empty:
    compare_mode = st.toggle("开启年份对比模式" if lang == "zh" else "Enable Yearly Comparison", value=False)

    if compare_mode:
        # 对比模式：按“月份”对齐，而不是按天
        national_trend["年份"] = national_trend["日期"].dt.year
        national_trend["月份"] = national_trend["日期"].dt.month

        fig = px.line(
            national_trend, x="月份", y="均价(元/kg)", color="年份", markers=True,
            labels={"月份": "月份", "均价(元/kg)": "价格 (元/公斤)", "年份": "年份"}
        )
        fig.update_layout(
            hovermode="x unified", height=500,
            xaxis=dict(tickmode='linear', tick0=1, dtick=1)  # 强制显示1-12月
        )
        fig.update_traces(textposition="top center", textfont=dict(size=11))
    else:
        # 普通模式：散点 + 极细虚线连接，弱化“强行连线”的违和感
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=national_trend["日期"], y=national_trend["均价(元/kg)"],
            mode='lines+markers+text',
            line=dict(color='#4B8B3B', width=2, dash='dot'),  # 虚线，弱化趋势
            marker=dict(size=10, color='#4B8B3B', line=dict(width=2, color='white')),
            text=national_trend["均价(元/kg)"].apply(lambda x: f"{x:.1f}"),
            textposition="top center", textfont=dict(size=11)
        ))
        fig.update_layout(
            hovermode="x unified", height=500,
            xaxis_title="Date" if lang == "en" else "日期",
            yaxis_title="Price (yuan/kg)" if lang == "en" else "价格 (元/公斤)"
        )

    st.caption("📌 注：2024-2025年为关键节点数据，未包含全部月份。等积累更多连续数据后，趋势将更平滑。")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("暂无全国均价数据。" if lang == "zh" else "No national trend data.")