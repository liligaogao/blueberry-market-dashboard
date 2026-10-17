import streamlit as st
from utils import get_lang

lang = get_lang()
st.title("ℹ️ 关于本项目" if lang == "zh" else "ℹ️ About This Project")

if lang == "zh":
    st.markdown("""
    ### 你好，我是 liligaogao 👋

    这是一个我个人从零开始独立开发的**蓝莓市场行情数据看板**。

    #### 🎯 为什么做这个？
    作为数据分析爱好者，我发现国内针对小宗水果（如蓝莓）的公开趋势分析工具极少。大部分数据要么零散，要么需要高昂的会员费。因此，我整合了**农业农村部、北京新发地、一亩田、惠农网**等公开渠道的数据，建成了这个透明的行情看板。

    #### 🛠️ 技术栈
    - **语言**：Python 3
    - **数据处理**：Pandas
    - **可视化**：Plotly (交互式图表)
    - **前端框架**：Streamlit (多页面架构)
    - **部署**：GitHub Actions + Streamlit Cloud

    #### 📝 数据说明
    本看板的数据来源于公开渠道的手动/半自动摘录，**仅供学习交流使用，不构成任何投资建议**。数据持续更新中。

    #### 🔗 开源地址
    欢迎 Star 或提 Issue：[GitHub 仓库](https://github.com/liligaogao/blueberry-market-dashboard)
    """)
else:
    st.markdown("""
    ### Hi, I'm liligaogao 👋

    This is a **Blueberry Market Dashboard** built from scratch entirely by me.

    #### 🎯 Why build this?
    As a data enthusiast, I found a lack of public trend analysis tools for niche fruits like blueberries in China. Data is usually scattered or locked behind paywalls. So, I aggregated data from public sources like the Ministry of Agriculture, Xinfadi Market, Yimutian, and Cnhnb to build this transparent dashboard.

    #### 🛠️ Tech Stack
    - **Language**: Python 3
    - **Data Processing**: Pandas
    - **Visualization**: Plotly
    - **Frontend**: Streamlit
    - **Deployment**: GitHub Actions + Streamlit Cloud

    #### 📝 Data Disclaimer
    The data is manually/automatically compiled from public sources. **For learning purposes only, not investment advice.** Data is continuously updated.

    #### 🔗 Open Source
    Feel free to star or submit an issue: [GitHub Repository](https://github.com/liligaogao/blueberry-market-dashboard)
    """)