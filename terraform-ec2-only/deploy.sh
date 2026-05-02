#!/bin/bash
set -e

AWS_REGION="${aws_region}"
ECR_IMAGE_URI="${ecr_image_uri}"

AWS_DB_HOST="${db_host}"
AWS_DB_NAME="${db_name}"
AWS_DB_USER="${db_user}"
AWS_DB_PW="${db_password}"

dnf update -y || yum update -y
dnf install -y docker awscli || yum install -y docker awscli

systemctl enable docker
systemctl start docker

aws ecr get-login-password --region "$AWS_REGION" \
| docker login --username AWS --password-stdin "$(echo "$ECR_IMAGE_URI" | cut -d'/' -f1)"

docker pull "$ECR_IMAGE_URI"

docker stop health-api || true
docker rm health-api || true

docker run -d \
  --name health-api \
  --restart unless-stopped \
  -p 8000:8000 \
  -e AWS_DB_HOST="$AWS_DB_HOST" \
  -e AWS_DB_NAME="$AWS_DB_NAME" \
  -e AWS_DB_USER="$AWS_DB_USER" \
  -e AWS_DB_PW="$AWS_DB_PW" \
  "$ECR_IMAGE_URI"