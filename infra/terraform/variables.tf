variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS deployment region"
}

variable "project_name" {
  type        = string
  default     = "chronicle"
  description = "Project name prefix"
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Target deployment environment"
}

variable "vpc_id" {
  type        = string
  default     = "vpc-12345678"
  description = "VPC ID where resources are deployed"
}

variable "public_subnet_ids" {
  type        = list(string)
  default     = ["subnet-11111111", "subnet-22222222"]
  description = "Subnets for ECS public tasks or ALB"
}

variable "private_subnet_ids" {
  type        = list(string)
  default     = ["subnet-33333333", "subnet-44444444"]
  description = "Subnets for RDS PostgreSQL database"
}

variable "db_username" {
  type        = string
  default     = "chronicle_admin"
  description = "PostgreSQL root master user"
}

variable "db_password" {
  type        = string
  sensitive   = true
  default     = "SecureMasterDbPass987!"
  description = "PostgreSQL root master password"
}

variable "ecr_repository_url" {
  type        = string
  default     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/chronicle"
  description = "ECR Docker image repository URI"
}

variable "ecs_execution_role_arn" {
  type        = string
  default     = "arn:aws:iam::123456789012:role/ecsTaskExecutionRole"
  description = "IAM Role for ECS task execution"
}

variable "ecs_task_role_arn" {
  type        = string
  default     = "arn:aws:iam::123456789012:role/ecsTaskRole"
  description = "IAM Role for application runtime permissions (S3, CloudWatch)"
}
