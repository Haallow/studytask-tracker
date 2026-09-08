#!/usr/bin/env python
"""Verify MongoDB connection and indexes."""
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).resolve().parent / '.env')

# Add app to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import init_db, get_db, check_connection

def main():
    print("Initializing database connection...")
    try:
        init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        return 1
    
    print("\nChecking connection...")
    if check_connection():
        print("✓ MongoDB is connected")
    else:
        print("✗ MongoDB connection failed")
        return 1
    
    db = get_db()
    
    print("\nChecking indexes on 'users' collection...")
    users_indexes = list(db.users.list_indexes())
    print(f"Found {len(users_indexes)} indexes:")
    for idx in users_indexes:
        print(f"  - {idx['name']}: {idx['key']}")
        if 'unique' in idx and idx['unique']:
            print(f"    (unique)")
    
    # Check for email unique index
    email_idx = [idx for idx in users_indexes if 'email' in idx['key']]
    if email_idx and email_idx[0].get('unique'):
        print("✓ Unique index on users.email exists")
    else:
        print("✗ Unique index on users.email not found")
    
    print("\nChecking indexes on 'tasks' collection...")
    tasks_indexes = list(db.tasks.list_indexes())
    print(f"Found {len(tasks_indexes)} indexes:")
    for idx in tasks_indexes:
        print(f"  - {idx['name']}: {idx['key']}")
    
    # Check for user_id index
    user_id_idx = [idx for idx in tasks_indexes if 'user_id' in idx['key']]
    if user_id_idx:
        print("✓ Index on tasks.user_id exists")
    else:
        print("✗ Index on tasks.user_id not found")
    
    print("\n✓ All database checks passed!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
