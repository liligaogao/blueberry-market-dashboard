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
    }
}

def get_lang():
    """获取当前语言设置，默认中文"""
    return st.session_state.get("lang", "zh")

def t(key):
    """获取翻译文字"""
    lang = get_lang()
    return TRANSLATIONS[lang].get(key, key)


# 下面是你原来就有的 load_data 和 sidebar_filter 函数
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

    # 1. 渠道类型
    if "渠道类型" in df.columns:
        all_channels = sorted(df["渠道类型"].dropna().unique().tolist())
        selected_channels = st.sidebar.multiselect(
            t("channel"), options=all_channels, default=all_channels,
            key="channel_filter"
        )
    else:
        selected_channels = None

    # 2. 产地
    all_origins = df["产地"].unique().tolist()
    selected_origins = st.sidebar.multiselect(
        t("origin"), options=all_origins, default=all_origins,
        key="origin_filter"
    )

    # 3. 日期范围
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

    # 4. 应用筛选
    mask = (df["产地"].isin(selected_origins)) & \
           (df["日期"].dt.date >= start_date) & \
           (df["日期"].dt.date <= end_date)
    if selected_channels is not None:
        mask = mask & (df["渠道类型"].isin(selected_channels))

    return df[mask].copy()