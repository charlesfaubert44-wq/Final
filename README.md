# 🔍 WSCC Investigation Management System
## Streamlit Edition

**Workers' Safety & Compensation Commission**
Northwest Territories & Nunavut

A modern, portable investigation management system built with Streamlit and Python. Runs entirely on your local machine with **no admin privileges required**.

---

## ✨ Features

- 📊 **Dashboard** - Real-time statistics and recent cases
- 📁 **Case Management** - Full CRUD operations for investigation cases
- 👥 **Officer Management** - Manage investigation officers and assignments
- 📄 **Reports** - Generate territory-specific and combined reports
- 💾 **Data Persistence** - SQLite database (no browser storage limits)
- 🔍 **Search & Filter** - Advanced search and filtering capabilities
- 📤 **Export/Import** - JSON export/import for backups
- 🚀 **No Server Required** - Runs entirely on your local machine

---

## 🚀 Quick Start (Test in 2 Minutes)

### Prerequisites

1. **Python 3.7 or higher** - [Download Python](https://www.python.org/downloads/)
   - Check version: `python --version`

2. **pip** - Usually comes with Python
   - Check version: `pip --version`

### Installation (No Admin Privileges Needed)

```bash
# Step 1: Navigate to project folder
cd wscc-portal-streamlit

# Step 2: Install dependencies (user-level, no admin)
pip install --user -r requirements.txt

# Step 3: Run the application
streamlit run app.py

# OR use the Windows batch file
RUN_WSCC.bat
```

The application will automatically open in your default browser at `http://localhost:8501`

---

## 📋 System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| **Python** | 3.7+ | 3.9+ |
| **RAM** | 512 MB | 1 GB |
| **Storage** | 100 MB | 500 MB |
| **Browser** | Chrome 90+, Firefox 88+, Edge 90+ | Latest versions |
| **Admin Rights** | ❌ Not Required | - |
| **Internet** | Required for initial install | Not required after setup |

---

## 📁 Project Structure

```
wscc-portal-streamlit/
├── app.py                    # Main Streamlit application
├── database.py               # SQLite database layer
├── wscc_data.db             # SQLite database (auto-created on first run)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── ROADMAP.md               # Detailed migration roadmap
├── RUN_WSCC.bat            # Windows launcher (double-click to run)
└── .gitignore              # Git ignore rules
```

---

## 🎯 Usage Guide

### First Run

1. **Launch the application:**
   - Windows: Double-click `RUN_WSCC.bat`
   - Terminal: `streamlit run app.py`

2. **Demo data loads automatically:**
   - 2 sample cases
   - 2 sample officers
   - Ready to explore immediately

3. **Navigate using sidebar:**
   - 📊 Dashboard - View statistics
   - 📁 Cases - Manage investigation cases
   - 👥 Officers - Manage officers
   - 📄 Reports - Generate reports
   - ⚙️ Settings - Configure system

### Managing Cases

#### Add a New Case

1. Click **📁 Cases** in sidebar
2. Click **➕ Add New Case** button
3. Fill in required fields:
   - Case Number (e.g., WSCC-2024-XXX)
   - Territory (NWT or Nunavut)
   - Employer name
   - Worker name
4. Optional fields:
   - Incident date
   - Reported date
   - Status (Open, Under Investigation, Closed)
   - Priority (Low, Medium, High)
   - Description
   - Assign officers
5. Click **✅ Add Case**

#### View Case Details

1. Navigate to **📁 Cases**
2. Click **View** button on any case
3. Explore different tabs:
   - **Overview** - Basic case information
   - **Timeline** - Event timeline
   - **Reports** - Investigation reports
   - **Tasks** - Assigned tasks
   - **Evidence** - Evidence log
   - **Photos** - Incident photos
   - **Charges** - Violations and penalties
   - **Court** - Court proceedings
   - **Conclusion** - Final findings
   - **Briefing Note** - BN25-XXX notes

#### Search and Filter

1. Use the search box to find cases by:
   - Case number
   - Employer name
   - Worker name
2. Filter by:
   - Territory (NWT / Nunavut / All)
   - Status (Open / Under Investigation / Closed / All)

### Managing Officers

#### Add a New Officer

1. Click **👥 Officers** in sidebar
2. Click **➕ Add New Officer** button
3. Fill in required fields:
   - Name
   - Role (e.g., Senior Investigator)
4. Optional fields:
   - Work Location
   - Experience
   - Specialization
   - Contact information
5. Click **✅ Add Officer**

#### Search Officers

- Use the search box to find officers by name or role

### Generating Reports

1. Click **📄 Reports** in sidebar
2. Choose report type:
   - **📄 NWT Report** - Northwest Territories cases only
   - **📄 Nunavut Report** - Nunavut cases only
   - **📄 Combined Report** - All cases

### Exporting Data

1. Click **📄 Reports** in sidebar
2. Click **📥 Export to JSON**
3. Click **⬇️ Download JSON**
4. Save backup file to safe location

### Importing Data

1. Click **📄 Reports** in sidebar
2. Click **📤 Upload JSON file**
3. Select previously exported JSON file
4. Data will merge with existing database

---

## 🔒 Data Storage

### Database Location

- **File:** `wscc_data.db` (in project folder)
- **Type:** SQLite database
- **Size:** Unlimited (no browser storage limits)
- **Backup:** Copy the `wscc_data.db` file to back up all data

### Database Tables

1. **cases** - Investigation cases
   - Case details
   - Timeline events
   - Reports, tasks, evidence
   - Photos, charges, court info
   - Conclusion and briefing notes

2. **officers** - Investigation officers
   - Personal information
   - Role and specialization
   - Contact details
   - Active/inactive status

3. **settings** - Application settings
   - User preferences
   - Configuration options

---

## 🛠️ Troubleshooting

### Issue: "streamlit: command not found"

**Problem:** Streamlit not in system PATH after user-level install

**Solution:**
```bash
# Option 1: Use Python module syntax
python -m streamlit run app.py

# Option 2: Add to PATH (Windows)
set PATH=%PATH%;%APPDATA%\Python\Python39\Scripts

# Option 2: Add to PATH (Mac/Linux)
export PATH="$HOME/.local/bin:$PATH"
```

### Issue: "Permission denied" during installation

**Problem:** Trying to install system-wide

**Solution:**
```bash
# Always use --user flag (no admin needed)
pip install --user -r requirements.txt
```

### Issue: Port 8501 already in use

**Problem:** Another Streamlit app is running

**Solution:**
```bash
# Option 1: Close other Streamlit apps
# Then restart

# Option 2: Use different port
streamlit run app.py --server.port 8502
```

### Issue: Database locked

**Problem:** Multiple instances accessing database

**Solution:**
1. Close all browser tabs running the app
2. Stop all running Streamlit processes
3. Restart the application

### Issue: Application won't start

**Problem:** Missing dependencies or Python issues

**Solution:**
```bash
# Reinstall dependencies
pip install --user --force-reinstall -r requirements.txt

# Check Python version (must be 3.7+)
python --version

# Try running with verbose output
streamlit run app.py --logger.level=debug
```

---

## 🆚 Comparison with Original Version

| Feature | Original (HTML/JS) | Streamlit Version |
|---------|-------------------|-------------------|
| **Technology** | HTML/CSS/JavaScript | Python/Streamlit |
| **Data Storage** | localStorage (5-10MB limit) | SQLite (unlimited) |
| **Files** | 8 JavaScript modules (2,392 lines) | 2 Python files (1,400 lines) |
| **Server** | None (file-based) | Local server (streamlit) |
| **Admin Rights** | Not required | Not required |
| **Portability** | Browser-dependent | Python-dependent |
| **Maintenance** | Complex (8 modules) | Simple (2 modules) |
| **UI Framework** | Custom CSS | Streamlit components |
| **Photo Storage** | IndexedDB (complex) | SQLite + base64 |
| **Backup** | Manual export | Copy database file |

### Key Advantages

1. ✅ **No Browser Storage Limits** - SQLite can grow infinitely
2. ✅ **Better Data Integrity** - ACID-compliant database
3. ✅ **Easier Maintenance** - 2 Python files vs 8 JS modules
4. ✅ **Professional UI** - Modern Streamlit components
5. ✅ **Better Error Handling** - Python exception handling
6. ✅ **Works on Restricted Computers** - No admin privileges needed

---

## 📈 Migration Status

The application is currently **40% complete** with core functionality implemented.

### ✅ Completed Features

- Database layer (SQLite)
- Navigation system
- Dashboard with statistics
- Case list with filtering
- Add new cases
- Officer management
- Add new officers
- Search functionality
- Basic export/import

### 🔄 In Progress

- Edit cases
- Delete cases
- Timeline management
- Task management

### ⏳ Planned Features

- Evidence logging
- Photo upload and management
- Reports generation (NWT, Nunavut, Combined)
- Charges and violations
- Court proceedings
- Case conclusion
- BN25-XXX briefing note generator
- Advanced search and filtering

See **ROADMAP.md** for complete migration plan.

---

## 🤝 Contributing

This is an internal WSCC project. For feature requests or bug reports, contact the development team.

---

## 📝 Version History

### Version 1.0 (October 2024)
- Initial Streamlit conversion
- Core case and officer management
- Dashboard and statistics
- SQLite database implementation
- Basic export/import

---

## 📞 Support

### Resources

- **Streamlit Documentation:** https://docs.streamlit.io
- **SQLite Documentation:** https://sqlite.org/docs.html
- **Python Documentation:** https://docs.python.org

### Getting Help

1. Check this README
2. Review ROADMAP.md
3. Check Streamlit documentation
4. Contact development team

---

## 📄 License

Internal use only - Workers' Safety & Compensation Commission
Northwest Territories & Nunavut

---

## 🎉 Acknowledgments

Built with:
- **Streamlit** - Python web framework
- **SQLite** - Embedded database
- **Python** - Programming language

Original HTML/JavaScript version converted to Streamlit for improved portability and maintainability.

---

**Made with ❤️ for WSCC**

*Last Updated: October 15, 2024*
