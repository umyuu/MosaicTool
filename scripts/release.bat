@echo on

cd /d %~dp0
cd ..
call venv\Scripts\activate
python scripts\release.py

TIMEOUT /T 10
