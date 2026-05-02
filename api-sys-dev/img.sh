set -e

set -a
source .env
set +a

echo "Logging into ECR..."

aws login
aws ecr get-login-password --region $AWS_REGION --profile $AWS_PROFILE_NAME | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "Login Succeeded"

docker build --no-cache -t $REPO_NAME:$TAG .

echo "Image Build Complete"

docker tag $REPO_NAME:$TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$TAG

echo "Tagged"

docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$TAG

echo "Image Pushed to ECR"

aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment --profile $AWS_PROFILE_NAME

echo "Image Pulled to Fargate"