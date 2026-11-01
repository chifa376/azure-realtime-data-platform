
resource "azurerm_synapse_workspace" "velib" {
  name                                 = "syn-velib-data-platform-2026"
  resource_group_name                  = azurerm_resource_group.velib.name
  location                             = azurerm_resource_group.velib.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.synapse.id

  sql_administrator_login         = "sqladminuser"
  managed_resource_group_name     = "rg-velib-synapse-managed"
  managed_virtual_network_enabled = false
  public_network_access_enabled   = true
  azuread_authentication_only     = true

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = "Student"
    Project     = "Velib-Live-Analytics"
  }

  lifecycle {
    prevent_destroy = true
  }
}
