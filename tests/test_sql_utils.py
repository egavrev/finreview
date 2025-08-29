import pytest
from pathlib import Path
import tempfile
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sql_utils import (
    get_engine, init_db, PDF, OperationRow, store_pdf_summary, 
    store_operations, get_pdf_by_path, get_operations_for_pdf,
    process_and_store
)
from pdf_processor import PDFSummary, Operation
from sqlmodel import Session, select


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as tmp_file:
        db_path = Path(tmp_file.name)
    
    engine = get_engine(db_path)
    init_db(engine)
    
    yield db_path
    
    # Cleanup
    db_path.unlink(missing_ok=True)


@pytest.fixture
def sample_pdf_summary():
    """Create a sample PDF summary for testing"""
    return PDFSummary(
        client_name="Test Client",
        account_number="MD1234567890",
        total_iesiri=1000.50,
        sold_initial=5000.00,
        sold_final=4000.00
    )


@pytest.fixture
def sample_operations():
    """Create sample operations for testing"""
    return [
        Operation(
            transaction_date="2025-01-01",
            processed_date="2025-01-02",
            description="Test Operation 1",
            amount_lei=100.00
        ),
        Operation(
            transaction_date="2025-01-03",
            processed_date="2025-01-04",
            description="Test Operation 2",
            amount_lei=-50.00
        )
    ]


def test_get_engine(temp_db):
    """Test database engine creation"""
    engine = get_engine(temp_db)
    assert engine is not None
    
    # Test that we can create a session
    with Session(engine) as session:
        assert session is not None


def test_init_db(temp_db):
    """Test database initialization"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    # Check that tables were created by trying to query them
    with Session(engine) as session:
        pdfs = session.exec(select(PDF)).all()
        operations = session.exec(select(OperationRow)).all()
        assert isinstance(pdfs, list)
        assert isinstance(operations, list)


def test_store_pdf_summary_new(temp_db, sample_pdf_summary):
    """Test storing a new PDF summary"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        pdf_id = store_pdf_summary(session, "/test/path.pdf", sample_pdf_summary)
        assert pdf_id > 0
        
        # Verify the PDF was stored correctly
        pdf = session.exec(select(PDF).where(PDF.id == pdf_id)).first()
        assert pdf is not None
        assert pdf.client_name == "Test Client"
        assert pdf.account_number == "MD1234567890"
        assert pdf.total_iesiri == 1000.50
        assert pdf.sold_initial == 5000.00
        assert pdf.sold_final == 4000.00


def test_store_pdf_summary_existing(temp_db, sample_pdf_summary):
    """Test storing a PDF summary for an existing file path"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Store the same PDF twice
        pdf_id1 = store_pdf_summary(session, "/test/path.pdf", sample_pdf_summary)
        
        # Modify the summary
        updated_summary = PDFSummary(
            client_name="Updated Client",
            account_number="MD9876543210",
            total_iesiri=2000.00,
            sold_initial=6000.00,
            sold_final=5000.00
        )
        
        pdf_id2 = store_pdf_summary(session, "/test/path.pdf", updated_summary)
        
        # Should return the same ID
        assert pdf_id1 == pdf_id2
        
        # Verify the PDF was updated
        pdf = session.exec(select(PDF).where(PDF.id == pdf_id1)).first()
        assert pdf.client_name == "Updated Client"
        assert pdf.account_number == "MD9876543210"


def test_store_operations_new(temp_db, sample_operations):
    """Test storing new operations"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    # First create a PDF
    with Session(engine) as session:
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        pdf_id = pdf.id
        
        # Store operations
        count = store_operations(session, pdf_id, sample_operations)
        assert count == 2
        
        # Verify operations were stored
        operations = session.exec(select(OperationRow).where(OperationRow.pdf_id == pdf_id)).all()
        assert len(operations) == 2
        assert operations[0].description == "Test Operation 1"
        assert operations[1].description == "Test Operation 2"


def test_store_operations_replace(temp_db, sample_operations):
    """Test replacing existing operations"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create a PDF
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        pdf_id = pdf.id
        
        # Store initial operations
        store_operations(session, pdf_id, sample_operations)
        
        # Store new operations (should replace the old ones)
        new_operations = [
            Operation(
                transaction_date="2025-02-01",
                processed_date="2025-02-02",
                description="New Operation",
                amount_lei=75.00
            )
        ]
        
        count = store_operations(session, pdf_id, new_operations)
        assert count == 1
        
        # Verify only new operations exist
        operations = session.exec(select(OperationRow).where(OperationRow.pdf_id == pdf_id)).all()
        assert len(operations) == 1
        assert operations[0].description == "New Operation"


def test_get_pdf_by_path_found(temp_db, sample_pdf_summary):
    """Test getting PDF by path when it exists"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Store a PDF
        pdf_id = store_pdf_summary(session, "/test/path.pdf", sample_pdf_summary)
        
        # Retrieve it by path
        pdf = get_pdf_by_path(session, "/test/path.pdf")
        assert pdf is not None
        assert pdf.id == pdf_id
        assert pdf.client_name == "Test Client"


def test_get_pdf_by_path_not_found(temp_db):
    """Test getting PDF by path when it doesn't exist"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        pdf = get_pdf_by_path(session, "/nonexistent/path.pdf")
        assert pdf is None


def test_get_operations_for_pdf_found(temp_db, sample_operations):
    """Test getting operations for a PDF when they exist"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create a PDF
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        pdf_id = pdf.id
        
        # Store operations
        store_operations(session, pdf_id, sample_operations)
        
        # Retrieve operations
        operations = get_operations_for_pdf(session, pdf_id)
        assert len(operations) == 2
        assert operations[0].description == "Test Operation 1"
        assert operations[1].description == "Test Operation 2"


def test_get_operations_for_pdf_empty(temp_db):
    """Test getting operations for a PDF when none exist"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create a PDF without operations
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        pdf_id = pdf.id
        
        # Retrieve operations
        operations = get_operations_for_pdf(session, pdf_id)
        assert len(operations) == 0


def test_process_and_store_integration(temp_db):
    """Test the integrated process_and_store function"""
    # This test would require a real PDF file or mocking the PDF processing
    # For now, we'll test the function signature and basic behavior
    
    # Create a minimal test PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids []\n/Count 0\n>>\nendobj\nxref\n0 3\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \ntrailer\n<<\n/Size 3\n/Root 1 0 R\n>>\nstartxref\n149\n%%EOF\n')
        tmp_file.flush()
        pdf_path = Path(tmp_file.name)
    
    try:
        # Test that the function can be called (may fail due to PDF processing)
        try:
            pdf_id, ops_count = process_and_store(pdf_path, temp_db)
            assert isinstance(pdf_id, int)
            assert isinstance(ops_count, int)
        except Exception as e:
            # Expected if PDF processing fails, but function should be callable
            assert "pdfplumber" in str(e) or "PDF" in str(e)
    finally:
        pdf_path.unlink(missing_ok=True)


def test_pdf_model_validation():
    """Test PDF model validation"""
    pdf = PDF(
        file_path="/test/path.pdf",
        client_name="Test Client",
        account_number="MD1234567890",
        total_iesiri=1000.50,
        sold_initial=5000.00,
        sold_final=4000.00
    )
    
    assert pdf.file_path == "/test/path.pdf"
    assert pdf.client_name == "Test Client"
    assert pdf.account_number == "MD1234567890"
    assert pdf.total_iesiri == 1000.50


def test_operation_row_model_validation():
    """Test OperationRow model validation"""
    op = OperationRow(
        pdf_id=1,
        transaction_date="2025-01-01",
        processed_date="2025-01-02",
        description="Test Operation",
        amount_lei=100.00
    )
    
    assert op.pdf_id == 1
    assert op.transaction_date == "2025-01-01"
    assert op.processed_date == "2025-01-02"
    assert op.description == "Test Operation"
    assert op.amount_lei == 100.00


if __name__ == "__main__":
    pytest.main([__file__])


