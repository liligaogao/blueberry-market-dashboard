import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
CLEAN_CSV_PATH = DATA_DIR / "blueberry_prices_clean.csv"
EXCEL_OUTPUT_PATH = DATA_DIR / "blueberry_market_report.xlsx"


def export_to_excel():
    """读取清洗后的数据，导出为带格式和图表的 Excel"""
    print("正在生成 Excel 报表...")

    df = pd.read_csv(CLEAN_CSV_PATH, encoding="utf-8-sig", parse_dates=["日期"])

    # 拆分全国数据和产地数据，方便分别作图
    national_df = df[df["产地"] == "全国"].sort_values("日期")
    origin_df = df[(df["日期"] == "2026-03-29") & (df["产地"] != "全国")].copy()

    with pd.ExcelWriter(EXCEL_OUTPUT_PATH, engine="xlsxwriter") as writer:
        # 1. 将主数据写入名为“行情数据”的 Sheet
        df.to_excel(writer, sheet_name="行情数据", index=False)

        workbook = writer.book
        worksheet = writer.sheets["行情数据"]

        # 2. 定义格式
        header_format = workbook.add_format({
            "bold": True,
            "text_wrap": True,
            "valign": "vcenter",
            "align": "center",
            "bg_color": "#DCE6F1",
            "border": 1
        })
        date_format = workbook.add_format({"num_format": "yyyy-mm-dd"})

        # 3. 设置列宽
        worksheet.set_column("A:A", 12, date_format)
        worksheet.set_column("B:B", 15)
        worksheet.set_column("C:C", 25)
        worksheet.set_column("D:F", 15)
        worksheet.set_column("G:G", 10)
        worksheet.set_column("H:H", 30)

        # 应用表头格式
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # 4. 插入折线图
        chart_line = workbook.add_chart({"type": "line"})
        national_df.to_excel(writer, sheet_name="图表数据源", index=False)
        chart_line.add_series({
            "name": "全国批发均价",
            "categories": ["图表数据源", 1, 0, len(national_df), 0],
            "values": ["图表数据源", 1, 5, len(national_df), 5],
            "marker": {"type": "circle", "size": 6},
        })
        chart_line.set_title({"name": "全国蓝莓批发均价走势"})
        chart_line.set_x_axis({"name": "日期"})
        chart_line.set_y_axis({"name": "价格 (元/公斤)"})
        chart_line.set_legend({"position": "bottom"})
        worksheet.insert_chart("J2", chart_line, {"x_scale": 1.5, "y_scale": 1.5})

        # 5. 插入柱状图
        chart_bar = workbook.add_chart({"type": "column"})
        origin_df.to_excel(writer, sheet_name="产地图表源", index=False)
        chart_bar.add_series({
            "name": "产地均价",
            "categories": ["产地图表源", 1, 1, len(origin_df), 1],
            "values": ["产地图表源", 1, 5, len(origin_df), 5],
            "data_labels": {"value": True},
        })
        chart_bar.set_title({"name": "主产区价格对比 (2026-03-29)"})
        chart_bar.set_x_axis({"name": "产地"})
        chart_bar.set_y_axis({"name": "价格 (元/公斤)"})
        chart_bar.set_legend({"none": True})
        worksheet.insert_chart("J20", chart_bar, {"x_scale": 1.5, "y_scale": 1.5})

    print(f"Excel 报表已生成：{EXCEL_OUTPUT_PATH}")


if __name__ == "__main__":
    export_to_excel()