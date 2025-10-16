@echo off
echo ========================================
echo Installing WSCC System Dependencies
echo ========================================
echo.
echo This will install all required packages...
echo Please wait, this may take several minutes.
echo.

cd /d "%~dp0"

REM Check if using portable Python
if exist "python\python.exe" (
    echo Using portable Python...
    set PYTHON_CMD=python\python.exe
) else (
    echo Using system Python...
    set PYTHON_CMD=python
)

echo.
echo Installing core framework...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install streamlit>=1.28.0

echo.
echo Installing data packages...
%PYTHON_CMD% -m pip install pandas>=2.0.0
%PYTHON_CMD% -m pip install plotly>=5.17.0

echo.
echo Installing security packages...
%PYTHON_CMD% -m pip install streamlit-authenticator>=0.4.0
%PYTHON_CMD% -m pip install pyyaml>=6.0
%PYTHON_CMD% -m pip install cryptography>=41.0.0

echo.
echo Installing analytics packages...
%PYTHON_CMD% -m pip install networkx>=3.1
%PYTHON_CMD% -m pip install scikit-learn>=1.3.0
%PYTHON_CMD% -m pip install nltk>=3.8.1
%PYTHON_CMD% -m pip install numpy>=1.24.0

echo.
echo Installing utilities...
%PYTHON_CMD% -m pip install python-dateutil>=2.8.2
%PYTHON_CMD% -m pip install pillow>=10.0.0

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run RUN_WSCC.bat to start the system.
echo.
pause
