#!/usr/bin/env python3
"""
Test script for operations matching functionality

This script demonstrates the hybrid rule-based classification system
for automatically classifying financial operations.
"""

import sys
from pathlib import Path
from sql_utils import (
    get_engine, init_db, Session,
    process_and_store_with_classification,
    get_classification_suggestions_for_pdf,
    auto_assign_high_confidence_operations,
    get_operations_with_types,
    get_operation_types
)
from operations_matcher import get_matcher, classify_operation


def test_single_operation_classification():
    """Test classification of individual operations"""
    print("=== Testing Single Operation Classification ===")
    
    # Test cases with different types of descriptions
    test_cases = [
        "AGROBAZAR",
        "LATTI FOODMART M",
        "FARMACIA FAMILIEI",
        "BE BEAUTY Salon",
        "MAIB ART TWIST SRL",
        "IURALEX COM SRL",
        "EA STUDIO FIT SRL",
        "OPENAI",
        "P2P de iesire de pe cardul",
        "AGROBAZAR SHOP 02",  # Similar to AGROBAZAR
        "FARMACIA MIRON",     # Similar to FARMACIA FAMILIEI
        "UNKNOWN SHOP",       # Should not match
    ]
    
    matcher = get_matcher()
    
    for description in test_cases:
        result = classify_operation(description)
        if result:
            print(f"'{description}' -> {result.type_name} ({result.confidence:.1f}% via {result.method})")
            if result.details:
                print(f"  Details: {result.details}")
        else:
            print(f"'{description}' -> No match found")
        print()


def test_pdf_processing_with_classification():
    """Test processing a PDF with automatic classification"""
    print("=== Testing PDF Processing with Classification ===")
    
    # Use one of the example PDFs
    pdf_path = "PDF_examples/August 2025-to-process.pdf"
    db_path = "test_classification.db"
    
    if not Path(pdf_path).exists():
        print(f"PDF file not found: {pdf_path}")
        return
    
    try:
        # Process PDF with classification
        pdf_id, ops_count, classifications = process_and_store_with_classification(
            pdf_path=pdf_path,
            db_path=db_path,
            auto_assign_high_confidence=True
        )
        
        print(f"PDF ID: {pdf_id}")
        print(f"Operations extracted: {ops_count}")
        print(f"High confidence classifications: {len(classifications)}")
        
        # Show classification results
        for op_id, description, type_name, confidence in classifications:
            print(f"  Operation {op_id}: '{description}' -> {type_name} ({confidence:.1f}%)")
        
        # Show all operations with their types
        engine = get_engine(db_path)
        with Session(engine) as session:
            operations_with_types = get_operations_with_types(session, pdf_id)
            
            print(f"\nAll operations for PDF {pdf_id}:")
            for operation, op_type in operations_with_types:
                type_name = op_type.name if op_type else "Unclassified"
                print(f"  {operation.id}: '{operation.description}' -> {type_name}")
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
    finally:
        # Clean up test database
        if Path(db_path).exists():
            Path(db_path).unlink()


def test_auto_assignment():
    """Test automatic assignment of high confidence operations"""
    print("=== Testing Auto Assignment ===")
    
    pdf_path = "PDF_examples/August 2025-to-process.pdf"
    db_path = "test_auto_assignment.db"
    
    if not Path(pdf_path).exists():
        print(f"PDF file not found: {pdf_path}")
        return
    
    try:
        # First, process without auto-assignment
        pdf_id, ops_count, _ = process_and_store_with_classification(
            pdf_path=pdf_path,
            db_path=db_path,
            auto_assign_high_confidence=False
        )
        
        print(f"PDF ID: {pdf_id}")
        print(f"Operations extracted: {ops_count}")
        
        # Show unclassified operations
        engine = get_engine(db_path)
        with Session(engine) as session:
            operations_with_types = get_operations_with_types(session, pdf_id)
            unclassified = [op for op, op_type in operations_with_types if op_type is None]
            
            print(f"Unclassified operations before auto-assignment: {len(unclassified)}")
            
            # Get classification suggestions
            suggestions = get_classification_suggestions_for_pdf(session, pdf_id)
            print(f"Classification suggestions: {len(suggestions)}")
            
            for operation, suggested_type, confidence, method in suggestions:
                print(f"  '{operation.description}' -> {suggested_type} ({confidence:.1f}% via {method})")
            
            # Auto-assign high confidence operations
            assigned_count = auto_assign_high_confidence_operations(session, pdf_id)
            print(f"Auto-assigned operations: {assigned_count}")
            
            # Show final state
            operations_with_types = get_operations_with_types(session, pdf_id)
            unclassified_after = [op for op, op_type in operations_with_types if op_type is None]
            
            print(f"Unclassified operations after auto-assignment: {len(unclassified_after)}")
            
            for operation, op_type in operations_with_types:
                type_name = op_type.name if op_type else "Unclassified"
                print(f"  {operation.id}: '{operation.description}' -> {type_name}")
        
    except Exception as e:
        print(f"Error in auto assignment test: {e}")
    finally:
        # Clean up test database
        if Path(db_path).exists():
            Path(db_path).unlink()


def test_matcher_statistics():
    """Test and display matcher statistics"""
    print("=== Matcher Statistics ===")
    
    matcher = get_matcher()
    stats = matcher.get_statistics()
    
    print("Operations Matcher Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test some operations to populate caches
    test_ops = ["AGROBAZAR", "FARMACIA FAMILIEI", "BE BEAUTY Salon"]
    for op in test_ops:
        classify_operation(op)
    
    # Show updated statistics
    stats_after = matcher.get_statistics()
    print(f"\nAfter processing {len(test_ops)} operations:")
    print(f"  Exact match cache size: {stats_after['exact_match_cache_size']}")
    print(f"  Fuzzy match cache size: {stats_after['fuzzy_match_cache_size']}")


def main():
    """Run all tests"""
    print("Operations Matching System Test Suite")
    print("=" * 50)
    
    try:
        # Test 1: Single operation classification
        test_single_operation_classification()
        
        # Test 2: PDF processing with classification
        test_pdf_processing_with_classification()
        
        # Test 3: Auto assignment
        test_auto_assignment()
        
        # Test 4: Matcher statistics
        test_matcher_statistics()
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
