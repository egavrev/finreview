#!/usr/bin/env python3
"""
Test script for operation types functionality
"""

from sql_utils import (
    get_engine, init_db, create_operation_type, get_operation_types,
    get_operation_type_by_name, assign_operation_type, get_operations_by_type,
    get_operations_with_types
)
from sqlmodel import Session

def test_operation_types():
    """Test the operation types functionality"""
    engine = get_engine("db.sqlite")
    init_db(engine)
    
    with Session(engine) as session:
        print("Testing operation types functionality...")
        
        # Test creating operation types
        print("\n1. Creating operation types...")
        type1 = create_operation_type(session, "Test Type 1", "Test description 1")
        type2 = create_operation_type(session, "Test Type 2", "Test description 2")
        print(f"Created types: {type1.name}, {type2.name}")
        
        # Test getting all types
        print("\n2. Getting all operation types...")
        types = get_operation_types(session)
        print(f"Found {len(types)} types:")
        for t in types:
            print(f"  - {t.name}: {t.description}")
        
        # Test getting type by name
        print("\n3. Getting type by name...")
        found_type = get_operation_type_by_name(session, "Test Type 1")
        if found_type:
            print(f"Found type: {found_type.name} (ID: {found_type.id})")
        
        # Test getting operations with types (should be empty initially)
        print("\n4. Getting operations with types...")
        operations_with_types = get_operations_with_types(session)
        print(f"Found {len(operations_with_types)} operations with types")
        
        print("\nOperation types functionality test completed!")

if __name__ == "__main__":
    test_operation_types()
