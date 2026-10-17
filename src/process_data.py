import pandas as pd
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
RAW_CSV_PATH = DATA_DIR / "blueberry_prices.csv"
CLEAN_CSV_PATH = DATA_DIR / "blueberry_prices_clean.csv"

# 完善后的城市字典：只要命中这些词，直接提取为城市，绝不乱切
CITY_MAPPING = {
    # 直辖市
    "北京": "直辖市", "上海": "直辖市", "天津": "直辖市", "重庆": "直辖市",
    # 山东
    "济南": "山东", "青岛": "山东", "烟台": "山东", "潍坊": "山东", "临沂": "山东", "日照": "山东",
    # 江苏
    "南京": "江苏", "连云港": "江苏", "无锡": "江苏", "常州": "江苏", "苏州": "江苏",
    # 浙江
    "嘉兴": "浙江", "杭州": "浙江",
    # 辽宁
    "丹东": "辽宁", "大连": "辽宁", "沈阳": "辽宁",
    # 云南
    "昆明": "云南", "玉溪": "云南", "红河": "云南", "保山": "云南", "澄江": "云南", "陆良": "云南",
    # 广东
    "深圳": "广东", "广州": "广东", "珠海": "广东",
    # 福建
    "福州": "福建", "厦门": "福建",
    # 四川
    "成都": "四川", "德阳": "四川",
    # 山西
    "太原": "山西"
}


def classify_channel(row):
    origin = str(row["产地"])
    retail_keywords = ["大润发", "盒马", "超市", "堤口"]
    for kw in retail_keywords:
        if kw in origin: return "零售"
    wholesale_keywords = ["全国", "新发地", "上海市场", "江南市场", "海峡市场", "河西市场", "东桥市场", "金马正昌",
                          "鼎信", "昆明市场", "市场", "进口"]
    for kw in wholesale_keywords:
        if kw in origin: return "批发"
    return "产地"


def parse_location(origin):
    origin = str(origin).strip()

    # 1. 特殊标记处理
    if not origin or origin in ["全国", "进口", "全国超市", "市场", "其他", "全国-产地货源", "全国-销地批发"]:
        return "全国/特殊", "全国/特殊", origin

    # 2. 处理多产地组合
    if "/" in origin and origin.split("/")[0] in ["四川", "云南", "山东"]:
        origin = origin.split("/")[0]

    # 3. 城市字典优先匹配（解决“连云港”被切碎、“济南超市”被切碎的问题）
    for city, province in CITY_MAPPING.items():
        if city in origin:
            # 比如 "济南超市"，找到"济南"，剩下的就是"超市"
            idx = origin.find(city)
            county = origin[idx + len(city):]
            # 如果县级为空，就用城市名
            if not county:
                county = city
            return province, city, county

    # 4. 通用省份匹配（兜底机制，处理字典里没写的地名）
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

            # 尝试提取带“市”字的地级市
            match_city = re.match(r'(.{2,4}?[市州盟])', rest)
            if match_city:
                city = match_city.group(1).replace("市", "")
                county = rest[len(match_city.group(1)):]
                return p, city, county if county else city
            else:
                # 如果没带“市”，且剩下的包含市场/超市，就取前2字当城市
                if any(kw in rest for kw in ["市场", "超市", "大润发", "水果"]):
                    return p, rest[:2] if len(rest) >= 2 else rest, rest
                # 强行切分
                if len(rest) >= 2:
                    return p, rest[:2], rest[2:] if len(rest) > 2 else rest
                else:
                    return p, rest, rest

    return "其他", "其他", origin


def extract_diameter(spec):
    spec = str(spec)
    match = re.search(r'(\d+)\s*[-~]\s*(\d+)\s*mm', spec)
    if match: return int(match.group(1))
    match = re.search(r'(\d+)\s*mm', spec)
    if match: return int(match.group(1))
    return None


def extract_grade(spec):
    spec = str(spec)
    if "精品" in spec or "品质最优" in spec: return "精品"
    if "特大" in spec: return "特大果"
    if "大果" in spec or "超大" in spec: return "大果"
    if "中果" in spec: return "中果"
    if "小果" in spec: return "小果"
    if "通货" in spec: return "通货"
    if "统货" in spec: return "统货"
    if "批发均价" in spec or "均价" in spec: return "均价"
    return "未分类"


def clean_blueberry_data():
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
        if not chunk_lines: continue

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

        all_dfs.append(pd.DataFrame(data, columns=header))

    cleaned_dfs = []
    for df in all_dfs:
        df = df.rename(columns={"渠道/产地": "产地", "价格(元/公斤)": "均价(元/kg)"})
        for col in ["最高价(元/kg)", "最低价(元/kg)", "均价(元/kg)", "交易量(吨)", "备注"]:
            if col not in df.columns: df[col] = None
        cleaned_dfs.append(df)

    df_final = pd.concat(cleaned_dfs, ignore_index=True)
    df_final["日期"] = pd.to_datetime(df_final["日期"], format="mixed", errors="coerce")
    df_final = df_final.sort_values("日期").reset_index(drop=True)
    df_final["产地"] = df_final["产地"].fillna("未知")
    for col in ["最高价(元/kg)", "最低价(元/kg)", "均价(元/kg)"]:
        df_final[col] = pd.to_numeric(df_final[col], errors="coerce")

    df_final = df_final.drop_duplicates(subset=["日期", "产地", "品种规格"], keep="last")

    df_final["年份"] = df_final["日期"].dt.year
    df_final["月份"] = df_final["日期"].dt.month
    df_final["周次"] = df_final["日期"].dt.isocalendar().week
    df_final["渠道类型"] = df_final.apply(classify_channel, axis=1)

    location_df = df_final["产地"].apply(parse_location).apply(pd.Series)
    df_final["省份"] = location_df[0]
    df_final["城市"] = location_df[1]
    df_final["区县/市场"] = location_df[2]

    df_final["果径(mm)"] = df_final["品种规格"].apply(extract_diameter)
    df_final["等级"] = df_final["品种规格"].apply(extract_grade)

    df_final.to_csv(CLEAN_CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"✅ 清洗完成！已保存为 {CLEAN_CSV_PATH}")
    return df_final


if __name__ == "__main__":
    clean_blueberry_data()