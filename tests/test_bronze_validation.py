
import json
import pytest
from unittest.mock import MagicMock
from src.platform_project.bronze_validation import validate_bronze_manifest




@pytest.fixture
def manifest():
    return {
        "batch_id": "batch_test_001",
        "collection_status": "copy_completed",
        "expected_page_count": 16,
        "expected_station_count": 1520,
    }


def test_bronze_complete(manifest):
    validate_bronze_manifest(manifest, "batch_test_001", 16, 1520)


def test_missing_page(manifest):
    with pytest.raises(ValueError, match="pages"):
        validate_bronze_manifest(manifest, "batch_test_001", 15, 1420)


def test_missing_stations(manifest):
    with pytest.raises(ValueError, match="stations"):
        validate_bronze_manifest(manifest, "batch_test_001", 16, 1500)


def test_wrong_batch_id(manifest):
    with pytest.raises(ValueError, match="Batch ID"):
        validate_bronze_manifest(manifest, "batch_test_002", 16, 1520)


def test_collection_not_completed(manifest):
    manifest["collection_status"] = "pending"
    with pytest.raises(ValueError, match="Collecte"):
        validate_bronze_manifest(manifest, "batch_test_001", 16, 1520)
