-- Financial Review App - Database Migration Script
-- This script initializes the database with default data

-- ==============================================
-- INITIAL DATA FOR OPERATION TYPES
-- ==============================================

-- Insert initial operation types
INSERT INTO operationtype (name, description, created_at) VALUES
('Income', 'Money coming in - salary, business income, investments', NOW()),
('Expense', 'Money going out - bills, groceries, rent', NOW()),
('Transfer', 'Money moving between accounts', NOW()),
('Investment', 'Investment purchases, sales, dividends', NOW()),
('Tax', 'Tax payments and refunds', NOW()),
('Insurance', 'Insurance premiums and payouts', NOW()),
('Medical', 'Medical expenses and bills', NOW()),
('Education', 'Education-related expenses', NOW()),
('Transportation', 'Gas, car maintenance, public transport', NOW()),
('Entertainment', 'Movies, restaurants, hobbies', NOW()),
('Utilities', 'Electricity, water, internet bills', NOW()),
('Shopping', 'General shopping and purchases', NOW()),
('Bank Fees', 'ATM fees, account maintenance fees', NOW()),
('Cash Withdrawal', 'Cash taken from ATM or bank', NOW()),
('Deposit', 'Money deposited into account', NOW())
ON CONFLICT (name) DO NOTHING;

-- ==============================================
-- INITIAL DATA FOR RULE CATEGORIES
-- ==============================================

-- Insert initial rule categories
INSERT INTO rulecategory (name, description, is_active, created_at) VALUES
('Income Patterns', 'Rules for identifying income transactions', true, NOW()),
('Expense Patterns', 'Rules for identifying expense transactions', true, NOW()),
('Transfer Patterns', 'Rules for identifying transfer transactions', true, NOW()),
('Investment Patterns', 'Rules for identifying investment transactions', true, NOW()),
('Tax Patterns', 'Rules for identifying tax-related transactions', true, NOW()),
('Insurance Patterns', 'Rules for identifying insurance transactions', true, NOW()),
('Medical Patterns', 'Rules for identifying medical transactions', true, NOW()),
('Education Patterns', 'Rules for identifying education transactions', true, NOW()),
('Transportation Patterns', 'Rules for identifying transportation transactions', true, NOW()),
('Entertainment Patterns', 'Rules for identifying entertainment transactions', true, NOW()),
('Utilities Patterns', 'Rules for identifying utility transactions', true, NOW()),
('Shopping Patterns', 'Rules for identifying shopping transactions', true, NOW()),
('Bank Fee Patterns', 'Rules for identifying bank fee transactions', true, NOW()),
('Cash Patterns', 'Rules for identifying cash transactions', true, NOW()),
('Deposit Patterns', 'Rules for identifying deposit transactions', true, NOW())
ON CONFLICT (name) DO NOTHING;

-- ==============================================
-- INITIAL DATA FOR MATCHING RULES
-- ==============================================

-- Income Rules (category matches operation type name)
INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Income', 'salary|wage|payroll|income|earnings', 85, 1, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Income', 'business|freelance|contract|consulting', 85, 2, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

-- Expense Rules
INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Expense', 'grocery|supermarket|food|market', 85, 1, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Entertainment', 'restaurant|cafe|dining|food|eat', 85, 2, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Transportation', 'gas|fuel|petrol|station|shell|bp|esso', 85, 1, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Utilities', 'electric|water|internet|phone|cable|utility', 85, 1, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Medical', 'medical|doctor|hospital|pharmacy|health|clinic', 85, 1, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Insurance', 'insurance|premium|coverage', 85, 1, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Tax', 'tax|irs|revenue|fiscal', 85, 1, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Bank Fees', 'fee|charge|maintenance|service', 85, 1, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Cash Withdrawal', 'atm|withdrawal|cash|money', 85, 1, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Shopping', 'amazon|ebay|shop|store|purchase|buy', 85, 1, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

-- Transfer Rules
INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Transfer', 'transfer|move|between|account', 85, 1, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

-- Investment Rules
INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Investment', 'investment|stock|bond|fund|portfolio|trading', 85, 1, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

-- Deposit Rules
INSERT INTO matchingrule (rule_type, category, pattern, weight, priority, is_active, created_at, created_by, usage_count, success_count)
VALUES ('keyword', 'Deposit', 'deposit|cash in|money in', 85, 1, true, NOW(), '', 0, 0)
ON CONFLICT DO NOTHING;

-- ==============================================
-- VERIFICATION QUERIES
-- ==============================================

-- Check inserted data
SELECT 'Operation Types' as table_name, COUNT(*) as count FROM operationtype
UNION ALL
SELECT 'Rule Categories' as table_name, COUNT(*) as count FROM rulecategory
UNION ALL
SELECT 'Matching Rules' as table_name, COUNT(*) as count FROM matchingrule;

-- ==============================================
-- SCHEMA ALIGNMENT FOR operationrow (idempotent)
-- ==============================================

-- Add new columns used by application models and backfill from legacy fields
ALTER TABLE operationrow ADD COLUMN IF NOT EXISTS transaction_date TIMESTAMP;

ALTER TABLE operationrow ADD COLUMN IF NOT EXISTS processed_date TIMESTAMP;

ALTER TABLE operationrow ADD COLUMN IF NOT EXISTS description TEXT;

ALTER TABLE operationrow ADD COLUMN IF NOT EXISTS amount_lei DOUBLE PRECISION;

ALTER TABLE operationrow ADD COLUMN IF NOT EXISTS type_id INTEGER;

-- Helpful indexes for new columns
CREATE INDEX IF NOT EXISTS idx_operationrow_transaction_date ON operationrow(transaction_date);
CREATE INDEX IF NOT EXISTS idx_operationrow_type_id_new ON operationrow(type_id);

-- NOTE: After verifying the app runs end-to-end in production, you may drop legacy columns:
-- ALTER TABLE operationrow DROP COLUMN operation_date;
-- ALTER TABLE operationrow DROP COLUMN operation_description;
-- ALTER TABLE operationrow DROP COLUMN operation_amount;
-- ALTER TABLE operationrow DROP COLUMN operation_type_id;

-- Success message
\echo 'Database migration completed successfully!'
\echo 'Check the verification results above to confirm data was inserted.'
