# Quick Security Implementation Guide

## Recommended: SQLCipher Encryption + Automated Backups

This provides maximum security for your investigation data on a work computer.

---

## Step 1: Install SQLCipher (5 minutes)

```bash
cd C:\Users\Charles\Desktop\wscc-portal-streamlit
pip install pysqlcipher3
```

---

## Step 2: Update requirements.txt (1 minute)

Add this line to requirements.txt:
```
pysqlcipher3>=1.2.0
```

---

## Step 3: Migrate Existing Database (10 minutes)

Create and run this script once:

**File: migrate_to_encrypted.py**
```python
import sqlite3
from pysqlcipher3 import dbapi2 as sqlcipher
import shutil
from datetime import datetime

def migrate_to_encrypted():
    """Migrate existing database to encrypted version"""

    # Step 1: Backup original (safety first!)
    backup_name = f'wscc_data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    shutil.copy('wscc_data.db', backup_name)
    print(f'✅ Backup created: {backup_name}')

    # Step 2: Read all data from old database
    print('📖 Reading existing data...')
    old_conn = sqlite3.connect('wscc_data.db')

    # Step 3: Create new encrypted database
    print('🔐 Creating encrypted database...')
    new_conn = sqlcipher.connect('wscc_data_encrypted.db')

    # SET YOUR PASSWORD HERE - REMEMBER THIS!
    PASSWORD = 'your-strong-password-here'  # CHANGE THIS!
    new_conn.execute(f"PRAGMA key='{PASSWORD}'")
    new_conn.execute("PRAGMA cipher_compatibility = 4")

    # Step 4: Copy all data
    print('📋 Copying data...')
    for line in old_conn.iterdump():
        try:
            new_conn.execute(line)
        except Exception as e:
            print(f'Warning: {e}')

    new_conn.commit()
    old_conn.close()
    new_conn.close()

    print('✅ Migration complete!')
    print('\nNext steps:')
    print('1. Test the encrypted database (see Step 4)')
    print('2. If working, replace original (see Step 5)')
    print(f'3. Keep backup safe: {backup_name}')

if __name__ == '__main__':
    print('WSCC Database Encryption Migration')
    print('=' * 50)
    print('\n⚠️  IMPORTANT: Edit this file and set a strong password first!')
    print('   Line 19: PASSWORD = "your-strong-password-here"\n')

    response = input('Have you set a strong password? (yes/no): ')
    if response.lower() == 'yes':
        migrate_to_encrypted()
    else:
        print('Please edit the file and set a password first.')

```

Run it:
```bash
python migrate_to_encrypted.py
```

---

## Step 4: Update database.py to Use Encryption (5 minutes)

Make these changes to database.py:

**Change 1: Import statement (line ~3)**
```python
# OLD:
import sqlite3

# NEW:
from pysqlcipher3 import dbapi2 as sqlite3
```

**Change 2: Add password configuration (add after imports)**
```python
# Database encryption password
# IMPORTANT: Store this securely! If lost, data cannot be recovered.
DB_PASSWORD = 'your-strong-password-here'  # Must match migration password
```

**Change 3: Update get_connection() function (around line ~15)**
```python
def get_connection():
    """Get database connection with encryption"""
    conn = sqlite3.connect(DB_FILE)

    # Enable encryption
    conn.execute(f"PRAGMA key='{DB_PASSWORD}'")
    conn.execute("PRAGMA cipher_compatibility = 4")

    conn.row_factory = sqlite3.Row
    return conn
```

---

## Step 5: Test and Activate (5 minutes)

1. **Temporarily rename files for testing:**
```bash
# Keep original safe
ren wscc_data.db wscc_data_ORIGINAL.db

# Test encrypted version
ren wscc_data_encrypted.db wscc_data.db
```

2. **Restart Streamlit and test:**
```bash
# Kill old server
# Press Ctrl+C in the terminal running Streamlit

# Start fresh
python -m streamlit run app.py
```

3. **Verify it works:**
   - Dashboard should show your data
   - Cases page should list your cases
   - Try adding a test case

4. **If everything works:**
```bash
# Delete the unencrypted original (ONLY if encrypted version works!)
del wscc_data_ORIGINAL.db
```

---

## Step 6: Set Up Automated Backups (15 minutes)

**File: backup_database.py**
```python
import os
import shutil
from datetime import datetime
from cryptography.fernet import Fernet

# Generate encryption key (run once and save this key!)
# Uncomment next line, run once, copy the output, then comment it again
# print(Fernet.generate_key())

# Paste your generated key here
BACKUP_KEY = b'your-generated-key-here'  # Replace with actual key from above

def create_encrypted_backup():
    """Create encrypted database backup"""

    # Backup location
    backup_dir = 'C:\\Users\\Charles\\Documents\\WSCC-Backups'
    os.makedirs(backup_dir, exist_ok=True)

    # Timestamp for backup file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'wscc_backup_{timestamp}.enc')

    # Read database file
    with open('wscc_data.db', 'rb') as f:
        data = f.read()

    # Encrypt the backup
    cipher = Fernet(BACKUP_KEY)
    encrypted_data = cipher.encrypt(data)

    # Save encrypted backup
    with open(backup_file, 'wb') as f:
        f.write(encrypted_data)

    # Get file size
    size = os.path.getsize(backup_file)
    size_kb = size / 1024

    print(f'✅ Encrypted backup created: {backup_file}')
    print(f'📦 Size: {size_kb:.1f} KB')

    # Cleanup old backups (keep last 7)
    cleanup_old_backups(backup_dir, keep=7)

    return backup_file

def cleanup_old_backups(backup_dir, keep=7):
    """Remove old backups, keeping only the most recent ones"""
    backups = sorted([
        f for f in os.listdir(backup_dir)
        if f.startswith('wscc_backup_') and f.endswith('.enc')
    ])

    if len(backups) > keep:
        for old_backup in backups[:-keep]:
            old_path = os.path.join(backup_dir, old_backup)
            os.remove(old_path)
            print(f'🗑️  Removed old backup: {old_backup}')

def restore_backup(backup_file):
    """Restore database from encrypted backup"""

    # Safety: backup current database first
    if os.path.exists('wscc_data.db'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.copy('wscc_data.db', f'wscc_data_before_restore_{timestamp}.db')
        print(f'✅ Current database backed up')

    # Read encrypted backup
    with open(backup_file, 'rb') as f:
        encrypted_data = f.read()

    # Decrypt
    cipher = Fernet(BACKUP_KEY)
    decrypted_data = cipher.decrypt(encrypted_data)

    # Write to database file
    with open('wscc_data.db', 'wb') as f:
        f.write(decrypted_data)

    print(f'✅ Database restored from: {backup_file}')

if __name__ == '__main__':
    print('WSCC Database Backup Tool')
    print('=' * 50)
    print('\n1. Create backup')
    print('2. Restore from backup')
    print('3. Exit')

    choice = input('\nChoice: ')

    if choice == '1':
        backup_file = create_encrypted_backup()
        print(f'\n✅ Backup saved to: {backup_file}')
    elif choice == '2':
        backup_file = input('Enter backup file path: ')
        if os.path.exists(backup_file):
            restore_backup(backup_file)
        else:
            print('❌ Backup file not found!')
    else:
        print('Goodbye!')
```

**Install backup tool dependency:**
```bash
pip install cryptography
```

**Add to requirements.txt:**
```
cryptography>=41.0.0
```

---

## Step 7: Schedule Automatic Backups (10 minutes)

### Option A: Windows Task Scheduler (Recommended)

1. Open Task Scheduler (search in Windows)
2. Create Basic Task:
   - Name: "WSCC Daily Backup"
   - Trigger: Daily at 6:00 PM (or your preference)
   - Action: Start a program
   - Program: `C:\Users\Charles\AppData\Local\Programs\Python\Python313\python.exe`
   - Arguments: `C:\Users\Charles\Desktop\wscc-portal-streamlit\backup_database.py`
   - Start in: `C:\Users\Charles\Desktop\wscc-portal-streamlit`

### Option B: Run manually when you remember
```bash
python backup_database.py
```

---

## Step 8: Test Backup and Restore (5 minutes)

1. **Create a test backup:**
```bash
python backup_database.py
# Choose option 1
```

2. **Verify backup file exists:**
```bash
dir C:\Users\Charles\Documents\WSCC-Backups
```

3. **Test restore (optional - only if you want to verify):**
   - Make a test change in the app (add a test case)
   - Run restore: `python backup_database.py` (choose option 2)
   - Verify the test case is gone (restored to backup state)

---

## Security Checklist

After completing all steps, you will have:

- ✅ **Encrypted database** - SQLCipher AES-256 encryption
- ✅ **Password protection** - Database cannot be read without password
- ✅ **Encrypted backups** - Automated daily encrypted backups
- ✅ **Backup rotation** - Keeps last 7 backups automatically
- ✅ **Recovery capability** - Can restore from any backup
- ✅ **No admin rights needed** - Everything runs in user space

---

## Important: Password Management

### Your passwords are stored in these files:
1. **migrate_to_encrypted.py** (line 19) - Only needed once
2. **database.py** (near top) - Needed every time app runs
3. **backup_database.py** (BACKUP_KEY) - Needed for backups/restore

### Best practices:
- ⚠️ **Use the same strong password** for database encryption (steps 3 & 4)
- ⚠️ **Use a different key** for backup encryption (step 6)
- ⚠️ **Write them down** and store in a secure location
- ⚠️ **If you forget the database password, your data is unrecoverable**
- ⚠️ **If you forget the backup key, your backups are unrecoverable**

### Suggested password storage:
- Write on paper and lock in a drawer
- Use a password manager (LastPass, 1Password, etc.)
- Store in encrypted USB drive

---

## Troubleshooting

### "Could not decrypt database" error
- **Cause:** Wrong password in database.py
- **Fix:** Verify DB_PASSWORD matches the password used in migration

### "Database is malformed" error
- **Cause:** Database file is corrupted or not encrypted
- **Fix:** Restore from backup using backup_database.py

### Backups not running automatically
- **Cause:** Task Scheduler not configured
- **Fix:** Re-check Task Scheduler settings (Step 7)

### "No module named 'pysqlcipher3'" error
- **Cause:** pysqlcipher3 not installed
- **Fix:** `pip install pysqlcipher3`

---

## Time Required

- **Total setup time:** ~1 hour
- **Daily maintenance:** None (automated)
- **Benefit:** Military-grade encryption protection

---

## Support

If you encounter any issues:
1. Check the backup file - you can always restore
2. The original unencrypted backup is saved in migration step
3. All backups are stored in `C:\Users\Charles\Documents\WSCC-Backups`

---

**Ready to implement?** Let me know and I'll help you through each step!
