import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_upload_valid_file(client, get_test_file):
    """
    Test valid CSV upload
    """
    with open(get_test_file("valid_sample.csv"), "rb") as f:
        res = client.post("/upload", files={"file": ("valid.csv", f, "text/csv")})
    assert res.status_code == 200

def test_upload_invalid_file(client, get_test_file):
    """
    Test invalid CSV upload
    """
    with open(get_test_file("invalid_sample.csv"), "rb") as f:
        res = client.post("/upload", files={"file": ("invalid.csv", f, "text/csv")})
    assert res.status_code == 400

def test_upload_large_file(client, get_test_file):
    """
    Test large CSV upload
    """
    with open(get_test_file("large_sample.csv"), "rb") as f:
        res = client.post("/upload", files={"file": ("large.csv", f, "text/csv")})
    assert res.status_code == 400