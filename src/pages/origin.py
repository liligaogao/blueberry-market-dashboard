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

# ========== 新增：地理维度切换 ==========
st.markdown("### 🔍 切换查看维度")
geo_dim = st.radio(
    "选择你想查看的地理颗粒度：",
    options=["具体产地（区县/市场）", "城市级", "省份级"],
    horizontal=True,
    label_visibility="collapsed"
)

if geo_dim == "省份级":
    group_col = "省份"
elif geo_dim == "城市级":
    group_col = "城市"
else:
    # 在具体产地维度下，如果包含具体的区县/市场，就用“城市+区县”拼接，否则用原产地
    origin_df["短产地"] = origin_df.apply(
        lambda row: f"{row['城市']}{row['区县/市场']}" if row['区县/市场'] != row['城市'] else row['产地'],
        axis=1
    )
    group_col = "短产地"

# 动态汇总数据
origin_summary = origin_df.groupby(group_col).agg(
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
origin_summary = origin_summary.rename(columns={group_col: "地区名称"})


def reference_level(n):
    if n == 1:
        return t("single_point")
    elif n <= 3:
        return t("normal")
    else:
        return t("high")


origin_summary["参考性"] = origin_summary["样本数"].apply(reference_level)
origin_summary = origin_summary.sort_values("均价", ascending=True)

# ========== 图1：平均价格对比 ==========
st.subheader(f"{t('origin_avg_title')} - {geo_dim}")
st.caption(t("origin_avg_note"))

origin_summary["颜色深度"] = origin_summary["样本数"].apply(lambda n: 1.0 if n >= 2 else 0.35)

fig1 = px.bar(
    origin_summary, x="均价", y="地区名称", orientation="h",
    text="均价", color="均价",
    color_continuous_scale="Purples",
    labels={"均价": t("avg_price_col"), "地区名称": ""},
    hover_data={"样本数": True, "最高价": ":.1f", "最低价": ":.1f", "数据日期范围": True}
)
fig1.update_traces(
    texttemplate='%{text:.1f}', textposition='outside',
    textfont=dict(size=13, color="#1A1A1A"),
    marker=dict(opacity=origin_summary["颜色深度"].tolist(), line=dict(width=0))
)
fig1.update_layout(
    showlegend=False, coloraxis_showscale=False, height=max(400, len(origin_summary) * 30),
    font=dict(size=13, color="#1A1A1A"),
    margin=dict(l=150, r=50, t=30, b=50)
)
st.plotly_chart(fig1, use_container_width=True)

# ========== 图2：明细表 ==========
st.subheader(t("origin_detail_title"))
st.dataframe(
    origin_summary[["地区名称", "均价", "最高价", "最低价", "样本数", "参考性", "数据日期范围"]],
    use_container_width=True,
    hide_index=True,  # <--- 加上这一行
    column_config={
        "地区名称": "地区名称",
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
        f"**{best['地区名称']}** ({best['均价']:.1f} {t('yuan_per_kg')}, n={int(best['样本数'])}) vs "
        f"**{worst['地区名称']}** ({worst['均价']:.1f} {t('yuan_per_kg')}) | "
        f"{t('price_gap')}: **{gap:.1f} {t('yuan_per_kg')}**"
    )

st.markdown("---")

# ========== 互动 1：进货成本模拟器（适配地理维度） ==========
st.markdown("### 🛒 进货成本模拟器")
st.caption("请先选择年份和地区，再拖动滑块测算预估成本。")

col_year, col_origin, col_weight = st.columns(3)

with col_year:
    available_years = sorted(filtered_df["日期"].dt.year.unique().tolist(), reverse=True)
    selected_year = st.selectbox("选择年份", available_years)

year_df = filtered_df[filtered_df["日期"].dt.year == selected_year].copy()
year_origin_df = year_df[year_df["产地"] != "全国"].copy()

if not year_origin_df.empty:
    # 根据当前选中的维度计算均价
    year_summary = year_origin_df.groupby(group_col).agg(
        均价=("均价(元/kg)", "mean")
    ).reset_index().sort_values("均价", ascending=True)
    year_summary = year_summary.rename(columns={group_col: "地区名称"})

    with col_origin:
        year_origins = sorted(year_summary["地区名称"].unique().tolist())
        selected_origin = st.selectbox("选择意向地区", year_origins)

    with col_weight:
        weight = st.number_input("输入进货重量 (公斤)", min_value=10, max_value=10000, value=100, step=50)

    if selected_origin and weight:
        target_row = year_summary[year_summary["地区名称"] == selected_origin]
        if not target_row.empty:
            avg_price = target_row.iloc[0]["均价"]
            total_cost = avg_price * weight

            st.info(
                f"📊 **测算结果（{selected_year}年，{geo_dim}）**：**{selected_origin}** 的均价约为 **{avg_price:.2f} 元/公斤**。\n\n"
                f"进货 **{weight} 公斤**，预计总成本为：**{total_cost:,.2f} 元**。")

            cheapest = year_summary.iloc[0]
            if cheapest["地区名称"] != selected_origin:
                save_cost = (avg_price - cheapest["均价"]) * weight
                st.success(
                    f"💡 **采购建议**：如果您选择当年均价最低的 **{cheapest['地区名称']}**（{cheapest['均价']:.2f} 元/公斤），"
                    f"同样的重量可以省下 **{save_cost:,.2f} 元**！")
else:
    st.warning(f"⚠️ {selected_year} 年暂无产地报价数据，请换一个年份。")

st.markdown("---")

# ========== 互动 2：自定义画图器 ==========
with st.expander("🛠️ 进阶探索：自定义图表生成器"):
    st.markdown("自己动手，探索数据中隐藏的关联关系。")

    col_x, col_y, col_c = st.columns(3)
    with col_x:
        x_axis = st.selectbox("X轴（横轴）", ["日期", "月份", "省份", "城市", "产地", "果径(mm)"])
    with col_y:
        y_axis = st.selectbox("Y轴（纵轴）", ["均价(元/kg)", "最高价(元/kg)", "最低价(元/kg)"])
    with col_c:
        color_by = st.selectbox("颜色分类", ["产地", "城市", "省份", "渠道类型", "等级", None])

    fig_custom = px.scatter(
        filtered_df, x=x_axis, y=y_axis, color=color_by,
        hover_data=["产地", "品种规格", "备注"],
        height=500,
        labels={"均价(元/kg)": "价格 (元/公斤)"}
    )
    fig_custom.update_layout(font=dict(color="#1A1A1A", size=13))
    st.plotly_chart(fig_custom, use_container_width=True)