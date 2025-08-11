#!/bin/bash

# BSH Complaints Management System - Production Deployment Script

set -e

echo "=========================================="
echo "BSH Complaints Management System"
echo "Production Deployment Script"
echo "=========================================="

# Configuration
PROJECT_ID="demo-bsh-complaints-management"
REGION="europe-west1"
SERVICE_NAME="demo-bsh-complaints-management"
BUCKET_NAME="bsh-complaints-db-bucket"

echo "Deploying to project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "Bucket: $BUCKET_NAME"

# Set the project
echo "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable storage.googleapis.com

# Create GCS bucket if it doesn't exist
echo "Setting up Cloud Storage bucket..."
gsutil ls -b gs://$BUCKET_NAME > /dev/null 2>&1 || {
    echo "Creating bucket: $BUCKET_NAME"
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME
}

# Build and deploy using Cloud Build
echo "Building and deploying application..."
gcloud builds submit \
    --config cloudbuild.yaml \
    --substitutions=_SERVICE_NAME=$SERVICE_NAME,_DEPLOY_REGION=$REGION,_PLATFORM=managed,_GCP_PROJECT_ID=$PROJECT_ID,_GCS_BUCKET_NAME=$BUCKET_NAME,_SECRET_MANAGER_KEY=openai-api-key \
    .

echo "=========================================="
echo "Deployment completed successfully!"
echo "Service URL: https://$SERVICE_NAME-$(gcloud config get-value project).$REGION.run.app"
echo "=========================================="
