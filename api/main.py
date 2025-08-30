from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from typing import List, Optional
import uvicorn
from pathlib import Path
import tempfile
import shutil
import os

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sql_utils import (
    get_engine, init_db, PDF, OperationRow, OperationType, process_and_store, 
    get_pdf_by_path, get_operations_for_pdf, create_operation_type, get_operation_types,
    get_operation_type_by_id, update_operation_type, delete_operation_type,
    assign_operation_type, get_operations_by_type, get_operations_with_types,
    get_operations_with_null_types
)
from pdf_processor import PDFSummary, Operation

app = FastAPI(title="Financial Review API", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_PATH = Path("db.sqlite")
engine = get_engine(DB_PATH)
init_db(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/")
async def root():
    return {"message": "Financial Review API"}

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """Upload and process a PDF file"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = Path(tmp_file.name)
    
    try:
        # Process the PDF
        pdf_id, ops_count = process_and_store(tmp_path, DB_PATH)
        
        # Get the processed data
        pdf_record = get_pdf_by_path(session, tmp_path)
        operations = get_operations_for_pdf(session, pdf_id)
        
        return {
            "success": True,
            "pdf_id": pdf_id,
            "operations_count": ops_count,
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
async def list_pdfs(session: Session = Depends(get_session)):
    """List all processed PDFs"""
    pdfs = session.exec(select(PDF).order_by(PDF.id.desc())).all()
    return [
        {
            "id": pdf.id,
            "file_path": pdf.file_path,
            "client_name": pdf.client_name,
            "account_number": pdf.account_number,
            "total_iesiri": pdf.total_iesiri,
            "sold_initial": pdf.sold_initial,
            "sold_final": pdf.sold_final,
            "created_at": pdf.created_at,
        }
        for pdf in pdfs
    ]

@app.get("/pdfs/{pdf_id}")
async def get_pdf_details(pdf_id: int, session: Session = Depends(get_session)):
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

@app.get("/operations")
async def list_operations(
    pdf_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session)
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

@app.get("/statistics")
async def get_statistics(session: Session = Depends(get_session)):
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
    session: Session = Depends(get_session)
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
async def list_operation_types(session: Session = Depends(get_session)):
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
async def get_operation_type(type_id: int, session: Session = Depends(get_session)):
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
    session: Session = Depends(get_session)
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
async def delete_type(type_id: int, session: Session = Depends(get_session)):
    """Delete an operation type"""
    success = delete_operation_type(session, type_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete operation type that is in use")
    
    return {"message": "Operation type deleted successfully"}

@app.post("/operations/{operation_id}/assign-type")
async def assign_type_to_operation(
    operation_id: int,
    type_id: Optional[int] = None,
    session: Session = Depends(get_session)
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
    session: Session = Depends(get_session)
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
    session: Session = Depends(get_session)
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
    session: Session = Depends(get_session)
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
