"""
Setup Authentication
Run this once to create user accounts with hashed passwords
"""

import streamlit_authenticator as stauth
import yaml
from pathlib import Path

def create_auth_config():
    """Create authentication configuration file with hashed passwords"""

    print('=' * 70)
    print('WSCC Authentication Setup')
    print('=' * 70)
    print()

    # Default users (you can modify these)
    users = []

    print('Create user accounts:')
    print('(Press Enter with blank username to finish)\n')

    while True:
        username = input('Username (or Enter to finish): ').strip()
        if not username:
            break

        name = input('Full Name: ').strip()
        password = input('Password: ').strip()

        users.append({
            'username': username,
            'name': name,
            'password': password
        })

        print(f'User "{username}" added\n')

    if not users:
        print('Creating default admin user...')
        users = [{
            'username': 'admin',
            'name': 'Administrator',
            'password': 'wscc2024'  # CHANGE THIS!
        }]
        print('WARNING: Default user created: admin / wscc2024')
        print('WARNING: IMPORTANT: Change this password after first login!\n')

    # Hash passwords
    print('Hashing passwords...')
    usernames = [user['username'] for user in users]
    names = [user['name'] for user in users]
    passwords = [user['password'] for user in users]

    # Use the newer API for streamlit-authenticator 0.4.x
    hasher = stauth.Hasher()
    hashed_passwords = [hasher.hash(password) for password in passwords]

    # Create config structure
    config = {
        'credentials': {
            'usernames': {}
        },
        'cookie': {
            'name': 'wscc_auth_cookie',
            'key': 'wscc_secret_key_12345',  # Change this to a random string
            'expiry_days': 30
        },
        'preauthorized': {
            'emails': []
        }
    }

    # Add users to config
    for username, name, hashed_password in zip(usernames, names, hashed_passwords):
        config['credentials']['usernames'][username] = {
            'name': name,
            'password': hashed_password
        }

    # Save to YAML file
    config_file = Path('auth_config.yaml')
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f'SUCCESS: Configuration saved to: {config_file}')
    print()
    print('User accounts created:')
    for user in users:
        print(f'  - Username: {user["username"]}, Name: {user["name"]}')
    print()
    print('=' * 70)
    print('Setup complete! You can now run the application.')
    print('=' * 70)

if __name__ == '__main__':
    create_auth_config()
