-- Financial Review App - Database Schema Creation
-- This script creates all necessary tables for the application

-- ==============================================
-- CREATE TABLES
-- ==============================================

-- User table
CREATE TABLE IF NOT EXISTS user (
    id SERIAL PRIMARY KEY,
    google_id VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    picture VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- PDF table
CREATE TABLE IF NOT EXISTS pdf (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR UNIQUE NOT NULL,
    client_name VARCHAR,
    account_number VARCHAR,
    total_iesiri FLOAT,
    sold_initial FLOAT,
    sold_final FLOAT,
    created_at VARCHAR,
    user_id INTEGER REFERENCES user(id)
);

-- OperationType table
CREATE TABLE IF NOT EXISTS operationtype (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    created_at VARCHAR DEFAULT (NOW()::text)
);

-- OperationRow table
CREATE TABLE IF NOT EXISTS operationrow (
    id SERIAL PRIMARY KEY,
    pdf_id INTEGER REFERENCES pdf(id),
    operation_date DATE,
    operation_description TEXT,
    operation_amount FLOAT,
    operation_type_id INTEGER REFERENCES operationtype(id),
    operation_hash VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RuleCategory table
CREATE TABLE IF NOT EXISTS rulecategory (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at VARCHAR DEFAULT (NOW()::text),
    updated_at VARCHAR DEFAULT (NOW()::text)
);

-- MatchingRule table
CREATE TABLE IF NOT EXISTS matchingrule (
    id SERIAL PRIMARY KEY,
    rule_type VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    pattern TEXT NOT NULL,
    weight INTEGER DEFAULT 85,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    comments TEXT,
    created_by VARCHAR,
    created_at VARCHAR DEFAULT (NOW()::text),
    updated_at VARCHAR DEFAULT (NOW()::text),
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    last_used VARCHAR
);

-- RuleMatchLog table
CREATE TABLE IF NOT EXISTS rulematchlog (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES matchingrule(id),
    operation_description TEXT NOT NULL,
    matched_type VARCHAR NOT NULL,
    confidence FLOAT NOT NULL,
    method VARCHAR NOT NULL,
    timestamp VARCHAR DEFAULT (NOW()::text),
    success BOOLEAN DEFAULT TRUE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_google_id ON user(google_id);
CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);
CREATE INDEX IF NOT EXISTS idx_pdf_file_path ON pdf(file_path);
CREATE INDEX IF NOT EXISTS idx_operationtype_name ON operationtype(name);
CREATE INDEX IF NOT EXISTS idx_operationrow_pdf_id ON operationrow(pdf_id);
CREATE INDEX IF NOT EXISTS idx_operationrow_type_id ON operationrow(operation_type_id);
CREATE INDEX IF NOT EXISTS idx_operationrow_hash ON operationrow(operation_hash);
CREATE INDEX IF NOT EXISTS idx_rulecategory_name ON rulecategory(name);
CREATE INDEX IF NOT EXISTS idx_matchingrule_rule_type ON matchingrule(rule_type);
CREATE INDEX IF NOT EXISTS idx_matchingrule_category ON matchingrule(category);
CREATE INDEX IF NOT EXISTS idx_matchingrule_is_active ON matchingrule(is_active);
CREATE INDEX IF NOT EXISTS idx_matchingrule_priority ON matchingrule(priority);
CREATE INDEX IF NOT EXISTS idx_rulematchlog_rule_id ON rulematchlog(rule_id);
CREATE INDEX IF NOT EXISTS idx_rulematchlog_timestamp ON rulematchlog(timestamp);
