
from pyspark.sql import DataFrame, functions as F


def check_data_quality(df: DataFrame):
    """
    Sépare les stations valides et rejetées
    en fonction des règles de qualité.
    """

    checked = (
        df
        .withColumn(
            "quality_errors",
            F.filter(
                F.array(
                    F.when(
                        F.col("station_id").isNull()
                        | (F.trim(F.col("station_id")) == ""),
                        F.lit("MISSING_STATION_ID")
                    ),
                    
                    F.when(
                        F.col("bikes_available").isNull()
                        | F.col("docks_available").isNull()
                        | F.col("capacity").isNull()
                        | F.col("mechanical_bikes").isNull()
                        | F.col("electric_bikes").isNull(),
                        F.lit("MISSING_QUANTITY")
                    ),
                    F.when(
                        (F.col("bikes_available") < 0)
                        | (F.col("docks_available") < 0)
                        | (F.col("capacity") < 0)
                        | (F.col("mechanical_bikes") < 0)
                        | (F.col("electric_bikes") < 0),
                        F.lit("NEGATIVE_QUANTITY")
                    ),
                    F.when(
                        F.col("latitude").isNull()
                        | F.col("longitude").isNull()
                        | ~F.col("latitude").between(-90, 90)
                        | ~F.col("longitude").between(-180, 180),
                        F.lit("INVALID_COORDINATES")
                    ),
                    F.when(
                        F.col("source_updated_at").isNull(),
                        F.lit("INVALID_SOURCE_DATE")
                    )
                ),
                lambda error: error.isNotNull()
            )
        )
        .withColumn(
            "is_valid",
            F.size("quality_errors") == 0
        )
    )

    valid_df = checked.filter(F.col("is_valid"))
    rejected_df = checked.filter(~F.col("is_valid"))

    return valid_df, rejected_df
