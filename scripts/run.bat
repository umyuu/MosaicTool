@echo on

cd /d %~dp0
cd ..
call venv\Scripts\activate
python app.py

TIMEOUT /T 10
