#!/bin/bash

# BSH Complaints Management - Production Deployment Script

set -e  # Exit on any error

echo "🚀 Starting deployment of BSH Complaints Management to Cloud Run..."

# Check if required environment variables are set
if [ -z "$PROJECT_ID" ]; then
    echo "❌ PROJECT_ID environment variable is not set"
    echo "Please run: export PROJECT_ID=prometa-dummy"
    exit 1
fi

# Set default values
REGION=${REGION:-"europe-west1"}
SERVICE_NAME=${SERVICE_NAME:-"prod-demo-bsh-complaints-management"}
BUCKET_NAME=${BUCKET_NAME:-"bsh-complaints-storage"}

echo "📋 Deployment Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service Name: $SERVICE_NAME"
echo "   Bucket Name: $BUCKET_NAME"

# Authenticate with Google Cloud (if not already authenticated)
echo "🔐 Checking Google Cloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ No active Google Cloud authentication found"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Set the project
echo "🏗️  Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Create GCS bucket if it doesn't exist
echo "🗄️  Checking/creating GCS bucket: $BUCKET_NAME..."
if ! gsutil ls -b gs://$BUCKET_NAME > /dev/null 2>&1; then
    echo "   Creating bucket $BUCKET_NAME..."
    gsutil mb -l $REGION gs://$BUCKET_NAME
    echo "   ✅ Bucket created successfully"
else
    echo "   ✅ Bucket already exists"
fi

# Set bucket permissions for Cloud Run service account
echo "🔒 Setting bucket permissions..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
gsutil iam ch serviceAccount:${SERVICE_ACCOUNT}:objectAdmin gs://$BUCKET_NAME || true

# Submit build to Cloud Build
echo "🏗️  Starting Cloud Build..."
gcloud builds submit --config cloudbuild.yaml .

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Your application should be available at:"
echo "   https://$SERVICE_NAME-$(gcloud config get-value project | tr ':' '-' | tr '.' '-')-$REGION.run.app"
echo ""
echo "📊 To check the service status:"
echo "   gcloud run services describe $SERVICE_NAME --region=$REGION"
echo ""
echo "📝 To view logs:"
echo "   gcloud logs tail --service=$SERVICE_NAME"
