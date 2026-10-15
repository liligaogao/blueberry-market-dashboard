import streamlit as st
import pandas as pd
import io

st.title("📥 数据下载")

filtered_df = st.session_state.get("filtered_df")

if filtered_df is None or filtered_df.empty:
    st.warning("当前筛选条件下暂无数据。")
    st.stop()

st.markdown(f"当前筛选后共有 **{len(filtered_df)} 条数据**，可下载为 CSV 或 Excel 文件。")

# ========== 处理数据，准备展示 ==========
preview_df = filtered_df.copy()
preview_df["日期"] = preview_df["日期"].dt.strftime("%Y-%m-%d")  # 去掉 00:00:00
preview_df = preview_df.fillna("")  # 将 None 替换为空字符串，表格更美观

# ========== 下载按钮一：下载 CSV ==========
csv_data = preview_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(
    label="📥 下载当前筛选数据 (CSV)",
    data=csv_data,
    file_name="blueberry_filtered.csv",
    mime="text/csv",
    key="download_csv"  # <-- 加上独特的 key，避免重复
)

# ========== 下载按钮二：生成并下载 Excel ==========
st.markdown("### 📊 导出为 Excel")
if st.button("生成 Excel 报表", key="generate_excel"):
    buffer = io.BytesIO()
    # 这里直接用 xlsxwriter 导出带数据的 Excel
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        preview_df.to_excel(writer, sheet_name="蓝莓行情", index=False)
    buffer.seek(0)
    st.download_button(
        label="📥 点击下载 Excel",
        data=buffer,
        file_name=f"蓝莓行情_{pd.Timestamp.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_excel"  # <-- 加上独特的 key，避免重复
    )

# ========== 数据预览 ==========
st.markdown("### 📋 数据预览")
st.dataframe(preview_df, use_container_width=True, height=500)