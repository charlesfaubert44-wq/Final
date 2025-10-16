========================================
WSCC INVESTIGATION MANAGEMENT SYSTEM
Standalone Edition
========================================

QUICK START:
1. Double-click RUN_WSCC.bat
2. Open browser to: http://localhost:8501
3. Press Ctrl+C in the window to stop

FIRST TIME SETUP (if needed):
1. Run INSTALL_PACKAGES.bat
2. Wait for installation to complete (5-10 minutes)
3. Run RUN_WSCC.bat

SYSTEM REQUIREMENTS:
- Windows 7 or later (64-bit)
- 500MB free disk space
- Internet connection (for first-time setup)
- Python 3.12 or later

TWO INSTALLATION OPTIONS:

OPTION 1: Use System Python (Recommended if you have Python)
1. Python already installed on your computer
2. Just run INSTALL_PACKAGES.bat
3. Run RUN_WSCC.bat

OPTION 2: Portable Python (No installation needed)
1. Download Python Embedded:
   https://www.python.org/downloads/windows/

2. Get "Windows embeddable package (64-bit)"
   Example: python-3.12.7-embed-amd64.zip

3. Extract to a "python" folder in this directory:
   wscc-portal-streamlit/
   └── python/
       ├── python.exe
       ├── python312.dll
       └── ... other files

4. Edit python/python312._pth:
   - Uncomment the line: import site
   - Save the file

5. Install pip:
   cd python
   curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
   python.exe get-pip.py

6. Run INSTALL_PACKAGES.bat

7. Run RUN_WSCC.bat

FEATURES:
- Case Management: Track investigation cases
- Evidence Management: Document and photos
- Officer Assignment: Team collaboration
- Smart Search: AI-powered case search
- Reports: Generate investigation reports
- Visual Analytics: Network visualization
- Data Export/Import: JSON and CSV formats
- Dark Mode: Eye-friendly interface

DEFAULT CREDENTIALS (app_secure.py):
Username: admin
Password: admin123
(Change in auth_config.yaml)

ACCESSING FROM ANOTHER COMPUTER:
1. Note your computer's IP address: ipconfig
2. Run: python -m streamlit run app.py --server.address 0.0.0.0
3. Access from other computer: http://YOUR_IP:8501

TRANSFERRING TO ANOTHER COMPUTER:
1. Copy entire wscc-portal-streamlit folder
2. Paste on new computer
3. If using portable Python: No reinstallation needed!
4. If using system Python: Run INSTALL_PACKAGES.bat
5. Run RUN_WSCC.bat

TROUBLESHOOTING:

Problem: "Python not found"
Solution: Install Python from python.org
          Or setup portable Python (see OPTION 2)

Problem: "Streamlit not found"
Solution: Run INSTALL_PACKAGES.bat

Problem: "Port 8501 already in use"
Solution: Edit RUN_WSCC.bat, change 8501 to 8080

Problem: Page won't load
Solution: Check if firewall is blocking port 8501
          Try accessing: http://127.0.0.1:8501

Problem: Database errors
Solution: Delete wscc_data.db (will recreate with demo data)

Problem: Missing packages
Solution: Run INSTALL_PACKAGES.bat again

FOLDER STRUCTURE:
wscc-portal-streamlit/
├── app.py                      Main application
├── app_secure.py               Secure version with auth
├── database.py                 Database management
├── evidence_ui.py              Evidence management
├── disclosure.py               Report generation
├── visual_analytics.py         Graph visualizations
├── requirements.txt            Python dependencies
├── wscc_data.db               SQLite database
├── RUN_WSCC.bat               Application launcher
├── INSTALL_PACKAGES.bat       Dependency installer
├── README_STANDALONE.txt      This file
├── PORTABLE_PYTHON_SETUP.md   Portable setup guide
└── CREATE_STANDALONE_PACKAGE.md   Advanced packaging

DATA BACKUP:
- Database location: wscc_data.db
- Backup regularly using Export function in app
- Or copy wscc_data.db to backup location

UPDATING:
- Run INSTALL_PACKAGES.bat to update packages
- Or manually: pip install --upgrade streamlit

SUPPORT:
- Documentation: See markdown files in this folder
- GitHub: https://github.com/charlesfaubert44-wq/Final
- Issues: Report at GitHub Issues page

VERSION INFORMATION:
Version: 1.0 Standalone
Python: 3.12+ required
Streamlit: 1.28.0+
Last Updated: January 2025

========================================
Workers' Safety & Compensation Commission
Investigation Management System
========================================
