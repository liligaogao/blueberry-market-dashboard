@echo off
cd /d "D:\Python-Project py-project01"
"D:\develop\python\python.exe" src\fetch_data.py
"D:\develop\python\python.exe" src\process_data.py
"D:\develop\python\python.exe" src\export_excel.py
echo.
echo Task Completed! You can close this window.
pause