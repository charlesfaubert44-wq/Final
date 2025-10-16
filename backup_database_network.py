"""
WSCC Database Backup Tool with Network Redundancy
Backs up to both local and network storage drives
"""

import os
import shutil
from datetime import datetime
from cryptography.fernet import Fernet
import json

# ==============================================================================
# CONFIGURATION - Edit these settings
# ==============================================================================

# Backup encryption key (generate once with: print(Fernet.generate_key()))
# IMPORTANT: Save this key securely! Without it, backups cannot be restored.
BACKUP_KEY = b'your-generated-key-here'  # Replace with your actual key

# Local backup location
LOCAL_BACKUP_DIR = r'C:\Users\Charles\Documents\WSCC-Backups'

# Network backup locations (can add multiple)
NETWORK_BACKUP_DIRS = [
    r'\\server\share\WSCC-Backups',  # UNC path example
    r'Z:\WSCC-Backups',               # Mapped drive example
    # Add more network locations as needed
]

# How many backups to keep (per location)
KEEP_BACKUPS = 7

# Database file location
DATABASE_FILE = 'wscc_data.db'

# ==============================================================================
# Backup Functions
# ==============================================================================

def generate_key():
    """Generate a new encryption key (run once)"""
    key = Fernet.generate_key()
    print('Generated encryption key:')
    print(key)
    print('\n⚠️  SAVE THIS KEY SECURELY!')
    print('Copy it to BACKUP_KEY in this file.')
    return key

def check_network_drive_available(path):
    """Check if network drive is accessible"""
    try:
        # Try to create directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        # Try to write a test file
        test_file = os.path.join(path, '.wscc_backup_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except Exception as e:
        return False

def get_available_backup_locations():
    """Get list of available backup locations (local + accessible network)"""
    locations = []

    # Add local location
    try:
        os.makedirs(LOCAL_BACKUP_DIR, exist_ok=True)
        locations.append(('Local', LOCAL_BACKUP_DIR))
        print(f'✅ Local backup: {LOCAL_BACKUP_DIR}')
    except Exception as e:
        print(f'❌ Local backup unavailable: {e}')

    # Check network locations
    for network_path in NETWORK_BACKUP_DIRS:
        if check_network_drive_available(network_path):
            locations.append(('Network', network_path))
            print(f'✅ Network backup: {network_path}')
        else:
            print(f'⚠️  Network backup unavailable: {network_path}')

    return locations

def create_backup_metadata(backup_file):
    """Create metadata file for backup"""
    metadata = {
        'backup_date': datetime.now().isoformat(),
        'database_file': DATABASE_FILE,
        'file_size': os.path.getsize(DATABASE_FILE),
        'encrypted': True,
        'version': '1.0'
    }

    metadata_file = backup_file.replace('.enc', '.json')
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    return metadata_file

def create_encrypted_backup():
    """Create encrypted database backup in all available locations"""

    print('\n' + '=' * 70)
    print('WSCC Database Backup - Network Redundancy')
    print('=' * 70)

    # Check if database exists
    if not os.path.exists(DATABASE_FILE):
        print(f'❌ Database file not found: {DATABASE_FILE}')
        return False

    # Get database info
    db_size = os.path.getsize(DATABASE_FILE)
    db_size_kb = db_size / 1024
    print(f'\n📊 Database size: {db_size_kb:.1f} KB')

    # Get available backup locations
    print('\n🔍 Checking backup locations...')
    locations = get_available_backup_locations()

    if not locations:
        print('\n❌ No backup locations available!')
        return False

    print(f'\n✅ Found {len(locations)} available backup location(s)')

    # Read database
    print(f'\n📖 Reading database: {DATABASE_FILE}')
    with open(DATABASE_FILE, 'rb') as f:
        data = f.read()

    # Encrypt data
    print('🔐 Encrypting backup...')
    cipher = Fernet(BACKUP_KEY)
    encrypted_data = cipher.encrypt(data)
    encrypted_size_kb = len(encrypted_data) / 1024
    print(f'✅ Encrypted size: {encrypted_size_kb:.1f} KB')

    # Create timestamp for filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'wscc_backup_{timestamp}.enc'

    # Save to all available locations
    print('\n💾 Saving encrypted backups...')
    success_count = 0
    failed_locations = []

    for location_type, location_path in locations:
        try:
            backup_file = os.path.join(location_path, backup_filename)

            # Save encrypted backup
            with open(backup_file, 'wb') as f:
                f.write(encrypted_data)

            # Create metadata file
            metadata_file = create_backup_metadata(backup_file)

            # Verify backup was written correctly
            if os.path.exists(backup_file):
                saved_size = os.path.getsize(backup_file)
                saved_size_kb = saved_size / 1024
                print(f'  ✅ {location_type}: {backup_file} ({saved_size_kb:.1f} KB)')
                success_count += 1

                # Cleanup old backups in this location
                cleanup_old_backups(location_path, KEEP_BACKUPS)
            else:
                failed_locations.append(f'{location_type}: {location_path}')
                print(f'  ❌ {location_type}: Failed to verify backup')

        except Exception as e:
            failed_locations.append(f'{location_type}: {location_path}')
            print(f'  ❌ {location_type}: {e}')

    # Summary
    print('\n' + '=' * 70)
    if success_count == len(locations):
        print('✅ SUCCESS: All backups completed successfully!')
    elif success_count > 0:
        print(f'⚠️  PARTIAL SUCCESS: {success_count}/{len(locations)} backups completed')
    else:
        print('❌ FAILURE: No backups were successful')

    if failed_locations:
        print('\n❌ Failed locations:')
        for loc in failed_locations:
            print(f'  - {loc}')

    print(f'\n📦 Backup file: {backup_filename}')
    print(f'🕐 Timestamp: {datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")}')
    print('=' * 70)

    return success_count > 0

def cleanup_old_backups(backup_dir, keep=7):
    """Remove old backups, keeping only the most recent ones"""
    try:
        # Get all backup files
        backups = sorted([
            f for f in os.listdir(backup_dir)
            if f.startswith('wscc_backup_') and f.endswith('.enc')
        ])

        if len(backups) > keep:
            removed_count = 0
            for old_backup in backups[:-keep]:
                old_path = os.path.join(backup_dir, old_backup)
                metadata_path = old_path.replace('.enc', '.json')

                # Remove backup file
                os.remove(old_path)
                # Remove metadata file if exists
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)

                removed_count += 1

            if removed_count > 0:
                print(f'    🗑️  Removed {removed_count} old backup(s)')
    except Exception as e:
        print(f'    ⚠️  Cleanup warning: {e}')

def list_available_backups():
    """List all available backups from all locations"""
    print('\n' + '=' * 70)
    print('Available Backups')
    print('=' * 70)

    locations = get_available_backup_locations()

    if not locations:
        print('\n❌ No backup locations accessible')
        return []

    all_backups = []

    for location_type, location_path in locations:
        try:
            backups = sorted([
                f for f in os.listdir(location_path)
                if f.startswith('wscc_backup_') and f.endswith('.enc')
            ], reverse=True)

            if backups:
                print(f'\n📁 {location_type}: {location_path}')
                print(f'   Found {len(backups)} backup(s):')

                for i, backup in enumerate(backups, 1):
                    backup_path = os.path.join(location_path, backup)
                    size = os.path.getsize(backup_path) / 1024

                    # Parse timestamp from filename
                    timestamp_str = backup.replace('wscc_backup_', '').replace('.enc', '')
                    try:
                        dt = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        date_str = dt.strftime('%Y-%m-%d %I:%M:%S %p')
                    except:
                        date_str = timestamp_str

                    print(f'   {i}. {backup}')
                    print(f'      Date: {date_str} | Size: {size:.1f} KB')

                    all_backups.append((location_type, backup_path, backup, date_str, size))
            else:
                print(f'\n📁 {location_type}: {location_path}')
                print(f'   No backups found')

        except Exception as e:
            print(f'\n📁 {location_type}: {location_path}')
            print(f'   Error: {e}')

    print('\n' + '=' * 70)
    return all_backups

def restore_backup(backup_file):
    """Restore database from encrypted backup"""
    print('\n' + '=' * 70)
    print('WSCC Database Restore')
    print('=' * 70)

    # Check if backup exists
    if not os.path.exists(backup_file):
        print(f'\n❌ Backup file not found: {backup_file}')
        return False

    backup_size = os.path.getsize(backup_file) / 1024
    print(f'\n📦 Backup file: {backup_file}')
    print(f'📊 Backup size: {backup_size:.1f} KB')

    # Safety: backup current database first
    if os.path.exists(DATABASE_FILE):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safety_backup = f'wscc_data_before_restore_{timestamp}.db'
        shutil.copy(DATABASE_FILE, safety_backup)
        safety_size = os.path.getsize(safety_backup) / 1024
        print(f'\n✅ Current database backed up: {safety_backup} ({safety_size:.1f} KB)')

    try:
        # Read encrypted backup
        print('\n📖 Reading encrypted backup...')
        with open(backup_file, 'rb') as f:
            encrypted_data = f.read()

        # Decrypt
        print('🔓 Decrypting backup...')
        cipher = Fernet(BACKUP_KEY)
        decrypted_data = cipher.decrypt(encrypted_data)
        decrypted_size = len(decrypted_data) / 1024
        print(f'✅ Decrypted size: {decrypted_size:.1f} KB')

        # Write to database file
        print(f'\n💾 Writing to: {DATABASE_FILE}')
        with open(DATABASE_FILE, 'wb') as f:
            f.write(decrypted_data)

        # Verify
        if os.path.exists(DATABASE_FILE):
            final_size = os.path.getsize(DATABASE_FILE) / 1024
            print(f'✅ Database restored: {DATABASE_FILE} ({final_size:.1f} KB)')
            print('\n' + '=' * 70)
            print('✅ SUCCESS: Database restored successfully!')
            print('=' * 70)
            print('\n⚠️  IMPORTANT: Restart the Streamlit application to load restored data')
            return True
        else:
            print('\n❌ FAILURE: Database file not found after restore')
            return False

    except Exception as e:
        print(f'\n❌ FAILURE: {e}')
        print('\nPossible causes:')
        print('  - Wrong encryption key (BACKUP_KEY)')
        print('  - Corrupted backup file')
        print('  - Insufficient disk space')
        return False

def configure_network_drives():
    """Interactive configuration for network drives"""
    print('\n' + '=' * 70)
    print('Network Drive Configuration')
    print('=' * 70)

    print('\nCurrent network backup locations:')
    if not NETWORK_BACKUP_DIRS:
        print('  (none configured)')
    else:
        for i, path in enumerate(NETWORK_BACKUP_DIRS, 1):
            status = '✅ Available' if check_network_drive_available(path) else '❌ Unavailable'
            print(f'  {i}. {path} - {status}')

    print('\nHow to add network backup locations:')
    print('  1. Edit this file: backup_database_network.py')
    print('  2. Find NETWORK_BACKUP_DIRS list (around line 21)')
    print('  3. Add your network paths:')
    print('     - UNC path: r"\\\\server\\share\\WSCC-Backups"')
    print('     - Mapped drive: r"Z:\\WSCC-Backups"')
    print('     - Network share: r"\\\\192.168.1.100\\backups\\WSCC"')
    print('\nExamples:')
    print('  NETWORK_BACKUP_DIRS = [')
    print('      r"\\\\wscc-server\\shared\\Backups\\WSCC",  # UNC path')
    print('      r"Z:\\WSCC-Backups",                      # Mapped network drive')
    print('      r"\\\\192.168.86.50\\backups\\WSCC",      # IP-based UNC')
    print('  ]')

# ==============================================================================
# Main Menu
# ==============================================================================

def main():
    """Main menu"""
    print('\n' + '=' * 70)
    print('WSCC Database Backup Tool - Network Redundancy Edition')
    print('=' * 70)

    while True:
        print('\nOptions:')
        print('  1. Create backup (local + network)')
        print('  2. List available backups')
        print('  3. Restore from backup')
        print('  4. Configure network drives')
        print('  5. Generate encryption key')
        print('  6. Test backup locations')
        print('  0. Exit')

        choice = input('\nChoice: ').strip()

        if choice == '1':
            create_encrypted_backup()
            input('\nPress Enter to continue...')

        elif choice == '2':
            list_available_backups()
            input('\nPress Enter to continue...')

        elif choice == '3':
            backups = list_available_backups()
            if backups:
                backup_path = input('\nEnter full path to backup file: ').strip()
                if backup_path:
                    restore_backup(backup_path)
            input('\nPress Enter to continue...')

        elif choice == '4':
            configure_network_drives()
            input('\nPress Enter to continue...')

        elif choice == '5':
            generate_key()
            input('\nPress Enter to continue...')

        elif choice == '6':
            get_available_backup_locations()
            input('\nPress Enter to continue...')

        elif choice == '0':
            print('\nGoodbye!')
            break

        else:
            print('\n❌ Invalid choice')

if __name__ == '__main__':
    # Check if encryption key is configured
    if BACKUP_KEY == b'your-generated-key-here':
        print('\n⚠️  WARNING: Encryption key not configured!')
        print('\nPlease run option 5 to generate a key, then update BACKUP_KEY in this file.')
        print('Or press Enter to continue anyway (backups will fail)...')
        input()

    main()
