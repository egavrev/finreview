#!/usr/bin/env python3
"""
Test script to verify PDF delete functionality.
"""

import requests
import tempfile
import shutil
from pathlib import Path
import json


def test_delete_functionality():
    """Test the PDF delete functionality."""
    
    API_BASE = "http://localhost:8000"
    
    print("Testing PDF Delete Functionality...")
    print("=" * 50)
    
    # First, let's check what PDFs exist
    print("1. Checking existing PDFs...")
    try:
        response = requests.get(f"{API_BASE}/pdfs")
        if response.status_code == 200:
            pdfs = response.json()
            print(f"   Found {len(pdfs)} existing PDFs")
            for pdf in pdfs:
                print(f"   - ID: {pdf['id']}, File: {pdf['file_path']}")
        else:
            print(f"   Failed to get PDFs: {response.status_code}")
            return
    except Exception as e:
        print(f"   Error getting PDFs: {e}")
        return
    
    if not pdfs:
        print("   No PDFs to test deletion with. Please upload some PDFs first.")
        return
    
    # Test with the first PDF
    test_pdf = pdfs[0]
    pdf_id = test_pdf['id']
    
    print(f"\n2. Testing deletion of PDF ID {pdf_id}...")
    print(f"   File: {test_pdf['file_path']}")
    print(f"   Client: {test_pdf['client_name']}")
    
    # Get operations count before deletion
    print(f"\n3. Checking operations before deletion...")
    try:
        response = requests.get(f"{API_BASE}/pdfs/{pdf_id}")
        if response.status_code == 200:
            pdf_details = response.json()
            operations_count = len(pdf_details['operations'])
            print(f"   Operations associated with this PDF: {operations_count}")
        else:
            print(f"   Failed to get PDF details: {response.status_code}")
            operations_count = "unknown"
    except Exception as e:
        print(f"   Error getting PDF details: {e}")
        operations_count = "unknown"
    
    # Confirm deletion
    print(f"\n4. Proceeding with deletion...")
    confirm = input("   Are you sure you want to delete this PDF? (yes/no): ")
    if confirm.lower() != 'yes':
        print("   Deletion cancelled.")
        return
    
    # Delete the PDF
    try:
        response = requests.delete(f"{API_BASE}/pdfs/{pdf_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Delete successful!")
            print(f"   Message: {result['message']}")
            print(f"   Operations deleted: {result['operations_deleted']}")
        else:
            print(f"   ❌ Delete failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error during deletion: {e}")
        return
    
    # Verify deletion
    print(f"\n5. Verifying deletion...")
    try:
        response = requests.get(f"{API_BASE}/pdfs/{pdf_id}")
        if response.status_code == 404:
            print(f"   ✅ PDF successfully deleted (404 Not Found)")
        else:
            print(f"   ⚠️  PDF still exists (Status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ Error verifying deletion: {e}")
    
    # Check remaining PDFs
    print(f"\n6. Checking remaining PDFs...")
    try:
        response = requests.get(f"{API_BASE}/pdfs")
        if response.status_code == 200:
            remaining_pdfs = response.json()
            print(f"   Remaining PDFs: {len(remaining_pdfs)}")
            if len(remaining_pdfs) < len(pdfs):
                print(f"   ✅ PDF count reduced by {len(pdfs) - len(remaining_pdfs)}")
            else:
                print(f"   ⚠️  PDF count unchanged")
        else:
            print(f"   Failed to get remaining PDFs: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting remaining PDFs: {e}")
    
    print(f"\n" + "=" * 50)
    print("Delete functionality test completed!")


if __name__ == "__main__":
    test_delete_functionality()
