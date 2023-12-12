echo off

:: Create virtual environment
echo Creating virtual environment...
py -3 -m venv venv

:: Install requirements
echo Installing requirements...
"%CD%\venv\Scripts\pip.exe" install -r requirements.txt --require-virtualenv

echo on