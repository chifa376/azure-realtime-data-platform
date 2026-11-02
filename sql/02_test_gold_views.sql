
-- ==================================================
-- 5CLOUD - TEST DES VUES GOLD
-- Base : velib_analytics
-- ==================================================

USE velib_analytics;
GO

-- 1. Vérifier les indicateurs globaux
SELECT
    total_stations,
    total_bikes,
    mechanical_bikes,
    electric_bikes,
    available_docks,
    empty_stations,
    full_stations
FROM dbo.vw_velib_gold_global;

-- 2. Vérifier le nombre de communes
SELECT COUNT(*) AS nombre_communes
FROM dbo.vw_velib_gold_communes;

-- 3. Afficher les 10 communes avec le plus de vélos
SELECT TOP 10
    commune,
    total_stations,
    total_bikes,
    mechanical_bikes,
    electric_bikes
FROM dbo.vw_velib_gold_communes
ORDER BY total_bikes DESC;
