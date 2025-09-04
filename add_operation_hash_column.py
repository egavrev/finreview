#!/usr/bin/env python3
"""
Simple script to add the missing operation_hash column to the operationrow table.
"""

import sqlite3
from pathlib import Path

def add_operation_hash_column():
    db_path = Path("db.sqlite")
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(operationrow)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'operation_hash' not in columns:
            print("Adding operation_hash column to operationrow table...")
            cursor.execute("ALTER TABLE operationrow ADD COLUMN operation_hash VARCHAR")
            
            # Update existing records with generated hashes
            print("Generating hashes for existing operations...")
            cursor.execute("SELECT id, transaction_date, description, amount_lei FROM operationrow")
            operations = cursor.fetchall()
            
            for op_id, transaction_date, description, amount_lei in operations:
                # Generate a simple hash (similar to the one in sql_utils.py)
                import hashlib
                hash_string = f"{transaction_date}|{description}|{amount_lei}"
                operation_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
                
                cursor.execute(
                    "UPDATE operationrow SET operation_hash = ? WHERE id = ?",
                    (operation_hash, op_id)
                )
            
            conn.commit()
            print(f"Successfully added operation_hash column and populated {len(operations)} operations")
        else:
            print("operation_hash column already exists")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_operation_hash_column()
