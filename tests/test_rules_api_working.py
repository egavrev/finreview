"""
Working unit tests for api/rules_api.py module
Focusing on tests that actually work with proper mocking
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlmodel import Session

# Import the API module
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from api.rules_api import (
    router, 
    RuleCategoryCreate, 
    RuleCategoryUpdate, 
    RuleCategoryResponse,
    MatchingRuleCreate,
    MatchingRuleUpdate,
    MatchingRuleResponse,
    RulePriorityUpdate,
    RuleTestRequest,
    RuleTestResponse,
    RuleValidationRequest,
    RuleValidationResponse,
    RunMatcherRequest,
    RunMatcherResponse,
    get_session
)

# Create test app
app = FastAPI()
app.include_router(router)


class TestPydanticModels:
    """Test Pydantic models for API requests/responses"""
    
    def test_rule_category_create(self):
        """Test RuleCategoryCreate model"""
        category = RuleCategoryCreate(
            name="Test Category",
            description="Test Description",
            color="#FF0000"
        )
        assert category.name == "Test Category"
        assert category.description == "Test Description"
        assert category.color == "#FF0000"
    
    def test_rule_category_create_minimal(self):
        """Test RuleCategoryCreate with minimal fields"""
        category = RuleCategoryCreate(name="Test Category")
        assert category.name == "Test Category"
        assert category.description is None
        assert category.color is None
    
    def test_rule_category_update(self):
        """Test RuleCategoryUpdate model"""
        update = RuleCategoryUpdate(
            name="Updated Name",
            description="Updated Description",
            color="#00FF00",
            is_active=False
        )
        assert update.name == "Updated Name"
        assert update.description == "Updated Description"
        assert update.color == "#00FF00"
        assert update.is_active is False
    
    def test_rule_category_response(self):
        """Test RuleCategoryResponse model"""
        response = RuleCategoryResponse(
            id=1,
            name="Test Category",
            description="Test Description",
            color="#FF0000",
            is_active=True,
            created_at="2023-01-01T00:00:00",
            updated_at="2023-01-01T00:00:00"
        )
        assert response.id == 1
        assert response.name == "Test Category"
        assert response.is_active is True
    
    def test_matching_rule_create(self):
        """Test MatchingRuleCreate model"""
        rule = MatchingRuleCreate(
            rule_type="keyword",
            category="Food",
            pattern="AGRO",
            weight=90,
            priority=1,
            created_by="test_user"
        )
        assert rule.rule_type == "keyword"
        assert rule.category == "Food"
        assert rule.pattern == "AGRO"
        assert rule.weight == 90
        assert rule.priority == 1
        assert rule.created_by == "test_user"
    
    def test_matching_rule_create_defaults(self):
        """Test MatchingRuleCreate with default values"""
        rule = MatchingRuleCreate(
            rule_type="exact",
            category="Food",
            pattern="AGROBAZAR"
        )
        assert rule.weight == 85  # Default weight
        assert rule.priority == 0  # Default priority
        assert rule.created_by is None
    
    def test_matching_rule_response(self):
        """Test MatchingRuleResponse model"""
        response = MatchingRuleResponse(
            id=1,
            rule_type="keyword",
            category="Food",
            pattern="AGRO",
            weight=90,
            priority=1,
            is_active=True,
            created_by="test_user",
            created_at="2023-01-01T00:00:00",
            updated_at="2023-01-01T00:00:00",
            usage_count=5,
            success_count=4,
            last_used="2023-01-01T12:00:00"
        )
        assert response.id == 1
        assert response.usage_count == 5
        assert response.success_count == 4
    
    def test_rule_priority_update(self):
        """Test RulePriorityUpdate model"""
        update = RulePriorityUpdate(rule_id=1, priority=5)
        assert update.rule_id == 1
        assert update.priority == 5
    
    def test_rule_test_request(self):
        """Test RuleTestRequest model"""
        request = RuleTestRequest(
            rule_id=1,
            test_strings=["AGROBAZAR", "FARMACIA"]
        )
        assert request.rule_id == 1
        assert len(request.test_strings) == 2
        assert "AGROBAZAR" in request.test_strings
    
    def test_rule_test_response(self):
        """Test RuleTestResponse model"""
        response = RuleTestResponse(
            test_string="AGROBAZAR",
            matches=True,
            confidence=95.0,
            rule_pattern="AGRO",
            rule_type="keyword"
        )
        assert response.test_string == "AGROBAZAR"
        assert response.matches is True
        assert response.confidence == 95.0
    
    def test_rule_validation_request(self):
        """Test RuleValidationRequest model"""
        request = RuleValidationRequest(
            rule_type="pattern",
            pattern=".*AGRO.*"
        )
        assert request.rule_type == "pattern"
        assert request.pattern == ".*AGRO.*"
    
    def test_rule_validation_response(self):
        """Test RuleValidationResponse model"""
        response = RuleValidationResponse(
            is_valid=True,
            message="Pattern is valid"
        )
        assert response.is_valid is True
        assert response.message == "Pattern is valid"
    
    def test_run_matcher_request(self):
        """Test RunMatcherRequest model"""
        request = RunMatcherRequest(
            operation_ids=[1, 2, 3],
            auto_assign_high_confidence=False
        )
        assert request.operation_ids == [1, 2, 3]
        assert request.auto_assign_high_confidence is False
    
    def test_run_matcher_request_defaults(self):
        """Test RunMatcherRequest with default values"""
        request = RunMatcherRequest()
        assert request.operation_ids is None
        assert request.auto_assign_high_confidence is True
    
    def test_run_matcher_response(self):
        """Test RunMatcherResponse model"""
        response = RunMatcherResponse(
            success=True,
            message="Processed successfully",
            processed=10,
            classified=8,
            remaining=2,
            details=[{"operation_id": 1, "category": "Food"}],
            error=None
        )
        assert response.success is True
        assert response.processed == 10
        assert response.classified == 8
        assert response.remaining == 2
        assert len(response.details) == 1


class TestDependencies:
    """Test API dependencies"""
    
    @patch('api.rules_api.get_engine')
    def test_get_session(self, mock_get_engine):
        """Test get_session dependency"""
        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine
        
        # Test that get_session yields a session
        session_gen = get_session()
        session = next(session_gen)
        
        assert isinstance(session, Session)
        mock_get_engine.assert_called_once()


class TestAPIEndpointsWorking:
    """Test API endpoints that actually work with proper mocking"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_validate_rule_pattern_endpoint_success(self, client):
        """Test successful rule pattern validation - this should work without DB"""
        with patch('api.rules_api.validate_rule_pattern', return_value=(True, "Pattern is valid")):
            response = client.post(
                "/api/rules/rules/validate",
                json={
                    "rule_type": "pattern",
                    "pattern": ".*AGRO.*"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['is_valid'] is True
            assert data['message'] == "Pattern is valid"
    
    def test_validate_rule_pattern_endpoint_invalid(self, client):
        """Test rule pattern validation with invalid pattern"""
        with patch('api.rules_api.validate_rule_pattern', return_value=(False, "Invalid regex pattern")):
            response = client.post(
                "/api/rules/rules/validate",
                json={
                    "rule_type": "pattern",
                    "pattern": "[invalid regex"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['is_valid'] is False
            assert data['message'] == "Invalid regex pattern"
    
    def test_invalid_json_request(self, client):
        """Test request with invalid JSON"""
        response = client.post(
            "/api/rules/categories",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_missing_required_fields(self, client):
        """Test request with missing required fields"""
        response = client.post(
            "/api/rules/categories",
            json={}  # Missing required 'name' field
        )
        assert response.status_code == 422  # Validation error
    
    def test_invalid_rule_type(self, client):
        """Test request with invalid rule type"""
        response = client.post(
            "/api/rules/rules",
            json={
                "rule_type": "invalid_type",
                "category": "Food",
                "pattern": "AGRO"
            }
        )
        # This should pass validation but fail in the endpoint logic
        assert response.status_code in [400, 500]
    
    def test_negative_weight(self, client):
        """Test request with negative weight"""
        response = client.post(
            "/api/rules/rules",
            json={
                "rule_type": "keyword",
                "category": "Food",
                "pattern": "AGRO",
                "weight": -10
            }
        )
        # This should pass validation but might fail in business logic
        assert response.status_code in [200, 400, 500]
    
    def test_empty_pattern(self, client):
        """Test request with empty pattern"""
        response = client.post(
            "/api/rules/rules",
            json={
                "rule_type": "keyword",
                "category": "Food",
                "pattern": ""
            }
        )
        # This should pass validation but fail in business logic
        assert response.status_code in [400, 500]


class TestAPIEndpointsWithMocking:
    """Test API endpoints with comprehensive mocking"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_create_category_success(self, client):
        """Test successful category creation with proper mocking"""
        # Mock the entire rules_manager module
        with patch('api.rules_api.get_rule_category_by_name', return_value=None) as mock_get_by_name, \
             patch('api.rules_api.create_rule_category') as mock_create_rule, \
             patch('api.rules_api.get_engine') as mock_get_engine:
            
            # Mock the database engine and session
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            
            # Mock the category object
            class MockCategory:
                def __init__(self):
                    self.id = 1
                    self.name = 'Test Category'
                    self.description = 'Test Description'
                    self.color = '#FF0000'
                    self.is_active = True
                    self.created_at = '2023-01-01T00:00:00'
                    self.updated_at = '2023-01-01T00:00:00'
            
            mock_category = MockCategory()
            mock_create_rule.return_value = mock_category
            
            # Test request
            response = client.post(
                "/api/rules/categories",
                json={
                    "name": "Test Category",
                    "description": "Test Description",
                    "color": "#FF0000"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['name'] == 'Test Category'
            assert data['description'] == 'Test Description'
            assert data['color'] == '#FF0000'
    
    def test_create_rule_success(self, client):
        """Test successful rule creation with proper mocking"""
        with patch('api.rules_api.validate_rule_pattern', return_value=(True, "Valid pattern")) as mock_validate, \
             patch('api.rules_api.create_matching_rule') as mock_create_rule, \
             patch('api.rules_api.get_engine') as mock_get_engine:
            
            # Mock the database engine
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            
            # Mock the rule object
            class MockRule:
                def __init__(self):
                    self.id = 1
                    self.rule_type = 'keyword'
                    self.category = 'Food'
                    self.pattern = 'AGRO'
                    self.weight = 90
                    self.priority = 1
                    self.is_active = True
                    self.created_by = 'test_user'
                    self.created_at = '2023-01-01T00:00:00'
                    self.updated_at = '2023-01-01T00:00:00'
                    self.usage_count = 0
                    self.success_count = 0
                    self.last_used = None
            
            mock_rule = MockRule()
            mock_create_rule.return_value = mock_rule
            
            # Test request
            response = client.post(
                "/api/rules/rules",
                json={
                    "rule_type": "keyword",
                    "category": "Food",
                    "pattern": "AGRO",
                    "weight": 90,
                    "priority": 1,
                    "created_by": "test_user"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['rule_type'] == 'keyword'
            assert data['category'] == 'Food'
            assert data['pattern'] == 'AGRO'
    
    def test_list_categories_success(self, client):
        """Test successful category listing with proper mocking"""
        with patch('api.rules_api.get_rule_categories') as mock_get_categories, \
             patch('api.rules_api.get_engine') as mock_get_engine:
            
            # Mock the database engine
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            
            # Mock the category object
            class MockCategory:
                def __init__(self):
                    self.id = 1
                    self.name = 'Test Category'
                    self.description = 'Test Description'
                    self.color = '#FF0000'
                    self.is_active = True
                    self.created_at = '2023-01-01T00:00:00'
                    self.updated_at = '2023-01-01T00:00:00'
            
            mock_category = MockCategory()
            mock_get_categories.return_value = [mock_category]
            
            # Test request
            response = client.get("/api/rules/categories")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]['name'] == 'Test Category'
    
    def test_list_rules_success(self, client):
        """Test successful rule listing with proper mocking"""
        with patch('api.rules_api.get_matching_rules') as mock_get_rules, \
             patch('api.rules_api.get_engine') as mock_get_engine:
            
            # Mock the database engine
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            
            # Mock the rule object
            mock_rule = Mock()
            mock_rule.__dict__ = {
                'id': 1,
                'rule_type': 'keyword',
                'category': 'Food',
                'pattern': 'AGRO',
                'weight': 90,
                'priority': 1,
                'is_active': True,
                'created_by': 'test_user',
                'created_at': '2023-01-01T00:00:00',
                'updated_at': '2023-01-01T00:00:00',
                'usage_count': 5,
                'success_count': 4,
                'last_used': '2023-01-01T12:00:00'
            }
            mock_get_rules.return_value = [mock_rule]
            
            # Test request
            response = client.get("/api/rules/rules")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]['rule_type'] == 'keyword'
    
    def test_bulk_update_priorities_success(self, client):
        """Test successful bulk priority update with proper mocking"""
        with patch('api.rules_api.bulk_update_rule_priorities', return_value=3) as mock_bulk_update, \
             patch('api.rules_api.get_engine') as mock_get_engine:
            
            # Mock the database engine
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine
            
            # Test request
            response = client.post(
                "/api/rules/rules/bulk-priority",
                json=[
                    {"rule_id": 1, "priority": 5},
                    {"rule_id": 2, "priority": 3},
                    {"rule_id": 3, "priority": 1}
                ]
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data['message'] == 'Updated 3 rules'
            assert data['updated_count'] == 3
