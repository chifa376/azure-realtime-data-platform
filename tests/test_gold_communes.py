
import pytest
from pyspark.sql import SparkSession

from src.platform_project.aggregations import build_gold_communes

@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder
        .master("local[1]")
        .appName("test_gold_communes")
        .getOrCreate()
    )
    yield session
    session.stop()


def test_empty_and_full_stations_by_commune(spark):
    columns = [
        "batch_id", "commune", "commune_code",
        "bikes_available", "mechanical_bikes",
        "electric_bikes", "docks_available",
        "is_operational", "is_stale",
    ]

    rows = [
        ("batch_test", "Paris", "75056", 0, 0, 0, 5, True, False),
        ("batch_test", "Paris", "75056", 4, 3, 1, 0, True, False),
        ("batch_test", "Paris", "75056", 0, 0, 0, 0, False, False),
        ("batch_test", "Paris", "75056", 0, 0, 0, 0, True, True),
    ]

    df = spark.createDataFrame(rows, columns)
    result = build_gold_communes(df).collect()[0]

    assert result["total_stations"] == 4
    assert result["empty_stations"] == 1
    assert result["full_stations"] == 1
