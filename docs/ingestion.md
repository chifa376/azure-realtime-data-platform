# Ingestion des données Vélib

## Responsable

Chifa : collecte des données, configuration Azure Data Factory,
historisation Bronze, suivi des exécutions et documentation.

## Architecture

API Paris Data → Azure Data Factory → ADLS Gen2 Bronze.

La collecte fonctionne par lots planifiés toutes les 10 minutes.
Il s’agit d’une ingestion périodique, pas d’un flux continu.
La fraîcheur dépend également des mises à jour de la source.

## Ressources Azure

| Ressource | Nom |
|---|---|
| Groupe de ressources | rg-velib-data-platform |
| Data Factory | adf-velib-chifa-2026 |
| Stockage ADLS Gen2 | stvelibchifa2026 |
| Conteneur | velib-data |
| Pipeline principal | pl_ingest_velib |
| Déclencheur | tr_velib_every_10_minutes |

Les définitions ADF sont versionnées dans ingestion/adf.

## Source

Dataset : velib-disponibilite-en-temps-reel.

Endpoint :
https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records

Authentification : anonyme.

Paramètres utilisés :
- limit=100
- order_by=stationcode
- offset calculé pour chaque page

Chaque réponse contient total_count et un tableau results.

## Fonctionnement du pipeline

1. get_station_count récupère le nombre de stations annoncé.
2. check_station_count vérifie que ce nombre est compris
   entre 1 et 9 900 ; sinon, le pipeline échoue explicitement.
3. for_each_page parcourt les pages séquentiellement.
4. copy_velib_page_to_bronze copie chaque réponse JSON.
5. write_collection_manifest écrit le manifeste uniquement
   après la réussite de la boucle.

La pagination est pilotée par la boucle et le paramètre offset.
MaxRequestNumber est fixé à 1 dans chaque activité de copie.

Des nouvelles tentatives sont configurées pour les activités
de collecte. La concurrence du pipeline est limitée à 1.

## Organisation des données

Chaque exécution possède son propre dossier :

bronze/velib/batch_id=<RunId>/manifest.json
bronze/velib/batch_id=<RunId>/pages/page_0000.json
bronze/velib/batch_id=<RunId>/pages/page_0001.json
...

Les fichiers Bronze conservent les réponses brutes.
Une nouvelle exécution écrit dans un nouveau dossier.

## Manifeste

Le manifeste contient notamment :
- batch_id ;
- pipeline_name ;
- pages_path ;
- expected_station_count ;
- expected_page_count ;
- page_size ;
- collection_status ;
- validation_status ;
- manifest_written_at_utc.

collection_status=copy_completed indique la réussite des copies.
Cela ne garantit pas la complétude du contenu.

validation_status=pending reste la valeur écrite actuellement :
le contrôle automatique du contenu reste à implémenter.

## Sécurité

Le service lié ADLS utilise l’identité managée système
de Data Factory.

Cette identité dispose du rôle Contributeur aux données Blob
du stockage sur le conteneur velib-data.

Aucune clé de stockage ni aucun jeton ne doit être ajouté au dépôt.

## Vérifications réalisées le 28 octobre 2026

Contrôle du ZIP de données transmis :
- 16 fichiers JSON lisibles ;
- 15 pages de 100 stations et une page de 20 ;
- 1 520 stations, conformément au total annoncé ;
- 1 520 codes station distincts ;
- aucun code station manquant ;
- structure des champs identique sur toutes les pages ;
- compteurs vérifiés entiers positifs ou nuls ;
- mechanical + ebike = numbikesavailable partout ;
- coordonnées dans les plages géographiques valides ;
- dates interprétables.

Le contrôle a été effectué hors du pipeline.
Il ne valide pas automatiquement les collectes suivantes.

Exécutions planifiées observées :
- 22:10:01 → 22:15:12 : réussite ;
- 22:20:01 → 22:25:14 : réussite ;
- troisième démarrage à 22:30:01.

Ces horaires sont ceux affichés dans le portail, heure de Paris.

## Points qualité pour Cyrine

Dans le ZIP contrôlé :
- 844 stations présentent un écart entre capacity et
  numbikesavailable + numdocksavailable ;
- certaines dates duedate sont anciennes, jusqu’en 2017 ;
- la date source la plus récente est
  2026-10-28T19:25:18Z.

Conserver les valeurs brutes et ajouter des indicateurs qualité.
Ne pas corriger arbitrairement les compteurs.

Une collecte paginée ne constitue pas un instantané atomique :
la source peut évoluer entre deux requêtes.

## Reprise par Cyrine

- Lire uniquement les lots disposant d’un manifeste de copie réussie.
- Lire le tableau results de chaque fichier JSON.
- Vérifier le nombre de pages, de lignes et les codes station uniques.
- Écrire un résultat de validation distinct.
- Conserver stationcode comme chaîne de caractères.
- Ajouter batch_id et distinguer date de collecte et date source.
- Produire les couches Silver et Gold avec Python dans Synapse.
- Préparer les tables ou vues nécessaires à Power BI.
- Prévoir la reprise d’un lot sans créer de doublons.

## Reprise par Nidhal

- Préparer l’infrastructure et les droits nécessaires à Synapse.
- Documenter les ressources avec Terraform.
- Construire Power BI à partir des données préparées.
- Afficher la dernière collecte et la fraîcheur de la source.
- Vérifier les coûts et les conditions de rafraîchissement.

## Exploitation

Pour surveiller :
Superviser → Exécutions de pipeline → Déclenché.

En cas d’échec :
1. ouvrir l’exécution ;
2. identifier l’activité en échec ;
3. lire son erreur ;
4. corriger la cause avant de relancer.

Un lot incomplet sans manifeste de réussite ne doit pas être consommé.

Le test du déclencheur est borné au 28 octobre 2026 à 23:10,
fuseau de Paris. Prévoir une nouvelle fenêtre pour les prochains
tests et la démonstration.

## Travaux restant à terminer

- Automatiser la validation du contenu des lots.
- Tester et documenter un scénario d’échec contrôlé.
- Ajouter les captures et exports des exécutions au dépôt.
- Intégrer le traitement Synapse à l’orchestration.
- Vérifier le pipeline complet jusqu’à Power BI.
