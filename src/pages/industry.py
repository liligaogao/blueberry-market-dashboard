import streamlit as st
from utils import t, get_lang

st.title(t("industry_title"))
st.caption(t("industry_subtitle"))

lang = get_lang()

# ==================== 市场供需 ====================
st.markdown(f"### {t('market_demand')}")

if lang == "zh":
    st.markdown("""
- **线上消费爆发**：2025年3月至2026年3月，抖音电商累计销售蓝莓超 **4200万单**，订单量同比增长 **122%**，成交额突破 **24亿元**，同比增长 **94%**。（来源：[开屏新闻](https://www.ccwb.cn/content/202603/27/c863322.html)）
- **供需仍有缺口**：2025年中国蓝莓产量约 **81万吨**，但国内年需求量超过 **100万吨**，仍存在约 **19万吨** 的供需缺口。（来源：[光明网](https://m.gmw.cn/toutiao/2026-04/16/content_1304420035.htm)）
- **价格波动剧烈**：2026年春季，全国批发均价从2月的28.5元/公斤跌至4月的18.5元/公斤，跌幅超 **35%**。（来源：本看板数据）
""")
else:
    st.markdown("""
- **E-commerce surge**: Mar 2025 – Mar 2026, Douyin sold over **42 million** blueberry orders, +**122%** YoY. GMV exceeded **2.4 billion yuan**, +**94%** YoY. (Source: [Kaiping News](https://www.ccwb.cn/content/202603/27/c863322.html))
- **Supply gap remains**: China's 2025 production ~**810,000 tons**, but demand >**1 million tons** — a gap of ~**190,000 tons**. (Source: [Guangming Online](https://m.gmw.cn/toutiao/2026-04/16/content_1304420035.htm))
- **Volatile prices**: Spring 2026 national avg fell from 28.5 to 18.5 yuan/kg, a drop of over **35%**. (Source: this dashboard)
""")

# ==================== 头部企业 ====================
st.markdown(f"### {t('top_companies')}")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**🥇 Aimeizhuang (Nuopuxin) / 爱莓庄农业集团**")
    if lang == "zh":
        st.markdown("""
        - **地位**：中国蓝莓产量第一（[沙利文2025年认证](http://m.zqrb.cn/gscy/qiyexinxi/2025-09-26/A1758892907623.html)）；全球产量领先（[欧睿国际2026年认证](https://static.nfnews.com/content/202609/04/c12788301.html)）。
        - **规模**：云南50平方公里种植面积，80个生态种植基地。
        - **影响力**：2025/2026产季营收突破 **29亿元**。
        """)
    else:
        st.markdown("""
        - **Ranking**: #1 in China by production (certified by [Frost & Sullivan 2025](http://m.zqrb.cn/gscy/qiyexinxi/2025-09-26/A1758892907623.html)); global leader (certified by [Euromonitor 2026](https://static.nfnews.com/content/202609/04/c12788301.html)).
        - **Scale**: 50 km² planting area in Yunnan, 80 eco-farms.
        - **Revenue**: 2025/26 season exceeded **2.9 billion yuan**.
        """)

    st.markdown("**🥈 Joyvio (Lenovo Holdings) / 佳沃集团**")
    if lang == "zh":
        st.markdown("""
        - **规模**：年产量超 **2万吨**，产值突破 **10亿元**，市场占有率超 **60%**（来源：[百度百科](https://baike.baidu.com/item/%E8%81%94%E6%83%B3%E6%8E%A7%E8%82%A1%E2%80%9C%E4%BD%B3%E6%B2%83%E2%80%9D%E8%93%9D%E8%8E%93)）。
        - **渠道**：并购全国最大水果渠道商鑫荣懋，覆盖300多个城市。
        """)
    else:
        st.markdown("""
        - **Scale**: Annual output >**20,000 tons**, revenue >**1 billion yuan**, market share >**60%** (source: [Baidu Baike](https://baike.baidu.com/item/%E8%81%94%E6%83%B3%E6%8E%A7%E8%82%A1%E2%80%9C%E4%BD%B3%E6%B2%83%E2%80%9D%E8%93%9D%E8%8E%93)).
        - **Channel**: Acquired Joy Wing Mau, China's largest fruit distributor, covering 300+ cities.
        """)

with col2:
    st.markdown("**🥉 Jiangsu Wotian / 江苏沃田集团**")
    if lang == "zh":
        st.markdown("""
        - **地位**：农业产业化 **国家重点龙头企业**，全国蓝莓行业首家获此认定（来源：[同花顺](https://basic.10jqka.com.cn/astockpc/astockmain/index.html#/operate?code=832139&marketid=33)）。
        - **业务**：覆盖种苗繁育、鲜果种植、深加工全产业链，年产能 **1000万株**。
        """)
    else:
        st.markdown("""
        - **Ranking**: National Key Leading Enterprise in Agricultural Industrialization — the first in China's blueberry industry (source: [Tonghuashun](https://basic.10jqka.com.cn/astockpc/astockmain/index.html#/operate?code=832139&marketid=33)).
        - **Business**: Full value chain from seedling breeding to deep processing, annual capacity **10 million seedlings**.
        """)

    st.markdown("**🍇 Ziyue / 紫约农业科技集团**")
    if lang == "zh":
        st.markdown("""
        - **技术**：拥有国家优良品种保护专利 **28个**，投资 **1.5亿元** 建深加工产业园（来源：[全国工商联](https://www.acfic.org.cn/ztzlhz/wqxwc/wqxwc_yxal/202504/t20250429_315111.html)）。
        - **模式**：集新品种研发、种植、精深加工、销售于一体。
        """)
    else:
        st.markdown("""
        - **Technology**: Holds **28** national patents for superior varieties; invested **150 million yuan** in a deep-processing park (source: [ACFIC](https://www.acfic.org.cn/ztzlhz/wqxwc/wqxwc_yxal/202504/t20250429_315111.html)).
        - **Model**: Integrated R&D, planting, deep processing, and sales.
        """)

# ==================== 页脚 ====================
st.markdown("---")
if lang == "zh":
    st.caption("📌 数据来源：证券日报、南方+、百度百科、同花顺、中国农网、全国工商联、光明网、开屏新闻等公开渠道 | 企业排名不分先后。")
else:
    st.caption("📌 Sources: Securities Daily, Nanfang+, Baidu Baike, Tonghuashun, China Rural Network, ACFIC, Guangming Online, Kaiping News, etc. | Companies listed in no particular order.")