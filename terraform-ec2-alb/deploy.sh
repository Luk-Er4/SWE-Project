#!/bin/bash
set -e

AWS_REGION="${aws_region}"
ECR_IMAGE_URI="${ecr_image_uri}"

AWS_DB_HOST="${db_host}"
AWS_DB_NAME="${db_name}"
AWS_DB_USER="${db_user}"
AWS_DB_PW="${db_password}"
PORT="${ec2_port_num}"
CONTAINER_NAME="${ec2_container_name}"

dnf update -y || yum update -y
dnf install -y docker awscli || yum install -y docker awscli

systemctl enable docker
systemctl start docker

aws ecr get-login-password --region "$AWS_REGION" \
| docker login --username AWS --password-stdin "$(echo "$ECR_IMAGE_URI" | cut -d'/' -f1)"

docker pull "$ECR_IMAGE_URI"

docker stop "$CONTAINER_NAME" || true
docker rm "$CONTAINER_NAME" || true

docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  -p "$PORT":"$PORT" \
  -e AWS_DB_HOST="$AWS_DB_HOST" \
  -e AWS_DB_NAME="$AWS_DB_NAME" \
  -e AWS_DB_USER="$AWS_DB_USER" \
  -e AWS_DB_PW="$AWS_DB_PW" \
  "$ECR_IMAGE_URI"