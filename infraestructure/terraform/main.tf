resource "azurerm_resource_group" "main" {
  name     = "rg-soundlog-dev"
  location = "francecentral"

  tags = {
    project    = "soundlog"
    managed_by = "terraform"
  }
}
#Frontend estático
resource "azurerm_storage_account" "frontend" {
  name = "soundlogdevfrontend"
  resource_group_name = azurerm_resource_group.main.name
  location = azurerm_resource_group.main.location
  account_tier= "Standard"
  account_replication_type = "LRS"
  account_kind = "StorageV2"

  https_traffic_only_enabled = true
  min_tls_version = "TLS1_2"

  static_website {
    index_document = "index.html"
    error_404_document = "404.html"
  }

  tags = {
    project    = "soundlog"
    managed_by = "terraform"
  }
}

#Storage account para las imágenes: Fotos perfil y portadas álbumes, singles
resource "azurerm_storage_account" "images" {
  name = "soundlogdevimages"
  resource_group_name = azurerm_resource_group.main.name
  location = azurerm_resource_group.main.location
  account_tier= "Standard"
  account_replication_type = "LRS"
  account_kind = "StorageV2"

  https_traffic_only_enabled = true
  min_tls_version = "TLS1_2"

  tags = {
    project    = "soundlog"
    managed_by = "terraform"
  }
}

#Contenedores
resource "azurerm_storage_container" "profile_pictures" {
  name = "profile-pictures"
  storage_account_name = azurerm_storage_account.images.name
  container_access_type = "blob" 
}

resource "azurerm_storage_container" "album_covers" {
  name = "album-covers"
  storage_account_name = azurerm_storage_account.images.name
  container_access_type = "blob" 
}
