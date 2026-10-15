import pandas as pd
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
RAW_CSV_PATH = DATA_DIR / "blueberry_prices.csv"
CLEAN_CSV_PATH = DATA_DIR / "blueberry_prices_clean.csv"


def classify_channel(row):
    """根据产地和品种规格判断渠道类型：批发 / 产地 / 零售"""
    origin = str(row["产地"])
    spec = str(row["品种规格"])

    # 零售渠道关键词
    retail_keywords = ["大润发", "盒马", "超市", "堤口"]
    for kw in retail_keywords:
        if kw in origin:
            return "零售"

    # 批发渠道关键词
    wholesale_keywords = [
        "全国", "新发地", "上海市场", "江南市场", "海峡市场",
        "河西市场", "东桥市场", "金马正昌", "鼎信", "昆明市场",
        "市场", "进口"
    ]
    for kw in wholesale_keywords:
        if kw in origin:
            return "批发"

    # 其他统一归为产地
    return "产地"


def extract_diameter(spec):
    """从品种规格中提取果径（mm），取范围下限"""
    spec = str(spec)
    # 匹配 "22-24mm" 或 "22mm" 或 "22 mm"
    match = re.search(r'(\d+)\s*[-~]\s*(\d+)\s*mm', spec)
    if match:
        return int(match.group(1))
    match = re.search(r'(\d+)\s*mm', spec)
    if match:
        return int(match.group(1))
    return None


def extract_grade(spec):
    """从品种规格中提取等级"""
    spec = str(spec)
    if "精品" in spec or "品质最优" in spec:
        return "精品"
    if "特大" in spec:
        return "特大果"
    if "大果" in spec or "超大" in spec:
        return "大果"
    if "中果" in spec:
        return "中果"
    if "小果" in spec:
        return "小果"
    if "通货" in spec:
        return "通货"
    if "统货" in spec:
        return "统货"
    if "批发均价" in spec or "均价" in spec:
        return "均价"
    return "未分类"


def clean_blueberry_data():
    """读取原始数据，清洗并输出为统一格式"""
    print("开始清洗数据...")

    # 1. 智能读取文件（解决 Excel 默认保存为 GBK 编码的问题）
    try:
        with open(RAW_CSV_PATH, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(RAW_CSV_PATH, "r", encoding="gb18030") as f:
            lines = f.readlines()

    # 2. 找到所有以"日期"开头的行（表头）
    header_lines = [i for i, line in enumerate(lines) if line.strip().startswith("日期")]
    all_dfs = []

    # 3. 逐段提取数据
    for idx, start_line in enumerate(header_lines):
        end_line = header_lines[idx + 1] - 1 if idx + 1 < len(header_lines) else len(lines)
        chunk_lines = lines[start_line + 1: end_line]
        chunk_lines = [line.strip() for line in chunk_lines if line.strip()]
        if not chunk_lines:
            continue

        header = lines[start_line].strip().split(",")
        header = [h.strip() for h in header if h.strip()]

        data = []
        for line in chunk_lines:
            row = [item.strip() for item in line.split(",")]
            if len(row) > len(header):
                row = row[:len(header)]
            elif len(row) < len(header):
                row.extend([None] * (len(header) - len(row)))
            data.append(row)

        df_chunk = pd.DataFrame(data, columns=header)
        all_dfs.append(df_chunk)

    # 4. 统一列名和格式
    cleaned_dfs = []
    for df in all_dfs:
        df = df.rename(columns={"渠道/产地": "产地", "价格(元/公斤)": "均价(元/kg)"})
        for col in ["最高价(元/kg)", "最低价(元/kg)", "均价(元/kg)", "交易量(吨)", "备注"]:
            if col not in df.columns:
                df[col] = None
        cleaned_dfs.append(df)

    df_final = pd.concat(cleaned_dfs, ignore_index=True)

    # 5. 基础清洗
    df_final["日期"] = pd.to_datetime(df_final["日期"], format="mixed", errors="coerce")
    df_final = df_final.sort_values("日期").reset_index(drop=True)
    df_final["产地"] = df_final["产地"].fillna("未知")
    for col in ["最高价(元/kg)", "最低价(元/kg)", "均价(元/kg)"]:
        df_final[col] = pd.to_numeric(df_final[col], errors="coerce")

    # 6. ========== 新增：衍生字段 ==========
    # 6.1 时间字段
    df_final["年份"] = df_final["日期"].dt.year
    df_final["月份"] = df_final["日期"].dt.month
    df_final["周次"] = df_final["日期"].dt.isocalendar().week

    # 6.2 渠道类型
    df_final["渠道类型"] = df_final.apply(classify_channel, axis=1)

    # 6.3 果径标准化
    df_final["果径(mm)"] = df_final["品种规格"].apply(extract_diameter)

    # 6.4 等级标准化
    df_final["等级"] = df_final["品种规格"].apply(extract_grade)

    # 7. 保存
    df_final.to_csv(CLEAN_CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"✅ 清洗完成！已保存为 {CLEAN_CSV_PATH}")
    print(f"   共处理 {len(df_final)} 条数据。")
    print(f"   新增字段：年份、月份、周次、渠道类型、果径(mm)、等级")
    print(f"   渠道分布：{df_final['渠道类型'].value_counts().to_dict()}")
    print(f"   等级分布：{df_final['等级'].value_counts().to_dict()}")
    return df_final


if __name__ == "__main__":
    clean_blueberry_data()