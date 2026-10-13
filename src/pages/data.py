import streamlit as st

st.title("📥 数据下载")

filtered_df = st.session_state.get("filtered_df")

if filtered_df is None or filtered_df.empty:
    st.warning("当前筛选条件下暂无数据。")
    st.stop()

st.markdown(f"当前筛选后共有 **{len(filtered_df)} 条数据**，可下载为 CSV 文件。")

# 下载按钮
csv_data = filtered_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(
    label="📥 下载当前筛选数据 (CSV)",
    data=csv_data,
    file_name="blueberry_filtered.csv",
    mime="text/csv"
)

# 数据预览
st.markdown("### 📋 数据预览")
preview_df = filtered_df.copy()
preview_df["日期"] = preview_df["日期"].dt.strftime("%Y-%m-%d")  # 去掉 00:00:00
preview_df = preview_df.fillna("")  # 将 None 替换为空字符串，表格更美观
st.dataframe(preview_df, use_container_width=True, height=500)