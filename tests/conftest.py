"""
Pytest configuration and common fixtures for the finreview project
"""
import pytest
import sys
from pathlib import Path

# Add project root to Python path for all tests
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Return the test data directory"""
    return project_root / "tests" / "test_data"


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment - runs before each test"""
    # Any global test setup can go here
    pass


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their names"""
    for item in items:
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_sql_utils" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_pdf_processor" in item.nodeid:
            item.add_marker(pytest.mark.unit)


