terraform {
  backend "azurerm" {
    resource_group_name  = "rg-velib-data-platform"
    storage_account_name = "stvelibchifa2026"
    container_name       = "tfstate"
    key                  = "velib.terraform.tfstate"

    use_azuread_auth = true
    use_cli          = true
  }
}