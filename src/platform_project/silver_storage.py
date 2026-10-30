
import os
from pathlib import Path
from uuid import uuid4

from pyspark.sql import DataFrame, functions as F


def save_silver_local(
    df: DataFrame,
    batch_id: str,
    output_root: str = "data/silver/velib"
) -> Path:
    """
    Enregistre un lot Silver en JSON Lines.

    Si le même batch_id est retraité, son fichier
    est remplacé plutôt que dupliqué.

    Cette implémentation est réservée aux tests locaux.
    """

    # Vérifier que les données concernent le bon lot
    invalid_batches = df.filter(
        F.col("batch_id").isNull()
        | (F.col("batch_id") != batch_id)
    ).count()

    if invalid_batches:
        raise ValueError("batch_id incohérent")

    total = df.count()

    if total == 0:
        raise ValueError("Lot Silver vide")

    # Vérifier l'unicité des stations du lot
    unique_count = df.select("station_id").distinct().count()

    if unique_count != total:
        raise ValueError("Doublons Silver détectés")

    # Dossier dédié au lot
    batch_dir = Path(output_root) / f"batch_id={batch_id}"
    batch_dir.mkdir(parents=True, exist_ok=True)

    output_file = batch_dir / "stations.jsonl"
    temp_file = batch_dir / f".tmp-{uuid4().hex}.jsonl"

    # Écriture dans un fichier temporaire
    try:
        with temp_file.open("w", encoding="utf-8") as file:
            for record in df.toJSON().toLocalIterator():
                file.write(record + "\n")

        # Remplacement après écriture réussie
        os.replace(temp_file, output_file)

    finally:
        if temp_file.exists():
            temp_file.unlink()

    print(f"Silver sauvegardé : {output_file}")
    print(f"Observations enregistrées : {total}")

    return output_file
