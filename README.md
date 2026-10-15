# 🫐 蓝莓市场行情看板 (Blueberry Market Dashboard)

基于 Python + Streamlit 搭建的蓝莓行情数据分析与可视化平台，覆盖 2024-2026 年价格历史数据。

## 🚀 在线体验
👉 **[点击访问在线看板](https://blueberry-market-dashboard-6hflxinc6n5flpufg77ft3.streamlit.app/)**

## ✨ 功能特性
- 📊 **首页大盘**：全国蓝莓批发均价走势、自动洞察。
- 📍 **产区分析**：不同产区价格对比、样本量明细、采购建议。
- 🛒 **零售市场**：零售端规格溢价分析（果径 vs 价格）。
- 🏢 **行业格局**：行业供需情况、头部企业背景。
- 📥 **数据下载**：支持逐行勾选、CSV/Excel 双导出。
- 🔄 **自动刷新**：每 60 秒自动更新数据。

## 📸 页面截图

### 首页大盘
![首页大盘](docs/screenshot_home.png)

### 产区分析
![产区分析](docs/screenshot_origin.png)

### 行业格局
![行业格局](docs/screenshot_industry.png)

## 🛠️ 本地运行
```bash
git clone https://github.com/liligaogao/blueberry-market-dashboard.git
cd blueberry-market-dashboard
pip install -r requirements.txt
streamlit run src/app.py
