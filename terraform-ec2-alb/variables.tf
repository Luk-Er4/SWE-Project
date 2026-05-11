variable "ecr_image_uri_sys_api" {
  type = string
  default = "077369590118.dkr.ecr.us-east-1.amazonaws.com/health-sys/api:v1"
}

variable "ecr_image_uri_data_api" {
  type = string
  default = "077369590118.dkr.ecr.us-east-1.amazonaws.com/health-data/api:v1"
}

variable "aws_region" {
  default = "us-east-1"
}

variable "db_user" {
  default = "admin"
  type = string
}

variable "db_name_sys" {
  default = "healthsys"
  type = string
}

variable "db_name_data" {
  default = "healthinfo"
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "port_sys_api" {
  default = "8000"
}

variable "port_data_api" {
  default = "8001"
}

variable "container_name_sys_api" {
  default = "health-sys-api"
}

variable "container_name_data_api" {
  default = "health-data-api"
}

variable "https_certificate" {
  type      = string
  sensitive = true
}

variable "zone_id" {
  type    = string
  default = "Z077001833HVL2EP22HGV"
}