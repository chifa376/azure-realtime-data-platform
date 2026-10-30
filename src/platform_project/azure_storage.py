
from pyspark.sql import DataFrame, SparkSession


def write_parquet_to_adls(
    df: DataFrame,
    output_path: str
) -> None:
    """
    Écrit un DataFrame Spark en Parquet dans ADLS Gen2.

    Le dossier du lot est remplacé en cas de
    réexécution du même traitement.
    """

    if not output_path.startswith("abfss://"):
        raise ValueError(
            "Le chemin doit être un chemin Azure ADLS Gen2"
        )

    if df.limit(1).count() == 0:
        raise ValueError("Impossible d'écrire un DataFrame vide")

    (
        df.write
        .mode("overwrite")
        .format("parquet")
        .save(output_path)
    )

    print("Écriture Parquet terminée :", output_path)


def read_parquet_from_adls(
    spark: SparkSession,
    input_path: str
) -> DataFrame:
    """Relit un dossier Parquet depuis ADLS Gen2."""

    if not input_path.startswith("abfss://"):
        raise ValueError(
            "Le chemin doit être un chemin Azure ADLS Gen2"
        )

    return spark.read.parquet(input_path)
