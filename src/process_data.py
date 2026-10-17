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

    retail_keywords = ["大润发", "盒马", "超市", "堤口"]
    for kw in retail_keywords:
        if kw in origin:
            return "零售"

    wholesale_keywords = [
        "全国", "新发地", "上海市场", "江南市场", "海峡市场",
        "河西市场", "东桥市场", "金马正昌", "鼎信", "昆明市场",
        "市场", "进口"
    ]
    for kw in wholesale_keywords:
        if kw in origin:
            return "批发"

    return "产地"


def parse_location(origin):
    """
    精准解析产地为：省份、城市、区县/具体地点
    返回格式：(省份, 城市, 区县)
    """
    origin = str(origin).strip()

    # 特殊处理非具体地名
    if not origin or origin in ["全国", "进口", "全国超市", "市场", "其他", "全国-产地货源", "全国-销地批发"]:
        return "全国/特殊", "全国/特殊", origin

    # 直辖市
    municipalities = ["北京", "上海", "天津", "重庆"]
    for m in municipalities:
        if origin.startswith(m):
            rest = origin[len(m):]
            return m, m, rest if rest else m

    # 普通省份
    provinces = [
        "云南", "山东", "辽宁", "江苏", "四川", "浙江", "福建", "山西",
        "广东", "安徽", "湖南", "湖北", "河南", "河北", "陕西", "贵州",
        "广西", "江西", "黑龙江", "吉林", "海南", "新疆", "内蒙古", "宁夏",
        "青海", "甘肃", "西藏"
    ]

    for p in provinces:
        if origin.startswith(p):
            rest = origin[len(p):]
            if not rest:
                return p, p, p

            # 尝试匹配地级市（以 市/州/盟/地区 结尾）
            match_city = re.match(r'(.{2,4}?[市州盟])', rest)
            if match_city:
                city = match_city.group(1).replace("市", "").replace("州", "").replace("盟", "")
                remaining = rest[len(match_city.group(1)):]
                return p, city, remaining if remaining else match_city.group(1)

            # 尝试匹配县/区/旗
            match_county = re.match(r'(.{2,4}?[区县旗])', rest)
            if match_county:
                # 如果直接是县，说明没有地级市（或者被跳过），城市未知
                return p, "未知市", match_county.group(1)

            # 没有“市/州/县”后缀的，默认取前2个字作为城市，剩下的作为区县
            if len(rest) >= 2:
                return p, rest[:2], rest[2:] if len(rest) > 2 else rest
            else:
                return p, rest, rest

    # 如果都不匹配，兜底处理
    return "其他", "其他", origin


def extract_diameter(spec):
    """从品种规格中提取果径（mm），取范围下限"""
    spec = str(spec)
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

    try:
        with open(RAW_CSV_PATH, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(RAW_CSV_PATH, "r", encoding="gb18030") as f:
            lines = f.readlines()

    header_lines = [i for i, line in enumerate(lines) if line.strip().startswith("日期")]
    all_dfs = []

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

    cleaned_dfs = []
    for df in all_dfs:
        df = df.rename(columns={"渠道/产地": "产地", "价格(元/公斤)": "均价(元/kg)"})
        for col in ["最高价(元/kg)", "最低价(元/kg)", "均价(元/kg)", "交易量(吨)", "备注"]:
            if col not in df.columns:
                df[col] = None
        cleaned_dfs.append(df)

    df_final = pd.concat(cleaned_dfs, ignore_index=True)

    # ========== 基础清洗 ==========
    df_final["日期"] = pd.to_datetime(df_final["日期"], format="mixed", errors="coerce")
    df_final = df_final.sort_values("日期").reset_index(drop=True)
    df_final["产地"] = df_final["产地"].fillna("未知")
    for col in ["最高价(元/kg)", "最低价(元/kg)", "均价(元/kg)"]:
        df_final[col] = pd.to_numeric(df_final[col], errors="coerce")

    # ========== 关键新增：去重 ==========
    before = len(df_final)
    df_final = df_final.drop_duplicates(subset=["日期", "产地", "品种规格"], keep="last")
    after = len(df_final)
    print(f"🔍 去重检查：{before} → {after}（删除了 {before - after} 条重复）")

    # ========== 衍生字段 ==========
    df_final["年份"] = df_final["日期"].dt.year
    df_final["月份"] = df_final["日期"].dt.month
    df_final["周次"] = df_final["日期"].dt.isocalendar().week
    df_final["渠道类型"] = df_final.apply(classify_channel, axis=1)

    # 精准拆分省市县
    location_df = df_final["产地"].apply(parse_location).apply(pd.Series)
    df_final["省份"] = location_df[0]
    df_final["城市"] = location_df[1]
    df_final["区县/市场"] = location_df[2]

    df_final["果径(mm)"] = df_final["品种规格"].apply(extract_diameter)
    df_final["等级"] = df_final["品种规格"].apply(extract_grade)

    # ========== 保存 ==========
    df_final.to_csv(CLEAN_CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"✅ 清洗完成！已保存为 {CLEAN_CSV_PATH}")
    print(f"   共处理 {len(df_final)} 条数据。")
    print(f"   新增字段：年份、月份、周次、渠道类型、省份、城市、区县/市场、果径(mm)、等级")
    return df_final


if __name__ == "__main__":
    clean_blueberry_data()