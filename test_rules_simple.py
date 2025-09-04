#!/usr/bin/env python3
"""
Simple test runner for the rules management system.
This avoids pytest dependencies and runs tests directly.
"""

import sys
from datetime import datetime
from sqlmodel import Session, create_engine, SQLModel
from rules_models import MatchingRule, RuleCategory, RuleMatchLog
from rules_manager import (
    # Category management
    create_rule_category, get_rule_categories, get_rule_category_by_id,
    get_rule_category_by_name, update_rule_category, delete_rule_category,
    # Rule management
    create_matching_rule, get_matching_rules, get_matching_rule_by_id,
    update_matching_rule, delete_matching_rule, bulk_update_rule_priorities,
    # Usage tracking
    log_rule_match, get_rule_statistics, get_category_statistics,
    # Testing and validation
    test_rule_pattern, validate_rule_pattern
)


def run_test(test_name, test_func):
    """Run a single test and report results"""
    try:
        test_func()
        print(f"✅ {test_name}: PASSED")
        return True
    except Exception as e:
        print(f"❌ {test_name}: FAILED - {str(e)}")
        return False


def test_create_rule_category(session):
    """Test creating a new rule category"""
    category = create_rule_category(
        session, "Test Category", "Test description", "#FF0000"
    )
    
    assert category.id is not None
    assert category.name == "Test Category"
    assert category.description == "Test description"
    assert category.color == "#FF0000"
    assert category.is_active is True
    assert category.created_at is not None
    assert category.updated_at is not None


def test_get_rule_categories(session):
    """Test retrieving rule categories"""
    # Create some test categories
    create_rule_category(session, "Food", "Food operations", "#FF6B6B")
    create_rule_category(session, "Healthcare", "Medical operations", "#4ECDC4")
    
    categories = get_rule_categories(session)
    
    assert len(categories) >= 2
    assert all(cat.is_active for cat in categories)
    category_names = [cat.name for cat in categories]
    assert "Food" in category_names
    assert "Healthcare" in category_names


def test_create_matching_rule(session):
    """Test creating a new matching rule"""
    rule = create_matching_rule(
        session, "exact", "Food", "TEST PATTERN", 90, 75, "test_user"
    )
    
    assert rule.id is not None
    assert rule.rule_type == "exact"
    assert rule.category == "Food"
    assert rule.pattern == "TEST PATTERN"
    assert rule.weight == 90
    assert rule.priority == 75
    assert rule.created_by == "test_user"
    assert rule.is_active is True
    assert rule.usage_count == 0
    assert rule.success_count == 0


def test_validate_rule_pattern():
    """Test rule pattern validation"""
    # Valid patterns
    assert validate_rule_pattern("exact", "Valid Pattern")[0] is True
    assert validate_rule_pattern("keyword", "Valid Keyword")[0] is True
    assert validate_rule_pattern("pattern", ".*Valid.*")[0] is True
    
    # Invalid patterns
    assert validate_rule_pattern("exact", "")[0] is False
    assert validate_rule_pattern("keyword", "")[0] is False
    assert validate_rule_pattern("pattern", "")[0] is False
    assert validate_rule_pattern("pattern", "[Invalid")[0] is False  # Invalid regex
    assert validate_rule_pattern("unknown", "pattern")[0] is False  # Unknown type


def test_log_rule_match(session):
    """Test logging a rule match"""
    # Create a rule first
    rule = create_matching_rule(session, "exact", "Food", "TEST", 100, 100)
    rule_id = rule.id
    
    log_entry = log_rule_match(
        session, rule_id, "Test operation", "Food", 95.0, "exact", True
    )
    
    assert log_entry.id is not None
    assert log_entry.rule_id == rule_id
    assert log_entry.operation_description == "Test operation"
    assert log_entry.matched_type == "Food"
    assert log_entry.confidence == 95.0
    assert log_entry.method == "exact"
    assert log_entry.success is True
    
    # Verify rule statistics were updated
    updated_rule = get_matching_rule_by_id(session, rule_id)
    assert updated_rule.usage_count == 1
    assert updated_rule.success_count == 1
    assert updated_rule.last_used is not None


def main():
    """Run all tests"""
    print("🧪 Running Rules Management Tests...")
    print("=" * 50)
    
    # Create test database
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    
    passed = 0
    total = 0
    
    with Session(engine) as session:
        tests = [
            ("Create Rule Category", lambda: test_create_rule_category(session)),
            ("Get Rule Categories", lambda: test_get_rule_categories(session)),
            ("Create Matching Rule", lambda: test_create_matching_rule(session)),
            ("Validate Rule Pattern", test_validate_rule_pattern),
            ("Log Rule Match", lambda: test_log_rule_match(session)),
        ]
        
        for test_name, test_func in tests:
            total += 1
            if run_test(test_name, test_func):
                passed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
