#!/bin/bash

# Simple Migration Script for Financial Review App
# This script runs the SQL migration to initialize the database

echo "🔄 Starting database migration..."

# Check if we have the migration script
if [ ! -f "migrate.sql" ]; then
    echo "❌ migrate.sql not found!"
    exit 1
fi

echo "📁 Migration files found"

# Function to run migration locally
run_local_migration() {
    echo "🏠 Running local migration..."
    
    # Check if psql is available
    if ! command -v psql &> /dev/null; then
        echo "❌ psql not found. Please install PostgreSQL client tools."
        exit 1
    fi
    
    # Check if local PostgreSQL is running
    if ! pg_isready -q; then
        echo "❌ PostgreSQL is not running. Please start PostgreSQL first."
        exit 1
    fi
    
    # Run the migration
    psql -d finreview -f migrate.sql
    
    if [ $? -eq 0 ]; then
        echo "✅ Local migration completed successfully!"
    else
        echo "❌ Local migration failed!"
        exit 1
    fi
}

# Function to run migration on production
run_production_migration() {
    echo "☁️ Running production migration..."
    
    # Get the PostgreSQL service URL
    read -p "Enter your PostgreSQL service URL (e.g., postgres-service-xxxxx-uc.a.run.app): " POSTGRES_URL
    
    if [ -z "$POSTGRES_URL" ]; then
        echo "❌ PostgreSQL URL is required!"
        exit 1
    fi
    
    # Run the migration
    psql "postgresql://finreview_user:FlhugG77XDC1_0SlYUfhuzd-TkEySuwTtYFcV3luIh0@${POSTGRES_URL}:5432/finreview" -f migrate.sql
    
    if [ $? -eq 0 ]; then
        echo "✅ Production migration completed successfully!"
    else
        echo "❌ Production migration failed!"
        exit 1
    fi
}

# Main menu
echo "Select migration target:"
echo "1) Local PostgreSQL"
echo "2) Production Cloud Run PostgreSQL"
echo "3) Exit"

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        run_local_migration
        ;;
    2)
        run_production_migration
        ;;
    3)
        echo "👋 Migration cancelled."
        exit 0
        ;;
    *)
        echo "❌ Invalid choice!"
        exit 1
        ;;
esac

echo "🎉 Migration process completed!"
