resource "azurerm_storage_account" "velib" {
  name                = "stvelibchifa2026"
  resource_group_name = azurerm_resource_group.velib.name
  location            = azurerm_resource_group.velib.location

  account_kind             = "StorageV2"
  account_tier             = "Standard"
  account_replication_type = "LRS"
  access_tier              = "Hot"

  is_hns_enabled = true
  nfsv3_enabled  = false
  sftp_enabled   = false

  https_traffic_only_enabled      = true
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = true
  default_to_oauth_authentication = true
  public_network_access_enabled   = true

  cross_tenant_replication_enabled  = false
  infrastructure_encryption_enabled = false



  blob_properties {
    versioning_enabled  = false
    change_feed_enabled = false

    delete_retention_policy {
      days = 7
    }

    container_delete_retention_policy {
      days = 7
    }
  }

  share_properties {
    retention_policy {
      days = 7
    }
  }

  tags = {
    projet = "VelibDataPlatform"
  }

  lifecycle {
    prevent_destroy = true
  }
}