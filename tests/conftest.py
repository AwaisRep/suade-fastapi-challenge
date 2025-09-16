import pytest
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.sample_generation import generate_sample

@pytest.fixture(scope="session")
def sample_data():
    """Generate sample data once per test session"""
    print("Starting sample data generation... (this may take up to a minute!)")
    result = generate_sample()
    print("Sample data generation complete!")
    return result

@pytest.fixture
def client(sample_data) -> TestClient:
    """FastAPI test client that depends on sample_data being ready"""
    from app.main import app
    return TestClient(app)

@pytest.fixture
def get_test_file():
    def _get_test_file(filename: str):
        return os.path.join(os.path.dirname(__file__), "test-data", filename)
    return _get_test_file