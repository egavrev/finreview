"""
Unit tests for the rules management system.
Tests all CRUD operations and business logic for matching rules and categories.
"""

import pytest
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
    run_rule_pattern_test
)


@pytest.fixture
def engine():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create a database session for testing"""
    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_categories(session):
    """Create sample rule categories for testing"""
    categories = []
    
    # Create test categories
    food_cat = create_rule_category(
        session, "Food", "Food and grocery operations", "#FF6B6B"
    )
    healthcare_cat = create_rule_category(
        session, "Healthcare", "Medical and pharmacy operations", "#4ECDC4"
    )
    transport_cat = create_rule_category(
        session, "Transport", "Transportation and fuel operations", "#45B7D1"
    )
    
    categories.extend([food_cat, healthcare_cat, transport_cat])
    return categories


@pytest.fixture
def sample_rules(session, sample_categories):
    """Create sample matching rules for testing"""
    rules = []
    
    # Create test rules
    exact_rule = create_matching_rule(
        session, "exact", "Food", "AGROBAZAR", 100, 100
    )
    keyword_rule = create_matching_rule(
        session, "keyword", "Healthcare", "FARMACIA", 85, 50
    )
    pattern_rule = create_matching_rule(
        session, "pattern", "Transport", ".*GAS.*", 75, 25
    )
    
    rules.extend([exact_rule, keyword_rule, pattern_rule])
    return rules


class TestRuleCategoryManagement:
    """Test rule category CRUD operations"""
    
    def test_create_rule_category(self, session):
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
    
    def test_get_rule_categories(self, session, sample_categories):
        """Test retrieving rule categories"""
        categories = get_rule_categories(session)
        
        assert len(categories) == 3
        assert all(cat.is_active for cat in categories)
        assert [cat.name for cat in categories] == ["Food", "Healthcare", "Transport"]
    
    def test_get_rule_categories_inactive(self, session, sample_categories):
        """Test retrieving categories including inactive ones"""
        # Deactivate one category
        update_rule_category(session, sample_categories[0].id, is_active=False)
        
        all_categories = get_rule_categories(session, active_only=False)
        active_categories = get_rule_categories(session, active_only=True)
        
        assert len(all_categories) == 3
        assert len(active_categories) == 2
    
    def test_get_rule_category_by_id(self, session, sample_categories):
        """Test retrieving a category by ID"""
        category = get_rule_category_by_id(session, sample_categories[0].id)
        
        assert category is not None
        assert category.name == "Food"
    
    def test_get_rule_category_by_name(self, session, sample_categories):
        """Test retrieving a category by name"""
        category = get_rule_category_by_name(session, "Healthcare")
        
        assert category is not None
        assert category.id == sample_categories[1].id
    
    def test_update_rule_category(self, session, sample_categories):
        """Test updating a rule category"""
        category_id = sample_categories[0].id
        original_updated_at = sample_categories[0].updated_at
        
        updated_category = update_rule_category(
            session, category_id,
            name="Updated Food",
            description="Updated description",
            color="#00FF00"
        )
        
        assert updated_category.name == "Updated Food"
        assert updated_category.description == "Updated description"
        assert updated_category.color == "#00FF00"
        assert updated_category.updated_at != original_updated_at
    
    def test_delete_rule_category_success(self, session):
        """Test successfully deleting a category with no rules"""
        category = create_rule_category(session, "Temp Category")
        category_id = category.id
        
        result = delete_rule_category(session, category_id)
        
        assert result is True
        assert get_rule_category_by_id(session, category_id) is None
    
    def test_delete_rule_category_failure(self, session, sample_categories, sample_rules):
        """Test failing to delete a category that has rules"""
        category_id = sample_categories[0].id  # Food category has rules
        
        result = delete_rule_category(session, category_id)
        
        assert result is False
        assert get_rule_category_by_id(session, category_id) is not None


class TestMatchingRuleManagement:
    """Test matching rule CRUD operations"""
    
    def test_create_matching_rule(self, session, sample_categories):
        """Test creating a new matching rule"""
        rule = create_matching_rule(
            session, "exact", "Food", "TEST PATTERN", 90, 75, created_by="test_user"
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
    
    def test_get_matching_rules(self, session, sample_rules):
        """Test retrieving matching rules with filtering"""
        # Get all rules
        all_rules = get_matching_rules(session)
        assert len(all_rules) == 3
        
        # Get rules by type
        exact_rules = get_matching_rules(session, rule_type="exact")
        assert len(exact_rules) == 1
        assert exact_rules[0].rule_type == "exact"
        
        # Get rules by category
        food_rules = get_matching_rules(session, category="Food")
        assert len(food_rules) == 1
        assert food_rules[0].category == "Food"
        
        # Get inactive rules
        # First deactivate a rule
        update_matching_rule(session, sample_rules[0].id, is_active=False)
        inactive_rules = get_matching_rules(session, active_only=False)
        assert len(inactive_rules) == 3  # All rules including inactive
    
    def test_get_matching_rule_by_id(self, session, sample_rules):
        """Test retrieving a rule by ID"""
        rule = get_matching_rule_by_id(session, sample_rules[0].id)
        
        assert rule is not None
        assert rule.pattern == "AGROBAZAR"
    
    def test_update_matching_rule(self, session, sample_rules):
        """Test updating a matching rule"""
        rule_id = sample_rules[0].id
        original_updated_at = sample_rules[0].updated_at
        
        updated_rule = update_matching_rule(
            session, rule_id,
            pattern="UPDATED PATTERN",
            weight=95,
            priority=80
        )
        
        assert updated_rule.pattern == "UPDATED PATTERN"
        assert updated_rule.weight == 95
        assert updated_rule.priority == 80
        assert updated_rule.updated_at != original_updated_at
    
    def test_delete_matching_rule(self, session, sample_rules):
        """Test deleting a matching rule"""
        rule_id = sample_rules[0].id
        
        result = delete_matching_rule(session, rule_id)
        
        assert result is True
        assert get_matching_rule_by_id(session, rule_id) is None
    
    def test_bulk_update_rule_priorities(self, session, sample_rules):
        """Test bulk updating rule priorities"""
        rule_updates = [
            (sample_rules[0].id, 200),
            (sample_rules[1].id, 150),
            (sample_rules[2].id, 100)
        ]
        
        updated_count = bulk_update_rule_priorities(session, rule_updates)
        
        assert updated_count == 3
        
        # Verify priorities were updated
        for rule_id, new_priority in rule_updates:
            rule = get_matching_rule_by_id(session, rule_id)
            assert rule.priority == new_priority


class TestRuleUsageTracking:
    """Test rule usage tracking and statistics"""
    
    def test_log_rule_match(self, session, sample_rules):
        """Test logging a rule match"""
        rule_id = sample_rules[0].id
        original_usage_count = sample_rules[0].usage_count
        original_success_count = sample_rules[0].success_count
        
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
        assert updated_rule.usage_count == original_usage_count + 1
        assert updated_rule.success_count == original_success_count + 1
        assert updated_rule.last_used is not None
    
    def test_get_rule_statistics(self, session, sample_rules):
        """Test retrieving rule statistics"""
        rule_id = sample_rules[0].id
        
        # Log some matches first
        log_rule_match(session, rule_id, "Test 1", "Food", 100.0, "exact", True)
        log_rule_match(session, rule_id, "Test 2", "Food", 90.0, "exact", True)
        log_rule_match(session, rule_id, "Test 3", "Food", 80.0, "exact", False)
        
        stats = get_rule_statistics(session, rule_id)
        
        assert stats['rule_id'] == rule_id
        assert stats['usage_count'] == 3
        assert stats['success_count'] == 2
        assert stats['success_rate'] == 66.67
        assert len(stats['recent_matches']) == 3
    
    def test_get_category_statistics(self, session, sample_categories, sample_rules):
        """Test retrieving category statistics"""
        # Log some matches for the Food category
        food_rule = sample_rules[0]  # This is the Food rule
        log_rule_match(session, food_rule.id, "Test 1", "Food", 100.0, "exact", True)
        log_rule_match(session, food_rule.id, "Test 2", "Food", 95.0, "exact", True)
        
        stats = get_category_statistics(session, "Food")
        
        assert stats['category'] == "Food"
        assert stats['total_rules'] == 1
        assert stats['active_rules'] == 1
        assert stats['total_usage'] == 2
        assert stats['total_success'] == 2
        assert stats['success_rate'] == 100.0
        assert len(stats['rules']) == 1


class TestRuleTestingAndValidation:
    """Test rule pattern testing and validation"""
    
    def test_test_rule_pattern_exact(self, session, sample_rules):
        """Test exact rule pattern testing"""
        exact_rule = sample_rules[0]  # AGROBAZAR rule
        
        results = run_rule_pattern_test(session, exact_rule.id, [
            "AGROBAZAR", "agrobazar", "OTHER STORE", "AGROBAZAR EXTRA"
        ])
        
        assert len(results) == 4
        assert results[0]['matches'] is True  # Exact match
        assert results[0]['confidence'] == 100
        assert results[1]['matches'] is True  # Case insensitive
        assert results[2]['matches'] is False  # No match
        assert results[3]['matches'] is False  # Partial match
    
    def test_test_rule_pattern_keyword(self, session, sample_rules):
        """Test keyword rule pattern testing"""
        keyword_rule = sample_rules[1]  # FARMACIA rule
        
        results = run_rule_pattern_test(session, keyword_rule.id, [
            "FARMACIA FAMILIEI", "FARMACIA MIRON", "RESTAURANT", "FARMACIA"
        ])
        
        assert len(results) == 4
        assert results[0]['matches'] is True  # Contains keyword
        assert results[0]['confidence'] == 85
        assert results[1]['matches'] is True  # Contains keyword
        assert results[2]['matches'] is False  # No keyword
        assert results[3]['matches'] is True  # Exact keyword
    
    def test_test_rule_pattern_regex(self, session, sample_rules):
        """Test regex rule pattern testing"""
        pattern_rule = sample_rules[2]  # .*GAS.* rule
        
        results = run_rule_pattern_test(session, pattern_rule.id, [
            "GAS STATION", "FUEL GAS", "RESTAURANT", "GAS"
        ])
        
        assert len(results) == 4
        assert results[0]['matches'] is True  # Matches pattern
        assert results[0]['confidence'] == 75
        assert results[1]['matches'] is True  # Matches pattern
        assert results[2]['matches'] is False  # No match
        assert results[3]['matches'] is True  # Exact match
    
    def test_validate_rule_pattern(self):
        """Test rule pattern validation"""
        # Valid patterns
        from rules_manager import validate_rule_pattern
        assert validate_rule_pattern("exact", "Valid Pattern")[0] is True
        assert validate_rule_pattern("keyword", "Valid Keyword")[0] is True
        assert validate_rule_pattern("pattern", ".*Valid.*")[0] is True
        
        # Invalid patterns
        assert validate_rule_pattern("exact", "")[0] is False
        assert validate_rule_pattern("keyword", "")[0] is False
        assert validate_rule_pattern("pattern", "")[0] is False
        assert validate_rule_pattern("pattern", "[Invalid")[0] is False  # Invalid regex
        assert validate_rule_pattern("unknown", "pattern")[0] is False  # Unknown type


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
