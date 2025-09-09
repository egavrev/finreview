"""
Rules management functions for the database-driven operations matching system.
This module provides CRUD operations for managing matching rules and categories.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlmodel import Session, select, update, delete
from rules_models import MatchingRule, RuleCategory, RuleMatchLog


# Rule Category Management
def create_rule_category(
    session: Session,
    name: str,
    description: Optional[str] = None,
    color: Optional[str] = None
) -> RuleCategory:
    """Create a new rule category"""
    category = RuleCategory(
        name=name,
        description=description,
        color=color
    )
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def get_rule_categories(session: Session, active_only: bool = True) -> List[RuleCategory]:
    """Get all rule categories, optionally filtered by active status"""
    query = select(RuleCategory)
    if active_only:
        query = query.where(RuleCategory.is_active == True)
    query = query.order_by(RuleCategory.name)
    return list(session.exec(query))


def get_rule_category_by_id(session: Session, category_id: int) -> Optional[RuleCategory]:
    """Get a rule category by ID"""
    return session.exec(select(RuleCategory).where(RuleCategory.id == category_id)).first()


def get_rule_category_by_name(session: Session, name: str) -> Optional[RuleCategory]:
    """Get a rule category by name"""
    return session.exec(select(RuleCategory).where(RuleCategory.name == name)).first()


def update_rule_category(
    session: Session,
    category_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    color: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Optional[RuleCategory]:
    """Update a rule category"""
    category = get_rule_category_by_id(session, category_id)
    if category:
        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
        if color is not None:
            category.color = color
        if is_active is not None:
            category.is_active = is_active
        
        category.updated_at = datetime.now().isoformat()
        session.add(category)
        session.commit()
        session.refresh(category)
    return category


def delete_rule_category(session: Session, category_id: int) -> bool:
    """Delete a rule category (only if no rules are using it)"""
    category = get_rule_category_by_id(session, category_id)
    if category:
        # Check if any rules are using this category
        rules_using_category = session.exec(
            select(MatchingRule).where(MatchingRule.category == category.name)
        ).first()
        
        if rules_using_category:
            return False  # Cannot delete if rules are using this category
        
        session.delete(category)
        session.commit()
        return True
    return False


# Matching Rule Management
def create_matching_rule(
    session: Session,
    rule_type: str,
    category: str,
    pattern: str,
    weight: int = 85,
    priority: int = 0,
    comments: Optional[str] = None,
    created_by: Optional[str] = None
) -> MatchingRule:
    """Create a new matching rule"""
    rule = MatchingRule(
        rule_type=rule_type,
        category=category,
        pattern=pattern,
        weight=weight,
        priority=priority,
        comments=comments,
        created_by=created_by
    )
    session.add(rule)
    session.commit()
    session.refresh(rule)
    return rule


def get_matching_rules(
    session: Session,
    rule_type: Optional[str] = None,
    category: Optional[str] = None,
    active_only: bool = True
) -> List[MatchingRule]:
    """Get matching rules with optional filtering"""
    query = select(MatchingRule)
    
    if rule_type:
        query = query.where(MatchingRule.rule_type == rule_type)
    if category:
        query = query.where(MatchingRule.category == category)
    if active_only:
        query = query.where(MatchingRule.is_active == True)
    
    query = query.order_by(MatchingRule.priority.desc(), MatchingRule.weight.desc())
    return list(session.exec(query))


def get_matching_rule_by_id(session: Session, rule_id: int) -> Optional[MatchingRule]:
    """Get a matching rule by ID"""
    return session.exec(select(MatchingRule).where(MatchingRule.id == rule_id)).first()


def update_matching_rule(
    session: Session,
    rule_id: int,
    rule_type: Optional[str] = None,
    category: Optional[str] = None,
    pattern: Optional[str] = None,
    weight: Optional[int] = None,
    priority: Optional[int] = None,
    comments: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Optional[MatchingRule]:
    """Update a matching rule"""
    rule = get_matching_rule_by_id(session, rule_id)
    if rule:
        if rule_type is not None:
            rule.rule_type = rule_type
        if category is not None:
            rule.category = category
        if pattern is not None:
            rule.pattern = pattern
        if weight is not None:
            rule.weight = weight
        if priority is not None:
            rule.priority = priority
        if comments is not None:
            rule.comments = comments
        if is_active is not None:
            rule.is_active = is_active
        
        rule.updated_at = datetime.now().isoformat()
        session.add(rule)
        session.commit()
        session.refresh(rule)
    return rule


def delete_matching_rule(session: Session, rule_id: int) -> bool:
    """Delete a matching rule"""
    rule = get_matching_rule_by_id(session, rule_id)
    if rule:
        session.delete(rule)
        session.commit()
        return True
    return False


def bulk_update_rule_priorities(
    session: Session,
    rule_updates: List[Tuple[int, int]]
) -> int:
    """Bulk update rule priorities (rule_id, new_priority)"""
    updated_count = 0
    for rule_id, new_priority in rule_updates:
        rule = get_matching_rule_by_id(session, rule_id)
        if rule:
            rule.priority = new_priority
            rule.updated_at = datetime.now().isoformat()
            session.add(rule)
            updated_count += 1
    
    if updated_count > 0:
        session.commit()
    
    return updated_count


# Rule Usage Tracking
def log_rule_match(
    session: Session,
    rule_id: int,
    operation_description: str,
    matched_type: str,
    confidence: float,
    method: str,
    success: bool = True
) -> RuleMatchLog:
    """Log a rule match for analytics and learning"""
    log_entry = RuleMatchLog(
        rule_id=rule_id,
        operation_description=operation_description,
        matched_type=matched_type,
        confidence=confidence,
        method=method,
        success=success
    )
    session.add(log_entry)
    
    # Update rule usage statistics
    rule = get_matching_rule_by_id(session, rule_id)
    if rule:
        rule.usage_count += 1
        if success:
            rule.success_count += 1
        rule.last_used = datetime.now().isoformat()
        session.add(rule)
    
    session.commit()
    session.refresh(log_entry)
    return log_entry


def get_rule_statistics(session: Session, rule_id: int) -> Dict[str, Any]:
    """Get statistics for a specific rule"""
    rule = get_matching_rule_by_id(session, rule_id)
    if not rule:
        return {}
    
    # Get recent match logs
    recent_matches = session.exec(
        select(RuleMatchLog)
        .where(RuleMatchLog.rule_id == rule_id)
        .order_by(RuleMatchLog.timestamp.desc())
        .limit(100)
    ).all()
    
    success_rate = (rule.success_count / rule.usage_count * 100) if rule.usage_count > 0 else 0
    
    return {
        'rule_id': rule.id,
        'pattern': rule.pattern,
        'category': rule.category,
        'usage_count': rule.usage_count,
        'success_count': rule.success_count,
        'success_rate': round(success_rate, 2),
        'last_used': rule.last_used,
        'recent_matches': [
            {
                'operation_description': match.operation_description,
                'confidence': match.confidence,
                'method': match.method,
                'success': match.success,
                'timestamp': match.timestamp
            }
            for match in recent_matches
        ]
    }


def get_category_statistics(session: Session, category_name: str) -> Dict[str, Any]:
    """Get statistics for a specific category"""
    rules = get_matching_rules(session, category=category_name)
    
    total_rules = len(rules)
    active_rules = len([r for r in rules if r.is_active])
    total_usage = sum(r.usage_count for r in rules)
    total_success = sum(r.success_count for r in rules)
    
    success_rate = (total_success / total_usage * 100) if total_usage > 0 else 0
    
    return {
        'category': category_name,
        'total_rules': total_rules,
        'active_rules': active_rules,
        'total_usage': total_usage,
        'total_success': total_success,
        'success_rate': round(success_rate, 2),
        'rules': [
            {
                'id': rule.id,
                'rule_type': rule.rule_type,
                'pattern': rule.pattern,
                'weight': rule.weight,
                'priority': rule.priority,
                'is_active': rule.is_active,
                'usage_count': rule.usage_count,
                'success_rate': round((rule.success_count / rule.usage_count * 100) if rule.usage_count > 0 else 0, 2)
            }
            for rule in rules
        ]
    }


# Rule Testing and Validation
def run_rule_pattern_test(
    session: Session,
    rule_id: int,
    test_strings: List[str]
) -> List[Dict[str, Any]]:
    """Test a rule pattern against a list of test strings"""
    rule = get_matching_rule_by_id(session, rule_id)
    if not rule:
        return []
    
    results = []
    
    for test_string in test_strings:
        matches = False
        confidence = 0
        
        if rule.rule_type == 'exact':
            matches = test_string.lower() == rule.pattern.lower()
            confidence = 100 if matches else 0
        elif rule.rule_type == 'keyword':
            matches = rule.pattern.lower() in test_string.lower()
            confidence = rule.weight if matches else 0
        elif rule.rule_type == 'pattern':
            import re
            try:
                matches = bool(re.search(rule.pattern, test_string, re.IGNORECASE))
                confidence = rule.weight if matches else 0
            except re.error:
                matches = False
                confidence = 0
        
        results.append({
            'test_string': test_string,
            'matches': matches,
            'confidence': confidence,
            'rule_pattern': rule.pattern,
            'rule_type': rule.rule_type
        })
    
    return results


def validate_rule_pattern(rule_type: str, pattern: str) -> Tuple[bool, str]:
    """Validate a rule pattern based on its type"""
    if rule_type == 'exact':
        if not pattern.strip():
            return False, "Exact pattern cannot be empty"
        return True, "Valid exact pattern"
    
    elif rule_type == 'keyword':
        if not pattern.strip():
            return False, "Keyword pattern cannot be empty"
        return True, "Valid keyword pattern"
    
    elif rule_type == 'pattern':
        if not pattern.strip():
            return False, "Regex pattern cannot be empty"
        try:
            import re
            re.compile(pattern)
            return True, "Valid regex pattern"
        except re.error as e:
            return False, f"Invalid regex pattern: {str(e)}"
    
    else:
        return False, f"Unknown rule type: {rule_type}"
