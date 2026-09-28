output "s3_bucket_name" {
  value       = aws_s3_bucket.data_lake.id
  description = "Amazon S3 Data Lake bucket name"
}

output "rds_endpoint" {
  value       = aws_db_instance.postgres.endpoint
  description = "PostgreSQL RDS connection endpoint"
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.cluster.name
  description = "Amazon ECS Cluster name"
}

output "cloudwatch_log_group" {
  value       = aws_cloudwatch_log_group.api_logs.name
  description = "CloudWatch log group for container logs"
}
