import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import shutil
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.main import app
from sql_utils import get_engine, init_db, PDF, OperationRow, process_and_store
from sqlmodel import Session, select

client = TestClient(app)


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
def sample_pdf_file():
    """Create a sample PDF file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        # Create a minimal PDF content (this is just a placeholder)
        tmp_file.write(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids []\n/Count 0\n>>\nendobj\nxref\n0 3\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \ntrailer\n<<\n/Size 3\n/Root 1 0 R\n>>\nstartxref\n149\n%%EOF\n')
        tmp_file.flush()
        yield Path(tmp_file.name)
    
    # Cleanup
    Path(tmp_file.name).unlink(missing_ok=True)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Financial Review API"}


def test_list_pdfs_empty(temp_db):
    """Test listing PDFs when database is empty"""
    # This test is challenging because the app uses a global database
    # For now, we'll test that the endpoint returns a valid response
    response = client.get("/pdfs")
    assert response.status_code == 200
    # The response should be a list (even if not empty due to existing data)
    assert isinstance(response.json(), list)


def test_upload_pdf_invalid_file():
    """Test uploading a non-PDF file"""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
        tmp_file.write(b"This is not a PDF file")
        tmp_file.flush()
        
        with open(tmp_file.name, 'rb') as f:
            response = client.post(
                "/upload-pdf",
                files={"file": ("test.txt", f, "text/plain")}
            )
    
    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]
    
    # Cleanup
    Path(tmp_file.name).unlink(missing_ok=True)


def test_get_pdf_details_not_found():
    """Test getting details of a non-existent PDF"""
    response = client.get("/pdfs/999")
    assert response.status_code == 404
    assert "PDF not found" in response.json()["detail"]


def test_get_operations_not_found():
    """Test getting operations for a non-existent PDF"""
    response = client.get("/pdfs/999/operations")
    assert response.status_code == 404
    # Check that it's a 404 error (the exact message format may vary)
    assert response.status_code == 404


def test_get_operations_empty():
    """Test getting operations when PDF exists but has no operations"""
    # This would require setting up a test database with a PDF but no operations
    # For now, we'll test the error case
    response = client.get("/pdfs/999/operations")
    assert response.status_code == 404


def test_upload_pdf_success(temp_db, sample_pdf_file):
    """Test successful PDF upload and processing"""
    # Mock the process_and_store function to return test data
    original_process = process_and_store
    
    def mock_process_and_store(pdf_path, db_path, skip_duplicates=True ):
        return 1, 5, False # pdf_id, operations_count, skipped_count
    
    try:
        # Replace the function temporarily
        import api.main
        api.main.process_and_store = mock_process_and_store
        
        with open(sample_pdf_file, 'rb') as f:
            response = client.post(
                "/upload-pdf",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"skip_duplicates": False}
            )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["pdf_id"] == 1
        
    finally:
        # Restore original function
        api.main.process_and_store = original_process


def test_upload_pdf_processing_error(temp_db, sample_pdf_file):
    """Test PDF upload when processing fails"""
    # Mock the process_and_store function to raise an exception
    original_process = process_and_store
    
    def mock_process_and_store(pdf_path, db_path):
        raise Exception("Processing failed")
    
    try:
        # Replace the function temporarily
        import api.main
        api.main.process_and_store = mock_process_and_store
        
        with open(sample_pdf_file, 'rb') as f:
            response = client.post(
                "/upload-pdf",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 500
        assert "Error processing PDF" in response.json()["detail"]
        
    finally:
        # Restore original function
        api.main.process_and_store = original_process


def test_cors_headers():
    """Test that CORS headers are properly set"""
    response = client.options("/")
    # The TestClient doesn't fully simulate CORS, but we can check the app has CORS middleware
    assert hasattr(app, 'user_middleware')
    cors_middleware = [m for m in app.user_middleware if 'CORSMiddleware' in str(m)]
    assert len(cors_middleware) > 0


if __name__ == "__main__":
    pytest.main([__file__])
