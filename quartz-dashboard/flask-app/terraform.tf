provider "aws" {
  region = "us-west-2"  # Replace with your desired AWS region
}

resource "aws_s3_bucket" "example_bucket" {
  bucket = "your-bucket-name"  # Replace with your desired bucket name

  versioning {
    enabled = true
  }
}

resource "aws_redshift_cluster" "example_cluster" {
  cluster_identifier      = "your-cluster-name"  # Replace with your desired cluster name
  node_type               = "dc2.large"
  cluster_type            = "single-node"
  master_username         = "your-username"  # Replace with your desired username
  master_password         = "your-password"  # Replace with your desired password
  publicly_accessible    = true
  skip_final_snapshot     = true
  encrypted               = false  # Setting encryption to false for an unencrypted cluster
}

output "s3_bucket_name" {
  value = aws_s3_bucket.example_bucket.id
}

output "redshift_cluster_id" {
  value = aws_redshift_cluster.example_cluster.id
}