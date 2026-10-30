
import json
import os
import sys
from pathlib import Path

from pyspark.sql import SparkSession, functions as F

# Configuration Spark locale pour Windows
os.environ["SPARK_LOCAL_HOSTNAME"] = "localhost"
os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

BATCH_ID = "0610bc1b-5d65-462b-8a84-335af2737c68"

BASE_PATH = (
    Path("data/bronze/velib") / f"batch_id={BATCH_ID}"
)

# Lire le manifeste
with open(BASE_PATH / "manifest.json", encoding="utf-8") as f:
    manifest = json.load(f)

assert manifest["batch_id"] == BATCH_ID
assert manifest["collection_status"] == "copy_completed"

expected_pages = manifest["expected_page_count"]
expected_stations = manifest["expected_station_count"]

pages = sorted((BASE_PATH / "pages").glob("page_*.json"))

print("Pages attendues :", expected_pages)
print("Pages trouvées :", len(pages))

assert len(pages) == expected_pages, "Nombre de pages incorrect"

# Démarrer Spark
spark = (
    SparkSession.builder
    .master("local[2]")
    .appName("5CLOUD-Velib-Bronze-Validation")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .getOrCreate()
)

try:
    # Chaque page contient un objet JSON
    # avec total_count et results
    pages_df = (
        spark.read
        .option("multiLine", True)
        .json([str(p.resolve()) for p in pages])
    )

    stations_df = (
        pages_df
        .select(F.explode("results").alias("station"))
        .select("station.*")
    )

    total = stations_df.count()

    missing_ids = stations_df.filter(
        F.col("stationcode").isNull() |
        (F.trim(F.col("stationcode")) == "")
    ).count()

    duplicates = (
        stations_df
        .groupBy("stationcode")
        .count()
        .filter(F.col("count") > 1)
        .count()
    )

    print("\n--- RAPPORT BRONZE ---")
    print("Stations attendues :", expected_stations)
    print("Stations trouvées :", total)
    print("Codes station manquants :", missing_ids)
    print("Codes station dupliqués :", duplicates)

    assert total == expected_stations
    assert missing_ids == 0
    assert duplicates == 0

    print("\nVALIDATION BRONZE RÉUSSIE")

finally:
    spark.stop()
