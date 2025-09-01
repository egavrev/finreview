#!/usr/bin/env python3
"""
Test script for hash-based deduplication functionality.
"""

import tempfile
import shutil
from pathlib import Path
from sql_utils import (
    get_engine, 
    init_db, 
    process_and_store, 
    process_and_store_with_classification,
    get_operations_for_pdf,
    Session
)


def test_deduplication():
    """Test the deduplication functionality with sample PDFs."""
    
    # Create a temporary database
    with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        print("Testing hash-based deduplication...")
        print(f"Using temporary database: {db_path}")
        
        # Initialize database
        engine = get_engine(db_path)
        init_db(engine)
        
        # Test with the sample PDFs
        pdf_examples = [
            "PDF_examples/document.pdf",
            "PDF_examples/August 2025-to-process.pdf"
        ]
        
        total_stored = 0
        total_skipped = 0
        
        for pdf_path in pdf_examples:
            if Path(pdf_path).exists():
                print(f"\nProcessing: {pdf_path}")
                
                # Process with deduplication enabled
                pdf_id, stored_count, skipped_count = process_and_store(
                    pdf_path, db_path, skip_duplicates=True
                )
                
                print(f"  PDF ID: {pdf_id}")
                print(f"  Operations stored: {stored_count}")
                print(f"  Operations skipped (duplicates): {skipped_count}")
                
                total_stored += stored_count
                total_skipped += skipped_count
                
                # Show some details about stored operations
                with Session(engine) as session:
                    operations = get_operations_for_pdf(session, pdf_id)
                    print(f"  Total operations in database for this PDF: {len(operations)}")
                    
                    # Show first few operations with their hashes
                    for i, op in enumerate(operations[:3]):
                        print(f"    Operation {i+1}: {op.description} (Hash: {op.operation_hash[:16]}...)")
            else:
                print(f"PDF not found: {pdf_path}")
        
        print(f"\nSummary:")
        print(f"  Total operations stored: {total_stored}")
        print(f"  Total operations skipped: {total_skipped}")
        print(f"  Deduplication rate: {total_skipped / (total_stored + total_skipped) * 100:.1f}%" if (total_stored + total_skipped) > 0 else "  No operations processed")
        
        # Test processing the same PDF again to see deduplication in action
        if pdf_examples[0] and Path(pdf_examples[0]).exists():
            print(f"\nRe-processing {pdf_examples[0]} to test deduplication...")
            pdf_id, stored_count, skipped_count = process_and_store(
                pdf_examples[0], db_path, skip_duplicates=True
            )
            print(f"  Operations stored: {stored_count}")
            print(f"  Operations skipped (duplicates): {skipped_count}")
            print(f"  Expected: Most operations should be skipped as duplicates")
        
    finally:
        # Clean up temporary database
        try:
            Path(db_path).unlink()
            print(f"\nCleaned up temporary database: {db_path}")
        except Exception as e:
            print(f"Warning: Could not clean up temporary database: {e}")


if __name__ == "__main__":
    test_deduplication()
