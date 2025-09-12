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
INSERT INTO rulecategory (name, description, created_at) VALUES
('Income Patterns', 'Rules for identifying income transactions', NOW()),
('Expense Patterns', 'Rules for identifying expense transactions', NOW()),
('Transfer Patterns', 'Rules for identifying transfer transactions', NOW()),
('Investment Patterns', 'Rules for identifying investment transactions', NOW()),
('Tax Patterns', 'Rules for identifying tax-related transactions', NOW()),
('Insurance Patterns', 'Rules for identifying insurance transactions', NOW()),
('Medical Patterns', 'Rules for identifying medical transactions', NOW()),
('Education Patterns', 'Rules for identifying education transactions', NOW()),
('Transportation Patterns', 'Rules for identifying transportation transactions', NOW()),
('Entertainment Patterns', 'Rules for identifying entertainment transactions', NOW()),
('Utilities Patterns', 'Rules for identifying utility transactions', NOW()),
('Shopping Patterns', 'Rules for identifying shopping transactions', NOW()),
('Bank Fee Patterns', 'Rules for identifying bank fee transactions', NOW()),
('Cash Patterns', 'Rules for identifying cash transactions', NOW()),
('Deposit Patterns', 'Rules for identifying deposit transactions', NOW())
ON CONFLICT (name) DO NOTHING;

-- ==============================================
-- INITIAL DATA FOR MATCHING RULES
-- ==============================================

-- Income Rules
INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'Salary Income',
    'salary|wage|payroll|income|earnings',
    ot.id,
    1,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Income Patterns' AND ot.name = 'Income';

INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'Business Income',
    'business|freelance|contract|consulting',
    ot.id,
    2,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Income Patterns' AND ot.name = 'Income';

-- Expense Rules
INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'Grocery Shopping',
    'grocery|supermarket|food|market',
    ot.id,
    1,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Expense Patterns' AND ot.name = 'Expense';

INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'Restaurant Expenses',
    'restaurant|cafe|dining|food|eat',
    ot.id,
    2,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Expense Patterns' AND ot.name = 'Entertainment';

INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'Gas Station',
    'gas|fuel|petrol|station|shell|bp|esso',
    ot.id,
    1,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Transportation Patterns' AND ot.name = 'Transportation';

INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'Utilities Bills',
    'electric|water|internet|phone|cable|utility',
    ot.id,
    1,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Utilities Patterns' AND ot.name = 'Utilities';

INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'Medical Expenses',
    'medical|doctor|hospital|pharmacy|health|clinic',
    ot.id,
    1,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Medical Patterns' AND ot.name = 'Medical';

INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'Insurance Payments',
    'insurance|premium|coverage',
    ot.id,
    1,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Insurance Patterns' AND ot.name = 'Insurance';

INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'Tax Payments',
    'tax|irs|revenue|fiscal',
    ot.id,
    1,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Tax Patterns' AND ot.name = 'Tax';

INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'Bank Fees',
    'fee|charge|maintenance|service',
    ot.id,
    1,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Bank Fee Patterns' AND ot.name = 'Bank Fees';

INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'ATM Withdrawals',
    'atm|withdrawal|cash|money',
    ot.id,
    1,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Cash Patterns' AND ot.name = 'Cash Withdrawal';

INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'Online Shopping',
    'amazon|ebay|shop|store|purchase|buy',
    ot.id,
    1,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Shopping Patterns' AND ot.name = 'Shopping';

-- Transfer Rules
INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'Account Transfers',
    'transfer|move|between|account',
    ot.id,
    1,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Transfer Patterns' AND ot.name = 'Transfer';

-- Investment Rules
INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'Investment Transactions',
    'investment|stock|bond|fund|portfolio|trading',
    ot.id,
    1,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Investment Patterns' AND ot.name = 'Investment';

-- Deposit Rules
INSERT INTO matchingrule (category_id, rule_name, pattern, operation_type_id, priority, is_active, created_at)
SELECT 
    rc.id,
    'Cash Deposits',
    'deposit|cash in|money in',
    ot.id,
    1,
    true,
    NOW()
FROM rulecategory rc, operationtype ot 
WHERE rc.name = 'Deposit Patterns' AND ot.name = 'Deposit';

-- ==============================================
-- VERIFICATION QUERIES
-- ==============================================

-- Check inserted data
SELECT 'Operation Types' as table_name, COUNT(*) as count FROM operationtype
UNION ALL
SELECT 'Rule Categories' as table_name, COUNT(*) as count FROM rulecategory
UNION ALL
SELECT 'Matching Rules' as table_name, COUNT(*) as count FROM matchingrule;

-- Success message
\echo 'Database migration completed successfully!'
\echo 'Check the verification results above to confirm data was inserted.'
