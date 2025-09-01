#!/usr/bin/env python3
"""
Test script to verify web API deduplication functionality.
"""

import requests
import tempfile
import shutil
from pathlib import Path
import json


def test_web_deduplication():
    """Test the web API deduplication functionality."""
    
    API_BASE = "http://localhost:8000"
    
    print("Testing Web API Deduplication...")
    print("=" * 50)
    
    # Test with sample PDFs
    pdf_examples = [
        "PDF_examples/document.pdf",
        "PDF_examples/August 2025-to-process.pdf"
    ]
    
    total_stored = 0
    total_skipped = 0
    
    for i, pdf_path in enumerate(pdf_examples):
        if Path(pdf_path).exists():
            print(f"\nTest {i+1}: Uploading {pdf_path}")
            
            # Upload PDF via web API
            with open(pdf_path, 'rb') as f:
                files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
                response = requests.post(f"{API_BASE}/upload-pdf", files=files)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Upload successful")
                print(f"  📊 Operations stored: {result['operations_stored']}")
                print(f"  ⚠️  Operations skipped (duplicates): {result['operations_skipped']}")
                print(f"  📈 Total processed: {result['total_operations_processed']}")
                
                if result['deduplication_info']['duplicates_found']:
                    print(f"  🔍 Duplicate percentage: {result['deduplication_info']['duplicate_percentage']:.1f}%")
                
                total_stored += result['operations_stored']
                total_skipped += result['operations_skipped']
                
                # Show PDF summary if available
                if result.get('pdf_summary'):
                    summary = result['pdf_summary']
                    print(f"  📄 PDF Summary:")
                    print(f"     Client: {summary.get('client_name', 'N/A')}")
                    print(f"     Account: {summary.get('account_number', 'N/A')}")
                    print(f"     Initial Balance: {summary.get('sold_initial', 'N/A')} LEI")
                    print(f"     Final Balance: {summary.get('sold_final', 'N/A')} LEI")
            else:
                print(f"  ❌ Upload failed: {response.status_code}")
                print(f"     Error: {response.text}")
        else:
            print(f"  ⚠️  PDF not found: {pdf_path}")
    
    print(f"\n" + "=" * 50)
    print(f"Summary:")
    print(f"  Total operations stored: {total_stored}")
    print(f"  Total operations skipped: {total_skipped}")
    print(f"  Deduplication rate: {total_skipped / (total_stored + total_skipped) * 100:.1f}%" if (total_stored + total_skipped) > 0 else "  No operations processed")
    
    # Test deduplication stats endpoint
    print(f"\n" + "=" * 50)
    print("Testing Deduplication Stats Endpoint...")
    
    try:
        response = requests.get(f"{API_BASE}/deduplication-stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"  📊 Deduplication Statistics:")
            print(f"     Total operations: {stats['total_operations']}")
            print(f"     Operations with hashes: {stats['operations_with_hashes']}")
            print(f"     Operations without hashes: {stats['operations_without_hashes']}")
            print(f"     Duplicate pairs: {stats['duplicate_pairs']}")
            print(f"     Hash coverage: {stats['hash_coverage_percentage']:.1f}%")
            print(f"     Duplicate percentage: {stats['duplicate_percentage']:.1f}%")
        else:
            print(f"  ❌ Failed to get stats: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error getting stats: {e}")
    
    # Test duplicates endpoint
    print(f"\n" + "=" * 50)
    print("Testing Duplicates Endpoint...")
    
    try:
        response = requests.get(f"{API_BASE}/duplicates")
        if response.status_code == 200:
            duplicates = response.json()
            print(f"  🔍 Found {duplicates['duplicate_pairs']} duplicate pairs")
            
            if duplicates['duplicate_pairs'] > 0:
                print(f"  📋 Sample duplicates:")
                for i, dup in enumerate(duplicates['duplicates'][:3]):  # Show first 3
                    op1 = dup['operation1']
                    op2 = dup['operation2']
                    print(f"     Pair {i+1}:")
                    print(f"       Operation 1: {op1['description']} ({op1['amount_lei']} LEI)")
                    print(f"       Operation 2: {op2['description']} ({op2['amount_lei']} LEI)")
                    print(f"       Hash: {op1['operation_hash'][:16]}...")
        else:
            print(f"  ❌ Failed to get duplicates: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error getting duplicates: {e}")


if __name__ == "__main__":
    test_web_deduplication()
