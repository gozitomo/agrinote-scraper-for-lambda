#!/bin/bash
set -e

AWS_REGION="ap-northeast-1"
ECR_ACCOUNT_ID="434364279795"
REPOSITORY_NAME="agrinote-scraper-for-lambda"
DOCKERFILE_DIR="docker/Dockerfile"
IMAGE_TAG="latest"
FULL_IMAGE_URL="${ECR_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPOSITORY_NAME}:${IMAGE_TAG}"

echo "=== 1. Buildx builder setup ==="
docker buildx create --use --name multiarch-builder 2>/dev/null || true

echo "=== 2. Building Docker image for linux/amd64 ==="
docker buildx build \
  --platform linux/amd64 \
  -t ${REPOSITORY_NAME}:${IMAGE_TAG} \
  -f ${DOCKERFILE_DIR} \
  --load \
  .

echo "=== 3. Logging into ECR ==="
aws ecr get-login-password --region ${AWS_REGION} \
| docker login \
    --username AWS \
    --password-stdin \
    ${ECR_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

echo "=== 4. Tagging image ==="
docker tag ${REPOSITORY_NAME}:${IMAGE_TAG} ${FULL_IMAGE_URL}

echo "=== 5. Pushing image to ECR ==="
docker push \
  ${FULL_IMAGE_URL}

echo "=== DONE! ==="
echo "Pushed: ${FULL_IMAGE_URL}"
