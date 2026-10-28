# Infrastructure Terraform — Vélib

## Périmètre actuel

Cette configuration décrit cinq ressources Azure existantes :

| Adresse Terraform | Ressource |
|---|---|
| azurerm_resource_group.velib | Groupe rg-velib-data-platform |
| azurerm_storage_account.velib | Stockage stvelibchifa2026 |
| azurerm_storage_container.velib_data | Conteneur velib-data |
| azurerm_data_factory.velib | Fabrique adf-velib-chifa-2026 |
| azurerm_role_assignment.adf_blob_contributor | Autorisation ADF sur le conteneur |

Les ressources ont été créées dans le portail puis importées
dans l’état Terraform. Le dernier plan vérifié affiche
« No changes ».

Cela valide l’alignement de la configuration avec l’existant.
Un déploiement complet dans un environnement vierge n’a pas
encore été testé.

## Prérequis

- Terraform conforme à versions.tf.
- Azure CLI installé et connecté.
- Accès à l’abonnement Azure for Students du projet.
- Permissions adaptées aux ressources et aux attributions de rôles.

## Utilisation avec PowerShell

Depuis le dossier infra/terraform :

```powershell
az login
az account set --subscription "Azure for Students"
$env:ARM_SUBSCRIPTION_ID = az account show --query id --output tsv

terraform init
terraform fmt -check
terraform validate
terraform plan
```

Examiner le plan avant toute application.

## Ressources déjà existantes

Sur une nouvelle machine, un état vide ne connaît pas les
ressources existantes. Il faut retrouver le backend partagé
ou effectuer les imports appropriés avant toute application.

Importer uniquement le groupe de ressources n’importe pas
automatiquement les ressources qu’il contient.

Les cinq adresses du tableau ci-dessus ont déjà été importées
sur la machine de Chifa. Les identifiants d’import sont les
identifiants Azure Resource Manager des ressources.

Pour l’attribution de rôle, retrouver son identifiant avec
Azure CLI et vérifier le principal, le rôle et le périmètre
avant de l’importer.

## État Terraform et travail en équipe

L’état est actuellement local.

- Ne pas publier terraform.tfstate ni ses sauvegardes.
- Ne pas publier le dossier .terraform.
- Conserver une sauvegarde sécurisée de l’état local.
- Versionner .terraform.lock.hcl.
- Prévoir un backend distant avec verrouillage avant que
  plusieurs membres gèrent ensemble cette infrastructure.
- Ne pas gérer simultanément les mêmes ressources avec
  plusieurs états indépendants.

## Sécurité et fonctionnement

- Conteneur privé.
- HTTPS et TLS 1.2.
- Identité managée système pour Data Factory.
- Rôle Storage Blob Data Contributor limité à velib-data.
- Suppression réversible des blobs et conteneurs : 7 jours.
- Protection prevent_destroy sur les ressources décrites.

L’accès réseau public du stockage reste activé conformément
à la configuration actuelle du projet.

## Déploiement des pipelines

Les pipelines, datasets et services liés ADF sont versionnés
dans ingestion/adf.

Cette configuration Terraform gère la fabrique et sa connexion
GitHub. Elle ne déploie pas encore les objets ADF eux-mêmes.
L’authentification GitHub dans ADF Studio peut nécessiter une
intervention utilisateur.

## Travaux restants

- Ajouter Synapse et ses accès.
- Compléter l’automatisation des composants Power BI.
- Préparer le backend distant.
- Paramétrer les noms pour les différents environnements.
- Tester la reproductibilité du déploiement complet.

Le bonus Terraform est donc partiellement réalisé.
