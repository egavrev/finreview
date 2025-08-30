#!/usr/bin/env python3
"""
Test script to verify the operations page functionality
"""

import requests
import json

def test_operations_endpoints():
    """Test the operations endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing operations endpoints...")
    
    # Test getting operations with null types
    try:
        response = requests.get(f"{base_url}/operations/null-types")
        if response.status_code == 200:
            operations = response.json()
            print(f"✓ Found {len(operations)} operations with null types")
            if operations:
                print(f"  Sample operation: {operations[0]}")
        else:
            print(f"✗ Failed to get operations: {response.status_code}")
    except Exception as e:
        print(f"✗ Error getting operations: {e}")
    
    # Test getting operation types
    try:
        response = requests.get(f"{base_url}/operation-types")
        if response.status_code == 200:
            types = response.json()
            print(f"✓ Found {len(types)} operation types")
            if types:
                print(f"  Sample type: {types[0]}")
        else:
            print(f"✗ Failed to get operation types: {response.status_code}")
    except Exception as e:
        print(f"✗ Error getting operation types: {e}")
    
    # Test creating a new operation type
    try:
        data = {
            "name": "Test Type",
            "description": "Test description"
        }
        response = requests.post(f"{base_url}/operation-types", data=data)
        if response.status_code == 200:
            new_type = response.json()
            print(f"✓ Created new operation type: {new_type['name']} (ID: {new_type['id']})")
            
            # Test assigning type to an operation
            if operations:
                operation_id = operations[0]['id']
                assign_data = {"type_id": new_type['id']}
                response = requests.post(f"{base_url}/operations/{operation_id}/assign-type", data=assign_data)
                if response.status_code == 200:
                    print(f"✓ Successfully assigned type to operation {operation_id}")
                else:
                    print(f"✗ Failed to assign type: {response.status_code}")
        else:
            print(f"✗ Failed to create operation type: {response.status_code}")
    except Exception as e:
        print(f"✗ Error creating operation type: {e}")

if __name__ == "__main__":
    test_operations_endpoints()
