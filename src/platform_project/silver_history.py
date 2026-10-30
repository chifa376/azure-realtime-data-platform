
from pyspark.sql import DataFrame, functions as F
from pyspark.sql.window import Window


def deduplicate_observations(df: DataFrame) -> DataFrame:
    """
    Supprime les doublons d'observations d'un même lot.

    Une observation est identifiée par :
    batch_id + station_id.

    Les différents lots restent distincts.
    """

    window = (
        Window
        .partitionBy("batch_id", "station_id")
        .orderBy(
            F.col("source_updated_at").desc_nulls_last(),
            F.col("station_name").asc_nulls_last()
        )
    )

    return (
        df
        .withColumn("_row_number", F.row_number().over(window))
        .filter(F.col("_row_number") == 1)
        .drop("_row_number")
    )


def prepare_silver_history(df: DataFrame) -> DataFrame:
    """
    Prépare les observations Silver historisées.

    Conserve l'identifiant de lot afin de permettre
    la comparaison entre collectes.
    """
    return deduplicate_observations(df)
