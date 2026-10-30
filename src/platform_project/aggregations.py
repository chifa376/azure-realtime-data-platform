
from pyspark.sql import DataFrame, functions as F


def build_gold_global(df: DataFrame) -> DataFrame:
    """Calcule les indicateurs globaux d'un lot Vélib."""

    return df.groupBy("batch_id").agg(
        F.count("*").alias("total_stations"),

        F.sum("bikes_available").alias("total_bikes"),
        F.sum("mechanical_bikes").alias("mechanical_bikes"),
        F.sum("electric_bikes").alias("electric_bikes"),
        F.sum("docks_available").alias("available_docks"),

        F.sum(
            F.when(
                (F.col("is_operational") == True)
                & (F.col("is_stale") == False)
                & (F.col("bikes_available") == 0),
                1
            ).otherwise(0)
        ).alias("empty_stations"),

        F.sum(
            F.when(
                (F.col("is_operational") == True)
                & (F.col("is_stale") == False)
                & (F.col("docks_available") == 0),
                1
            ).otherwise(0)
        ).alias("full_stations"),

        F.sum(
            F.when(F.col("is_stale") == True, 1)
            .otherwise(0)
        ).alias("stale_stations"),

        F.sum(
            F.when(F.col("capacity_mismatch") == True, 1)
            .otherwise(0)
        ).alias("capacity_mismatches"),

        F.max("source_updated_at").alias(
            "latest_source_update"
        )
    )


def build_gold_communes(df: DataFrame) -> DataFrame:
    """Calcule les disponibilités par commune."""

    return df.groupBy(
        "batch_id", "commune", "commune_code"
    ).agg(
        F.count("*").alias("total_stations"),
        F.sum("bikes_available").alias("total_bikes"),
        F.sum("mechanical_bikes").alias("mechanical_bikes"),
        F.sum("electric_bikes").alias("electric_bikes"),
        F.sum("docks_available").alias("available_docks"),

        F.sum(
            F.when(F.col("is_stale") == True, 1)
            .otherwise(0)
        ).alias("stale_stations")
    )
