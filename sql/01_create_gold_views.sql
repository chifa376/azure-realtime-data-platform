
-- ============================================================
-- 5CLOUD - VELIB DATA PLATFORM
-- Vues Gold pour Azure Synapse Serverless SQL et Power BI
-- Base : velib_analytics
-- Lot de test : 28 octobre 2026
-- ============================================================

USE velib_analytics;
GO

-- ============================================================
-- 1. VUE GOLD GLOBAL
-- ============================================================

CREATE OR ALTER VIEW dbo.vw_velib_gold_global AS
SELECT
    batch_id,
    total_stations,
    total_bikes,
    mechanical_bikes,
    electric_bikes,
    available_docks,
    empty_stations,
    full_stations,
    stale_stations,
    capacity_mismatches,
    latest_source_update
FROM OPENROWSET(
    BULK 'https://stvelibchifa2026.dfs.core.windows.net/velib-data/gold/velib/global/batch_id=0610bc1b-5d65-462b-8a84-335af2737c68/*.parquet',
    FORMAT = 'PARQUET'
) AS gold;
GO

-- ============================================================
-- 2. VUE GOLD COMMUNES
-- ============================================================

CREATE OR ALTER VIEW dbo.vw_velib_gold_communes AS
SELECT
    batch_id,
    commune,
    commune_code,
    total_stations,
    total_bikes,
    mechanical_bikes,
    electric_bikes,
    available_docks,
    stale_stations
FROM OPENROWSET(
    BULK 'https://stvelibchifa2026.dfs.core.windows.net/velib-data/gold/velib/communes/batch_id=0610bc1b-5d65-462b-8a84-335af2737c68/*.parquet',
    FORMAT = 'PARQUET'
) AS communes;
GO
