import streamlit as st
import pandas as pd
from pathlib import Path

# ============ 翻译字典 ============
TRANSLATIONS = {
    "zh": {
        "title": "🫐 蓝莓市场行情动态看板",
        "nav_home": "首页大盘",
        "nav_origin": "产区分析",
        "nav_retail": "零售市场",
        "nav_industry": "行业格局",
        "nav_data": "数据下载",
        "filter": "数据筛选",
        "channel": "渠道类型",
        "origin": "选择产地",
        "date_range": "选择日期范围",
        "last_update": "数据最后更新",
        "disclaimer": "数据来源：农业农村部、北京新发地市场及公开农产品信息平台 | 数据仅供学习交流，不构成投资或商业建议。",

        # 首页
        "home_title": "📊 首页大盘概览",
        "key_metrics": "📈 关键指标",
        "data_count": "数据条数",
        "latest_price": "最新全国均价",
        "max_price": "最高价格 (元/kg)",
        "today_insight": "🧠 今日洞察",
        "national_trend_title": "📈 全国批发均价走势",
        "no_data": "当前筛选条件下暂无数据。",
        "highest": "最高",
        "lowest": "最低",
        "price_gap": "价差",
        "yuan_per_kg": "元/公斤",
        "up": "上涨",
        "down": "下跌",
        "cumulative": "累计",

        # 产区分析
        "origin_title": "📍 产区分析",
        "date_range_label": "📅 当前数据时间范围",
        "origin_avg_title": "各产区平均价格对比",
        "origin_avg_note": "⚠️ 均价是选定时间范围内所有数据的算术平均。样本数 n=1 的柱子用浅色绘制，仅代表单点报价，不具有统计意义。",
        "origin_detail_title": "各产区价格与样本量明细",
        "purchase_advice": "💡 采购建议",
        "origin_col": "产地",
        "avg_price_col": "均价 (元/kg)",
        "max_price_col": "最高价 (元/kg)",
        "min_price_col": "最低价 (元/kg)",
        "sample_count": "样本数 (n)",
        "reference": "参考性",
        "date_range_col": "数据日期范围",
        "single_point": "⚠️ 单点报价",
        "normal": "一般",
        "high": "较高",

        # 零售市场
        "retail_title": "🛒 零售市场",
        "diameter_vs_price": "果径大小 vs 零售价格",
        "channel_compare": "各渠道同规格价格对比",
        "value_advice": "💡 性价比建议",
        "spec": "规格",
        "origin_label": "产地",

        # 行业格局
        "industry_title": "🏢 蓝莓行业格局与市场背景",
        "industry_subtitle": "本页面数据整理自公开新闻报道、企业公告及行业平台，仅供学习交流。",
        "market_demand": "📈 市场关注度与供需情况",
        "top_companies": "🏆 国内蓝莓行业头部企业",

        # 数据下载
        "data_title": "📥 数据下载",
        "data_count_msg": "当前筛选后共有 **{n}** 条数据，可下载为 CSV 或 Excel 文件。",
        "second_filter": "🔍 二次筛选（仅影响本页下载）",
        "keyword_search": "关键词搜索（产地或品种规格）",
        "keyword_placeholder": "例如：云南、18mm、盒马",
        "start_date": "开始日期",
        "end_date": "结束日期",
        "filter_result": "📊 筛选结果：共 **{n}** 条数据",
        "second_no_data": "当前二次筛选条件下暂无数据，请调整筛选条件。",
        "select_rows": "✅ 勾选你想导出的数据行",
        "select_rows_note": "点击最左侧的复选框来选择要导出的行。不勾选任何行时，默认导出全部。",
        "selected_msg": "✅ 已勾选 **{n}** 条数据，将导出勾选的部分。",
        "not_selected_msg": "ℹ️ 未勾选任何行，将导出全部 **{n}** 条数据。",
        "download_csv": "📥 下载 (CSV，{n} 条)",
        "export_excel": "📊 导出为 Excel",
        "generate_excel": "生成 Excel 报表",
        "download_excel": "📥 下载 Excel（{n} 条）",
        "data_preview": "📋 数据预览",
        "select_col": "选择",
    },
    "en": {
        "title": "🫐 Blueberry Market Dashboard",
        "nav_home": "Home Overview",
        "nav_origin": "Origin Analysis",
        "nav_retail": "Retail Market",
        "nav_industry": "Industry Landscape",
        "nav_data": "Data Download",
        "filter": "Data Filters",
        "channel": "Channel Type",
        "origin": "Select Origin",
        "date_range": "Select Date Range",
        "last_update": "Last Updated",
        "disclaimer": "Data sources: Ministry of Agriculture, Beijing Xinfadi Market, and public platforms | For learning only, not for investment advice.",

        # Home
        "home_title": "📊 Market Overview",
        "key_metrics": "📈 Key Metrics",
        "data_count": "Data Points",
        "latest_price": "Latest National Avg Price",
        "max_price": "Highest Price (yuan/kg)",
        "today_insight": "🧠 Today's Insights",
        "national_trend_title": "📈 National Wholesale Price Trend",
        "no_data": "No data available under current filters.",
        "highest": "Highest",
        "lowest": "Lowest",
        "price_gap": "Price Gap",
        "yuan_per_kg": "yuan/kg",
        "up": "up",
        "down": "down",
        "cumulative": "cumulative",

        # Origin
        "origin_title": "📍 Origin Analysis",
        "date_range_label": "📅 Data Range",
        "origin_avg_title": "Average Price by Origin",
        "origin_avg_note": "⚠️ Average is the arithmetic mean of all data in the selected period. Bars with n=1 are drawn lighter and represent single-point quotes only.",
        "origin_detail_title": "Price & Sample Details by Origin",
        "purchase_advice": "💡 Purchase Recommendation",
        "origin_col": "Origin",
        "avg_price_col": "Avg Price (yuan/kg)",
        "max_price_col": "Max Price (yuan/kg)",
        "min_price_col": "Min Price (yuan/kg)",
        "sample_count": "Samples (n)",
        "reference": "Reliability",
        "date_range_col": "Data Date Range",
        "single_point": "⚠️ Single point",
        "normal": "Normal",
        "high": "High",

        # Retail
        "retail_title": "🛒 Retail Market",
        "diameter_vs_price": "Berry Size vs Retail Price",
        "channel_compare": "Price Comparison by Channel & Spec",
        "value_advice": "💡 Value Recommendation",
        "spec": "Spec",
        "origin_label": "Channel",

        # Industry
        "industry_title": "🏢 Blueberry Industry Landscape",
        "industry_subtitle": "Data compiled from public news, corporate announcements and industry platforms. For learning only.",
        "market_demand": "📈 Market Demand & Supply",
        "top_companies": "🏆 Leading Companies in China",

        # Data
        "data_title": "📥 Data Download",
        "data_count_msg": "**{n}** rows selected. Download as CSV or Excel.",
        "second_filter": "🔍 Additional Filters (this page only)",
        "keyword_search": "Keyword Search (origin or spec)",
        "keyword_placeholder": "e.g. Yunnan, 18mm, Hema",
        "start_date": "Start Date",
        "end_date": "End Date",
        "filter_result": "📊 Filtered Result: **{n}** rows",
        "second_no_data": "No data under current filters. Please adjust.",
        "select_rows": "✅ Select Rows to Export",
        "select_rows_note": "Check the leftmost box to select rows. If none selected, all rows will be exported.",
        "selected_msg": "✅ **{n}** rows selected. Only these will be exported.",
        "not_selected_msg": "ℹ️ No rows selected. All **{n}** rows will be exported.",
        "download_csv": "📥 Download CSV ({n} rows)",
        "export_excel": "📊 Export to Excel",
        "generate_excel": "Generate Excel Report",
        "download_excel": "📥 Download Excel ({n} rows)",
        "data_preview": "📋 Data Preview",
        "select_col": "Select",
    }
}

def get_lang():
    return st.session_state.get("lang", "zh")

def t(key):
    lang = get_lang()
    return TRANSLATIONS[lang].get(key, key)


@st.cache_data(ttl=60)
def load_data():
    BASE_DIR = Path(__file__).resolve().parent.parent
    csv_path = BASE_DIR / "data" / "processed" / "blueberry_prices_clean.csv"
    if not csv_path.exists():
        return pd.DataFrame()
    df = pd.read_csv(csv_path, encoding="utf-8-sig", parse_dates=["日期"])
    return df


def sidebar_filter(df):
    st.sidebar.header(f"🔍 {t('filter')}")

    if "渠道类型" in df.columns:
        all_channels = sorted(df["渠道类型"].dropna().unique().tolist())
        selected_channels = st.sidebar.multiselect(
            t("channel"), options=all_channels, default=all_channels,
            key="channel_filter"
        )
    else:
        selected_channels = None

    all_origins = df["产地"].unique().tolist()
    selected_origins = st.sidebar.multiselect(
        t("origin"), options=all_origins, default=all_origins,
        key="origin_filter"
    )

    min_date = df["日期"].min().date()
    max_date = df["日期"].max().date()
    date_range = st.sidebar.date_input(
        t("date_range"),
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date,
        key="date_filter"
    )

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    st.session_state["start_date"] = start_date
    st.session_state["end_date"] = end_date

    mask = (df["产地"].isin(selected_origins)) & \
           (df["日期"].dt.date >= start_date) & \
           (df["日期"].dt.date <= end_date)
    if selected_channels is not None:
        mask = mask & (df["渠道类型"].isin(selected_channels))

    return df[mask].copy()