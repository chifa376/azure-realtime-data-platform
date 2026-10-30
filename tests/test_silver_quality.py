
import os
import sys

# Configuration PySpark sous Windows
os.environ["SPARK_LOCAL_HOSTNAME"] = "localhost"
os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession, functions as F
from src.platform_project.quality import check_data_quality


def test_negative_quantity_rule():
    """Vérifie la détection d'une quantité négative."""

    spark = (
        SparkSession.builder
        .master("local[1]")
        .appName("SilverQualityTest")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .getOrCreate()
    )

    try:
        df = spark.createDataFrame(
            [(
                "TEST_001", -5, 10, 20, 0, 0,
                48.8566, 2.3522
            )],
            [
                "station_id",
                "bikes_available",
                "docks_available",
                "capacity",
                "mechanical_bikes",
                "electric_bikes",
                "latitude",
                "longitude"
            ]
        )

        df = df.withColumn(
            "source_updated_at",
            F.current_timestamp()
        )

        valid_df, rejected_df = check_data_quality(df)

        assert valid_df.count() == 0
        assert rejected_df.count() == 1

        errors = rejected_df.first()["quality_errors"]

        assert "NEGATIVE_QUANTITY" in errors

    finally:
        spark.stop()

def test_missing_station_id_rule():
    """Vérifie le rejet d'une station sans identifiant."""

    spark = (
        SparkSession.builder
        .master("local[1]")
        .appName("SilverQualityTest")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .getOrCreate()
    )

    try:
        # Utiliser une chaîne vide plutôt que None
        # pour conserver une inférence de schéma simple.
        df = spark.createDataFrame(
            [("", 5, 10, 20, 3, 2, 48.8566, 2.3522)],
            [
                "station_id",
                "bikes_available",
                "docks_available",
                "capacity",
                "mechanical_bikes",
                "electric_bikes",
                "latitude",
                "longitude"
            ]
        ).withColumn(
            "source_updated_at",
            F.current_timestamp()
        )

        valid_df, rejected_df = check_data_quality(df)

        assert valid_df.count() == 0
        assert rejected_df.count() == 1
        assert (
            "MISSING_STATION_ID"
            in rejected_df.first()["quality_errors"]
        )

    finally:
        spark.stop()

def test_invalid_coordinates_rule():
    """Vérifie le rejet d'une latitude invalide."""

    spark = (
        SparkSession.builder
        .master("local[1]")
        .appName("SilverQualityTest")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .getOrCreate()
    )

    try:
        df = spark.createDataFrame(
            [(
                "TEST_003", 5, 10, 20, 3, 2,
                120.0, 2.3522
            )],
            [
                "station_id",
                "bikes_available",
                "docks_available",
                "capacity",
                "mechanical_bikes",
                "electric_bikes",
                "latitude",
                "longitude"
            ]
        ).withColumn(
            "source_updated_at",
            F.current_timestamp()
        )

        valid_df, rejected_df = check_data_quality(df)

        assert valid_df.count() == 0
        assert rejected_df.count() == 1

        errors = rejected_df.first()["quality_errors"]

        assert "INVALID_COORDINATES" in errors

    finally:
        spark.stop()

def test_missing_source_date_rule():
    """Vérifie le rejet d'une date source manquante."""

    spark = (
        SparkSession.builder
        .master("local[1]")
        .appName("SilverQualityTest")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .getOrCreate()
    )

    try:
        df = spark.createDataFrame(
            [(
                "TEST_004", 5, 10, 20, 3, 2,
                48.8566, 2.3522
            )],
            [
                "station_id",
                "bikes_available",
                "docks_available",
                "capacity",
                "mechanical_bikes",
                "electric_bikes",
                "latitude",
                "longitude"
            ]
        ).withColumn(
            "source_updated_at",
            F.lit(None).cast("timestamp")
        )

        valid_df, rejected_df = check_data_quality(df)

        assert valid_df.count() == 0
        assert rejected_df.count() == 1

        errors = rejected_df.first()["quality_errors"]

        assert "INVALID_SOURCE_DATE" in errors

    finally:
        spark.stop()

def test_missing_quantity_rule():
    """Vérifie le rejet d'une station sans quantité de vélos."""

    spark = (
        SparkSession.builder
        .master("local[1]")
        .appName("SilverQualityTest")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .getOrCreate()
    )

    try:
        df = spark.createDataFrame(
            [(
                "TEST_005", 5, 10, 20, 3, 2,
                48.8566, 2.3522
            )],
            [
                "station_id",
                "bikes_available",
                "docks_available",
                "capacity",
                "mechanical_bikes",
                "electric_bikes",
                "latitude",
                "longitude"
            ]
        )

        # Simuler une quantité manquante
        df = (
            df
            .withColumn(
                "bikes_available",
                F.lit(None).cast("integer")
            )
            .withColumn(
                "source_updated_at",
                F.current_timestamp()
            )
        )

        valid_df, rejected_df = check_data_quality(df)

        assert valid_df.count() == 0
        assert rejected_df.count() == 1

        errors = rejected_df.first()["quality_errors"]

        assert "MISSING_QUANTITY" in errors

    finally:
        spark.stop()
