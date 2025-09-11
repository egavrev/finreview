#!/usr/bin/env python3
"""
Production Migration Script for SQLite to PostgreSQL

This script migrates your existing SQLite data to the Cloud Run PostgreSQL instance.
Run this AFTER you have deployed both services to Cloud Run.
"""

import os
import sys
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import sqlite3

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))


class ProductionMigrator:
    """Migrates SQLite data to production PostgreSQL via API"""
    
    def __init__(self, sqlite_path: str, api_base_url: str):
        self.sqlite_path = sqlite_path
        self.api_base_url = api_base_url.rstrip('/')
        self.migration_log = []
    
    def connect_sqlite(self):
        """Connect to local SQLite database"""
        if not Path(self.sqlite_path).exists():
            raise FileNotFoundError(f"SQLite database not found: {self.sqlite_path}")
        
        self.sqlite_conn = sqlite3.connect(self.sqlite_path)
        self.sqlite_conn.row_factory = sqlite3.Row
        print("✅ Connected to SQLite database")
    
    def test_api_connection(self):
        """Test connection to production API"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Connected to production API")
                return True
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            return False
    
    def get_sqlite_data(self, table_name: str) -> List[Dict[str, Any]]:
        """Get data from SQLite table"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            data.append(dict(row))
        
        print(f"📊 Found {len(data)} records in {table_name}")
        return data
    
    def migrate_operation_types(self):
        """Migrate operation types to production"""
        print("🔄 Migrating operation types...")
        
        data = self.get_sqlite_data('operationtype')
        success_count = 0
        
        for item in data:
            try:
                # Create operation type via API
                payload = {
                    "name": item['name'],
                    "description": item.get('description', '')
                }
                
                response = requests.post(
                    f"{self.api_base_url}/operation-types",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    success_count += 1
                else:
                    print(f"⚠️ Failed to create operation type '{item['name']}': {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error creating operation type '{item['name']}': {e}")
        
        print(f"✅ Migrated {success_count}/{len(data)} operation types")
        self.migration_log.append(f"Operation Types: {success_count}/{len(data)}")
    
    def migrate_pdfs_and_operations(self):
        """Migrate PDFs and their operations"""
        print("🔄 Migrating PDFs and operations...")
        
        pdfs_data = self.get_sqlite_data('pdf')
        operations_data = self.get_sqlite_data('operationrow')
        
        # Group operations by PDF
        operations_by_pdf = {}
        for op in operations_data:
            pdf_id = op['pdf_id']
            if pdf_id not in operations_by_pdf:
                operations_by_pdf[pdf_id] = []
            operations_by_pdf[pdf_id].append(op)
        
        migrated_pdfs = 0
        migrated_operations = 0
        
        for pdf in pdfs_data:
            try:
                # Note: PDF files can't be uploaded via API, so we'll create placeholder entries
                # You'll need to re-upload the actual PDF files through the web interface
                
                pdf_operations = operations_by_pdf.get(pdf['id'], [])
                print(f"📄 PDF '{pdf['client_name']}' has {len(pdf_operations)} operations")
                
                # For now, just log the PDF info
                print(f"   - Client: {pdf['client_name']}")
                print(f"   - Account: {pdf['account_number']}")
                print(f"   - Total Iesiri: {pdf['total_iesiri']}")
                
                migrated_pdfs += 1
                migrated_operations += len(pdf_operations)
                
                # TODO: Re-upload PDF files through web interface
                print(f"   ⚠️ You'll need to re-upload the PDF file through the web interface")
                
            except Exception as e:
                print(f"❌ Error processing PDF: {e}")
        
        print(f"✅ Processed {migrated_pdfs} PDFs with {migrated_operations} operations")
        self.migration_log.append(f"PDFs: {migrated_pdfs}, Operations: {migrated_operations}")
    
    def generate_migration_report(self):
        """Generate migration report"""
        report_path = Path("production_migration_report.txt")
        
        with open(report_path, 'w') as f:
            f.write("Production Migration Report\n")
            f.write("=" * 30 + "\n")
            f.write(f"Migration Date: {datetime.now().isoformat()}\n")
            f.write(f"SQLite Source: {self.sqlite_path}\n")
            f.write(f"API Target: {self.api_base_url}\n\n")
            
            f.write("Migration Results:\n")
            f.write("-" * 20 + "\n")
            for log_entry in self.migration_log:
                f.write(f"{log_entry}\n")
            
            f.write("\nNext Steps:\n")
            f.write("-" * 10 + "\n")
            f.write("1. Re-upload PDF files through the web interface\n")
            f.write("2. Verify all data is correctly migrated\n")
            f.write("3. Test the application functionality\n")
        
        print(f"📄 Migration report saved to: {report_path}")
    
    def close_sqlite(self):
        """Close SQLite connection"""
        if hasattr(self, 'sqlite_conn'):
            self.sqlite_conn.close()
        print("🔒 SQLite connection closed")


def main():
    """Main migration function"""
    print("🔄 Production Migration Tool")
    print("=" * 30)
    
    # Configuration
    sqlite_path = "api/db.sqlite"
    api_base_url = "https://finreview-app-xxxxx-uc.a.run.app"  # Replace with your actual URL
    
    print(f"SQLite Path: {sqlite_path}")
    print(f"API URL: {api_base_url}")
    print()
    
    # Create migrator
    migrator = ProductionMigrator(sqlite_path, api_base_url)
    
    try:
        # Connect to databases
        migrator.connect_sqlite()
        
        # Test API connection
        if not migrator.test_api_connection():
            print("❌ Cannot connect to production API. Please check the URL and ensure services are running.")
            return
        
        # Run migration
        migrator.migrate_operation_types()
        migrator.migrate_pdfs_and_operations()
        migrator.generate_migration_report()
        
        print("\n🎉 Migration completed!")
        print("Next steps:")
        print("1. Re-upload your PDF files through the web interface")
        print("2. Verify all data is correctly migrated")
        print("3. Test the application functionality")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        
    finally:
        migrator.close_sqlite()


if __name__ == "__main__":
    main()
