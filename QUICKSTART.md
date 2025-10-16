# 🚀 Quick Start Guide - WSCC Streamlit Edition

**Complete in 3 simple steps!**

---

## ✅ Step 1: Install Dependencies (One-Time Setup)

Open Command Prompt or PowerShell in the project folder:

```bash
pip install -r requirements.txt
```

**Note:** This installs to your user folder - **no admin privileges required!**

---

## ✅ Step 2: Launch the Application

Choose one of these methods:

### Method A: Double-Click the Batch File (Easiest)
- Double-click `RUN_WSCC.bat`
- Browser opens automatically at http://localhost:8501

### Method B: Command Line
```bash
python -m streamlit run app.py
```

### Method C: If streamlit is in your PATH
```bash
streamlit run app.py
```

---

## ✅ Step 3: Use the Application

The browser opens automatically to http://localhost:8501

### Navigation

Use the sidebar to access different pages:
- **📊 Dashboard** - Statistics and recent cases
- **📁 Cases** - Manage investigation cases
- **👥 Officers** - Manage officers
- **📄 Reports** - Generate reports and export data
- **⚙️ Settings** - System settings

---

## 📝 Quick Feature Tour

### Add a New Case

1. Click **📁 Cases** in sidebar
2. Click **➕ Add New Case**
3. Fill in required fields:
   - Case Number: `WSCC-2024-XXX`
   - Territory: `Northwest Territories` or `Nunavut`
   - Employer: Company name
   - Worker: Worker name
4. Click **✅ Add Case**

### View Case Details

1. Navigate to **📁 Cases**
2. Click **View** on any case
3. Explore tabs:
   - Overview, Timeline, Reports, Tasks, Evidence, Photos, Charges, Court, Conclusion, Briefing Note

### Add a New Officer

1. Click **👥 Officers** in sidebar
2. Click **➕ Add New Officer**
3. Fill in details:
   - Name
   - Role
   - Work Location (optional)
4. Click **✅ Add Officer**

### Export Data

1. Click **📄 Reports** in sidebar
2. Click **📥 Export to JSON**
3. Click **⬇️ Download JSON**
4. Save backup file

---

## 🗄️ Data Location

All data is stored in:
```
wscc-portal-streamlit/wscc_data.db
```

To backup your data:
1. Copy `wscc_data.db` to a safe location
2. To restore: Replace the file with your backup

---

## ⚙️ Configuration

### Change Port (if 8501 is busy)

```bash
python -m streamlit run app.py --server.port 8502
```

### Disable Usage Statistics

Create `.streamlit/config.toml`:
```toml
[browser]
gatherUsageStats = false
```

---

## ❌ Stop the Application

- Press `CTRL + C` in the terminal
- Or close the Command Prompt window

---

## 🆘 Troubleshooting

### "streamlit: command not found"

**Solution:**
```bash
# Use Python module syntax instead
python -m streamlit run app.py
```

### Port Already in Use

**Solution:**
```bash
# Use a different port
python -m streamlit run app.py --server.port 8502
```

### Application Won't Start

**Solution:**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python version (must be 3.7+)
python --version
```

---

## 📊 Current Features (v1.0)

### ✅ Working Features
- Dashboard with statistics
- Case list with search/filter
- Add new cases
- View case details (basic)
- Officer management
- Add new officers
- Data export to JSON

### 🔄 In Development
- Edit cases
- Delete cases
- Timeline management
- Task tracking
- Evidence logging
- Photo upload
- Report generation
- Charges and court proceedings

---

## 📖 More Information

- **Full Documentation:** See `README.md`
- **Migration Roadmap:** See `ROADMAP.md`
- **Streamlit Docs:** https://docs.streamlit.io

---

## 🎯 Next Steps

1. Explore the demo data (2 cases, 2 officers)
2. Add your first real case
3. Assign officers to cases
4. Export data regularly for backups

---

**Your application is now running at:**
👉 http://localhost:8501

**Enjoy the WSCC Investigation Management System!** 🎉
