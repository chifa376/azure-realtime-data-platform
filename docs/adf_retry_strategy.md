# 5CLOUD — Stratégie de reprise ADF

## Objectif

Garantir qu'un lot Vélib n'est publié dans Gold que lorsque les données Silver, Gold Global et Gold Communes ont été enregistrées et validées.

## Scénarios de reprise

| Situation | Comportement attendu |
|---|---|
| Nouveau `batch_id` | Exécuter Silver, Gold Global et Gold Communes, puis publier le lot |
| Lot déjà publié avec succès | Ne pas écraser les données existantes |
| Échec pendant l'écriture Silver | Ne pas publier le lot ; examiner les fichiers éventuellement incomplets |
| Échec après Silver et Gold Global | Ne pas publier le lot ; prévoir une reprise contrôlée |
| Échec pendant la publication | Vérifier le registre avant toute nouvelle tentative |
| Réexécution du même `batch_id` | Ne pas écraser les fichiers ; appliquer la procédure de reprise validée |

## Règle de publication

Un lot est considéré comme publié uniquement lorsqu'un enregistrement `status = success` existe dans :

`gold/velib/publications/batch_id=<batch_id>/`

Cet enregistrement doit être créé après validation des trois jeux de données.

## Points à valider avec l'équipe

- Définir comment reprendre un lot partiellement écrit sans supprimer de données valides.
- Vérifier le comportement des tentatives automatiques d'ADF.
- Tester la publication et les vues SQL dynamiques sur un nouveau lot.
- Mettre à jour le package Python installé dans le pool Synapse avant le déploiement.


## Configuration ADF vérifiée

Pipeline : `pl_ingest_velib`

Activité : `run_silver_gold`

- Notebook : `velib_synapse`
- Pool Spark : `sparkvelib`
- Paramètre batch_id : `@pipeline().RunId`
- Retry automatique : 0
- Dépendance : `write_collection_manifest` doit réussir

## Procédure de reprise retenue pour la première version

Si une exécution échoue après une écriture partielle :

1. Ne pas publier le lot dans le registre Gold.
2. Ne pas écraser automatiquement les fichiers existants.
3. Identifier les dossiers Silver, Gold Global et Gold Communes déjà créés.
4. Vérifier leur intégrité et leur cohérence.
5. Décider d'une reprise contrôlée ou d'une nouvelle collecte avec un nouveau batch_id.

La relance automatique d'un lot partiel n'est pas activée.
La procédure devra être validée avec Chifa avant le déploiement Azure.
