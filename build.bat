@echo on

cd /d %~dp0
call venv\Scripts\activate
pyinstaller app.py --onefile --noconsole --clean --collect-data tkinterdnd2

TIMEOUT /T 10
