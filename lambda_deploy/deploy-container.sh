#!/bin/bash

# Configuration
FUNCTION_NAME="stockwellness-semantic-search"
REGION="us-east-2"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REPOSITORY_NAME="stockwellness-semantic"
IMAGE_TAG="latest"

echo "🐳 Building Lambda Container Image..."

# Create ECR repository if it doesn't exist
echo "📦 Creating ECR repository..."
aws ecr create-repository \
    --repository-name $REPOSITORY_NAME \
    --region $REGION 2>/dev/null || echo "Repository already exists"

# Get login token for ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build the Docker image
echo "🏗️ Building Docker image..."
docker build -t $REPOSITORY_NAME:$IMAGE_TAG .

# Tag the image for ECR
echo "🏷️ Tagging image for ECR..."
docker tag $REPOSITORY_NAME:$IMAGE_TAG $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME:$IMAGE_TAG

# Push the image to ECR
echo "⬆️ Pushing image to ECR..."
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME:$IMAGE_TAG

echo "✅ Container image pushed to ECR!"
echo "📍 Image URI: $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPOSITORY_NAME:$IMAGE_TAG"
echo ""
echo "🚀 Next steps:"
echo "1. Go to AWS Lambda Console"
echo "2. Create function → Container image"
echo "3. Use the Image URI above"
echo "4. Set memory to 1024MB and timeout to 60s" 