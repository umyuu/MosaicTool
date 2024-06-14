@echo on

cd /d %~dp0
cd ..
call venv\Scripts\activate
pyinstaller app.py --icon=assets/icons/app_icon.ico --onefile --windowed --name "MosaicTool" --noconfirm --noconsole --clean --collect-data tkinterdnd2 --add-data ./assets;./assets --add-data ./third_party;./third_party

TIMEOUT /T 10
