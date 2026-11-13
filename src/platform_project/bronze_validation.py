
def validate_bronze_manifest(
    manifest,
    batch_id,
    actual_pages,
    actual_stations
):
    if manifest.get("batch_id") != batch_id:
        raise ValueError("Batch ID incorrect")

    if manifest.get("collection_status") != "copy_completed":
        raise ValueError("Collecte non terminée")

    expected_pages = int(manifest["expected_page_count"])
    expected_stations = int(manifest["expected_station_count"])

    if expected_pages <= 0 or expected_stations <= 0:
        raise ValueError("Volumes attendus invalides")

    if actual_pages != expected_pages:
        raise ValueError(
            f"Nombre de pages incorrect : "
            f"{actual_pages}/{expected_pages}"
        )

    if actual_stations != expected_stations:
        raise ValueError(
            f"Nombre de stations incorrect : "
            f"{actual_stations}/{expected_stations}"
        )

    return True
