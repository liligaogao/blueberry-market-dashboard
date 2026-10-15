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

# 二次筛选
st.markdown(f"### {t('second_filter')}")
col1, col2 = st.columns(2)
with col1:
    all_origins = sorted(filtered_df["产地"].dropna().unique().tolist())
    selected_origins = st.multiselect(t("origin"), options=all_origins, default=all_origins, key="download_origin_filter")
with col2:
    keyword = st.text_input(t("keyword_search"), value="", placeholder=t("keyword_placeholder"), key="download_keyword")

date_col1, date_col2 = st.columns(2)
min_date = filtered_df["日期"].min().date()
max_date = filtered_df["日期"].max().date()
with date_col1:
    start_date = st.date_input(t("start_date"), value=min_date, min_value=min_date, max_value=max_date, key="download_start_date")
with date_col2:
    end_date = st.date_input(t("end_date"), value=max_date, min_value=min_date, max_value=max_date, key="download_end_date")

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

preview_df = download_df.copy()
preview_df["日期"] = preview_df["日期"].dt.strftime("%Y-%m-%d")
preview_df = preview_df.fillna("")
preview_df.insert(0, t("select_col"), False)

# 行选择
st.markdown(f"### {t('select_rows')}")
st.caption(t("select_rows_note"))

edited_df = st.data_editor(
    preview_df, use_container_width=True, height=500, hide_index=True,
    column_config={
        t("select_col"): st.column_config.CheckboxColumn(t("select_col"), default=False, width="small"),
    },
    disabled=[col for col in preview_df.columns if col != t("select_col")],
    key="data_editor_unique",
)

selected_rows = edited_df[edited_df[t("select_col")] == True].drop(columns=[t("select_col")])
if len(selected_rows) > 0:
    export_df = selected_rows
    st.success(t("selected_msg").format(n=len(export_df)))
else:
    export_df = edited_df.drop(columns=[t("select_col")])
    st.info(t("not_selected_msg").format(n=len(export_df)))

csv_data = export_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(
    label=t("download_csv").format(n=len(export_df)),
    data=csv_data,
    file_name="blueberry_filtered.csv",
    mime="text/csv",
    key="data_page_dl_csv_unique"
)

st.markdown(f"### {t('export_excel')}")
if st.button(t("generate_excel"), key="data_page_gen_excel_btn"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        export_df.to_excel(writer, sheet_name="Blueberry", index=False)
    buffer.seek(0)
    st.download_button(
        label=t("download_excel").format(n=len(export_df)),
        data=buffer,
        file_name=f"blueberry_{pd.Timestamp.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="data_page_dl_excel_unique"
    )