#!/usr/bin/env python3
"""
Script to copy operations from root db.sqlite to api/db.sqlite
"""

import sqlite3
from pathlib import Path

def copy_operations():
    root_db = Path("db.sqlite")
    api_db = Path("api/db.sqlite")
    
    if not root_db.exists():
        print("Root database not found!")
        return
    
    if not api_db.exists():
        print("API database not found!")
        return
    
    # Connect to both databases
    root_conn = sqlite3.connect(root_db)
    api_conn = sqlite3.connect(api_db)
    
    try:
        # Get operations from root database
        root_cursor = root_conn.cursor()
        root_cursor.execute("SELECT id, pdf_id, type_id, transaction_date, processed_date, description, amount_lei, operation_hash FROM operationrow")
        operations = root_cursor.fetchall()
        
        print(f"Found {len(operations)} operations in root database")
        
        if len(operations) == 0:
            print("No operations to copy")
            return
        
        # Copy operations to API database
        api_cursor = api_conn.cursor()
        
        # First, check if operationrow table exists in API database
        api_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operationrow'")
        if not api_cursor.fetchone():
            print("Creating operationrow table in API database...")
            # Create the table structure
            api_cursor.execute("""
                CREATE TABLE operationrow (
                    id INTEGER NOT NULL,
                    pdf_id INTEGER NOT NULL,
                    type_id INTEGER,
                    transaction_date VARCHAR,
                    processed_date VARCHAR,
                    description VARCHAR,
                    amount_lei FLOAT,
                    operation_hash VARCHAR,
                    PRIMARY KEY (id),
                    FOREIGN KEY (pdf_id) REFERENCES pdf (id),
                    FOREIGN KEY (type_id) REFERENCES operationtype (id)
                )
            """)
        
        # Copy each operation
        copied_count = 0
        for op in operations:
            try:
                api_cursor.execute("""
                    INSERT INTO operationrow (id, pdf_id, type_id, transaction_date, processed_date, description, amount_lei, operation_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, op)
                copied_count += 1
            except sqlite3.IntegrityError as e:
                print(f"Error copying operation {op[0]}: {e}")
                continue
        
        # Also copy PDF and operation type tables
        print("Copying PDF table...")
        root_cursor.execute("SELECT * FROM pdf")
        pdfs = root_cursor.fetchall()
        for pdf in pdfs:
            try:
                api_cursor.execute("INSERT INTO pdf VALUES (?, ?, ?, ?, ?, ?, ?, ?)", pdf)
            except sqlite3.IntegrityError:
                pass  # Already exists
        
        print("Copying operationtype table...")
        root_cursor.execute("SELECT * FROM operationtype")
        types = root_cursor.fetchall()
        for op_type in types:
            try:
                api_cursor.execute("INSERT INTO operationtype VALUES (?, ?, ?, ?)", op_type)
            except sqlite3.IntegrityError:
                pass  # Already exists
        
        api_conn.commit()
        print(f"Successfully copied {copied_count} operations to API database")
        
    except Exception as e:
        print(f"Error: {e}")
        api_conn.rollback()
    finally:
        root_conn.close()
        api_conn.close()

if __name__ == "__main__":
    copy_operations()
