
from pathlib import Path


def test_gold_files_exist():
    """Vérifie que les résultats Gold ont été enregistrés."""

    batch_id = "0610bc1b-5d65-462b-8a84-335af2737c68"

    gold_root = Path("data/gold/velib")

    global_file = (
        gold_root / "global"
        / f"batch_id={batch_id}"
        / "data.jsonl"
    )

    communes_file = (
        gold_root / "communes"
        / f"batch_id={batch_id}"
        / "data.jsonl"
    )

    assert global_file.exists()
    assert communes_file.exists()


def test_gold_saved_counts():
    """Vérifie le nombre de lignes persistées."""

    batch_id = "0610bc1b-5d65-462b-8a84-335af2737c68"

    gold_root = Path("data/gold/velib")

    global_file = (
        gold_root / "global"
        / f"batch_id={batch_id}"
        / "data.jsonl"
    )

    communes_file = (
        gold_root / "communes"
        / f"batch_id={batch_id}"
        / "data.jsonl"
    )

    with global_file.open(encoding="utf-8") as file:
        global_count = sum(1 for line in file)

    with communes_file.open(encoding="utf-8") as file:
        communes_count = sum(1 for line in file)

    assert global_count == 1
    assert communes_count == 69
