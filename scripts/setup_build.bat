@echo off
REM 
setlocal
set /P ANSWER="PyInstaller���u�[�g���[�_�[���č쐬���ăC���X�g�[�����܂��B��낵���ł����H (y/n)�H"

if /i {%ANSWER%}=={y} (goto :y)
echo �����𒆒f���܂����B
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
REM PyInstraller���ăC���X�g�[�����܂��B
popd
call venv\Scripts\activate
echo Y|pip uninstall pyinstaller
pip install ..\pyinstaller

endlocal
timeout /T 15
