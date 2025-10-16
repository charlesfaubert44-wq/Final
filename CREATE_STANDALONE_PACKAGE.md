# Creating a Standalone WSCC Investigation Management System

This guide shows how to create a fully standalone version that can run on any Windows computer without Python installation.

---

## Method 1: Self-Contained Portable Package (Recommended)

Creates a folder containing everything needed - just copy and run!

### Step 1: Download Python Embedded

1. Download Python Embedded: https://www.python.org/downloads/windows/
2. Get "Windows embeddable package (64-bit)"
3. Example: `python-3.12.7-embed-amd64.zip`

### Step 2: Create Package Structure

Create this folder structure:
```
WSCC-Investigation-System/
├── python/                    (Python embedded)
├── app/                       (Your application)
│   ├── app.py
│   ├── database.py
│   ├── evidence_ui.py
│   ├── disclosure.py
│   ├── visual_analytics.py
│   ├── wscc_data.db
│   └── requirements.txt
├── data/                      (Database location)
├── RUN_WSCC.bat              (Launcher)
└── INSTALL_PACKAGES.bat      (First-time setup)
```

### Step 3: Setup Script

Create `SETUP_STANDALONE.bat` to automate the process:

```batch
@echo off
echo ========================================
echo WSCC Investigation System Setup
echo ========================================
echo.

REM Create directory structure
echo Creating directories...
mkdir WSCC-Investigation-System
cd WSCC-Investigation-System
mkdir python
mkdir app
mkdir data

echo.
echo Downloading Python Embedded...
echo Please download Python Embedded from:
echo https://www.python.org/ftp/python/3.12.7/python-3.12.7-embed-amd64.zip
echo.
echo Extract the contents to: %CD%\python\
echo.
pause

echo.
echo Configuring Python...
cd python

REM Enable pip support
echo Editing python312._pth to enable pip...
powershell -Command "(gc python312._pth) -replace '#import site', 'import site' | Out-File -encoding ASCII python312._pth"

echo.
echo Installing pip...
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python.exe get-pip.py

echo.
echo Setup complete!
echo Next: Run INSTALL_PACKAGES.bat
pause
```

### Step 4: Package Installation Script

Create `INSTALL_PACKAGES.bat`:

```batch
@echo off
echo ========================================
echo Installing WSCC System Dependencies
echo ========================================
echo.
echo This will install all required packages...
echo Please wait, this may take several minutes.
echo.

cd /d "%~dp0"
cd python

echo Installing Streamlit...
python.exe -m pip install streamlit

echo Installing data packages...
python.exe -m pip install pandas plotly

echo Installing security packages...
python.exe -m pip install streamlit-authenticator pyyaml cryptography

echo Installing analytics packages...
python.exe -m pip install networkx scikit-learn nltk

echo Installing additional utilities...
python.exe -m pip install python-dateutil pillow

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run RUN_WSCC.bat to start the system.
pause
```

### Step 5: Application Launcher

Create `RUN_WSCC.bat`:

```batch
@echo off
title WSCC Investigation Management System

REM Set colors for better visibility
color 0A

echo.
echo ========================================
echo   WSCC Investigation Management System
echo   Starting Application...
echo ========================================
echo.

REM Get script directory
cd /d "%~dp0"

REM Set Python path
set PYTHONPATH=%CD%\python
set PATH=%PYTHONPATH%;%PYTHONPATH%\Scripts;%PATH%

REM Check if Python exists
if not exist "python\python.exe" (
    echo ERROR: Python not found!
    echo Please run SETUP_STANDALONE.bat first.
    pause
    exit /b 1
)

REM Check if Streamlit is installed
python\python.exe -m pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo ERROR: Streamlit not installed!
    echo Please run INSTALL_PACKAGES.bat first.
    pause
    exit /b 1
)

REM Navigate to app directory
cd app

echo Starting Streamlit server...
echo.
echo Access the application at:
echo   http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Run the application
..\python\python.exe -m streamlit run app.py --server.port 8501 --server.headless true

pause
```

### Step 6: Quick Start Guide

Create `README_STANDALONE.txt`:

```
========================================
WSCC INVESTIGATION MANAGEMENT SYSTEM
Standalone Edition
========================================

FIRST TIME SETUP:
1. Run SETUP_STANDALONE.bat
2. Download Python Embedded when prompted
3. Run INSTALL_PACKAGES.bat
4. Wait for installation to complete

RUNNING THE APPLICATION:
- Double-click RUN_WSCC.bat
- Open browser to: http://localhost:8501
- Press Ctrl+C in the window to stop

SYSTEM REQUIREMENTS:
- Windows 7 or later
- 500MB free disk space
- No admin rights needed
- No Python installation required

TRANSFERRING TO ANOTHER COMPUTER:
1. Copy entire WSCC-Investigation-System folder
2. Paste on new computer
3. Run RUN_WSCC.bat
4. No reinstallation needed!

TROUBLESHOOTING:
- If Python not found: Re-run SETUP_STANDALONE.bat
- If packages missing: Re-run INSTALL_PACKAGES.bat
- If port 8501 blocked: Edit RUN_WSCC.bat and change port

For support: See PORTABLE_PYTHON_SETUP.md

========================================
Version 1.0 - Standalone Edition
========================================
```

---

## Method 2: PyInstaller Executable (Advanced)

Creates a single .exe file (experimental for Streamlit).

### Installation

```bash
pip install pyinstaller
```

### Create Spec File

Create `wscc_app.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('database.py', '.'),
        ('evidence_ui.py', '.'),
        ('disclosure.py', '.'),
        ('visual_analytics.py', '.'),
        ('wscc_data.db', '.'),
    ],
    hiddenimports=[
        'streamlit',
        'pandas',
        'plotly',
        'networkx',
        'sklearn',
        'nltk',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WSCC_Investigation_System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='wscc_icon.ico'  # Optional: Add your icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WSCC_Investigation_System',
)
```

### Build Command

```bash
pyinstaller wscc_app.spec
```

**Note:** PyInstaller with Streamlit can be tricky. Method 1 is more reliable.

---

## Method 3: Docker Container (Linux/Mac/Windows)

For advanced users who want containerization.

### Create Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
# Build image
docker build -t wscc-investigation-system .

# Run container
docker run -p 8501:8501 wscc-investigation-system
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  wscc-app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

---

## Distribution Checklist

### Files to Include in Standalone Package:
- [ ] Python embedded (python folder)
- [ ] All application .py files
- [ ] requirements.txt
- [ ] Database file (wscc_data.db)
- [ ] RUN_WSCC.bat launcher
- [ ] INSTALL_PACKAGES.bat setup script
- [ ] README_STANDALONE.txt instructions
- [ ] PORTABLE_PYTHON_SETUP.md guide

### Files to Exclude:
- [ ] __pycache__ folders
- [ ] .git folder
- [ ] .claude folder
- [ ] node_modules (if any)
- [ ] Virtual environments (venv, env)
- [ ] .pyc files
- [ ] Development tools

### Testing Standalone Package:
1. [ ] Copy to fresh computer/folder
2. [ ] Run setup scripts
3. [ ] Verify application launches
4. [ ] Test all features work
5. [ ] Check database operations
6. [ ] Verify no Python path issues

---

## Package Size Optimization

### Reduce Package Size:

1. **Use Python Embedded instead of full Python**
   - Embedded: ~25MB
   - Full Python: ~100MB

2. **Install only required packages**
   - Skip optional dependencies
   - Use --no-cache-dir with pip

3. **Compress with 7-Zip**
   - Create .7z archive
   - Can reduce size by 60-70%

4. **Remove unnecessary files**
   ```batch
   del /s /q __pycache__
   del /s /q *.pyc
   del /s /q .git
   ```

---

## Automatic Updater (Optional)

Create `UPDATE_WSCC.bat`:

```batch
@echo off
echo Checking for updates...
cd /d "%~dp0"

REM Update Python packages
python\python.exe -m pip install --upgrade streamlit pandas plotly

echo.
echo Update complete!
pause
```

---

## Security Considerations

1. **Database Encryption**
   - Use SQLCipher for encrypted database
   - Included in requirements.txt

2. **User Authentication**
   - Enable in app_secure.py
   - Configure auth_config.yaml

3. **Network Security**
   - Run on localhost only by default
   - Use --server.address for network access

4. **Data Backup**
   - Include backup script
   - Auto-backup to data/ folder

---

## Support and Maintenance

### Creating Distribution Package:

```batch
REM Create distribution ZIP
powershell Compress-Archive -Path WSCC-Investigation-System -DestinationPath WSCC-Standalone-v1.0.zip
```

### Version Control:

Create `VERSION.txt`:
```
WSCC Investigation Management System
Version: 1.0 Standalone
Build Date: 2025-01-16
Python: 3.12.7 Embedded
Streamlit: Latest
```

---

**Recommendation:** Use Method 1 (Self-Contained Package) for work computers.
It's the most reliable, portable, and doesn't require complex build processes.
