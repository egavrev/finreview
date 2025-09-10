# Financial Review API

A comprehensive financial document processing system that extracts and analyzes card operations from PDF account statements.

## Features

- **PDF Processing**: Extract financial data from PDF account statements
- **Data Analysis**: Parse and categorize financial operations
- **Database Storage**: Store processed data using SQLAlchemy/SQLModel
- **REST API**: FastAPI-based API for uploading and querying financial data
- **Google OAuth 2.0 Authentication**: Secure access with Google account integration
- **Email Whitelist**: Restrict access to authorized family members only
- **JWT Token Management**: Secure session handling with JSON Web Tokens
- **Operations Management**: Web interface for categorizing and managing financial operations
- **Type Assignment**: Assign operation types to uncategorized transactions
- **Custom Types**: Create new operation types for better categorization
- **Protected Routes**: All pages and API endpoints require authentication
- **Comprehensive Testing**: 88% code coverage with unit and integration tests

## Architecture

- **Backend**: Python 3.11/3.12 with FastAPI
- **Frontend**: Next.js with TypeScript and shadcn/ui components
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy/SQLModel with Pydantic v2
- **Authentication**: Google OAuth 2.0 with JWT tokens
- **PDF Processing**: pdfplumber for text and table extraction
- **Testing**: pytest with coverage reporting

## Project Structure

```
finreview/
├── api/
│   └── main.py              # FastAPI application with authentication
├── frontend/                # Next.js frontend application
│   ├── src/
│   │   ├── app/            # Next.js app router pages
│   │   │   ├── operations/ # Operations management page
│   │   │   ├── reports/    # Reports page
│   │   │   ├── files/      # PDF files management page
│   │   │   ├── rules/      # Rules management page
│   │   │   ├── pdf/        # PDF details page
│   │   │   └── auth/       # Authentication pages
│   │   ├── components/     # Reusable UI components
│   │   │   ├── ui/         # shadcn/ui components
│   │   │   ├── ProtectedRoute.tsx # Route protection
│   │   │   └── LoginButton.tsx    # OAuth login
│   │   └── contexts/       # React contexts
│   │       └── AuthContext.tsx    # Authentication state
│   └── package.json        # Frontend dependencies
├── tests/
│   ├── conftest.py          # Pytest configuration
│   ├── test_api.py          # API endpoint tests
│   ├── test_pdf_processor.py # PDF processing tests
│   └── test_sql_utils.py    # Database utility tests
├── PDF_examples/            # Sample PDF files
├── pdf_processor.py         # PDF processing logic
├── sql_utils.py            # Database operations with user management
├── auth.py                 # Authentication logic and JWT handling
├── requirements.txt         # Python dependencies
├── run_tests.py            # Test runner script
├── .env                    # Environment variables (create from template)
├── env_template.txt        # Environment variables template
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

4. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

## Authentication Setup

This application uses Google OAuth 2.0 for secure authentication with email whitelist functionality to restrict access to authorized family members only.

### 1. Google Cloud Console Setup

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create a new project** or select an existing one
3. **Enable Google+ API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
4. **Create OAuth 2.0 credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8000/auth/google/callback` (for development)
     - `https://yourdomain.com/auth/google/callback` (for production)
5. **Copy your credentials**:
   - Client ID
   - Client Secret

### 2. Environment Variables Setup

1. **Copy the environment template**:
```bash
cp env_template.txt .env
```

2. **Edit the `.env` file** with your actual values:
```bash
# Google OAuth 2.0 Credentials (get these from Google Cloud Console)
GOOGLE_CLIENT_ID=your_actual_client_id_from_google
GOOGLE_CLIENT_SECRET=your_actual_client_secret_from_google
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# JWT Configuration (generate a secure random key)
JWT_SECRET_KEY=your_secure_random_jwt_secret_key
JWT_EXPIRATION_HOURS=24

# Email Whitelist (comma-separated list of authorized emails)
ALLOWED_EMAILS=your.email@gmail.com,your.wife.email@gmail.com,your.family.member@gmail.com
```

### 3. Generate JWT Secret Key

For security, generate a strong JWT secret key:

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using OpenSSL
openssl rand -base64 32
```

### 4. Authentication Flow

The authentication system works as follows:

1. **User clicks "Login with Google"** on the frontend
2. **Frontend redirects** to Google OAuth consent screen
3. **User authorizes** the application with their Google account
4. **Google redirects back** to the backend with an authorization code
5. **Backend exchanges code** for access token and fetches user info
6. **Backend checks email whitelist** - only authorized emails can proceed
7. **Backend creates/updates user** in the database
8. **Backend generates JWT token** and redirects to frontend
9. **Frontend stores JWT token** and uses it for all API requests
10. **All subsequent requests** include the JWT token in Authorization header

### 5. Security Features

- **Email Whitelist**: Only emails in `ALLOWED_EMAILS` can access the system
- **JWT Tokens**: Secure session management with configurable expiration
- **Protected Routes**: All frontend pages require authentication
- **Protected API Endpoints**: All backend endpoints require valid JWT tokens
- **CORS Configuration**: Properly configured for frontend-backend communication
- **Token Validation**: JWT tokens are validated on every API request

### 6. User Management

The system automatically:
- **Creates new users** when they first authenticate
- **Updates user information** on each login (name, picture, last_login)
- **Links operations to users** for data isolation
- **Stores user preferences** and authentication state

### 7. Troubleshooting Authentication

**Common Issues:**

1. **"redirect_uri_mismatch" error**:
   - Ensure the redirect URI in Google Cloud Console exactly matches `GOOGLE_REDIRECT_URI` in your `.env` file
   - Check for trailing slashes and protocol (http vs https)

2. **"Access denied" error**:
   - Verify the user's email is in the `ALLOWED_EMAILS` list
   - Check for typos in email addresses
   - Ensure no extra spaces in the comma-separated list

3. **"Invalid authentication credentials" error**:
   - Check if JWT token is properly stored in browser localStorage
   - Verify JWT_SECRET_KEY is the same between backend restarts
   - Check if token has expired (default: 24 hours)

4. **Frontend infinite loading**:
   - Check browser console for API errors
   - Verify backend server is running on correct port
   - Check CORS configuration

**Debug Steps:**
1. Check browser developer tools > Network tab for failed requests
2. Check backend logs for authentication errors
3. Verify environment variables are loaded correctly
4. Test authentication endpoints directly with curl

## Usage

### Running the API

Start the FastAPI server:
```bash
python api/main.py
```

The API will be available at `http://localhost:8000`

### Running the Frontend

Start the Next.js development server:
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Frontend Authentication

The frontend includes several authentication components:

**AuthContext (`src/contexts/AuthContext.tsx`)**:
- Manages global authentication state
- Handles token storage in localStorage
- Provides login/logout functions
- Validates tokens on app initialization

**ProtectedRoute (`src/components/ProtectedRoute.tsx`)**:
- Wraps pages that require authentication
- Redirects unauthenticated users to login
- Shows loading state during authentication check

**LoginButton (`src/components/LoginButton.tsx`)**:
- Google OAuth login button
- Handles the OAuth flow initiation
- Styled with shadcn/ui components

**UserProfile (`src/components/UserProfile.tsx`)**:
- Displays user information (name, email, picture)
- Provides logout functionality
- Shows in the sidebar when authenticated

### Operations Management

The operations page (`/operations`) provides a comprehensive interface for managing financial operations:

- **View Uncategorized Operations**: See all operations that need type assignment
- **Assign Types**: Select from existing operation types or create new ones
- **Create Custom Types**: Add new categories for better organization
- **Real-time Updates**: Changes are immediately reflected in the interface
- **Authentication Required**: All operations require valid authentication

To use the operations management:

1. **Login with Google** using the login button
2. Upload PDF files through the API or frontend
3. Navigate to the Operations page
4. Review operations that need categorization
5. Click "Assign Type" for any operation
6. Select an existing type or create a new one
7. Operations are automatically updated in the database

### API Endpoints

**Authentication Endpoints:**
- `GET /auth/google` - Get Google OAuth URL
- `GET /auth/google/callback` - Handle Google OAuth callback
- `GET /auth/me` - Get current user information (requires authentication)
- `POST /auth/logout` - Logout endpoint

**PDF Management (requires authentication):**
- `GET /pdfs` - List all processed PDFs
- `POST /upload-pdf` - Upload and process a PDF file
- `GET /pdfs/{pdf_id}` - Get details of a specific PDF
- `DELETE /pdfs/{pdf_id}` - Delete a PDF and its operations

**Operations Management (requires authentication):**
- `GET /operations` - List all operations with optional filtering
- `GET /operations/null-types` - Get operations that need type assignment
- `GET /operations/with-types` - Get operations with their associated types
- `GET /operations/by-month/{year}/{month}` - Get operations for a specific month
- `GET /operations/by-type/{type_id}` - Get operations of a specific type
- `POST /operations/manual` - Create a manual operation
- `POST /operations/{operation_id}/assign-type` - Assign a type to an operation
- `DELETE /operations/{operation_id}` - Delete an operation

**Operation Types (requires authentication):**
- `GET /operation-types` - List all operation types
- `POST /operation-types` - Create a new operation type
- `GET /operation-types/{type_id}` - Get a specific operation type
- `PUT /operation-types/{type_id}` - Update an operation type
- `DELETE /operation-types/{type_id}` - Delete an operation type

**Reports (requires authentication):**
- `GET /reports/available-months` - Get list of available months with data
- `GET /reports/monthly/{year}/{month}` - Get monthly report data
- `GET /reports/monthly/{year}/{month}/type/{type_id}` - Get operations by type for a month

**Statistics (requires authentication):**
- `GET /statistics` - Get overall statistics

**Rules Management (requires authentication):**
- `GET /api/rules/categories` - List rule categories
- `POST /api/rules/categories` - Create a new category
- `GET /api/rules/rules` - List all rules
- `POST /api/rules/rules` - Create a new rule
- `POST /api/rules/run-matcher` - Run the rules matcher

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

### Backend Dependencies
- `fastapi`: Web framework
- `sqlmodel`: SQL database ORM
- `pdfplumber`: PDF text extraction
- `pydantic`: Data validation
- `uvicorn`: ASGI server
- `python-jose[cryptography]`: JWT token handling
- `python-dotenv`: Environment variable loading
- `httpx`: HTTP client for Google API calls

### Frontend Dependencies
- `next`: React framework
- `react`: UI library
- `typescript`: Type safety
- `tailwindcss`: CSS framework
- `lucide-react`: Icon library
- `@radix-ui/*`: UI component primitives

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
