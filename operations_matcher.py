"""
Operations Matcher Module

This module implements a hybrid rule-based classification system for automatically
classifying financial operations based on their descriptions.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from functools import lru_cache
import difflib
from collections import defaultdict


@dataclass
class MatchResult:
    """Result of a matching operation"""
    type_name: str
    confidence: float
    method: str  # 'exact', 'fuzzy', 'keyword', 'pattern'
    details: Dict[str, Any]


@dataclass
class ClassificationSuggestion:
    """Suggestion for operation classification"""
    operation_id: int
    type_name: str
    confidence: float
    method: str
    details: Dict[str, Any]
    should_auto_assign: bool


class OperationsMatcher:
    """Hybrid rule-based operations classifier"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the matcher with configuration"""
        self.config_path = config_path or "config/operations_matching.yaml"
        self.config = self._load_config()
        self.exact_match_cache = {}
        self.fuzzy_match_cache = {}
        self.learned_patterns = defaultdict(list)
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _normalize_description(self, description: str) -> str:
        """Normalize description for comparison"""
        if not description:
            return ""
        
        # Convert to uppercase and remove extra whitespace
        normalized = description.upper().strip()
        # Normalize spaces but preserve dots, hyphens, and other important characters
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized.strip()
    
    def exact_match(self, description: str) -> Optional[MatchResult]:
        """Exact match layer - direct string comparison"""
        normalized_desc = self._normalize_description(description)
        
        # Check cache first
        if normalized_desc in self.exact_match_cache:
            return self.exact_match_cache[normalized_desc]
        
        exact_matches = self.config.get('exact_matches', {})
        
        # Direct match - normalize config keys for comparison
        for pattern, type_name in exact_matches.items():
            normalized_pattern = self._normalize_description(pattern)
            if normalized_desc == normalized_pattern:
                result = MatchResult(
                    type_name=type_name,
                    confidence=100.0,
                    method='exact',
                    details={'matched_description': normalized_desc}
                )
                self.exact_match_cache[normalized_desc] = result
                return result
        
        # Check for partial matches (exact substring)
        for pattern, type_name in exact_matches.items():
            normalized_pattern = self._normalize_description(pattern)
            if normalized_pattern in normalized_desc or normalized_desc in normalized_pattern:
                result = MatchResult(
                    type_name=type_name,
                    confidence=95.0,
                    method='exact',
                    details={'matched_pattern': pattern, 'description': normalized_desc}
                )
                self.exact_match_cache[normalized_desc] = result
                return result
        
        # No match found
        self.exact_match_cache[normalized_desc] = None
        return None
    
    def fuzzy_match(self, description: str) -> Optional[MatchResult]:
        """Fuzzy match layer - string similarity"""
        normalized_desc = self._normalize_description(description)
        
        # Check cache first
        if normalized_desc in self.fuzzy_match_cache:
            return self.fuzzy_match_cache[normalized_desc]
        
        exact_matches = self.config.get('exact_matches', {})
        fuzzy_config = self.config.get('fuzzy_matching', {})
        min_similarity = fuzzy_config.get('min_similarity', 85)
        max_candidates = fuzzy_config.get('max_candidates', 5)
        
        best_match = None
        best_similarity = 0
        
        # Compare with all exact match patterns
        for pattern, type_name in exact_matches.items():
            similarity = self._calculate_similarity(normalized_desc, pattern)
            
            if similarity > best_similarity and similarity >= min_similarity:
                best_similarity = similarity
                best_match = MatchResult(
                    type_name=type_name,
                    confidence=similarity,
                    method='fuzzy',
                    details={
                        'matched_pattern': pattern,
                        'similarity': similarity,
                        'description': normalized_desc
                    }
                )
        
        self.fuzzy_match_cache[normalized_desc] = best_match
        return best_match
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using multiple algorithms"""
        if not str1 or not str2:
            return 0.0
        
        # Use difflib for sequence matching
        similarity = difflib.SequenceMatcher(None, str1, str2).ratio()
        
        # Convert to percentage
        return similarity * 100
    
    def keyword_match(self, description: str) -> Optional[MatchResult]:
        """Keyword match layer - keyword-based classification"""
        normalized_desc = self._normalize_description(description)
        keyword_matches = self.config.get('keyword_matches', {})
        
        best_match = None
        best_score = 0
        
        for category, config in keyword_matches.items():
            keywords = config.get('keywords', [])
            weight = config.get('weight', 70)
            type_name = config.get('type', category)
            
            # Count matching keywords
            matched_keywords = []
            for keyword in keywords:
                if keyword.upper() in normalized_desc:
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                # Calculate score based on number of matched keywords and weight
                score = min(weight + (len(matched_keywords) * 5), 95)
                
                if score > best_score:
                    best_score = score
                    best_match = MatchResult(
                        type_name=type_name,
                        confidence=score,
                        method='keyword',
                        details={
                            'matched_keywords': matched_keywords,
                            'total_keywords': len(keywords),
                            'category': category,
                            'description': normalized_desc
                        }
                    )
        
        return best_match
    
    def pattern_match(self, description: str) -> Optional[MatchResult]:
        """Pattern match layer - regular expression matching"""
        normalized_desc = self._normalize_description(description)
        pattern_matches = self.config.get('pattern_matches', {})
        
        best_match = None
        best_score = 0
        
        for category, config in pattern_matches.items():
            patterns = config.get('patterns', [])
            weight = config.get('weight', 60)
            type_name = config.get('type', category)
            
            matched_patterns = []
            for pattern in patterns:
                try:
                    if re.search(pattern, normalized_desc, re.IGNORECASE):
                        matched_patterns.append(pattern)
                except re.error:
                    continue  # Skip invalid patterns
            
            if matched_patterns:
                # Calculate score based on number of matched patterns and weight
                score = min(weight + (len(matched_patterns) * 3), 90)
                
                if score > best_score:
                    best_score = score
                    best_match = MatchResult(
                        type_name=type_name,
                        confidence=score,
                        method='pattern',
                        details={
                            'matched_patterns': matched_patterns,
                            'total_patterns': len(patterns),
                            'category': category,
                            'description': normalized_desc
                        }
                    )
        
        return best_match
    
    def classify_operation(self, description: str) -> Optional[MatchResult]:
        """Classify an operation using the hybrid approach"""
        if not description:
            return None
        
        # Layer 1: Exact Match
        result = self.exact_match(description)
        if result:
            return result
        
        # Layer 2: Fuzzy Match
        result = self.fuzzy_match(description)
        if result and result.confidence >= self.config['confidence_thresholds']['fuzzy_match_auto']:
            return result
        
        # Layer 3: Keyword Match
        result = self.keyword_match(description)
        if result and result.confidence >= self.config['confidence_thresholds']['keyword_match_auto']:
            return result
        
        # Layer 4: Pattern Match
        result = self.pattern_match(description)
        if result and result.confidence >= self.config['confidence_thresholds']['pattern_match_auto']:
            return result
        
        # Return the best result from lower confidence matches
        candidates = []
        
        fuzzy_result = self.fuzzy_match(description)
        if fuzzy_result:
            candidates.append(fuzzy_result)
        
        keyword_result = self.keyword_match(description)
        if keyword_result:
            candidates.append(keyword_result)
        
        pattern_result = self.pattern_match(description)
        if pattern_result:
            candidates.append(pattern_result)
        
        if candidates:
            return max(candidates, key=lambda x: x.confidence)
        
        return None
    
    def get_classification_suggestions(self, operations: List[Tuple[int, str]]) -> List[ClassificationSuggestion]:
        """Get classification suggestions for a list of operations"""
        suggestions = []
        thresholds = self.config['confidence_thresholds']
        
        for operation_id, description in operations:
            result = self.classify_operation(description)
            
            if result:
                # Determine if should auto-assign based on confidence
                should_auto_assign = False
                
                if result.method == 'exact':
                    should_auto_assign = True
                elif result.method == 'fuzzy' and result.confidence >= thresholds['fuzzy_match_auto']:
                    should_auto_assign = True
                elif result.method == 'keyword' and result.confidence >= thresholds['keyword_match_auto']:
                    should_auto_assign = True
                elif result.method == 'pattern' and result.confidence >= thresholds['pattern_match_auto']:
                    should_auto_assign = True
                
                suggestion = ClassificationSuggestion(
                    operation_id=operation_id,
                    type_name=result.type_name,
                    confidence=result.confidence,
                    method=result.method,
                    details=result.details,
                    should_auto_assign=should_auto_assign
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def learn_from_correction(self, description: str, correct_type: str, user_confidence: float = 90):
        """Learn from user corrections to improve future matching"""
        if not self.config.get('learning', {}).get('track_success', False):
            return
        
        normalized_desc = self._normalize_description(description)
        min_confidence = self.config['learning']['min_confidence_for_learning']
        max_patterns = self.config['learning']['max_learned_patterns']
        
        if user_confidence >= min_confidence:
            # Add to learned patterns
            self.learned_patterns[correct_type].append({
                'pattern': normalized_desc,
                'confidence': user_confidence,
                'count': 1
            })
            
            # Limit the number of learned patterns
            if len(self.learned_patterns[correct_type]) > max_patterns:
                # Keep the most confident patterns
                self.learned_patterns[correct_type].sort(
                    key=lambda x: (x['confidence'], x['count']), 
                    reverse=True
                )
                self.learned_patterns[correct_type] = self.learned_patterns[correct_type][:max_patterns]
    
    def get_learned_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all learned patterns"""
        return dict(self.learned_patterns)
    
    def clear_caches(self):
        """Clear all caches"""
        self.exact_match_cache.clear()
        self.fuzzy_match_cache.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get matching statistics"""
        return {
            'exact_match_cache_size': len(self.exact_match_cache),
            'fuzzy_match_cache_size': len(self.fuzzy_match_cache),
            'learned_patterns_count': sum(len(patterns) for patterns in self.learned_patterns.values()),
            'total_exact_matches': len(self.config.get('exact_matches', {})),
            'total_keyword_categories': len(self.config.get('keyword_matches', {})),
            'total_pattern_categories': len(self.config.get('pattern_matches', {}))
        }


# Global matcher instance
_global_matcher: Optional[OperationsMatcher] = None


def get_matcher(config_path: Optional[str] = None) -> OperationsMatcher:
    """Get or create the global matcher instance"""
    global _global_matcher
    if _global_matcher is None:
        _global_matcher = OperationsMatcher(config_path)
    return _global_matcher


def classify_operation(description: str, config_path: Optional[str] = None) -> Optional[MatchResult]:
    """Convenience function to classify a single operation"""
    matcher = get_matcher(config_path)
    return matcher.classify_operation(description)


def get_classification_suggestions(operations: List[Tuple[int, str]], config_path: Optional[str] = None) -> List[ClassificationSuggestion]:
    """Convenience function to get classification suggestions"""
    matcher = get_matcher(config_path)
    return matcher.get_classification_suggestions(operations)
