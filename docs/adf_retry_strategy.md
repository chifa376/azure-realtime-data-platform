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


## Points restant à valider avec l'équipe

- Vérifier que le notebook ne réécrit pas un lot déjà publié.
- Faire valider la Pull Request par Chifa.
- Déployer les versions définitives du notebook et du package Python.
- Créer et tester les vues SQL dynamiques définitives.
- Connecter Power BI aux nouvelles vues avec Nidhal.
- Vérifier l'actualisation après une nouvelle collecte ADF.



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
5. Lancer une nouvelle collecte avec un nouveau batch_id, après avoir vérifié que le lot partiel n'a pas été publié. La reprise du même lot n'est pas prise en charge.

La relance automatique d'un lot partiel n'est pas activée.
La procédure devra être validée avec Chifa avant le déploiement Azure.


## Résultats des tests Azure

Tests réalisés avec Chifa dans l'environnement isolé
`test/dynamic-gold/`.

### Lot Bronze incomplet
- Un écart entre le nombre de stations attendu et collecté a été détecté.
- Le notebook s'est arrêté avant les écritures Silver/Gold.
- Le lot n'a pas été publié.

### Échec partiel Silver/Gold
- Un échec volontaire a été provoqué après l'écriture Silver.
- Les fichiers Silver ont été conservés.
- Aucun fichier Gold ni enregistrement de publication n'a été créé.
- Une nouvelle collecte avec un nouveau `batch_id` a réussi.

### Stratégie retenue
- Conserver `errorifexists` et `retry: 0`.
- Ne jamais écraser automatiquement un lot partiel.
- En cas d'échec, relancer une nouvelle collecte avec un nouveau `batch_id`.
- La reprise automatique du même lot n'est pas prise en charge.

### Validation des vues SQL dynamiques
- Dernier lot publié :
  `62c90c99-042d-4832-9038-696b910e429a`
- Gold Global : 1 ligne.
- Gold Communes : 69 lignes.
- Stations : 1 522.
- Vélos disponibles : 19 947.
- Même `batch_id` dans les trois vues.
- Lot échoué `6dd373cb...` : absent du registre.

Les tests SQL ont été réalisés avec les vues `_test`.
Les vues de production et le rapport Power BI existant
n'ont pas encore été remplacés.
