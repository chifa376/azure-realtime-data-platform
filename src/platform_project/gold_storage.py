
import os
from pathlib import Path
from uuid import uuid4

from pyspark.sql import DataFrame, functions as F


def save_gold_local(
    df: DataFrame,
    batch_id: str,
    dataset_name: str,
    output_root: str = "data/gold/velib"
) -> Path:
    """
    Enregistre un dataset Gold en JSON Lines.
    Le même lot est remplacé à chaque réexécution.
    """

    if not dataset_name or not dataset_name.replace("_", "").isalnum():
        raise ValueError("Nom de dataset invalide")

    invalid_batches = df.filter(
        F.col("batch_id").isNull()
        | (F.col("batch_id") != batch_id)
    ).count()

    if invalid_batches:
        raise ValueError("batch_id incohérent")

    if df.limit(1).count() == 0:
        raise ValueError("Dataset Gold vide")

    batch_dir = (
        Path(output_root)
        / dataset_name
        / f"batch_id={batch_id}"
    )
    batch_dir.mkdir(parents=True, exist_ok=True)

    output_file = batch_dir / "data.jsonl"
    temp_file = batch_dir / f".tmp-{uuid4().hex}.jsonl"

    try:
        with temp_file.open("w", encoding="utf-8") as file:
            for record in df.toJSON().toLocalIterator():
                file.write(record + "\n")

        os.replace(temp_file, output_file)

    finally:
        if temp_file.exists():
            temp_file.unlink()

    print(f"Gold sauvegardé : {output_file}")

    return output_file
