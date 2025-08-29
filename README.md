# Financial Review API

A comprehensive financial document processing system that extracts and analyzes card operations from PDF account statements.

## Features

- **PDF Processing**: Extract financial data from PDF account statements
- **Data Analysis**: Parse and categorize financial operations
- **Database Storage**: Store processed data using SQLAlchemy/SQLModel
- **REST API**: FastAPI-based API for uploading and querying financial data
- **Comprehensive Testing**: 88% code coverage with unit and integration tests

## Architecture

- **Backend**: Python 3.11/3.12 with FastAPI
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy/SQLModel with Pydantic v2
- **PDF Processing**: pdfplumber for text and table extraction
- **Testing**: pytest with coverage reporting

## Project Structure

```
finreview/
├── api/
│   └── main.py              # FastAPI application
├── tests/
│   ├── conftest.py          # Pytest configuration
│   ├── test_api.py          # API endpoint tests
│   ├── test_pdf_processor.py # PDF processing tests
│   └── test_sql_utils.py    # Database utility tests
├── PDF_examples/            # Sample PDF files
├── pdf_processor.py         # PDF processing logic
├── sql_utils.py            # Database operations
├── requirements.txt         # Python dependencies
├── run_tests.py            # Test runner script
└── README.md               # This file
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd finreview
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the API

Start the FastAPI server:
```bash
python api/main.py
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `GET /` - Health check
- `GET /pdfs` - List all processed PDFs
- `POST /upload-pdf` - Upload and process a PDF file
- `GET /pdfs/{pdf_id}` - Get details of a specific PDF
- `GET /pdfs/{pdf_id}/operations` - Get operations for a specific PDF

### Processing PDFs from Command Line

```bash
python pdf_processor.py path/to/your/file.pdf
```

## Testing

### Running All Tests

```bash
python run_tests.py
```

### Running Specific Test Types

```bash
# Unit tests only
python run_tests.py unit

# Integration tests only
python run_tests.py integration
```

### Running Tests with Coverage

```bash
# Run tests with coverage report
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m coverage run -m pytest tests/ -v

# Generate coverage report
python -m coverage report -m --include="*.py" --omit="*/site-packages/*,*/tests/*"
```

### Test Coverage

Current test coverage: **88%**

- `pdf_processor.py`: 88% coverage
- `sql_utils.py`: 100% coverage  
- `api/main.py`: 79% coverage

## Test Structure

### Unit Tests (`tests/test_pdf_processor.py`)
- PDF text extraction and parsing
- Number normalization and amount parsing
- Table-based data extraction
- Pattern matching and search
- CLI functionality

### Unit Tests (`tests/test_sql_utils.py`)
- Database engine creation and initialization
- PDF summary storage and retrieval
- Operation storage and replacement
- Database query operations
- Model validation

### Integration Tests (`tests/test_api.py`)
- API endpoint functionality
- File upload validation
- Error handling
- CORS configuration
- Database integration

## Development

### Adding New Tests

1. Create test functions in the appropriate test file
2. Use pytest fixtures for common setup
3. Follow the naming convention: `test_<functionality>`
4. Add appropriate assertions and error checking

### Test Configuration

The test configuration is in `tests/conftest.py`:
- Automatic test categorization (unit/integration)
- Common fixtures for database and file operations
- Path configuration for imports

### Running Tests in Development

```bash
# Run tests with verbose output
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -v

# Run specific test file
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_api.py -v

# Run tests matching a pattern
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/ -k "test_upload" -v
```

## Dependencies

### Core Dependencies
- `fastapi`: Web framework
- `sqlmodel`: SQL database ORM
- `pdfplumber`: PDF text extraction
- `pydantic`: Data validation
- `uvicorn`: ASGI server

### Testing Dependencies
- `pytest`: Testing framework
- `pytest-cov`: Coverage reporting
- `httpx`: HTTP client for testing

## Contributing

1. Write tests for new functionality
2. Ensure test coverage remains above 80%
3. Run the full test suite before submitting changes
4. Follow the existing code style and patterns

## License

[Add your license information here]
