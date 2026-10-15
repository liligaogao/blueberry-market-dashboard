import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils import load_data, sidebar_filter, t, get_lang

# 页面配置（必须是第一个 Streamlit 命令）
st.set_page_config(page_title="蓝莓市场行情看板", layout="wide", page_icon="🫐")

# 每 60 秒自动刷新
st_autorefresh(interval=60 * 1000, key="data_refresh")

# ========== 语言切换器（放在侧边栏最顶部） ==========
lang_choice = st.sidebar.radio(
    "🌐 Language / 语言",
    options=["中文", "English"],
    index=0 if get_lang() == "zh" else 1,
    key="lang_selector",
)
st.session_state["lang"] = "zh" if lang_choice == "中文" else "en"
st.sidebar.markdown("---")

# ========== 加载数据 ==========
df = load_data()
if df.empty:
    st.error("找不到清洗后的数据文件，请先运行 process_data.py 生成 blueberry_prices_clean.csv")
    st.stop()

# 全局侧边栏筛选
filtered_df = sidebar_filter(df)
st.session_state["df"] = df
st.session_state["filtered_df"] = filtered_df

# ========== 多页面导航（标题按语言切换） ==========
pages = [
    st.Page("pages/home.py",     title=t("nav_home"),     icon="📊", default=True),
    st.Page("pages/origin.py",   title=t("nav_origin"),   icon="📍"),
    st.Page("pages/retail.py",   title=t("nav_retail"),   icon="🛒"),
    st.Page("pages/industry.py", title=t("nav_industry"), icon="🏢"),
    st.Page("pages/data.py",     title=t("nav_data"),     icon="📥"),
]

pg = st.navigation(pages)
pg.run()

# ========== 页脚 ==========
st.sidebar.markdown("---")
st.sidebar.caption(f"📅 {t('last_update')}: **{df['日期'].max().strftime('%Y-%m-%d')}**")
st.sidebar.caption(t("disclaimer"))