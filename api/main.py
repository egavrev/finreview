from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session, select
from sqlalchemy import delete
from typing import List, Optional
import uvicorn
from pathlib import Path
import tempfile
import shutil
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sql_utils import (
    get_engine, init_db, PDF, OperationRow, OperationType, process_and_store, 
    get_pdf_by_path, get_operations_for_pdf, create_operation_type, create_manual_operation, get_operation_types,
    get_operation_type_by_id, update_operation_type, delete_operation_type,
    assign_operation_type, get_operations_by_type, get_operations_with_types,
    get_operations_with_null_types, get_operations_by_month, delete_operation, get_available_months, get_monthly_report_data, get_operations_by_type_for_month,
    get_duplicate_operations, User
)
from pdf_processor import PDFSummary, Operation
from api.rules_api import router as rules_router
from rules_models import MatchingRule, RuleCategory, RuleMatchLog
from auth import authenticate_google_user, get_current_user, get_google_oauth_url, AuthError, security

app = FastAPI(title="Financial Review API", version="1.0.0")

# CORS middleware for frontend communication
# Get CORS origins from environment or use defaults
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://192.168.0.6:3000,http://192.168.0.6:8000").split(",")
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup - PostgreSQL for production, SQLite for development
def setup_database_with_retry():
    """Setup database with retry logic for production deployments"""
    max_retries = 5  # Increased for Cloud Run
    retry_delay = 5  # Increased for Cloud Run
    
    # Debug environment variables
    print(f"🔍 ENVIRONMENT variable: '{os.getenv('ENVIRONMENT')}'")
    print(f"🔍 DATABASE_URL variable: '{os.getenv('DATABASE_URL')}'")
    
    for attempt in range(max_retries):
        try:
            if os.getenv("ENVIRONMENT") == "production":
                # Production: Use PostgreSQL
                DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://finreview_user:FlhugG77XDC1_0SlYUfhuzd-TkEySuwTtYFcV3luIh0@postgres-service:5432/finreview")
                print(f"🔄 Attempting to connect to PostgreSQL (attempt {attempt + 1}/{max_retries}): {DATABASE_URL}")
                engine = get_engine(DATABASE_URL)
            else:
                # Development: Use SQLite
                DB_PATH = Path(__file__).parent / "db.sqlite"
                print(f"🔄 Using SQLite database: {DB_PATH}")
                engine = get_engine(DB_PATH)
            
            init_db(engine)
            print(f"✅ Database connected successfully on attempt {attempt + 1}")
            return engine
            
        except Exception as e:
            print(f"❌ Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 1.2  # Gentler backoff
            else:
                print("💥 All database connection attempts failed")
                # For Cloud Run, we need to start the app even if DB fails
                print("🚀 Starting FastAPI without database connection...")
                return None

# Try to setup database, but don't fail if it doesn't work
try:
    engine = setup_database_with_retry()
    print("✅ Database engine created successfully")
except Exception as e:
    print(f"⚠️ Database setup failed, starting without DB: {e}")
    engine = None

# Include routers
app.include_router(rules_router)

def get_session():
    if engine is None:
        raise HTTPException(status_code=503, detail="Database not available")
    with Session(engine) as session:
        yield session

@app.get("/")
async def root():
    return {"message": "Financial Review API"}

@app.get("/health")
async def health_check():
    """Health check endpoint to keep container warm"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "finreview-api",
        "database": "connected" if engine is not None else "disconnected"
    }

@app.get("/health/database")
async def health_check_database(session: Session = Depends(get_session)):
    """Health check that also tests database connection"""
    try:
        # Simple database query to keep PostgreSQL warm too
        session.exec(select(OperationRow).limit(1))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }


# Authentication endpoints
@app.get("/auth/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    auth_url = get_google_oauth_url()
    return {"auth_url": auth_url}


@app.get("/auth/google/callback")
async def google_callback(code: str = Query(...)):
    """Handle Google OAuth callback"""
    try:
        result = await authenticate_google_user(code, str(DB_PATH))
        
        # Redirect to frontend with token in URL parameter
        token = result["access_token"]
        redirect_url = f"{frontend_url}/auth/callback?token={token}"
        
        return RedirectResponse(url=redirect_url)
        
    except AuthError as e:
        # Redirect to frontend with error
        error_url = f"{frontend_url}/auth/error?message={str(e)}"
        return RedirectResponse(url=error_url)
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Redirect to frontend with error
        error_url = f"{frontend_url}/auth/error?message=Authentication failed"
        return RedirectResponse(url=error_url)


def get_current_user_with_db_path(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current user with correct database path"""
    return get_current_user(credentials, db_path=str(DB_PATH))

@app.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user_with_db_path)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "created_at": current_user.created_at.isoformat(),
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }


@app.post("/auth/logout")
async def logout():
    """Logout endpoint (client should remove token)"""
    return {"message": "Logged out successfully"}

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Upload and process a PDF file with deduplication"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = Path(tmp_file.name)
    
    try:
        # Process the PDF with deduplication enabled
        pdf_id, stored_count, skipped_count = process_and_store(tmp_path, DB_PATH, skip_duplicates=True)
        
        # Get the processed data
        pdf_record = get_pdf_by_path(session, tmp_path)
        operations = get_operations_for_pdf(session, pdf_id)
        
        return {
            "success": True,
            "pdf_id": pdf_id,
            "operations_stored": stored_count,
            "operations_skipped": skipped_count,
            "total_operations_processed": stored_count + skipped_count,
            "deduplication_info": {
                "duplicates_found": skipped_count > 0,
                "duplicate_percentage": (skipped_count / (stored_count + skipped_count) * 100) if (stored_count + skipped_count) > 0 else 0
            },
            "pdf_summary": {
                "client_name": pdf_record.client_name,
                "account_number": pdf_record.account_number,
                "total_iesiri": pdf_record.total_iesiri,
                "sold_initial": pdf_record.sold_initial,
                "sold_final": pdf_record.sold_final,
            } if pdf_record else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        # Clean up temporary file
        os.unlink(tmp_path)

@app.get("/pdfs")
async def list_pdfs(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """List all processed PDFs with operation counts"""
    pdfs = session.exec(select(PDF).order_by(PDF.id.desc())).all()
    
    result = []
    for pdf in pdfs:
        # Get operation count for this PDF
        operations_count = session.exec(select(OperationRow).where(OperationRow.pdf_id == pdf.id)).all()
        
        result.append({
            "id": pdf.id,
            "file_path": pdf.file_path,
            "client_name": pdf.client_name,
            "account_number": pdf.account_number,
            "total_iesiri": pdf.total_iesiri,
            "sold_initial": pdf.sold_initial,
            "sold_final": pdf.sold_final,
            "created_at": pdf.created_at,
            "operations_count": len(operations_count),
        })
    
    return result

@app.get("/pdfs/{pdf_id}")
async def get_pdf_details(
    pdf_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get details of a specific PDF"""
    pdf = session.exec(select(PDF).where(PDF.id == pdf_id)).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    operations = get_operations_for_pdf(session, pdf_id)
    
    return {
        "pdf": {
            "id": pdf.id,
            "file_path": pdf.file_path,
            "client_name": pdf.client_name,
            "account_number": pdf.account_number,
            "total_iesiri": pdf.total_iesiri,
            "sold_initial": pdf.sold_initial,
            "sold_final": pdf.sold_final,
            "created_at": pdf.created_at,
        },
        "operations": [
            {
                "id": op.id,
                "type_id": op.type_id,
                "transaction_date": op.transaction_date,
                "processed_date": op.processed_date,
                "description": op.description,
                "amount_lei": op.amount_lei,
            }
            for op in operations
        ]
    }


@app.delete("/pdfs/{pdf_id}")
async def delete_pdf(
    pdf_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Delete a PDF and all its associated operations"""
    pdf = session.exec(select(PDF).where(PDF.id == pdf_id)).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    try:
        # Get operations count before deletion
        operations_count = session.exec(select(OperationRow).where(OperationRow.pdf_id == pdf_id)).all()
        operations_deleted_count = len(operations_count)
        
        # Delete all operations associated with this PDF
        for operation in operations_count:
            session.delete(operation)
        
        # Delete the PDF record
        session.delete(pdf)
        session.commit()
        
        return {
            "success": True,
            "message": f"PDF '{pdf.file_path}' and all associated operations deleted successfully",
            "pdf_id": pdf_id,
            "operations_deleted": operations_deleted_count
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting PDF: {str(e)}")

@app.get("/operations")
async def list_operations(
    pdf_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """List operations with optional filtering"""
    query = select(OperationRow)
    if pdf_id:
        query = query.where(OperationRow.pdf_id == pdf_id)
    
    query = query.order_by(OperationRow.id.desc()).offset(offset).limit(limit)
    operations = session.exec(query).all()
    
    return [
        {
            "id": op.id,
            "pdf_id": op.pdf_id,
            "type_id": op.type_id,
            "transaction_date": op.transaction_date,
            "processed_date": op.processed_date,
            "description": op.description,
            "amount_lei": op.amount_lei,
        }
        for op in operations
    ]

@app.post("/operations/manual")
async def create_manual_operation_endpoint(
    transaction_date: str = Form(...),
    type_id: str = Form(...),  # Accept as string first
    amount_lei: str = Form(...),  # Accept as string first
    description: Optional[str] = Form(None),
    processed_date: Optional[str] = Form(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Create a manual operation"""
    try:
        # Convert string parameters to proper types
        try:
            type_id_int = int(type_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid type_id: must be a number")
        
        try:
            amount_float = float(amount_lei)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid amount: must be a number")
        
        # Validate amount (maximum 999999.99)
        if amount_float > 999999.99:
            raise HTTPException(status_code=400, detail="Amount cannot exceed 999999.99 MDL")
        
        if amount_float <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        # Validate type_id exists
        operation_type = get_operation_type_by_id(session, type_id_int)
        if not operation_type:
            raise HTTPException(status_code=404, detail="Operation type not found")
        
        # Create the manual operation
        operation = create_manual_operation(
            session=session,
            transaction_date=transaction_date,
            type_id=type_id_int,
            amount_lei=amount_float,
            description=description,
            processed_date=processed_date
        )
        
        return {
            "id": operation.id,
            "pdf_id": operation.pdf_id,
            "type_id": operation.type_id,
            "transaction_date": operation.transaction_date,
            "processed_date": operation.processed_date,
            "description": operation.description,
            "amount_lei": operation.amount_lei,
            "operation_hash": operation.operation_hash,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating manual operation: {str(e)}")


@app.get("/operations/by-month/{year}/{month}")
async def get_operations_by_month_endpoint(
    year: int,
    month: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get all operations for a specific month"""
    try:
        operations_with_types = get_operations_by_month(session, year, month)
        
        result = []
        for operation, operation_type in operations_with_types:
            result.append({
                "id": operation.id,
                "pdf_id": operation.pdf_id,
                "type_id": operation.type_id,
                "type_name": operation_type.name if operation_type else None,
                "transaction_date": operation.transaction_date,
                "processed_date": operation.processed_date,
                "description": operation.description,
                "amount_lei": operation.amount_lei,
                "is_manual": operation.pdf_id is None,
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching operations: {str(e)}")


@app.delete("/operations/{operation_id}")
async def delete_operation_endpoint(
    operation_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Delete an operation by ID"""
    try:
        success = delete_operation(session, operation_id)
        if success:
            return {"success": True, "message": "Operation deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Operation not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting operation: {str(e)}")


@app.get("/statistics")
async def get_statistics(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get overall statistics"""
    pdfs = session.exec(select(PDF)).all()
    operations = session.exec(select(OperationRow)).all()
    
    total_iesiri = sum(pdf.total_iesiri or 0 for pdf in pdfs)
    total_operations = len(operations)
    total_amount = sum(op.amount_lei or 0 for op in operations)
    
    return {
        "total_pdfs": len(pdfs),
        "total_operations": total_operations,
        "total_iesiri": total_iesiri,
        "total_amount": total_amount,
        "average_amount_per_operation": total_amount / total_operations if total_operations > 0 else 0,
    }

# Operation Type endpoints
@app.post("/operation-types")
async def create_type(
    name: str,
    description: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Create a new operation type"""
    try:
        operation_type = create_operation_type(session, name, description)
        return {
            "id": operation_type.id,
            "name": operation_type.name,
            "description": operation_type.description,
            "created_at": operation_type.created_at,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating operation type: {str(e)}")

@app.get("/operation-types")
async def list_operation_types(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """List all operation types"""
    types = get_operation_types(session)
    return [
        {
            "id": op_type.id,
            "name": op_type.name,
            "description": op_type.description,
            "created_at": op_type.created_at,
        }
        for op_type in types
    ]

@app.get("/operation-types/{type_id}")
async def get_operation_type(
    type_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get a specific operation type"""
    op_type = get_operation_type_by_id(session, type_id)
    if not op_type:
        raise HTTPException(status_code=404, detail="Operation type not found")
    
    return {
        "id": op_type.id,
        "name": op_type.name,
        "description": op_type.description,
        "created_at": op_type.created_at,
    }

@app.put("/operation-types/{type_id}")
async def update_type(
    type_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Update an operation type"""
    op_type = update_operation_type(session, type_id, name, description)
    if not op_type:
        raise HTTPException(status_code=404, detail="Operation type not found")
    
    return {
        "id": op_type.id,
        "name": op_type.name,
        "description": op_type.description,
        "created_at": op_type.created_at,
    }

@app.delete("/operation-types/{type_id}")
async def delete_type(
    type_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Delete an operation type"""
    success = delete_operation_type(session, type_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete operation type that is in use")
    
    return {"message": "Operation type deleted successfully"}

@app.post("/operations/{operation_id}/assign-type")
async def assign_type_to_operation(
    operation_id: int,
    type_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Assign a type to an operation"""
    operation = assign_operation_type(session, operation_id, type_id)
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    return {
        "id": operation.id,
        "pdf_id": operation.pdf_id,
        "type_id": operation.type_id,
        "transaction_date": operation.transaction_date,
        "processed_date": operation.processed_date,
        "description": operation.description,
        "amount_lei": operation.amount_lei,
    }

@app.get("/operations/by-type/{type_id}")
async def get_operations_by_type_endpoint(
    type_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get all operations of a specific type"""
    operations = get_operations_by_type(session, type_id)
    return [
        {
            "id": op.id,
            "pdf_id": op.pdf_id,
            "type_id": op.type_id,
            "transaction_date": op.transaction_date,
            "processed_date": op.processed_date,
            "description": op.description,
            "amount_lei": op.amount_lei,
        }
        for op in operations
    ]

@app.get("/operations/with-types")
async def get_operations_with_types_endpoint(
    pdf_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get operations with their associated types"""
    operations_with_types = get_operations_with_types(session, pdf_id)
    return [
        {
            "operation": {
                "id": op.id,
                "pdf_id": op.pdf_id,
                "type_id": op.type_id,
                "transaction_date": op.transaction_date,
                "processed_date": op.processed_date,
                "description": op.description,
                "amount_lei": op.amount_lei,
            },
            "type": {
                "id": op_type.id,
                "name": op_type.name,
                "description": op_type.description,
            } if op_type else None
        }
        for op, op_type in operations_with_types
    ]


@app.get("/operations/null-types")
async def get_operations_with_null_types_endpoint(
    pdf_id: Optional[int] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get operations that have null type_id"""
    operations = get_operations_with_null_types(session, pdf_id)
    return [
        {
            "id": op.id,
            "pdf_id": op.pdf_id,
            "type_id": op.type_id,
            "transaction_date": op.transaction_date,
            "processed_date": op.processed_date,
            "description": op.description,
            "amount_lei": op.amount_lei,
        }
        for op in operations
    ]

# Monthly Reports endpoints
@app.get("/reports/available-months")
async def get_available_months_endpoint(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get list of available months with data"""
    return get_available_months(session)


@app.get("/reports/monthly/{year}/{month}")
async def get_monthly_report(
    year: int,
    month: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get monthly report data with pie chart and grouped operations"""
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    return get_monthly_report_data(session, year, month)


@app.get("/reports/monthly/{year}/{month}/type/{type_id}")
async def get_monthly_operations_by_type(
    year: int,
    month: int,
    type_id: int,
    limit: int = 10,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_with_db_path)
):
    """Get operations of a specific type for a given month with pagination"""
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    result = get_operations_by_type_for_month(session, type_id, year, month, limit, offset)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


# Deduplication management endpoints
@app.get("/duplicates")
async def get_duplicates(session: Session = Depends(get_session)):
    """Get all duplicate operations in the database"""
    try:
        duplicates = get_duplicate_operations(session)
        return {
            "duplicate_pairs": len(duplicates),
            "duplicates": [
                {
                    "operation1": {
                        "id": op1.id,
                        "pdf_id": op1.pdf_id,
                        "transaction_date": op1.transaction_date,
                        "description": op1.description,
                        "amount_lei": op1.amount_lei,
                        "operation_hash": op1.operation_hash,
                    },
                    "operation2": {
                        "id": op2.id,
                        "pdf_id": op2.pdf_id,
                        "transaction_date": op2.transaction_date,
                        "description": op2.description,
                        "amount_lei": op2.amount_lei,
                        "operation_hash": op2.operation_hash,
                    }
                }
                for op1, op2 in duplicates
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting duplicates: {str(e)}")


@app.get("/deduplication-stats")
async def get_deduplication_stats(session: Session = Depends(get_session)):
    """Get deduplication statistics"""
    try:
        # Get total operations
        total_operations = session.exec(select(OperationRow)).all()
        
        # Get operations with hashes
        operations_with_hashes = session.exec(
            select(OperationRow).where(OperationRow.operation_hash.is_not(None))
        ).all()
        
        # Get operations without hashes
        operations_without_hashes = session.exec(
            select(OperationRow).where(OperationRow.operation_hash.is_(None))
        ).all()
        
        # Get duplicate pairs
        duplicates = get_duplicate_operations(session)
        
        return {
            "total_operations": len(total_operations),
            "operations_with_hashes": len(operations_with_hashes),
            "operations_without_hashes": len(operations_without_hashes),
            "duplicate_pairs": len(duplicates),
            "hash_coverage_percentage": (len(operations_with_hashes) / len(total_operations) * 100) if total_operations else 0,
            "duplicate_percentage": (len(duplicates) * 2 / len(total_operations) * 100) if total_operations else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting deduplication stats: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
