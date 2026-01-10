@echo off
echo Installing NLP dependencies...
cd /d %~dp0

if not exist .venv (
    echo Virtual environment not found. Please run start_server.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing NLP libraries...
py -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org sentence-transformers scikit-learn fuzzywuzzy python-Levenshtein

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ NLP dependencies installed successfully!
    echo The system will now use semantic similarity for better answer understanding.
) else (
    echo.
    echo ⚠️ Some dependencies failed to install. The system will use fallback methods.
)

pause

