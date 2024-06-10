@echo on

cd /d %~dp0
call venv\Scripts\activate
pyinstaller app.py --onefile --windowed --name "MosaicTool" --noconsole --clean --collect-data tkinterdnd2 --add-data third_party\icons;third_party\icons

TIMEOUT /T 10
