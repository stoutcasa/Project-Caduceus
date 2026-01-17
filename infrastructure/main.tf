#Terraform
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

# Pull MySQL Image
resource "docker_image" "mysql" {
  name         = "mysql:8.0"
  keep_locally = true
}

# 1. The Legacy Server (Source)
resource "docker_container" "legacy_server" {
  image = docker_image.mysql.image_id
  name  = "vista_legacy"
  ports {
    internal = 3306
    external = 3306
  }
  env = [
    "MYSQL_ROOT_PASSWORD=rootpassword",
    "MYSQL_DATABASE=vista_dump"
  ]
  # Keep container running
  command = ["--default-authentication-plugin=mysql_native_password"]
}

# 2. The Modern Server (Target)
resource "docker_container" "modern_server" {
  image = docker_image.mysql.image_id
  name  = "millennium_target"
  ports {
    internal = 3306
    external = 3307 # Mapped to port 3307 on your host
  }
  env = [
    "MYSQL_ROOT_PASSWORD=rootpassword",
    "MYSQL_DATABASE=millennium_core"
  ]
  command = ["--default-authentication-plugin=mysql_native_password"]
}
