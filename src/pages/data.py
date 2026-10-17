import streamlit as st
import pandas as pd
import io
from utils import t

st.title(t("data_title"))

filtered_df = st.session_state.get("filtered_df")
if filtered_df is None or filtered_df.empty:
    st.warning(t("no_data"))
    st.stop()

st.markdown(t("data_count_msg").format(n=len(filtered_df)))

# ========== 数据字典 (新增) ==========
with st.expander("📖 查看数据字典（字段说明）" if t("data_title") == "📥 数据下载" else "📖 Data Dictionary"):
    st.markdown("""
    | 字段名 | 含义 | 单位/格式 | 数据来源 |
    |---|---|---|---|
    | **日期** | 报价发布日期 | YYYY-MM-DD | 原始数据 |
    | **产地** | 生产地或批发市场 | - | 原始数据 |
    | **品种规格** | 具体品种及果径描述 | - | 原始数据 |
    | **最高价 / 最低价 / 均价** | 价格区间及平均值 | 元/公斤 | 原始数据 |
    | **交易量** | 市场成交量 | 吨 (暂无数据) | 原始数据 |
    | **备注** | 数据来源或补充说明 | - | 原始数据 |
    | **年份/月份/周次** | 基于日期自动生成的时间维度 | - | 衍生字段 |
    | **渠道类型** | 产地、批发、零售 | - | 衍生字段 |
    | **省份** | 根据产地提取的省份信息 | - | 衍生字段 |
    | **果径(mm)** | 从规格中提取的数字果径 | 毫米 | 衍生字段 |
    | **等级** | 精品、大果、统货等 | - | 衍生字段 |
    """)

# ========== 二次筛选 ==========
st.markdown(f"### {t('second_filter')}")
col1, col2 = st.columns(2)
with col1:
    all_origins = sorted(filtered_df["产地"].dropna().unique().tolist())
    selected_origins = st.multiselect(t("origin"), options=all_origins, default=all_origins,
                                      key="download_origin_filter")
with col2:
    keyword = st.text_input(t("keyword_search"), value="", placeholder=t("keyword_placeholder"), key="download_keyword")

date_col1, date_col2 = st.columns(2)
min_date = filtered_df["日期"].min().date()
max_date = filtered_df["日期"].max().date()
with date_col1:
    start_date = st.date_input(t("start_date"), value=min_date, min_value=min_date, max_value=max_date,
                               key="download_start_date")
with date_col2:
    end_date = st.date_input(t("end_date"), value=max_date, min_value=min_date, max_value=max_date,
                             key="download_end_date")

download_df = filtered_df[
    (filtered_df["产地"].isin(selected_origins)) &
    (filtered_df["日期"].dt.date >= start_date) &
    (filtered_df["日期"].dt.date <= end_date)
    ].copy()

if keyword:
    mask = (
            download_df["产地"].astype(str).str.contains(keyword, case=False, na=False) |
            download_df["品种规格"].astype(str).str.contains(keyword, case=False, na=False)
    )
    download_df = download_df[mask]

st.markdown(f"### {t('filter_result').format(n=len(download_df))}")
if download_df.empty:
    st.warning(t("second_no_data"))
    st.stop()

# 处理数据
preview_df = download_df.copy()
preview_df["日期"] = preview_df["日期"].dt.strftime("%Y-%m-%d")
preview_df = preview_df.fillna("")
preview_df.insert(0, t("select_col"), False)

# 行选择
st.markdown(f"### {t('select_rows')}")
edited_df = st.data_editor(
    preview_df, use_container_width=True, height=400, hide_index=True,
    column_config={t("select_col"): st.column_config.CheckboxColumn(t("select_col"), default=False, width="small")},
    disabled=[col for col in preview_df.columns if col != t("select_col")],
    key="data_editor_unique",
)

selected_rows = edited_df[edited_df[t("select_col")] == True].drop(columns=[t("select_col")])
export_df = selected_rows if len(selected_rows) > 0 else edited_df.drop(columns=[t("select_col")])

# 提示
if len(selected_rows) > 0:
    st.success(t("selected_msg").format(n=len(export_df)))
else:
    st.info(t("not_selected_msg").format(n=len(export_df)))

# ========== 导出 CSV ==========
csv_data = export_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(
    label=t("download_csv").format(n=len(export_df)),
    data=csv_data,
    file_name="blueberry_filtered.csv",
    mime="text/csv",
    key="data_page_dl_csv_unique"
)

# ========== 导出带图表的 Excel ==========
st.markdown(f"### {t('export_excel')}")
if st.button(t("generate_excel"), key="data_page_gen_excel_btn"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        export_df.to_excel(writer, sheet_name="蓝莓行情", index=False)

        workbook = writer.book
        worksheet = writer.sheets["蓝莓行情"]

        # 格式化表格
        header_format = workbook.add_format({'bold': True, 'bg_color': '#DCE6F1', 'border': 1})
        for col_num, value in enumerate(export_df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # 插入内嵌折线图（基于导出的数据）
        chart = workbook.add_chart({'type': 'line'})
        # 假设我们要画前 30 行的数据图表，防止数据太长
        max_rows = min(len(export_df) + 1, 30)

        # 尝试找到“日期”和“均价”的列索引
        try:
            date_col = export_df.columns.get_loc("日期")
            price_col = export_df.columns.get_loc("均价(元/kg)")
            chart.add_series({
                'categories': ['蓝莓行情', 1, date_col, max_rows - 1, date_col],
                'values': ['蓝莓行情', 1, price_col, max_rows - 1, price_col],
                'name': '价格走势',
            })
            chart.set_title({'name': '近期价格走势'})
            chart.set_x_axis({'name': '日期'})
            chart.set_y_axis({'name': '价格 (元/公斤)'})
            worksheet.insert_chart('K2', chart, {'x_scale': 1.5, 'y_scale': 1.5})
        except:
            pass  # 如果找不到列名，就不画图

    buffer.seek(0)
    st.download_button(
        label=t("download_excel").format(n=len(export_df)),
        data=buffer,
        file_name=f"blueberry_{pd.Timestamp.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="data_page_dl_excel_unique"
    )