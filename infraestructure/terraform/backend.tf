#El estado de Terraform se guarda en Azure Storage.
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-soundlog-tfstate"
    storage_account_name = "soundlogtfstate"   
    container_name       = "tfstate"
    key                  = "soundlog.terraform.tfstate"
  }
}
