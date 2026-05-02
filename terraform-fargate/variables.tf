variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "health-sys"
}

variable "task_definition_name" {
  description = "Task Definition name prefix"
  type        = string
  default     = "task-def-fargate-api"
}

variable "aws_region" {
  default = "us-east-1"
}
