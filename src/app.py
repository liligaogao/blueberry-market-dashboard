import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from utils import load_data, sidebar_filter, t, get_lang

# 页面配置（必须是第一个 Streamlit 命令）
st.set_page_config(page_title="蓝莓市场行情看板", layout="wide", page_icon="🫐")

# 全局图表主题配置（统一风格）
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = ["#4B8B3B", "#1f77b4", "#ff7f0e", "#d62728"]

# ========== 全局字体与移动端适配 CSS ==========
# 注意：<style> 必须顶格写，前面不能有空格，否则会被当成代码块显示出来
st.markdown("""
<style>
/* 1. 强制加粗全局的常规文本和列表 */
.stMarkdown p, .stMarkdown li {
    font-size: 1.05rem !important; 
    font-weight: 500 !important;   
    color: #1A1A1A !important;     
}

/* 2. 放大并加粗所有标题 (H1, H2, H3, H4) */
h1, h2, h3, h4 {
    color: #1A1A1A !important;
    font-weight: 700 !important;
}

/* 3. 让指标卡（数字）更大、标签更清晰 */
[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #1A1A1A !important;
}
[data-testid="stMetricLabel"] {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #333333 !important;
}

/* 4. 针对手机屏幕 (宽度小于 768px) 的样式 */
@media (max-width: 768px) {
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.5rem !important; }
    h3 { font-size: 1.2rem !important; }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

st_autorefresh(interval=60 * 1000, key="data_refresh")

# ========== 语言切换器 ==========
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

# ========== 多页面导航 ==========
pages = [
    st.Page("pages/home.py", title=t("nav_home"), icon="📊", default=True),
    st.Page("pages/origin.py", title=t("nav_origin"), icon="📍"),
    st.Page("pages/retail.py", title=t("nav_retail"), icon="🛒"),
    st.Page("pages/industry.py", title=t("nav_industry"), icon="🏢"),
    st.Page("pages/data.py", title=t("nav_data"), icon="📥"),
    st.Page("pages/about.py", title="关于项目 / About", icon="ℹ️"),
]

pg = st.navigation(pages)
pg.run()

# ========== 页脚 ==========
st.sidebar.markdown("---")
st.sidebar.caption(f"📅 {t('last_update')}: **{df['日期'].max().strftime('%Y-%m-%d')}**")
st.sidebar.caption(t("disclaimer"))