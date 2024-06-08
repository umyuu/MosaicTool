@echo on

cd /d %~dp0
call venv\Scripts\activate
pyinstaller app.spec

TIMEOUT /T 10
