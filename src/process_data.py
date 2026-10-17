import pandas as pd
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
RAW_CSV_PATH = DATA_DIR / "blueberry_prices.csv"
CLEAN_CSV_PATH = DATA_DIR / "blueberry_prices_clean.csv"

# 预置直辖市和主要地级市字典
SPECIAL_CITIES = {
    "北京": "北京", "上海": "上海", "天津": "天津", "重庆": "重庆",
    "济南": "济南", "青岛": "青岛", "烟台": "烟台", "潍坊": "潍坊",
    "临沂": "临沂", "日照": "日照", "南京": "南京", "连云港": "连云港",
    "无锡": "无锡", "常州": "常州", "苏州": "苏州", "嘉兴": "嘉兴",
    "丹东": "丹东", "大连": "大连", "沈阳": "沈阳", "昆明": "昆明",
    "玉溪": "玉溪", "红河": "红河", "保山": "保山", "澄江": "澄江",
    "陆良": "陆良", "深圳": "深圳", "广州": "广州", "福州": "福州",
    "德阳": "德阳", "太原": "太原"
}


def classify_channel(row):
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


def clean_suffix(text):
    """清洗区县/市场名，去掉多余的词，但不破坏正常名称"""
    if not text:
        return text
    # 如果是纯市场/超市，直接返回原名，不要乱切
    market_keywords = ["超市", "市场", "大润发", "盒马", "鲜生", "批发", "水果"]
    for kw in market_keywords:
        if kw in text:
            return text

    # 正常区县，去掉“市”、“区”、“县”后缀（可选，这里保留原名更清晰）
    # 如果你想保留原汁原味的区县名，这里直接 return text 就行
    return text


def parse_location(origin):
    origin = str(origin).strip()

    # 1. 特殊标记处理
    if not origin or origin in ["全国", "进口", "全国超市", "市场", "其他", "全国-产地货源", "全国-销地批发"]:
        return "全国/特殊", "全国/特殊", origin

    # 2. 处理多产地组合（如 "四川/云南"），取第一个
    if "/" in origin and origin.split("/")[0] in ["四川", "云南", "山东"]:
        origin = origin.split("/")[0]

    # 3. 匹配直辖市和预置城市
    for city, city_name in SPECIAL_CITIES.items():
        if origin.startswith(city):
            province = "直辖市"
            if city in ["济南", "青岛", "烟台", "潍坊", "临沂", "日照"]:
                province = "山东"
            elif city in ["南京", "连云港", "无锡", "常州", "苏州"]:
                province = "江苏"
            elif city in ["丹东", "大连", "沈阳"]:
                province = "辽宁"
            elif city in ["昆明", "玉溪", "红河", "保山", "澄江", "陆良"]:
                province = "云南"
            elif city in ["深圳", "广州"]:
                province = "广东"
            elif city in ["嘉兴"]:
                province = "浙江"
            elif city in ["德阳"]:
                province = "四川"
            elif city in ["太原"]:
                province = "山西"

            rest = origin[len(city):]
            # 如果后面还有区县，去掉“市”字后缀
            county = rest
            if rest.endswith("市"):
                county = rest[:-1]
            elif rest.startswith("市"):
                county = rest[1:]

            # 处理类似 "丹东东港市" -> 城市:丹东, 区县:东港市 (保留原样)
            if county.startswith(city):
                county = county[len(city):]

            return province, city, clean_suffix(county) if county else city

    # 4. 通用省份匹配
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

            # 尝试用正则匹配带“市”的地级市
            match_city = re.match(r'(.{2,4}?[市州盟])', rest)
            if match_city:
                city = match_city.group(1)
                county = rest[len(city):]
                return p, city.replace("市", ""), clean_suffix(county) if county else city
            else:
                # 如果没带市字，强行截取前2-3个字当城市
                if len(rest) >= 2:
                    return p, rest[:2], clean_suffix(rest[2:]) if len(rest) > 2 else rest
                else:
                    return p, rest, rest

    return "其他", "其他", clean_suffix(origin)


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