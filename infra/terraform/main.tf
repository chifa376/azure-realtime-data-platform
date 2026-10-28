resource "azurerm_resource_group" "velib" {
  name     = "rg-velib-data-platform"
  location = "francecentral"

  lifecycle {
    prevent_destroy = true
  }
}