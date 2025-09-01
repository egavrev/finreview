#!/usr/bin/env python3
"""
Migration script to add hashes to existing operations in the database.
This script should be run once to migrate existing data to use the hash system.
"""

import sys
from pathlib import Path
from sql_utils import get_engine, init_db, migrate_existing_operations_to_hashes, Session


def migrate_database(db_path: str):
    """
    Migrate an existing database to use hash-based deduplication.
    
    Args:
        db_path: Path to the database file
    """
    print(f"Migrating database: {db_path}")
    
    # Check if database exists
    if not Path(db_path).exists():
        print(f"Error: Database file not found: {db_path}")
        return False
    
    try:
        # Initialize database engine
        engine = get_engine(db_path)
        init_db(engine)  # This will create the new hash column if it doesn't exist
        
        # Migrate existing operations
        with Session(engine) as session:
            updated_count = migrate_existing_operations_to_hashes(session)
            
            if updated_count > 0:
                print(f"Successfully migrated {updated_count} operations to use hash-based deduplication.")
            else:
                print("No operations needed migration (all operations already have hashes).")
        
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        return False


def main():
    """Main function to run the migration."""
    if len(sys.argv) != 2:
        print("Usage: python migrate_to_hashes.py <database_path>")
        print("Example: python migrate_to_hashes.py db.sqlite")
        sys.exit(1)
    
    db_path = sys.argv[1]
    
    print("Hash-based Deduplication Migration Tool")
    print("=" * 40)
    
    success = migrate_database(db_path)
    
    if success:
        print("\nMigration completed successfully!")
        print("\nYour database now supports hash-based deduplication.")
        print("New operations will automatically be checked for duplicates.")
    else:
        print("\nMigration failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
