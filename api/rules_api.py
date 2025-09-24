"""
API endpoints for rules management.
Provides REST API for managing matching rules and categories.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session, select
from pathlib import Path

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sql_utils import get_engine, get_operations_with_null_types, assign_operation_type, get_operation_types, OperationRow, User
import os
from auth import get_current_user, security
from rules_manager import (
    # Category management
    create_rule_category, get_rule_categories, get_rule_category_by_id,
    get_rule_category_by_name, update_rule_category, delete_rule_category,
    # Rule management
    create_matching_rule, get_matching_rules, get_matching_rule_by_id,
    update_matching_rule, delete_matching_rule, bulk_update_rule_priorities,
    # Usage tracking
    get_rule_statistics, get_category_statistics, log_rule_match,
    # Testing and validation
    run_rule_pattern_test, validate_rule_pattern
)

router = APIRouter(prefix="/api/rules", tags=["rules"])


# Pydantic models for API requests/responses
class RuleCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Hex color code")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        return v.strip()


class RuleCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$', description="Hex color code")
    is_active: Optional[bool] = Field(None, description="Whether the category is active")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        return v.strip() if v else v


class RuleCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str


class MatchingRuleCreate(BaseModel):
    rule_type: str = Field(..., pattern=r'^(exact|keyword|pattern)$', description="Rule type: exact, keyword, or pattern")
    category: str = Field(..., min_length=1, max_length=100, description="Category name")
    pattern: str = Field(..., min_length=1, max_length=500, description="Pattern to match")
    weight: int = Field(85, ge=1, le=100, description="Rule weight (1-100)")
    priority: int = Field(0, ge=0, le=1000, description="Rule priority (0-1000)")
    comments: Optional[str] = Field(None, max_length=1000, description="Rule comments")
    created_by: Optional[str] = Field(None, max_length=100, description="Creator identifier")

    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, v, info):
        if not v.strip():
            raise ValueError('Pattern cannot be empty or whitespace only')
        
        rule_type = info.data.get('rule_type')
        if rule_type == 'pattern':
            import re
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f'Invalid regex pattern: {str(e)}')
        
        return v.strip()


class MatchingRuleUpdate(BaseModel):
    rule_type: Optional[str] = Field(None, pattern=r'^(exact|keyword|pattern)$', description="Rule type")
    category: Optional[str] = Field(None, min_length=1, max_length=100, description="Category name")
    pattern: Optional[str] = Field(None, min_length=1, max_length=500, description="Pattern to match")
    weight: Optional[int] = Field(None, ge=1, le=100, description="Rule weight (1-100)")
    priority: Optional[int] = Field(None, ge=0, le=1000, description="Rule priority (0-1000)")
    comments: Optional[str] = Field(None, max_length=1000, description="Rule comments")
    is_active: Optional[bool] = Field(None, description="Whether the rule is active")

    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, v, info):
        if v is not None:
            if not v.strip():
                raise ValueError('Pattern cannot be empty or whitespace only')
            
            rule_type = info.data.get('rule_type')
            if rule_type == 'pattern':
                import re
                try:
                    re.compile(v)
                except re.error as e:
                    raise ValueError(f'Invalid regex pattern: {str(e)}')
            
            return v.strip()
        return v


class MatchingRuleResponse(BaseModel):
    id: int
    rule_type: str
    category: str
    pattern: str
    weight: int
    priority: int
    is_active: bool
    comments: Optional[str] = None
    created_by: Optional[str] = None
    created_at: str
    updated_at: str
    usage_count: int
    success_count: int
    last_used: Optional[str] = None


class RulePriorityUpdate(BaseModel):
    rule_id: int
    priority: int


class RuleTestRequest(BaseModel):
    rule_id: int
    test_strings: List[str]


class RuleTestResponse(BaseModel):
    test_string: str
    matches: bool
    confidence: float
    rule_pattern: str
    rule_type: str


class RuleValidationRequest(BaseModel):
    rule_type: str
    pattern: str


class RuleValidationResponse(BaseModel):
    is_valid: bool
    message: str


class RunMatcherRequest(BaseModel):
    operation_ids: Optional[List[int]] = None  # If None, process all unclassified operations
    auto_assign_high_confidence: bool = True


class RunMatcherResponse(BaseModel):
    success: bool
    message: str
    processed: int
    classified: int
    remaining: int
    details: Optional[List[dict]] = None
    error: Optional[str] = None


# Pagination models
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number (1-based)")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# Search and filtering models
class RuleSearchParams(BaseModel):
    search: Optional[str] = Field(None, max_length=200, description="Search term for pattern or category")
    rule_type: Optional[str] = Field(None, pattern=r'^(exact|keyword|pattern)$', description="Filter by rule type")
    category: Optional[str] = Field(None, max_length=100, description="Filter by category")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    min_weight: Optional[int] = Field(None, ge=1, le=100, description="Minimum weight filter")
    max_weight: Optional[int] = Field(None, ge=1, le=100, description="Maximum weight filter")


def _auth_db_path_or_url() -> str:
    """Return DB URL for production or local SQLite path for dev."""
    db_url = os.getenv("DATABASE_URL")
    if os.getenv("ENVIRONMENT") == "production" and db_url:
        return db_url
    return str(Path(__file__).parent / "db.sqlite")


# Dependency to get database session
def get_session():
    engine = get_engine(_auth_db_path_or_url())
    with Session(engine) as session:
        yield session


# Authentication dependency for rules API
def get_current_user_with_db_path(credentials = Depends(security)):
    """Dependency to get current user with correct database path or URL."""
    return get_current_user(credentials, db_path=_auth_db_path_or_url())


# Category endpoints
@router.post("/categories", response_model=RuleCategoryResponse)
def create_category(
    category: RuleCategoryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Create a new rule category"""
    try:
        # Check if category already exists
        existing = get_rule_category_by_name(session, category.name)
        if existing:
            raise HTTPException(status_code=400, detail="Category already exists")
        
        db_category = create_rule_category(
            session, category.name, category.description, category.color
        )
        return RuleCategoryResponse(**db_category.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=PaginatedResponse)
def list_categories(
    active_only: bool = True,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get all rule categories with pagination"""
    try:
        categories = get_rule_categories(session, active_only=active_only)
        
        # Apply pagination
        total = len(categories)
        start = pagination.offset
        end = start + pagination.page_size
        paginated_categories = categories[start:end]
        
        total_pages = (total + pagination.page_size - 1) // pagination.page_size
        
        return PaginatedResponse(
            items=[RuleCategoryResponse(**cat.__dict__) for cat in paginated_categories],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/{category_id}", response_model=RuleCategoryResponse)
def get_category(
    category_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get a specific rule category"""
    try:
        category = get_rule_category_by_id(session, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return RuleCategoryResponse(**category.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/categories/{category_id}", response_model=RuleCategoryResponse)
def update_category(
    category_id: int,
    category_update: RuleCategoryUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Update a rule category"""
    try:
        updated_category = update_rule_category(
            session, category_id,
            name=category_update.name,
            description=category_update.description,
            color=category_update.color,
            is_active=category_update.is_active
        )
        if not updated_category:
            raise HTTPException(status_code=404, detail="Category not found")
        return RuleCategoryResponse(**updated_category.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Delete a rule category"""
    try:
        success = delete_rule_category(session, category_id)
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete category that has rules"
            )
        return {"message": "Category deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Rule endpoints
@router.post("/rules", response_model=MatchingRuleResponse)
def create_rule(
    rule: MatchingRuleCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Create a new matching rule"""
    try:
        # Validate the rule pattern
        is_valid, message = validate_rule_pattern(rule.rule_type, rule.pattern)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        # Set created_by to current user if not provided
        created_by = rule.created_by or current_user.email
        
        db_rule = create_matching_rule(
            session, rule.rule_type, rule.category, rule.pattern,
            rule.weight, rule.priority, rule.comments, created_by
        )
        return MatchingRuleResponse(**db_rule.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules", response_model=PaginatedResponse)
def list_rules(
    search_params: RuleSearchParams = Depends(),
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get matching rules with search, filtering, and pagination"""
    try:
        # Get all rules first (we'll implement filtering in rules_manager later)
        rules = get_matching_rules(
            session, 
            rule_type=search_params.rule_type, 
            category=search_params.category, 
            active_only=search_params.is_active if search_params.is_active is not None else True
        )
        
        # Apply search filter if provided
        if search_params.search:
            search_term = search_params.search.lower()
            rules = [
                rule for rule in rules 
                if search_term in rule.pattern.lower() or search_term in rule.category.lower()
            ]
        
        # Apply weight filters
        if search_params.min_weight is not None:
            rules = [rule for rule in rules if rule.weight >= search_params.min_weight]
        if search_params.max_weight is not None:
            rules = [rule for rule in rules if rule.weight <= search_params.max_weight]
        
        # Apply pagination
        total = len(rules)
        start = pagination.offset
        end = start + pagination.page_size
        paginated_rules = rules[start:end]
        
        total_pages = (total + pagination.page_size - 1) // pagination.page_size
        
        return PaginatedResponse(
            items=[MatchingRuleResponse(**rule.__dict__) for rule in paginated_rules],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules/{rule_id}", response_model=MatchingRuleResponse)
def get_rule(
    rule_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get a specific matching rule"""
    try:
        rule = get_matching_rule_by_id(session, rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        return MatchingRuleResponse(**rule.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rules/{rule_id}", response_model=MatchingRuleResponse)
def update_rule(
    rule_id: int,
    rule_update: MatchingRuleUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Update a matching rule"""
    try:
        # Validate pattern if it's being updated
        if rule_update.pattern:
            is_valid, message = validate_rule_pattern(
                rule_update.rule_type or "keyword", rule_update.pattern
            )
            if not is_valid:
                raise HTTPException(status_code=400, detail=message)
        
        updated_rule = update_matching_rule(
            session, rule_id,
            rule_type=rule_update.rule_type,
            category=rule_update.category,
            pattern=rule_update.pattern,
            weight=rule_update.weight,
            priority=rule_update.priority,
            comments=rule_update.comments,
            is_active=rule_update.is_active
        )
        if not updated_rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        return MatchingRuleResponse(**updated_rule.__dict__)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rules/{rule_id}")
def delete_rule(
    rule_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Delete a matching rule"""
    try:
        success = delete_matching_rule(session, rule_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete rule")
        return {"message": "Rule deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules/bulk-priority")
def bulk_update_priorities(
    updates: List[RulePriorityUpdate],
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Bulk update rule priorities"""
    try:
        rule_updates = [(update.rule_id, update.priority) for update in updates]
        updated_count = bulk_update_rule_priorities(session, rule_updates)
        return {"message": f"Updated {updated_count} rules", "updated_count": updated_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Testing and validation endpoints
@router.post("/rules/{rule_id}/test", response_model=List[RuleTestResponse])
def test_rule(
    rule_id: int,
    test_request: RuleTestRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Test a rule pattern against test strings"""
    try:
        results = run_rule_pattern_test(session, rule_id, test_request.test_strings)
        return [
            RuleTestResponse(**result) for result in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules/validate", response_model=RuleValidationResponse)
def validate_rule_pattern_endpoint(
    validation_request: RuleValidationRequest,
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Validate a rule pattern"""
    try:
        is_valid, message = validate_rule_pattern(
            validation_request.rule_type, validation_request.pattern
        )
        return RuleValidationResponse(is_valid=is_valid, message=message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Statistics endpoints
@router.get("/rules/{rule_id}/statistics")
def get_rule_stats(
    rule_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get statistics for a specific rule"""
    try:
        stats = get_rule_statistics(session, rule_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Rule not found")
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/{category_name}/statistics")
def get_category_stats(
    category_name: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get statistics for a specific category"""
    try:
        stats = get_category_statistics(session, category_name)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Rules matcher endpoint
@router.post("/run-matcher", response_model=RunMatcherResponse)
def run_rules_matcher(
    request: RunMatcherRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Run the rules matcher on unclassified operations"""
    try:
        # Get operations to process
        if request.operation_ids:
            # Process specific operations
            operations = []
            for op_id in request.operation_ids:
                op = session.exec(select(OperationRow).where(OperationRow.id == op_id)).first()
                if op and op.type_id is None:
                    operations.append(op)
        else:
            # Process all unclassified operations
            operations = get_operations_with_null_types(session)
        
        if not operations:
            return RunMatcherResponse(
                success=True,
                message="No unclassified operations found",
                processed=0,
                classified=0,
                remaining=0
            )
        
        # Get operation types for mapping
        operation_types = get_operation_types(session)
        type_name_to_id = {ot.name: ot.id for ot in operation_types}
        
        # Get all active rules
        rules = get_matching_rules(session, active_only=True)
        
        processed = 0
        classified = 0
        details = []
        
        for operation in operations:
            processed += 1
            best_match = None
            best_confidence = 0
            
            # Try to match the operation description against all rules
            for rule in rules:
                if not operation.description:
                    continue
                
                confidence = 0
                matches = False
                
                if rule.rule_type == 'exact':
                    if operation.description.lower() == rule.pattern.lower():
                        matches = True
                        confidence = rule.weight
                elif rule.rule_type == 'keyword':
                    if rule.pattern.lower() in operation.description.lower():
                        matches = True
                        confidence = rule.weight
                elif rule.rule_type == 'pattern':
                    import re
                    try:
                        if re.search(rule.pattern, operation.description, re.IGNORECASE):
                            matches = True
                            confidence = rule.weight
                    except re.error:
                        continue
                
                if matches and confidence > best_confidence:
                    best_match = rule
                    best_confidence = confidence
            
            # Auto-assign if confidence is high enough
            if best_match and best_confidence >= 80:  # High confidence threshold
                type_id = type_name_to_id.get(best_match.category)
                if type_id:
                    assign_operation_type(session, operation.id, type_id)
                    classified += 1
                    
                    # Log the match
                    log_rule_match(
                        session, best_match.id, operation.description or '',
                        best_match.category, best_confidence, best_match.rule_type
                    )
                    
                    details.append({
                        'operation_id': operation.id,
                        'description': operation.description,
                        'matched_category': best_match.category,
                        'confidence': best_confidence,
                        'rule_pattern': best_match.pattern,
                        'rule_type': best_match.rule_type
                    })
        
        remaining = processed - classified
        
        return RunMatcherResponse(
            success=True,
            message=f"Successfully processed {processed} operations. {classified} were automatically classified.",
            processed=processed,
            classified=classified,
            remaining=remaining,
            details=details
        )
        
    except Exception as e:
        return RunMatcherResponse(
            success=False,
            message="Error running rules matcher",
            processed=0,
            classified=0,
            remaining=0,
            error=str(e)
        )
