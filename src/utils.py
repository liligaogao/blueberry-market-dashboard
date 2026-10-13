import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data(ttl=60)
def load_data():
    """加载清洗后的数据"""
    BASE_DIR = Path(__file__).resolve().parent.parent
    csv_path = BASE_DIR / "data" / "processed" / "blueberry_prices_clean.csv"
    if not csv_path.exists():
        return pd.DataFrame()
    df = pd.read_csv(csv_path, encoding="utf-8-sig", parse_dates=["日期"])
    return df

def sidebar_filter(df):
    """在侧边栏构建筛选器，返回筛选后的数据"""
    st.sidebar.header("🔍 数据筛选")

    all_origins = df["产地"].unique().tolist()
    selected_origins = st.sidebar.multiselect(
        "选择产地", options=all_origins, default=all_origins,
        key="origin_filter"
    )

    min_date = df["日期"].min().date()
    max_date = df["日期"].max().date()
    date_range = st.sidebar.date_input(
        "选择日期范围",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date,
        key="date_filter"
    )

    # 防止用户只点了一个日期导致解包失败
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    filtered_df = df[
        (df["产地"].isin(selected_origins)) &
        (df["日期"].dt.date >= start_date) &
        (df["日期"].dt.date <= end_date)
    ].copy()

    return filtered_df