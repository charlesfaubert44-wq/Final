# Portable Python Setup Guide for Work Computers

This guide helps you set up Python on work computers with restricted admin rights.

## Why Portable Python?

✅ No admin rights needed
✅ No system PATH modification required
✅ Can be on USB drive for multiple computers
✅ Won't conflict with system Python
✅ Easy to uninstall (just delete folder)

---

## Method 1: WinPython (Recommended)

### Step 1: Download WinPython

1. Go to: **https://winpython.github.io/**
2. Click "Download" or visit: https://github.com/winpython/winpython/releases
3. Download the latest version:
   - **WinPython64-3.12.x.x** (recommended)
   - Choose "dot" version (smaller, ~100MB) or full version
   - Example: `Winpython64-3.12.7.1dot.exe`

### Step 2: Extract WinPython

1. Run the downloaded `.exe` file
2. Extract to a location you can access without admin:
   ```
   Good locations:
   - C:\Users\[YourName]\WinPython
   - C:\Users\[YourName]\Desktop\WinPython
   - D:\WinPython (if available)
   ```
3. Wait for extraction to complete

### Step 3: Folder Structure

After extraction, you'll have:
```
WinPython/
├── python-3.12.x.amd64/
│   ├── python.exe          ← Main Python executable
│   ├── Scripts/
│   │   ├── pip.exe         ← Package installer
│   │   └── streamlit.exe   ← (after installing Streamlit)
│   └── Lib/
├── WinPython Command Prompt.exe  ← Use this!
└── WinPython Powershell Prompt.exe
```

### Step 4: Using WinPython

**Option A: Command Prompt Shortcut (Easiest)**
1. Double-click **"WinPython Command Prompt.exe"**
2. This opens a command prompt with Python in PATH
3. Test it:
   ```bash
   python --version
   pip --version
   ```

**Option B: From Any Command Prompt**
```bash
cd C:\Users\[YourName]\WinPython\python-3.12.x.amd64
python.exe --version
```

### Step 5: Install Required Packages

In the WinPython Command Prompt, navigate to project folder:
```bash
cd C:\Users\[YourName]\Desktop\wscc-portal-streamlit
pip install -r requirements.txt
```

Or install packages individually:
```bash
pip install streamlit
pip install pandas
pip install plotly
pip install streamlit-authenticator
pip install pyyaml
pip install cryptography
pip install networkx
pip install scikit-learn
pip install nltk
```

### Step 6: Run the WSCC Investigation Management System

```bash
cd C:\Users\[YourName]\Desktop\wscc-portal-streamlit
python -m streamlit run app.py
```

---

## Method 2: Python Embedded Distribution (Smallest)

For minimal installation (~25MB):

### Step 1: Download Python Embedded

1. Go to: https://www.python.org/downloads/windows/
2. Find "Windows embeddable package (64-bit)"
3. Download (e.g., `python-3.12.7-embed-amd64.zip`)

### Step 2: Extract and Setup

1. Extract ZIP to any folder (e.g., `C:\Users\[YourName]\Python-Embedded`)
2. Edit `python312._pth` file (inside extracted folder):
   - Uncomment the line: `import site`
   - Save and close

3. Download get-pip.py:
   ```bash
   # In Command Prompt, navigate to Python folder:
   cd C:\Users\[YourName]\Python-Embedded

   # Download get-pip.py
   curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

   # Install pip
   python.exe get-pip.py
   ```

### Step 3: Install Packages

```bash
cd C:\Users\[YourName]\Python-Embedded
python.exe -m pip install streamlit pandas plotly
```

### Step 4: Run Application

```bash
cd C:\Users\[YourName]\Desktop\wscc-portal-streamlit
C:\Users\[YourName]\Python-Embedded\python.exe -m streamlit run app.py
```

---

## Quick Launch Scripts

### Option 1: Batch File for WinPython

Create `run_wscc_app.bat` in your WinPython folder:

```batch
@echo off
echo Starting WSCC Investigation Management System...
cd /d "C:\Users\[YourName]\WinPython\python-3.12.x.amd64"
set PATH=%CD%;%CD%\Scripts;%PATH%
cd /d "C:\Users\[YourName]\Desktop\wscc-portal-streamlit"
python.exe -m streamlit run app.py --server.port 8501
pause
```

Double-click this file to start the application!

### Option 2: Batch File for Embedded Python

Create `run_wscc_app.bat` anywhere:

```batch
@echo off
echo Starting WSCC Investigation Management System...
cd /d "C:\Users\[YourName]\Desktop\wscc-portal-streamlit"
"C:\Users\[YourName]\Python-Embedded\python.exe" -m streamlit run app.py --server.port 8501
pause
```

---

## Troubleshooting

### Issue: "Python not found"
**Solution:** Use full path to python.exe or use WinPython Command Prompt shortcut

### Issue: "Module not found" error
**Solution:** Make sure you installed packages in the correct Python environment:
```bash
python -m pip install [package-name]
```

### Issue: "Permission denied" when installing packages
**Solution:** Use the `--user` flag:
```bash
pip install --user streamlit
```

### Issue: Can't access localhost:8501
**Solution:** Check if port is blocked by firewall. Try a different port:
```bash
python -m streamlit run app.py --server.port 8080
```

---

## Transferring to Another Computer

### Method 1: Copy WinPython Folder
1. Copy entire WinPython folder to USB drive
2. Paste on new computer (same location or update batch file paths)
3. Run WinPython Command Prompt
4. All packages are preserved!

### Method 2: Export Package List
On original computer:
```bash
pip freeze > requirements.txt
```

On new computer:
```bash
pip install -r requirements.txt
```

---

## Additional Tips

### Running on Different Port
```bash
python -m streamlit run app.py --server.port 8080
```

### Running Headless (No Browser Auto-Open)
```bash
python -m streamlit run app.py --server.headless true
```

### Accessing from Network
```bash
python -m streamlit run app.py --server.address 0.0.0.0
```

### Checking Installed Packages
```bash
pip list
```

### Updating Streamlit
```bash
pip install --upgrade streamlit
```

---

## Support

For more help:
- WinPython Documentation: https://github.com/winpython/winpython
- Python Documentation: https://docs.python.org/
- Streamlit Documentation: https://docs.streamlit.io/

---

**Note:** Replace `[YourName]` with your actual Windows username in all paths above.
