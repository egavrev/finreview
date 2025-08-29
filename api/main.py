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

from sql_utils import get_engine, init_db, PDF, OperationRow, process_and_store, get_pdf_by_path, get_operations_for_pdf
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
