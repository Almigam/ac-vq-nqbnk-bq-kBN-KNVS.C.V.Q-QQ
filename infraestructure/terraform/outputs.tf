#Archivo de configuración de Terraform para definir los outputs del módulo principal.
output "resource_group_name" {
  description = "Nombre del Resource Group creado"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Región donde se desplegó el Resource Group"
  value       = azurerm_resource_group.main.location
}

output "frontend_url" {
  description = "URL del sitio web estático desplegado en Azure Storage"
  value       = azurerm_storage_account.frontend.primary_web_endpoint
}

output "images_storage_url" {
  description = "URL base del storage de imágenes"
  value       = azurerm_storage_account.images.primary_blob_endpoint
}