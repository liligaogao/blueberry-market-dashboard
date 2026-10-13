# 🫐 蓝莓市场行情看板 (Blueberry Market Dashboard)

基于 Python + Streamlit 搭建的蓝莓行情数据分析与可视化平台，覆盖2024-2026年价格历史数据。

## ✨ 功能特性
- 📊 **首页大盘**：全国蓝莓批发均价走势、自动洞察最高/最低价。
- 📍 **产区分析**：云南、辽宁、山东等主产区价格对比与分布。
- 🛒 **零售市场**：零售端规格溢价分析（果径大小 vs 价格）。
- 📥 **数据下载**：支持筛选后导出 CSV 数据。
- 🔄 **自动刷新**：每 60 秒自动更新最新数据。

## 🚀 在线体验
👉 [点击访问在线看板](https://blueberry-market-dashboard-6hflxinc6n5flpufg77ft3.streamlit.app/)

## 🛠️ 本地运行
```bash
pip install -r requirements.txt
streamlit run src/app.py
