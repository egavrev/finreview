from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class MatchingRule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rule_type: str = Field(index=True)  # 'exact', 'keyword', 'pattern'
    category: str = Field(index=True)   # 'Food', 'Healthcare', etc.
    pattern: str  # The actual rule pattern (exact string, keyword, or regex)
    weight: int = Field(default=85)     # Confidence weight (0-100)
    is_active: bool = Field(default=True, index=True)
    priority: int = Field(default=0, index=True)  # Higher priority rules are checked first
    comments: Optional[str] = None  # Optional comments/notes for the rule
    created_by: Optional[str] = None
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = Field(default=0)  # How many times this rule has been used
    success_count: int = Field(default=0)  # How many times it successfully classified
    last_used: Optional[str] = None


class RuleCategory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    color: Optional[str] = None  # Hex color for UI display
    is_active: bool = Field(default=True, index=True)
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())


class RuleMatchLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rule_id: Optional[int] = Field(default=None, foreign_key="matchingrule.id")
    operation_description: str
    matched_type: str
    confidence: float
    method: str  # 'exact', 'fuzzy', 'keyword', 'pattern'
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    success: bool = Field(default=True)  # Whether the classification was correct
