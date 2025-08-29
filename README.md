# Financial Review Application

A modern web application for processing and analyzing PDF financial statements. Built with FastAPI backend and Next.js frontend.

## Features

- 📄 **PDF Upload & Processing**: Upload financial statement PDFs and extract key data
- 📊 **Statistics Dashboard**: View overall statistics and summaries
- 💰 **Operations Analysis**: Detailed view of all financial operations
- 🎨 **Modern UI**: Clean, responsive interface built with shadcn/ui and Tailwind CSS
- 🔍 **Data Persistence**: SQLite database with SQLModel ORM

## Architecture

- **Backend**: FastAPI (Python 3.11+) with SQLModel/SQLAlchemy
- **Frontend**: Next.js 13+ with TypeScript and Tailwind CSS
- **Database**: SQLite (can be migrated to PostgreSQL)
- **UI Components**: shadcn/ui design system

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Node.js 16+ (for frontend)
- npm or yarn

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database**:
   ```bash
   python db_init.py
   ```

3. **Start the FastAPI server**:
   ```bash
   python api/main.py
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:3000`

## Usage

### Uploading PDFs

1. Open the web application at `http://localhost:3000`
2. Click "Choose File" and select a PDF financial statement
3. Click "Upload" to process the PDF
4. View the extracted data in the dashboard

### Viewing Statistics

The dashboard shows:
- Total number of processed PDFs
- Total operations extracted
- Total withdrawals (iesiri)
- Average amount per operation

### Analyzing Operations

1. Click "View Details" on any PDF in the dashboard
2. See detailed information about:
   - Client and account information
   - Balance ranges (initial/final)
   - Complete list of operations with dates and amounts

## API Endpoints

- `GET /` - API health check
- `POST /upload-pdf` - Upload and process a PDF file
- `GET /pdfs` - List all processed PDFs
- `GET /pdfs/{id}` - Get details for a specific PDF
- `GET /operations` - List operations with optional filtering
- `GET /statistics` - Get overall statistics

## Development

### Project Structure

```
finreview/
├── api/
│   └── main.py              # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js app router
│   │   ├── components/      # UI components
│   │   └── lib/             # Utilities
│   └── package.json
├── tests/                   # Python tests
├── pdf_processor.py         # PDF processing logic
├── sql_utils.py            # Database utilities
├── ingest_pdf.py           # CLI for batch processing
└── requirements.txt        # Python dependencies
```

### Running Tests

```bash
# Run Python tests
pytest

# Run with coverage
pytest --cov=.
```

### Database Management

The application uses SQLite by default. To migrate to PostgreSQL:

1. Update the database URL in `sql_utils.py`
2. Install PostgreSQL dependencies
3. Run database migrations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.
