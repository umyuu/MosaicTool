@echo on

cd /d %~dp0
call venv\Scripts\activate
python app.py

TIMEOUT /T 10
