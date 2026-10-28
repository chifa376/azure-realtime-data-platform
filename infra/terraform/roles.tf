resource "azurerm_role_assignment" "adf_blob_contributor" {
  scope                = azurerm_storage_container.velib_data.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_data_factory.velib.identity[0].principal_id
  principal_type       = "ServicePrincipal"

  lifecycle {
    prevent_destroy = true
  }
}