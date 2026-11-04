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