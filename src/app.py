import streamlit as st
from streamlit_autorefresh import st_autorefresh
from utils import load_data, sidebar_filter

# 页面配置（必须是第一个 Streamlit 命令）
st.set_page_config(page_title="蓝莓市场行情看板", layout="wide", page_icon="🫐")

# 每 60 秒自动刷新
st_autorefresh(interval=60 * 1000, key="data_refresh")

# ===== 新增：展示蓝莓 Logo =====
# st.image("src/assets/blueberry_logo.png", width=150)

st.title("🫐 蓝莓市场行情动态看板")

# 加载数据
df = load_data()
if df.empty:
    st.error("找不到清洗后的数据文件，请先运行 process_data.py 生成 blueberry_prices_clean.csv")
    st.stop()

# 全局侧边栏筛选（所有页面共享筛选结果）
filtered_df = sidebar_filter(df)

# 把数据存入 session_state，供各子页面读取
st.session_state["df"] = df
st.session_state["filtered_df"] = filtered_df

# 定义多页面导航
pages = [
    st.Page("pages/home.py",   title="首页大盘",  icon="📊", default=True),
    st.Page("pages/origin.py", title="产区分析",  icon="📍"),
    st.Page("pages/retail.py", title="零售市场",  icon="🛒"),
    st.Page("pages/data.py",   title="数据下载",  icon="📥"),
]

pg = st.navigation(pages)
pg.run()

# 页脚（所有页面共享）
st.sidebar.markdown("---")
st.caption("数据来源：农业农村部、北京新发地市场及公开农产品信息平台 | 数据仅供学习交流，不构成投资或商业建议。")