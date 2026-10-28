resource "azurerm_data_factory" "velib" {
  name                = "adf-velib-chifa-2026"
  resource_group_name = azurerm_resource_group.velib.name
  location            = azurerm_resource_group.velib.location

  public_network_enabled = true

  identity {
    type = "SystemAssigned"
  }

  github_configuration {
    account_name       = "chifa376"
    repository_name    = "azure-realtime-data-platform"
    branch_name        = "main"
    root_folder        = "/ingestion/adf"
    git_url            = "https://github.com"
    publishing_enabled = true
  }

  lifecycle {
    prevent_destroy = true
  }
}