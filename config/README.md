# Operations Matching System

This directory contains the configuration and documentation for the hybrid rule-based operations matching system.

## Overview

The Operations Matching System automatically classifies financial operations from PDF exports using a multi-layered approach:

1. **Exact Match** - Direct string comparison (100% confidence)
2. **Fuzzy Match** - String similarity using Levenshtein distance (85-99% confidence)
3. **Keyword Match** - Keyword-based classification (70-90% confidence)
4. **Pattern Match** - Regular expression pattern matching (60-80% confidence)

## Configuration Files

### `operations_matching.yaml`

The main configuration file that defines:

- **Confidence thresholds** for each classification method
- **Exact match rules** for direct string comparisons
- **Keyword matching rules** organized by category
- **Pattern matching rules** using regular expressions
- **Learning configuration** for improving accuracy over time
- **Performance settings** for caching and batch processing

## Configuration Structure

### Confidence Thresholds

```yaml
confidence_thresholds:
  exact_match: 100
  fuzzy_match_auto: 95      # Auto-assign above this threshold
  fuzzy_match_suggest: 85   # Suggest above this threshold
  keyword_match_auto: 80
  keyword_match_suggest: 70
  pattern_match_auto: 75
  pattern_match_suggest: 65
```

### Exact Matches

Direct string comparisons for known merchants:

```yaml
exact_matches:
  "AGROBAZAR": "Food"
  "FARMACIA FAMILIEI": "Healthcare"
  "BE BEAUTY Salon": "Entertainment"
```

### Keyword Matches

Keyword-based classification with weights:

```yaml
keyword_matches:
  food:
    keywords: ["AGRO", "MARKET", "FOODMART", "RESTAURANT"]
    weight: 90
    type: "Food"
```

### Pattern Matches

Regular expression patterns:

```yaml
pattern_matches:
  food_patterns:
    patterns:
      - ".*AGRO.*"
      - ".*MARKET.*"
      - ".*FOOD.*"
    weight: 75
    type: "Food"
```

## Usage

### Basic Classification

```python
from operations_matcher import classify_operation

# Classify a single operation
result = classify_operation("AGROBAZAR")
if result:
    print(f"Type: {result.type_name}")
    print(f"Confidence: {result.confidence}%")
    print(f"Method: {result.method}")
```

### PDF Processing with Classification

```python
from pdf_processor import extract_and_classify_operations
from sql_utils import process_and_store_with_classification

# Process PDF and get classifications
operations, suggestions = extract_and_classify_operations("path/to/file.pdf")

# Process and store with auto-assignment
pdf_id, ops_count, classifications = process_and_store_with_classification(
    pdf_path="path/to/file.pdf",
    db_path="database.db",
    auto_assign_high_confidence=True
)
```

### Auto-Assignment

```python
from sql_utils import auto_assign_high_confidence_operations

# Auto-assign high confidence operations
assigned_count = auto_assign_high_confidence_operations(session, pdf_id)
print(f"Auto-assigned {assigned_count} operations")
```

## Classification Methods

### 1. Exact Match (100% confidence)

- **Purpose**: Direct string comparison for known merchants
- **Use Case**: Frequently encountered merchants with consistent naming
- **Example**: "AGROBAZAR" → Food

### 2. Fuzzy Match (85-99% confidence)

- **Purpose**: Handle variations in merchant names
- **Algorithm**: Levenshtein distance for string similarity
- **Use Case**: Similar merchants with slight name variations
- **Example**: "AGROBAZAR SHOP 02" → Food (similar to "AGROBAZAR")

### 3. Keyword Match (70-90% confidence)

- **Purpose**: Classify based on keywords in description
- **Method**: Count matching keywords and apply weights
- **Use Case**: Merchants with descriptive names
- **Example**: "FARMACIA MIRON" → Healthcare (contains "FARMACIA")

### 4. Pattern Match (60-80% confidence)

- **Purpose**: Use regular expressions for complex patterns
- **Method**: Regex pattern matching
- **Use Case**: Merchants following naming patterns
- **Example**: ".*FARMACIA.*" → Healthcare

## Learning System

The system can learn from user corrections to improve accuracy:

```python
from operations_matcher import get_matcher

matcher = get_matcher()

# Learn from user correction
matcher.learn_from_correction(
    description="NEW GROCERY STORE",
    correct_type="Food",
    user_confidence=95
)
```

## Performance Features

### Caching

- **Exact Match Cache**: Stores exact match results
- **Fuzzy Match Cache**: Stores fuzzy match results
- **Configurable cache sizes** in the configuration

### Batch Processing

- Process multiple operations efficiently
- Configurable batch sizes
- Memory-efficient processing

## Customization

### Adding New Rules

1. **Exact Matches**: Add to `exact_matches` section
2. **Keywords**: Add to `keyword_matches` section
3. **Patterns**: Add to `pattern_matches` section

### Adjusting Thresholds

Modify confidence thresholds in `confidence_thresholds`:

```yaml
confidence_thresholds:
  fuzzy_match_auto: 90  # More strict auto-assignment
  keyword_match_auto: 85  # Higher confidence required
```

### Adding New Categories

1. Add new operation types to the database
2. Add corresponding rules in the configuration
3. Update the frontend to display new categories

## Testing

Run the test suite to verify the system:

```bash
python test_operations_matching.py
```

Run the demonstration to see the system in action:

```bash
python demo_operations_matching.py
```

## Troubleshooting

### Common Issues

1. **No matches found**: Check if the description is normalized correctly
2. **Low confidence**: Review keyword and pattern rules
3. **Configuration errors**: Validate YAML syntax
4. **Performance issues**: Adjust cache sizes and batch processing

### Debugging

Enable debug logging to see detailed classification information:

```python
from operations_matcher import get_matcher

matcher = get_matcher()
result = matcher.classify_operation("TEST DESCRIPTION")
print(f"Debug info: {result.details}")
```

## Best Practices

1. **Start with exact matches** for frequently encountered merchants
2. **Use keywords** for broad categories
3. **Use patterns** for complex naming conventions
4. **Monitor confidence scores** and adjust thresholds
5. **Learn from user corrections** to improve accuracy
6. **Regularly review and update** rules based on new data

## Integration

The system integrates with:

- **PDF Processing**: Automatic classification during PDF import
- **Database Operations**: Auto-assignment of operation types
- **API Endpoints**: Classification suggestions for the frontend
- **User Interface**: Display of confidence scores and suggestions
