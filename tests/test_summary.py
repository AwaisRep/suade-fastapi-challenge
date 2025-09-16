import pytest
from fastapi.testclient import TestClient
from app.main import app
import shutil
import os

def validate_summary_response(data: dict) -> None:
    """Helper function to validate summary response structure"""
    expected_fields = ["maximum", "minimum", "average"]
    for field in expected_fields:
        assert field in data, f"Missing field: {field}"
        assert isinstance(data[field], float), f"Field {field} should be float"

# As this test relies on empty data, we will perform this case first
def test_summary_empty_data(client):
    """Test summary for non-existing transaction data"""
    
    res = client.get("/summary/123")
    assert res.status_code == 400

def test_uploaded_data(client, get_test_file):
    """Upload test data once for the remaining tests to re-use"""

    with open(get_test_file("valid_sample.csv"), "rb") as f:
        res = client.post("/upload", files={"file": ("valid.csv", f, "text/csv")})

    assert res.status_code == 200

def test_summary_no_dates(client):
    """Test summary for existing user without date ranges"""

    res = client.get("/summary/305")
    assert res.status_code == 200

    validate_summary_response(res.json()["data"])


def test_summary_with_date_range(client):
    """Test summary for existing user with date ranges"""

    res = client.get("/summary/305?date_from=2025-01-01&date_to=2025-12-31")
    assert res.status_code == 200

    validate_summary_response(res.json()["data"])

def test_summary_with_start_date(client):
    """Test summary for existing user with only start ranges"""

    res = client.get("/summary/305?date_to=2025-06-01")
    assert res.status_code == 200

    validate_summary_response(res.json()["data"])

def test_summary_with_end_date(client):
    """Test summary for existing user with only end date"""

    res = client.get("/summary/305?date_from=2025-06-01")
    assert res.status_code == 200

    validate_summary_response(res.json()["data"])

def test_summary_invalid_date_range(client):
    """Test summary for where date_from is after date_to"""

    res = client.get("/summary/305?date_from=2025-01-01&date_to=2024-01-01")
    assert res.status_code == 400

def test_summary_invalid_date_format(client):
    """Test summary for an invalid date format being given"""

    res = client.get("/summary/305?date_from=2025-0s-01")
    assert res.status_code == 400

def test_summary_no_transactions(client):
    """Test summary for a user with no transactions in a given date"""

    res = client.get("/summary/305?date_from=2020-01-01&date_to=2021-0-1")
    assert res.status_code == 400
    
def test_summary_invalid_user_id(client):
    """Test summary for non-existing user"""

    res = client.get("/summary/30534324324342322344323542dsdssdf")
    assert res.status_code == 400