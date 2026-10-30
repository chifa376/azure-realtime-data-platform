
from pyspark.sql import DataFrame, functions as F


def clean_velib_data(
    df: DataFrame,
    batch_id: str,
    reference_time
) -> DataFrame:
    """
    Transforme les données Bronze Vélib en données Silver.

    - Renomme et normalise les colonnes.
    - Convertit les dates en UTC.
    - Préserve les valeurs manquantes.
    - Signale les anomalies métier.
    - Ajoute les métadonnées du traitement.
    """

    silver_df = (
        df
        .select(
            F.col("stationcode").cast("string").alias("station_id"),
            F.trim(F.col("name")).alias("station_name"),
            F.col("capacity").cast("integer").alias("capacity"),
            F.col("numbikesavailable").cast("integer")
                .alias("bikes_available"),
            F.col("numdocksavailable").cast("integer")
                .alias("docks_available"),
            F.col("mechanical").cast("integer")
                .alias("mechanical_bikes"),
            F.col("ebike").cast("integer")
                .alias("electric_bikes"),
            F.col("nom_arrondissement_communes").alias("commune"),
            F.col("code_insee_commune").cast("string")
                .alias("commune_code"),
            F.col("coordonnees_geo.lat").cast("double")
                .alias("latitude"),
            F.col("coordonnees_geo.lon").cast("double")
                .alias("longitude"),
            F.col("duedate").alias("source_updated_raw"),
            F.upper(F.trim(F.col("is_installed")))
                .alias("is_installed_raw"),
            F.upper(F.trim(F.col("is_renting")))
                .alias("is_renting_raw"),
            F.upper(F.trim(F.col("is_returning")))
                .alias("is_returning_raw"),
        )
        .withColumn(
            "source_updated_at",
            F.to_timestamp("source_updated_raw")
        )
        .withColumn(
            "is_operational",
            (F.col("is_installed_raw") == "OUI")
            & (F.col("is_renting_raw") == "OUI")
            & (F.col("is_returning_raw") == "OUI")
        )
        .withColumn(
            "capacity_mismatch",
            F.when(
                F.col("capacity").isNotNull()
                & F.col("bikes_available").isNotNull()
                & F.col("docks_available").isNotNull(),
                F.col("capacity") != (
                    F.col("bikes_available")
                    + F.col("docks_available")
                )
            )
        )
        .withColumn("batch_id", F.lit(batch_id))
        .withColumn("processed_at", F.current_timestamp())
        .withColumn(
    "is_stale",
    F.when(
        F.col("source_updated_at").isNull(),
        F.lit(None).cast("boolean")
    ).otherwise(
        F.col("source_updated_at")
        < (
            F.lit(reference_time).cast("timestamp")
            - F.expr("INTERVAL 24 HOURS")
        )
    )
)
    )

    return silver_df
