resource "azurerm_synapse_spark_pool" "velib" {
  name                 = "sparkvelib"
  synapse_workspace_id = azurerm_synapse_workspace.velib.id

  node_size_family = "MemoryOptimized"
  node_size        = "Small"
  spark_version    = "3.5"

  auto_scale {
    min_node_count = 3
    max_node_count = 3
  }

  auto_pause {
    delay_in_minutes = 15
  }

  tags = {
    Environment = "student"
    project     = "Velib-Live-Analytics"
  }

  lifecycle {
    prevent_destroy = true
  }
}
