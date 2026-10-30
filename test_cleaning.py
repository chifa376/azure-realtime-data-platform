
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Configuration PySpark pour Windows
os.environ["SPARK_LOCAL_HOSTNAME"] = "localhost"
os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession, functions as F
from src.platform_project.cleaning import clean_velib_data
from src.platform_project.quality import check_data_quality
from src.platform_project.silver_history import prepare_silver_history
from src.platform_project.silver_storage import save_silver_local
from src.platform_project.aggregations import (
    build_gold_global,
    build_gold_communes
)
from src.platform_project.gold_storage import save_gold_local

BATCH_ID = "0610bc1b-5d65-462b-8a84-335af2737c68"

pages_path = (
    Path("data/bronze/velib")
    / f"batch_id={BATCH_ID}"
    / "pages"
)

spark = (
    SparkSession.builder
    .master("local[2]")
    .appName("5CLOUD-Velib-Silver")
    .config("spark.driver.host", "127.0.0.1")
    .config("spark.driver.bindAddress", "127.0.0.1")
    .config("spark.sql.session.timeZone", "UTC")
    .getOrCreate()
)

try:
    # Lecture locale des fichiers JSON avec Python
    # pour éviter le problème Hadoop NativeIO sur Windows

    page_files = sorted(pages_path.glob("page_*.json"))

    print("Pages JSON trouvées :", len(page_files))

    if len(page_files) != 16:
        raise ValueError(
            f"16 pages attendues, {len(page_files)} trouvées"
        )

    stations = []

    for file_path in page_files:
        with file_path.open("r", encoding="utf-8-sig") as file:
            page = json.load(file)

        stations.extend(page["results"])

    print("Stations chargées :", len(stations))

    manifest_path = pages_path.parent / "manifest.json"

    with manifest_path.open("r", encoding="utf-8-sig") as file:
        manifest = json.load(file)

    collection_time = datetime.fromisoformat(
        manifest["manifest_written_at_utc"].replace("Z", "+00:00")
    )

    # Convertir les stations en JSON pour PySpark
    json_records = [
        json.dumps(station, ensure_ascii=False)
        for station in stations
    ]

    # Création du DataFrame Spark
    stations_df = spark.read.json(
        spark.sparkContext.parallelize(json_records, 2)
    )

    print("DataFrame Spark créé avec succès")

    # Transformation Bronze vers Silver
    silver_df = clean_velib_data(
    stations_df,
    BATCH_ID,
    collection_time
)

    print("\n--- SILVER : APERÇU ---")

    silver_df.select(
        "station_id",
        "station_name",
        "bikes_available",
        "docks_available",
        "capacity_mismatch"
    ).show(10, truncate=False)

    print("Stations Silver :", silver_df.count())

    print(
        "Anomalies de capacité :",
        silver_df.filter(
            F.col("capacity_mismatch") == True
        ).count()
    )

    
    print("\n--- CONTRÔLES QUALITÉ SILVER ---")

    negative_values = silver_df.filter(
        (F.col("bikes_available") < 0)
        | (F.col("docks_available") < 0)
        | (F.col("capacity") < 0)
    ).count()

    invalid_coordinates = silver_df.filter(
        F.col("latitude").isNull()
        | F.col("longitude").isNull()
        | ~F.col("latitude").between(-90, 90)
        | ~F.col("longitude").between(-180, 180)
    ).count()

    missing_dates = silver_df.filter(
        F.col("source_updated_at").isNull()
    ).count()

    
    # Fraîcheur par rapport au manifeste
    reference_time = collection_time.astimezone(timezone.utc)

    stale_stations = silver_df.filter(
        F.col("is_stale") == True
    ).count()


    print("Valeurs négatives :", negative_values)
    print("Coordonnées invalides :", invalid_coordinates)
    print("Dates manquantes/invalides :", missing_dates)
    print("Stations anciennes au moment du manifeste (> 24 h) :", stale_stations)

    print("\n--- VALIDATION QUALITÉ SILVER ---")

    valid_df, rejected_df = check_data_quality(silver_df)

    print("Stations valides :", valid_df.count())
    print("Stations rejetées :", rejected_df.count())

    rejected_df.select(
        "station_id", "quality_errors"
    ).show(10, truncate=False)

    print("\n--- TEST DE REJET CONTRÔLÉ ---")

    # Créer une station invalide à partir d'une vraie station
    invalid_station = (
        silver_df.limit(1)
        .withColumn("station_id", F.lit("TEST_INVALID"))
        .withColumn("bikes_available", F.lit(-5))
    )

    test_valid, test_rejected = check_data_quality(
        invalid_station
    )

    print("Stations valides du test :", test_valid.count())
    print("Stations rejetées du test :", test_rejected.count())

    test_rejected.select(
        "station_id",
        "bikes_available",
        "quality_errors"
    ).show(truncate=False)

    assert test_valid.count() == 0
    assert test_rejected.count() == 1

    print("\n--- TEST HISTORISATION SILVER ---")

    history_df = prepare_silver_history(valid_df)

    print("Observations avant déduplication :", valid_df.count())
    print("Observations après déduplication :", history_df.count())

    # Injecter volontairement un doublon
    duplicated_df = valid_df.unionByName(valid_df.limit(1))

    deduplicated_df = prepare_silver_history(duplicated_df)

    print("Avec un doublon injecté :", duplicated_df.count())
    print("Après suppression du doublon :", deduplicated_df.count())

    assert deduplicated_df.count() == valid_df.count()

    print("TEST DE DÉDUPLICATION RÉUSSI")

    
    print("\n--- TEST HISTORISATION MULTI-LOTS ---")

    # Simulation d'un deuxième lot pour le test
    second_batch = (
        history_df
        .withColumn("batch_id", F.lit("TEST_BATCH_002"))
    )

    # Conserver les observations des deux lots
    combined_df = history_df.unionByName(second_batch)

    multi_batch_history = prepare_silver_history(combined_df)

    print("Nombre de lots :", multi_batch_history.select(
        "batch_id"
    ).distinct().count())

    print("Observations historisées :", multi_batch_history.count())

    print("Observations par lot :")
    multi_batch_history.groupBy("batch_id").count().show(
        truncate=False
    )

    assert multi_batch_history.count() == 3040
    assert multi_batch_history.select(
        "batch_id"
    ).distinct().count() == 2

    print("TEST MULTI-LOTS RÉUSSI")

    
    print("\n--- ÉCRITURE SILVER PERSISTANTE ---")

    # Utiliser uniquement le lot réel validé
    silver_history = prepare_silver_history(valid_df)

    # Première écriture
    output_file = save_silver_local(
        silver_history,
        BATCH_ID
    )

    with output_file.open("r", encoding="utf-8") as file:
        first_count = sum(1 for line in file)

    print("Après première écriture :", first_count)

    # Simuler une reprise du même traitement
    save_silver_local(
        silver_history,
        BATCH_ID
    )

    with output_file.open("r", encoding="utf-8") as file:
        second_count = sum(1 for line in file)

    print("Après deuxième écriture :", second_count)

    assert first_count == 1520
    assert second_count == first_count

    print("TEST DE REPRISE SILVER RÉUSSI")


    print("\n--- GOLD : KPI GLOBAUX ---")

    # Utiliser uniquement les données réelles validées
    gold_input = prepare_silver_history(valid_df)

    gold_global = build_gold_global(gold_input)

    gold_global.show(truncate=False)

    print("\n--- GOLD : KPI PAR COMMUNE ---")

    gold_communes = build_gold_communes(gold_input)

    gold_communes.orderBy(
        F.desc("total_bikes")
    ).show(10, truncate=False)

    # Vérification de cohérence
    global_values = gold_global.first()

    assert global_values["total_stations"] == 1520
    assert global_values["stale_stations"] == 17
    assert global_values["capacity_mismatches"] == 848

    # Les agrégations par commune doivent
    # retrouver le même nombre de stations.
    communes_total = gold_communes.agg(
        F.sum("total_stations")
    ).first()[0]

    assert communes_total == 1520

    print("\nTEST KPI GOLD RÉUSSI")


    print("\n--- ÉCRITURE GOLD PERSISTANTE ---")

    global_file = save_gold_local(
        gold_global,
        BATCH_ID,
        "global"
    )

    communes_file = save_gold_local(
        gold_communes,
        BATCH_ID,
        "communes"
    )

    def count_saved_rows(path):
        with path.open("r", encoding="utf-8") as file:
            return sum(1 for line in file)

    first_global = count_saved_rows(global_file)
    first_communes = count_saved_rows(communes_file)

    print("KPI globaux enregistrés :", first_global)
    print("Communes enregistrées :", first_communes)

    # Réexécution volontaire du même lot
    save_gold_local(gold_global, BATCH_ID, "global")
    save_gold_local(gold_communes, BATCH_ID, "communes")

    second_global = count_saved_rows(global_file)
    second_communes = count_saved_rows(communes_file)

    print("KPI globaux après reprise :", second_global)
    print("Communes après reprise :", second_communes)

    assert first_global == second_global == 1
    assert first_communes == second_communes
    assert first_communes > 0

    print("TEST DE REPRISE GOLD RÉUSSI")

finally:
    spark.stop()
