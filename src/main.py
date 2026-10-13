from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 定位项目根目录：py-project01/
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
CSV_PATH = DATA_DIR / "blueberry_prices.csv"

# 1. 读取真实的蓝莓行情数据
# 注意：如果你的CSV是由Excel保存的，可能需要指定 encoding='utf-8-sig'
try:
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
except UnicodeDecodeError:
    # 如果 utf-8-sig 报错，尝试用 gbk (Windows Excel 默认编码)
    df = pd.read_csv(CSV_PATH, encoding="gbk")

# 2. 数据清洗
# 将日期列转换为 datetime 类型，方便按时间排序
df["日期"] = pd.to_datetime(df["日期"])
# 按日期排序，避免折线图乱连
df = df.sort_values("日期")

print("成功读取数据，共", len(df), "条记录")
print(df[["日期", "产地", "均价(元/kg)"]].head(10))

# 3. 设置中文字体
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

# ... 前面的读取和清洗代码保持不变 ...

# ==========================================
# 4. 可视化：分为两张图
# ==========================================
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

# 把数据拆分成两部分
# 图 1：全国均价走势（只看产地是“全国”的数据）
national_df = df[df["产地"] == "全国"].sort_values("日期")
# 图 2：各产地价格对比（排除“全国”，只看具体产地）
origin_df = df[df["产地"] != "全国"].sort_values("日期")

# 创建画布，准备画两张图（1行2列）
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# ------------------ 绘制第一张图：全国均价走势 ------------------
sns.lineplot(data=national_df, x="日期", y="均价(元/kg)", marker="o", ax=axes[0], color="#1f77b4")
axes[0].set_title("全国蓝莓批发均价走势", fontsize=14)
axes[0].set_xlabel("日期")
axes[0].set_ylabel("价格 (元/公斤)")
axes[0].tick_params(axis='x', rotation=45)

# ------------------ 绘制第二张图：产地价格对比 ------------------
# 用柱状图对比不同产地的价格，更直观
sns.barplot(data=origin_df, x="产地", y="均价(元/kg)", ax=axes[1], hue="产地", palette="Set2", legend=False)
axes[1].set_title("不同产地蓝莓价格对比（特定日期）", fontsize=14)
axes[1].set_xlabel("产地")
axes[1].set_ylabel("价格 (元/公斤)")

# 在柱状图上标注具体价格数值
for container in axes[1].containers:
    axes[1].bar_label(container, fmt='%.1f', padding=3)

# 调整布局，防止标签重叠
plt.tight_layout()

# 5. 保存图片
png_path = DATA_DIR / "blueberry_market_analysis.png"
plt.savefig(png_path, dpi=150)
print(f"已保存图表: {png_path}")

plt.show()