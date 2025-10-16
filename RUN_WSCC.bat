@echo off
REM ============================================
REM WSCC Investigation Management System
REM Streamlit Edition - Windows Launcher
REM ============================================

echo.
echo ================================================
echo  WSCC Investigation Management System
echo  Streamlit Edition
echo ================================================
echo.
echo Starting application...
echo.
echo The browser will open automatically at:
echo http://localhost:8501
echo.
echo Press CTRL+C to stop the server
echo ================================================
echo.

REM Start Streamlit
streamlit run app.py

REM If streamlit command not found, try with python -m
if errorlevel 1 (
    echo.
    echo Streamlit command not found. Trying alternative method...
    echo.
    python -m streamlit run app.py
)

pause
