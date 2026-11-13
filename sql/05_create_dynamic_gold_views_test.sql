
USE velib_analytics;
GO

-- 1. Dernier lot Gold publié dans l'environnement de test
CREATE OR ALTER VIEW dbo.vw_velib_latest_published_batch_test AS
SELECT TOP 1
    batch_id,
    published_at_utc
FROM OPENROWSET(
    BULK 'https://stvelibchifa2026.dfs.core.windows.net/velib-data/test/dynamic-gold/gold/velib/publications/batch_id=*/*.parquet',
    FORMAT = 'PARQUET'
) AS publication
WHERE status = 'success'
ORDER BY published_at_utc DESC, batch_id DESC;
GO

-- 2. Gold Global dynamique - test
CREATE OR ALTER VIEW dbo.vw_velib_gold_global_dynamic_test AS
SELECT
    g.batch_id,
    g.total_stations,
    g.total_bikes,
    g.mechanical_bikes,
    g.electric_bikes,
    g.available_docks,
    g.empty_stations,
    g.full_stations,
    g.stale_stations,
    g.capacity_mismatches,
    g.latest_source_update
FROM OPENROWSET(
    BULK 'https://stvelibchifa2026.dfs.core.windows.net/velib-data/test/dynamic-gold/gold/velib/global/batch_id=*/*.parquet',
    FORMAT = 'PARQUET'
) AS g
INNER JOIN dbo.vw_velib_latest_published_batch_test AS p
    ON g.batch_id = p.batch_id;
GO

-- 3. Gold Communes dynamique - test
CREATE OR ALTER VIEW dbo.vw_velib_gold_communes_dynamic_test AS
SELECT
    c.batch_id,
    c.commune,
    c.commune_code,
    c.total_stations,
    c.total_bikes,
    c.mechanical_bikes,
    c.electric_bikes,
    c.available_docks,
    c.stale_stations
FROM OPENROWSET(
    BULK 'https://stvelibchifa2026.dfs.core.windows.net/velib-data/test/dynamic-gold/gold/velib/communes/batch_id=*/*.parquet',
    FORMAT = 'PARQUET'
) AS c
INNER JOIN dbo.vw_velib_latest_published_batch_test AS p
    ON c.batch_id = p.batch_id;
GO
