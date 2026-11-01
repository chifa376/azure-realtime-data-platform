resource "azurerm_storage_data_lake_gen2_filesystem" "synapse" {
  name               = "synapse"
  storage_account_id = azurerm_storage_account.velib.id

  lifecycle {
    prevent_destroy = true
  }
}
