cd ..
call venv\Scripts\activate

python -m cProfile -o profile_result.prof app.py
snakeviz profile_result.prof

TIMEOUT 15
