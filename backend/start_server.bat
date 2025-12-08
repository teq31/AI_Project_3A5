@echo off
echo Starting SmarTest Backend Server...
cd /d %~dp0
if not exist .venv (
    echo Creating virtual environment...
    py -m venv .venv
)
echo Activating virtual environment...
call .venv\Scripts\activate.bat
echo Installing dependencies...
py -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
echo Starting FastAPI server on http://127.0.0.1:8000
py -m uvicorn app.main:app --reload --port 8000
pause

