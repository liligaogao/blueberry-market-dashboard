import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data(ttl=60)
def load_data():
    BASE_DIR = Path(__file__).resolve().parent.parent
    csv_path = BASE_DIR / "data" / "processed" / "blueberry_prices_clean.csv"
    if not csv_path.exists():
        return pd.DataFrame()
    df = pd.read_csv(csv_path, encoding="utf-8-sig", parse_dates=["日期"])
    return df

def sidebar_filter(df):
    st.sidebar.header("🔍 数据筛选")

    # 1. 渠道类型筛选
    if "渠道类型" in df.columns:
        all_channels = sorted(df["渠道类型"].dropna().unique().tolist())
        selected_channels = st.sidebar.multiselect(
            "渠道类型", options=all_channels, default=all_channels,
            key="channel_filter"
        )
    else:
        selected_channels = None

    # 2. 产地筛选
    all_origins = df["产地"].unique().tolist()
    selected_origins = st.sidebar.multiselect(
        "选择产地", options=all_origins, default=all_origins,
        key="origin_filter"
    )

    # 3. 日期范围
    min_date = df["日期"].min().date()
    max_date = df["日期"].max().date()
    date_range = st.sidebar.date_input(
        "选择日期范围",
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

    filtered_df = df[mask].copy()
    return filtered_df