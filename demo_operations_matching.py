#!/usr/bin/env python3
"""
Demo script for Operations Matching System

This script demonstrates how the hybrid rule-based classification system
automatically classifies financial operations from the database.
"""

from operations_matcher import classify_operation, get_matcher
from sql_utils import get_engine, Session, get_operations_with_types, get_operation_types, get_operations_with_null_types, auto_assign_all_high_confidence_operations
from collections import defaultdict


def demo_single_classifications():
    """Demonstrate classification of individual operations"""
    print("🔍 SINGLE OPERATION CLASSIFICATION DEMO")
    print("=" * 50)
    
    # Test cases with different types of descriptions
    test_cases = [
        "AGROBAZAR",
        "LATTI FOODMART M", 
        "FARMACIA FAMILIEI",
        "BE BEAUTY Salon",
        "RESTAURANT JERAFFE",
        "MAIB ART TWIST SRL",
        "IURALEX COM SRL",
        "EA STUDIO FIT SRL",
        "OPENAI",
        "P2P de iesire de pe cardul",
        "AGROBAZAR SHOP 02",  # Similar to AGROBAZAR
        "FARMACIA MIRON",     # Similar to FARMACIA FAMILIEI
        "UNKNOWN MERCHANT",   # Should not match
    ]
    
    print("Testing classification of individual operations:")
    print()
    
    for description in test_cases:
        result = classify_operation(description)
        
        if result:
            # Color coding based on confidence
            if result.confidence >= 95:
                confidence_color = "🟢"  # Green for high confidence
            elif result.confidence >= 80:
                confidence_color = "🟡"  # Yellow for medium confidence
            else:
                confidence_color = "🟠"  # Orange for low confidence
            
            print(f"{confidence_color} '{description}'")
            print(f"   → {result.type_name} ({result.confidence:.1f}% confidence)")
            print(f"   → Method: {result.method}")
            
            # Show details based on method
            if result.method == 'exact':
                print(f"   → Exact match found")
            elif result.method == 'fuzzy':
                print(f"   → Similar to: {result.details.get('matched_pattern', 'Unknown')}")
            elif result.method == 'keyword':
                keywords = result.details.get('matched_keywords', [])
                print(f"   → Matched keywords: {', '.join(keywords)}")
            elif result.method == 'pattern':
                patterns = result.details.get('matched_patterns', [])
                print(f"   → Matched patterns: {len(patterns)}")
        else:
            print(f"🔴 '{description}'")
            print(f"   → No classification found")
        
        print()


def demo_database_classification():
    """Demonstrate classification of all database operations"""
    print("📊 DATABASE OPERATIONS CLASSIFICATION DEMO")
    print("=" * 50)
    
    engine = get_engine('db.sqlite')
    with Session(engine) as session:
        # Get all operations from database
        operations_with_types = get_operations_with_types(session)
        operation_types = get_operation_types(session)
        
        print(f"📈 Database Statistics:")
        print(f"   • Total operations: {len(operations_with_types)}")
        print(f"   • Operation types: {[t.name for t in operation_types]}")
        
        # Analyze current classification status
        classified_count = 0
        unclassified_count = 0
        type_distribution = defaultdict(int)
        
        for operation, op_type in operations_with_types:
            if op_type:
                classified_count += 1
                type_distribution[op_type.name] += 1
            else:
                unclassified_count += 1
        
        print(f"   • Currently classified: {classified_count}")
        print(f"   • Currently unclassified: {unclassified_count}")
        print(f"   • Classification rate: {(classified_count/len(operations_with_types)*100):.1f}%")
        
        print()
        print("📊 Current Classification Distribution:")
        for type_name, count in sorted(type_distribution.items()):
            percentage = (count / len(operations_with_types)) * 100
            print(f"   • {type_name}: {count} operations ({percentage:.1f}%)")
        
        print()
        print("🔍 CLASSIFICATION ANALYSIS")
        print("-" * 30)
        
        # Test classification on unclassified operations
        unclassified_operations = get_operations_with_null_types(session)
        print(f"Testing classification on {len(unclassified_operations)} unclassified operations:")
        print()
        
        classification_results = {
            'exact': 0,
            'fuzzy': 0,
            'keyword': 0,
            'pattern': 0,
            'no_match': 0
        }
        
        confidence_ranges = {
            '95-100%': 0,
            '80-94%': 0,
            '70-79%': 0,
            '60-69%': 0,
            '0-59%': 0
        }
        
        suggested_types = defaultdict(int)
        
        for operation in unclassified_operations:
            if operation.description:
                result = classify_operation(operation.description)
                
                if result:
                    classification_results[result.method] += 1
                    suggested_types[result.type_name] += 1
                    
                    # Categorize by confidence
                    if result.confidence >= 95:
                        confidence_ranges['95-100%'] += 1
                    elif result.confidence >= 80:
                        confidence_ranges['80-94%'] += 1
                    elif result.confidence >= 70:
                        confidence_ranges['70-79%'] += 1
                    elif result.confidence >= 60:
                        confidence_ranges['60-69%'] += 1
                    else:
                        confidence_ranges['0-59%'] += 1
                    
                    # Show high confidence suggestions
                    if result.confidence >= 80:
                        print(f"🟢 '{operation.description}' → {result.type_name} ({result.confidence:.1f}% via {result.method})")
                else:
                    classification_results['no_match'] += 1
                    confidence_ranges['0-59%'] += 1
        
        print()
        print("📊 Classification Method Distribution:")
        for method, count in classification_results.items():
            if count > 0:
                percentage = (count / sum(classification_results.values())) * 100
                print(f"   • {method.capitalize()}: {count} ({percentage:.1f}%)")
        
        print()
        print("📊 Confidence Distribution:")
        for range_name, count in confidence_ranges.items():
            if count > 0:
                percentage = (count / sum(confidence_ranges.values())) * 100
                print(f"   • {range_name}: {count} ({percentage:.1f}%)")
        
        print()
        print("📊 Suggested Type Distribution:")
        for type_name, count in sorted(suggested_types.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {type_name}: {count} suggestions")


def demo_auto_classification_potential():
    """Demonstrate potential auto-classification results"""
    print("🚀 AUTO-CLASSIFICATION POTENTIAL DEMO")
    print("=" * 50)
    
    engine = get_engine('db.sqlite')
    with Session(engine) as session:
        unclassified_operations = get_operations_with_null_types(session)
        
        print(f"Analyzing {len(unclassified_operations)} unclassified operations for auto-classification potential:")
        print()
        
        auto_assignable = []
        review_needed = []
        no_suggestion = []
        
        for operation in unclassified_operations:
            if operation.description:
                result = classify_operation(operation.description)
                
                if result:
                    if result.confidence >= 95 or result.method == 'exact':
                        auto_assignable.append((operation, result))
                    elif result.confidence >= 70:
                        review_needed.append((operation, result))
                    else:
                        no_suggestion.append(operation)
                else:
                    no_suggestion.append(operation)
        
        print(f"🟢 Auto-assignable (high confidence): {len(auto_assignable)}")
        print(f"🟡 Review needed (medium confidence): {len(review_needed)}")
        print(f"🔴 No suggestion (low confidence): {len(no_suggestion)}")
        
        print()
        print("🟢 HIGH CONFIDENCE AUTO-ASSIGNABLE OPERATIONS:")
        for operation, result in auto_assignable:
            print(f"   • '{operation.description}' → {result.type_name} ({result.confidence:.1f}% via {result.method})")
        
        print()
        print("🟡 MEDIUM CONFIDENCE REVIEW OPERATIONS:")
        for operation, result in review_needed:
            print(f"   • '{operation.description}' → {result.type_name} ({result.confidence:.1f}% via {result.method})")
        
        print()
        print("🔴 NO SUGGESTION OPERATIONS:")
        for operation in no_suggestion:
            print(f"   • '{operation.description}'")
        
        # Calculate potential improvement
        total_ops = len(unclassified_operations)
        potential_auto = len(auto_assignable)
        potential_review = len(review_needed)
        
        print()
        print("📈 POTENTIAL IMPROVEMENT:")
        print(f"   • Operations that could be auto-assigned: {potential_auto} ({(potential_auto/total_ops*100):.1f}%)")
        print(f"   • Operations needing review: {potential_review} ({(potential_review/total_ops*100):.1f}%)")
        print(f"   • Total potential improvement: {potential_auto + potential_review} ({((potential_auto + potential_review)/total_ops*100):.1f}%)")


def update_all_high_confidence_operations():
    """Update all high confidence operations in the database"""
    print("🔄 UPDATING ALL HIGH CONFIDENCE OPERATIONS")
    print("=" * 50)
    
    engine = get_engine('db.sqlite')
    with Session(engine) as session:
        # Get current status
        operations_with_types = get_operations_with_types(session)
        unclassified_before = len([op for op, op_type in operations_with_types if op_type is None])
        
        print(f"📊 Before update:")
        print(f"   • Total operations: {len(operations_with_types)}")
        print(f"   • Unclassified operations: {unclassified_before}")
        
        # Auto-assign high confidence operations
        assigned_count = auto_assign_all_high_confidence_operations(session)
        
        # Get updated status
        operations_with_types_after = get_operations_with_types(session)
        unclassified_after = len([op for op, op_type in operations_with_types_after if op_type is None])
        
        print()
        print(f"📊 After update:")
        print(f"   • Operations auto-assigned: {assigned_count}")
        print(f"   • Remaining unclassified: {unclassified_after}")
        print(f"   • Improvement: {unclassified_before - unclassified_after} operations")
        
        # Show updated classification distribution
        type_distribution = defaultdict(int)
        for operation, op_type in operations_with_types_after:
            if op_type:
                type_distribution[op_type.name] += 1
        
        print()
        print("📊 Updated Classification Distribution:")
        for type_name, count in sorted(type_distribution.items()):
            percentage = (count / len(operations_with_types_after)) * 100
            print(f"   • {type_name}: {count} operations ({percentage:.1f}%)")
        
        # Show newly classified operations
        if assigned_count > 0:
            print()
            print("🟢 NEWLY CLASSIFIED OPERATIONS:")
            newly_classified = []
            for operation, op_type in operations_with_types_after:
                if op_type:
                    # Check if this was previously unclassified
                    was_unclassified = True
                    for orig_op, orig_type in operations_with_types:
                        if orig_op.id == operation.id and orig_type is not None:
                            was_unclassified = False
                            break
                    if was_unclassified:
                        newly_classified.append((operation, op_type))
            
            for operation, op_type in newly_classified:
                print(f"   • '{operation.description}' → {op_type.name}")


def demo_matcher_capabilities():
    """Demonstrate the capabilities of the matcher"""
    print("⚙️ MATCHER CAPABILITIES DEMO")
    print("=" * 50)
    
    matcher = get_matcher()
    stats = matcher.get_statistics()
    
    print("📈 Matcher Statistics:")
    print(f"   • Exact match rules: {stats['total_exact_matches']}")
    print(f"   • Keyword categories: {stats['total_keyword_categories']}")
    print(f"   • Pattern categories: {stats['total_pattern_categories']}")
    print(f"   • Cache size (exact): {stats['exact_match_cache_size']}")
    print(f"   • Cache size (fuzzy): {stats['fuzzy_match_cache_size']}")
    
    print()
    print("🎯 Classification Methods:")
    print("   1. Exact Match (100% confidence)")
    print("      - Direct string comparison")
    print("      - Example: 'AGROBAZAR' → Food")
    print()
    print("   2. Fuzzy Match (85-99% confidence)")
    print("      - String similarity using Levenshtein distance")
    print("      - Example: 'AGROBAZAR SHOP 02' → Food (similar to 'AGROBAZAR')")
    print()
    print("   3. Keyword Match (70-90% confidence)")
    print("      - Matches based on keywords in description")
    print("      - Example: 'FARMACIA MIRON' → Healthcare (contains 'FARMACIA')")
    print()
    print("   4. Pattern Match (60-80% confidence)")
    print("      - Regular expression pattern matching")
    print("      - Example: '.*FARMACIA.*' → Healthcare")


def demo_learning_capabilities():
    """Demonstrate learning capabilities"""
    print("🧠 LEARNING CAPABILITIES DEMO")
    print("=" * 50)
    
    matcher = get_matcher()
    
    print("📚 Learning from user corrections:")
    print()
    
    # Simulate user corrections based on real data
    corrections = [
        ("AGROBAZAR", "Food", 95),
        ("FARMACIA FAMILIEI", "Healthcare", 90),
        ("BE BEAUTY Salon", "Entertainment", 85),
        ("RESTAURANT JERAFFE", "Restaurant", 90),
        ("OPENAI", "Bills", 85),
    ]
    
    for description, correct_type, confidence in corrections:
        print(f"   • User corrected: '{description}' → {correct_type} ({confidence}% confidence)")
        matcher.learn_from_correction(description, correct_type, confidence)
    
    print()
    print("📖 Learned patterns:")
    learned = matcher.get_learned_patterns()
    for type_name, patterns in learned.items():
        if patterns:
            print(f"   • {type_name}: {len(patterns)} patterns")
            for pattern in patterns:
                print(f"     - '{pattern['pattern']}' (confidence: {pattern['confidence']}%)")


def demo_real_world_examples():
    """Show real-world examples from the database"""
    print("🌍 REAL-WORLD EXAMPLES FROM DATABASE")
    print("=" * 50)
    
    engine = get_engine('db.sqlite')
    with Session(engine) as session:
        operations_with_types = get_operations_with_types(session)
        
        # Group by type
        type_groups = defaultdict(list)
        unclassified = []
        
        for operation, op_type in operations_with_types:
            if op_type:
                type_groups[op_type.name].append(operation)
            else:
                unclassified.append(operation)
        
        print("📊 Current Classifications by Type:")
        for type_name, operations in sorted(type_groups.items()):
            print(f"   • {type_name}: {len(operations)} operations")
            # Show all examples
            for op in operations:
                print(f"     - {op.description}")
            print()
        
        print(f"🔴 Unclassified: {len(unclassified)} operations")
        for op in unclassified:
            result = classify_operation(op.description)
            if result:
                print(f"   • {op.description} → Suggested: {result.type_name} ({result.confidence:.1f}%)")
            else:
                print(f"   • {op.description} → No suggestion")


def main():
    """Run the complete demonstration"""
    print("🚀 OPERATIONS MATCHING SYSTEM DEMONSTRATION")
    print("=" * 60)
    print()
    
    try:
        # Demo 1: Single classifications
        demo_single_classifications()
        
        print("\n" + "=" * 60 + "\n")
        
        # Demo 2: Database classification analysis
        demo_database_classification()
        
        print("\n" + "=" * 60 + "\n")
        
        # Demo 3: Auto-classification potential
        demo_auto_classification_potential()
        
        print("\n" + "=" * 60 + "\n")
        
        # Demo 4: Update all high confidence operations
        update_all_high_confidence_operations()
        
        print("\n" + "=" * 60 + "\n")
        
        # Demo 5: Real-world examples
        demo_real_world_examples()
        
        print("\n" + "=" * 60 + "\n")
        
        # Demo 6: Matcher capabilities
        demo_matcher_capabilities()
        
        print("\n" + "=" * 60 + "\n")
        
        # Demo 7: Learning capabilities
        demo_learning_capabilities()
        
        print("\n" + "=" * 60)
        print("✅ DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print()
        print("💡 Key Benefits:")
        print("   • Automatic classification of financial operations")
        print("   • High accuracy with confidence scoring")
        print("   • Multiple classification methods")
        print("   • Learning from user corrections")
        print("   • Configurable rules and thresholds")
        print("   • Real-world data analysis")
        print("   • Database auto-update functionality")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
