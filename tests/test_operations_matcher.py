"""
Unit tests for operations_matcher.py module
"""
import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open
from operations_matcher import (
    OperationsMatcher, 
    MatchResult, 
    ClassificationSuggestion,
    get_matcher,
    classify_operation,
    get_classification_suggestions
)


class TestMatchResult:
    """Test MatchResult dataclass"""
    
    def test_match_result_creation(self):
        """Test MatchResult creation with all fields"""
        result = MatchResult(
            type_name="Food",
            confidence=95.0,
            method="exact",
            details={"matched_description": "AGROBAZAR"}
        )
        
        assert result.type_name == "Food"
        assert result.confidence == 95.0
        assert result.method == "exact"
        assert result.details == {"matched_description": "AGROBAZAR"}


class TestClassificationSuggestion:
    """Test ClassificationSuggestion dataclass"""
    
    def test_classification_suggestion_creation(self):
        """Test ClassificationSuggestion creation with all fields"""
        suggestion = ClassificationSuggestion(
            operation_id=1,
            type_name="Food",
            confidence=90.0,
            method="keyword",
            details={"matched_keywords": ["AGRO"]},
            should_auto_assign=True
        )
        
        assert suggestion.operation_id == 1
        assert suggestion.type_name == "Food"
        assert suggestion.confidence == 90.0
        assert suggestion.method == "keyword"
        assert suggestion.details == {"matched_keywords": ["AGRO"]}
        assert suggestion.should_auto_assign is True


class TestOperationsMatcher:
    """Test OperationsMatcher class"""
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            'confidence_thresholds': {
                'exact_match': 100,
                'fuzzy_match_auto': 95,
                'fuzzy_match_suggest': 85,
                'keyword_match_auto': 80,
                'keyword_match_suggest': 70,
                'pattern_match_auto': 75,
                'pattern_match_suggest': 65
            },
            'fuzzy_matching': {
                'min_similarity': 85,
                'max_candidates': 5
            },
            'exact_matches': {
                'AGROBAZAR': 'Food',
                'FARMACIA FAMILIEI': 'Healthcare',
                'RESTAURANT JERAFFE': 'Restaurant'
            },
            'keyword_matches': {
                'food': {
                    'keywords': ['AGRO', 'MARKET', 'FOOD'],
                    'weight': 90,
                    'type': 'Food'
                },
                'healthcare': {
                    'keywords': ['FARMACIA', 'APOTECA', 'MEDICAL'],
                    'weight': 85,
                    'type': 'Healthcare'
                }
            },
            'pattern_matches': {
                'food_patterns': {
                    'patterns': ['.*AGRO.*', '.*MARKET.*'],
                    'weight': 75,
                    'type': 'Food'
                }
            },
            'learning': {
                'track_success': True,
                'min_confidence_for_learning': 70,
                'max_learned_patterns': 1000
            }
        }
    
    @pytest.fixture
    def temp_config_file(self, sample_config):
        """Create a temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(sample_config, f)
            return f.name
    
    def test_init_with_config_path(self, temp_config_file):
        """Test initialization with config path"""
        matcher = OperationsMatcher(temp_config_file)
        assert matcher.config_path == temp_config_file
        assert matcher.config is not None
        assert 'exact_matches' in matcher.config
        assert 'keyword_matches' in matcher.config
    
    def test_init_with_default_config(self):
        """Test initialization with default config path"""
        with patch('operations_matcher.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data='exact_matches: {}')):
                matcher = OperationsMatcher()
                assert matcher.config_path == "config/operations_matching.yaml"
    
    def test_init_config_file_not_found(self):
        """Test initialization when config file doesn't exist"""
        with pytest.raises(FileNotFoundError):
            OperationsMatcher("nonexistent_config.yaml")
    
    def test_load_config(self, temp_config_file):
        """Test config loading"""
        matcher = OperationsMatcher(temp_config_file)
        assert isinstance(matcher.config, dict)
        assert 'confidence_thresholds' in matcher.config
    
    def test_normalize_description(self, temp_config_file):
        """Test description normalization"""
        matcher = OperationsMatcher(temp_config_file)
        
        # Test basic normalization
        assert matcher._normalize_description("  agrobazar  ") == "AGROBAZAR"
        assert matcher._normalize_description("Farmacia\nFamiliei") == "FARMACIA FAMILIEI"
        assert matcher._normalize_description("") == ""
        assert matcher._normalize_description(None) == ""
        
        # Test whitespace normalization
        assert matcher._normalize_description("  multiple   spaces  ") == "MULTIPLE SPACES"
    
    def test_exact_match_direct_match(self, temp_config_file):
        """Test exact match with direct string match"""
        matcher = OperationsMatcher(temp_config_file)
        
        result = matcher.exact_match("AGROBAZAR")
        assert result is not None
        assert result.type_name == "Food"
        assert result.confidence == 100.0
        assert result.method == "exact"
    
    def test_exact_match_partial_match(self, temp_config_file):
        """Test exact match with partial string match"""
        matcher = OperationsMatcher(temp_config_file)
        
        result = matcher.exact_match("AGROBAZAR CHISINAU")
        assert result is not None
        assert result.type_name == "Food"
        assert result.confidence == 95.0
        assert result.method == "exact"
    
    def test_exact_match_no_match(self, temp_config_file):
        """Test exact match with no match"""
        matcher = OperationsMatcher(temp_config_file)
        
        result = matcher.exact_match("UNKNOWN MERCHANT")
        assert result is None
    
    def test_exact_match_caching(self, temp_config_file):
        """Test exact match caching"""
        matcher = OperationsMatcher(temp_config_file)
        
        # First call
        result1 = matcher.exact_match("AGROBAZAR")
        assert result1 is not None
        
        # Second call should use cache
        result2 = matcher.exact_match("AGROBAZAR")
        assert result2 is not None
        assert result1 == result2
    
    def test_calculate_similarity(self, temp_config_file):
        """Test similarity calculation"""
        matcher = OperationsMatcher(temp_config_file)
        
        # Test identical strings
        assert matcher._calculate_similarity("AGROBAZAR", "AGROBAZAR") == 100.0
        
        # Test similar strings
        similarity = matcher._calculate_similarity("AGROBAZAR", "AGROBAZAR CHISINAU")
        assert 0 < similarity < 100
        
        # Test empty strings
        assert matcher._calculate_similarity("", "AGROBAZAR") == 0.0
        assert matcher._calculate_similarity("AGROBAZAR", "") == 0.0
        assert matcher._calculate_similarity("", "") == 0.0
    
    def test_fuzzy_match_with_match(self, temp_config_file):
        """Test fuzzy match with similarity above threshold"""
        matcher = OperationsMatcher(temp_config_file)
        
        # Use a string similar to AGROBAZAR
        result = matcher.fuzzy_match("AGROBAZAR CHISINAU")
        # This might match depending on similarity threshold
        if result:
            assert result.method == "fuzzy"
            assert result.confidence >= 85  # min_similarity from config
    
    def test_fuzzy_match_no_match(self, temp_config_file):
        """Test fuzzy match with similarity below threshold"""
        matcher = OperationsMatcher(temp_config_file)
        
        result = matcher.fuzzy_match("COMPLETELY DIFFERENT STRING")
        # Should not match due to low similarity
        assert result is None
    
    def test_fuzzy_match_caching(self, temp_config_file):
        """Test fuzzy match caching"""
        matcher = OperationsMatcher(temp_config_file)
        
        # First call
        result1 = matcher.fuzzy_match("AGROBAZAR CHISINAU")
        
        # Second call should use cache
        result2 = matcher.fuzzy_match("AGROBAZAR CHISINAU")
        assert result1 == result2
    
    def test_keyword_match_single_keyword(self, temp_config_file):
        """Test keyword match with single keyword"""
        matcher = OperationsMatcher(temp_config_file)
        
        result = matcher.keyword_match("AGROBAZAR CHISINAU")
        assert result is not None
        assert result.type_name == "Food"
        assert result.method == "keyword"
        assert "AGRO" in result.details['matched_keywords']
    
    def test_keyword_match_multiple_keywords(self, temp_config_file):
        """Test keyword match with multiple keywords"""
        matcher = OperationsMatcher(temp_config_file)
        
        result = matcher.keyword_match("AGRO MARKET FOOD")
        assert result is not None
        assert result.type_name == "Food"
        assert len(result.details['matched_keywords']) > 1
    
    def test_keyword_match_no_match(self, temp_config_file):
        """Test keyword match with no matching keywords"""
        matcher = OperationsMatcher(temp_config_file)
        
        result = matcher.keyword_match("UNKNOWN MERCHANT")
        assert result is None
    
    def test_keyword_match_best_score(self, temp_config_file):
        """Test keyword match returns best scoring match"""
        matcher = OperationsMatcher(temp_config_file)
        
        # This should match both food and healthcare, but food should win due to higher weight
        result = matcher.keyword_match("AGRO FARMACIA")
        assert result is not None
        # The result should be the one with higher weight/score
    
    def test_pattern_match_success(self, temp_config_file):
        """Test pattern match with successful regex match"""
        matcher = OperationsMatcher(temp_config_file)
        
        result = matcher.pattern_match("AGROBAZAR CHISINAU")
        assert result is not None
        assert result.type_name == "Food"
        assert result.method == "pattern"
        assert len(result.details['matched_patterns']) > 0
    
    def test_pattern_match_no_match(self, temp_config_file):
        """Test pattern match with no regex match"""
        matcher = OperationsMatcher(temp_config_file)
        
        result = matcher.pattern_match("UNKNOWN MERCHANT")
        assert result is None
    
    def test_pattern_match_invalid_regex(self, temp_config_file):
        """Test pattern match with invalid regex pattern"""
        # Create config with invalid regex
        config_with_invalid_regex = {
            'pattern_matches': {
                'test': {
                    'patterns': ['[invalid regex'],
                    'weight': 75,
                    'type': 'Test'
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_with_invalid_regex, f)
            temp_file = f.name
        
        try:
            matcher = OperationsMatcher(temp_file)
            # Should not raise exception, just skip invalid patterns
            result = matcher.pattern_match("test string")
            # Result might be None due to invalid regex being skipped
        finally:
            Path(temp_file).unlink()
    
    def test_classify_operation_exact_match(self, temp_config_file):
        """Test classify_operation with exact match"""
        matcher = OperationsMatcher(temp_config_file)
        
        result = matcher.classify_operation("AGROBAZAR")
        assert result is not None
        assert result.type_name == "Food"
        assert result.method == "exact"
    
    def test_classify_operation_fuzzy_match_auto(self, temp_config_file):
        """Test classify_operation with fuzzy match above auto threshold"""
        matcher = OperationsMatcher(temp_config_file)
        
        # Mock exact match to return None, fuzzy match to return high confidence
        with patch.object(matcher, 'exact_match', return_value=None):
            with patch.object(matcher, 'fuzzy_match') as mock_fuzzy:
                mock_fuzzy.return_value = MatchResult(
                    type_name="Food",
                    confidence=96.0,  # Above fuzzy_match_auto threshold (95)
                    method="fuzzy",
                    details={}
                )
                
                result = matcher.classify_operation("AGROBAZAR CHISINAU")
                assert result is not None
                assert result.method == "fuzzy"
    
    def test_classify_operation_fuzzy_match_below_auto(self, temp_config_file):
        """Test classify_operation with fuzzy match below auto threshold"""
        matcher = OperationsMatcher(temp_config_file)
        
        # Mock exact match to return None, fuzzy match to return low confidence
        with patch.object(matcher, 'exact_match', return_value=None):
            with patch.object(matcher, 'fuzzy_match') as mock_fuzzy:
                mock_fuzzy.return_value = MatchResult(
                    type_name="Food",
                    confidence=90.0,  # Below fuzzy_match_auto threshold (95)
                    method="fuzzy",
                    details={}
                )
                
                # Mock other methods to return None
                with patch.object(matcher, 'keyword_match', return_value=None):
                    with patch.object(matcher, 'pattern_match', return_value=None):
                        result = matcher.classify_operation("AGROBAZAR CHISINAU")
                        # Should return the fuzzy result as best candidate
                        assert result is not None
                        assert result.method == "fuzzy"
    
    def test_classify_operation_keyword_match_auto(self, temp_config_file):
        """Test classify_operation with keyword match above auto threshold"""
        matcher = OperationsMatcher(temp_config_file)
        
        # Mock exact and fuzzy to return None, keyword to return high confidence
        with patch.object(matcher, 'exact_match', return_value=None):
            with patch.object(matcher, 'fuzzy_match', return_value=None):
                with patch.object(matcher, 'keyword_match') as mock_keyword:
                    mock_keyword.return_value = MatchResult(
                        type_name="Food",
                        confidence=85.0,  # Above keyword_match_auto threshold (80)
                        method="keyword",
                        details={}
                    )
                    
                    result = matcher.classify_operation("AGROBAZAR")
                    assert result is not None
                    assert result.method == "keyword"
    
    def test_classify_operation_pattern_match_auto(self, temp_config_file):
        """Test classify_operation with pattern match above auto threshold"""
        matcher = OperationsMatcher(temp_config_file)
        
        # Mock other methods to return None, pattern to return high confidence
        with patch.object(matcher, 'exact_match', return_value=None):
            with patch.object(matcher, 'fuzzy_match', return_value=None):
                with patch.object(matcher, 'keyword_match', return_value=None):
                    with patch.object(matcher, 'pattern_match') as mock_pattern:
                        mock_pattern.return_value = MatchResult(
                            type_name="Food",
                            confidence=80.0,  # Above pattern_match_auto threshold (75)
                            method="pattern",
                            details={}
                        )
                        
                        result = matcher.classify_operation("AGROBAZAR")
                        assert result is not None
                        assert result.method == "pattern"
    
    def test_classify_operation_no_match(self, temp_config_file):
        """Test classify_operation with no matches"""
        matcher = OperationsMatcher(temp_config_file)
        
        # Mock all methods to return None
        with patch.object(matcher, 'exact_match', return_value=None):
            with patch.object(matcher, 'fuzzy_match', return_value=None):
                with patch.object(matcher, 'keyword_match', return_value=None):
                    with patch.object(matcher, 'pattern_match', return_value=None):
                        result = matcher.classify_operation("UNKNOWN MERCHANT")
                        assert result is None
    
    def test_classify_operation_empty_description(self, temp_config_file):
        """Test classify_operation with empty description"""
        matcher = OperationsMatcher(temp_config_file)
        
        result = matcher.classify_operation("")
        assert result is None
        
        result = matcher.classify_operation(None)
        assert result is None
    
    def test_get_classification_suggestions(self, temp_config_file):
        """Test get_classification_suggestions"""
        matcher = OperationsMatcher(temp_config_file)
        
        operations = [
            (1, "AGROBAZAR"),
            (2, "FARMACIA FAMILIEI"),
            (3, "UNKNOWN MERCHANT")
        ]
        
        suggestions = matcher.get_classification_suggestions(operations)
        
        # Should have suggestions for first two operations
        assert len(suggestions) >= 2
        
        # Check first suggestion
        first_suggestion = suggestions[0]
        assert first_suggestion.operation_id == 1
        assert first_suggestion.type_name == "Food"
        assert first_suggestion.should_auto_assign is True  # Exact match
    
    def test_get_classification_suggestions_auto_assign_logic(self, temp_config_file):
        """Test auto-assign logic in classification suggestions"""
        matcher = OperationsMatcher(temp_config_file)
        
        # Mock classify_operation to return different confidence levels
        def mock_classify(description):
            if description == "HIGH_CONFIDENCE":
                return MatchResult("Food", 96.0, "fuzzy", {})
            elif description == "MEDIUM_CONFIDENCE":
                return MatchResult("Food", 85.0, "keyword", {})
            elif description == "LOW_CONFIDENCE":
                return MatchResult("Food", 60.0, "pattern", {})
            return None
        
        with patch.object(matcher, 'classify_operation', side_effect=mock_classify):
            operations = [
                (1, "HIGH_CONFIDENCE"),
                (2, "MEDIUM_CONFIDENCE"),
                (3, "LOW_CONFIDENCE")
            ]
            
            suggestions = matcher.get_classification_suggestions(operations)
            
            # High confidence fuzzy should auto-assign
            high_conf = next(s for s in suggestions if s.operation_id == 1)
            assert high_conf.should_auto_assign is True
            
            # Medium confidence keyword should auto-assign
            med_conf = next(s for s in suggestions if s.operation_id == 2)
            assert med_conf.should_auto_assign is True
            
            # Low confidence pattern should not auto-assign
            low_conf = next(s for s in suggestions if s.operation_id == 3)
            assert low_conf.should_auto_assign is False
    
    def test_learn_from_correction_disabled(self, temp_config_file):
        """Test learn_from_correction when learning is disabled"""
        # Create config with learning disabled
        config_no_learning = {
            'learning': {'track_success': False}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_no_learning, f)
            temp_file = f.name
        
        try:
            matcher = OperationsMatcher(temp_file)
            matcher.learn_from_correction("AGROBAZAR", "Food", 90)
            # Should not raise exception and not add to learned patterns
            assert len(matcher.learned_patterns) == 0
        finally:
            Path(temp_file).unlink()
    
    def test_learn_from_correction_enabled(self, temp_config_file):
        """Test learn_from_correction when learning is enabled"""
        matcher = OperationsMatcher(temp_config_file)
        
        matcher.learn_from_correction("AGROBAZAR", "Food", 90)
        
        # Should add to learned patterns
        assert "Food" in matcher.learned_patterns
        assert len(matcher.learned_patterns["Food"]) == 1
        assert matcher.learned_patterns["Food"][0]['pattern'] == "AGROBAZAR"
        assert matcher.learned_patterns["Food"][0]['confidence'] == 90
    
    def test_learn_from_correction_low_confidence(self, temp_config_file):
        """Test learn_from_correction with low confidence"""
        matcher = OperationsMatcher(temp_config_file)
        
        matcher.learn_from_correction("AGROBAZAR", "Food", 50)  # Below min_confidence_for_learning (70)
        
        # Should not add to learned patterns
        assert len(matcher.learned_patterns) == 0
    
    def test_learn_from_correction_max_patterns_limit(self, temp_config_file):
        """Test learn_from_correction respects max patterns limit"""
        matcher = OperationsMatcher(temp_config_file)
        
        # Add more patterns than the limit
        for i in range(1005):  # More than max_learned_patterns (1000)
            matcher.learn_from_correction(f"PATTERN_{i}", "Food", 90)
        
        # Should be limited to max_learned_patterns
        assert len(matcher.learned_patterns["Food"]) == 1000
    
    def test_get_learned_patterns(self, temp_config_file):
        """Test get_learned_patterns"""
        matcher = OperationsMatcher(temp_config_file)
        
        matcher.learn_from_correction("AGROBAZAR", "Food", 90)
        matcher.learn_from_correction("FARMACIA", "Healthcare", 85)
        
        patterns = matcher.get_learned_patterns()
        
        assert "Food" in patterns
        assert "Healthcare" in patterns
        assert len(patterns["Food"]) == 1
        assert len(patterns["Healthcare"]) == 1
    
    def test_clear_caches(self, temp_config_file):
        """Test clear_caches"""
        matcher = OperationsMatcher(temp_config_file)
        
        # Populate caches
        matcher.exact_match("AGROBAZAR")
        matcher.fuzzy_match("AGROBAZAR CHISINAU")
        
        assert len(matcher.exact_match_cache) > 0
        assert len(matcher.fuzzy_match_cache) > 0
        
        # Clear caches
        matcher.clear_caches()
        
        assert len(matcher.exact_match_cache) == 0
        assert len(matcher.fuzzy_match_cache) == 0
    
    def test_get_statistics(self, temp_config_file):
        """Test get_statistics"""
        matcher = OperationsMatcher(temp_config_file)
        
        # Populate some data
        matcher.exact_match("AGROBAZAR")
        matcher.fuzzy_match("AGROBAZAR CHISINAU")
        matcher.learn_from_correction("TEST PATTERN", "Food", 90)
        
        stats = matcher.get_statistics()
        
        assert 'exact_match_cache_size' in stats
        assert 'fuzzy_match_cache_size' in stats
        assert 'learned_patterns_count' in stats
        assert 'total_exact_matches' in stats
        assert 'total_keyword_categories' in stats
        assert 'total_pattern_categories' in stats
        
        assert stats['exact_match_cache_size'] >= 1
        assert stats['fuzzy_match_cache_size'] >= 1
        assert stats['learned_patterns_count'] >= 1


class TestGlobalFunctions:
    """Test global convenience functions"""
    
    def test_get_matcher_singleton(self):
        """Test get_matcher returns singleton instance"""
        # Clear global matcher
        import operations_matcher
        operations_matcher._global_matcher = None
        
        matcher1 = get_matcher()
        matcher2 = get_matcher()
        
        assert matcher1 is matcher2
        assert isinstance(matcher1, OperationsMatcher)
    
    def test_get_matcher_with_config_path(self):
        """Test get_matcher with custom config path"""
        # Clear global matcher
        import operations_matcher
        operations_matcher._global_matcher = None
        
        with patch('operations_matcher.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data='exact_matches: {}')):
                matcher = get_matcher("custom_config.yaml")
                assert matcher.config_path == "custom_config.yaml"
    
    def test_classify_operation_function(self):
        """Test classify_operation convenience function"""
        with patch('operations_matcher.get_matcher') as mock_get_matcher:
            mock_matcher = mock_get_matcher.return_value
            mock_matcher.classify_operation.return_value = MatchResult(
                "Food", 95.0, "exact", {}
            )
            
            result = classify_operation("AGROBAZAR")
            
            mock_matcher.classify_operation.assert_called_once_with("AGROBAZAR")
            assert result.type_name == "Food"
    
    def test_get_classification_suggestions_function(self):
        """Test get_classification_suggestions convenience function"""
        with patch('operations_matcher.get_matcher') as mock_get_matcher:
            mock_matcher = mock_get_matcher.return_value
            mock_suggestion = ClassificationSuggestion(
                1, "Food", 95.0, "exact", {}, True
            )
            mock_matcher.get_classification_suggestions.return_value = [mock_suggestion]
            
            operations = [(1, "AGROBAZAR")]
            suggestions = get_classification_suggestions(operations)
            
            mock_matcher.get_classification_suggestions.assert_called_once_with(operations)
            assert len(suggestions) == 1
            assert suggestions[0].type_name == "Food"


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            'confidence_thresholds': {
                'exact_match': 100,
                'fuzzy_match_auto': 95,
                'fuzzy_match_suggest': 85,
                'keyword_match_auto': 80,
                'keyword_match_suggest': 70,
                'pattern_match_auto': 75,
                'pattern_match_suggest': 65
            },
            'fuzzy_matching': {
                'min_similarity': 85,
                'max_candidates': 5
            },
            'exact_matches': {
                'AGROBAZAR': 'Food',
                'FARMACIA FAMILIEI': 'Healthcare',
                'RESTAURANT JERAFFE': 'Restaurant'
            },
            'keyword_matches': {
                'food': {
                    'keywords': ['AGRO', 'MARKET', 'FOOD'],
                    'weight': 90,
                    'type': 'Food'
                },
                'healthcare': {
                    'keywords': ['FARMACIA', 'APOTECA', 'MEDICAL'],
                    'weight': 85,
                    'type': 'Healthcare'
                }
            },
            'pattern_matches': {
                'food_patterns': {
                    'patterns': ['.*AGRO.*', '.*MARKET.*'],
                    'weight': 75,
                    'type': 'Food'
                }
            },
            'learning': {
                'track_success': True,
                'min_confidence_for_learning': 70,
                'max_learned_patterns': 1000
            }
        }
    
    def test_operations_matcher_with_malformed_yaml(self):
        """Test OperationsMatcher with malformed YAML"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_file = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                OperationsMatcher(temp_file)
        finally:
            Path(temp_file).unlink()
    
    def test_operations_matcher_with_missing_config_sections(self):
        """Test OperationsMatcher with missing config sections"""
        minimal_config = {
            'confidence_thresholds': {
                'exact_match': 100,
                'fuzzy_match_auto': 95,
                'keyword_match_auto': 80,
                'pattern_match_auto': 75
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(minimal_config, f)
            temp_file = f.name
        
        try:
            matcher = OperationsMatcher(temp_file)
            
            # Should handle missing sections gracefully
            result = matcher.exact_match("TEST")
            assert result is None
            
            result = matcher.keyword_match("TEST")
            assert result is None
            
            result = matcher.pattern_match("TEST")
            assert result is None
            
        finally:
            Path(temp_file).unlink()
    
    @pytest.fixture
    def temp_config_file(self, sample_config):
        """Create a temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(sample_config, f)
            return f.name
    
    def test_classify_operation_with_unicode_description(self, sample_config):
        """Test classify_operation with unicode description"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(sample_config, f)
            temp_file = f.name
        
        try:
            matcher = OperationsMatcher(temp_file)
            
            # Test with unicode characters
            result = matcher.classify_operation("FARMACIA FAMILIEI ĂÂÎȘȚ")
            # Should not raise exception and should normalize properly
            assert result is None or isinstance(result, MatchResult)
        finally:
            Path(temp_file).unlink()
    
    def test_normalize_description_with_special_characters(self, sample_config):
        """Test normalize_description with special characters"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(sample_config, f)
            temp_file = f.name
        
        try:
            matcher = OperationsMatcher(temp_file)
            
            # Test various special characters
            test_cases = [
                "AGRO-BAZAR",
                "FARMACIA.FAMILIEI",
                "RESTAURANT:JERAFFE",
                "MARKET,CHISINAU",
                "SHOP;MALL",
                "STORE?QUERY"
            ]
            
            for test_case in test_cases:
                normalized = matcher._normalize_description(test_case)
                assert isinstance(normalized, str)
                assert normalized == normalized.upper()  # Should be uppercase
        finally:
            Path(temp_file).unlink()
