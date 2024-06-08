@echo on

cd /d %~dp0
cd..

if not exist "venv/Scripts/activate" (
  python -m venv venv  
  call venv\Scripts\activate
  pip install -r requirements.txt  
)

TIMEOUT /T 10
