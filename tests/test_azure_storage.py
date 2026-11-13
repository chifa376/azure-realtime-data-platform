
import pytest
from unittest.mock import MagicMock

from src.platform_project.azure_storage import write_parquet_to_adls


def test_refuse_invalid_path():
    df = MagicMock()

    with pytest.raises(ValueError, match="Azure ADLS Gen2"):
        write_parquet_to_adls(df, "invalid/path")

    df.write.save.assert_not_called()


def test_refuse_empty_dataframe():
    df = MagicMock()
    df.limit.return_value.count.return_value = 0

    with pytest.raises(ValueError, match="DataFrame vide"):
        write_parquet_to_adls(
            df,
            "abfss://container@storage.dfs.core.windows.net/test"
        )

    df.write.save.assert_not_called()



def test_write_uses_errorifexists():
    df = MagicMock()
    df.limit.return_value.count.return_value = 1

    output_path = "abfss://container@storage.dfs.core.windows.net/test"

    write_parquet_to_adls(df, output_path)

    writer = df.write.mode.return_value
    parquet_writer = writer.format.return_value

    df.write.mode.assert_called_once_with("errorifexists")
    writer.format.assert_called_once_with("parquet")
    parquet_writer.save.assert_called_once_with(output_path)

