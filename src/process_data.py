# import pandas as pd
# from pathlib import Path
#
# BASE_DIR = Path(__file__).resolve().parent.parent
# DATA_DIR = BASE_DIR / "data" / "processed"
# RAW_CSV_PATH = DATA_DIR / "blueberry_prices.csv"
# CLEAN_CSV_PATH = DATA_DIR / "blueberry_prices_clean.csv"
#
#
# def clean_blueberry_data():
#     """读取乱格式的 CSV，清洗并输出为统一格式"""
#     print("开始清洗数据...")
#
#     # 1. 智能读取文件（解决 Excel 默认保存为 GBK 编码的问题）
#     try:
#         with open(RAW_CSV_PATH, "r", encoding="utf-8-sig") as f:
#             lines = f.readlines()
#     except UnicodeDecodeError:
#         with open(RAW_CSV_PATH, "r", encoding="gb18030") as f:
#             lines = f.readlines()
#
#     # 2. 找到所有以"日期"开头的行（表头），并记录它们的行号
#     header_lines = [i for i, line in enumerate(lines) if line.strip().startswith("日期")]
#
#     all_dfs = []
#
#     # 3. 逐段提取数据
#     for idx, start_line in enumerate(header_lines):
#         # 确定当前数据段的结束行（下一段表头前，或文件末尾）
#         end_line = header_lines[idx + 1] - 1 if idx + 1 < len(header_lines) else len(lines)
#
#         # 提取当前段的数据行
#         chunk_lines = lines[start_line + 1: end_line]
#         chunk_lines = [line.strip() for line in chunk_lines if line.strip()]
#
#         if not chunk_lines:
#             continue
#
#         # 根据表头内容，构建 DataFrame
#         header = lines[start_line].strip().split(",")
#         # 过滤掉因为末尾逗号导致的空列名
#         header = [h.strip() for h in header if h.strip()]
#
#         data = []
#         for line in chunk_lines:
#             # 按照逗号分割，并去除首尾空格
#             row = [item.strip() for item in line.split(",")]
#             # 确保行长度与表头长度一致（多退少补）
#             if len(row) > len(header):
#                 row = row[:len(header)]
#             elif len(row) < len(header):
#                 row.extend([None] * (len(header) - len(row)))
#             data.append(row)
#
#         df_chunk = pd.DataFrame(data, columns=header)
#         all_dfs.append(df_chunk)
#
#     # 4. 统一列名和格式
#     cleaned_dfs = []
#     for df in all_dfs:
#         # 修正列名：把"渠道/产地"改为"产地"，把"价格(元/公斤)"改为"均价(元/kg)"
#         df = df.rename(columns={"渠道/产地": "产地", "价格(元/公斤)": "均价(元/kg)"})
#
#         # 补充缺失的列，保证所有列都一致
#         for col in ["最高价(元/kg)", "最低价(元/kg)", "均价(元/kg)", "交易量(吨)", "备注"]:
#             if col not in df.columns:
#                 df[col] = None  # 零售数据没有最高/最低价，就填 None
#
#         cleaned_dfs.append(df)
#
#     # 5. 合并所有数据
#     df_final = pd.concat(cleaned_dfs, ignore_index=True)
#
#     # 6. 数据清洗细节
#     # 转换日期格式（兼容 2026/2/16 和 2026-02-16）
#     df_final["日期"] = pd.to_datetime(df_final["日期"], format="mixed", errors="coerce")
#     # 按照日期排序
#     df_final = df_final.sort_values("日期").reset_index(drop=True)
#     # 填充缺失的产地名称
#     df_final["产地"] = df_final["产地"].fillna("未知")
#     # 确保价格列是数值类型
#     for col in ["最高价(元/kg)", "最低价(元/kg)", "均价(元/kg)"]:
#         df_final[col] = pd.to_numeric(df_final[col], errors="coerce")
#
#     # 7. 保存为干净的 CSV
#     df_final.to_csv(CLEAN_CSV_PATH, index=False, encoding="utf-8-sig")
#     print(f"清洗完成！已保存为 {CLEAN_CSV_PATH}")
#     print(f"共处理 {len(df_final)} 条数据。")
#     print(df_final.head(10))  # 打印前10行看看效果
#     return df_final
#
#
# if __name__ == "__main__":
#     clean_blueberry_data()


# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from pathlib import Path
#
# BASE_DIR = Path(__file__).resolve().parent.parent
# DATA_DIR = BASE_DIR / "data" / "processed"
# CLEAN_CSV_PATH = DATA_DIR / "blueberry_prices_clean.csv"
#
# # 读取清洗后的数据
# df = pd.read_csv(CLEAN_CSV_PATH, encoding="utf-8-sig", parse_dates=["日期"])
#
# plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
# plt.rcParams["axes.unicode_minus"] = False
#
# # 创建画布，准备画两张图
# fig, axes = plt.subplots(1, 2, figsize=(16, 6))
#
# # ------------------ 图1：全国与主产地均价走势 ------------------
# # 筛选出没有零售数据的记录（即全国均价 + 产地价）
# market_df = df[df["备注"].str.contains("周|地头|产地", na=False)]
#
# sns.lineplot(data=market_df, x="日期", y="均价(元/kg)", hue="产地", marker="o", ax=axes[0])
# axes[0].set_title("全国与主产地蓝莓价格走势", fontsize=14)
# axes[0].set_xlabel("日期")
# axes[0].set_ylabel("价格 (元/公斤)")
# axes[0].tick_params(axis='x', rotation=45)
#
# # ------------------ 图2：零售端价格对比（按规格） ------------------
# # 筛选出零售端的数据
# retail_df = df[df["备注"].str.contains("折合|降至|降至|跌", na=False)].copy()
# # 简化规格名称，方便显示
# retail_df["规格"] = retail_df["品种规格"].str.replace("云南高山蓝莓 ", "").str.replace(" 超大果", "").str.replace(" Plus款", "").str.replace(" 250g装", "").str.replace(" 500g装", "").str.replace(" 125g装", "")
#
# sns.barplot(data=retail_df, x="规格", y="均价(元/kg)", hue="产地", ax=axes[1], palette="Set2")
# axes[1].set_title("零售端不同规格蓝莓价格对比", fontsize=14)
# axes[1].set_xlabel("规格")
# axes[1].set_ylabel("价格 (元/公斤)")
# axes[1].tick_params(axis='x', rotation=45)
#
# # 在柱状图上标注数值
# for container in axes[1].containers:
#     axes[1].bar_label(container, fmt='%.1f', padding=3)
#
# plt.tight_layout()
# png_path = DATA_DIR / "blueberry_market_analysis_v2.png"
# plt.savefig(png_path, dpi=150)
# print(f"已保存图表: {png_path}")
# plt.show()


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
CLEAN_CSV_PATH = DATA_DIR / "blueberry_prices_clean.csv"

# 读取清洗后的数据
df = pd.read_csv(CLEAN_CSV_PATH, encoding="utf-8-sig", parse_dates=["日期"])

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

# 创建画布，改为 1行3列，展示三张图
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

# ================= 图1：全国批发均价走势 =================
national_df = df[df["产地"] == "全国"].sort_values("日期")
sns.lineplot(data=national_df, x="日期", y="均价(元/kg)", marker="o", ax=axes[0], color="#1f77b4", linewidth=2)
axes[0].set_title("全国蓝莓批发均价走势", fontsize=14)
axes[0].set_xlabel("日期")
axes[0].set_ylabel("价格 (元/公斤)")
axes[0].tick_params(axis='x', rotation=45)
# 数值标注
for i, row in national_df.iterrows():
    axes[0].annotate(f"{row['均价(元/kg)']:.1f}", (row["日期"], row["均价(元/kg)"]),
                     textcoords="offset points", xytext=(0,8), ha='center', fontsize=10)

# ================= 图2：主产地价格对比（仅看同一天的数据） =================
# 筛选 3月29日 的产地数据，用柱状图对比
origin_df = df[(df["日期"] == "2026-03-29") & (df["产地"] != "全国")].copy()
# 合并产地和品种规格作为标签
origin_df["标签"] = origin_df["产地"] + " " + origin_df["品种规格"]
sns.barplot(data=origin_df, x="标签", y="均价(元/kg)", ax=axes[1], hue="产地", palette="Set2", legend=False)
axes[1].set_title("主产区地头/批发价格对比 (2026-03-29)", fontsize=14)
axes[1].set_xlabel("产地及规格")
axes[1].set_ylabel("价格 (元/公斤)")
axes[1].tick_params(axis='x', rotation=45)
# 标注数值
for container in axes[1].containers:
    axes[1].bar_label(container, fmt='%.1f', padding=3)

# ================= 图3：零售端价格对比（按规格排序） =================
# 筛选零售端数据（排除全国、批发均价、云南蓝莓等模糊标签）
retail_df = df[df["产地"].isin(["济南大润发", "盒马鲜生", "上海市场", "北京新发地"])].copy()
# 对规格进行排序，让 14mm, 18mm, 22mm, 24mm 等按顺序排列
retail_df["规格排序"] = retail_df["品种规格"].str.extract(r'(\d+)mm').astype(float)
retail_df = retail_df.sort_values("规格排序")
sns.barplot(data=retail_df, x="品种规格", y="均价(元/kg)", ax=axes[2], hue="产地", palette="Set3")
axes[2].set_title("零售端不同规格蓝莓价格对比", fontsize=14)
axes[2].set_xlabel("规格")
axes[2].set_ylabel("价格 (元/公斤)")
axes[2].tick_params(axis='x', rotation=45)
# 标注数值
for container in axes[2].containers:
    axes[2].bar_label(container, fmt='%.1f', padding=3)

plt.tight_layout()
png_path = DATA_DIR / "blueberry_market_analysis_v3.png"
plt.savefig(png_path, dpi=150)
print(f"已保存三合图表: {png_path}")
plt.show()

# 把清洗后的数据导出为 Excel
excel_path = DATA_DIR / "blueberry_market_report.xlsx"
df.to_excel(excel_path, index=False, sheet_name="蓝莓行情")
print(f"已生成 Excel 报表: {excel_path}")