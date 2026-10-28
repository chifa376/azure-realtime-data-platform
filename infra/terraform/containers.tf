resource "azurerm_storage_container" "velib_data" {
  name                  = "velib-data"
  storage_account_id    = azurerm_storage_account.velib.id
  container_access_type = "private"

  lifecycle {
    prevent_destroy = true
  }
}