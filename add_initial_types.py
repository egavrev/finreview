#!/usr/bin/env python3
"""
Script to add initial operation types to the database
"""

from sql_utils import get_engine, init_db, create_operation_type
from sqlmodel import Session

def main():
    """Add initial operation types"""
    engine = get_engine("db.sqlite")
    init_db(engine)
    
    with Session(engine) as session:
        # Define some common operation types
        initial_types = [
            ("Salary", "Salary payments and income"),
            ("Food", "Food and dining expenses"),
            ("Transport", "Transportation costs"),
            ("Shopping", "Shopping and retail purchases"),
            ("Bills", "Utility bills and services"),
            ("Entertainment", "Entertainment and leisure"),
            ("Healthcare", "Healthcare and medical expenses"),
            ("Education", "Education and training costs"),
            ("Travel", "Travel and vacation expenses"),
            ("Investment", "Investment and savings"),
            ("Other", "Other miscellaneous expenses"),
        ]
        
        for name, description in initial_types:
            try:
                create_operation_type(session, name, description)
                print(f"Created operation type: {name}")
            except Exception as e:
                print(f"Error creating {name}: {e}")
        
        print("Initial operation types added successfully!")

if __name__ == "__main__":
    main()
