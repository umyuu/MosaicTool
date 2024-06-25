@echo on

cd /d %~dp0
cd ..
call venv\Scripts\activate
pyinstaller app.py --icon=assets/icons/app_icon.ico --windowed --name "MosaicTool" --noconfirm --clean --collect-data tkinterdnd2 --add-data ./assets;./assets --add-data ./third_party;./third_party --exclude-module=pip-licenses --exclude-module=numpy --exclude-module=snakeviz

TIMEOUT /T 10
