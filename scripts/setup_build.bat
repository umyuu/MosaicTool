@echo off
REM 
setlocal
set /P ANSWER="PyInstallerをブートローダーを再作成し再インストールします。よろしいですか？ (y/n)？"

if /i {%ANSWER%}=={y} (goto :y)
echo 処理を中断しました。
timeout /T 15
exit

:y
cd /d %~dp0
cd ..
pushd ..

git clone https://github.com/pyinstaller/pyinstaller
cd .\pyinstaller
python -m venv venv
call venv\Scripts\activate
cd .\bootloader
python .\waf distclean all
cd ..\
pip install .
call venv\Scripts\deactivate
REM PyInstrallerを再インストールします。
popd
call venv\Scripts\activate
echo Y|pip uninstall pyinstaller
pip install ..\pyinstaller

endlocal
timeout /T 15
