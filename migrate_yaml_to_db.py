#!/usr/bin/env python3
"""
Migration script to convert operations_matching.yaml to database tables.
This script should be run once to migrate existing YAML configuration to the new database schema.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any
from sqlmodel import Session, select
from sql_utils import get_engine, init_db
from rules_models import MatchingRule, RuleCategory


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """Load the YAML configuration file"""
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def create_categories_from_yaml(session: Session, config: Dict[str, Any]) -> Dict[str, int]:
    """Create rule categories from YAML configuration"""
    categories = {}
    
    # Extract unique categories from exact matches
    exact_matches = config.get('exact_matches', {})
    for _, category in exact_matches.items():
        if category not in categories:
            cat = RuleCategory(
                name=category,
                description=f"Category for {category} operations",
                color=f"#{hash(category) % 0xFFFFFF:06x}"  # Generate a color based on name
            )
            session.add(cat)
            session.commit()
            session.refresh(cat)
            categories[category] = cat.id
    
    # Extract categories from keyword matches
    keyword_matches = config.get('keyword_matches', {})
    for key, data in keyword_matches.items():
        category = data.get('type')
        if category and category not in categories:
            cat = RuleCategory(
                name=category,
                description=f"Category for {category} operations",
                color=f"#{hash(category) % 0xFFFFFF:06x}"
            )
            session.add(cat)
            session.commit()
            session.refresh(cat)
            categories[category] = cat.id
    
    return categories


def migrate_exact_matches(session: Session, config: Dict[str, Any], categories: Dict[str, int]):
    """Migrate exact matches from YAML to database"""
    exact_matches = config.get('exact_matches', {})
    
    for pattern, category in exact_matches.items():
        if category in categories:
            rule = MatchingRule(
                rule_type='exact',
                category=category,
                pattern=pattern,
                weight=100,  # Exact matches have highest confidence
                priority=100,  # Highest priority
                created_by='migration',
                created_at='2024-01-01T00:00:00'  # Migration timestamp
            )
            session.add(rule)
    
    session.commit()


def migrate_keyword_matches(session: Session, config: Dict[str, Any], categories: Dict[str, int]):
    """Migrate keyword matches from YAML to database"""
    keyword_matches = config.get('keyword_matches', {})
    
    for key, data in keyword_matches.items():
        category = data.get('type')
        keywords = data.get('keywords', [])
        weight = data.get('weight', 85)
        
        if category in categories:
            for keyword in keywords:
                rule = MatchingRule(
                    rule_type='keyword',
                    category=category,
                    pattern=keyword,
                    weight=weight,
                    priority=50,  # Medium priority
                    created_by='migration',
                    created_at='2024-01-01T00:00:00'
                )
                session.add(rule)
    
    session.commit()


def migrate_pattern_matches(session: Session, config: Dict[str, Any], categories: Dict[str, int]):
    """Migrate pattern matches from YAML to database"""
    pattern_matches = config.get('pattern_matches', {})
    
    for key, data in pattern_matches.items():
        category = data.get('type')
        patterns = data.get('patterns', [])
        weight = data.get('weight', 75)
        
        if category in categories:
            for pattern in patterns:
                rule = MatchingRule(
                    rule_type='pattern',
                    category=category,
                    pattern=pattern,
                    weight=weight,
                    priority=25,  # Lower priority
                    created_by='migration',
                    created_at='2024-01-01T00:00:00'
                )
                session.add(rule)
    
    session.commit()


def verify_migration(session: Session, config: Dict[str, Any]) -> Dict[str, Any]:
    """Verify that migration was successful"""
    # Count rules by type
    exact_rules = session.exec(select(MatchingRule).where(MatchingRule.rule_type == 'exact')).all()
    keyword_rules = session.exec(select(MatchingRule).where(MatchingRule.rule_type == 'keyword')).all()
    pattern_rules = session.exec(select(MatchingRule).where(MatchingRule.rule_type == 'pattern')).all()
    categories = session.exec(select(RuleCategory)).all()
    
    # Count expected rules from YAML
    expected_exact = len(config.get('exact_matches', {}))
    expected_keywords = sum(len(data.get('keywords', [])) for data in config.get('keyword_matches', {}).values())
    expected_patterns = sum(len(data.get('patterns', [])) for data in config.get('pattern_matches', {}).values())
    expected_categories = len(set(
        list(config.get('exact_matches', {}).values()) +
        [data.get('type') for data in config.get('keyword_matches', {}).values()] +
        [data.get('type') for data in config.get('pattern_matches', {}).values()]
    ))
    
    return {
        'migrated': {
            'exact_rules': len(exact_rules),
            'keyword_rules': len(keyword_rules),
            'pattern_rules': len(pattern_rules),
            'categories': len(categories)
        },
        'expected': {
            'exact_rules': expected_exact,
            'keyword_rules': expected_keywords,
            'pattern_rules': expected_patterns,
            'categories': expected_categories
        },
        'success': (
            len(exact_rules) == expected_exact and
            len(keyword_rules) == expected_keywords and
            len(pattern_rules) == expected_patterns and
            len(categories) == expected_categories
        )
    }


def main():
    """Main migration function"""
    config_path = "config/operations_matching.yaml"
    db_path = "api/db.sqlite"
    
    if not Path(config_path).exists():
        print(f"Error: Configuration file {config_path} not found!")
        return
    
    print("Starting migration from YAML to database...")
    
    # Load configuration
    config = load_yaml_config(config_path)
    print(f"Loaded configuration with {len(config)} sections")
    
    # Initialize database
    engine = get_engine(db_path)
    init_db(engine)
    
    with Session(engine) as session:
        # Create categories
        print("Creating rule categories...")
        categories = create_categories_from_yaml(session, config)
        print(f"Created {len(categories)} categories")
        
        # Migrate rules
        print("Migrating exact matches...")
        migrate_exact_matches(session, config, categories)
        
        print("Migrating keyword matches...")
        migrate_keyword_matches(session, config, categories)
        
        print("Migrating pattern matches...")
        migrate_pattern_matches(session, config, categories)
        
        # Verify migration
        print("Verifying migration...")
        verification = verify_migration(session, config)
        
        if verification['success']:
            print("✅ Migration completed successfully!")
        else:
            print("❌ Migration verification failed!")
            print("Expected:", verification['expected'])
            print("Migrated:", verification['migrated'])
        
        print("\nMigration summary:")
        print(f"Categories: {verification['migrated']['categories']}")
        print(f"Exact rules: {verification['migrated']['exact_rules']}")
        print(f"Keyword rules: {verification['migrated']['keyword_rules']}")
        print(f"Pattern rules: {verification['migrated']['pattern_rules']}")


if __name__ == "__main__":
    main()
