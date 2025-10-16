# Security Enhancement Options for WSCC Streamlit

## Current Security Status

**Location:** `C:\Users\Charles\Desktop\wscc-portal-streamlit\wscc_data.db`
**Format:** Plain SQLite database (unencrypted)
**Risk Level:** Medium - Anyone with file system access can read the database

---

## Option 1: Database Encryption with SQLCipher (RECOMMENDED)

### What It Provides
- Industry-standard AES-256 encryption
- Password-protected database
- Transparent to application (minimal code changes)
- Cannot be read without correct password

### Implementation Steps

1. **Install pysqlcipher3:**
```bash
pip install pysqlcipher3
```

2. **Modify database.py to use encrypted database:**

```python
# At the top of database.py, replace:
# import sqlite3
# with:
from pysqlcipher3 import dbapi2 as sqlite3

# Then modify get_connection():
def get_connection():
    """Get database connection with encryption"""
    conn = sqlite3.connect('wscc_data.db')

    # Set encryption password (CHANGE THIS!)
    conn.execute("PRAGMA key='your-strong-password-here'")

    # Optional: Enable additional security features
    conn.execute("PRAGMA cipher_compatibility = 4")

    return conn
```

3. **Migrate existing database:**
```bash
# Run this Python script once to encrypt existing data:
python migrate_to_encrypted.py
```

### Pros
- Strong encryption (AES-256)
- Minimal code changes
- Industry standard
- Password protection

### Cons
- Requires password management
- Slight performance overhead (~5-15%)
- Must remember password (no recovery)

---

## Option 2: File System Security (Medium Security)

### What It Provides
- Windows file permissions
- Protected directory location
- BitLocker encryption

### Implementation Steps

1. **Move database to protected location:**
```bash
# Create protected directory
mkdir C:\ProgramData\WSCC-Data

# Move database
move wscc_data.db C:\ProgramData\WSCC-Data\

# Update app.py DB_FILE path:
# DB_FILE = 'C:\\ProgramData\\WSCC-Data\\wscc_data.db'
```

2. **Set restrictive Windows permissions:**
```powershell
# Remove inheritance
icacls "C:\ProgramData\WSCC-Data" /inheritance:r

# Grant only your user full access
icacls "C:\ProgramData\WSCC-Data" /grant "%USERNAME%:(OI)(CI)F"

# Grant SYSTEM access (required)
icacls "C:\ProgramData\WSCC-Data" /grant "SYSTEM:(OI)(CI)F"
```

3. **Enable BitLocker (if available):**
   - Right-click C: drive → Turn on BitLocker
   - Follow Windows encryption wizard

### Pros
- No code changes required
- Uses Windows security features
- Works with existing backup tools

### Cons
- Only protects from other users on same computer
- No protection if computer is stolen (unless BitLocker enabled)
- Can be bypassed with admin privileges

---

## Option 3: Application Authentication (User Access Control)

### What It Provides
- User login system
- Role-based access control
- Audit logging

### Implementation Steps

1. **Install streamlit-authenticator:**
```bash
pip install streamlit-authenticator
```

2. **Add authentication to app.py:**

```python
import streamlit_authenticator as stauth

# At the top of main():
def main():
    # Authentication configuration
    names = ['Charles', 'Admin User']
    usernames = ['charles', 'admin']
    passwords = ['password123', 'admin123']  # CHANGE THESE!

    hashed_passwords = stauth.Hasher(passwords).generate()

    authenticator = stauth.Authenticate(
        names,
        usernames,
        hashed_passwords,
        'wscc_cookie',
        'wscc_key',
        cookie_expiry_days=30
    )

    name, authentication_status, username = authenticator.login('Login', 'main')

    if authentication_status:
        st.sidebar.success(f'Welcome {name}')
        authenticator.logout('Logout', 'sidebar')

        # Rest of your app code here
        # ...

    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')
```

### Pros
- Controls who can access the application
- Audit trail of who accessed what
- Multiple user support
- Session management

### Cons
- Database still unencrypted on disk
- Requires user management
- More complex implementation

---

## Option 4: Encrypted Backup Strategy (Complement to Other Options)

### What It Provides
- Automated encrypted backups
- Protection against data loss
- Offsite storage capability

### Implementation Steps

1. **Create backup script (backup_database.py):**

```python
import os
import shutil
import zipfile
from datetime import datetime
from cryptography.fernet import Fernet

# Generate key once and save it securely
# key = Fernet.generate_key()
# Save this key somewhere safe!

KEY = b'your-generated-key-here'  # Replace with actual key

def create_encrypted_backup():
    """Create encrypted database backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = 'C:\\Users\\Charles\\Documents\\WSCC-Backups'

    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)

    # Read database
    with open('wscc_data.db', 'rb') as f:
        data = f.read()

    # Encrypt
    cipher = Fernet(KEY)
    encrypted_data = cipher.encrypt(data)

    # Save encrypted backup
    backup_file = os.path.join(backup_dir, f'wscc_backup_{timestamp}.enc')
    with open(backup_file, 'wb') as f:
        f.write(encrypted_data)

    print(f'Encrypted backup created: {backup_file}')

    # Keep only last 7 backups
    cleanup_old_backups(backup_dir, keep=7)

def cleanup_old_backups(backup_dir, keep=7):
    """Remove old backups, keep only most recent"""
    backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.enc')])
    if len(backups) > keep:
        for old_backup in backups[:-keep]:
            os.remove(os.path.join(backup_dir, old_backup))
            print(f'Removed old backup: {old_backup}')

if __name__ == '__main__':
    create_encrypted_backup()
```

2. **Schedule automatic backups:**
   - Use Windows Task Scheduler to run daily
   - Or add to Streamlit app as background task

### Pros
- Protects against data loss
- Encrypted backups
- Automated process
- Version history

### Cons
- Requires key management
- Uses disk space
- Needs regular monitoring

---

## Comparison Matrix

| Feature | SQLCipher | File Permissions | App Authentication | Encrypted Backups |
|---------|-----------|------------------|-------------------|-------------------|
| **Encryption at Rest** | ✅ Yes | ❌ No (unless BitLocker) | ❌ No | ✅ Yes (backups) |
| **Access Control** | ✅ Yes (password) | ✅ Yes (OS-level) | ✅ Yes (users) | ❌ No |
| **Ease of Implementation** | Medium | Easy | Hard | Medium |
| **Code Changes Required** | Minimal | None | Extensive | None |
| **Performance Impact** | Low (5-15%) | None | None | None |
| **Recovery Options** | ❌ No (if password lost) | ✅ Yes | ✅ Yes | ✅ Yes |
| **Multi-User Support** | ❌ No | ❌ No | ✅ Yes | N/A |
| **Protection Level** | High | Medium | Medium | High (backups) |

---

## Recommended Approach

### For Maximum Security (Recommended)
**Combine Options 1 + 4:**
1. Encrypt database with SQLCipher
2. Implement automated encrypted backups
3. Store backups on separate drive or cloud storage

**Effort:** 1-2 hours
**Security Level:** High

### For Quick Implementation
**Use Option 2 (File Permissions):**
1. Move database to protected directory
2. Set restrictive permissions
3. Enable BitLocker if available

**Effort:** 15 minutes
**Security Level:** Medium

### For Multi-User Environment
**Combine Options 1 + 3 + 4:**
1. Encrypt database
2. Add user authentication
3. Implement backups

**Effort:** 3-4 hours
**Security Level:** Very High

---

## Migration Scripts

### Script 1: Migrate to SQLCipher (migrate_to_encrypted.py)

```python
import sqlite3
from pysqlcipher3 import dbapi2 as sqlcipher

def migrate_to_encrypted():
    """Migrate existing database to encrypted version"""

    # Backup original
    import shutil
    shutil.copy('wscc_data.db', 'wscc_data_backup_unencrypted.db')
    print('Backup created: wscc_data_backup_unencrypted.db')

    # Read all data from old database
    old_conn = sqlite3.connect('wscc_data.db')

    # Create new encrypted database
    new_conn = sqlcipher.connect('wscc_data_encrypted.db')
    new_conn.execute("PRAGMA key='your-strong-password-here'")  # CHANGE THIS!
    new_conn.execute("PRAGMA cipher_compatibility = 4")

    # Copy schema and data
    for line in old_conn.iterdump():
        new_conn.execute(line)

    new_conn.commit()
    old_conn.close()
    new_conn.close()

    print('Migration complete!')
    print('1. Test new database: wscc_data_encrypted.db')
    print('2. If working, rename: wscc_data_encrypted.db -> wscc_data.db')
    print('3. Keep backup: wscc_data_backup_unencrypted.db')

if __name__ == '__main__':
    migrate_to_encrypted()
```

### Script 2: Restore from Encrypted Backup (restore_backup.py)

```python
from cryptography.fernet import Fernet

def restore_backup(backup_file, key):
    """Restore database from encrypted backup"""

    # Read encrypted backup
    with open(backup_file, 'rb') as f:
        encrypted_data = f.read()

    # Decrypt
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(encrypted_data)

    # Write to database file
    with open('wscc_data.db', 'wb') as f:
        f.write(decrypted_data)

    print('Database restored successfully!')

if __name__ == '__main__':
    KEY = b'your-generated-key-here'  # Replace with your actual key
    backup_file = input('Enter backup file path: ')
    restore_backup(backup_file, KEY)
```

---

## Next Steps

Choose your security level and let me know which option(s) you want to implement. I can:

1. Install required packages
2. Create migration scripts
3. Update database.py for encryption
4. Set up automated backups
5. Configure file permissions

**No admin privileges are required for any of these options.**
