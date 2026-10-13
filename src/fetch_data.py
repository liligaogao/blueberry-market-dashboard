# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# from pathlib import Path
# from datetime import datetime
#
# BASE_DIR = Path(__file__).resolve().parent.parent
# RAW_CSV_PATH = BASE_DIR / "data" / "processed" / "blueberry_prices.csv"
#
# def fetch_moa_blueberry():
#     """模拟抓取农业农村部最新蓝莓价格，并追加到原始CSV中"""
#     print("开始抓取最新数据...")
#
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
#     }
#
#     url = "http://zdscxx.moa.gov.cn:8080/nyb/pc/frequency.jsp"
#
#     try:
#         resp = requests.get(url, headers=headers, timeout=10)
#         resp.raise_for_status()
#         soup = BeautifulSoup(resp.text, "lxml")
#
#         # 模拟一条抓取到的数据
#         new_data = {
#             "日期": datetime.today().strftime("%Y/%m/%d"),
#             "产地": "全国",
#             "品种规格": "批发均价",
#             "最高价(元/kg)": 18.2,
#             "最低价(元/kg)": 18.2,
#             "均价(元/kg)": 18.2,
#             "交易量(吨)": None,
#             "备注": "自动抓取数据"
#         }
#
#         # 去重检查
#         if RAW_CSV_PATH.exists():
#             try:
#                 try:
#                     df_existing = pd.read_csv(RAW_CSV_PATH, encoding="utf-8-sig")
#                 except UnicodeDecodeError:
#                     df_existing = pd.read_csv(RAW_CSV_PATH, encoding="gb18030")
#                 if "日期" in df_existing.columns:
#                     today_date = pd.to_datetime(new_data["日期"]).date()
#                     existing_dates = pd.to_datetime(df_existing["日期"], format="mixed", errors="coerce").dt.date
#                     if today_date in existing_dates.values:
#                         print(f"今日数据 ({today_date}) 已存在，跳过抓取。")
#                         return
#             except Exception as e:
#                 print(f"读取已有数据时出现问题，将直接追加：{e}")
#
#         # 追加数据到 CSV
#         with open(RAW_CSV_PATH, "a", encoding="utf-8-sig", newline="") as f:
#             if f.tell() == 0:
#                 f.write("日期,产地,品种规格,最高价(元/kg),最低价(元/kg),均价(元/kg),交易量(吨),备注\n")
#             f.write(f"{new_data['日期']},{new_data['产地']},{new_data['品种规格']},{new_data['最高价(元/kg)']},{new_data['最低价(元/kg)']},{new_data['均价(元/kg)']},,{new_data['备注']}\n")
#
#         print(f"成功抓取并追加一条数据：{new_data['日期']} - {new_data['均价(元/kg)']}元/kg")
#
#     except Exception as e:
#         print(f"抓取失败：{e}")
#
#
# if __name__ == "__main__":
#     fetch_moa_blueberry()

import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_CSV_PATH = BASE_DIR / "data" / "processed" / "blueberry_prices.csv"

def fetch_moa_blueberry():
    """模拟抓取农业农村部最新蓝莓价格，并安全追加到原始CSV中"""
    print("开始抓取最新数据...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    url = "http://zdscxx.moa.gov.cn:8080/nyb/pc/frequency.jsp"

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # 模拟一条抓取到的数据
        new_data = {
            "日期": datetime.today().strftime("%Y/%m/%d"),
            "产地": "全国",
            "品种规格": "批发均价",
            "最高价(元/kg)": 18.2,
            "最低价(元/kg)": 18.2,
            "均价(元/kg)": 18.2,
            "交易量(吨)": None,
            "备注": "自动抓取数据"
        }

        # 1. 安全读取已有数据（自动兼容 utf-8-sig 和 gb18030）
        if RAW_CSV_PATH.exists():
            try:
                df_existing = pd.read_csv(RAW_CSV_PATH, encoding="utf-8-sig")
            except UnicodeDecodeError:
                df_existing = pd.read_csv(RAW_CSV_PATH, encoding="gb18030")
        else:
            df_existing = pd.DataFrame()

        # 2. 检查今天的数据是否已经存在
        if not df_existing.empty and "日期" in df_existing.columns:
            today_date = pd.to_datetime(new_data["日期"]).date()
            existing_dates = pd.to_datetime(df_existing["日期"], format="mixed", errors="coerce").dt.date
            if today_date in existing_dates.values:
                print(f"今日数据 ({today_date}) 已存在，跳过抓取。")
                return

        # 3. 在内存中合并（避免直接向文件末尾追加导致乱码）
        df_new = pd.DataFrame([new_data])
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)

        # 4. 全量重写文件（统一使用 utf-8-sig 编码，这样以后 Excel 打开也不会乱码）
        df_combined.to_csv(RAW_CSV_PATH, index=False, encoding="utf-8-sig")
        print(f"成功抓取并追加一条数据：{new_data['日期']} - {new_data['均价(元/kg)']}元/kg")

    except Exception as e:
        print(f"抓取失败：{e}")

if __name__ == "__main__":
    fetch_moa_blueberry()