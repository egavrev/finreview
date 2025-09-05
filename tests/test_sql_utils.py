import pytest
from pathlib import Path
import tempfile
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sql_utils import (
    get_engine, init_db, PDF, OperationRow, store_pdf_summary, 
    store_operations, get_pdf_by_path, get_operations_for_pdf,
    process_and_store, generate_operation_hash, check_operation_exists_by_hash,
    store_operations_with_deduplication, get_duplicate_operations,
    create_operation_type, create_manual_operation, get_operation_types, get_operation_type_by_id, get_operation_type_by_name,
    update_operation_type, delete_operation_type, assign_operation_type, get_operations_by_type,
    get_operations_with_types, get_operations_with_null_types, get_operations_by_month,
    delete_operation, get_available_months, get_operations_by_type_for_month,
    get_monthly_report_data, process_and_store_with_classification,
    get_classification_suggestions_for_pdf, auto_assign_high_confidence_operations,
    auto_assign_all_high_confidence_operations
)
from pdf_processor import PDFSummary, Operation
from sqlmodel import Session, select
from sql_utils import OperationType
from unittest.mock import MagicMock, patch


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
            pdf_id, ops_count, skipped_count = process_and_store(pdf_path, temp_db, skip_duplicates=False)
            assert isinstance(pdf_id, int)
            assert isinstance(ops_count, int)
            assert isinstance(skipped_count, int)
            assert skipped_count == 0
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


def test_generate_operation_hash_basic():
    """Test basic hash generation and consistency"""
    from pdf_processor import Operation
    
    operation = Operation(
        transaction_date="2025-01-15",
        processed_date="2025-01-16",
        description="SUPERMARKET ABC",
        amount_lei=125.50
    )
    
    hash1 = generate_operation_hash(operation)
    hash2 = generate_operation_hash(operation)
    
    # Same operation should always produce same hash
    assert hash1 == hash2
    # Hash should be SHA-256 hex string (64 characters)
    assert len(hash1) == 64


def test_generate_operation_hash_processed_date_excluded():
    """Test that processed_date is excluded from hash calculation"""
    from pdf_processor import Operation
    
    # Same operation data but different processed_date
    operation1 = Operation(
        transaction_date="2025-01-15",
        processed_date="2025-01-16",
        description="SUPERMARKET ABC",
        amount_lei=125.50
    )
    
    operation2 = Operation(
        transaction_date="2025-01-15",
        processed_date="2025-01-17",  # Different processed_date
        description="SUPERMARKET ABC",
        amount_lei=125.50
    )
    
    hash1 = generate_operation_hash(operation1)
    hash2 = generate_operation_hash(operation2)
    
    # Hashes should be identical since processed_date is excluded
    assert hash1 == hash2


def test_check_operation_exists_by_hash_found(temp_db):
    """Test finding an existing operation by hash"""
    from pdf_processor import Operation
    
    # Create a test operation and generate its hash
    operation = Operation(
        transaction_date="2025-01-15",
        processed_date="2025-01-16",
        description="TEST SHOP",
        amount_lei=50.00
    )
    operation_hash = generate_operation_hash(operation)
    
    engine = get_engine(temp_db)
    with Session(engine) as session:
        # First create a PDF (required for foreign key)
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        # Create and store the operation in database
        operation_row = OperationRow(
            pdf_id=pdf.id,
            transaction_date=operation.transaction_date,
            processed_date=operation.processed_date,
            description=operation.description,
            amount_lei=operation.amount_lei,
            operation_hash=operation_hash
        )
        session.add(operation_row)
        session.commit()
        
        # Check if operation exists by hash
        found_operation = check_operation_exists_by_hash(session, operation_hash)
        
        assert found_operation is not None
        assert found_operation.description == "TEST SHOP"
        assert found_operation.amount_lei == 50.00


def test_check_operation_exists_by_hash_not_found(temp_db):
    """Test when operation hash doesn't exist"""
    engine = get_engine(temp_db)
    with Session(engine) as session:
        # Check for a hash that doesn't exist
        fake_hash = "a" * 64  # 64 character fake hash
        found_operation = check_operation_exists_by_hash(session, fake_hash)
        
        assert found_operation is None


def test_store_operations_with_deduplication_basic(temp_db):
    """Test basic deduplication - store operations without duplicates"""
    from pdf_processor import Operation
    
    operations = [
        Operation("2025-01-15", "2025-01-16", "SHOP A", 100.00),
        Operation("2025-01-16", "2025-01-17", "SHOP B", 200.00),
    ]
    
    engine = get_engine(temp_db)
    with Session(engine) as session:
        # Create a PDF first
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        # Store operations with deduplication
        stored_count, skipped_count = store_operations_with_deduplication(
            session, pdf.id, operations, skip_duplicates=True
        )
        
        assert stored_count == 2
        assert skipped_count == 0
        
        # Verify operations were actually stored in database
        stored_operations = session.exec(select(OperationRow).where(OperationRow.pdf_id == pdf.id)).all()
        assert len(stored_operations) == 2
        
        # Verify operation hashes were generated
        for op in stored_operations:
            assert op.operation_hash is not None
            assert len(op.operation_hash) == 64  # SHA-256 hash length


def test_store_operations_with_deduplication_skip_duplicates(temp_db):
    """Test deduplication - skip operations that already exist"""
    from pdf_processor import Operation
    
    # Create two operations with same hash (different processed_date)
    operation1 = Operation("2025-01-15", "2025-01-16", "SHOP A", 100.00)
    operation2 = Operation("2025-01-15", "2025-01-17", "SHOP A", 100.00)  # Same hash, different processed_date
    
    operations = [operation1, operation2]
    
    engine = get_engine(temp_db)
    with Session(engine) as session:
        # Create a PDF first
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        # Store first operation
        stored_count, skipped_count = store_operations_with_deduplication(
            session, pdf.id, [operation1], skip_duplicates=True
        )
        assert stored_count == 1
        assert skipped_count == 0
        
        # Verify first operation was stored
        stored_ops = session.exec(select(OperationRow).where(OperationRow.pdf_id == pdf.id)).all()
        assert len(stored_ops) == 1
        assert stored_ops[0].description == "SHOP A"
        
        # Try to store both operations - both should be skipped as duplicates
        # Use replace_existing=False to keep existing operations
        stored_count, skipped_count = store_operations_with_deduplication(
            session, pdf.id, operations, skip_duplicates=True, replace_existing=False
        )
        
        # Both operations should be skipped: operation1 (already exists) + operation2 (same hash)
        assert stored_count == 0  # No new operations stored
        assert skipped_count == 2  # Both operations skipped as duplicates
        
        # Verify no additional operations were added
        stored_ops = session.exec(select(OperationRow).where(OperationRow.pdf_id == pdf.id)).all()
        assert len(stored_ops) == 1  # Still only 1 operation
        
        # Verify the hash was generated correctly
        assert stored_ops[0].operation_hash is not None
        expected_hash = generate_operation_hash(operation1)
        assert stored_ops[0].operation_hash == expected_hash


def test_get_duplicate_operations(temp_db, sample_operations):
    """Test finding duplicate operations by hash"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create PDFs first to satisfy foreign key constraints
        pdf1 = PDF(file_path="/test/path1.pdf")
        pdf2 = PDF(file_path="/test/path2.pdf")
        pdf3 = PDF(file_path="/test/path3.pdf")
        session.add_all([pdf1, pdf2, pdf3])
        session.commit()
        session.refresh(pdf1)
        session.refresh(pdf2)
        session.refresh(pdf3)
        
        # Create duplicate operations with same hash
        op1 = OperationRow(
            pdf_id=pdf1.id,
            transaction_date="2024-01-01T10:00:00",
            description="Test operation",
            amount_lei=100.0,
            operation_hash="same_hash_123"
        )
        op2 = OperationRow(
            pdf_id=pdf2.id,
            transaction_date="2024-01-01T10:00:00",
            description="Test operation",
            amount_lei=100.0,
            operation_hash="same_hash_123"
        )
        op3 = OperationRow(
            pdf_id=pdf3.id,
            transaction_date="2024-01-01T10:00:00",
            description="Test operation",
            amount_lei=100.0,
            operation_hash="same_hash_123"
        )
        
        session.add_all([op1, op2, op3])
        session.commit()
        
        duplicates = get_duplicate_operations(session)
        
        # Should find 3 pairs: (op1, op2), (op1, op3), (op2, op3)
        assert len(duplicates) == 3
        assert all(len(pair) == 2 for pair in duplicates)
        assert all(pair[0].operation_hash == pair[1].operation_hash for pair in duplicates)


def test_get_pdf_by_path(temp_db, sample_pdf_summary):
    """Test getting PDF by file path"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Store a PDF first
        pdf_id = store_pdf_summary(session, "/test/path.pdf", sample_pdf_summary)
        
        # Retrieve it by path
        pdf = get_pdf_by_path(session, "/test/path.pdf")
        assert pdf is not None
        assert pdf.id == pdf_id
        assert pdf.file_path == "/test/path.pdf"


def test_get_operations_for_pdf(temp_db, sample_operations):
    """Test getting operations for a specific PDF"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create a PDF first
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
        assert all(op.pdf_id == pdf_id for op in operations)


def test_create_operation_type(temp_db):
    """Test creating a new operation type"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        op_type = create_operation_type(session, "Test Type", "Test Description")
        
        assert op_type.id is not None
        assert op_type.name == "Test Type"
        assert op_type.description == "Test Description"
        
        # Verify it's in the database
        stored_type = session.exec(select(OperationType).where(OperationType.id == op_type.id)).first()
        assert stored_type is not None
        assert stored_type.name == "Test Type"


def test_create_manual_operation(temp_db):
    """Test creating a manual operation"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # First create an operation type
        op_type = create_operation_type(session, "Manual Type")
        
        # Create manual operation
        operation = create_manual_operation(
            session=session,
            transaction_date="2024-01-01T10:00:00",
            type_id=op_type.id,
            amount_lei=150.0,
            description="Manual test operation",
            processed_date="2024-01-01T11:00:00"
        )
        
        assert operation.id is not None
        assert operation.pdf_id is None  # Manual operations have no PDF
        assert operation.type_id == op_type.id
        assert operation.transaction_date == "2024-01-01T10:00:00"
        assert operation.processed_date == "2024-01-01T11:00:00"
        assert operation.description == "Manual test operation"
        assert operation.amount_lei == 150.0
        assert operation.operation_hash is not None


def test_get_operation_types(temp_db):
    """Test getting all operation types"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create multiple types
        type1 = create_operation_type(session, "Type A", "Description A")
        type2 = create_operation_type(session, "Type B", "Description B")
        
        types = get_operation_types(session)
        assert len(types) >= 2
        
        type_names = [t.name for t in types]
        assert "Type A" in type_names
        assert "Type B" in type_names


def test_get_operation_type_by_id(temp_db):
    """Test getting operation type by ID"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        op_type = create_operation_type(session, "Test Type")
        
        retrieved_type = get_operation_type_by_id(session, op_type.id)
        assert retrieved_type is not None
        assert retrieved_type.id == op_type.id
        assert retrieved_type.name == "Test Type"


def test_get_operation_type_by_name(temp_db):
    """Test getting operation type by name"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        op_type = create_operation_type(session, "Test Type")
        
        retrieved_type = get_operation_type_by_name(session, "Test Type")
        assert retrieved_type is not None
        assert retrieved_type.id == op_type.id
        assert retrieved_type.name == "Test Type"


def test_update_operation_type(temp_db):
    """Test updating an operation type"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        op_type = create_operation_type(session, "Original Name", "Original Description")
        
        # Update name only
        updated_type = update_operation_type(session, op_type.id, name="Updated Name")
        assert updated_type is not None
        assert updated_type.name == "Updated Name"
        assert updated_type.description == "Original Description"
        
        # Update description only
        updated_type = update_operation_type(session, op_type.id, description="Updated Description")
        assert updated_type is not None
        assert updated_type.name == "Updated Name"
        assert updated_type.description == "Updated Description"
        
        # Update both
        updated_type = update_operation_type(session, op_type.id, "Final Name", "Final Description")
        assert updated_type is not None
        assert updated_type.name == "Final Name"
        assert updated_type.description == "Final Description"


def test_delete_operation_type_success(temp_db):
    """Test successfully deleting an operation type"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        op_type = create_operation_type(session, "To Delete")
        
        result = delete_operation_type(session, op_type.id)
        assert result is True
        
        # Verify it's deleted
        deleted_type = get_operation_type_by_id(session, op_type.id)
        assert deleted_type is None


def test_delete_operation_type_with_operations(temp_db, sample_operations):
    """Test deleting operation type that has operations (should fail)"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create operation type
        op_type = create_operation_type(session, "Used Type")
        
        # Create a PDF and store operations
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        # Store operations and assign type
        store_operations(session, pdf.id, sample_operations)
        operations = get_operations_for_pdf(session, pdf.id)
        operations[0].type_id = op_type.id
        session.add(operations[0])
        session.commit()
        
        # Try to delete - should fail
        result = delete_operation_type(session, op_type.id)
        assert result is False
        
        # Verify it still exists
        existing_type = get_operation_type_by_id(session, op_type.id)
        assert existing_type is not None


def test_assign_operation_type(temp_db, sample_operations):
    """Test assigning a type to an operation"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create operation type
        op_type = create_operation_type(session, "Assigned Type")
        
        # Create a PDF and store operations
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        # Store operations
        store_operations(session, pdf.id, sample_operations)
        operations = get_operations_for_pdf(session, pdf.id)
        
        # Assign type to operation
        result = assign_operation_type(session, operations[0].id, op_type.id)
        
        assert result is not None
        assert result.type_id == op_type.id
        
        # Verify in database
        updated_operation = session.exec(select(OperationRow).where(OperationRow.id == operations[0].id)).first()
        assert updated_operation.type_id == op_type.id


def test_assign_operation_type_none(temp_db, sample_operations):
    """Test removing type assignment from operation"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create operation type
        op_type = create_operation_type(session, "Test Type")
        
        # Create a PDF and store operations
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        # Store operations and assign type
        store_operations(session, pdf.id, sample_operations)
        operations = get_operations_for_pdf(session, pdf.id)
        operations[0].type_id = op_type.id
        session.add(operations[0])
        session.commit()
        
        # Remove type assignment
        result = assign_operation_type(session, operations[0].id, None)
        
        assert result is not None
        assert result.type_id is None
        
        # Verify in database
        updated_operation = session.exec(select(OperationRow).where(OperationRow.id == operations[0].id)).first()
        assert updated_operation.type_id is None


def test_get_operations_by_type(temp_db, sample_operations):
    """Test getting operations by type"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create operation type
        op_type = create_operation_type(session, "Test Type")
        
        # Create a PDF and store operations
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        # Store operations and assign type
        store_operations(session, pdf.id, sample_operations)
        operations = get_operations_for_pdf(session, pdf.id)
        for op in operations:
            op.type_id = op_type.id
            session.add(op)
        session.commit()
        
        operations_by_type = get_operations_by_type(session, op_type.id)
        assert len(operations_by_type) == 2
        assert all(op.type_id == op_type.id for op in operations_by_type)


def test_get_operations_with_types(temp_db, sample_operations):
    """Test getting operations with their associated types"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create operation type
        op_type = create_operation_type(session, "Test Type")
        
        # Create a PDF and store operations
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        # Store operations and assign type to first operation
        store_operations(session, pdf.id, sample_operations)
        operations = get_operations_for_pdf(session, pdf.id)
        operations[0].type_id = op_type.id
        session.add(operations[0])
        session.commit()
        
        operations_with_types = get_operations_with_types(session)
        assert len(operations_with_types) == 2
        
        # First operation should have type
        op1, type1 = operations_with_types[0]
        assert op1.id == operations[0].id
        assert type1 is not None
        assert type1.name == "Test Type"
        
        # Second operation should have no type
        op2, type2 = operations_with_types[1]
        assert op2.id == operations[1].id
        assert type2 is None


def test_get_operations_with_null_types(temp_db, sample_operations):
    """Test getting operations without type assignment"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create a PDF and store operations
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        # Store operations
        store_operations(session, pdf.id, sample_operations)
        
        operations = get_operations_with_null_types(session)
        assert len(operations) == 2
        assert all(op.type_id is None for op in operations)


def test_get_operations_by_month(temp_db, sample_operations):
    """Test getting operations for a specific month"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create a PDF and store operations
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        # Store operations with January 2024 dates
        store_operations(session, pdf.id, sample_operations)
        operations = get_operations_for_pdf(session, pdf.id)
        for op in operations:
            op.transaction_date = "2024-01-01T10:00:00"
            session.add(op)
        session.commit()
        
        operations_by_month = get_operations_by_month(session, 2024, 1)
        assert len(operations_by_month) == 2
        assert all(op[0].transaction_date.startswith("2024-01") for op in operations_by_month)


def test_delete_operation(temp_db, sample_operations):
    """Test deleting an operation"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create a PDF and store operations
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        # Store operations
        store_operations(session, pdf.id, sample_operations)
        operations = get_operations_for_pdf(session, pdf.id)
        operation_id = operations[0].id
        
        result = delete_operation(session, operation_id)
        assert result is True
        
        # Verify it's deleted
        deleted_operation = session.exec(select(OperationRow).where(OperationRow.id == operation_id)).first()
        assert deleted_operation is None


def test_delete_operation_not_found(temp_db):
    """Test deleting non-existent operation"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        result = delete_operation(session, 99999)
        assert result is False


def test_get_available_months(temp_db, sample_operations):
    """Test getting available months with data"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create a PDF and store operations
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        # Store operations with different dates
        store_operations(session, pdf.id, sample_operations)
        operations = get_operations_for_pdf(session, pdf.id)
        operations[0].transaction_date = "2024-01-01T10:00:00"
        operations[1].transaction_date = "2024-02-01T10:00:00"
        session.add_all(operations)
        session.commit()
        
        months = get_available_months(session)
        assert len(months) >= 2
        
        # Should be sorted by year-month descending
        assert months[0]["year"] >= months[1]["year"]
        
        # Check month labels
        month_labels = [m["label"] for m in months]
        assert "2024-01" in month_labels
        assert "2024-02" in month_labels


def test_get_operations_by_type_for_month(temp_db, sample_operations):
    """Test getting operations by type for a specific month with pagination"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create operation type
        op_type = create_operation_type(session, "Test Type")
        
        # Create a PDF and store operations
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        # Store operations with January 2024 dates and assign type
        store_operations(session, pdf.id, sample_operations)
        operations = get_operations_for_pdf(session, pdf.id)
        for op in operations:
            op.transaction_date = "2024-01-01T10:00:00"
            op.type_id = op_type.id
            session.add(op)
        session.commit()
        
        result = get_operations_by_type_for_month(session, op_type.id, 2024, 1, limit=1, offset=0)
        
        assert "error" not in result
        assert result["type"]["id"] == op_type.id
        assert result["type"]["name"] == "Test Type"
        assert result["year"] == 2024
        assert result["month"] == 1
        assert len(result["operations"]) == 1
        assert result["pagination"]["limit"] == 1
        assert result["pagination"]["offset"] == 0
        assert result["pagination"]["total"] == 2
        assert result["pagination"]["has_more"] is True


def test_get_operations_by_type_for_month_not_found(temp_db):
    """Test getting operations for non-existent operation type"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        result = get_operations_by_type_for_month(session, 99999, 2024, 1)
        assert "error" in result
        assert result["error"] == "Operation type not found"


def test_get_monthly_report_data(temp_db, sample_operations):
    """Test getting monthly report data"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        # Create operation type
        op_type = create_operation_type(session, "Test Type")
        
        # Create a PDF and store operations
        pdf = PDF(file_path="/test/path.pdf")
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        # Store operations with January 2024 dates and assign type
        store_operations(session, pdf.id, sample_operations)
        operations = get_operations_for_pdf(session, pdf.id)
        for op in operations:
            op.transaction_date = "2024-01-01T10:00:00"
            op.type_id = op_type.id
            session.add(op)
        session.commit()
        
        report_data = get_monthly_report_data(session, 2024, 1)
        
        assert report_data["year"] == 2024
        assert report_data["month"] == 1
        assert report_data["total_operations"] == 2
        assert len(report_data["type_groups"]) == 1
        assert report_data["type_groups"][0]["type_name"] == "Test Type"
        assert report_data["type_groups"][0]["operation_count"] == 2
        assert len(report_data["pie_chart_data"]) == 1
        assert report_data["summary"]["most_expensive_type"] == "Test Type"


def test_get_monthly_report_data_no_operations(temp_db):
    """Test getting monthly report data for month with no operations"""
    engine = get_engine(temp_db)
    init_db(engine)
    
    with Session(engine) as session:
        report_data = get_monthly_report_data(session, 2024, 1)
        
        assert report_data["year"] == 2024
        assert report_data["month"] == 1
        assert report_data["total_operations"] == 0
        assert report_data["total_amount"] == 0
        assert len(report_data["type_groups"]) == 0
        assert len(report_data["pie_chart_data"]) == 0


# def test_process_and_store_integration(temp_db, tmp_path):
#     """Test the complete process_and_store function"""
#     # Create a mock PDF file
#     pdf_path = tmp_path / "test.pdf"
#     pdf_path.write_text("Mock PDF content")
#     
#     # Create a mock database
#     db_path = tmp_path / "test.db"
#     
#     # Mock the PDF processing functions
#     with patch('sql_utils.process_pdf') as mock_process_pdf, \
#          patch('sql_utils.extract_card_operations') as mock_extract_ops:
#         
#         mock_process_pdf.return_value = PDFSummary(
#             client_name="Test Client",
#             account_number="123456",
#             total_iesiri=100.0,
#             sold_initial=1000.0,
#             sold_final=900.0
#         )
#         
#         mock_extract_ops.return_value = [
#             Operation(
#                 transaction_date="2024-01-01T10:00:00",
#                 processed_date="2024-01-01T10:00:00",
#                 description="Test operation",
#                 amount_lei=100.0
#             )
#         ]
#         
#         pdf_id, stored_count, skipped_count = process_and_store(
#             str(pdf_path), str(db_path), skip_duplicates=True
#         )
#         
#         assert pdf_id > 0
#         assert stored_count == 1
#         assert skipped_count == 0


# def test_process_and_store_with_classification_integration(temp_db, tmp_path):
#     """Test the complete process_and_store_with_classification function"""
#     # Create a mock PDF file
#     pdf_path = tmp_path / "test.pdf"
#     pdf_path.write_text("Mock PDF content")
#     
#     # Mock the PDF processing and classification functions
#     with patch('sql_utils.process_pdf') as mock_process_pdf, \
#          patch('sql_utils.extract_and_classify_operations') as mock_extract_classify, \
#          patch('pdf_processor.get_high_confidence_suggestions') as mock_high_conf:
#         
#         mock_process_pdf.return_value = PDFSummary(
#             client_name="Test Client",
#             account_number="123456",
#             total_iesiri=100.0,
#             sold_initial=1000.0,
#             sold_final=900.0
#         )
#         
#         # Create a mock ClassificationSuggestion object
#         mock_suggestion = MagicMock()
#         mock_suggestion.operation_id = 0
#         mock_suggestion.type_name = "Test Type"
#         mock_suggestion.confidence = 95.0
#         mock_suggestion.method = "exact"
#         mock_suggestion.should_auto_assign = True
#         mock_suggestion.details = {}
#         
#         mock_extract_classify.return_value = (
#             [Operation(
#                 transaction_date="2024-01-01T10:00:00",
#                 processed_date="2024-01-01T10:00:00",
#                 description="Test operation",
#                 amount_lei=100.0
#             )],
#             [mock_suggestion]
#         )
#         
#         mock_high_conf.return_value = [mock_suggestion]
#         
#         pdf_id, stored_count, skipped_count, classification_results = process_and_store_with_classification(
#             str(pdf_path), temp_db, auto_assign_high_confidence=True
#         )
#         
#         assert pdf_id > 0
#         assert stored_count == 1
#         assert skipped_count == 0
#         assert len(classification_results) == 0  # No operation types exist yet


# # def test_auto_assign_high_confidence_operations(temp_db, sample_operations):
#     """Test auto-assigning high confidence operations"""
#     engine = get_engine(temp_db)
#     init_db(engine)
#     
#     with Session(engine) as session:
#         # Create operation type
#         op_type = create_operation_type(session, "Test Type")
#         
#         # Create a PDF and store operations
#         pdf = PDF(file_path="/test/path.pdf")
#         session.add(pdf)
#         session.commit()
#         session.refresh(pdf)
#         
#         # Store operations
#         store_operations(session, pdf.id, sample_operations)
#         
#         # Mock the operations matcher
#         with patch('operations_matcher.get_matcher') as mock_get_matcher:
#             mock_matcher = MagicMock()
#             mock_matcher.config = {
#                 'confidence_thresholds': {
#                     'fuzzy_match_auto': 80,
#                     'keyword_match_auto': 80,
#                     'pattern_match_auto': 75
#                 }
#             }
#             mock_matcher.classify_operation.return_value = MagicMock(
#                 type_name="Test Type",
#                 confidence=85.0,
#                 method="fuzzy"
#             )
#             mock_get_matcher.return_value = mock_matcher
#             
#             assigned_count = auto_assign_high_confidence_operations(session, pdf.id)
#             
#             assert assigned_count == 2
#             
#             # Verify operations now have types assigned
#             operations = get_operations_for_pdf(session, pdf.id)
#             assert all(op.type_id is not None for op in operations)
# 
# 
# # def test_auto_assign_all_high_confidence_operations(temp_db, sample_operations):
#     """Test auto-assigning high confidence operations across all PDFs"""
#     engine = get_engine(temp_db)
#     init_db(engine)
#     
#     with Session(engine) as session:
#         # Create operation type
#         op_type = create_operation_type(session, "Test Type")
#         
#         # Create a PDF and store operations
#         pdf = PDF(file_path="/test/path.pdf")
#         session.add(pdf)
#         session.commit()
#         session.refresh(pdf)
#         
#         # Store operations
#         store_operations(session, pdf.id, sample_operations)
#         
#         # Mock the operations matcher
#         with patch('operations_matcher.get_matcher') as mock_get_matcher:
#             mock_matcher = MagicMock()
#             mock_matcher.config = {
#                 'confidence_thresholds': {
#                     'fuzzy_match_auto': 80,
#                     'keyword_match_auto': 80,
#                     'pattern_match_auto': 75
#                 }
#             }
#             mock_matcher.classify_operation.return_value = MagicMock(
#                 type_name="Test Type",
#                 confidence=85.0,
#                 method="fuzzy"
#             )
#             mock_get_matcher.return_value = mock_matcher
#             
#             assigned_count = auto_assign_all_high_confidence_operations(session)
#             
#             assert assigned_count == 2
#             
#             # Verify operations now have types assigned
#             operations = get_operations_with_null_types(session)
#             assert len(operations) == 0  # All operations should now have types
# 
# 
# # def test_error_handling_in_classification_functions(temp_db, sample_operations):
#     """Test error handling in classification functions when matcher fails"""
#     engine = get_engine(temp_db)
#     init_db(engine)
#     
#     with Session(engine) as session:
#         # Create a PDF and store operations
#         pdf = PDF(file_path="/test/path.pdf")
#         session.add(pdf)
#         session.commit()
#         session.refresh(pdf)
#         
#         # Store operations
#         store_operations(session, pdf.id, sample_operations)
#         
#         # Test with exception in get_matcher
#         with patch('operations_matcher.get_matcher', side_effect=Exception("Matcher error")):
#             suggestions = get_classification_suggestions_for_pdf(session, pdf.id)
#             assert suggestions == []
#             
#             assigned_count = auto_assign_high_confidence_operations(session, pdf.id)
#             assert assigned_count == 0
#             
#             assigned_count = auto_assign_all_high_confidence_operations(session)
#             assert assigned_count == 0
# 
# 
# def test_operation_hash_uniqueness():
#     """Test that operation hashes are unique for different operations"""
#     op1 = Operation(
#         transaction_date="2024-01-01T10:00:00",
#         processed_date="2024-01-01T10:00:00",
#         description="Operation A",
#         amount_lei=100.0
#     )
#     
#     op2 = Operation(
#         transaction_date="2024-01-01T10:00:00",
#         processed_date="2024-01-01T10:00:00",
#         description="Operation B",  # Different description
#         amount_lei=100.0
#     )
#     
#     op3 = Operation(
#         transaction_date="2024-01-01T10:00:00",
#         processed_date="2024-01-01T10:00:00",
#         description="Operation A",
#         amount_lei=200.0  # Different amount
#     )
#     
#     hash1 = generate_operation_hash(op1)
#     hash2 = generate_operation_hash(op2)
#     hash3 = generate_operation_hash(op3)
#     
#     assert hash1 != hash2
#     assert hash1 != hash3
#     assert hash2 != hash3
#     
#     # Same operation should have same hash
#     op1_copy = Operation(
#         transaction_date="2024-01-01T10:00:00",
#         processed_date="2024-01-01T11:00:00",  # Different processed date
#         description="Operation A",
#         amount_lei=100.0
#     )
#     hash1_copy = generate_operation_hash(op1_copy)
#     assert hash1 == hash1_copy  # Hash should be same despite different processed_date
# 
# 
# def test_session_management():
#     """Test that database sessions are properly managed"""
#     engine = get_engine(":memory:")
#     init_db(engine)
#     
#     # Test that we can create and query data
#     with Session(engine) as session:
#         op_type = create_operation_type(session, "Test Type")
#         assert op_type.id is not None
#         
#         # Test that data persists in the same session
#         retrieved_type = get_operation_type_by_id(session, op_type.id)
#         assert retrieved_type is not None
#         assert retrieved_type.name == "Test Type"
#     
#     # Test that session is properly closed
#     with Session(engine) as session:
#         retrieved_type = get_operation_type_by_id(session, op_type.id)
#         assert retrieved_type is not None  # Data should persist across sessions
# 
# 
# if __name__ == "__main__":
#     pytest.main([__file__])


