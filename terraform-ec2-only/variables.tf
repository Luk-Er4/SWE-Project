variable "ecr_image_uri_sys_api" {
  type = string
  default = "077369590118.dkr.ecr.us-east-1.amazonaws.com/health-sys/api:v30"
}

variable "ecr_image_uri_data_api" {
  type = string
  default = "077369590118.dkr.ecr.us-east-1.amazonaws.com/health-sys/data:v30"
}

variable "aws_region" {
  default = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "health-sys"
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