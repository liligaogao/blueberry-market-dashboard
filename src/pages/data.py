import streamlit as st
import pandas as pd
import io

st.title("📥 数据下载")

filtered_df = st.session_state.get("filtered_df")

if filtered_df is None or filtered_df.empty:
    st.warning("当前筛选条件下暂无数据。")
    st.stop()

# ========== 页面内独立筛选器 ==========
st.markdown("### 🔍 二次筛选（仅影响本页下载）")

col1, col2 = st.columns(2)
with col1:
    all_origins = sorted(filtered_df["产地"].dropna().unique().tolist())
    selected_origins = st.multiselect(
        "选择产地（可多选）", options=all_origins, default=all_origins,
        key="download_origin_filter",
    )
with col2:
    keyword = st.text_input(
        "关键词搜索（产地或品种规格）", value="",
        placeholder="例如：云南、18mm、盒马",
        key="download_keyword",
    )

date_col1, date_col2 = st.columns(2)
min_date = filtered_df["日期"].min().date()
max_date = filtered_df["日期"].max().date()
with date_col1:
    start_date = st.date_input("开始日期", value=min_date, min_value=min_date, max_value=max_date, key="download_start_date")
with date_col2:
    end_date = st.date_input("结束日期", value=max_date, min_value=min_date, max_value=max_date, key="download_end_date")

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

st.markdown(f"### 📊 筛选结果：共 **{len(download_df)}** 条数据")

if download_df.empty:
    st.warning("当前二次筛选条件下暂无数据，请调整筛选条件。")
    st.stop()

# ========== 处理数据 ==========
preview_df = download_df.copy()
preview_df["日期"] = preview_df["日期"].dt.strftime("%Y-%m-%d")
preview_df = preview_df.fillna("")
# 在最前面加一个"选择"列，默认全部不勾选
preview_df.insert(0, "选择", False)

# ========== 用 st.data_editor 实现逐行勾选 ==========
st.markdown("### ✅ 勾选你想导出的数据行")
st.caption("点击最左侧的复选框来选择要导出的行。不勾选任何行时，默认导出全部。")

edited_df = st.data_editor(
    preview_df,
    use_container_width=True,
    height=500,
    hide_index=True,
    column_config={
        "选择": st.column_config.CheckboxColumn(
            "选择",
            help="勾选要导出的行",
            default=False,
            width="small",
        ),
    },
    disabled=[col for col in preview_df.columns if col != "选择"],  # 除"选择"外其他列不可编辑
    key="data_editor_unique",
)

# ========== 根据勾选状态决定导出的数据 ==========
selected_rows = edited_df[edited_df["选择"] == True].drop(columns=["选择"])

if len(selected_rows) > 0:
    export_df = selected_rows
    st.success(f"✅ 已勾选 **{len(export_df)}** 条数据，将导出勾选的部分。")
else:
    export_df = edited_df.drop(columns=["选择"])
    st.info(f"ℹ️ 未勾选任何行，将导出全部 **{len(export_df)}** 条数据。")

# ========== 下载按钮1：CSV ==========
csv_data = export_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(
    label=f"📥 下载 (CSV，{len(export_df)} 条)",
    data=csv_data,
    file_name="blueberry_filtered.csv",
    mime="text/csv",
    key="data_page_dl_csv_unique"
)

# ========== 下载按钮2：Excel ==========
st.markdown("### 📊 导出为 Excel")
if st.button("生成 Excel 报表", key="data_page_gen_excel_btn"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        export_df.to_excel(writer, sheet_name="蓝莓行情", index=False)
    buffer.seek(0)
    st.download_button(
        label=f"📥 下载 Excel（{len(export_df)} 条）",
        data=buffer,
        file_name=f"蓝莓行情_{pd.Timestamp.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="data_page_dl_excel_unique"
    )