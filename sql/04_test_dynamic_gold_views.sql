
USE velib_analytics;
GO

-- Dernier lot publié
SELECT *
FROM dbo.vw_velib_latest_published_batch;

-- Vérifier les volumes des deux vues
SELECT COUNT(*) AS global_rows
FROM dbo.vw_velib_gold_global_dynamic;

SELECT COUNT(*) AS communes_rows
FROM dbo.vw_velib_gold_communes_dynamic;

-- Vérifier que les deux vues utilisent le même lot
SELECT
    g.batch_id AS global_batch,
    c.batch_id AS communes_batch
FROM dbo.vw_velib_gold_global_dynamic AS g
CROSS JOIN (
    SELECT DISTINCT batch_id
    FROM dbo.vw_velib_gold_communes_dynamic
) AS c;
